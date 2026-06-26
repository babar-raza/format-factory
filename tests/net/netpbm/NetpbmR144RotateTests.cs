// Tests for NetpbmImage.Rotate90Cw, Rotate180, Rotate270Cw.
// Sprint: ff-sprint-s147-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R144

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R144: Tests for NetpbmImage rotation transforms: Rotate90Cw, Rotate180, Rotate270Cw.
/// Rotate90Cw: width/height swap; top-left corner goes to top-right.
/// Rotate180: dimensions unchanged; top-left goes to bottom-right.
/// Rotate270Cw: width/height swap (same as Rotate90Cw dims but different content).
/// Covers: Rotate90Cw swaps dimensions; Rotate180 preserves dimensions;
/// Rotate270Cw swaps dimensions; Rotate90Cw top-left pixel correct;
/// Rotate180 top-left pixel goes to bottom-right; original unchanged after rotation;
/// Rotate90Cw format preserved; Rotate180 format preserved;
/// dogfood Rotate90Cw x4 returns original dimensions;
/// dogfood Rotate90Cw x2 equals Rotate180 dimensions.
/// </summary>
public class NetpbmR144RotateTests
{
    private static NetpbmImage MakePgm(int w, int h)
    {
        var img = NetpbmImage.Create(w, h, NetpbmFormat.PGM_P5);
        // Fill with row*10+col values so we can track pixel positions
        for (int r = 0; r < h; r++)
            for (int c = 0; c < w; c++)
                img.SetPixel(r, c, (byte)((r * 10 + c) % 256));
        return img;
    }

    // -------------------------------------------------------------------------
    // Rotate90Cw tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate90Cw_SwapsDimensions()
    {
        var img = NetpbmImage.Create(4, 6, NetpbmFormat.PGM_P5); // 4 wide, 6 tall
        var rotated = img.Rotate90Cw();
        Assert.Equal(6, rotated.Width);  // was height
        Assert.Equal(4, rotated.Height); // was width
    }

    [Fact]
    public void Rotate90Cw_PreservesFormat()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var rotated = img.Rotate90Cw();
        Assert.Equal(NetpbmFormat.PGM_P5, rotated.Format);
    }

    [Fact]
    public void Rotate90Cw_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 99);
        _ = img.Rotate90Cw();
        Assert.Equal(99, img.GetPixel(0, 0)); // original not mutated
        Assert.Equal(3, img.Width);
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void Rotate90Cw_TopLeftPixelMovesToTopRight()
    {
        // In a Rotate90Cw: pixel at (row=0, col=0) maps to (row=0, col=Height-1) in rotated image.
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5); // 3 wide, 4 tall
        img.SetPixel(0, 0, 77); // top-left
        var rotated = img.Rotate90Cw(); // now 4 wide, 3 tall
        // After 90 CW: top-left (r=0,c=0) goes to (row=0, col=Height-1=3) in rotated
        Assert.Equal(77, rotated.GetPixel(0, rotated.Width - 1));
    }

    // -------------------------------------------------------------------------
    // Rotate180 tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate180_PreservesDimensions()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var rotated = img.Rotate180();
        Assert.Equal(5, rotated.Width);
        Assert.Equal(3, rotated.Height);
    }

    [Fact]
    public void Rotate180_PreservesFormat()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var rotated = img.Rotate180();
        Assert.Equal(NetpbmFormat.PGM_P5, rotated.Format);
    }

    [Fact]
    public void Rotate180_TopLeftGoesToBottomRight()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 42); // top-left
        var rotated = img.Rotate180();
        // After 180: top-left (0,0) maps to (Height-1, Width-1) = (2,2)
        Assert.Equal(42, rotated.GetPixel(rotated.Height - 1, rotated.Width - 1));
    }

    // -------------------------------------------------------------------------
    // Rotate270Cw tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate270Cw_SwapsDimensions()
    {
        var img = NetpbmImage.Create(4, 6, NetpbmFormat.PGM_P5); // 4 wide, 6 tall
        var rotated = img.Rotate270Cw();
        Assert.Equal(6, rotated.Width);  // was height
        Assert.Equal(4, rotated.Height); // was width
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Rotate90CwFourTimes_RestoresOriginalDimensions()
    {
        var img = NetpbmImage.Create(4, 6, NetpbmFormat.PGM_P5);
        var r1 = img.Rotate90Cw();
        var r2 = r1.Rotate90Cw();
        var r3 = r2.Rotate90Cw();
        var r4 = r3.Rotate90Cw();
        Assert.Equal(img.Width, r4.Width);
        Assert.Equal(img.Height, r4.Height);
    }

    [Fact]
    public void DogfoodPipeline_Rotate90CwTwice_SameDimensionsAsRotate180()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var twice90 = img.Rotate90Cw().Rotate90Cw();
        var once180 = img.Rotate180();
        Assert.Equal(once180.Width, twice90.Width);
        Assert.Equal(once180.Height, twice90.Height);
    }
}
