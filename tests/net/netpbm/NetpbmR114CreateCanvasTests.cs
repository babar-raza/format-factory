using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R114 Train C: NetpbmImage.Create — blank canvas factory for image composition pipelines.
/// </summary>
public class NetpbmR114CreateCanvasTests
{
    [Fact]
    public void Create_GrayscaleCanvas_CorrectDimensions()
    {
        var img = NetpbmImage.Create(10, 8, NetpbmFormat.PGM_P2);
        Assert.Equal(10, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void Create_GrayscaleCanvas_AllZeroByDefault()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P2);
        Assert.All(img.Pixels, p => Assert.Equal(0, p));
    }

    [Fact]
    public void Create_GrayscaleCanvas_FillValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P2, fill: 128);
        Assert.All(img.Pixels, p => Assert.Equal(128, p));
    }

    [Fact]
    public void Create_ColorCanvas_HasChannels()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM_P3);
        Assert.NotNull(img.RedChannel);
        Assert.NotNull(img.GreenChannel);
        Assert.NotNull(img.BlueChannel);
    }

    [Fact]
    public void Create_ColorCanvas_ChannelsFilledCorrectly()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P3, fill: 200);
        Assert.All(img.RedChannel!, p => Assert.Equal(200, p));
        Assert.All(img.GreenChannel!, p => Assert.Equal(200, p));
        Assert.All(img.BlueChannel!, p => Assert.Equal(200, p));
    }

    [Fact]
    public void Create_InvalidWidth_Throws()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            NetpbmImage.Create(0, 4, NetpbmFormat.PGM_P2));
    }

    [Fact]
    public void Create_InvalidHeight_Throws()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            NetpbmImage.Create(4, -1, NetpbmFormat.PGM_P2));
    }

    [Fact]
    public void Create_CanvasIsEditable()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P2);
        img.SetPixel(2, 2, 99);
        Assert.Equal(99, img.GetPixel(2, 2));
    }
}
