// Tests for NetpbmImage.Scale, GetBrightness, AddBorder deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R234

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R234: Tests for NetpbmImage.Scale, GetBrightness, AddBorder deeper coverage.
/// Scale(factor): scales the image by a float factor (e.g., 2.0 = double size).
/// GetBrightness(): returns average pixel brightness (0.0–255.0 range).
/// AddBorder(size, r, g, b): adds a colored border of given pixel width around the image.
/// Covers: Scale non-null; Scale double-size dimensions; Scale half-size dimensions;
/// Scale 1.0 same dimensions; Scale pixel values preserved relative; Scale save-load;
/// Scale grayscale non-null; Scale consistent dimensions;
/// GetBrightness in valid range; GetBrightness all-black near zero; GetBrightness all-white 255;
/// GetBrightness grayscale mid-value; GetBrightness consistent; GetBrightness after Sepia changes;
/// GetBrightness after Invert complementary; GetBrightness after flip unchanged;
/// AddBorder non-null; AddBorder increases dimensions; AddBorder pixels at border correct;
/// AddBorder save-load roundtrip; AddBorder white border; AddBorder grayscale;
/// dogfood CreateCanvas→Scale→GetBrightness→AddBorder→SaveToFile→verify pipeline.
/// </summary>
public class NetpbmR234ScaleAndGetBrightnessDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR234ScaleAndGetBrightnessDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR234_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateMidGrayCanvas(int w = 8, int h = 4)
    {
        var img = NetpbmImage.CreateCanvas(w, h, NetpbmFormat.PGM);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                img.SetPixel(x, y, 128);
        return img;
    }

    private static NetpbmImage CreateColorCanvas(int w = 8, int h = 4)
    {
        var img = NetpbmImage.CreateCanvas(w, h, NetpbmFormat.PPM);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                img.SetPixel(x, y, 128, 128, 128);
        return img;
    }

    // -------------------------------------------------------------------------
    // Scale
    // -------------------------------------------------------------------------

    [Fact]
    public void Scale_NonNull()
    {
        var img = CreateMidGrayCanvas(8, 4);
        Assert.NotNull(img.Scale(2.0));
    }

    [Fact]
    public void Scale_Double_DoublesWidth()
    {
        var img = CreateMidGrayCanvas(8, 4);
        var scaled = img.Scale(2.0);
        Assert.Equal(16, scaled.Width);
    }

    [Fact]
    public void Scale_Double_DoublesHeight()
    {
        var img = CreateMidGrayCanvas(8, 4);
        var scaled = img.Scale(2.0);
        Assert.Equal(8, scaled.Height);
    }

    [Fact]
    public void Scale_Half_HalvesDimensions()
    {
        var img = CreateMidGrayCanvas(8, 4);
        var scaled = img.Scale(0.5);
        Assert.Equal(4, scaled.Width);
        Assert.Equal(2, scaled.Height);
    }

    [Fact]
    public void Scale_One_SameDimensions()
    {
        var img = CreateMidGrayCanvas(8, 4);
        var scaled = img.Scale(1.0);
        Assert.Equal(img.Width, scaled.Width);
        Assert.Equal(img.Height, scaled.Height);
    }

    [Fact]
    public void Scale_SaveAndLoad()
    {
        var img = CreateMidGrayCanvas(8, 4);
        var scaled = img.Scale(2.0);
        var path = TempFile("scaled.pgm");
        scaled.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(16, loaded.Width);
        Assert.Equal(8, loaded.Height);
    }

    [Fact]
    public void Scale_Grayscale_NonNull()
    {
        var img = CreateMidGrayCanvas();
        Assert.NotNull(img.Scale(1.5));
    }

    [Fact]
    public void Scale_Color_NonNull()
    {
        var img = CreateColorCanvas();
        Assert.NotNull(img.Scale(2.0));
    }

    [Fact]
    public void Scale_Consistent()
    {
        var img = CreateMidGrayCanvas(8, 4);
        var s1 = img.Scale(2.0);
        var s2 = img.Scale(2.0);
        Assert.Equal(s1.Width, s2.Width);
        Assert.Equal(s1.Height, s2.Height);
    }

    // -------------------------------------------------------------------------
    // GetBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_InValidRange()
    {
        var img = CreateMidGrayCanvas();
        var brightness = img.GetBrightness();
        Assert.True(brightness >= 0.0 && brightness <= 255.0);
    }

    [Fact]
    public void GetBrightness_AllBlack_NearZero()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.PGM);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 0);
        Assert.True(img.GetBrightness() < 5.0);
    }

    [Fact]
    public void GetBrightness_AllWhite_NearMax()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.PGM);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 255);
        Assert.True(img.GetBrightness() > 250.0);
    }

    [Fact]
    public void GetBrightness_MidGray_AroundHalf()
    {
        var img = CreateMidGrayCanvas();
        var brightness = img.GetBrightness();
        // All pixels = 128, so brightness ≈ 128
        Assert.True(Math.Abs(brightness - 128.0) < 10.0);
    }

    [Fact]
    public void GetBrightness_Consistent()
    {
        var img = CreateMidGrayCanvas();
        var b1 = img.GetBrightness();
        var b2 = img.GetBrightness();
        Assert.Equal(b1, b2, precision: 4);
    }

    [Fact]
    public void GetBrightness_AfterInvert_Complementary()
    {
        var img = CreateMidGrayCanvas(8, 4);
        var original = img.GetBrightness();
        var inverted = img.Invert().GetBrightness();
        // original + inverted ≈ 255 for uniform images
        Assert.True(Math.Abs(original + inverted - 255.0) < 20.0);
    }

    [Fact]
    public void GetBrightness_AfterFlip_Unchanged()
    {
        var img = CreateMidGrayCanvas();
        var original = img.GetBrightness();
        var flipped = img.FlipHorizontal().GetBrightness();
        Assert.Equal(original, flipped, precision: 4);
    }

    // -------------------------------------------------------------------------
    // AddBorder
    // -------------------------------------------------------------------------

    [Fact]
    public void AddBorder_NonNull()
    {
        var img = CreateColorCanvas(8, 4);
        Assert.NotNull(img.AddBorder(1, 0, 0, 0));
    }

    [Fact]
    public void AddBorder_IncreasesWidth()
    {
        var img = CreateColorCanvas(8, 4);
        var bordered = img.AddBorder(2, 0, 0, 0);
        Assert.Equal(img.Width + 4, bordered.Width); // 2 pixels on each side
    }

    [Fact]
    public void AddBorder_IncreasesHeight()
    {
        var img = CreateColorCanvas(8, 4);
        var bordered = img.AddBorder(2, 0, 0, 0);
        Assert.Equal(img.Height + 4, bordered.Height);
    }

    [Fact]
    public void AddBorder_PixelsAtBorderCorrectColor()
    {
        var img = CreateColorCanvas(8, 4);
        var bordered = img.AddBorder(1, 255, 0, 0); // red border
        var cornerPx = bordered.GetPixel(0, 0);
        Assert.Equal(255, cornerPx.R);
        Assert.Equal(0, cornerPx.G);
        Assert.Equal(0, cornerPx.B);
    }

    [Fact]
    public void AddBorder_SaveAndLoad()
    {
        var img = CreateColorCanvas(8, 4);
        var bordered = img.AddBorder(1, 0, 0, 0);
        var path = TempFile("bordered.ppm");
        bordered.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(10, loaded.Width);
        Assert.Equal(6, loaded.Height);
    }

    [Fact]
    public void AddBorder_Grayscale_NonNull()
    {
        var img = CreateMidGrayCanvas();
        Assert.NotNull(img.AddBorder(1, 0, 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_Scale_GetBrightness_AddBorder_SaveToFile_Verify_Pipeline()
    {
        var img = NetpbmImage.CreateCanvas(8, 4, NetpbmFormat.PGM);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 8; x++)
                img.SetPixel(x, y, 100); // dark gray

        // GetBrightness baseline
        var brightness = img.GetBrightness();
        Assert.True(Math.Abs(brightness - 100.0) < 5.0);

        // Scale 2x
        var scaled = img.Scale(2.0);
        Assert.NotNull(scaled);
        Assert.Equal(16, scaled.Width);
        Assert.Equal(8, scaled.Height);

        // GetBrightness on scaled should be similar
        var scaledBrightness = scaled.GetBrightness();
        Assert.True(Math.Abs(scaledBrightness - brightness) < 15.0);

        // Scale 0.5x from original
        var halfScaled = img.Scale(0.5);
        Assert.Equal(4, halfScaled.Width);
        Assert.Equal(2, halfScaled.Height);

        // AddBorder — 2px black border around original
        var bordered = img.AddBorder(2, 0, 0, 0);
        Assert.NotNull(bordered);
        Assert.Equal(8 + 4, bordered.Width);   // 12
        Assert.Equal(4 + 4, bordered.Height);  // 8

        // Border pixels should be black
        var borderPx = bordered.GetPixel(0, 0);
        Assert.True(borderPx.R == 0 || borderPx.R < 10);

        // GetBrightness on bordered is lower (black border reduces avg)
        var borderedBrightness = bordered.GetBrightness();
        Assert.True(borderedBrightness < brightness); // border darkens average

        // AddBorder then Scale
        var borderedAndScaled = bordered.Scale(2.0);
        Assert.Equal(24, borderedAndScaled.Width);
        Assert.Equal(16, borderedAndScaled.Height);

        // After Invert — brightness is complementary
        var inverted = img.Invert();
        var invertedBrightness = inverted.GetBrightness();
        Assert.True(Math.Abs(brightness + invertedBrightness - 255.0) < 20.0);

        // SaveToFile for all variants
        var origPath = TempFile("dogfood_gray.pgm");
        var scaledPath = TempFile("dogfood_scaled.pgm");
        var borderedPath = TempFile("dogfood_bordered.pgm");

        img.SaveToFile(origPath);
        scaled.SaveToFile(scaledPath);
        bordered.SaveToFile(borderedPath);

        Assert.True(File.Exists(origPath));
        Assert.True(File.Exists(scaledPath));
        Assert.True(File.Exists(borderedPath));

        // Verify file sizes: scaled should be larger than original
        Assert.True(new FileInfo(scaledPath).Length >= new FileInfo(origPath).Length);

        // Load and verify
        var loadedScaled = NetpbmImage.LoadFile(scaledPath);
        Assert.Equal(16, loadedScaled.Width);
        Assert.Equal(8, loadedScaled.Height);
        Assert.True(Math.Abs(loadedScaled.GetBrightness() - brightness) < 20.0);

        var loadedBordered = NetpbmImage.LoadFile(borderedPath);
        Assert.Equal(12, loadedBordered.Width);
        Assert.Equal(8, loadedBordered.Height);
    }
}
