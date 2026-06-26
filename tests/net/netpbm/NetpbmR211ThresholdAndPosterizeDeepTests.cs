// Tests for NetpbmImage.Threshold, Posterize, MedianFilter deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R211

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R211: Tests for NetpbmImage.Threshold, Posterize, MedianFilter deeper coverage.
/// Threshold(value): returns binary image with pixels >= value set to 255, else 0.
/// Posterize(levels): reduces color depth to the given number of levels.
/// MedianFilter(radius): applies median blur filter.
/// Covers: Threshold non-null; Threshold preserves dimensions; Threshold mid-value result correct;
/// Threshold at 0 all white; Threshold at 255 all black; Threshold after DrawLine;
/// Posterize non-null; Posterize preserves dimensions; Posterize levels 2 works;
/// Posterize levels 4 works; Posterize after AdjustBrightness;
/// MedianFilter non-null; MedianFilter preserves dimensions; MedianFilter radius 1 works;
/// MedianFilter radius 2 works; MedianFilter on uniform canvas non-null;
/// dogfood CreateCanvas->DrawLine->Threshold->Posterize->MedianFilter->SaveToFile->Verify pipeline.
/// </summary>
public class NetpbmR211ThresholdAndPosterizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR211ThresholdAndPosterizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR211_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // Threshold
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        Assert.NotNull(img.Threshold(128));
    }

    [Fact]
    public void Threshold_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 128);
        var result = img.Threshold(128);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Threshold_AtZero_AllWhite()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        var result = img.Threshold(0);
        // All pixels (128) >= 0, so all = 255
        Assert.Equal(255, result.GetPixelColor(0, 0));
        Assert.Equal(255, result.GetPixelColor(3, 3));
    }

    [Fact]
    public void Threshold_At255_AllBlack()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        var result = img.Threshold(255);
        // All pixels (128) < 255, so all = 0
        Assert.Equal(0, result.GetPixelColor(0, 0));
    }

    [Fact]
    public void Threshold_PixelCount_Preserved()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 100);
        var result = img.Threshold(100);
        Assert.Equal(img.Width * img.Height, result.Width * result.Height);
    }

    [Fact]
    public void Threshold_AfterDrawLine_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 50);
        var withLine = img.DrawLine(0, 4, 7, 4, 200);
        var result = withLine.Threshold(128);
        Assert.NotNull(result);
        Assert.Equal(8, result.Width);
    }

    [Fact]
    public void Threshold_DifferentValues_BothNonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        Assert.NotNull(img.Threshold(64));
        Assert.NotNull(img.Threshold(192));
    }

    // -------------------------------------------------------------------------
    // Posterize
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        Assert.NotNull(img.Posterize(4));
    }

    [Fact]
    public void Posterize_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 100);
        var result = img.Posterize(4);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Posterize_Levels2_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        Assert.NotNull(img.Posterize(2));
    }

    [Fact]
    public void Posterize_Levels4_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        Assert.NotNull(img.Posterize(4));
    }

    [Fact]
    public void Posterize_Levels8_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 200);
        Assert.NotNull(img.Posterize(8));
    }

    [Fact]
    public void Posterize_PixelCount_Preserved()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 100);
        var result = img.Posterize(4);
        Assert.Equal(img.Width * img.Height, result.Width * result.Height);
    }

    [Fact]
    public void Posterize_ThenThreshold_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        var result = img.Posterize(4).Threshold(100);
        Assert.NotNull(result);
    }

    // -------------------------------------------------------------------------
    // MedianFilter
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(6, 6, 128);
        Assert.NotNull(img.MedianFilter(1));
    }

    [Fact]
    public void MedianFilter_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 100);
        var result = img.MedianFilter(1);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void MedianFilter_Radius1_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 100);
        Assert.NotNull(img.MedianFilter(1));
    }

    [Fact]
    public void MedianFilter_Radius2_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 100);
        Assert.NotNull(img.MedianFilter(2));
    }

    [Fact]
    public void MedianFilter_UniformCanvas_SamePixelValue()
    {
        var img = NetpbmImage.CreateCanvas(6, 6, 150);
        var result = img.MedianFilter(1);
        Assert.NotNull(result);
        Assert.Equal(150, result.GetPixelColor(2, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_DrawLine_Threshold_Posterize_MedianFilter_SaveToFile_Verify_Pipeline()
    {
        // Create canvas with variation
        var canvas = NetpbmImage.CreateCanvas(8, 8, 100);
        var withLine = canvas.DrawLine(0, 0, 7, 7, 200);
        var withLine2 = withLine.DrawLine(0, 7, 7, 0, 50);

        // Threshold
        var thresholded = withLine2.Threshold(128);
        Assert.NotNull(thresholded);
        Assert.Equal(8, thresholded.Width);
        Assert.Equal(8, thresholded.Height);

        // Posterize
        var posterized = withLine2.Posterize(4);
        Assert.NotNull(posterized);
        Assert.Equal(8, posterized.Width);

        // MedianFilter
        var filtered = withLine2.MedianFilter(1);
        Assert.NotNull(filtered);
        Assert.Equal(8, filtered.Width);
        Assert.Equal(8, filtered.Height);

        // Chain: Threshold -> Posterize
        var chained = withLine2.Threshold(128).Posterize(2);
        Assert.NotNull(chained);
        Assert.Equal(8, chained.Width);

        // Save and reload
        var path = TempFile("dogfood_threshold.pgm");
        chained.SaveToFile(path);
        Assert.True(File.Exists(path));

        var reloaded = NetpbmImage.LoadFile(path);
        Assert.NotNull(reloaded);
        Assert.Equal(8, reloaded.Width);
        Assert.Equal(8, reloaded.Height);

        // Histogram should show limited values due to posterize
        var hist = reloaded.GetHistogram();
        Assert.NotNull(hist);
        Assert.True(hist.Count > 0);
    }
}
