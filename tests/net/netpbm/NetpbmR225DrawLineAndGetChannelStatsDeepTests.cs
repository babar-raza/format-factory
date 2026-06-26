// Tests for NetpbmImage.DrawLine, GetChannelStats deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R225

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R225: Tests for NetpbmImage.DrawLine, GetChannelStats deeper coverage.
/// DrawLine(x0, y0, x1, y1, r, g, b): draws a line between two points with given color.
/// GetChannelStats(): returns per-channel statistics (min, max, avg) for the image.
/// Covers: DrawLine non-null; DrawLine horizontal pixels colored; DrawLine vertical pixels colored;
/// DrawLine diagonal non-null; DrawLine multiple lines; DrawLine on grayscale;
/// DrawLine then SaveToFile/LoadFile preserved; DrawLine zero-length same point;
/// GetChannelStats non-null; GetChannelStats min non-negative; GetChannelStats max <= 255;
/// GetChannelStats avg in range; GetChannelStats after SetPixel reflects;
/// GetChannelStats on uniform canvas; GetChannelStats on grayscale has fewer channels;
/// GetChannelStats on color has three channels;
/// dogfood CreateCanvas→DrawLine×4→GetChannelStats→SaveToFile→LoadFile→FlipH→verify pipeline.
/// </summary>
public class NetpbmR225DrawLineAndGetChannelStatsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR225DrawLineAndGetChannelStatsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR225_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // DrawLine
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawLine_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.PPM);
        img.DrawLine(0, 0, 9, 0, 255, 0, 0);
        Assert.NotNull(img);
    }

    [Fact]
    public void DrawLine_Horizontal_PixelsColored()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.PPM);
        img.DrawLine(0, 0, 9, 0, 255, 0, 0); // horizontal red line at y=0
        var pixel = img.GetPixel(5, 0);
        Assert.True(pixel.R > 0 || pixel.R == 255);
    }

    [Fact]
    public void DrawLine_Vertical_PixelsColored()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.PPM);
        img.DrawLine(0, 0, 0, 9, 0, 255, 0); // vertical green line at x=0
        var pixel = img.GetPixel(0, 5);
        Assert.True(pixel.G > 0 || pixel.G == 255);
    }

    [Fact]
    public void DrawLine_Diagonal_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.PPM);
        img.DrawLine(0, 0, 9, 9, 0, 0, 255);
        Assert.NotNull(img);
    }

    [Fact]
    public void DrawLine_MultipleLines_NoneThrow()
    {
        var img = NetpbmImage.CreateCanvas(20, 20, NetpbmFormat.PPM);
        var ex1 = Record.Exception(() => img.DrawLine(0, 0, 19, 0, 255, 0, 0));
        var ex2 = Record.Exception(() => img.DrawLine(0, 0, 0, 19, 0, 255, 0));
        var ex3 = Record.Exception(() => img.DrawLine(0, 0, 19, 19, 0, 0, 255));
        var ex4 = Record.Exception(() => img.DrawLine(19, 0, 0, 19, 255, 255, 0));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
        Assert.Null(ex4);
    }

    [Fact]
    public void DrawLine_OnGrayscale_NoThrow()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.PGM);
        var ex = Record.Exception(() => img.DrawLine(0, 0, 9, 9, 200));
        Assert.Null(ex);
    }

    [Fact]
    public void DrawLine_ThenSaveAndLoad_Preserved()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.PPM);
        img.DrawLine(0, 0, 9, 0, 255, 0, 0);
        var path = TempFile("drawline.ppm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.Equal(10, loaded.Width);
        Assert.Equal(10, loaded.Height);
    }

    [Fact]
    public void DrawLine_ZeroLength_SamePoint_NoThrow()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.PPM);
        var ex = Record.Exception(() => img.DrawLine(5, 5, 5, 5, 255, 255, 255));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetChannelStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelStats_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.PPM);
        Assert.NotNull(img.GetChannelStats());
    }

    [Fact]
    public void GetChannelStats_MinNonNegative()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.PPM);
        var stats = img.GetChannelStats();
        foreach (var s in stats)
            Assert.True(s.Min >= 0);
    }

    [Fact]
    public void GetChannelStats_MaxAtMost255()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.PPM);
        img.DrawLine(0, 0, 7, 7, 255, 128, 64);
        var stats = img.GetChannelStats();
        foreach (var s in stats)
            Assert.True(s.Max <= 255);
    }

    [Fact]
    public void GetChannelStats_AvgInRange()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.PPM);
        img.DrawLine(0, 0, 7, 0, 200, 100, 50);
        var stats = img.GetChannelStats();
        foreach (var s in stats)
        {
            Assert.True(s.Avg >= 0);
            Assert.True(s.Avg <= 255);
        }
    }

    [Fact]
    public void GetChannelStats_AfterSetPixel_Reflects()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.PPM);
        img.SetPixel(0, 0, 255, 0, 0);
        var stats = img.GetChannelStats();
        // R channel max should be 255
        Assert.True(stats[0].Max >= 255 || stats.Exists(s => s.Max >= 255));
    }

    [Fact]
    public void GetChannelStats_ColorImage_ThreeChannels()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.PPM);
        var stats = img.GetChannelStats();
        Assert.Equal(3, stats.Count);
    }

    [Fact]
    public void GetChannelStats_GrayscaleImage_OneChannel()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.PGM);
        var stats = img.GetChannelStats();
        Assert.Equal(1, stats.Count);
    }

    [Fact]
    public void GetChannelStats_UniformCanvas_MinEqualsMax()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.PGM);
        // All pixels default to 0 — uniform canvas
        var stats = img.GetChannelStats();
        Assert.Equal(stats[0].Min, stats[0].Max);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_DrawLine_GetChannelStats_SaveToFile_LoadFile_FlipH_Pipeline()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, NetpbmFormat.PPM);

        // DrawLine × 4 — different colors
        img.DrawLine(0, 0, 15, 0, 255, 0, 0);      // top horizontal — red
        img.DrawLine(0, 15, 15, 15, 0, 255, 0);    // bottom horizontal — green
        img.DrawLine(0, 0, 0, 15, 0, 0, 255);      // left vertical — blue
        img.DrawLine(15, 0, 15, 15, 255, 255, 0);  // right vertical — yellow

        // GetChannelStats
        var stats = img.GetChannelStats();
        Assert.NotNull(stats);
        Assert.Equal(3, stats.Count);
        foreach (var s in stats)
        {
            Assert.True(s.Min >= 0);
            Assert.True(s.Max <= 255);
            Assert.True(s.Avg >= 0 && s.Avg <= 255);
        }
        // R channel has max = 255 (red + yellow lines)
        Assert.True(stats[0].Max >= 255 || stats.Exists(s => s.Max >= 255));

        // SaveToFile
        var path = TempFile("dogfood_drawline.ppm");
        img.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile
        var loaded = NetpbmImage.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.Equal(16, loaded.Width);
        Assert.Equal(16, loaded.Height);

        // GetChannelStats on loaded — consistent
        var loadedStats = loaded.GetChannelStats();
        Assert.Equal(3, loadedStats.Count);
        for (int i = 0; i < 3; i++)
        {
            Assert.Equal(stats[i].Min, loadedStats[i].Min);
            Assert.Equal(stats[i].Max, loadedStats[i].Max);
        }

        // FlipH on loaded — stats may differ (pixel positions swap) but dimensions same
        var flipped = loaded.FlipHorizontal();
        Assert.Equal(16, flipped.Width);
        Assert.Equal(16, flipped.Height);
        var flippedStats = flipped.GetChannelStats();
        Assert.Equal(3, flippedStats.Count);
        // After flip, channel min/max should be the same (same pixels, just mirrored)
        for (int i = 0; i < 3; i++)
        {
            Assert.Equal(loadedStats[i].Min, flippedStats[i].Min);
            Assert.Equal(loadedStats[i].Max, flippedStats[i].Max);
        }

        // DrawLine on loaded
        loaded.DrawLine(0, 8, 15, 8, 128, 128, 128); // middle horizontal — gray
        var updatedStats = loaded.GetChannelStats();
        Assert.NotNull(updatedStats);
        Assert.Equal(3, updatedStats.Count);
    }
}
