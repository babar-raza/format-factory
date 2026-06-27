// Tests for NetpbmImage.GetMorphologicalErosion, GetMorphologicalDilation, GetMorphologicalOpening deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R322

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R322: Tests for NetpbmImage.GetMorphologicalErosion, GetMorphologicalDilation, GetMorphologicalOpening deeper.
/// GetMorphologicalErosion(kernelSize): applies morphological erosion with a square structuring element.
/// GetMorphologicalDilation(kernelSize): applies morphological dilation with a square structuring element.
/// GetMorphologicalOpening(kernelSize): applies erosion followed by dilation (morphological opening).
/// Covers: GetMorphologicalErosion no-throw; GetMorphologicalErosion same dimensions;
/// GetMorphologicalErosion reduces or maintains mean vs dilation; GetMorphologicalErosion consistent;
/// GetMorphologicalDilation no-throw; GetMorphologicalDilation same dimensions;
/// GetMorphologicalDilation consistent; GetMorphologicalDilation mean geq erosion mean;
/// GetMorphologicalOpening no-throw; GetMorphologicalOpening same dimensions;
/// GetMorphologicalOpening mean leq dilation mean; GetMorphologicalOpening consistent;
/// GetMorphologicalOpening save-load;
/// dogfood GetMorphologicalErosion→GetMorphologicalDilation→GetMorphologicalOpening→SaveToFile pipeline.
/// </summary>
public class NetpbmR322GetMorphologicalErosionAndDilationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR322GetMorphologicalErosionAndDilationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR322_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateBinaryPgm()
    {
        // 10×10 binary-like PGM: dark spots (0) on bright background (255)
        // Morphological operations have clear, predictable effects
        var path = TempFile("binary.pgm");
        int[,] pixels = {
            { 255,255,255,255,255,255,255,255,255,255 },
            { 255,255,255,255,255,255,255,255,255,255 },
            { 255,255,0,0,0,255,255,255,255,255 },
            { 255,255,0,0,0,255,255,255,255,255 },
            { 255,255,0,0,0,255,255,255,255,255 },
            { 255,255,255,255,255,255,0,0,255,255 },
            { 255,255,255,255,255,255,0,0,255,255 },
            { 255,255,255,255,255,255,255,255,255,255 },
            { 255,255,255,255,255,255,255,255,255,255 },
            { 255,255,255,255,255,255,255,255,255,255 },
        };
        var rows = new System.Collections.Generic.List<string>();
        for (int r = 0; r < 10; r++)
        {
            var row = new System.Collections.Generic.List<string>();
            for (int c = 0; c < 10; c++)
                row.Add(pixels[r, c].ToString());
            rows.Add(string.Join(" ", row));
        }
        File.WriteAllText(path, $"P2\n10 10\n255\n{string.Join("\n", rows)}\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetMorphologicalErosion
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMorphologicalErosion_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateBinaryPgm());
        var ex = Record.Exception(() => img.GetMorphologicalErosion(3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMorphologicalErosion_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateBinaryPgm());
        var er = img.GetMorphologicalErosion(3);
        Assert.Equal(img.Width, er.Width);
        Assert.Equal(img.Height, er.Height);
    }

    [Fact]
    public void GetMorphologicalErosion_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBinaryPgm());
        var er1 = img.GetMorphologicalErosion(3);
        var er2 = img.GetMorphologicalErosion(3);
        Assert.Equal(er1.Pixels, er2.Pixels);
    }

    [Fact]
    public void GetMorphologicalErosion_MeanLeqOriginal()
    {
        // Erosion of bright-background dark-spot image should reduce mean (expand dark regions)
        var img = NetpbmImage.LoadFile(CreateBinaryPgm());
        var er = img.GetMorphologicalErosion(3);
        double origMean = img.Pixels.Average(p => (double)p);
        double erMean = er.Pixels.Average(p => (double)p);
        Assert.True(erMean <= origMean);
    }

    // -------------------------------------------------------------------------
    // GetMorphologicalDilation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMorphologicalDilation_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateBinaryPgm());
        var ex = Record.Exception(() => img.GetMorphologicalDilation(3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMorphologicalDilation_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateBinaryPgm());
        var dl = img.GetMorphologicalDilation(3);
        Assert.Equal(img.Width, dl.Width);
        Assert.Equal(img.Height, dl.Height);
    }

    [Fact]
    public void GetMorphologicalDilation_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBinaryPgm());
        var dl1 = img.GetMorphologicalDilation(3);
        var dl2 = img.GetMorphologicalDilation(3);
        Assert.Equal(dl1.Pixels, dl2.Pixels);
    }

    [Fact]
    public void GetMorphologicalDilation_MeanGeqErosion()
    {
        var img = NetpbmImage.LoadFile(CreateBinaryPgm());
        var er = img.GetMorphologicalErosion(3);
        var dl = img.GetMorphologicalDilation(3);
        double erMean = er.Pixels.Average(p => (double)p);
        double dlMean = dl.Pixels.Average(p => (double)p);
        Assert.True(dlMean >= erMean);
    }

    // -------------------------------------------------------------------------
    // GetMorphologicalOpening
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMorphologicalOpening_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateBinaryPgm());
        var ex = Record.Exception(() => img.GetMorphologicalOpening(3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMorphologicalOpening_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateBinaryPgm());
        var op = img.GetMorphologicalOpening(3);
        Assert.Equal(img.Width, op.Width);
        Assert.Equal(img.Height, op.Height);
    }

    [Fact]
    public void GetMorphologicalOpening_MeanLeqDilation()
    {
        var img = NetpbmImage.LoadFile(CreateBinaryPgm());
        var dl = img.GetMorphologicalDilation(3);
        var op = img.GetMorphologicalOpening(3);
        double dlMean = dl.Pixels.Average(p => (double)p);
        double opMean = op.Pixels.Average(p => (double)p);
        Assert.True(opMean <= dlMean);
    }

    [Fact]
    public void GetMorphologicalOpening_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBinaryPgm());
        var op1 = img.GetMorphologicalOpening(3);
        var op2 = img.GetMorphologicalOpening(3);
        Assert.Equal(op1.Pixels, op2.Pixels);
    }

    [Fact]
    public void GetMorphologicalOpening_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBinaryPgm());
        var op = img.GetMorphologicalOpening(3);
        var path = TempFile("op_save.pgm");
        op.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(op.Width, loaded.Width);
        Assert.Equal(op.Height, loaded.Height);
        Assert.Equal(op.Pixels, loaded.Pixels);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMorphologicalErosion_GetMorphologicalDilation_GetMorphologicalOpening_SaveToFile_Pipeline()
    {
        // Remote sensing — satellite SAR image morphological feature extraction
        // Dark pixels = water bodies, bright pixels = land
        var path = TempFile("sar_land_water.pgm");
        int W = 12, H = 12;
        int[,] land = new int[H, W];
        // Fill with bright land (200)
        for (int r = 0; r < H; r++)
            for (int c = 0; c < W; c++)
                land[r, c] = 200;
        // Lake region (dark, rows 3-8, cols 2-9)
        for (int r = 3; r <= 8; r++)
            for (int c = 2; c <= 9; c++)
                land[r, c] = 30;
        // River channel (dark strip, rows 0-2, cols 5-6)
        for (int r = 0; r <= 2; r++)
            for (int c = 5; c <= 6; c++)
                land[r, c] = 40;

        var rows = new System.Collections.Generic.List<string>();
        for (int r = 0; r < H; r++)
        {
            var row = new System.Collections.Generic.List<string>();
            for (int c = 0; c < W; c++)
                row.Add(land[r, c].ToString());
            rows.Add(string.Join(" ", row));
        }
        File.WriteAllText(path, $"P2\n{W} {H}\n255\n{string.Join("\n", rows)}\n");

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(W, img.Width);
        Assert.Equal(H, img.Height);

        double origMean = img.Pixels.Average(p => (double)p);

        // GetMorphologicalErosion — expands dark regions (water bodies appear larger)
        var er = img.GetMorphologicalErosion(3);
        Assert.Equal(W, er.Width);
        Assert.Equal(H, er.Height);
        double erMean = er.Pixels.Average(p => (double)p);
        Assert.True(erMean <= origMean); // erosion darkens the image
        Assert.Equal(er.Pixels, img.GetMorphologicalErosion(3).Pixels); // consistent

        // GetMorphologicalDilation — shrinks dark regions (water appears smaller)
        var dl = img.GetMorphologicalDilation(3);
        Assert.Equal(W, dl.Width);
        Assert.Equal(H, dl.Height);
        double dlMean = dl.Pixels.Average(p => (double)p);
        Assert.True(dlMean >= erMean); // dilation lightens relative to erosion
        Assert.Equal(dl.Pixels, img.GetMorphologicalDilation(3).Pixels); // consistent

        // GetMorphologicalOpening — removes thin features (river channel may disappear)
        var op = img.GetMorphologicalOpening(3);
        Assert.Equal(W, op.Width);
        Assert.Equal(H, op.Height);
        double opMean = op.Pixels.Average(p => (double)p);
        Assert.True(opMean <= dlMean); // opening ≤ dilation
        Assert.Equal(op.Pixels, img.GetMorphologicalOpening(3).Pixels); // consistent

        // Save all outputs
        var erPath = TempFile("sar_erosion.pgm");
        er.SaveToFile(erPath);
        Assert.True(File.Exists(erPath));

        var dlPath = TempFile("sar_dilation.pgm");
        dl.SaveToFile(dlPath);
        Assert.True(File.Exists(dlPath));

        var opPath = TempFile("sar_opening.pgm");
        op.SaveToFile(opPath);
        Assert.True(File.Exists(opPath));
        Assert.True(new FileInfo(opPath).Length > 0);

        // LoadFile and verify
        var loadedOp = NetpbmImage.LoadFile(opPath);
        Assert.Equal(W, loadedOp.Width);
        Assert.Equal(H, loadedOp.Height);
        Assert.Equal(op.Pixels, loadedOp.Pixels);

        // Chain morphological operations on loaded
        var ex1 = Record.Exception(() => loadedOp.GetMorphologicalErosion(3));
        var ex2 = Record.Exception(() => loadedOp.GetMorphologicalDilation(3));
        var ex3 = Record.Exception(() => loadedOp.GetMorphologicalOpening(3));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
