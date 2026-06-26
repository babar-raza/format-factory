// Tests for NetpbmImage.DrawLine, GetHistogram, GetStats deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R203

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R203: Tests for NetpbmImage.DrawLine, GetHistogram, GetStats deeper coverage.
/// DrawLine(x1, y1, x2, y2, value): draws a line segment between two points.
/// GetHistogram(): returns the pixel value frequency distribution.
/// GetStats(): returns image statistics (mean, stddev, min, max).
/// Covers: DrawLine non-null; DrawLine preserves dimensions; DrawLine horizontal preserves size;
/// DrawLine vertical preserves size; DrawLine diagonal preserves size;
/// GetHistogram non-null; GetHistogram count positive; GetHistogram total equals pixel count;
/// GetHistogram contains canvas fill value; GetStats non-null; GetStats MinValue <= MaxValue;
/// GetStats MeanValue between Min and Max; GetStats PixelCount equals Width*Height;
/// dogfood CreateCanvas->DrawLine->GetHistogram->GetStats->Verify pipeline.
/// </summary>
public class NetpbmR203DrawLineAndGetHistogramDeepTests
{
    // -------------------------------------------------------------------------
    // DrawLine
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawLine_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 200);
        Assert.NotNull(img.DrawLine(0, 0, 7, 7, 50));
    }

    [Fact]
    public void DrawLine_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.Pgm, 200);
        var result = img.DrawLine(0, 0, 7, 5, 50);
        Assert.Equal(8, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void DrawLine_Horizontal_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 6, NetpbmFormat.Pgm, 200);
        var result = img.DrawLine(0, 3, 9, 3, 100);
        Assert.Equal(10, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void DrawLine_Vertical_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 10, NetpbmFormat.Pgm, 200);
        var result = img.DrawLine(3, 0, 3, 9, 100);
        Assert.Equal(6, result.Width);
        Assert.Equal(10, result.Height);
    }

    [Fact]
    public void DrawLine_Diagonal_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 200);
        var result = img.DrawLine(0, 7, 7, 0, 50);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void DrawLine_Chain_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 200);
        var result = img.DrawLine(0, 0, 7, 0, 50).DrawLine(0, 7, 7, 7, 100);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // GetHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 128);
        Assert.NotNull(img.GetHistogram());
    }

    [Fact]
    public void GetHistogram_CountPositive()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 128);
        var hist = img.GetHistogram();
        Assert.True(hist.Count > 0);
    }

    [Fact]
    public void GetHistogram_TotalEqualsPixelCount()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 128);
        var hist = img.GetHistogram();
        var total = 0;
        foreach (var count in hist.Values)
            total += count;
        Assert.Equal(img.Width * img.Height, total);
    }

    [Fact]
    public void GetHistogram_ContainsCanvasFillValue()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 128);
        var hist = img.GetHistogram();
        // All pixels are 128, so histogram should have 128 as a key
        Assert.True(hist.ContainsKey(128));
    }

    [Fact]
    public void GetHistogram_AfterDrawLine_HasMultipleValues()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 200);
        var withLine = img.DrawLine(0, 0, 7, 7, 50);
        var hist = withLine.GetHistogram();
        // Should have at least 2 values: 200 (background) and 50 (line)
        Assert.True(hist.Count >= 2);
    }

    // -------------------------------------------------------------------------
    // GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStats_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 128);
        Assert.NotNull(img.GetStats());
    }

    [Fact]
    public void GetStats_MinLessThanOrEqualMax()
    {
        var img = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 128);
        var stats = img.GetStats();
        Assert.True(stats.MinValue <= stats.MaxValue);
    }

    [Fact]
    public void GetStats_MeanBetweenMinAndMax()
    {
        var img = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 128);
        var stats = img.GetStats();
        Assert.True(stats.MeanValue >= stats.MinValue);
        Assert.True(stats.MeanValue <= stats.MaxValue);
    }

    [Fact]
    public void GetStats_PixelCountEqualsWidthTimesHeight()
    {
        var img = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 128);
        var stats = img.GetStats();
        Assert.Equal(img.Width * img.Height, stats.PixelCount);
    }

    [Fact]
    public void GetStats_UniformCanvas_MinEqualsMax()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 100);
        var stats = img.GetStats();
        Assert.Equal(stats.MinValue, stats.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_DrawLine_GetHistogram_GetStats_Verify_Pipeline()
    {
        // CreateCanvas
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 200);
        Assert.Equal(10, img.Width);
        Assert.Equal(10, img.Height);

        // DrawLine border
        var bordered = img
            .DrawLine(0, 0, 9, 0, 50)   // top
            .DrawLine(0, 9, 9, 9, 50)   // bottom
            .DrawLine(0, 0, 0, 9, 50)   // left
            .DrawLine(9, 0, 9, 9, 50);  // right

        Assert.Equal(10, bordered.Width);
        Assert.Equal(10, bordered.Height);

        // GetHistogram
        var hist = bordered.GetHistogram();
        Assert.NotNull(hist);
        Assert.True(hist.Count >= 2); // background (200) and border (50)
        var total = 0;
        foreach (var v in hist.Values) total += v;
        Assert.Equal(100, total); // 10x10 = 100 pixels

        // GetStats
        var stats = bordered.GetStats();
        Assert.NotNull(stats);
        Assert.Equal(100, stats.PixelCount);
        Assert.True(stats.MinValue <= 50);
        Assert.True(stats.MaxValue >= 200);
        Assert.True(stats.MeanValue >= stats.MinValue);
        Assert.True(stats.MeanValue <= stats.MaxValue);

        // DrawLine diagonal
        var withDiag = bordered.DrawLine(1, 1, 8, 8, 128);
        var diagStats = withDiag.GetStats();
        Assert.Equal(100, diagStats.PixelCount);
    }
}
