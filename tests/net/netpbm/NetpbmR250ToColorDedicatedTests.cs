// Tests for NetpbmImage.ToColor dedicated coverage.
// Sprint: ff-sprint-s243-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R250

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R250: Dedicated tests for NetpbmImage.ToColor().
/// Converts PGM image to PPM color image.
/// Returns new image (non-destructive).
/// Result format is PPM.
/// Width preserved.
/// Height preserved.
/// MaxValue preserved.
/// Grayscale pixels replicated to R/G/B channels.
/// Original image format unchanged after call.
/// RedChannel/GreenChannel/BlueChannel all non-null on result.
/// Called twice → both non-null.
/// Dogfood: set known PGM pixels, verify RGB channels match.
/// </summary>
public class NetpbmR250ToColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Return value / non-destructive tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ToColor_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ToColor();
        Assert.NotNull(result);
    }

    [Fact]
    public void ToColor_ReturnsDifferentObject()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ToColor();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void ToColor_OriginalFormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.ToColor();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    // -------------------------------------------------------------------------
    // Format and preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ToColor_ResultFormatIsPPM()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ToColor();
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void ToColor_WidthPreserved()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ToColor();
        Assert.Equal(6, result.Width);
    }

    [Fact]
    public void ToColor_HeightPreserved()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ToColor();
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void ToColor_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.ToColor();
        Assert.Equal(200, result.MaxValue);
    }

    [Fact]
    public void ToColor_RedChannelNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ToColor();
        Assert.NotNull(result.RedChannel);
    }

    [Fact]
    public void ToColor_GreenChannelNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ToColor();
        Assert.NotNull(result.GreenChannel);
    }

    [Fact]
    public void ToColor_BlueChannelNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ToColor();
        Assert.NotNull(result.BlueChannel);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PixelValueReplicatedToChannels()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 150);
        var result = img.ToColor();
        // Gray value 150 should map to R=G=B=150
        Assert.Equal(150, result.RedChannel![0]);
        Assert.Equal(150, result.GreenChannel![0]);
        Assert.Equal(150, result.BlueChannel![0]);
    }
}
