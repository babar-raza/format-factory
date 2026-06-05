// R106 Wave 2: Netpbm Overlay tests
// Ledger: R106-GOVERNED-DOTNET-NETPBM-OVERLAY-001

using System;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR106OverlayTests
{
    private static NetpbmImage MakeGray(int w, int h, byte val)
    {
        var px = new byte[w * h];
        for (int i = 0; i < px.Length; i++) px[i] = val;
        return new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = w, Height = h, MaxValue = 255, Pixels = px };
    }

    private static NetpbmImage MakeRgb(int w, int h, byte r, byte g, byte b)
    {
        int sz = w * h;
        var red = new byte[sz]; var green = new byte[sz]; var blue = new byte[sz];
        for (int i = 0; i < sz; i++) { red[i] = r; green[i] = g; blue[i] = b; }
        return new NetpbmImage { Format = NetpbmFormat.PPM_P3, Width = w, Height = h, MaxValue = 255, RedChannel = red, GreenChannel = green, BlueChannel = blue };
    }

    [Fact]
    public void Overlay_SameSize_ReplacesAll()
    {
        var bg = MakeGray(4, 4, 0);
        var fg = MakeGray(4, 4, 255);
        var result = bg.Overlay(fg, 0, 0);
        for (int i = 0; i < result.Pixels.Length; i++)
            Assert.Equal(255, result.Pixels[i]);
    }

    [Fact]
    public void Overlay_PartialOverlap()
    {
        var bg = MakeGray(4, 4, 0);
        var fg = MakeGray(2, 2, 100);
        var result = bg.Overlay(fg, 1, 1);
        Assert.Equal(0, result.Pixels[0]); // (0,0) unchanged
        Assert.Equal(100, result.Pixels[1 * 4 + 1]); // (1,1) overlaid
        Assert.Equal(100, result.Pixels[2 * 4 + 2]); // (2,2) overlaid
        Assert.Equal(0, result.Pixels[3 * 4 + 3]); // (3,3) unchanged
    }

    [Fact]
    public void Overlay_NoOverlap_UnchangedCopy()
    {
        var bg = MakeGray(2, 2, 50);
        var fg = MakeGray(1, 1, 200);
        var result = bg.Overlay(fg, 10, 10); // way beyond bounds
        for (int i = 0; i < result.Pixels.Length; i++)
            Assert.Equal(50, result.Pixels[i]);
    }

    [Fact]
    public void Overlay_PPM()
    {
        var bg = MakeRgb(3, 3, 0, 0, 0);
        var fg = MakeRgb(1, 1, 255, 128, 64);
        var result = bg.Overlay(fg, 1, 1);
        Assert.Equal(255, result.RedChannel![1 * 3 + 1]);
        Assert.Equal(128, result.GreenChannel![1 * 3 + 1]);
        Assert.Equal(64, result.BlueChannel![1 * 3 + 1]);
        Assert.Equal(0, result.RedChannel[0]); // unchanged
    }

    [Fact]
    public void Overlay_FormatMismatch_Throws()
    {
        var bg = MakeGray(2, 2, 0);
        var fg = MakeRgb(1, 1, 255, 0, 0);
        Assert.Throws<InvalidOperationException>(() => bg.Overlay(fg, 0, 0));
    }

    [Fact]
    public void Overlay_NegativeOffset_Throws()
    {
        var bg = MakeGray(2, 2, 0);
        var fg = MakeGray(1, 1, 255);
        Assert.Throws<ArgumentOutOfRangeException>(() => bg.Overlay(fg, -1, 0));
    }

    [Fact]
    public void Overlay_DoesNotMutateOriginal()
    {
        var bg = MakeGray(2, 2, 0);
        var fg = MakeGray(2, 2, 255);
        var result = bg.Overlay(fg, 0, 0);
        Assert.Equal(0, bg.Pixels[0]); // original unchanged
        Assert.Equal(255, result.Pixels[0]); // result changed
    }

    [Fact]
    public void Overlay_PartiallyOutOfBounds_ClipsToImage()
    {
        var bg = MakeGray(3, 3, 0);
        var fg = MakeGray(3, 3, 100);
        var result = bg.Overlay(fg, 2, 2); // Only (2,2) overlaps
        Assert.Equal(100, result.Pixels[2 * 3 + 2]);
        Assert.Equal(0, result.Pixels[0]);
    }

    [Fact]
    public void Overlay_ZeroSizeOverlay_NoCrash()
    {
        var bg = MakeGray(2, 2, 50);
        var fg = MakeGray(2, 2, 200);
        // Place far away, no overlap
        var result = bg.Overlay(fg, 100, 100);
        Assert.Equal(50, result.Pixels[0]);
    }

    [Fact]
    public void Overlay_FullImage_AtOrigin()
    {
        var bg = MakeGray(3, 3, 10);
        var fg = MakeGray(3, 3, 99);
        var result = bg.Overlay(fg, 0, 0);
        for (int i = 0; i < 9; i++)
            Assert.Equal(99, result.Pixels[i]);
    }
}
