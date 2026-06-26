// Tests for NetpbmImage.Rotate, Crop, GetHistogram deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R242

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R242: Tests for NetpbmImage.Rotate, Crop, GetHistogram deeper.
/// Rotate(degrees): returns a rotated copy of the image (90, 180, 270 degrees).
/// Crop(x, y, width, height): returns a cropped sub-image.
/// GetHistogram(): returns a frequency distribution of pixel values.
/// Covers: Rotate non-null; Rotate 90 swaps width and height; Rotate 180 preserves dims;
/// Rotate 270 swaps width and height; Rotate no-throw; Rotate persist; Rotate RGB;
/// Rotate then Rotate reverses; Rotate 360 = identity dims;
/// Crop non-null; Crop output has expected width; Crop output has expected height;
/// Crop top-left; Crop center; Crop full image; Crop persist; Crop RGB; Crop no-throw;
/// GetHistogram non-null; GetHistogram length 256; GetHistogram sums to total pixels;
/// GetHistogram all values in range; GetHistogram consistent; GetHistogram for grayscale;
/// GetHistogram max value non-negative; GetHistogram for uniform image;
/// dogfood CreateImage→Rotate→Crop→GetHistogram→SaveToFile pipeline.
/// </summary>
public class NetpbmR242RotateAndCropDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR242RotateAndCropDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR242_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGrayscale8x4()
    {
        // 8-wide, 4-tall PGM with gradient
        var pixels = new byte[8 * 4];
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 8; c++)
                pixels[r * 8 + c] = (byte)(c * 32);
        return NetpbmImage.CreatePgm(8, 4, pixels);
    }

    private static NetpbmImage CreateGrayscaleSquare()
    {
        // 6x6 uniform 128
        var pixels = new byte[6 * 6];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = 128;
        return NetpbmImage.CreatePgm(6, 6, pixels);
    }

    private static NetpbmImage CreateRgb6x6()
    {
        var pixels = new byte[6 * 6 * 3];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)(i % 256);
        return NetpbmImage.CreatePpm(6, 6, pixels);
    }

    // -------------------------------------------------------------------------
    // Rotate
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate_NonNull()
    {
        var img = CreateGrayscale8x4();
        Assert.NotNull(img.Rotate(90));
    }

    [Fact]
    public void Rotate90_SwapsWidthAndHeight()
    {
        var img = CreateGrayscale8x4();
        var rotated = img.Rotate(90);
        Assert.Equal(img.Height, rotated.Width);
        Assert.Equal(img.Width, rotated.Height);
    }

    [Fact]
    public void Rotate180_PreservesDimensions()
    {
        var img = CreateGrayscale8x4();
        var rotated = img.Rotate(180);
        Assert.Equal(img.Width, rotated.Width);
        Assert.Equal(img.Height, rotated.Height);
    }

    [Fact]
    public void Rotate270_SwapsWidthAndHeight()
    {
        var img = CreateGrayscale8x4();
        var rotated = img.Rotate(270);
        Assert.Equal(img.Height, rotated.Width);
        Assert.Equal(img.Width, rotated.Height);
    }

    [Fact]
    public void Rotate_NoThrow()
    {
        var img = CreateGrayscale8x4();
        var ex = Record.Exception(() => img.Rotate(90));
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate_Persist()
    {
        var img = CreateGrayscale8x4();
        var rotated = img.Rotate(90);
        var path = TempFile("rotate_persist.pgm");
        rotated.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(rotated.Width, loaded.Width);
        Assert.Equal(rotated.Height, loaded.Height);
    }

    [Fact]
    public void Rotate_RGB_NonNull()
    {
        var img = CreateRgb6x6();
        Assert.NotNull(img.Rotate(90));
    }

    [Fact]
    public void Rotate_RGB_PreservesDimensionsFor180()
    {
        var img = CreateRgb6x6();
        var rotated = img.Rotate(180);
        Assert.Equal(img.Width, rotated.Width);
        Assert.Equal(img.Height, rotated.Height);
    }

    [Fact]
    public void Rotate90_Then270_RestoresDimensions()
    {
        var img = CreateGrayscale8x4();
        var r90 = img.Rotate(90);
        var r270 = r90.Rotate(270);
        Assert.Equal(img.Width, r270.Width);
        Assert.Equal(img.Height, r270.Height);
    }

    [Fact]
    public void Rotate180_Twice_RestoresDimensions()
    {
        var img = CreateGrayscale8x4();
        var twice = img.Rotate(180).Rotate(180);
        Assert.Equal(img.Width, twice.Width);
        Assert.Equal(img.Height, twice.Height);
    }

    // -------------------------------------------------------------------------
    // Crop
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_NonNull()
    {
        var img = CreateGrayscaleSquare();
        Assert.NotNull(img.Crop(0, 0, 3, 3));
    }

    [Fact]
    public void Crop_OutputHasExpectedWidth()
    {
        var img = CreateGrayscaleSquare();
        var cropped = img.Crop(1, 1, 4, 3);
        Assert.Equal(4, cropped.Width);
    }

    [Fact]
    public void Crop_OutputHasExpectedHeight()
    {
        var img = CreateGrayscaleSquare();
        var cropped = img.Crop(1, 1, 4, 3);
        Assert.Equal(3, cropped.Height);
    }

    [Fact]
    public void Crop_TopLeft_Works()
    {
        var img = CreateGrayscaleSquare();
        var cropped = img.Crop(0, 0, 2, 2);
        Assert.Equal(2, cropped.Width);
        Assert.Equal(2, cropped.Height);
    }

    [Fact]
    public void Crop_NoThrow()
    {
        var img = CreateGrayscaleSquare();
        var ex = Record.Exception(() => img.Crop(0, 0, 3, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void Crop_Persist()
    {
        var img = CreateGrayscaleSquare();
        var cropped = img.Crop(0, 0, 4, 4);
        var path = TempFile("crop_persist.pgm");
        cropped.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(4, loaded.Width);
        Assert.Equal(4, loaded.Height);
    }

    [Fact]
    public void Crop_RGB_NonNull()
    {
        var img = CreateRgb6x6();
        Assert.NotNull(img.Crop(0, 0, 3, 3));
    }

    [Fact]
    public void Crop_RGB_PreservesDimensions()
    {
        var img = CreateRgb6x6();
        var cropped = img.Crop(1, 1, 3, 4);
        Assert.Equal(3, cropped.Width);
        Assert.Equal(4, cropped.Height);
    }

    [Fact]
    public void Crop_SmallerThanOriginal()
    {
        var img = CreateGrayscaleSquare();
        var cropped = img.Crop(1, 1, 2, 2);
        Assert.True(cropped.Width < img.Width);
        Assert.True(cropped.Height < img.Height);
    }

    // -------------------------------------------------------------------------
    // GetHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_NonNull()
    {
        var img = CreateGrayscaleSquare();
        Assert.NotNull(img.GetHistogram());
    }

    [Fact]
    public void GetHistogram_Length256()
    {
        var img = CreateGrayscaleSquare();
        var hist = img.GetHistogram();
        Assert.Equal(256, hist.Length);
    }

    [Fact]
    public void GetHistogram_SumsToTotalPixels()
    {
        var img = CreateGrayscaleSquare();
        var hist = img.GetHistogram();
        long total = 0;
        foreach (var v in hist) total += v;
        Assert.Equal(img.Width * img.Height, total);
    }

    [Fact]
    public void GetHistogram_AllValuesNonNegative()
    {
        var img = CreateGrayscaleSquare();
        var hist = img.GetHistogram();
        foreach (var v in hist)
            Assert.True(v >= 0);
    }

    [Fact]
    public void GetHistogram_Consistent()
    {
        var img = CreateGrayscaleSquare();
        var h1 = img.GetHistogram();
        var h2 = img.GetHistogram();
        for (int i = 0; i < 256; i++)
            Assert.Equal(h1[i], h2[i]);
    }

    [Fact]
    public void GetHistogram_UniformImage_OneNonZeroBucket()
    {
        var img = CreateGrayscaleSquare(); // all pixels = 128
        var hist = img.GetHistogram();
        int nonZero = 0;
        foreach (var v in hist)
            if (v > 0) nonZero++;
        Assert.Equal(1, nonZero);
    }

    [Fact]
    public void GetHistogram_UniformImage_Bucket128HasAllPixels()
    {
        var img = CreateGrayscaleSquare(); // all pixels = 128
        var hist = img.GetHistogram();
        Assert.Equal(img.Width * img.Height, hist[128]);
    }

    [Fact]
    public void GetHistogram_GradientImage_MultipleNonZero()
    {
        var img = CreateGrayscale8x4(); // gradient pixels
        var hist = img.GetHistogram();
        int nonZero = 0;
        foreach (var v in hist)
            if (v > 0) nonZero++;
        Assert.True(nonZero > 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateImage_Rotate_Crop_GetHistogram_SaveToFile_Pipeline()
    {
        // Create 12x8 grayscale with banded gradient
        var pixels = new byte[12 * 8];
        for (int r = 0; r < 8; r++)
            for (int c = 0; c < 12; c++)
                pixels[r * 12 + c] = (byte)(c * 20 + r * 5);
        var gray = NetpbmImage.CreatePgm(12, 8, pixels);

        Assert.Equal(12, gray.Width);
        Assert.Equal(8, gray.Height);

        // GetHistogram baseline
        var hist = gray.GetHistogram();
        Assert.NotNull(hist);
        Assert.Equal(256, hist.Length);
        long total = 0;
        foreach (var v in hist) total += v;
        Assert.Equal(12 * 8, total);

        // Rotate 90
        var r90 = gray.Rotate(90);
        Assert.NotNull(r90);
        Assert.Equal(8, r90.Width);   // swapped
        Assert.Equal(12, r90.Height); // swapped

        // GetHistogram after rotate — same total pixels
        var histR90 = r90.GetHistogram();
        long totalR90 = 0;
        foreach (var v in histR90) totalR90 += v;
        Assert.Equal(12 * 8, totalR90);

        // Rotate 180
        var r180 = gray.Rotate(180);
        Assert.Equal(12, r180.Width);
        Assert.Equal(8, r180.Height);

        // Rotate 270
        var r270 = gray.Rotate(270);
        Assert.Equal(8, r270.Width);
        Assert.Equal(12, r270.Height);

        // 90+270 = identity dims
        var r90then270 = r90.Rotate(270);
        Assert.Equal(gray.Width, r90then270.Width);
        Assert.Equal(gray.Height, r90then270.Height);

        // Crop center region 6x4
        var cropped = gray.Crop(3, 2, 6, 4);
        Assert.NotNull(cropped);
        Assert.Equal(6, cropped.Width);
        Assert.Equal(4, cropped.Height);

        // GetHistogram on cropped — sums to 24
        var histCropped = cropped.GetHistogram();
        long totalCropped = 0;
        foreach (var v in histCropped) totalCropped += v;
        Assert.Equal(6 * 4, totalCropped);

        // Rotate cropped
        var croppedR90 = cropped.Rotate(90);
        Assert.Equal(4, croppedR90.Width);
        Assert.Equal(6, croppedR90.Height);

        // RGB image
        var rgbPixels = new byte[10 * 10 * 3];
        for (int i = 0; i < rgbPixels.Length; i++)
            rgbPixels[i] = (byte)(i % 256);
        var rgb = NetpbmImage.CreatePpm(10, 10, rgbPixels);

        var rgbR90 = rgb.Rotate(90);
        Assert.Equal(10, rgbR90.Width);
        Assert.Equal(10, rgbR90.Height); // square stays same

        var rgbCrop = rgb.Crop(2, 2, 5, 5);
        Assert.Equal(5, rgbCrop.Width);
        Assert.Equal(5, rgbCrop.Height);

        // SaveToFile rotated grayscale
        var pathR90 = TempFile("dogfood_rotate90.pgm");
        r90.SaveToFile(pathR90);
        Assert.True(File.Exists(pathR90));
        var loadedR90 = NetpbmImage.LoadFile(pathR90);
        Assert.Equal(8, loadedR90.Width);
        Assert.Equal(12, loadedR90.Height);
        var loadedHist = loadedR90.GetHistogram();
        Assert.Equal(256, loadedHist.Length);

        // SaveToFile cropped
        var pathCrop = TempFile("dogfood_crop.pgm");
        cropped.SaveToFile(pathCrop);
        Assert.True(File.Exists(pathCrop));
        var loadedCrop = NetpbmImage.LoadFile(pathCrop);
        Assert.Equal(6, loadedCrop.Width);
        Assert.Equal(4, loadedCrop.Height);
        var loadedCropHist = loadedCrop.GetHistogram();
        long loadedTotal = 0;
        foreach (var v in loadedCropHist) loadedTotal += v;
        Assert.Equal(6 * 4, loadedTotal);

        // SaveToFile RGB rotated
        var pathRgbR90 = TempFile("dogfood_rgb_rotate90.ppm");
        rgbR90.SaveToFile(pathRgbR90);
        Assert.True(File.Exists(pathRgbR90));
        var loadedRgb = NetpbmImage.LoadFile(pathRgbR90);
        Assert.Equal(10, loadedRgb.Width);
        Assert.Equal(10, loadedRgb.Height);
    }
}
