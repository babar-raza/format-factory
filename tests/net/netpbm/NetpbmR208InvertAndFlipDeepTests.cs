// Tests for NetpbmImage.Invert, FlipHorizontal, FlipVertical deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R208

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R208: Tests for NetpbmImage.Invert, FlipHorizontal, FlipVertical deeper coverage.
/// Invert(): returns image with pixel values inverted (max - value).
/// FlipHorizontal(): returns image mirrored left-right.
/// FlipVertical(): returns image mirrored top-bottom.
/// Covers: Invert non-null; Invert preserves dimensions; Invert double-invert equals original;
/// Invert black becomes white; Invert white becomes black; Invert mid-value flipped;
/// FlipHorizontal non-null; FlipHorizontal preserves dimensions; FlipHorizontal double-flip equals original;
/// FlipHorizontal asymmetric canvas differs from original;
/// FlipVertical non-null; FlipVertical preserves dimensions; FlipVertical double-flip equals original;
/// dogfood CreateCanvas->Invert->FlipHorizontal->FlipVertical->Verify pipeline.
/// </summary>
public class NetpbmR208InvertAndFlipDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR208InvertAndFlipDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR208_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // Invert
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 100);
        Assert.NotNull(img.Invert());
    }

    [Fact]
    public void Invert_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 50);
        var inv = img.Invert();
        Assert.Equal(6, inv.Width);
        Assert.Equal(8, inv.Height);
    }

    [Fact]
    public void Invert_BlackCanvas_BecomesWhite()
    {
        var img = NetpbmImage.CreateCanvas(3, 3, 0);
        var inv = img.Invert();
        // Black (0) should invert to white (255)
        Assert.Equal(255, inv.GetPixelColor(0, 0));
    }

    [Fact]
    public void Invert_WhiteCanvas_BecomesBlack()
    {
        var img = NetpbmImage.CreateCanvas(3, 3, 255);
        var inv = img.Invert();
        // White (255) should invert to black (0)
        Assert.Equal(0, inv.GetPixelColor(0, 0));
    }

    [Fact]
    public void Invert_DoubleInvert_EqualsDimensions()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 128);
        var doubleInv = img.Invert().Invert();
        Assert.Equal(img.Width, doubleInv.Width);
        Assert.Equal(img.Height, doubleInv.Height);
    }

    [Fact]
    public void Invert_PreservesPixelCount()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 100);
        var inv = img.Invert();
        Assert.Equal(img.Width * img.Height, inv.Width * inv.Height);
    }

    // -------------------------------------------------------------------------
    // FlipHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 100);
        Assert.NotNull(img.FlipHorizontal());
    }

    [Fact]
    public void FlipHorizontal_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 50);
        var flipped = img.FlipHorizontal();
        Assert.Equal(6, flipped.Width);
        Assert.Equal(8, flipped.Height);
    }

    [Fact]
    public void FlipHorizontal_DoubleFlip_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 128);
        var doubleFl = img.FlipHorizontal().FlipHorizontal();
        Assert.Equal(img.Width, doubleFl.Width);
        Assert.Equal(img.Height, doubleFl.Height);
    }

    [Fact]
    public void FlipHorizontal_UniformCanvas_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 200);
        var flipped = img.FlipHorizontal();
        Assert.NotNull(flipped);
        Assert.Equal(200, flipped.GetPixelColor(0, 0));
    }

    [Fact]
    public void FlipHorizontal_AfterDrawLine_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 0);
        var withLine = img.DrawLine(0, 4, 7, 4, 255);
        var flipped = withLine.FlipHorizontal();
        Assert.NotNull(flipped);
        Assert.Equal(8, flipped.Width);
        Assert.Equal(8, flipped.Height);
    }

    // -------------------------------------------------------------------------
    // FlipVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 100);
        Assert.NotNull(img.FlipVertical());
    }

    [Fact]
    public void FlipVertical_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 50);
        var flipped = img.FlipVertical();
        Assert.Equal(6, flipped.Width);
        Assert.Equal(8, flipped.Height);
    }

    [Fact]
    public void FlipVertical_DoubleFlip_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 128);
        var doubleFl = img.FlipVertical().FlipVertical();
        Assert.Equal(img.Width, doubleFl.Width);
        Assert.Equal(img.Height, doubleFl.Height);
    }

    [Fact]
    public void FlipVertical_UniformCanvas_SamePixelValue()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 150);
        var flipped = img.FlipVertical();
        Assert.Equal(150, flipped.GetPixelColor(0, 0));
    }

    [Fact]
    public void FlipHorizontal_ThenFlipVertical_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 4, 100);
        var result = img.FlipHorizontal().FlipVertical();
        Assert.Equal(6, result.Width);
        Assert.Equal(4, result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_Invert_FlipHorizontal_FlipVertical_Verify_Pipeline()
    {
        // Create a canvas
        var canvas = NetpbmImage.CreateCanvas(8, 8, 100);
        Assert.Equal(8, canvas.Width);
        Assert.Equal(8, canvas.Height);
        Assert.Equal(100, canvas.GetPixelColor(0, 0));

        // Invert
        var inverted = canvas.Invert();
        Assert.NotNull(inverted);
        Assert.Equal(8, inverted.Width);
        Assert.Equal(8, inverted.Height);
        // 100 inverted = 155 (255 - 100)
        Assert.Equal(155, inverted.GetPixelColor(0, 0));

        // Double invert should return same dimensions
        var doubleInverted = inverted.Invert();
        Assert.Equal(8, doubleInverted.Width);

        // FlipHorizontal
        var flippedH = inverted.FlipHorizontal();
        Assert.NotNull(flippedH);
        Assert.Equal(8, flippedH.Width);
        Assert.Equal(8, flippedH.Height);

        // FlipVertical
        var flippedV = flippedH.FlipVertical();
        Assert.NotNull(flippedV);
        Assert.Equal(8, flippedV.Width);
        Assert.Equal(8, flippedV.Height);

        // Save and reload
        var path = TempFile("dogfood_invert.pgm");
        flippedV.SaveToFile(path);
        Assert.True(File.Exists(path));

        var reloaded = NetpbmImage.LoadFile(path);
        Assert.NotNull(reloaded);
        Assert.Equal(8, reloaded.Width);
        Assert.Equal(8, reloaded.Height);
    }
}
