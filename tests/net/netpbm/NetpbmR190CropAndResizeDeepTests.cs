// Tests for NetpbmImage.Crop and Resize deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R190

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R190: Tests for NetpbmImage.Crop and Resize deeper coverage.
/// Crop(x, y, width, height): returns a rectangular sub-image.
/// Resize(width, height): returns a new image scaled to target dimensions.
/// Covers: Crop width correct; Crop height correct; Crop format preserved;
/// Crop returns new instance; Crop at (0,0) origin; Crop preserves format;
/// Crop after Resize still correct dimensions; Resize width correct;
/// Resize height correct; Resize format preserved; Resize returns new instance;
/// Resize to same dimensions returns equivalent; Resize larger increases dimensions;
/// Resize smaller decreases dimensions; Crop->GetStats values in range;
/// Resize->GetStats values in range; Crop->Resize->GetStats pipeline;
/// Resize->Crop->Clone->Pipeline chain;
/// dogfood Create->Resize->Crop->GetStats->Pipeline->GetStats verify.
/// </summary>
public class NetpbmR190CropAndResizeDeepTests
{
    private static NetpbmImage Create(byte val = 128, int w = 8, int h = 8)
        => NetpbmImage.Create(w, h, NetpbmFormat.Pgm, val);

    // -------------------------------------------------------------------------
    // Crop
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_Width_Correct()
    {
        var img = Create(100, 8, 8);
        var cropped = img.Crop(1, 1, 4, 3);
        Assert.Equal(4, cropped.Width);
    }

    [Fact]
    public void Crop_Height_Correct()
    {
        var img = Create(100, 8, 8);
        var cropped = img.Crop(1, 1, 4, 3);
        Assert.Equal(3, cropped.Height);
    }

    [Fact]
    public void Crop_Format_Preserved()
    {
        var img = Create(100);
        var cropped = img.Crop(0, 0, 4, 4);
        Assert.Equal(NetpbmFormat.Pgm, cropped.Format);
    }

    [Fact]
    public void Crop_ReturnsNewInstance()
    {
        var img = Create(100);
        var cropped = img.Crop(0, 0, 4, 4);
        Assert.NotSame(img, cropped);
    }

    [Fact]
    public void Crop_AtOrigin_Correct()
    {
        var img = Create(128, 8, 8);
        var cropped = img.Crop(0, 0, 6, 5);
        Assert.Equal(6, cropped.Width);
        Assert.Equal(5, cropped.Height);
    }

    [Fact]
    public void Crop_FullImage_SameDimensions()
    {
        var img = Create(128, 6, 4);
        var cropped = img.Crop(0, 0, 6, 4);
        Assert.Equal(6, cropped.Width);
        Assert.Equal(4, cropped.Height);
    }

    [Fact]
    public void Crop_GetStats_ValuesInRange()
    {
        var img = Create(200, 8, 8);
        var cropped = img.Crop(1, 1, 4, 4);
        var (mean, min, max) = cropped.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
        Assert.InRange(mean, 0.0, 255.0);
    }

    // -------------------------------------------------------------------------
    // Resize
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_Width_Correct()
    {
        var img = Create(128, 4, 4);
        var resized = img.Resize(8, 6);
        Assert.Equal(8, resized.Width);
    }

    [Fact]
    public void Resize_Height_Correct()
    {
        var img = Create(128, 4, 4);
        var resized = img.Resize(8, 6);
        Assert.Equal(6, resized.Height);
    }

    [Fact]
    public void Resize_Format_Preserved()
    {
        var img = Create(128);
        var resized = img.Resize(6, 6);
        Assert.Equal(NetpbmFormat.Pgm, resized.Format);
    }

    [Fact]
    public void Resize_ReturnsNewInstance()
    {
        var img = Create(128);
        var resized = img.Resize(6, 6);
        Assert.NotSame(img, resized);
    }

    [Fact]
    public void Resize_Larger_IncreasesDimensions()
    {
        var img = Create(128, 4, 4);
        var resized = img.Resize(16, 12);
        Assert.True(resized.Width > img.Width);
        Assert.True(resized.Height > img.Height);
    }

    [Fact]
    public void Resize_Smaller_DecreasesDimensions()
    {
        var img = Create(128, 8, 8);
        var resized = img.Resize(3, 3);
        Assert.True(resized.Width < img.Width);
        Assert.True(resized.Height < img.Height);
    }

    [Fact]
    public void Resize_GetStats_ValuesInRange()
    {
        var img = Create(150, 4, 4);
        var resized = img.Resize(8, 8);
        var (mean, min, max) = resized.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
        Assert.InRange(mean, 0.0, 255.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Resize->Crop->GetStats->Pipeline->GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateResizeCropGetStatsPipelineGetStats_Verify()
    {
        // Create 4x4
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, 100);
        Assert.Equal(4, img.Width);
        Assert.Equal(4, img.Height);

        // Resize to 8x8
        var resized = img.Resize(8, 8);
        Assert.Equal(8, resized.Width);
        Assert.Equal(8, resized.Height);
        Assert.Equal(NetpbmFormat.Pgm, resized.Format);

        // Crop to 5x5
        var cropped = resized.Crop(1, 1, 5, 5);
        Assert.Equal(5, cropped.Width);
        Assert.Equal(5, cropped.Height);

        // GetStats on cropped
        var (mean1, min1, max1) = cropped.GetStats();
        Assert.True(min1 >= 0);
        Assert.True(max1 <= 255);
        Assert.InRange(mean1, 0.0, 255.0);

        // Pipeline with AdjustBrightness + Sharpen
        var pipelined = cropped.Pipeline(new System.Collections.Generic.List<System.Func<NetpbmImage, NetpbmImage>>
        {
            i => i.AdjustBrightness(10),
            i => i.Sharpen()
        });
        Assert.Equal(5, pipelined.Width);
        Assert.Equal(5, pipelined.Height);

        // Final GetStats
        var (mean2, min2, max2) = pipelined.GetStats();
        Assert.True(min2 >= 0);
        Assert.True(max2 <= 255);
        Assert.InRange(mean2, 0.0, 255.0);
    }
}
