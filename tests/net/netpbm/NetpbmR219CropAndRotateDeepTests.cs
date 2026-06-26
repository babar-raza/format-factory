// Tests for NetpbmImage.Crop, Rotate, GetPixel deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R219

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R219: Tests for NetpbmImage.Crop, Rotate, GetPixel deeper coverage.
/// Crop(x, y, width, height): crops the image to the given rectangle.
/// Rotate(degrees): rotates the image by the given degrees.
/// Covers: Crop non-null; Crop dims match crop area; Crop pixel count = w*h;
/// Crop at origin; Crop to full size same as original dims;
/// Crop then SaveToFile creates file; Rotate non-null; Rotate 90 dims flipped or same;
/// Rotate 180 same dims; Rotate 0 no-op dims same; Rotate then SaveToFile;
/// Rotate double 180 same dims; GetPixel uniform canvas consistent;
/// GetPixel after Crop at origin; GetPixel after Rotate;
/// dogfood CreateCanvas→DrawLine→Crop→Rotate→GetPixel→SaveToFile→LoadFile pipeline.
/// </summary>
public class NetpbmR219CropAndRotateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR219CropAndRotateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR219_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // Crop
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        Assert.NotNull(img.Crop(0, 0, 8, 8));
    }

    [Fact]
    public void Crop_DimsMatchCropArea()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        var cropped = img.Crop(0, 0, 8, 6);
        Assert.Equal(8, cropped.Width);
        Assert.Equal(6, cropped.Height);
    }

    [Fact]
    public void Crop_PixelCountEqualsWidthTimesHeight()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        var cropped = img.Crop(2, 2, 6, 4);
        Assert.Equal(6 * 4, cropped.PixelCount);
    }

    [Fact]
    public void Crop_AtOrigin_NoThrow()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        var ex = Record.Exception(() => img.Crop(0, 0, 8, 8));
        Assert.Null(ex);
    }

    [Fact]
    public void Crop_ToFullSize_SameDims()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var cropped = img.Crop(0, 0, 8, 8);
        Assert.Equal(8, cropped.Width);
        Assert.Equal(8, cropped.Height);
    }

    [Fact]
    public void Crop_ThenSaveToFile_CreatesFile()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        var cropped = img.Crop(2, 2, 8, 8);
        var path = TempFile("cropped.pgm");
        cropped.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void Crop_SmallArea_CorrectDims()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        var cropped = img.Crop(7, 7, 2, 2);
        Assert.Equal(2, cropped.Width);
        Assert.Equal(2, cropped.Height);
        Assert.Equal(4, cropped.PixelCount);
    }

    // -------------------------------------------------------------------------
    // Rotate
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        Assert.NotNull(img.Rotate(90));
    }

    [Fact]
    public void Rotate_180_SameDims()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var rotated = img.Rotate(180);
        Assert.Equal(8, rotated.Width);
        Assert.Equal(8, rotated.Height);
    }

    [Fact]
    public void Rotate_0_NoOpDims()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var rotated = img.Rotate(0);
        Assert.Equal(8, rotated.Width);
        Assert.Equal(8, rotated.Height);
    }

    [Fact]
    public void Rotate_360_SameDims()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var rotated = img.Rotate(360);
        Assert.Equal(8, rotated.Width);
        Assert.Equal(8, rotated.Height);
    }

    [Fact]
    public void Rotate_ThenSaveToFile_CreatesFile()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var rotated = img.Rotate(90);
        var path = TempFile("rotated.pgm");
        rotated.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void Rotate_Double180_SameDimsAsOriginal()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var rotated = img.Rotate(180).Rotate(180);
        Assert.Equal(8, rotated.Width);
        Assert.Equal(8, rotated.Height);
    }

    [Fact]
    public void Rotate_NoThrow_ForAllAngles()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        foreach (var angle in new[] { 0, 90, 180, 270, 360 })
        {
            var ex = Record.Exception(() => img.Rotate(angle));
            Assert.Null(ex);
        }
    }

    // -------------------------------------------------------------------------
    // GetPixel after transformations
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixel_AfterCrop_AtOrigin_ConsistentWithOriginal()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 128);
        var cropped = img.Crop(0, 0, 8, 8);
        Assert.Equal(128, cropped.GetPixel(0, 0));
    }

    [Fact]
    public void GetPixel_AfterRotate180_UniformCanvas()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 150);
        var rotated = img.Rotate(180);
        Assert.Equal(150, rotated.GetPixel(0, 0));
        Assert.Equal(150, rotated.GetPixel(7, 7));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_DrawLine_Crop_Rotate_GetPixel_SaveToFile_LoadFile_Pipeline()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);

        // DrawLine
        img.DrawLine(0, 0, 15, 15, 50);
        img.DrawLine(0, 15, 15, 0, 100);

        // Crop to top-left quadrant
        var cropped = img.Crop(0, 0, 8, 8);
        Assert.Equal(8, cropped.Width);
        Assert.Equal(8, cropped.Height);
        Assert.Equal(64, cropped.PixelCount);

        // GetPixel on cropped
        var pixel = cropped.GetPixel(0, 0);
        Assert.True(pixel >= 0 && pixel <= 255);

        // Rotate 180
        var rotated = cropped.Rotate(180);
        Assert.Equal(8, rotated.Width);
        Assert.Equal(8, rotated.Height);

        // GetPixel after rotate
        var rPixel = rotated.GetPixel(0, 0);
        Assert.True(rPixel >= 0 && rPixel <= 255);

        // SaveToFile
        var path = TempFile("crop_rotate.pgm");
        rotated.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile
        var loaded = NetpbmImage.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.Equal(8, loaded.Width);
        Assert.Equal(8, loaded.Height);
        Assert.Equal(64, loaded.PixelCount);

        // GetHistogram on loaded
        var hist = loaded.GetHistogram();
        Assert.NotNull(hist);
        var sum = 0;
        foreach (var kv in hist)
            sum += kv.Value;
        Assert.Equal(64, sum);

        // Rotate original image 90 degrees
        var rotated90 = img.Rotate(90);
        Assert.NotNull(rotated90);
        // After rotation dims may swap for non-square or stay same
        Assert.True(rotated90.Width > 0 && rotated90.Height > 0);

        // Crop and chain Rotate
        var chainPath = TempFile("chain.pgm");
        img.Crop(4, 4, 8, 8).Rotate(180).SaveToFile(chainPath);
        Assert.True(File.Exists(chainPath));
    }
}
