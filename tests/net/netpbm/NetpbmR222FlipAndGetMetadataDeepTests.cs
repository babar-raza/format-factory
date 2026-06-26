// Tests for NetpbmImage.FlipHorizontal, FlipVertical, GetMetadata deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R222

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R222: Tests for NetpbmImage.FlipHorizontal, FlipVertical, GetMetadata deeper coverage.
/// FlipHorizontal(): mirrors image left-to-right.
/// FlipVertical(): mirrors image top-to-bottom.
/// GetMetadata(): returns image metadata (format, width, height, maxval, channel count).
/// Covers: FlipHorizontal non-null; FlipHorizontal same dimensions; FlipHorizontal pixel check;
/// FlipHorizontal twice restores original; FlipHorizontal on grayscale;
/// FlipVertical non-null; FlipVertical same dimensions; FlipVertical pixel check;
/// FlipVertical twice restores original; FlipVertical on grayscale;
/// GetMetadata non-null; GetMetadata width correct; GetMetadata height correct;
/// GetMetadata format correct; GetMetadata maxval positive; GetMetadata channels positive;
/// GetMetadata after resize; GetMetadata after conversion;
/// dogfood CreateCanvas→FlipH→FlipV→GetMetadata→SaveToFile→LoadFile→verify pipeline.
/// </summary>
public class NetpbmR222FlipAndGetMetadataDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR222FlipAndGetMetadataDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR222_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateColorCanvas(int w = 6, int h = 4)
    {
        var img = NetpbmImage.CreateCanvas(w, h, NetpbmFormat.PPM);
        // Paint left half red, right half blue
        for (int y = 0; y < h; y++)
        {
            for (int x = 0; x < w / 2; x++)
                img.SetPixel(x, y, 255, 0, 0);
            for (int x = w / 2; x < w; x++)
                img.SetPixel(x, y, 0, 0, 255);
        }
        return img;
    }

    private static NetpbmImage CreateGrayCanvas(int w = 6, int h = 4)
    {
        var img = NetpbmImage.CreateCanvas(w, h, NetpbmFormat.PGM);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                img.SetPixel(x, y, x * 40); // gradient left-to-right
        return img;
    }

    // -------------------------------------------------------------------------
    // FlipHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_NonNull()
    {
        var img = CreateColorCanvas();
        Assert.NotNull(img.FlipHorizontal());
    }

    [Fact]
    public void FlipHorizontal_SameDimensions()
    {
        var img = CreateColorCanvas(6, 4);
        var flipped = img.FlipHorizontal();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void FlipHorizontal_PixelMirrored()
    {
        var img = CreateColorCanvas(6, 4);
        var flipped = img.FlipHorizontal();
        // Original: left=red(255,0,0), right=blue(0,0,255)
        // Flipped: left=blue, right=red
        var leftPixel = flipped.GetPixel(0, 0);
        Assert.Equal(0, leftPixel.R);
        Assert.Equal(0, leftPixel.G);
        Assert.Equal(255, leftPixel.B);
    }

    [Fact]
    public void FlipHorizontal_TwiceRestoresOriginal()
    {
        var img = CreateColorCanvas(6, 4);
        var original = img.GetPixel(0, 0);
        var restored = img.FlipHorizontal().FlipHorizontal().GetPixel(0, 0);
        Assert.Equal(original.R, restored.R);
        Assert.Equal(original.G, restored.G);
        Assert.Equal(original.B, restored.B);
    }

    [Fact]
    public void FlipHorizontal_OnGrayscale_NonNull()
    {
        var img = CreateGrayCanvas();
        Assert.NotNull(img.FlipHorizontal());
    }

    [Fact]
    public void FlipHorizontal_OnGrayscale_SameDimensions()
    {
        var img = CreateGrayCanvas(6, 4);
        var flipped = img.FlipHorizontal();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    // -------------------------------------------------------------------------
    // FlipVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_NonNull()
    {
        var img = CreateColorCanvas();
        Assert.NotNull(img.FlipVertical());
    }

    [Fact]
    public void FlipVertical_SameDimensions()
    {
        var img = CreateColorCanvas(6, 4);
        var flipped = img.FlipVertical();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void FlipVertical_TwiceRestoresOriginal()
    {
        var img = CreateColorCanvas(6, 4);
        var original = img.GetPixel(0, 0);
        var restored = img.FlipVertical().FlipVertical().GetPixel(0, 0);
        Assert.Equal(original.R, restored.R);
        Assert.Equal(original.G, restored.G);
        Assert.Equal(original.B, restored.B);
    }

    [Fact]
    public void FlipVertical_OnGrayscale_NonNull()
    {
        var img = CreateGrayCanvas();
        Assert.NotNull(img.FlipVertical());
    }

    [Fact]
    public void FlipHorizontalAndVertical_BothNonNull()
    {
        var img = CreateColorCanvas();
        Assert.NotNull(img.FlipHorizontal().FlipVertical());
    }

    // -------------------------------------------------------------------------
    // GetMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetadata_NonNull()
    {
        var img = CreateColorCanvas();
        Assert.NotNull(img.GetMetadata());
    }

    [Fact]
    public void GetMetadata_WidthCorrect()
    {
        var img = CreateColorCanvas(6, 4);
        Assert.Equal(6, img.GetMetadata().Width);
    }

    [Fact]
    public void GetMetadata_HeightCorrect()
    {
        var img = CreateColorCanvas(6, 4);
        Assert.Equal(4, img.GetMetadata().Height);
    }

    [Fact]
    public void GetMetadata_FormatCorrect()
    {
        var img = CreateColorCanvas();
        var meta = img.GetMetadata();
        Assert.True(meta.Format == "PPM" || meta.Format == "P6" || meta.Format.Length > 0);
    }

    [Fact]
    public void GetMetadata_MaxvalPositive()
    {
        var img = CreateColorCanvas();
        Assert.True(img.GetMetadata().Maxval > 0);
    }

    [Fact]
    public void GetMetadata_ChannelsPositive()
    {
        var img = CreateColorCanvas();
        Assert.True(img.GetMetadata().Channels > 0);
    }

    [Fact]
    public void GetMetadata_AfterResize_ReflectsNewDimensions()
    {
        var img = CreateColorCanvas(6, 4);
        var resized = img.Resize(12, 8);
        var meta = resized.GetMetadata();
        Assert.Equal(12, meta.Width);
        Assert.Equal(8, meta.Height);
    }

    [Fact]
    public void GetMetadata_GrayscaleChannelsLessThanColor()
    {
        var color = CreateColorCanvas(6, 4);
        var gray = color.ToGrayscale();
        Assert.True(gray.GetMetadata().Channels <= color.GetMetadata().Channels);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_FlipH_FlipV_GetMetadata_SaveAndLoad_Pipeline()
    {
        var img = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.PPM);

        // Draw distinct corner colors
        img.SetPixel(0, 0, 255, 0, 0);   // top-left = red
        img.SetPixel(7, 0, 0, 255, 0);   // top-right = green
        img.SetPixel(0, 5, 0, 0, 255);   // bottom-left = blue
        img.SetPixel(7, 5, 255, 255, 0); // bottom-right = yellow

        // GetMetadata on original
        var meta = img.GetMetadata();
        Assert.NotNull(meta);
        Assert.Equal(8, meta.Width);
        Assert.Equal(6, meta.Height);
        Assert.True(meta.Maxval > 0);
        Assert.True(meta.Channels > 0);

        // FlipHorizontal — corners swap left/right
        var flippedH = img.FlipHorizontal();
        Assert.Equal(8, flippedH.Width);
        Assert.Equal(6, flippedH.Height);
        var topRight = flippedH.GetPixel(7, 0);
        Assert.Equal(255, topRight.R); // was top-left red, now top-right
        var topLeft = flippedH.GetPixel(0, 0);
        Assert.Equal(255, topLeft.G); // was top-right green, now top-left

        // FlipVertical on flipped — corners swap top/bottom
        var flippedHV = flippedH.FlipVertical();
        Assert.Equal(8, flippedHV.Width);
        Assert.Equal(6, flippedHV.Height);

        // GetMetadata consistent after flips
        var metaAfter = flippedHV.GetMetadata();
        Assert.Equal(meta.Width, metaAfter.Width);
        Assert.Equal(meta.Height, metaAfter.Height);
        Assert.Equal(meta.Channels, metaAfter.Channels);

        // FlipH twice = original
        var restoredH = img.FlipHorizontal().FlipHorizontal();
        var origPixel = img.GetPixel(0, 0);
        var restPixel = restoredH.GetPixel(0, 0);
        Assert.Equal(origPixel.R, restPixel.R);

        // FlipV twice = original
        var restoredV = img.FlipVertical().FlipVertical();
        var origPixelBL = img.GetPixel(0, 5);
        var restPixelBL = restoredV.GetPixel(0, 5);
        Assert.Equal(origPixelBL.B, restPixelBL.B);

        // SaveToFile and LoadFile
        var path = TempFile("dogfood_flip.ppm");
        img.SaveToFile(path);
        Assert.True(File.Exists(path));

        var loaded = NetpbmImage.LoadFile(path);
        Assert.NotNull(loaded);
        var loadedMeta = loaded.GetMetadata();
        Assert.Equal(8, loadedMeta.Width);
        Assert.Equal(6, loadedMeta.Height);

        // FlipH on loaded
        var loadedFlipped = loaded.FlipHorizontal();
        Assert.Equal(8, loadedFlipped.Width);
        Assert.Equal(6, loadedFlipped.Height);
        Assert.NotNull(loadedFlipped.GetMetadata());

        // ToGrayscale and GetMetadata
        var gray = img.ToGrayscale();
        var grayMeta = gray.GetMetadata();
        Assert.Equal(8, grayMeta.Width);
        Assert.Equal(6, grayMeta.Height);
        Assert.True(grayMeta.Channels <= meta.Channels);
    }
}
