// R93 Train M: Netpbm .NET CopyRegion Tests
// Governed skill: /add-dotnet-api
// Ledger: R93-GOVERNED-DOTNET-NETPBM-COPYREGION-001
// Sprint: FORMAT-FACTORY-R93-CONTEXT-PACK-SUPERVISOR-MCP-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

using System;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR93CopyRegionTests
{
    private static NetpbmImage MakePgm(int width, int height, byte fill = 0)
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = width,
            Height = height,
            MaxValue = 255,
            Pixels = new byte[width * height]
        };
        if (fill != 0)
            Array.Fill(img.Pixels, fill);
        return img;
    }

    private static NetpbmImage MakePpm(int width, int height, byte r = 0, byte g = 0, byte b = 0)
    {
        int len = width * height;
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = width,
            Height = height,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel   = new byte[len],
            GreenChannel = new byte[len],
            BlueChannel  = new byte[len]
        };
        if (r != 0) Array.Fill(img.RedChannel,   r);
        if (g != 0) Array.Fill(img.GreenChannel, g);
        if (b != 0) Array.Fill(img.BlueChannel,  b);
        return img;
    }

    [Fact]
    public void CopyRegion_PGM_CopiesPixelsCorrectly()
    {
        var src = MakePgm(4, 4, fill: 200);
        var dst = MakePgm(4, 4, fill: 0);

        dst.CopyRegion(src, srcTop: 0, srcLeft: 0, regionHeight: 2, regionWidth: 2, destTop: 1, destLeft: 1);

        Assert.Equal(200, dst.GetPixel(1, 1));
        Assert.Equal(200, dst.GetPixel(2, 2));
        Assert.Equal(0,   dst.GetPixel(0, 0));
        Assert.Equal(0,   dst.GetPixel(3, 3));
    }

    [Fact]
    public void CopyRegion_PPM_CopiesChannelsCorrectly()
    {
        var src = MakePpm(4, 4, r: 255, g: 128, b: 64);
        var dst = MakePpm(4, 4, r: 0,   g: 0,   b: 0);

        dst.CopyRegion(src, srcTop: 0, srcLeft: 0, regionHeight: 2, regionWidth: 2, destTop: 0, destLeft: 0);

        var (rr, rg, rb) = dst.GetPixelColor(0, 0);
        Assert.Equal(255, rr);
        Assert.Equal(128, rg);
        Assert.Equal(64,  rb);
    }

    [Fact]
    public void CopyRegion_NullSource_ThrowsArgumentNullException()
    {
        var dst = MakePgm(4, 4);
        Assert.Throws<ArgumentNullException>(() =>
            dst.CopyRegion(null!, 0, 0, 2, 2, 0, 0));
    }

    [Fact]
    public void CopyRegion_FormatMismatch_ThrowsArgumentException()
    {
        var src = MakePgm(4, 4);
        var dst = MakePpm(4, 4);
        Assert.Throws<ArgumentException>(() =>
            dst.CopyRegion(src, 0, 0, 2, 2, 0, 0));
    }

    [Fact]
    public void CopyRegion_NegativeCoordinates_ThrowsArgumentOutOfRangeException()
    {
        var src = MakePgm(4, 4);
        var dst = MakePgm(4, 4);
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            dst.CopyRegion(src, -1, 0, 2, 2, 0, 0));
    }

    [Fact]
    public void CopyRegion_ZeroRegionHeight_ThrowsArgumentOutOfRangeException()
    {
        var src = MakePgm(4, 4);
        var dst = MakePgm(4, 4);
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            dst.CopyRegion(src, 0, 0, 0, 2, 0, 0));
    }

    [Fact]
    public void CopyRegion_ClampsToAvailableBounds()
    {
        // Source is 2x2, destination is 4x4; request larger region — should clamp
        var src = MakePgm(2, 2, fill: 99);
        var dst = MakePgm(4, 4, fill: 0);

        dst.CopyRegion(src, srcTop: 0, srcLeft: 0, regionHeight: 10, regionWidth: 10, destTop: 0, destLeft: 0);

        // Only 2x2 area should be copied
        Assert.Equal(99, dst.GetPixel(0, 0));
        Assert.Equal(99, dst.GetPixel(1, 1));
        // Row/col 2 and beyond untouched
        Assert.Equal(0,  dst.GetPixel(2, 0));
        Assert.Equal(0,  dst.GetPixel(0, 2));
    }

    [Fact]
    public void CopyRegion_DestBeyondBounds_NothingCopied()
    {
        // destTop == dst.Height → nothing to copy
        var src = MakePgm(4, 4, fill: 77);
        var dst = MakePgm(4, 4, fill: 0);

        dst.CopyRegion(src, 0, 0, 2, 2, destTop: 4, destLeft: 0);

        // All pixels should remain 0
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                Assert.Equal(0, dst.GetPixel(r, c));
    }
}
