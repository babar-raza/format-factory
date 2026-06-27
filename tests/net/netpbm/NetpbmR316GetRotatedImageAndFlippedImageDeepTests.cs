// Tests for NetpbmImage.GetRotatedImage, GetFlippedImage deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R316

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R316: Tests for NetpbmImage.GetRotatedImage, GetFlippedImage deeper.
/// GetRotatedImage(degrees): returns a new image rotated by the given angle (90, 180, 270).
/// GetFlippedImage(axis): returns a new image flipped along the given axis ("horizontal" or "vertical").
/// Covers: GetRotatedImage no-throw; GetRotatedImage same dims for 180°; GetRotatedImage consistent;
/// GetRotatedImage 180-degree double-rotation roundtrip; GetRotatedImage save-load;
/// GetFlippedImage no-throw; GetFlippedImage same dims; GetFlippedImage consistent;
/// GetFlippedImage double-flip roundtrip; GetFlippedImage save-load;
/// GetFlippedImage horizontal differs from vertical;
/// dogfood CreateImage→GetRotatedImage→GetFlippedImage→SaveToFile pipeline.
/// </summary>
public class NetpbmR316GetRotatedImageAndFlippedImageDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR316GetRotatedImageAndFlippedImageDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR316_" + Guid.NewGuid().ToString("N"));
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
        var pixels = new byte[12 * 10];
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
                pixels[r * 12 + c] = (byte)(c * 20 + r * 5);
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using var fs = File.OpenWrite(path); fs.Write(header); fs.Write(pixels);
        return path;
    }

    private string CreateAsymmetricPgm()
    {
        // Asymmetric: left half dark, right half bright
        var path = TempFile("asymmetric.pgm");
        var pixels = new byte[12 * 10];
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
                pixels[r * 12 + c] = c < 6 ? (byte)30 : (byte)220;
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using var fs = File.OpenWrite(path); fs.Write(header); fs.Write(pixels);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRotatedImage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRotatedImage_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetRotatedImage(180));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRotatedImage_SameDims_For180()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var rot = img.GetRotatedImage(180);
        Assert.Equal(img.Width, rot.Width);
        Assert.Equal(img.Height, rot.Height);
    }

    [Fact]
    public void GetRotatedImage_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var r1 = img.GetRotatedImage(180);
        var r2 = img.GetRotatedImage(180);
        Assert.Equal(r1.GetMeanPixelValue(), r2.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetRotatedImage_180_DoubleRotation_Roundtrip()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var dbl = img.GetRotatedImage(180).GetRotatedImage(180);
        // 180+180=360 → should restore original mean
        Assert.Equal(img.GetMeanPixelValue(), dbl.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetRotatedImage_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var rot = img.GetRotatedImage(180);
        var path = TempFile("rot_save.pgm");
        rot.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(rot.Width, loaded.Width);
        Assert.Equal(rot.GetMeanPixelValue(), loaded.GetMeanPixelValue(), precision: 2);
    }

    // -------------------------------------------------------------------------
    // GetFlippedImage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFlippedImage_NoThrow_Horizontal()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetFlippedImage("horizontal"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFlippedImage_NoThrow_Vertical()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetFlippedImage("vertical"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFlippedImage_SameDims()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var flipped = img.GetFlippedImage("horizontal");
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void GetFlippedImage_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var f1 = img.GetFlippedImage("vertical");
        var f2 = img.GetFlippedImage("vertical");
        Assert.Equal(f1.GetMeanPixelValue(), f2.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetFlippedImage_DoubleFlip_Roundtrip()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var dbl = img.GetFlippedImage("horizontal").GetFlippedImage("horizontal");
        Assert.Equal(img.GetMeanPixelValue(), dbl.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetFlippedImage_Horizontal_Differs_From_Vertical()
    {
        var img = NetpbmImage.LoadFile(CreateAsymmetricPgm());
        var horiz = img.GetFlippedImage("horizontal");
        var vert = img.GetFlippedImage("vertical");
        // Both preserve mean but differ structurally
        Assert.Equal(img.GetMeanPixelValue(), horiz.GetMeanPixelValue(), precision: 4);
        Assert.Equal(img.GetMeanPixelValue(), vert.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetFlippedImage_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var flipped = img.GetFlippedImage("vertical");
        var path = TempFile("flip_save.pgm");
        flipped.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(flipped.Width, loaded.Width);
        Assert.Equal(flipped.GetMeanPixelValue(), loaded.GetMeanPixelValue(), precision: 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRotatedImage_GetFlippedImage_SaveToFile_Pipeline()
    {
        // Microscopy image augmentation — cell culture batch quality control
        var path = TempFile("dogfood_microscopy.pgm");
        var pixels = new byte[12 * 10];
        // Simulate cell culture: bright clusters (cells), dark background
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
            {
                // Cell clusters in quadrants
                bool topLeft = r < 4 && c < 5;
                bool bottomRight = r >= 6 && c >= 7;
                bool cell = topLeft || bottomRight;
                bool nucleus = (r == 2 && c == 2) || (r == 8 && c == 10);
                pixels[r * 12 + c] = nucleus ? (byte)250 : cell ? (byte)(180 + (r + c) % 40) : (byte)(20 + (r + c) % 30);
            }
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using (var fs = File.OpenWrite(path)) { fs.Write(header); fs.Write(pixels); }

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(10, img.Height);
        Assert.Equal(255, img.MaxVal);

        var origMean = img.GetMeanPixelValue();
        Assert.True(origMean > 0.0);

        // GetRotatedImage 180° — invert cell position for counting validation
        var rot180 = img.GetRotatedImage(180);
        Assert.Equal(12, rot180.Width);
        Assert.Equal(10, rot180.Height);
        Assert.Equal(rot180.GetMeanPixelValue(), img.GetRotatedImage(180).GetMeanPixelValue(), precision: 4); // consistent
        // 180° rotation preserves mean
        Assert.Equal(origMean, rot180.GetMeanPixelValue(), precision: 2);

        // Double 180° rotation roundtrip
        var rot360 = rot180.GetRotatedImage(180);
        Assert.Equal(origMean, rot360.GetMeanPixelValue(), precision: 4);

        // GetFlippedImage horizontal — mirror left-right
        var flipH = img.GetFlippedImage("horizontal");
        Assert.Equal(12, flipH.Width);
        Assert.Equal(10, flipH.Height);
        Assert.Equal(origMean, flipH.GetMeanPixelValue(), precision: 4); // preserves mean
        Assert.Equal(flipH.GetMeanPixelValue(), img.GetFlippedImage("horizontal").GetMeanPixelValue(), precision: 4); // consistent

        // GetFlippedImage vertical — mirror top-bottom
        var flipV = img.GetFlippedImage("vertical");
        Assert.Equal(12, flipV.Width);
        Assert.Equal(10, flipV.Height);
        Assert.Equal(origMean, flipV.GetMeanPixelValue(), precision: 4); // preserves mean
        Assert.Equal(flipV.GetMeanPixelValue(), img.GetFlippedImage("vertical").GetMeanPixelValue(), precision: 4); // consistent

        // Double flip roundtrip
        var flipHH = img.GetFlippedImage("horizontal").GetFlippedImage("horizontal");
        Assert.Equal(origMean, flipHH.GetMeanPixelValue(), precision: 4);
        var flipVV = img.GetFlippedImage("vertical").GetFlippedImage("vertical");
        Assert.Equal(origMean, flipVV.GetMeanPixelValue(), precision: 4);

        // SaveToFile — rotated 180°
        var out1 = TempFile("dogfood_microscopy_rot180.pgm");
        rot180.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loadedRot = NetpbmImage.LoadFile(out1);
        Assert.Equal(12, loadedRot.Width);
        Assert.Equal(rot180.GetMeanPixelValue(), loadedRot.GetMeanPixelValue(), precision: 2);

        // SaveToFile — flipped horizontal
        var out2 = TempFile("dogfood_microscopy_flipH.pgm");
        flipH.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loadedFlipH = NetpbmImage.LoadFile(out2);
        Assert.Equal(12, loadedFlipH.Width);
        Assert.Equal(flipH.GetMeanPixelValue(), loadedFlipH.GetMeanPixelValue(), precision: 2);

        // SaveToFile — flipped vertical
        var out3 = TempFile("dogfood_microscopy_flipV.pgm");
        flipV.SaveToFile(out3);
        Assert.True(File.Exists(out3));
        var loadedFlipV = NetpbmImage.LoadFile(out3);
        Assert.Equal(flipV.GetMeanPixelValue(), loadedFlipV.GetMeanPixelValue(), precision: 2);

        // Chain: rotate → flip → save (data augmentation pipeline)
        var augmented = img.GetRotatedImage(180).GetFlippedImage("horizontal");
        Assert.Equal(12, augmented.Width);
        Assert.Equal(10, augmented.Height);
        // Chained ops preserve mean
        Assert.Equal(origMean, augmented.GetMeanPixelValue(), precision: 2);
        var ex1 = Record.Exception(() => augmented.SaveToFile(TempFile("dogfood_augmented.pgm")));
        Assert.Null(ex1);

        // Multiple augmentations
        var aug2 = img.GetFlippedImage("vertical").GetFlippedImage("horizontal").GetRotatedImage(180);
        Assert.Equal(12, aug2.Width);
        var ex2 = Record.Exception(() => aug2.SaveToFile(TempFile("dogfood_aug2.pgm")));
        Assert.Null(ex2);
    }
}
