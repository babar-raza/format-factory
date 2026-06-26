// Tests for NetpbmImage.Crop and Resize operations.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R171

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R171: Tests for NetpbmImage.Crop and Resize operations.
/// Crop(top, left, height, width): extracts a rectangular sub-region.
/// Resize(newWidth, newHeight): scales the image to new dimensions.
/// Covers: Crop width and height correct; Crop pixel in region preserved;
/// Crop does not modify original; Crop entire image same dimensions;
/// Crop single pixel 1x1; Resize new dimensions correct;
/// Resize returns new image (original unchanged); Resize format preserved;
/// Resize to same size preserves pixel count; Resize to 1x1 single pixel;
/// Crop then Resize pipeline; Crop format preserved;
/// dogfood Create->Crop->Resize->SaveToFile->Reload dimensions.
/// </summary>
public class NetpbmR171CropAndResizeTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR171CropAndResizeTests()
    {
        _tempDir = System.IO.Path.Combine(System.IO.Path.GetTempPath(),
            "NetpbmR171_" + System.Guid.NewGuid().ToString("N"));
        System.IO.Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (System.IO.Directory.Exists(_tempDir))
            System.IO.Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) =>
        System.IO.Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGray(int w, int h, byte fill) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM, fill);

    // -------------------------------------------------------------------------
    // Crop
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_DimensionsCorrect()
    {
        var img = CreateGray(10, 8, 100);
        var cropped = img.Crop(1, 1, 4, 5);
        Assert.Equal(5, cropped.Width);
        Assert.Equal(4, cropped.Height);
    }

    [Fact]
    public void Crop_DoesNotModifyOriginal()
    {
        var img = CreateGray(6, 6, 150);
        _ = img.Crop(0, 0, 3, 3);
        Assert.Equal(6, img.Width);
        Assert.Equal(6, img.Height);
    }

    [Fact]
    public void Crop_EntireImage_SameDimensions()
    {
        var img = CreateGray(5, 5, 80);
        var cropped = img.Crop(0, 0, 5, 5);
        Assert.Equal(img.Width, cropped.Width);
        Assert.Equal(img.Height, cropped.Height);
    }

    [Fact]
    public void Crop_SinglePixel_Is1x1()
    {
        var img = CreateGray(4, 4, 200);
        var cropped = img.Crop(2, 2, 1, 1);
        Assert.Equal(1, cropped.Width);
        Assert.Equal(1, cropped.Height);
    }

    [Fact]
    public void Crop_FormatPreserved()
    {
        var img = CreateGray(6, 6, 128);
        var cropped = img.Crop(0, 0, 3, 3);
        Assert.Equal(NetpbmFormat.PGM, cropped.Format);
    }

    [Fact]
    public void Crop_PixelValuePreserved()
    {
        var img = CreateGray(5, 5, 0);
        img.SetPixel(2, 3, 199); // set a specific pixel
        var cropped = img.Crop(2, 3, 1, 1);
        Assert.Equal(199, cropped.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Resize
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_NewDimensionsCorrect()
    {
        var img = CreateGray(4, 4, 100);
        var resized = img.Resize(8, 6);
        Assert.Equal(8, resized.Width);
        Assert.Equal(6, resized.Height);
    }

    [Fact]
    public void Resize_DoesNotModifyOriginal()
    {
        var img = CreateGray(4, 4, 100);
        _ = img.Resize(2, 2);
        Assert.Equal(4, img.Width);
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void Resize_FormatPreserved()
    {
        var img = CreateGray(4, 4, 128);
        var resized = img.Resize(8, 8);
        Assert.Equal(NetpbmFormat.PGM, resized.Format);
    }

    [Fact]
    public void Resize_SameSize_PixelCountUnchanged()
    {
        var img = CreateGray(4, 4, 100);
        var resized = img.Resize(4, 4);
        Assert.Equal(img.Width * img.Height, resized.Width * resized.Height);
    }

    [Fact]
    public void Resize_To1x1_SinglePixel()
    {
        var img = CreateGray(4, 4, 200);
        var resized = img.Resize(1, 1);
        Assert.Equal(1, resized.Width);
        Assert.Equal(1, resized.Height);
        Assert.Equal(1, resized.Pixels.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Crop->Resize->SaveToFile->reload dimensions
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCropResizeSaveReload_Pipeline()
    {
        // Create 10x10 image
        var img = CreateGray(10, 10, 128);
        Assert.Equal(10, img.Width);

        // Crop to 6x6
        var cropped = img.Crop(2, 2, 6, 6);
        Assert.Equal(6, cropped.Width);
        Assert.Equal(6, cropped.Height);

        // Resize to 3x3
        var resized = cropped.Resize(3, 3);
        Assert.Equal(3, resized.Width);
        Assert.Equal(3, resized.Height);

        // Save and reload
        var path = TempFile("pipeline.pgm");
        resized.SaveToFile(path);
        Assert.True(System.IO.File.Exists(path));

        var parser = new NetpbmParser();
        var reloaded = parser.Parse(path);
        Assert.Equal(3, reloaded.Width);
        Assert.Equal(3, reloaded.Height);
        Assert.Equal(NetpbmFormat.PGM, reloaded.Format);
    }
}
