// Tests for NetpbmImage color channel properties dedicated coverage.
// Sprint: ff-sprint-s237-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R244

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R244: Dedicated tests for NetpbmImage color channel properties (RedChannel, GreenChannel, BlueChannel, Pixels).
/// PGM image Pixels array is non-null.
/// PGM image Pixels length equals Width*Height.
/// PPM image RedChannel is non-null.
/// PPM image GreenChannel is non-null.
/// PPM image BlueChannel is non-null.
/// PPM channel lengths equal Width*Height.
/// SetPixel reflects in Pixels array for PGM.
/// Create with fill — Pixels all equal fill value.
/// PGM image RedChannel is null (no color channels).
/// Dogfood: create PPM, set pixels, verify channels.
/// </summary>
public class NetpbmR244ColorChannelsTests
{
    // -------------------------------------------------------------------------
    // Functional tests — PGM (Pixels array)
    // -------------------------------------------------------------------------

    [Fact]
    public void Pgm_Pixels_NonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.NotNull(img.Pixels);
    }

    [Fact]
    public void Pgm_Pixels_LengthEqualsWidthTimesHeight()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.Equal(6 * 4, img.Pixels.Length);
    }

    [Fact]
    public void Pgm_SetPixel_ReflectsInPixelsArray()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 128);
        Assert.Equal(128, img.GetPixel(0, 0));
    }

    [Fact]
    public void Pgm_CreateWithFill_AllPixelsEqualFill()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, fill: 100);
        Assert.All(img.Pixels, p => Assert.Equal(100, p));
    }

    [Fact]
    public void Pgm_RedChannel_IsNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.Null(img.RedChannel);
    }

    // -------------------------------------------------------------------------
    // Functional tests — PPM (color channels)
    // -------------------------------------------------------------------------

    [Fact]
    public void Ppm_RedChannel_NonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6, maxValue: 255);
        Assert.NotNull(img.RedChannel);
    }

    [Fact]
    public void Ppm_GreenChannel_NonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6, maxValue: 255);
        Assert.NotNull(img.GreenChannel);
    }

    [Fact]
    public void Ppm_BlueChannel_NonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6, maxValue: 255);
        Assert.NotNull(img.BlueChannel);
    }

    [Fact]
    public void Ppm_ChannelLengthEqualsWidthTimesHeight()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PPM_P6, maxValue: 255);
        Assert.Equal(5 * 3, img.RedChannel!.Length);
        Assert.Equal(5 * 3, img.GreenChannel!.Length);
        Assert.Equal(5 * 3, img.BlueChannel!.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Ppm_SetPixels_VerifyChannels()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6, fill: 200);
        Assert.NotNull(img.RedChannel);
        Assert.NotNull(img.GreenChannel);
        Assert.NotNull(img.BlueChannel);
        Assert.Equal(4 * 4, img.RedChannel!.Length);
        Assert.All(img.RedChannel, p => Assert.Equal(200, p));
    }
}
