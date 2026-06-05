using Xunit;
using System;
using System.IO;
using FormatFactory.Netpbm;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR113TileTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/pgm"));

    private NetpbmImage CreateTestImage(int w, int h, NetpbmFormat fmt = NetpbmFormat.PGM_P2)
    {
        var img = new NetpbmImage
        {
            Format = fmt,
            Width = w,
            Height = h,
            MaxValue = 255,
            Pixels = new byte[w * h]
        };
        for (int i = 0; i < img.Pixels.Length; i++)
            img.Pixels[i] = (byte)(i % 256);
        return img;
    }

    [Fact]
    public void Tile_1x1_ReturnsSameSize()
    {
        var img = CreateTestImage(4, 4);
        var tiled = img.Tile(1, 1);
        Assert.Equal(4, tiled.Width);
        Assert.Equal(4, tiled.Height);
    }

    [Fact]
    public void Tile_2x2_DoublesSize()
    {
        var img = CreateTestImage(3, 3);
        var tiled = img.Tile(2, 2);
        Assert.Equal(6, tiled.Width);
        Assert.Equal(6, tiled.Height);
    }

    [Fact]
    public void Tile_3x1_TriplesWidth()
    {
        var img = CreateTestImage(2, 2);
        var tiled = img.Tile(3, 1);
        Assert.Equal(6, tiled.Width);
        Assert.Equal(2, tiled.Height);
    }

    [Fact]
    public void Tile_PixelsCopied_Correctly()
    {
        var img = CreateTestImage(2, 2);
        img.Pixels[0] = 10;
        img.Pixels[1] = 20;
        img.Pixels[2] = 30;
        img.Pixels[3] = 40;
        var tiled = img.Tile(2, 1);
        // First tile
        Assert.Equal(10, tiled.Pixels[0]);
        Assert.Equal(20, tiled.Pixels[1]);
        // Second tile (same row, offset by width)
        Assert.Equal(10, tiled.Pixels[2]);
        Assert.Equal(20, tiled.Pixels[3]);
    }

    [Fact]
    public void Tile_PreservesFormat()
    {
        var img = CreateTestImage(2, 2, NetpbmFormat.PGM_P2);
        var tiled = img.Tile(2, 2);
        Assert.Equal(NetpbmFormat.PGM_P2, tiled.Format);
    }

    [Fact]
    public void Tile_ZeroTilesX_Throws()
    {
        var img = CreateTestImage(2, 2);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Tile(0, 1));
    }

    [Fact]
    public void Tile_ZeroTilesY_Throws()
    {
        var img = CreateTestImage(2, 2);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Tile(1, 0));
    }

    [Fact]
    public void Tile_SaveAndReload_Roundtrip()
    {
        var img = CreateTestImage(4, 4);
        var tiled = img.Tile(2, 2);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            tiled.SaveToFile(tmp);
            var reloaded = NetpbmParser.Parse(tmp);
            Assert.Equal(8, reloaded.Width);
            Assert.Equal(8, reloaded.Height);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
