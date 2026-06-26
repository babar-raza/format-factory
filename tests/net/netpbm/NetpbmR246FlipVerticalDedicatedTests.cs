// Tests for NetpbmImage.FlipVertical dedicated coverage.
// Sprint: ff-sprint-s239-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R246

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R246: Dedicated tests for NetpbmImage.FlipVertical().
/// FlipVertical mirrors the image top-bottom IN PLACE (modifies the original, void return).
/// Dimensions are preserved. Pixel at (r, c) swaps with pixel at (H-1-r, c).
/// Covers: width unchanged after flip; height unchanged after flip;
/// format unchanged after flip; MaxValue unchanged after flip;
/// top row pixel moves to bottom row; bottom row pixel moves to top row;
/// center row unchanged (odd height); double flip restores original pixels;
/// dogfood Create->SetPixel->FlipVertical->GetPixel verify; dogfood two-column consistency.
/// </summary>
public class NetpbmR246FlipVerticalDedicatedTests
{
    // -------------------------------------------------------------------------
    // Dimension/format preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.FlipVertical();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void FlipVertical_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.FlipVertical();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void FlipVertical_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.FlipVertical();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void FlipVertical_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 200);
        img.FlipVertical();
        Assert.Equal(200, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Pixel transform tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_TopRowPixel_MovesToBottomRow()
    {
        // 3-wide, 3-tall image
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 77); // col=0, row=0 (top)
        img.FlipVertical();
        // After flip: col=0, row=2 (bottom) should have 77
        Assert.Equal(77, img.GetPixel(0, 2));
    }

    [Fact]
    public void FlipVertical_BottomRowPixel_MovesToTopRow()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 2, 88); // col=1, row=2 (bottom)
        img.FlipVertical();
        // After flip: col=1, row=0 (top) should have 88
        Assert.Equal(88, img.GetPixel(1, 0));
    }

    [Fact]
    public void FlipVertical_CenterRow_Unchanged()
    {
        // 3-tall image: center row = row 1
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 1, 55); // col=0, row=1 (center)
        img.FlipVertical();
        Assert.Equal(55, img.GetPixel(0, 1));
    }

    [Fact]
    public void FlipVertical_DoubleFlip_RestoresOriginal()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 10);
        img.SetPixel(2, 1, 50);
        img.SetPixel(3, 3, 200);
        int p00 = img.GetPixel(0, 0);
        int p21 = img.GetPixel(2, 1);
        int p33 = img.GetPixel(3, 3);
        img.FlipVertical();
        img.FlipVertical();
        Assert.Equal(p00, img.GetPixel(0, 0));
        Assert.Equal(p21, img.GetPixel(2, 1));
        Assert.Equal(p33, img.GetPixel(3, 3));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateSetPixelFlipVerify()
    {
        // 2x3 image: width=2, height=3
        var img = NetpbmImage.Create(2, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 10);  // col=0, row=0 (top)
        img.SetPixel(1, 0, 20);  // col=1, row=0 (top)
        img.SetPixel(0, 2, 30);  // col=0, row=2 (bottom)
        img.SetPixel(1, 2, 40);  // col=1, row=2 (bottom)
        img.FlipVertical();
        // Top row should now have what was the bottom row
        Assert.Equal(30, img.GetPixel(0, 0));
        Assert.Equal(40, img.GetPixel(1, 0));
        // Bottom row should now have what was the top row
        Assert.Equal(10, img.GetPixel(0, 2));
        Assert.Equal(20, img.GetPixel(1, 2));
    }

    [Fact]
    public void DogfoodPipeline_TwoColumnConsistency()
    {
        // Verify both columns are flipped consistently
        var img = NetpbmImage.Create(2, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 11);  // col=0, row=0
        img.SetPixel(1, 0, 22);  // col=1, row=0
        img.SetPixel(0, 3, 33);  // col=0, row=3
        img.SetPixel(1, 3, 44);  // col=1, row=3
        img.FlipVertical();
        // Row 0 (was row 3)
        Assert.Equal(33, img.GetPixel(0, 0));
        Assert.Equal(44, img.GetPixel(1, 0));
        // Row 3 (was row 0)
        Assert.Equal(11, img.GetPixel(0, 3));
        Assert.Equal(22, img.GetPixel(1, 3));
    }
}
