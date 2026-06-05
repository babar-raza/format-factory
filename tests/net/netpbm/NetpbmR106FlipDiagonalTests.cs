// R106 Wave 2: Netpbm FlipDiagonal tests
// Ledger: R106-GOVERNED-DOTNET-NETPBM-FLIPDIAGONAL-001

using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR106FlipDiagonalTests
{
    [Fact]
    public void FlipDiagonal_SwapsDimensions()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2, Width = 3, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 1, 2, 3, 4, 5, 6 }
        };
        var flipped = img.FlipDiagonal();
        Assert.Equal(2, flipped.Width);
        Assert.Equal(3, flipped.Height);
    }

    [Fact]
    public void FlipDiagonal_PixelTranspose_PGM()
    {
        // 2x3 image:
        // 1 2 3
        // 4 5 6
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2, Width = 3, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 1, 2, 3, 4, 5, 6 }
        };
        var f = img.FlipDiagonal();
        // Expected 3x2:
        // 1 4
        // 2 5
        // 3 6
        Assert.Equal(1, f.Pixels[0]);
        Assert.Equal(4, f.Pixels[1]);
        Assert.Equal(2, f.Pixels[2]);
        Assert.Equal(5, f.Pixels[3]);
        Assert.Equal(3, f.Pixels[4]);
        Assert.Equal(6, f.Pixels[5]);
    }

    [Fact]
    public void FlipDiagonal_SquareImage()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2, Width = 2, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 1, 2, 3, 4 }
        };
        var f = img.FlipDiagonal();
        Assert.Equal(2, f.Width);
        Assert.Equal(2, f.Height);
        Assert.Equal(1, f.Pixels[0]);
        Assert.Equal(3, f.Pixels[1]);
        Assert.Equal(2, f.Pixels[2]);
        Assert.Equal(4, f.Pixels[3]);
    }

    [Fact]
    public void FlipDiagonal_PPM()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3, Width = 2, Height = 1, MaxValue = 255,
            Pixels = System.Array.Empty<byte>(),
            RedChannel = new byte[] { 100, 200 },
            GreenChannel = new byte[] { 50, 150 },
            BlueChannel = new byte[] { 10, 20 }
        };
        var f = img.FlipDiagonal();
        Assert.Equal(1, f.Width);
        Assert.Equal(2, f.Height);
        Assert.Equal(100, f.RedChannel![0]);
        Assert.Equal(200, f.RedChannel[1]);
    }

    [Fact]
    public void FlipDiagonal_1x1_NoChange()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2, Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 42 }
        };
        var f = img.FlipDiagonal();
        Assert.Equal(1, f.Width);
        Assert.Equal(1, f.Height);
        Assert.Equal(42, f.Pixels[0]);
    }

    [Fact]
    public void FlipDiagonal_TwiceReturnsOriginal()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2, Width = 3, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 10, 20, 30, 40, 50, 60 }
        };
        var result = img.FlipDiagonal().FlipDiagonal();
        Assert.Equal(3, result.Width);
        Assert.Equal(2, result.Height);
        for (int i = 0; i < img.Pixels.Length; i++)
            Assert.Equal(img.Pixels[i], result.Pixels[i]);
    }

    [Fact]
    public void FlipDiagonal_PBM()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1, Width = 2, Height = 1, MaxValue = 1,
            Pixels = new byte[] { 0, 1 }
        };
        var f = img.FlipDiagonal();
        Assert.Equal(1, f.Width);
        Assert.Equal(2, f.Height);
        Assert.Equal(0, f.Pixels[0]);
        Assert.Equal(1, f.Pixels[1]);
    }

    [Fact]
    public void FlipDiagonal_PreservesFormat()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5, Width = 2, Height = 3, MaxValue = 255,
            Pixels = new byte[6]
        };
        var f = img.FlipDiagonal();
        Assert.Equal(NetpbmFormat.PGM_P5, f.Format);
        Assert.Equal(255, f.MaxValue);
    }
}
