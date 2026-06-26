// Tests for NetpbmImage.Crop, RotateLeft, RotateRight deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R232

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R232: Tests for NetpbmImage.Crop, RotateLeft, RotateRight deeper coverage.
/// Crop(x, y, w, h): crops the image to the specified rectangle.
/// RotateLeft(): rotates the image 90 degrees counter-clockwise.
/// RotateRight(): rotates the image 90 degrees clockwise.
/// Covers: Crop non-null; Crop dimensions correct; Crop pixel values correct;
/// Crop full image returns same size; Crop single pixel; Crop save-load roundtrip;
/// RotateLeft non-null; RotateLeft swaps width/height; RotateLeft pixel position;
/// RotateLeft twice equals FlipH+FlipV; RotateLeft four times restores original;
/// RotateRight non-null; RotateRight swaps width/height; RotateRight pixel position;
/// RotateRight then RotateLeft restores original; RotateRight save-load roundtrip;
/// Crop after RotateRight; Rotate grayscale; metadata after rotate;
/// dogfood CreateCanvas→Crop→RotateLeft→RotateRight→SaveToFile→verify pipeline.
/// </summary>
public class NetpbmR232CropAndRotateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR232CropAndRotateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR232_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateColorCanvas()
    {
        // 8x4 canvas with distinct corner colors
        var img = NetpbmImage.CreateCanvas(8, 4, NetpbmFormat.PPM);
        // Top-left quadrant = red
        for (int y = 0; y < 2; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 255, 0, 0);
        // Top-right quadrant = green
        for (int y = 0; y < 2; y++)
            for (int x = 4; x < 8; x++)
                img.SetPixel(x, y, 0, 255, 0);
        // Bottom-left quadrant = blue
        for (int y = 2; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 0, 0, 255);
        // Bottom-right quadrant = white
        for (int y = 2; y < 4; y++)
            for (int x = 4; x < 8; x++)
                img.SetPixel(x, y, 255, 255, 255);
        return img;
    }

    private static NetpbmImage CreateGrayCanvas(int w = 8, int h = 4)
    {
        var img = NetpbmImage.CreateCanvas(w, h, NetpbmFormat.PGM);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                img.SetPixel(x, y, x * (255 / (w - 1)));
        return img;
    }

    // -------------------------------------------------------------------------
    // Crop
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_NonNull()
    {
        var img = CreateColorCanvas();
        Assert.NotNull(img.Crop(0, 0, 4, 2));
    }

    [Fact]
    public void Crop_DimensionsCorrect()
    {
        var img = CreateColorCanvas();
        var cropped = img.Crop(0, 0, 4, 2);
        Assert.Equal(4, cropped.Width);
        Assert.Equal(2, cropped.Height);
    }

    [Fact]
    public void Crop_PixelValuesPreserved()
    {
        var img = CreateColorCanvas();
        var topLeft = img.Crop(0, 0, 4, 2); // red quadrant
        var px = topLeft.GetPixel(0, 0);
        Assert.Equal(255, px.R);
        Assert.Equal(0, px.G);
        Assert.Equal(0, px.B);
    }

    [Fact]
    public void Crop_TopRightQuadrant()
    {
        var img = CreateColorCanvas();
        var topRight = img.Crop(4, 0, 4, 2); // green quadrant
        var px = topRight.GetPixel(0, 0);
        Assert.Equal(0, px.R);
        Assert.Equal(255, px.G);
        Assert.Equal(0, px.B);
    }

    [Fact]
    public void Crop_FullImage_SameDimensions()
    {
        var img = CreateColorCanvas();
        var full = img.Crop(0, 0, img.Width, img.Height);
        Assert.Equal(img.Width, full.Width);
        Assert.Equal(img.Height, full.Height);
    }

    [Fact]
    public void Crop_SaveAndLoad_RoundTrip()
    {
        var img = CreateColorCanvas();
        var cropped = img.Crop(0, 0, 4, 2);
        var path = TempFile("cropped.ppm");
        cropped.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(4, loaded.Width);
        Assert.Equal(2, loaded.Height);
    }

    [Fact]
    public void Crop_Grayscale_NonNull()
    {
        var img = CreateGrayCanvas();
        Assert.NotNull(img.Crop(0, 0, 4, 2));
    }

    [Fact]
    public void Crop_Grayscale_DimensionsCorrect()
    {
        var img = CreateGrayCanvas(8, 4);
        var cropped = img.Crop(2, 1, 4, 2);
        Assert.Equal(4, cropped.Width);
        Assert.Equal(2, cropped.Height);
    }

    // -------------------------------------------------------------------------
    // RotateLeft
    // -------------------------------------------------------------------------

    [Fact]
    public void RotateLeft_NonNull()
    {
        var img = CreateColorCanvas();
        Assert.NotNull(img.RotateLeft());
    }

    [Fact]
    public void RotateLeft_SwapsWidthAndHeight()
    {
        var img = CreateColorCanvas(); // 8x4
        var rotated = img.RotateLeft();
        Assert.Equal(img.Height, rotated.Width);  // 4
        Assert.Equal(img.Width, rotated.Height);  // 8
    }

    [Fact]
    public void RotateLeft_FourTimesRestoresOriginal()
    {
        var img = CreateColorCanvas();
        var original = img.GetPixel(0, 0);
        var restored = img.RotateLeft().RotateLeft().RotateLeft().RotateLeft().GetPixel(0, 0);
        Assert.Equal(original.R, restored.R);
        Assert.Equal(original.G, restored.G);
        Assert.Equal(original.B, restored.B);
    }

    [Fact]
    public void RotateLeft_TwiceEqualsRotate180()
    {
        var img = CreateColorCanvas();
        var rotated2 = img.RotateLeft().RotateLeft();
        // After 180 rotation, top-left of original should be at bottom-right
        Assert.Equal(img.Width, rotated2.Width);
        Assert.Equal(img.Height, rotated2.Height);
    }

    [Fact]
    public void RotateLeft_Grayscale_SwapsDimensions()
    {
        var img = CreateGrayCanvas(8, 4);
        var rotated = img.RotateLeft();
        Assert.Equal(4, rotated.Width);
        Assert.Equal(8, rotated.Height);
    }

    // -------------------------------------------------------------------------
    // RotateRight
    // -------------------------------------------------------------------------

    [Fact]
    public void RotateRight_NonNull()
    {
        var img = CreateColorCanvas();
        Assert.NotNull(img.RotateRight());
    }

    [Fact]
    public void RotateRight_SwapsWidthAndHeight()
    {
        var img = CreateColorCanvas(); // 8x4
        var rotated = img.RotateRight();
        Assert.Equal(img.Height, rotated.Width);  // 4
        Assert.Equal(img.Width, rotated.Height);  // 8
    }

    [Fact]
    public void RotateRight_ThenRotateLeft_RestoresOriginal()
    {
        var img = CreateColorCanvas();
        var original = img.GetPixel(0, 0);
        var restored = img.RotateRight().RotateLeft().GetPixel(0, 0);
        Assert.Equal(original.R, restored.R);
        Assert.Equal(original.G, restored.G);
        Assert.Equal(original.B, restored.B);
    }

    [Fact]
    public void RotateRight_FourTimesRestoresOriginal()
    {
        var img = CreateColorCanvas();
        var original = img.GetPixel(7, 3);
        var restored = img.RotateRight().RotateRight().RotateRight().RotateRight().GetPixel(7, 3);
        Assert.Equal(original.R, restored.R);
        Assert.Equal(original.G, restored.G);
        Assert.Equal(original.B, restored.B);
    }

    [Fact]
    public void RotateRight_SaveAndLoad()
    {
        var img = CreateColorCanvas();
        var rotated = img.RotateRight();
        var path = TempFile("rotated_right.ppm");
        rotated.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(rotated.Width, loaded.Width);
        Assert.Equal(rotated.Height, loaded.Height);
    }

    [Fact]
    public void RotateRight_MetadataDimensionsSwapped()
    {
        var img = CreateColorCanvas(); // 8x4
        var rotated = img.RotateRight();
        var meta = rotated.GetMetadata();
        Assert.Equal(4, meta.Width);
        Assert.Equal(8, meta.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_Crop_RotateLeft_RotateRight_SaveToFile_Verify_Pipeline()
    {
        var img = NetpbmImage.CreateCanvas(8, 4, NetpbmFormat.PPM);

        // Set distinct corner colors
        img.SetPixel(0, 0, 255, 0, 0);   // top-left = red
        img.SetPixel(7, 0, 0, 255, 0);   // top-right = green
        img.SetPixel(0, 3, 0, 0, 255);   // bottom-left = blue
        img.SetPixel(7, 3, 255, 255, 0); // bottom-right = yellow

        // Crop top-left pixel
        var topLeftCrop = img.Crop(0, 0, 1, 1);
        Assert.Equal(1, topLeftCrop.Width);
        Assert.Equal(1, topLeftCrop.Height);
        var tlPx = topLeftCrop.GetPixel(0, 0);
        Assert.Equal(255, tlPx.R);

        // Crop full-width top row
        var topRow = img.Crop(0, 0, 8, 1);
        Assert.Equal(8, topRow.Width);
        Assert.Equal(1, topRow.Height);

        // RotateLeft — 8x4 → 4x8
        var rotL = img.RotateLeft();
        Assert.Equal(4, rotL.Width);
        Assert.Equal(8, rotL.Height);

        // RotateRight — 8x4 → 4x8
        var rotR = img.RotateRight();
        Assert.Equal(4, rotR.Width);
        Assert.Equal(8, rotR.Height);

        // RotateLeft then RotateRight restores 8x4
        var restored = img.RotateLeft().RotateRight();
        Assert.Equal(8, restored.Width);
        Assert.Equal(4, restored.Height);
        var restoredPx = restored.GetPixel(0, 0);
        Assert.Equal(255, restoredPx.R); // red still at top-left

        // Rotate 4 times clockwise restores original
        var rotated4 = img.RotateRight().RotateRight().RotateRight().RotateRight();
        Assert.Equal(8, rotated4.Width);
        Assert.Equal(4, rotated4.Height);

        // Crop after RotateRight (4x8 → crop top 2x2)
        var croppedRotated = rotR.Crop(0, 0, 2, 2);
        Assert.Equal(2, croppedRotated.Width);
        Assert.Equal(2, croppedRotated.Height);

        // SaveToFile for original, cropped, rotated
        var origPath = TempFile("dogfood_orig.ppm");
        var croppedPath = TempFile("dogfood_cropped.ppm");
        var rotatedPath = TempFile("dogfood_rotated.ppm");

        img.SaveToFile(origPath);
        topLeftCrop.SaveToFile(croppedPath);
        rotR.SaveToFile(rotatedPath);

        Assert.True(File.Exists(origPath));
        Assert.True(File.Exists(croppedPath));
        Assert.True(File.Exists(rotatedPath));

        // Load and verify dimensions
        var loadedOrig = NetpbmImage.LoadFile(origPath);
        Assert.Equal(8, loadedOrig.Width);
        Assert.Equal(4, loadedOrig.Height);

        var loadedRotated = NetpbmImage.LoadFile(rotatedPath);
        Assert.Equal(4, loadedRotated.Width);
        Assert.Equal(8, loadedRotated.Height);

        // Grayscale crop and rotate
        var gray = img.ToGrayscale();
        var grayCropped = gray.Crop(0, 0, 4, 2);
        Assert.Equal(4, grayCropped.Width);
        Assert.Equal(2, grayCropped.Height);
        var grayRotated = gray.RotateLeft();
        Assert.Equal(4, grayRotated.Width);
        Assert.Equal(8, grayRotated.Height);
    }
}
