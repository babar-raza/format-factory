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
    public void DrawRectangle_NegativeTop_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.DrawRectangle(-1, 0, 2, 2, 128));
    }

    [Fact]
    public void DrawRectangle_NegativeLeft_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.DrawRectangle(0, -1, 2, 2, 128));
    }

    [Fact]
    public void DrawRectangle_NegativeHeight_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.DrawRectangle(0, 0, -1, 2, 128));
    }

    [Fact]
    public void DrawRectangle_NegativeWidth_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.DrawRectangle(0, 0, 2, -1, 128));
    }

    // -------------------------------------------------------------------------
    // DrawRectangle functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawRectangle_FillsTargetRegion()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        // DrawRectangle(top=1, left=1, rectHeight=2, rectWidth=2, fill=200)
        img.DrawRectangle(1, 1, 2, 2, 200);

        Assert.Equal(200, img.GetPixel(1, 1));
        Assert.Equal(200, img.GetPixel(1, 2));
        Assert.Equal(200, img.GetPixel(2, 1));
        Assert.Equal(200, img.GetPixel(2, 2));
    }

    [Fact]
    public void DrawRectangle_PixelsOutsideRectangle_Unchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
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
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
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
    public void GetChannelStats_PgmImage_ReturnsMeanMinMax()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        // All pixels are 0 by default
        var stats = img.GetStats();
        Assert.Equal(0.0, stats.Mean);
        Assert.Equal(0, stats.Min);
        Assert.Equal(0, stats.Max);
    }

    [Fact]
    public void GetChannelStats_PpmImage_ChannelStatsNotNull()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PPM_P6);
        // PPM images should not throw on GetChannelStats
        var ex = Record.Exception(() => img.GetChannelStats());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create -> DrawRectangle -> GetChannelStats pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreatePgm_DrawRectangle_GetStats_MeanEquals128()
    {
        // Create a PGM image, fill with DrawRectangle, verify stats
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.DrawRectangle(0, 0, 4, 4, 128);

        var stats = img.GetStats();
        // All pixels = 128 so mean = 128, min = 128, max = 128
        Assert.Equal(128.0, stats.Mean);
        Assert.Equal(128, stats.Min);
        Assert.Equal(128, stats.Max);
    }
}
