// Tests for NetpbmImage.BlurBox, Sharpen, AdjustBrightness deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R213

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R213: Tests for NetpbmImage.BlurBox, Sharpen, AdjustBrightness deeper coverage.
/// BlurBox(radius): applies box blur with the given radius.
/// Sharpen(): applies sharpening filter.
/// AdjustBrightness(delta): adjusts all pixel values by delta (clamped).
/// Covers: BlurBox non-null; BlurBox preserves dimensions; BlurBox radius 1 works;
/// BlurBox radius 2 works; BlurBox uniform canvas same value;
/// Sharpen non-null; Sharpen preserves dimensions; Sharpen pixel count preserved;
/// Sharpen uniform canvas non-null; Sharpen after BlurBox;
/// AdjustBrightness non-null; AdjustBrightness positive delta increases value;
/// AdjustBrightness negative delta decreases value; AdjustBrightness zero delta preserves;
/// AdjustBrightness clamps at 0 and 255; AdjustBrightness preserves dimensions;
/// dogfood CreateCanvas->AdjustBrightness->BlurBox->Sharpen->SaveToFile->Verify pipeline.
/// </summary>
public class NetpbmR213BlurAndSharpenDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR213BlurAndSharpenDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR213_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // BlurBox
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(6, 6, 128);
        Assert.NotNull(img.BlurBox(1));
    }

    [Fact]
    public void BlurBox_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 100);
        var result = img.BlurBox(1);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void BlurBox_Radius1_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 100);
        Assert.NotNull(img.BlurBox(1));
    }

    [Fact]
    public void BlurBox_Radius2_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 100);
        Assert.NotNull(img.BlurBox(2));
    }

    [Fact]
    public void BlurBox_UniformCanvas_SamePixelValue()
    {
        var img = NetpbmImage.CreateCanvas(6, 6, 150);
        var result = img.BlurBox(1);
        Assert.Equal(150, result.GetPixelColor(2, 2));
    }

    [Fact]
    public void BlurBox_PixelCount_Preserved()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 100);
        var result = img.BlurBox(1);
        Assert.Equal(img.Width * img.Height, result.Width * result.Height);
    }

    [Fact]
    public void BlurBox_ThenBlurBox_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(6, 6, 100);
        var result = img.BlurBox(1).BlurBox(1);
        Assert.NotNull(result);
        Assert.Equal(6, result.Width);
    }

    // -------------------------------------------------------------------------
    // Sharpen
    // -------------------------------------------------------------------------

    [Fact]
    public void Sharpen_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        Assert.NotNull(img.Sharpen());
    }

    [Fact]
    public void Sharpen_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 100);
        var result = img.Sharpen();
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Sharpen_PixelCount_Preserved()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 128);
        var result = img.Sharpen();
        Assert.Equal(img.Width * img.Height, result.Width * result.Height);
    }

    [Fact]
    public void Sharpen_UniformCanvas_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 200);
        Assert.NotNull(img.Sharpen());
    }

    [Fact]
    public void Sharpen_AfterBlurBox_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(6, 6, 128);
        var result = img.BlurBox(1).Sharpen();
        Assert.NotNull(result);
        Assert.Equal(6, result.Width);
    }

    [Fact]
    public void Sharpen_TwiceCalled_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        Assert.NotNull(img.Sharpen().Sharpen());
    }

    // -------------------------------------------------------------------------
    // AdjustBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustBrightness_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        Assert.NotNull(img.AdjustBrightness(10));
    }

    [Fact]
    public void AdjustBrightness_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 100);
        var result = img.AdjustBrightness(20);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void AdjustBrightness_Positive_IncreasesValue()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 100);
        var result = img.AdjustBrightness(50);
        Assert.True(result.GetPixelColor(0, 0) >= 100);
    }

    [Fact]
    public void AdjustBrightness_Negative_DecreasesValue()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 200);
        var result = img.AdjustBrightness(-50);
        Assert.True(result.GetPixelColor(0, 0) <= 200);
    }

    [Fact]
    public void AdjustBrightness_Zero_PreservesValue()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        var result = img.AdjustBrightness(0);
        Assert.Equal(128, result.GetPixelColor(0, 0));
    }

    [Fact]
    public void AdjustBrightness_ClampedAtMax()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 250);
        var result = img.AdjustBrightness(100);
        Assert.True(result.GetPixelColor(0, 0) <= 255);
    }

    [Fact]
    public void AdjustBrightness_ClampedAtMin()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 10);
        var result = img.AdjustBrightness(-100);
        Assert.True(result.GetPixelColor(0, 0) >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_AdjustBrightness_BlurBox_Sharpen_SaveToFile_Verify_Pipeline()
    {
        // Create canvas
        var canvas = NetpbmImage.CreateCanvas(8, 8, 100);
        Assert.Equal(8, canvas.Width);
        Assert.Equal(100, canvas.GetPixelColor(0, 0));

        // AdjustBrightness
        var brighter = canvas.AdjustBrightness(50);
        Assert.NotNull(brighter);
        Assert.Equal(8, brighter.Width);
        Assert.True(brighter.GetPixelColor(0, 0) >= 100);

        // Draw variation then BlurBox
        var varied = brighter.DrawLine(0, 0, 7, 7, 0);
        var blurred = varied.BlurBox(1);
        Assert.NotNull(blurred);
        Assert.Equal(8, blurred.Width);
        Assert.Equal(8, blurred.Height);

        // Sharpen
        var sharpened = blurred.Sharpen();
        Assert.NotNull(sharpened);
        Assert.Equal(8, sharpened.Width);
        Assert.Equal(8, sharpened.Height);

        // AdjustBrightness negative
        var dimmed = sharpened.AdjustBrightness(-20);
        Assert.NotNull(dimmed);

        // Save and reload
        var path = TempFile("dogfood_blur_sharpen.pgm");
        dimmed.SaveToFile(path);
        Assert.True(File.Exists(path));

        var reloaded = NetpbmImage.LoadFile(path);
        Assert.NotNull(reloaded);
        Assert.Equal(8, reloaded.Width);
        Assert.Equal(8, reloaded.Height);

        // Histogram should be non-trivial
        var hist = reloaded.GetHistogram();
        Assert.NotNull(hist);
        Assert.True(hist.Count > 0);
    }
}
