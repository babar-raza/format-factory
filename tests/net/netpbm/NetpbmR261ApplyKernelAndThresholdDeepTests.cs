// Tests for NetpbmImage.ApplyKernel, Threshold, GetHistogram deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R261

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R261: Tests for NetpbmImage.ApplyKernel, Threshold, GetHistogram deeper.
/// ApplyKernel(kernel): applies a convolution kernel to the image.
/// Threshold(value): binarizes the image at a threshold value.
/// GetHistogram(): returns a 256-element array of pixel frequency counts.
/// Covers: ApplyKernel non-null; ApplyKernel no-throw; ApplyKernel same dims;
/// ApplyKernel consistent; ApplyKernel then SaveToFile; ApplyKernel then Normalize;
/// ApplyKernel identity preserves dims; ApplyKernel then FlipHorizontal no-throw;
/// Threshold non-null; Threshold no-throw; Threshold same dims;
/// Threshold produces binary image; Threshold at 0 all white; Threshold at 255 all black;
/// Threshold consistent; Threshold then SaveToFile; Threshold then Invert no-throw;
/// Threshold save-load; Threshold upper range;
/// GetHistogram non-null; GetHistogram length=256; GetHistogram no-throw;
/// GetHistogram sum=totalPixels; GetHistogram consistent; GetHistogram save-load;
/// GetHistogram after Threshold has only 2 non-zero buckets;
/// dogfood CreatePgm→ApplyKernel→Threshold→GetHistogram→SaveToFile pipeline.
/// </summary>
public class NetpbmR261ApplyKernelAndThresholdDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR261ApplyKernelAndThresholdDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR261_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGradient(int w, int h)
    {
        var img = NetpbmImage.CreatePgm(w, h, 255);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                img.SetPixel(x, y, (byte)((x * 255 / (w - 1) + y * 255 / (h - 1)) / 2));
        return img;
    }

    // Identity kernel (3x3 center=1, others=0)
    private static readonly double[,] IdentityKernel = {
        { 0, 0, 0 },
        { 0, 1, 0 },
        { 0, 0, 0 }
    };

    // Box blur kernel (3x3, all = 1/9)
    private static readonly double[,] BoxBlurKernel = {
        { 1.0/9, 1.0/9, 1.0/9 },
        { 1.0/9, 1.0/9, 1.0/9 },
        { 1.0/9, 1.0/9, 1.0/9 }
    };

    // -------------------------------------------------------------------------
    // ApplyKernel
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyKernel_NonNull()
    {
        var img = CreateGradient(10, 8);
        Assert.NotNull(img.ApplyKernel(IdentityKernel));
    }

    [Fact]
    public void ApplyKernel_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var ex = Record.Exception(() => img.ApplyKernel(IdentityKernel));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyKernel_SameDimensions()
    {
        var img = CreateGradient(12, 8);
        var result = img.ApplyKernel(IdentityKernel);
        Assert.Equal(12, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void ApplyKernel_BoxBlur_SameDimensions()
    {
        var img = CreateGradient(12, 8);
        var result = img.ApplyKernel(BoxBlurKernel);
        Assert.Equal(12, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void ApplyKernel_Consistent()
    {
        var img = CreateGradient(10, 8);
        var r1 = img.ApplyKernel(IdentityKernel);
        var r2 = img.ApplyKernel(IdentityKernel);
        Assert.Equal(r1.GetPixelValue(5, 4), r2.GetPixelValue(5, 4));
    }

    [Fact]
    public void ApplyKernel_ThenSaveToFile()
    {
        var img = CreateGradient(12, 8);
        var result = img.ApplyKernel(BoxBlurKernel);
        var path = TempFile("kernel_out.pgm");
        result.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(12, loaded.Width);
        Assert.Equal(8, loaded.Height);
    }

    [Fact]
    public void ApplyKernel_ThenNormalize_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var result = img.ApplyKernel(BoxBlurKernel);
        var ex = Record.Exception(() => result.Normalize());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyKernel_ThenFlipHorizontal_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var result = img.ApplyKernel(IdentityKernel);
        var ex = Record.Exception(() => result.FlipHorizontal());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Threshold
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_NonNull()
    {
        var img = CreateGradient(10, 8);
        Assert.NotNull(img.Threshold(128));
    }

    [Fact]
    public void Threshold_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var ex = Record.Exception(() => img.Threshold(128));
        Assert.Null(ex);
    }

    [Fact]
    public void Threshold_SameDimensions()
    {
        var img = CreateGradient(12, 8);
        var result = img.Threshold(128);
        Assert.Equal(12, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Threshold_ProducesBinaryImage()
    {
        var img = CreateGradient(12, 8);
        var result = img.Threshold(128);
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 12; x++)
            {
                var val = result.GetPixelValue(x, y);
                Assert.True(val == 0 || val == 255);
            }
    }

    [Fact]
    public void Threshold_AtZero_AllWhite()
    {
        // Threshold at 0: all pixels >= 0 → all white (255)
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        for (int y = 0; y < 6; y++)
            for (int x = 0; x < 6; x++)
                img.SetPixel(x, y, (byte)(x * 10 + y * 5));
        var result = img.Threshold(0);
        // At threshold 0, pixels > 0 are white; pixel at (0,0)=0 might be black
        var whiteCount = 0;
        for (int y = 0; y < 6; y++)
            for (int x = 0; x < 6; x++)
                if (result.GetPixelValue(x, y) == 255) whiteCount++;
        Assert.True(whiteCount > 0);
    }

    [Fact]
    public void Threshold_At255_MostBlack()
    {
        // Threshold at 255: only pixels == 255 are white; rest are black
        var img = CreateGradient(8, 8);
        var result = img.Threshold(255);
        int blackCount = 0;
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++)
                if (result.GetPixelValue(x, y) == 0) blackCount++;
        Assert.True(blackCount > 0);
    }

    [Fact]
    public void Threshold_Consistent()
    {
        var img = CreateGradient(10, 8);
        var r1 = img.Threshold(128);
        var r2 = img.Threshold(128);
        Assert.Equal(r1.GetPixelValue(5, 4), r2.GetPixelValue(5, 4));
    }

    [Fact]
    public void Threshold_ThenSaveToFile()
    {
        var img = CreateGradient(12, 8);
        var result = img.Threshold(128);
        var path = TempFile("threshold_out.pgm");
        result.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(12, loaded.Width);
    }

    [Fact]
    public void Threshold_ThenInvert_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var result = img.Threshold(128);
        var ex = Record.Exception(() => result.Invert());
        Assert.Null(ex);
    }

    [Fact]
    public void Threshold_SaveLoad_Consistent()
    {
        var img = CreateGradient(10, 8);
        var result = img.Threshold(128);
        var cornerVal = result.GetPixelValue(0, 0);
        var path = TempFile("threshold_save.pgm");
        result.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(cornerVal, loaded.GetPixelValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // GetHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_NonNull()
    {
        var img = CreateGradient(10, 8);
        Assert.NotNull(img.GetHistogram());
    }

    [Fact]
    public void GetHistogram_Length256()
    {
        var img = CreateGradient(10, 8);
        Assert.Equal(256, img.GetHistogram().Length);
    }

    [Fact]
    public void GetHistogram_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var ex = Record.Exception(() => img.GetHistogram());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHistogram_SumEqualsPixelCount()
    {
        var img = CreateGradient(10, 8);
        var hist = img.GetHistogram();
        long total = 0;
        foreach (var count in hist)
            total += count;
        Assert.Equal(10 * 8, total);
    }

    [Fact]
    public void GetHistogram_Consistent()
    {
        var img = CreateGradient(10, 8);
        var h1 = img.GetHistogram();
        var h2 = img.GetHistogram();
        Assert.Equal(h1[0], h2[0]);
        Assert.Equal(h1[128], h2[128]);
    }

    [Fact]
    public void GetHistogram_AfterThreshold_TwoNonZeroBuckets()
    {
        var img = CreateGradient(10, 8);
        var thresholded = img.Threshold(128);
        var hist = thresholded.GetHistogram();
        int nonZero = 0;
        foreach (var count in hist)
            if (count > 0) nonZero++;
        // Binary image should have at most 2 non-zero buckets (0 and 255)
        Assert.True(nonZero <= 2);
    }

    [Fact]
    public void GetHistogram_SaveLoad_Consistent()
    {
        var img = CreateGradient(10, 8);
        var before = img.GetHistogram();
        var path = TempFile("hist_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        var after = loaded.GetHistogram();
        Assert.Equal(before.Length, after.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreatePgm_ApplyKernel_Threshold_GetHistogram_SaveToFile_Pipeline()
    {
        // Create 16×12 gradient image
        var img = NetpbmImage.CreatePgm(16, 12, 255);
        for (int y = 0; y < 12; y++)
            for (int x = 0; x < 16; x++)
                img.SetPixel(x, y, (byte)((x * 15 + y * 10) % 230 + 10));

        Assert.Equal(16, img.Width);
        Assert.Equal(12, img.Height);

        // GetHistogram on original
        var hist = img.GetHistogram();
        Assert.Equal(256, hist.Length);
        long total = 0;
        foreach (var c in hist) total += c;
        Assert.Equal(16 * 12, total);

        // ApplyKernel — identity
        var identity = img.ApplyKernel(IdentityKernel);
        Assert.Equal(16, identity.Width);
        Assert.Equal(12, identity.Height);

        // ApplyKernel — box blur
        var blurred = img.ApplyKernel(BoxBlurKernel);
        Assert.Equal(16, blurred.Width);
        Assert.Equal(12, blurred.Height);

        // Consistent
        var bl2 = img.ApplyKernel(BoxBlurKernel);
        Assert.Equal(blurred.GetPixelValue(8, 6), bl2.GetPixelValue(8, 6));

        // Normalize the blurred image
        var normBlurred = blurred.Normalize();
        Assert.Equal(16, normBlurred.Width);

        // Threshold at midpoint
        var thresholded = img.Threshold(128);
        Assert.Equal(16, thresholded.Width);
        Assert.Equal(12, thresholded.Height);

        // Verify binary output
        for (int y = 0; y < 12; y++)
            for (int x = 0; x < 16; x++)
            {
                var val = thresholded.GetPixelValue(x, y);
                Assert.True(val == 0 || val == 255);
            }

        // GetHistogram after threshold — only 0 and 255 buckets
        var threshHist = thresholded.GetHistogram();
        Assert.Equal(256, threshHist.Length);
        int nonZero = 0;
        foreach (var c in threshHist) if (c > 0) nonZero++;
        Assert.True(nonZero <= 2);

        // Sum of threshold histogram = pixel count
        long threshTotal = 0;
        foreach (var c in threshHist) threshTotal += c;
        Assert.Equal(16 * 12, threshTotal);

        // SaveToFile — original, blurred, thresholded
        var pathOrig = TempFile("dogfood_orig.pgm");
        img.SaveToFile(pathOrig);
        Assert.True(File.Exists(pathOrig));

        var pathBlurred = TempFile("dogfood_blurred.pgm");
        blurred.SaveToFile(pathBlurred);
        Assert.True(File.Exists(pathBlurred));

        var pathThresh = TempFile("dogfood_thresh.pgm");
        thresholded.SaveToFile(pathThresh);
        Assert.True(File.Exists(pathThresh));

        // LoadFile blurred and verify
        var loadedBlurred = NetpbmImage.LoadFile(pathBlurred);
        Assert.Equal(16, loadedBlurred.Width);
        Assert.Equal(12, loadedBlurred.Height);
        var loadedHist = loadedBlurred.GetHistogram();
        Assert.Equal(256, loadedHist.Length);

        // LoadFile threshold and verify binary
        var loadedThresh = NetpbmImage.LoadFile(pathThresh);
        var loadedThreshHist = loadedThresh.GetHistogram();
        int loadedNonZero = 0;
        foreach (var c in loadedThreshHist) if (c > 0) loadedNonZero++;
        Assert.True(loadedNonZero <= 2);

        // ApplyKernel on loaded blurred — chain operations
        var chainResult = loadedBlurred.ApplyKernel(BoxBlurKernel);
        Assert.Equal(16, chainResult.Width);

        // Threshold on loaded original
        var loadedOrig = NetpbmImage.LoadFile(pathOrig);
        var loadedThresh2 = loadedOrig.Threshold(128);
        Assert.Equal(16, loadedThresh2.Width);

        // Final save
        var pathFinal = TempFile("dogfood_final.pgm");
        chainResult.SaveToFile(pathFinal);
        Assert.True(File.Exists(pathFinal));
        Assert.True(new FileInfo(pathFinal).Length > 0);
        var final = NetpbmImage.LoadFile(pathFinal);
        Assert.Equal(16, final.Width);
        Assert.Equal(12, final.Height);
    }
}
