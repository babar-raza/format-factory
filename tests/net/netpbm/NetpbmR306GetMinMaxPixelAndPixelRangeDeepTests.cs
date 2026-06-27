// Tests for NetpbmImage.GetMinPixel, GetMaxPixel, GetPixelRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R306

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R306: Tests for NetpbmImage.GetMinPixel, GetMaxPixel, GetPixelRange deeper.
/// GetMinPixel(): returns the minimum pixel value in the image.
/// GetMaxPixel(): returns the maximum pixel value in the image.
/// GetPixelRange(): returns the difference between max and min pixel values.
/// Covers: GetMinPixel no-throw; GetMinPixel non-negative; GetMinPixel consistent;
/// GetMinPixel zero for black image; GetMinPixel leq GetMaxPixel; GetMinPixel save-load;
/// GetMaxPixel no-throw; GetMaxPixel leq MaxVal; GetMaxPixel consistent;
/// GetMaxPixel MaxVal for white image; GetMaxPixel save-load;
/// GetPixelRange no-throw; GetPixelRange non-negative; GetPixelRange consistent;
/// GetPixelRange zero for uniform; GetPixelRange save-load;
/// dogfood CreateImage→GetMinPixel→GetMaxPixel→GetPixelRange→SaveToFile pipeline.
/// </summary>
public class NetpbmR306GetMinMaxPixelAndPixelRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR306GetMinMaxPixelAndPixelRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR306_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateGradientPgm()
    {
        var path = TempFile("gradient.pgm");
        // 16x1 horizontal gradient: 0..240 (step=16)
        var pixels = new byte[16];
        for (int i = 0; i < 16; i++) pixels[i] = (byte)(i * 16);
        var header = System.Text.Encoding.ASCII.GetBytes($"P5\n16 1\n255\n");
        using var fs = File.OpenWrite(path);
        fs.Write(header, 0, header.Length);
        fs.Write(pixels, 0, pixels.Length);
        return path;
    }

    private string CreateBlackPgm()
    {
        var path = TempFile("black.pgm");
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n8 8\n255\n");
        using var fs = File.OpenWrite(path);
        fs.Write(header, 0, header.Length);
        fs.Write(new byte[64], 0, 64);
        return path;
    }

    private string CreateWhitePgm()
    {
        var path = TempFile("white.pgm");
        var pixels = new byte[64];
        Array.Fill(pixels, (byte)255);
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n8 8\n255\n");
        using var fs = File.OpenWrite(path);
        fs.Write(header, 0, header.Length);
        fs.Write(pixels, 0, pixels.Length);
        return path;
    }

    private string CreateUniformMidPgm()
    {
        var path = TempFile("mid.pgm");
        var pixels = new byte[64];
        Array.Fill(pixels, (byte)128);
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n8 8\n255\n");
        using var fs = File.OpenWrite(path);
        fs.Write(header, 0, header.Length);
        fs.Write(pixels, 0, pixels.Length);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetMinPixel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMinPixel_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetMinPixel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMinPixel_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetMinPixel() >= 0);
    }

    [Fact]
    public void GetMinPixel_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetMinPixel(), img.GetMinPixel());
    }

    [Fact]
    public void GetMinPixel_Zero_ForBlackImage()
    {
        var img = NetpbmImage.LoadFile(CreateBlackPgm());
        Assert.Equal(0, img.GetMinPixel());
    }

    [Fact]
    public void GetMinPixel_Leq_GetMaxPixel()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetMinPixel() <= img.GetMaxPixel());
    }

    [Fact]
    public void GetMinPixel_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var before = img.GetMinPixel();
        var path = TempFile("min_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetMinPixel());
    }

    // -------------------------------------------------------------------------
    // GetMaxPixel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxPixel_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetMaxPixel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMaxPixel_LeqMaxVal()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetMaxPixel() <= img.MaxVal);
    }

    [Fact]
    public void GetMaxPixel_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetMaxPixel(), img.GetMaxPixel());
    }

    [Fact]
    public void GetMaxPixel_MaxVal_ForWhiteImage()
    {
        var img = NetpbmImage.LoadFile(CreateWhitePgm());
        Assert.Equal(img.MaxVal, img.GetMaxPixel());
    }

    [Fact]
    public void GetMaxPixel_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var before = img.GetMaxPixel();
        var path = TempFile("max_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetMaxPixel());
    }

    // -------------------------------------------------------------------------
    // GetPixelRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelRange_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetPixelRange());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPixelRange_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetPixelRange() >= 0);
    }

    [Fact]
    public void GetPixelRange_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetPixelRange(), img.GetPixelRange());
    }

    [Fact]
    public void GetPixelRange_Zero_ForUniformImage()
    {
        var img = NetpbmImage.LoadFile(CreateUniformMidPgm());
        Assert.Equal(0, img.GetPixelRange());
    }

    [Fact]
    public void GetPixelRange_Equals_MaxMinus_Min()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetMaxPixel() - img.GetMinPixel(), img.GetPixelRange());
    }

    [Fact]
    public void GetPixelRange_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var before = img.GetPixelRange();
        var path = TempFile("range_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetPixelRange());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMinMaxPixel_GetPixelRange_SaveToFile_Pipeline()
    {
        // Synthetic remote sensing — multispectral land classification scene
        // 12×10 image: water(10), urban(90), vegetation(60), bare_soil(40), shadow(0)
        var path = TempFile("dogfood_landcover.pgm");
        var pixels = new byte[12 * 10];
        int[] pattern = { 10, 90, 60, 40, 0, 128, 200, 80, 55, 180, 30, 240 };
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
                pixels[r * 12 + c] = (byte)((pattern[c] + r * 2) % 256);

        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using (var fs = File.OpenWrite(path)) { fs.Write(header); fs.Write(pixels); }

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(10, img.Height);
        Assert.Equal(255, img.MaxVal);

        // GetMinPixel
        var minPx = img.GetMinPixel();
        Assert.True(minPx >= 0);
        Assert.True(minPx <= img.MaxVal);
        Assert.Equal(minPx, img.GetMinPixel()); // consistent

        // GetMaxPixel
        var maxPx = img.GetMaxPixel();
        Assert.True(maxPx >= 0);
        Assert.True(maxPx <= img.MaxVal);
        Assert.Equal(maxPx, img.GetMaxPixel()); // consistent

        // Ordering invariant
        Assert.True(minPx <= maxPx);

        // GetPixelRange
        var range = img.GetPixelRange();
        Assert.True(range >= 0);
        Assert.Equal(maxPx - minPx, range);
        Assert.Equal(range, img.GetPixelRange()); // consistent

        // The land cover image has diverse values — range should be large
        Assert.True(range > 50);

        // GetMean / GetBrightness should be between min and max
        var mean = img.GetMeanPixelValue();
        Assert.True(mean >= minPx);
        Assert.True(mean <= maxPx);

        // SaveToFile
        var out1 = TempFile("dogfood_landcover_out.pgm");
        img.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(out1);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);
        Assert.Equal(minPx, loaded.GetMinPixel());
        Assert.Equal(maxPx, loaded.GetMaxPixel());
        Assert.Equal(range, loaded.GetPixelRange());

        // Black image baseline
        var black = NetpbmImage.LoadFile(CreateBlackPgm());
        Assert.Equal(0, black.GetMinPixel());
        Assert.Equal(0, black.GetMaxPixel());
        Assert.Equal(0, black.GetPixelRange());

        // White image baseline
        var white = NetpbmImage.LoadFile(CreateWhitePgm());
        Assert.Equal(255, white.GetMinPixel());
        Assert.Equal(255, white.GetMaxPixel());
        Assert.Equal(0, white.GetPixelRange());

        // Gradient image: min=0, max=240, range=240
        var grad = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(0, grad.GetMinPixel());
        Assert.Equal(240, grad.GetMaxPixel());
        Assert.Equal(240, grad.GetPixelRange());

        // Final save via AdjustBrightness (contrast stretch simulation)
        var out2 = TempFile("dogfood_landcover_stretched.pgm");
        var stretched = img.NormalizePixels(); // normalise to [0,255]
        stretched.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.True(loaded2.GetPixelRange() >= range); // stretching increases or preserves range
        var ex1 = Record.Exception(() => loaded2.GetMinPixel());
        var ex2 = Record.Exception(() => loaded2.GetMaxPixel());
        var ex3 = Record.Exception(() => loaded2.GetPixelRange());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
