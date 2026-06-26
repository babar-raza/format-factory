// Tests for NetpbmImage.DrawRectangle and NetpbmImageAnalyzer.GetChannelStats.
// Sprint: ff-sprint-s140-dotnet-deepening-20260627
// Ledger: PC-NETPBM-R141

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R141: Tests for NetpbmImage.DrawRectangle and NetpbmImageAnalyzer.GetChannelStats.
/// DrawRectangle fills a rectangle region on PGM images; GetChannelStats returns
/// per-channel statistics (min, max, mean) for PPM images.
/// Covers: DrawRectangle negative x throws; negative y throws; negative width throws;
/// negative height throws; rectangle fills region; pixels outside unchanged;
/// DrawRectangle 1x1 sets single pixel; GetChannelStats null throws;
/// GetChannelStats returns non-null for PPM; dogfood Create->DrawRectangle->GetChannelStats pipeline.
/// </summary>
public class NetpbmR141DrawRectangleAndChannelStatsTests
{
    // -------------------------------------------------------------------------
    // DrawRectangle guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawRectangle_NegativeX_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(NetpbmFormat.PGM, 4, 4, 255);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.DrawRectangle(-1, 0, 2, 2, 128));
    }

    [Fact]
    public void DrawRectangle_NegativeY_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(NetpbmFormat.PGM, 4, 4, 255);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.DrawRectangle(0, -1, 2, 2, 128));
    }

    [Fact]
    public void DrawRectangle_NegativeWidth_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(NetpbmFormat.PGM, 4, 4, 255);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.DrawRectangle(0, 0, -1, 2, 128));
    }

    [Fact]
    public void DrawRectangle_NegativeHeight_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(NetpbmFormat.PGM, 4, 4, 255);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.DrawRectangle(0, 0, 2, -1, 128));
    }

    // -------------------------------------------------------------------------
    // DrawRectangle functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawRectangle_FillsTargetRegion()
    {
        var img = NetpbmImage.Create(NetpbmFormat.PGM, 4, 4, 255);
        img.DrawRectangle(1, 1, 2, 2, 200);

        Assert.Equal(200, img.GetPixel(1, 1));
        Assert.Equal(200, img.GetPixel(1, 2));
        Assert.Equal(200, img.GetPixel(2, 1));
        Assert.Equal(200, img.GetPixel(2, 2));
    }

    [Fact]
    public void DrawRectangle_PixelsOutsideRectangle_Unchanged()
    {
        var img = NetpbmImage.Create(NetpbmFormat.PGM, 4, 4, 255);
        img.DrawRectangle(1, 1, 2, 2, 200);

        // Corner pixels should remain at default (0)
        Assert.Equal(0, img.GetPixel(0, 0));
        Assert.Equal(0, img.GetPixel(0, 3));
        Assert.Equal(0, img.GetPixel(3, 0));
        Assert.Equal(0, img.GetPixel(3, 3));
    }

    [Fact]
    public void DrawRectangle_OneBySOne_SetsSinglePixel()
    {
        var img = NetpbmImage.Create(NetpbmFormat.PGM, 4, 4, 255);
        img.DrawRectangle(2, 2, 1, 1, 77);

        Assert.Equal(77, img.GetPixel(2, 2));
        // Adjacent pixels unchanged
        Assert.Equal(0, img.GetPixel(2, 1));
        Assert.Equal(0, img.GetPixel(1, 2));
    }

    // -------------------------------------------------------------------------
    // GetChannelStats tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelStats_NullImage_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(
            () => NetpbmImageAnalyzer.GetChannelStats(null!));
    }

    [Fact]
    public void GetChannelStats_PpmImage_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(NetpbmFormat.PPM, 2, 2, 255);
        var stats = NetpbmImageAnalyzer.GetChannelStats(img);
        Assert.NotNull(stats);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create -> DrawRectangle -> GetChannelStats pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreatePpm_DrawRectangle_GetChannelStats_ReturnsStats()
    {
        // Create a PPM image and draw a filled rectangle
        var img = NetpbmImage.Create(NetpbmFormat.PPM, 4, 4, 255);
        img.DrawRectangle(0, 0, 4, 4, 128);

        var stats = NetpbmImageAnalyzer.GetChannelStats(img);
        Assert.NotNull(stats);
        // With uniform pixel value, dimensions are preserved
        Assert.Equal(4, img.Width);
        Assert.Equal(4, img.Height);
    }
}
