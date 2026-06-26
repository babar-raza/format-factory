// Tests for NetpbmImage.CopyRegion.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R146

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R146: Tests for NetpbmImage.CopyRegion.
/// CopyRegion(source, srcTop, srcLeft, regionHeight, regionWidth, destTop, destLeft)
/// copies a rectangular region from source into this image. Formats must match.
/// Clamps copy area to available source/destination bounds — never throws for out-of-bounds overlap.
/// Throws ArgumentNullException for null source; ArgumentException if formats differ;
/// ArgumentOutOfRangeException for negative coords or non-positive dimensions.
/// Covers: null source throws; format mismatch throws; negative srcTop throws;
/// zero regionHeight throws; pixel values copied correctly;
/// region does not affect pixels outside the destination area;
/// copy at offset (0,0); copy at non-zero destination offset;
/// clamping when region exceeds bounds completes without exception;
/// dogfood Create->FillRegion->CopyRegion->GetPixel pipeline.
/// </summary>
public class NetpbmR146CopyRegionTests
{
    private static NetpbmImage MakeGray(int w, int h, byte fill)
    {
        var px = new byte[w * h];
        for (int i = 0; i < px.Length; i++) px[i] = fill;
        return new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = w, Height = h, MaxValue = 255, Pixels = px,
        };
    }

    // -------------------------------------------------------------------------
    // Error cases
    // -------------------------------------------------------------------------

    [Fact]
    public void CopyRegion_NullSource_Throws()
    {
        var dest = MakeGray(4, 4, 0);
        Assert.Throws<ArgumentNullException>(() =>
            dest.CopyRegion(null!, 0, 0, 2, 2, 0, 0));
    }

    [Fact]
    public void CopyRegion_FormatMismatch_Throws()
    {
        var dest = MakeGray(4, 4, 0);
        var pbm = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 2, Height = 2, MaxValue = 1,
            Pixels = new byte[] { 0, 1, 1, 0 },
        };
        Assert.ThrowsAny<Exception>(() => dest.CopyRegion(pbm, 0, 0, 2, 2, 0, 0));
    }

    [Fact]
    public void CopyRegion_NegativeSrcTop_Throws()
    {
        var dest = MakeGray(4, 4, 0);
        var src = MakeGray(4, 4, 200);
        Assert.ThrowsAny<Exception>(() => dest.CopyRegion(src, -1, 0, 2, 2, 0, 0));
    }

    [Fact]
    public void CopyRegion_ZeroRegionHeight_Throws()
    {
        var dest = MakeGray(4, 4, 0);
        var src = MakeGray(4, 4, 200);
        Assert.ThrowsAny<Exception>(() => dest.CopyRegion(src, 0, 0, 0, 2, 0, 0));
    }

    // -------------------------------------------------------------------------
    // Pixel correctness
    // -------------------------------------------------------------------------

    [Fact]
    public void CopyRegion_CopiesPixelValues()
    {
        var src = MakeGray(4, 4, 200);
        var dest = MakeGray(4, 4, 0);
        dest.CopyRegion(src, 0, 0, 2, 2, 0, 0);
        Assert.Equal(200, dest.GetPixel(0, 0));
        Assert.Equal(200, dest.GetPixel(1, 1));
    }

    [Fact]
    public void CopyRegion_OnlyCopiesSpecifiedRegion()
    {
        var src = MakeGray(4, 4, 200);
        var dest = MakeGray(4, 4, 0);
        // Copy only top-left 2x2 from src to dest at (0,0)
        dest.CopyRegion(src, 0, 0, 2, 2, 0, 0);
        // Pixel outside region should still be 0
        Assert.Equal(0, dest.GetPixel(2, 2));
        Assert.Equal(0, dest.GetPixel(3, 3));
    }

    [Fact]
    public void CopyRegion_AtNonZeroOffset_CopiesCorrectly()
    {
        var src = MakeGray(4, 4, 128);
        var dest = MakeGray(4, 4, 0);
        // Copy 2x2 from src at (0,0) to dest at (2,2)
        dest.CopyRegion(src, 0, 0, 2, 2, 2, 2);
        Assert.Equal(128, dest.GetPixel(2, 2));
        Assert.Equal(128, dest.GetPixel(3, 3));
        // Top-left should still be 0
        Assert.Equal(0, dest.GetPixel(0, 0));
    }

    [Fact]
    public void CopyRegion_ExceedingBounds_DoesNotThrow()
    {
        var src = MakeGray(4, 4, 100);
        var dest = MakeGray(4, 4, 0);
        // Region extends beyond both source and dest bounds — should clamp silently
        var ex = Record.Exception(() => dest.CopyRegion(src, 0, 0, 100, 100, 0, 0));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood: pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateFillRegionCopyRegion_Pipeline()
    {
        // Create a 6x6 canvas filled with 0
        var canvas = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5, fill: 0);

        // Fill a 3x3 stamp with 255
        var stamp = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, fill: 255);

        // Copy stamp into canvas at (1,1)
        canvas.CopyRegion(stamp, 0, 0, 3, 3, 1, 1);

        // Verify copied pixels
        Assert.Equal(255, canvas.GetPixel(1, 1));
        Assert.Equal(255, canvas.GetPixel(3, 3));

        // Verify unmodified corner
        Assert.Equal(0, canvas.GetPixel(0, 0));
        Assert.Equal(0, canvas.GetPixel(5, 5));
    }
}
