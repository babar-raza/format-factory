// Tests for NetpbmImage.GetConnectedComponentCount, GetMorphologyFeatures deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R358

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R358: Tests for NetpbmImage.GetConnectedComponentCount, GetMorphologyFeatures deeper.
/// GetConnectedComponentCount(): returns the count of connected bright regions in the image.
/// GetMorphologyFeatures(): returns an array of morphological feature values (area, perimeter, etc.).
/// Covers: GetConnectedComponentCount no-throw; GetConnectedComponentCount non-negative;
/// GetConnectedComponentCount zero for uniform dark; GetConnectedComponentCount consistent;
/// GetConnectedComponentCount save-load; GetConnectedComponentCount positive for multi-blob;
/// GetMorphologyFeatures no-throw; GetMorphologyFeatures non-null; GetMorphologyFeatures non-empty;
/// GetMorphologyFeatures consistent; GetMorphologyFeatures save-load;
/// dogfood CreateImage→GetConnectedComponentCount→GetMorphologyFeatures pipeline.
/// </summary>
public class NetpbmR358GetConnectedComponentCountAndMorphologyFeaturesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR358GetConnectedComponentCountAndMorphologyFeaturesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR358_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateDarkImage()
    {
        int w = 64, h = 64;
        var pixels = new byte[w * h];
        Array.Fill(pixels, (byte)20);
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    private static NetpbmImage CreateMultiBlobImage()
    {
        // Three distinct bright circular blobs on dark background
        int w = 80, h = 80;
        var pixels = new byte[w * h];
        Array.Fill(pixels, (byte)20);
        int[] cx = { 15, 40, 65 };
        int[] cy = { 40, 40, 40 };
        int r = 10;
        for (int b = 0; b < 3; b++)
            for (int y = 0; y < h; y++)
                for (int x = 0; x < w; x++)
                    if ((x - cx[b]) * (x - cx[b]) + (y - cy[b]) * (y - cy[b]) <= r * r)
                        pixels[y * w + x] = 200;
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    private static NetpbmImage CreateSingleBlobImage()
    {
        int w = 64, h = 64;
        var pixels = new byte[w * h];
        Array.Fill(pixels, (byte)20);
        int cx = 32, cy = 32, r = 15;
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                if ((x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r)
                    pixels[y * w + x] = 200;
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    // -------------------------------------------------------------------------
    // GetConnectedComponentCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConnectedComponentCount_NoThrow()
    {
        var img = CreateSingleBlobImage();
        var ex = Record.Exception(() => img.GetConnectedComponentCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetConnectedComponentCount_NonNegative()
    {
        var img = CreateSingleBlobImage();
        Assert.True(img.GetConnectedComponentCount() >= 0);
    }

    [Fact]
    public void GetConnectedComponentCount_Zero_ForDarkImage()
    {
        var img = CreateDarkImage();
        Assert.Equal(0, img.GetConnectedComponentCount());
    }

    [Fact]
    public void GetConnectedComponentCount_Positive_ForMultiBlob()
    {
        var img = CreateMultiBlobImage();
        Assert.True(img.GetConnectedComponentCount() > 0);
    }

    [Fact]
    public void GetConnectedComponentCount_Consistent()
    {
        var img = CreateMultiBlobImage();
        Assert.Equal(img.GetConnectedComponentCount(), img.GetConnectedComponentCount());
    }

    [Fact]
    public void GetConnectedComponentCount_SaveLoad_Consistent()
    {
        var img = CreateMultiBlobImage();
        var before = img.GetConnectedComponentCount();
        var path = TempFile("cc_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetConnectedComponentCount());
    }

    // -------------------------------------------------------------------------
    // GetMorphologyFeatures
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMorphologyFeatures_NoThrow()
    {
        var img = CreateSingleBlobImage();
        var ex = Record.Exception(() => img.GetMorphologyFeatures());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMorphologyFeatures_NonNull()
    {
        var img = CreateSingleBlobImage();
        Assert.NotNull(img.GetMorphologyFeatures());
    }

    [Fact]
    public void GetMorphologyFeatures_NonEmpty()
    {
        var img = CreateSingleBlobImage();
        Assert.NotEmpty(img.GetMorphologyFeatures());
    }

    [Fact]
    public void GetMorphologyFeatures_Consistent()
    {
        var img = CreateSingleBlobImage();
        var f1 = img.GetMorphologyFeatures();
        var f2 = img.GetMorphologyFeatures();
        Assert.Equal(f1.Length, f2.Length);
        for (int i = 0; i < f1.Length; i++)
            Assert.Equal(f1[i], f2[i]);
    }

    [Fact]
    public void GetMorphologyFeatures_SaveLoad_Consistent()
    {
        var img = CreateSingleBlobImage();
        var before = img.GetMorphologyFeatures();
        var path = TempFile("mf_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        var after = loaded.GetMorphologyFeatures();
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetConnectedComponentCount_GetMorphologyFeatures_Pipeline()
    {
        // Biomedical — automated cell counting in immunofluorescence microscopy
        // DAPI-stained nuclei segmentation for proliferation index calculation
        var rng = new Random(20241201);
        int w = 120, h = 120;

        // Dense cell field: many nuclei (DAPI-like — bright circular blobs)
        var densePixels = new byte[w * h];
        Array.Fill(densePixels, (byte)15);
        // Generate ~20 nuclei of varying sizes
        int[][] nuclei = {
            new[] {15, 15, 8}, new[] {35, 12, 7}, new[] {58, 18, 9}, new[] {82, 10, 8}, new[] {105, 15, 7},
            new[] {10, 40, 8}, new[] {30, 38, 9}, new[] {55, 42, 7}, new[] {78, 35, 8}, new[] {102, 40, 9},
            new[] {18, 65, 7}, new[] {42, 68, 8}, new[] {65, 62, 9}, new[] {90, 65, 7}, new[] {110, 70, 8},
            new[] {12, 90, 9}, new[] {38, 88, 7}, new[] {62, 92, 8}, new[] {86, 88, 9}, new[] {108, 92, 7},
        };
        foreach (var n in nuclei)
        {
            int ncx = n[0], ncy = n[1], nr = n[2];
            for (int y = 0; y < h; y++)
                for (int x = 0; x < w; x++)
                    if ((x - ncx) * (x - ncx) + (y - ncy) * (y - ncy) <= nr * nr)
                        densePixels[y * w + x] = (byte)(180 + rng.Next(60));
        }
        var denseImg = NetpbmImage.FromGrayscalePixels(densePixels, w, h, 255);

        // Sparse cell field: fewer nuclei
        var sparsePixels = new byte[w * h];
        Array.Fill(sparsePixels, (byte)15);
        int[][] sparseNuclei = {
            new[] {30, 30, 10}, new[] {90, 30, 9}, new[] {30, 90, 10}, new[] {90, 90, 9}, new[] {60, 60, 11}
        };
        foreach (var n in sparseNuclei)
        {
            int ncx = n[0], ncy = n[1], nr = n[2];
            for (int y = 0; y < h; y++)
                for (int x = 0; x < w; x++)
                    if ((x - ncx) * (x - ncx) + (y - ncy) * (y - ncy) <= nr * nr)
                        sparsePixels[y * w + x] = (byte)(185 + rng.Next(55));
        }
        var sparseImg = NetpbmImage.FromGrayscalePixels(sparsePixels, w, h, 255);

        // GetConnectedComponentCount
        var ccDense = denseImg.GetConnectedComponentCount();
        Assert.True(ccDense >= 0);
        Assert.Equal(ccDense, denseImg.GetConnectedComponentCount()); // consistent

        var ccSparse = sparseImg.GetConnectedComponentCount();
        Assert.True(ccSparse >= 0);
        Assert.Equal(ccSparse, sparseImg.GetConnectedComponentCount()); // consistent

        // Dense field should have more (or equal) components than sparse
        Assert.True(ccDense >= ccSparse);
        // Both should have detected at least some nuclei
        Assert.True(ccSparse > 0);
        Assert.True(ccDense > 0);

        // GetMorphologyFeatures
        var mfDense = denseImg.GetMorphologyFeatures();
        Assert.NotNull(mfDense);
        Assert.NotEmpty(mfDense);
        Assert.Equal(mfDense, denseImg.GetMorphologyFeatures()); // consistent (by array equality not reference)
        var mfDense2 = denseImg.GetMorphologyFeatures();
        Assert.Equal(mfDense.Length, mfDense2.Length);
        for (int i = 0; i < mfDense.Length; i++)
            Assert.Equal(mfDense[i], mfDense2[i]);

        var mfSparse = sparseImg.GetMorphologyFeatures();
        Assert.NotNull(mfSparse);
        Assert.NotEmpty(mfSparse);

        // Same number of feature dimensions
        Assert.Equal(mfDense.Length, mfSparse.Length);

        // Basic image properties
        Assert.Equal(w, denseImg.Width);
        Assert.Equal(h, denseImg.Height);
        Assert.True(denseImg.GetMeanIntensity() >= 0.0 && denseImg.GetMeanIntensity() <= 255.0);

        // SaveToFile — dense
        var pathDense = TempFile("dapi_dense.pgm");
        denseImg.SaveToFile(pathDense);
        Assert.True(File.Exists(pathDense));
        Assert.True(new FileInfo(pathDense).Length > 0);

        // SaveToFile — sparse
        var pathSparse = TempFile("dapi_sparse.pgm");
        sparseImg.SaveToFile(pathSparse);
        Assert.True(File.Exists(pathSparse));

        // LoadFile and verify — dense
        var loadedDense = NetpbmImage.LoadFile(pathDense);
        Assert.Equal(ccDense, loadedDense.GetConnectedComponentCount());
        var mfLoadedDense = loadedDense.GetMorphologyFeatures();
        Assert.Equal(mfDense.Length, mfLoadedDense.Length);
        for (int i = 0; i < mfDense.Length; i++)
            Assert.Equal(mfDense[i], mfLoadedDense[i], precision: 6);

        // LoadFile and verify — sparse
        var loadedSparse = NetpbmImage.LoadFile(pathSparse);
        Assert.Equal(ccSparse, loadedSparse.GetConnectedComponentCount());
        var mfLoadedSparse = loadedSparse.GetMorphologyFeatures();
        Assert.Equal(mfSparse.Length, mfLoadedSparse.Length);

        // Additional no-throw
        var ex1 = Record.Exception(() => denseImg.GetStandardDeviation());
        var ex2 = Record.Exception(() => sparseImg.GetHistogram());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
