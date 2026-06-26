// Tests for NetpbmImage.FlipHorizontal dedicated coverage.
// Sprint: ff-sprint-s246-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R253

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R253: Dedicated tests for NetpbmImage.FlipHorizontal().
/// FlipHorizontal mirrors the image left-right IN PLACE (modifies the original, void return).
/// Dimensions are preserved. Pixel at (col, row) swaps with pixel at (W-1-col, row).
/// Covers: width unchanged after flip; height unchanged after flip;
/// format unchanged after flip; MaxValue unchanged after flip;
/// left-column pixel moves to right column; right-column pixel moves to left column;
/// center column unchanged (odd width); double flip restores original pixels;
/// dogfood Create->SetPixel->FlipHorizontal->GetPixel verify; dogfood two-row consistency.
/// </summary>
public class NetpbmR253FlipHorizontalDedicatedTests
{
    // -------------------------------------------------------------------------
    // Dimension/format preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.FlipHorizontal();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void FlipHorizontal_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.FlipHorizontal();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void FlipHorizontal_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.FlipHorizontal();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void FlipHorizontal_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 200);
        img.FlipHorizontal();
        Assert.Equal(200, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Pixel transform tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_LeftColumnPixel_MovesToRightColumn()
    {
        // 3-wide, 3-tall image: width=3
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 77); // col=0, row=0 (left edge)
        img.FlipHorizontal();
        // After flip: col=2 (right edge), row=0 should have 77
        Assert.Equal(77, img.GetPixel(2, 0));
    }

    [Fact]
    public void FlipHorizontal_RightColumnPixel_MovesToLeftColumn()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(2, 1, 88); // col=2, row=1 (right edge)
        img.FlipHorizontal();
        // After flip: col=0, row=1 (left edge) should have 88
        Assert.Equal(88, img.GetPixel(0, 1));
    }

    [Fact]
    public void FlipHorizontal_CenterColumn_Unchanged()
    {
        // 3-wide image: center col = col 1
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 0, 55); // col=1, row=0 (center)
        img.FlipHorizontal();
        Assert.Equal(55, img.GetPixel(1, 0));
    }

    [Fact]
    public void FlipHorizontal_DoubleFlip_RestoresOriginal()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 10);
        img.SetPixel(1, 2, 50);
        img.SetPixel(3, 3, 200);
        int p00 = img.GetPixel(0, 0);
        int p12 = img.GetPixel(1, 2);
        int p33 = img.GetPixel(3, 3);
        img.FlipHorizontal();
        img.FlipHorizontal();
        Assert.Equal(p00, img.GetPixel(0, 0));
        Assert.Equal(p12, img.GetPixel(1, 2));
        Assert.Equal(p33, img.GetPixel(3, 3));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateSetPixelFlipVerify()
    {
        // 3x2 image: width=3, height=2
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 10);  // col=0, row=0 (left)
        img.SetPixel(2, 0, 30);  // col=2, row=0 (right)
        img.SetPixel(0, 1, 40);  // col=0, row=1 (left)
        img.SetPixel(2, 1, 60);  // col=2, row=1 (right)
        img.FlipHorizontal();
        // Left column should now have what was the right column
        Assert.Equal(30, img.GetPixel(0, 0));
        Assert.Equal(60, img.GetPixel(0, 1));
        // Right column should now have what was the left column
        Assert.Equal(10, img.GetPixel(2, 0));
        Assert.Equal(40, img.GetPixel(2, 1));
    }

    [Fact]
    public void DogfoodPipeline_TwoRowConsistency()
    {
        // Verify both rows are flipped consistently
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 11);  // col=0, row=0
        img.SetPixel(0, 1, 22);  // col=0, row=1
        img.SetPixel(3, 0, 33);  // col=3, row=0
        img.SetPixel(3, 1, 44);  // col=3, row=1
        img.FlipHorizontal();
        // Col 0 (was col 3)
        Assert.Equal(33, img.GetPixel(0, 0));
        Assert.Equal(44, img.GetPixel(0, 1));
        // Col 3 (was col 0)
        Assert.Equal(11, img.GetPixel(3, 0));
        Assert.Equal(22, img.GetPixel(3, 1));
    }
}
