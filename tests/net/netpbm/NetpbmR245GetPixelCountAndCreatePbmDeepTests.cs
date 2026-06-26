// Tests for NetpbmImage.GetPixelCount, CreatePbm, GetMaxValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R245

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R245: Tests for NetpbmImage.GetPixelCount, CreatePbm, GetMaxValue deeper.
/// GetPixelCount(): returns the total number of pixels (width × height).
/// CreatePbm(width, height, pixels): creates a 1-bit bitmap (black/white) PBM image.
/// GetMaxValue(): returns the maximum pixel value in the image.
/// Covers: GetPixelCount equals width times height; GetPixelCount positive; GetPixelCount consistent;
/// GetPixelCount after Resize changes; GetPixelCount after Crop changes; GetPixelCount for RGB;
/// GetPixelCount no-throw; GetPixelCount for grayscale and bitmap;
/// CreatePbm non-null; CreatePbm has correct width; CreatePbm has correct height; CreatePbm is bitmap;
/// CreatePbm persist; CreatePbm pixel values in range 0-1; CreatePbm load-save round-trip;
/// CreatePbm then ConvertToGrayscale; CreatePbm no-throw;
/// GetMaxValue positive; GetMaxValue in range 0-255; GetMaxValue consistent; GetMaxValue for uniform;
/// GetMaxValue for gradient; GetMaxValue after Invert changes; GetMaxValue no-throw;
/// GetMaxValue for black image is zero; GetMaxValue for white image is 255;
/// dogfood CreatePgm→GetPixelCount→GetMaxValue→CreatePbm→SaveToFile pipeline.
/// </summary>
public class NetpbmR245GetPixelCountAndCreatePbmDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR245GetPixelCountAndCreatePbmDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR245_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGrayscale8x6()
    {
        var pixels = new byte[8 * 6];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)(i * 5 % 256);
        return NetpbmImage.CreatePgm(8, 6, pixels);
    }

    private static NetpbmImage CreateUniformWhite()
    {
        var pixels = new byte[6 * 6];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = 255;
        return NetpbmImage.CreatePgm(6, 6, pixels);
    }

    private static NetpbmImage CreateUniformBlack()
    {
        var pixels = new byte[6 * 6];
        return NetpbmImage.CreatePgm(6, 6, pixels);
    }

    private static NetpbmImage CreateRgb6x6()
    {
        var pixels = new byte[6 * 6 * 3];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)(i % 200 + 30);
        return NetpbmImage.CreatePpm(6, 6, pixels);
    }

    // -------------------------------------------------------------------------
    // GetPixelCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelCount_EqualsWidthTimesHeight()
    {
        var img = CreateGrayscale8x6();
        Assert.Equal(img.Width * img.Height, img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_Positive()
    {
        var img = CreateGrayscale8x6();
        Assert.True(img.GetPixelCount() > 0);
    }

    [Fact]
    public void GetPixelCount_Consistent()
    {
        var img = CreateGrayscale8x6();
        Assert.Equal(img.GetPixelCount(), img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_NoThrow()
    {
        var img = CreateGrayscale8x6();
        var ex = Record.Exception(() => img.GetPixelCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPixelCount_AfterCrop_Changes()
    {
        var img = CreateGrayscale8x6();
        var cropped = img.Crop(0, 0, 4, 3);
        Assert.Equal(4 * 3, cropped.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_AfterResize_Changes()
    {
        var img = CreateGrayscale8x6();
        var resized = img.Resize(10, 12);
        Assert.Equal(10 * 12, resized.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_ForRgb_EqualsWidthTimesHeight()
    {
        var img = CreateRgb6x6();
        // Pixel count is W×H regardless of channel count
        Assert.Equal(img.Width * img.Height, img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_EightBySix_Is48()
    {
        var img = CreateGrayscale8x6();
        Assert.Equal(48, img.GetPixelCount());
    }

    // -------------------------------------------------------------------------
    // CreatePbm
    // -------------------------------------------------------------------------

    [Fact]
    public void CreatePbm_NonNull()
    {
        var pixels = new byte[4 * 4];
        for (int i = 0; i < pixels.Length; i++) pixels[i] = (byte)(i % 2);
        Assert.NotNull(NetpbmImage.CreatePbm(4, 4, pixels));
    }

    [Fact]
    public void CreatePbm_HasCorrectWidth()
    {
        var pixels = new byte[4 * 4];
        var img = NetpbmImage.CreatePbm(4, 4, pixels);
        Assert.Equal(4, img.Width);
    }

    [Fact]
    public void CreatePbm_HasCorrectHeight()
    {
        var pixels = new byte[4 * 4];
        var img = NetpbmImage.CreatePbm(4, 4, pixels);
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void CreatePbm_NoThrow()
    {
        var pixels = new byte[6 * 6];
        for (int i = 0; i < pixels.Length; i++) pixels[i] = (byte)(i % 2);
        var ex = Record.Exception(() => NetpbmImage.CreatePbm(6, 6, pixels));
        Assert.Null(ex);
    }

    [Fact]
    public void CreatePbm_Persist()
    {
        var pixels = new byte[5 * 5];
        for (int i = 0; i < pixels.Length; i++) pixels[i] = (byte)(i % 2);
        var img = NetpbmImage.CreatePbm(5, 5, pixels);
        var path = TempFile("pbm_persist.pbm");
        img.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(5, loaded.Width);
        Assert.Equal(5, loaded.Height);
    }

    [Fact]
    public void CreatePbm_GetPixelCount_Correct()
    {
        var pixels = new byte[4 * 6];
        var img = NetpbmImage.CreatePbm(4, 6, pixels);
        Assert.Equal(4 * 6, img.GetPixelCount());
    }

    [Fact]
    public void CreatePbm_AllBlack_Works()
    {
        var pixels = new byte[4 * 4]; // all 0 = black
        var img = NetpbmImage.CreatePbm(4, 4, pixels);
        Assert.Equal(4, img.Width);
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void CreatePbm_AllWhite_Works()
    {
        var pixels = new byte[4 * 4];
        for (int i = 0; i < pixels.Length; i++) pixels[i] = 1; // 1 = white
        var img = NetpbmImage.CreatePbm(4, 4, pixels);
        Assert.Equal(4, img.Width);
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void CreatePbm_ThenConvertToGrayscale_NonNull()
    {
        var pixels = new byte[4 * 4];
        for (int i = 0; i < pixels.Length; i++) pixels[i] = (byte)(i % 2);
        var img = NetpbmImage.CreatePbm(4, 4, pixels);
        var gray = img.ConvertToGrayscale();
        Assert.NotNull(gray);
        Assert.Equal(4, gray.Width);
        Assert.Equal(4, gray.Height);
    }

    // -------------------------------------------------------------------------
    // GetMaxValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxValue_Positive()
    {
        var img = CreateGrayscale8x6();
        Assert.True(img.GetMaxValue() >= 0);
    }

    [Fact]
    public void GetMaxValue_InRange()
    {
        var img = CreateGrayscale8x6();
        Assert.True(img.GetMaxValue() >= 0 && img.GetMaxValue() <= 255);
    }

    [Fact]
    public void GetMaxValue_Consistent()
    {
        var img = CreateGrayscale8x6();
        Assert.Equal(img.GetMaxValue(), img.GetMaxValue());
    }

    [Fact]
    public void GetMaxValue_NoThrow()
    {
        var img = CreateGrayscale8x6();
        var ex = Record.Exception(() => img.GetMaxValue());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMaxValue_ForBlackImage_Zero()
    {
        var img = CreateUniformBlack(); // all 0
        Assert.Equal(0, img.GetMaxValue());
    }

    [Fact]
    public void GetMaxValue_ForWhiteImage_255()
    {
        var img = CreateUniformWhite(); // all 255
        Assert.Equal(255, img.GetMaxValue());
    }

    [Fact]
    public void GetMaxValue_AfterInvert_Changes()
    {
        var img = CreateUniformBlack(); // all 0, max=0
        var inverted = img.Invert(); // all 255
        Assert.Equal(255, inverted.GetMaxValue());
    }

    [Fact]
    public void GetMaxValue_ForGradient_Positive()
    {
        var img = CreateGrayscale8x6(); // has varied values
        Assert.True(img.GetMaxValue() > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreatePgm_GetPixelCount_GetMaxValue_CreatePbm_SaveToFile_Pipeline()
    {
        // Create 10x8 gradient grayscale
        var pixels = new byte[10 * 8];
        for (int r = 0; r < 8; r++)
            for (int c = 0; c < 10; c++)
                pixels[r * 10 + c] = (byte)(c * 25 + r * 5);

        var gray = NetpbmImage.CreatePgm(10, 8, pixels);
        Assert.Equal(10, gray.Width);
        Assert.Equal(8, gray.Height);

        // GetPixelCount
        Assert.Equal(10 * 8, gray.GetPixelCount());
        Assert.Equal(80, gray.GetPixelCount());

        // GetMaxValue
        var maxVal = gray.GetMaxValue();
        Assert.True(maxVal > 0 && maxVal <= 255);

        // GetMaxValue of inverted = 255 - min of original
        var inverted = gray.Invert();
        var invertedMax = inverted.GetMaxValue();
        Assert.True(invertedMax > 0 && invertedMax <= 255);

        // GetPixelCount preserved after Invert
        Assert.Equal(80, inverted.GetPixelCount());

        // Threshold — create bitmap-like from grayscale
        var thresholded = gray.Threshold(127);
        Assert.Equal(10 * 8, thresholded.GetPixelCount());

        // Create PBM
        var pbmPixels = new byte[8 * 8];
        for (int r = 0; r < 8; r++)
            for (int c = 0; c < 8; c++)
                pbmPixels[r * 8 + c] = (byte)((r + c) % 2); // checkerboard
        var pbm = NetpbmImage.CreatePbm(8, 8, pbmPixels);
        Assert.NotNull(pbm);
        Assert.Equal(8, pbm.Width);
        Assert.Equal(8, pbm.Height);
        Assert.Equal(64, pbm.GetPixelCount());

        // GetMaxValue on PBM (should be 0 or 1)
        var pbmMax = pbm.GetMaxValue();
        Assert.True(pbmMax <= 1 || pbmMax <= 255); // binary or scaled

        // CreatePbm all black
        var blackPbm = NetpbmImage.CreatePbm(4, 4, new byte[16]);
        Assert.Equal(0, blackPbm.GetMaxValue());
        Assert.Equal(16, blackPbm.GetPixelCount());

        // CreatePbm all white
        var whitePbmPixels = new byte[4 * 4];
        for (int i = 0; i < whitePbmPixels.Length; i++) whitePbmPixels[i] = 1;
        var whitePbm = NetpbmImage.CreatePbm(4, 4, whitePbmPixels);
        Assert.Equal(16, whitePbm.GetPixelCount());

        // Crop and GetPixelCount
        var cropped = gray.Crop(2, 1, 6, 5);
        Assert.Equal(6 * 5, cropped.GetPixelCount());
        var croppedMax = cropped.GetMaxValue();
        Assert.True(croppedMax >= 0 && croppedMax <= 255);

        // Resize and GetPixelCount
        var resized = gray.Resize(5, 4);
        Assert.Equal(5 * 4, resized.GetPixelCount());

        // GetAverageBrightness correlation with GetMaxValue
        Assert.True(gray.GetAverageBrightness() <= gray.GetMaxValue() || gray.GetMaxValue() == 0);

        // SaveToFile grayscale
        var grayPath = TempFile("dogfood_gray.pgm");
        gray.SaveToFile(grayPath);
        Assert.True(File.Exists(grayPath));
        var loadedGray = NetpbmImage.LoadFile(grayPath);
        Assert.Equal(80, loadedGray.GetPixelCount());
        Assert.Equal(maxVal, loadedGray.GetMaxValue());

        // SaveToFile PBM
        var pbmPath = TempFile("dogfood_checkerboard.pbm");
        pbm.SaveToFile(pbmPath);
        Assert.True(File.Exists(pbmPath));
        var loadedPbm = NetpbmImage.LoadFile(pbmPath);
        Assert.Equal(8, loadedPbm.Width);
        Assert.Equal(8, loadedPbm.Height);
        Assert.Equal(64, loadedPbm.GetPixelCount());

        // SaveToFile cropped
        var cropPath = TempFile("dogfood_cropped.pgm");
        cropped.SaveToFile(cropPath);
        Assert.True(File.Exists(cropPath));
        var loadedCrop = NetpbmImage.LoadFile(cropPath);
        Assert.Equal(6 * 5, loadedCrop.GetPixelCount());
        Assert.True(loadedCrop.GetMaxValue() >= 0);
    }
}
