// Tests for NetpbmImage.FlipVertical dedicated coverage.
// Sprint: ff-sprint-s168-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R164

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R164: Dedicated tests for NetpbmImage.FlipVertical().
/// FlipVertical is an IN-PLACE void mutation: it swaps rows top-to-bottom
/// in the same image instance. Width, Height, and Format are unchanged.
/// Top pixel row moves to bottom; bottom pixel row moves to top.
/// Middle row unchanged for odd-height images. Double-flip restores.
/// Covers: in-place void (no return); width unchanged; height unchanged;
/// format unchanged; top pixel moves to bottom; bottom pixel moves to top;
/// center row unchanged (odd height); double-flip restores original;
/// dogfood Create->SetPixel->Flip->GetPixel; multi-column consistency.
/// </summary>
public class NetpbmR164FlipVerticalTests
{
    // -------------------------------------------------------------------------
    // Structural / type tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_ReturnsVoid_InPlace()
    {
        // FlipVertical has void return — verify it compiles and runs without error
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        img.FlipVertical(); // must not throw
    }

    [Fact]
    public void FlipVertical_Width_Unchanged()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PGM_P5);
        img.FlipVertical();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void FlipVertical_Height_Unchanged()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PGM_P5);
        img.FlipVertical();
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void FlipVertical_Format_Unchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.FlipVertical();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    // -------------------------------------------------------------------------
    // Pixel mapping tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_TopPixel_MovesToBottom()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5); // 3w 4h
        img.SetPixel(0, 1, 77); // top row (row=0), col=1
        img.FlipVertical();
        // top row maps to row H-1 = 3
        Assert.Equal(77, img.GetPixel(3, 1));
    }

    [Fact]
    public void FlipVertical_BottomPixel_MovesToTop()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5); // 4h
        img.SetPixel(3, 2, 88); // bottom row (row=3), col=2
        img.FlipVertical();
        // bottom row maps to row 0
        Assert.Equal(88, img.GetPixel(0, 2));
    }

    [Fact]
    public void FlipVertical_CenterRow_Unchanged_OddHeight()
    {
        var img = NetpbmImage.Create(4, 5, NetpbmFormat.PGM_P5); // 5h — center at row 2
        img.SetPixel(2, 1, 55); // center row, col=1
        img.FlipVertical();
        Assert.Equal(55, img.GetPixel(2, 1));
    }

    [Fact]
    public void FlipVertical_DoubleFlip_RestoresOriginal()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 10);
        img.SetPixel(1, 1, 20);
        img.SetPixel(2, 2, 30);
        img.FlipVertical();
        img.FlipVertical();
        Assert.Equal(10, img.GetPixel(0, 0));
        Assert.Equal(20, img.GetPixel(1, 1));
        Assert.Equal(30, img.GetPixel(2, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateSetPixelFlipGetPixel()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5); // 4w 3h
        img.SetPixel(0, 2, 99); // row=0, col=2 (top row)
        img.FlipVertical();
        // top row (0) maps to bottom row (H-1=2)
        Assert.Equal(99, img.GetPixel(2, 2));
    }

    [Fact]
    public void FlipVertical_MultiColumn_RowSwapConsistent()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5); // 2h
        // Set entire top row
        img.SetPixel(0, 0, 10);
        img.SetPixel(0, 1, 20);
        img.SetPixel(0, 2, 30);
        img.SetPixel(0, 3, 40);
        img.FlipVertical();
        // All must appear in bottom row (row 1 -> row H-1=1)
        Assert.Equal(10, img.GetPixel(1, 0));
        Assert.Equal(20, img.GetPixel(1, 1));
        Assert.Equal(30, img.GetPixel(1, 2));
        Assert.Equal(40, img.GetPixel(1, 3));
    }
}
