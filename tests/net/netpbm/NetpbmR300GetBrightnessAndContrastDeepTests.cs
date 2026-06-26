// Tests for NetpbmImage.GetBrightness, GetContrast, AdjustBrightness deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R300

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R300: Tests for NetpbmImage.GetBrightness, GetContrast, AdjustBrightness deeper.
/// GetBrightness(): returns the mean pixel intensity (0 = black, MaxVal = white).
/// GetContrast(): returns the standard deviation of pixel intensities.
/// AdjustBrightness(delta): returns a new image with each pixel intensity shifted by delta.
/// Covers: GetBrightness no-throw; GetBrightness in range; GetBrightness consistent;
/// GetBrightness zero for black; GetBrightness maxval for white; GetBrightness save-load;
/// GetContrast no-throw; GetContrast non-negative; GetContrast consistent;
/// GetContrast zero for uniform; GetContrast save-load;
/// AdjustBrightness no-throw; AdjustBrightness same dims; AdjustBrightness non-null;
/// AdjustBrightness consistent; AdjustBrightness save-load;
/// dogfood CreateImage→GetBrightness→GetContrast→AdjustBrightness→SaveToFile pipeline.
/// </summary>
public class NetpbmR300GetBrightnessAndContrastDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR300GetBrightnessAndContrastDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR300_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateMidGrayPgm()
    {
        // Uniform mid-gray (128)
        var path = TempFile("midgray.pgm");
        File.WriteAllText(path,
            "P2\n6 6\n255\n" +
            "128 128 128 128 128 128\n" +
            "128 128 128 128 128 128\n" +
            "128 128 128 128 128 128\n" +
            "128 128 128 128 128 128\n" +
            "128 128 128 128 128 128\n" +
            "128 128 128 128 128 128\n");
        return path;
    }

    private string CreateBlackPgm()
    {
        var path = TempFile("black.pgm");
        File.WriteAllText(path,
            "P2\n4 4\n255\n" +
            "0 0 0 0\n" +
            "0 0 0 0\n" +
            "0 0 0 0\n" +
            "0 0 0 0\n");
        return path;
    }

    private string CreateWhitePgm()
    {
        var path = TempFile("white.pgm");
        File.WriteAllText(path,
            "P2\n4 4\n255\n" +
            "255 255 255 255\n" +
            "255 255 255 255\n" +
            "255 255 255 255\n" +
            "255 255 255 255\n");
        return path;
    }

    private string CreateMixedPgm()
    {
        var path = TempFile("mixed.pgm");
        File.WriteAllText(path,
            "P2\n8 6\n255\n" +
            " 20  40  60  80 100 120 140 160\n" +
            " 30  50  70  90 110 130 150 170\n" +
            " 40  60  80 100 120 140 160 180\n" +
            " 50  70  90 110 130 150 170 190\n" +
            " 60  80 100 120 140 160 180 200\n" +
            " 70  90 110 130 150 170 190 210\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var ex = Record.Exception(() => img.GetBrightness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBrightness_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var b = img.GetBrightness();
        Assert.True(b >= 0.0);
        Assert.True(b <= img.MaxVal);
    }

    [Fact]
    public void GetBrightness_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        Assert.Equal(img.GetBrightness(), img.GetBrightness());
    }

    [Fact]
    public void GetBrightness_Zero_ForBlack()
    {
        var img = NetpbmImage.LoadFile(CreateBlackPgm());
        Assert.Equal(0.0, img.GetBrightness(), precision: 6);
    }

    [Fact]
    public void GetBrightness_MaxVal_ForWhite()
    {
        var img = NetpbmImage.LoadFile(CreateWhitePgm());
        Assert.Equal(255.0, img.GetBrightness(), precision: 6);
    }

    [Fact]
    public void GetBrightness_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var before = img.GetBrightness();
        var path = TempFile("br_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetBrightness(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetContrast
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContrast_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var ex = Record.Exception(() => img.GetContrast());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContrast_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        Assert.True(img.GetContrast() >= 0.0);
    }

    [Fact]
    public void GetContrast_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        Assert.Equal(img.GetContrast(), img.GetContrast());
    }

    [Fact]
    public void GetContrast_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateMidGrayPgm());
        Assert.Equal(0.0, img.GetContrast(), precision: 6);
    }

    [Fact]
    public void GetContrast_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var before = img.GetContrast();
        var path = TempFile("co_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetContrast(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // AdjustBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustBrightness_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var ex = Record.Exception(() => img.AdjustBrightness(10));
        Assert.Null(ex);
    }

    [Fact]
    public void AdjustBrightness_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var adjusted = img.AdjustBrightness(20);
        Assert.Equal(img.Width, adjusted.Width);
        Assert.Equal(img.Height, adjusted.Height);
    }

    [Fact]
    public void AdjustBrightness_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        Assert.NotNull(img.AdjustBrightness(-10));
    }

    [Fact]
    public void AdjustBrightness_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var a1 = img.AdjustBrightness(15);
        var a2 = img.AdjustBrightness(15);
        Assert.Equal(a1.Width, a2.Width);
        Assert.Equal(a1.Height, a2.Height);
        Assert.Equal(a1.GetBrightness(), a2.GetBrightness(), precision: 6);
    }

    [Fact]
    public void AdjustBrightness_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var adjusted = img.AdjustBrightness(10);
        var path = TempFile("ab_save.pgm");
        adjusted.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(adjusted.Width, loaded.Width);
        Assert.Equal(adjusted.Height, loaded.Height);
        Assert.Equal(adjusted.GetBrightness(), loaded.GetBrightness(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetBrightness_GetContrast_AdjustBrightness_SaveToFile_Pipeline()
    {
        // Medical X-ray simulation: chest scan with varied tissue densities
        var path = TempFile("dogfood_xray.pgm");
        File.WriteAllText(path,
            "P2\n12 10\n255\n" +
            " 20  25  30  35  40 180 185 188 182 186 190 192\n" +
            " 22  28  32  38  42 175 182 190 178 184 188 195\n" +
            " 25  30  35  40  45 120 125 128 122 126 130 132\n" +
            " 28  35  38  45  48  60  65  68  62  66  70  72\n" +
            " 30  38  42  48  52  55  60  62  58  62  65  68\n" +
            " 32  40  45  50  55  58  62  65  60  64  68  70\n" +
            " 35  42  48  52  58  60  65  68  62  66  70  72\n" +
            " 38  45  50  55  60  62  68  70  65  68  72  75\n" +
            " 40  48  52  58  62  65  70  72  68  70  74  78\n" +
            " 42  50  55  60  65  68  72  75  70  72  76  80\n");

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(10, img.Height);
        Assert.Equal(120, img.GetPixelCount());

        // GetBrightness — in range
        var brightness = img.GetBrightness();
        Assert.True(brightness >= 0.0);
        Assert.True(brightness <= img.MaxVal);
        Assert.Equal(brightness, img.GetBrightness()); // consistent

        // GetContrast — positive (varied pixel values)
        var contrast = img.GetContrast();
        Assert.True(contrast >= 0.0);
        Assert.Equal(contrast, img.GetContrast()); // consistent

        // AdjustBrightness — brighten by +30
        var brighter = img.AdjustBrightness(30);
        Assert.NotNull(brighter);
        Assert.Equal(img.Width, brighter.Width);
        Assert.Equal(img.Height, brighter.Height);
        // Brighter image should have higher or equal mean brightness
        Assert.True(brighter.GetBrightness() >= brightness);

        // AdjustBrightness — darken by -20
        var darker = img.AdjustBrightness(-20);
        Assert.NotNull(darker);
        Assert.Equal(img.Width, darker.Width);
        // Darker image should have lower or equal mean brightness
        Assert.True(darker.GetBrightness() <= brightness);

        // Black image
        var black = NetpbmImage.LoadFile(CreateBlackPgm());
        Assert.Equal(0.0, black.GetBrightness(), precision: 6);
        Assert.Equal(0.0, black.GetContrast(), precision: 6);
        var brightenedBlack = black.AdjustBrightness(50);
        Assert.Equal(black.Width, brightenedBlack.Width);

        // White image
        var white = NetpbmImage.LoadFile(CreateWhitePgm());
        Assert.Equal(255.0, white.GetBrightness(), precision: 6);
        Assert.Equal(0.0, white.GetContrast(), precision: 6);

        // Uniform mid-gray
        var midGray = NetpbmImage.LoadFile(CreateMidGrayPgm());
        Assert.Equal(0.0, midGray.GetContrast(), precision: 6);
        Assert.Equal(128.0, midGray.GetBrightness(), precision: 0);

        // SaveToFile — original
        var out1 = TempFile("dogfood_xray_out.pgm");
        img.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify brightness/contrast preserved
        var loaded = NetpbmImage.LoadFile(out1);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);
        Assert.Equal(brightness, loaded.GetBrightness(), precision: 6);
        Assert.Equal(contrast, loaded.GetContrast(), precision: 6);

        // Save brighter version
        var outBrighter = TempFile("dogfood_xray_bright.pgm");
        brighter.SaveToFile(outBrighter);
        Assert.True(File.Exists(outBrighter));
        var loadedBrighter = NetpbmImage.LoadFile(outBrighter);
        Assert.Equal(brighter.GetBrightness(), loadedBrighter.GetBrightness(), precision: 6);

        // Final save
        var out2 = TempFile("dogfood_xray_v2.pgm");
        darker.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.True(loaded2.GetBrightness() >= 0.0);
        Assert.True(loaded2.GetContrast() >= 0.0);
        var ex1 = Record.Exception(() => loaded2.AdjustBrightness(5));
        Assert.Null(ex1);
    }
}
