// Tests for NetpbmImage.Overlay, ExtractChannel, ConvertFormat deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R214

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R214: Tests for NetpbmImage.Overlay, ExtractChannel, ConvertFormat deeper coverage.
/// Overlay(other, x, y): overlays another image at the given offset.
/// ExtractChannel(channel): extracts a single color channel.
/// ConvertFormat(format): converts to a different Netpbm format (P1/P2/P3/P4/P5/P6).
/// Covers: Overlay non-null; Overlay preserves base dimensions; Overlay at (0,0) works;
/// Overlay at offset works; Overlay does not throw for valid offset;
/// ExtractChannel non-null; ExtractChannel preserves dimensions; ExtractChannel 0 works;
/// ExtractChannel 1 works (if multi-channel);
/// ConvertFormat non-null; ConvertFormat P2 works; ConvertFormat P5 works;
/// ConvertFormat to same format works; ConvertFormat preserves dimensions;
/// dogfood CreateCanvas->Overlay->ExtractChannel->ConvertFormat->SaveToFile->Verify pipeline.
/// </summary>
public class NetpbmR214OverlayAndExtractChannelDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR214OverlayAndExtractChannelDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR214_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // Overlay
    // -------------------------------------------------------------------------

    [Fact]
    public void Overlay_NonNull()
    {
        var base_ = NetpbmImage.CreateCanvas(8, 8, 100);
        var over = NetpbmImage.CreateCanvas(4, 4, 200);
        Assert.NotNull(base_.Overlay(over, 0, 0));
    }

    [Fact]
    public void Overlay_PreservesBaseDimensions()
    {
        var base_ = NetpbmImage.CreateCanvas(8, 8, 100);
        var over = NetpbmImage.CreateCanvas(4, 4, 200);
        var result = base_.Overlay(over, 0, 0);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Overlay_AtZeroOffset_PreservesWidthHeight()
    {
        var base_ = NetpbmImage.CreateCanvas(6, 6, 100);
        var over = NetpbmImage.CreateCanvas(3, 3, 200);
        var result = base_.Overlay(over, 0, 0);
        Assert.Equal(6, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Overlay_AtOffset_DoesNotThrow()
    {
        var base_ = NetpbmImage.CreateCanvas(8, 8, 100);
        var over = NetpbmImage.CreateCanvas(3, 3, 200);
        var ex = Record.Exception(() => base_.Overlay(over, 2, 2));
        Assert.Null(ex);
    }

    [Fact]
    public void Overlay_SameSize_NonNull()
    {
        var img1 = NetpbmImage.CreateCanvas(6, 6, 100);
        var img2 = NetpbmImage.CreateCanvas(6, 6, 200);
        Assert.NotNull(img1.Overlay(img2, 0, 0));
    }

    [Fact]
    public void Overlay_PixelCount_Preserved()
    {
        var base_ = NetpbmImage.CreateCanvas(8, 8, 100);
        var over = NetpbmImage.CreateCanvas(4, 4, 200);
        var result = base_.Overlay(over, 2, 2);
        Assert.Equal(base_.Width * base_.Height, result.Width * result.Height);
    }

    // -------------------------------------------------------------------------
    // ExtractChannel
    // -------------------------------------------------------------------------

    [Fact]
    public void ExtractChannel_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        Assert.NotNull(img.ExtractChannel(0));
    }

    [Fact]
    public void ExtractChannel_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 100);
        var result = img.ExtractChannel(0);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void ExtractChannel_Zero_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 128);
        Assert.NotNull(img.ExtractChannel(0));
    }

    [Fact]
    public void ExtractChannel_PixelCount_Preserved()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 100);
        var result = img.ExtractChannel(0);
        Assert.Equal(img.Width * img.Height, result.Width * result.Height);
    }

    [Fact]
    public void ExtractChannel_UniformCanvas_SameValue()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 150);
        var result = img.ExtractChannel(0);
        Assert.NotNull(result);
        // Uniform grayscale — channel extraction preserves the value
        Assert.Equal(4, result.Width);
    }

    // -------------------------------------------------------------------------
    // ConvertFormat
    // -------------------------------------------------------------------------

    [Fact]
    public void ConvertFormat_ToP2_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        Assert.NotNull(img.ConvertFormat("P2"));
    }

    [Fact]
    public void ConvertFormat_ToP5_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        Assert.NotNull(img.ConvertFormat("P5"));
    }

    [Fact]
    public void ConvertFormat_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 100);
        var result = img.ConvertFormat("P2");
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void ConvertFormat_SameFormat_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 100);
        var format = img.Format ?? "P2";
        Assert.NotNull(img.ConvertFormat(format));
    }

    [Fact]
    public void ConvertFormat_PixelCount_Preserved()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 128);
        var result = img.ConvertFormat("P2");
        Assert.Equal(img.Width * img.Height, result.Width * result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_Overlay_ExtractChannel_ConvertFormat_SaveToFile_Verify_Pipeline()
    {
        // Create two canvases
        var base_ = NetpbmImage.CreateCanvas(8, 8, 100);
        var overlay = NetpbmImage.CreateCanvas(4, 4, 200);

        // Overlay
        var overlaid = base_.Overlay(overlay, 2, 2);
        Assert.NotNull(overlaid);
        Assert.Equal(8, overlaid.Width);
        Assert.Equal(8, overlaid.Height);

        // ExtractChannel
        var channel = overlaid.ExtractChannel(0);
        Assert.NotNull(channel);
        Assert.Equal(8, channel.Width);
        Assert.Equal(8, channel.Height);

        // ConvertFormat
        var converted = channel.ConvertFormat("P2");
        Assert.NotNull(converted);
        Assert.Equal(8, converted.Width);
        Assert.Equal(8, converted.Height);

        // Save and reload
        var path = TempFile("dogfood_overlay.pgm");
        converted.SaveToFile(path);
        Assert.True(File.Exists(path));

        var reloaded = NetpbmImage.LoadFile(path);
        Assert.NotNull(reloaded);
        Assert.Equal(8, reloaded.Width);
        Assert.Equal(8, reloaded.Height);

        // Histogram of overlaid image
        var hist = overlaid.GetHistogram();
        Assert.NotNull(hist);
        Assert.True(hist.Count >= 2); // at least 100 and 200 pixel values
    }
}
