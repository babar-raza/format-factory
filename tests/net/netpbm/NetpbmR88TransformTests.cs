// R88 Train J — Netpbm .NET FlipVertical + Invert transform tests
using Xunit;
using FormatFactory.Netpbm;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR88TransformTests
{
    // ---- FlipVertical (PGM) ----

    [Fact]
    public void FlipVertical_PGM_SwapsTopAndBottom()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 2, Height = 3, MaxValue = 255,
            Pixels = new byte[] { 10, 20, 30, 40, 50, 60 }
        };
        img.FlipVertical();
        // Row 0 (was 10,20) should now be row 2 values (50,60)
        Assert.Equal(50, img.GetPixel(0, 0));
        Assert.Equal(60, img.GetPixel(0, 1));
        Assert.Equal(10, img.GetPixel(2, 0));
        Assert.Equal(20, img.GetPixel(2, 1));
        // Middle row unchanged
        Assert.Equal(30, img.GetPixel(1, 0));
    }

    [Fact]
    public void FlipVertical_PBM_SwapsRows()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 2, Height = 2, MaxValue = 1,
            Pixels = new byte[] { 0, 1, 1, 0 }
        };
        img.FlipVertical();
        Assert.Equal(1, img.GetPixel(0, 0));
        Assert.Equal(0, img.GetPixel(0, 1));
        Assert.Equal(0, img.GetPixel(1, 0));
        Assert.Equal(1, img.GetPixel(1, 1));
    }

    [Fact]
    public void FlipVertical_PPM_SwapsColorRows()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1, Height = 2, MaxValue = 255,
            Pixels = System.Array.Empty<byte>(),
            RedChannel = new byte[] { 100, 200 },
            GreenChannel = new byte[] { 50, 150 },
            BlueChannel = new byte[] { 10, 90 }
        };
        img.FlipVertical();
        Assert.Equal((200, 150, 90), img.GetPixelColor(0, 0));
        Assert.Equal((100, 50, 10), img.GetPixelColor(1, 0));
    }

    [Fact]
    public void FlipVertical_Twice_RestoresOriginal()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 1, 2, 3, 4, 5, 6 }
        };
        img.FlipVertical();
        img.FlipVertical();
        Assert.Equal(new byte[] { 1, 2, 3, 4, 5, 6 }, img.Pixels);
    }

    // ---- Invert ----

    [Fact]
    public void Invert_PBM_Toggles01()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 4, Height = 1, MaxValue = 1,
            Pixels = new byte[] { 0, 1, 1, 0 }
        };
        img.Invert();
        Assert.Equal(new byte[] { 1, 0, 0, 1 }, img.Pixels);
    }

    [Fact]
    public void Invert_PGM_SubtractsFromMax()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 0, 128, 255 }
        };
        img.Invert();
        Assert.Equal(255, img.Pixels[0]);
        Assert.Equal(127, img.Pixels[1]);
        Assert.Equal(0, img.Pixels[2]);
    }

    [Fact]
    public void Invert_PPM_InvertsAllChannels()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = System.Array.Empty<byte>(),
            RedChannel = new byte[] { 100 },
            GreenChannel = new byte[] { 0 },
            BlueChannel = new byte[] { 255 }
        };
        img.Invert();
        Assert.Equal((155, 255, 0), img.GetPixelColor(0, 0));
    }

    [Fact]
    public void Invert_Twice_RestoresOriginal()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 0, 128, 255 }
        };
        img.Invert();
        img.Invert();
        Assert.Equal(new byte[] { 0, 128, 255 }, img.Pixels);
    }
}
