// Tests for NetpbmImage.FlipHorizontal, FlipVertical, Resize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R247

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R247: Tests for NetpbmImage.FlipHorizontal, FlipVertical, Resize deeper.
/// FlipHorizontal(): returns a horizontally mirrored copy of the image.
/// FlipVertical(): returns a vertically mirrored copy of the image.
/// Resize(width, height): resizes the image to the specified dimensions.
/// Covers: FlipHorizontal non-null; FlipHorizontal preserves dims; FlipHorizontal no-throw;
/// FlipHorizontal persist; FlipHorizontal twice = original dims; FlipHorizontal for RGB;
/// FlipHorizontal then Invert; FlipHorizontal pixel count same;
/// FlipVertical non-null; FlipVertical preserves dims; FlipVertical no-throw;
/// FlipVertical persist; FlipVertical twice = original dims; FlipVertical for RGB;
/// FlipVertical then FlipHorizontal; FlipVertical then Crop;
/// Resize non-null; Resize new width correct; Resize new height correct; Resize no-throw;
/// Resize persist; Resize larger dims; Resize smaller dims; Resize for RGB;
/// Resize then Crop; Resize then Invert; Resize then FlipHorizontal;
/// dogfood CreateGrayscale→FlipHorizontal→FlipVertical→Resize→SaveToFile pipeline.
/// </summary>
public class NetpbmR247FlipAndResizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR247FlipAndResizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR247_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGrayscale10x8()
    {
        var pixels = new byte[10 * 8];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)(i * 3 % 256);
        return NetpbmImage.CreatePgm(10, 8, pixels);
    }

    private static NetpbmImage CreateRgb8x6()
    {
        var pixels = new byte[8 * 6 * 3];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)(i % 256);
        return NetpbmImage.CreatePpm(8, 6, pixels);
    }

    // -------------------------------------------------------------------------
    // FlipHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_NonNull()
    {
        var img = CreateGrayscale10x8();
        Assert.NotNull(img.FlipHorizontal());
    }

    [Fact]
    public void FlipHorizontal_PreservesWidth()
    {
        var img = CreateGrayscale10x8();
        Assert.Equal(img.Width, img.FlipHorizontal().Width);
    }

    [Fact]
    public void FlipHorizontal_PreservesHeight()
    {
        var img = CreateGrayscale10x8();
        Assert.Equal(img.Height, img.FlipHorizontal().Height);
    }

    [Fact]
    public void FlipHorizontal_PreservesPixelCount()
    {
        var img = CreateGrayscale10x8();
        Assert.Equal(img.GetPixelCount(), img.FlipHorizontal().GetPixelCount());
    }

    [Fact]
    public void FlipHorizontal_NoThrow()
    {
        var img = CreateGrayscale10x8();
        var ex = Record.Exception(() => img.FlipHorizontal());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipHorizontal_Persist()
    {
        var img = CreateGrayscale10x8();
        var flipped = img.FlipHorizontal();
        var path = TempFile("flip_h.pgm");
        flipped.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(10, loaded.Width);
        Assert.Equal(8, loaded.Height);
    }

    [Fact]
    public void FlipHorizontal_TwiceSameDims()
    {
        var img = CreateGrayscale10x8();
        var flipped = img.FlipHorizontal().FlipHorizontal();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void FlipHorizontal_ForRgb_PreservesDims()
    {
        var img = CreateRgb8x6();
        var flipped = img.FlipHorizontal();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void FlipHorizontal_ThenInvert_NonNull()
    {
        var img = CreateGrayscale10x8();
        var result = img.FlipHorizontal().Invert();
        Assert.NotNull(result);
        Assert.Equal(10, result.Width);
    }

    // -------------------------------------------------------------------------
    // FlipVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_NonNull()
    {
        var img = CreateGrayscale10x8();
        Assert.NotNull(img.FlipVertical());
    }

    [Fact]
    public void FlipVertical_PreservesWidth()
    {
        var img = CreateGrayscale10x8();
        Assert.Equal(img.Width, img.FlipVertical().Width);
    }

    [Fact]
    public void FlipVertical_PreservesHeight()
    {
        var img = CreateGrayscale10x8();
        Assert.Equal(img.Height, img.FlipVertical().Height);
    }

    [Fact]
    public void FlipVertical_PreservesPixelCount()
    {
        var img = CreateGrayscale10x8();
        Assert.Equal(img.GetPixelCount(), img.FlipVertical().GetPixelCount());
    }

    [Fact]
    public void FlipVertical_NoThrow()
    {
        var img = CreateGrayscale10x8();
        var ex = Record.Exception(() => img.FlipVertical());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipVertical_Persist()
    {
        var img = CreateGrayscale10x8();
        var flipped = img.FlipVertical();
        var path = TempFile("flip_v.pgm");
        flipped.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(10, loaded.Width);
        Assert.Equal(8, loaded.Height);
    }

    [Fact]
    public void FlipVertical_TwiceSameDims()
    {
        var img = CreateGrayscale10x8();
        var flipped = img.FlipVertical().FlipVertical();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void FlipVertical_ForRgb_PreservesDims()
    {
        var img = CreateRgb8x6();
        var flipped = img.FlipVertical();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void FlipVertical_ThenFlipHorizontal_NonNull()
    {
        var img = CreateGrayscale10x8();
        var result = img.FlipVertical().FlipHorizontal();
        Assert.NotNull(result);
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    [Fact]
    public void FlipVertical_ThenCrop_NonNull()
    {
        var img = CreateGrayscale10x8();
        var flipped = img.FlipVertical();
        var cropped = flipped.Crop(0, 0, 5, 4);
        Assert.Equal(5, cropped.Width);
        Assert.Equal(4, cropped.Height);
    }

    // -------------------------------------------------------------------------
    // Resize
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_NonNull()
    {
        var img = CreateGrayscale10x8();
        Assert.NotNull(img.Resize(20, 16));
    }

    [Fact]
    public void Resize_NewWidthCorrect()
    {
        var img = CreateGrayscale10x8();
        Assert.Equal(20, img.Resize(20, 16).Width);
    }

    [Fact]
    public void Resize_NewHeightCorrect()
    {
        var img = CreateGrayscale10x8();
        Assert.Equal(16, img.Resize(20, 16).Height);
    }

    [Fact]
    public void Resize_NoThrow()
    {
        var img = CreateGrayscale10x8();
        var ex = Record.Exception(() => img.Resize(15, 12));
        Assert.Null(ex);
    }

    [Fact]
    public void Resize_Persist()
    {
        var img = CreateGrayscale10x8();
        var resized = img.Resize(20, 16);
        var path = TempFile("resize.pgm");
        resized.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(20, loaded.Width);
        Assert.Equal(16, loaded.Height);
    }

    [Fact]
    public void Resize_LargerDims()
    {
        var img = CreateGrayscale10x8();
        var resized = img.Resize(30, 24);
        Assert.Equal(30, resized.Width);
        Assert.Equal(24, resized.Height);
        Assert.Equal(720, resized.GetPixelCount());
    }

    [Fact]
    public void Resize_SmallerDims()
    {
        var img = CreateGrayscale10x8();
        var resized = img.Resize(5, 4);
        Assert.Equal(5, resized.Width);
        Assert.Equal(4, resized.Height);
    }

    [Fact]
    public void Resize_ForRgb_NewDims()
    {
        var img = CreateRgb8x6();
        var resized = img.Resize(16, 12);
        Assert.Equal(16, resized.Width);
        Assert.Equal(12, resized.Height);
    }

    [Fact]
    public void Resize_ThenCrop_Works()
    {
        var img = CreateGrayscale10x8();
        var resized = img.Resize(20, 16);
        var cropped = resized.Crop(0, 0, 10, 8);
        Assert.Equal(10, cropped.Width);
        Assert.Equal(8, cropped.Height);
    }

    [Fact]
    public void Resize_ThenInvert_Works()
    {
        var img = CreateGrayscale10x8();
        var resized = img.Resize(20, 16);
        var inverted = resized.Invert();
        Assert.Equal(20, inverted.Width);
        Assert.Equal(16, inverted.Height);
    }

    [Fact]
    public void Resize_ThenFlipHorizontal_Works()
    {
        var img = CreateGrayscale10x8();
        var resized = img.Resize(20, 16);
        var flipped = resized.FlipHorizontal();
        Assert.Equal(20, flipped.Width);
        Assert.Equal(16, flipped.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FlipHorizontal_FlipVertical_Resize_SaveToFile_Pipeline()
    {
        // Create base grayscale 12×8
        var basePixels = new byte[12 * 8];
        for (int i = 0; i < basePixels.Length; i++)
            basePixels[i] = (byte)(i * 2 % 256);
        var base_img = NetpbmImage.CreatePgm(12, 8, basePixels);

        Assert.Equal(12, base_img.Width);
        Assert.Equal(8, base_img.Height);
        Assert.Equal(96, base_img.GetPixelCount());

        // FlipHorizontal
        var flipH = base_img.FlipHorizontal();
        Assert.Equal(12, flipH.Width);
        Assert.Equal(8, flipH.Height);
        Assert.Equal(96, flipH.GetPixelCount());

        // FlipVertical
        var flipV = base_img.FlipVertical();
        Assert.Equal(12, flipV.Width);
        Assert.Equal(8, flipV.Height);

        // FlipH then FlipV
        var flipHV = base_img.FlipHorizontal().FlipVertical();
        Assert.Equal(12, flipHV.Width);
        Assert.Equal(8, flipHV.Height);

        // FlipH twice same dims
        var flipHTwice = base_img.FlipHorizontal().FlipHorizontal();
        Assert.Equal(base_img.Width, flipHTwice.Width);
        Assert.Equal(base_img.Height, flipHTwice.Height);

        // FlipV twice same dims
        var flipVTwice = base_img.FlipVertical().FlipVertical();
        Assert.Equal(base_img.Width, flipVTwice.Width);

        // Resize to larger
        var enlarged = base_img.Resize(24, 16);
        Assert.Equal(24, enlarged.Width);
        Assert.Equal(16, enlarged.Height);
        Assert.Equal(384, enlarged.GetPixelCount());

        // Resize to smaller
        var shrunk = base_img.Resize(6, 4);
        Assert.Equal(6, shrunk.Width);
        Assert.Equal(4, shrunk.Height);

        // FlipH on resized
        var flipHEnlarged = enlarged.FlipHorizontal();
        Assert.Equal(24, flipHEnlarged.Width);
        Assert.Equal(16, flipHEnlarged.Height);

        // FlipV on resized
        var flipVEnlarged = enlarged.FlipVertical();
        Assert.Equal(24, flipVEnlarged.Width);

        // Resize then Crop
        var resizeCrop = enlarged.Crop(0, 0, 12, 8);
        Assert.Equal(12, resizeCrop.Width);
        Assert.Equal(8, resizeCrop.Height);

        // FlipH then Crop
        var flipCrop = flipH.Crop(2, 1, 8, 6);
        Assert.Equal(8, flipCrop.Width);
        Assert.Equal(6, flipCrop.Height);

        // Invert on flipped
        var invertFlip = flipH.Invert();
        Assert.Equal(12, invertFlip.Width);

        // RGB pipeline
        var rgb = CreateRgb8x6();
        var rgbFlipH = rgb.FlipHorizontal();
        Assert.Equal(8, rgbFlipH.Width);
        Assert.Equal(6, rgbFlipH.Height);

        var rgbFlipV = rgb.FlipVertical();
        Assert.Equal(8, rgbFlipV.Width);

        var rgbResized = rgb.Resize(16, 12);
        Assert.Equal(16, rgbResized.Width);
        Assert.Equal(12, rgbResized.Height);

        // GetAverageBrightness consistent after flips
        var b1 = base_img.GetAverageBrightness();
        var b2 = flipH.GetAverageBrightness();
        Assert.True(Math.Abs(b1 - b2) < 5.0); // should be same brightness

        // GetPixelCount after all ops
        Assert.Equal(96, base_img.GetPixelCount());
        Assert.Equal(384, enlarged.GetPixelCount());
        Assert.Equal(24, shrunk.GetPixelCount());

        // SaveToFile multiple images
        var pathBase = TempFile("base.pgm");
        var pathFlipH = TempFile("flip_h.pgm");
        var pathFlipV = TempFile("flip_v.pgm");
        var pathEnlarged = TempFile("enlarged.pgm");

        base_img.SaveToFile(pathBase);
        flipH.SaveToFile(pathFlipH);
        flipV.SaveToFile(pathFlipV);
        enlarged.SaveToFile(pathEnlarged);

        Assert.True(File.Exists(pathBase));
        Assert.True(File.Exists(pathFlipH));
        Assert.True(File.Exists(pathFlipV));
        Assert.True(File.Exists(pathEnlarged));

        // LoadFile and verify all
        var loadedBase = NetpbmImage.LoadFile(pathBase);
        Assert.Equal(12, loadedBase.Width);
        Assert.Equal(8, loadedBase.Height);

        var loadedFlipH = NetpbmImage.LoadFile(pathFlipH);
        Assert.Equal(12, loadedFlipH.Width);
        Assert.Equal(8, loadedFlipH.Height);

        var loadedEnlarged = NetpbmImage.LoadFile(pathEnlarged);
        Assert.Equal(24, loadedEnlarged.Width);
        Assert.Equal(16, loadedEnlarged.Height);

        // Operations on loaded images
        var loadedFlipV = loadedBase.FlipVertical();
        Assert.Equal(12, loadedFlipV.Width);

        var loadedResize = loadedBase.Resize(6, 4);
        Assert.Equal(6, loadedResize.Width);

        // Final save
        var pathFinal = TempFile("final.pgm");
        loadedResize.SaveToFile(pathFinal);
        Assert.True(File.Exists(pathFinal));
        var finalImg = NetpbmImage.LoadFile(pathFinal);
        Assert.Equal(6, finalImg.Width);
        Assert.Equal(4, finalImg.Height);
    }
}
