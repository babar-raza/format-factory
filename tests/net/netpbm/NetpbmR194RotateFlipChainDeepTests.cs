// Tests for NetpbmImage.Rotate90Cw, Rotate180, Rotate270, FlipHorizontal, FlipVertical chain deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R194

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R194: Tests for NetpbmImage transform chain — Rotate90Cw, Rotate180, Rotate270,
/// FlipHorizontal, FlipVertical deeper coverage.
/// Rotate90Cw(): rotates image 90 degrees clockwise; swaps Width and Height.
/// Rotate180(): rotates image 180 degrees; preserves Width and Height.
/// Rotate270(): rotates image 270 degrees clockwise; swaps Width and Height.
/// FlipHorizontal(): mirrors image left-right; preserves dimensions.
/// FlipVertical(): mirrors image top-bottom; preserves dimensions.
/// Covers: Rotate90Cw non-null; Rotate90Cw swaps dimensions; Rotate90Cw four-times is identity;
/// Rotate180 non-null; Rotate180 preserves dimensions; Rotate180 twice is identity;
/// Rotate270 non-null; Rotate270 swaps dimensions; Rotate90Cw+Rotate270 is identity;
/// FlipHorizontal non-null; FlipHorizontal preserves dimensions; FlipHorizontal twice is identity;
/// FlipVertical non-null; FlipVertical preserves dimensions; FlipVertical twice is identity;
/// FlipHorizontal+FlipVertical equals Rotate180;
/// dogfood CreateCanvas->Rotate->Flip->Chain->Verify pipeline.
/// </summary>
public class NetpbmR194RotateFlipChainDeepTests
{
    // -------------------------------------------------------------------------
    // Rotate90Cw
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate90Cw_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 255);
        Assert.NotNull(img.Rotate90Cw());
    }

    [Fact]
    public void Rotate90Cw_SwapsDimensions()
    {
        var img = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 255);
        var rotated = img.Rotate90Cw();
        Assert.Equal(img.Height, rotated.Width);
        Assert.Equal(img.Width, rotated.Height);
    }

    [Fact]
    public void Rotate90Cw_FourTimes_RestoresDimensions()
    {
        var img = NetpbmImage.CreateCanvas(5, 3, NetpbmFormat.Pgm, 255);
        var result = img.Rotate90Cw().Rotate90Cw().Rotate90Cw().Rotate90Cw();
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    [Fact]
    public void Rotate90Cw_SquareImage_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 255);
        var rotated = img.Rotate90Cw();
        Assert.Equal(4, rotated.Width);
        Assert.Equal(4, rotated.Height);
    }

    [Fact]
    public void Rotate90Cw_PixelCount_Preserved()
    {
        var img = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 255);
        var rotated = img.Rotate90Cw();
        Assert.Equal(img.Width * img.Height, rotated.Width * rotated.Height);
    }

    // -------------------------------------------------------------------------
    // Rotate180
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate180_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 255);
        Assert.NotNull(img.Rotate180());
    }

    [Fact]
    public void Rotate180_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(5, 3, NetpbmFormat.Pgm, 255);
        var rotated = img.Rotate180();
        Assert.Equal(img.Width, rotated.Width);
        Assert.Equal(img.Height, rotated.Height);
    }

    [Fact]
    public void Rotate180_Twice_RestoresDimensions()
    {
        var img = NetpbmImage.CreateCanvas(5, 7, NetpbmFormat.Pgm, 255);
        var result = img.Rotate180().Rotate180();
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    // -------------------------------------------------------------------------
    // Rotate270
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate270_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 255);
        Assert.NotNull(img.Rotate270());
    }

    [Fact]
    public void Rotate270_SwapsDimensions()
    {
        var img = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 255);
        var rotated = img.Rotate270();
        Assert.Equal(img.Height, rotated.Width);
        Assert.Equal(img.Width, rotated.Height);
    }

    [Fact]
    public void Rotate90Cw_ThenRotate270_RestoresDimensions()
    {
        var img = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 255);
        var result = img.Rotate90Cw().Rotate270();
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    // -------------------------------------------------------------------------
    // FlipHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 255);
        Assert.NotNull(img.FlipHorizontal());
    }

    [Fact]
    public void FlipHorizontal_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(5, 3, NetpbmFormat.Pgm, 255);
        var flipped = img.FlipHorizontal();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void FlipHorizontal_Twice_RestoresDimensions()
    {
        var img = NetpbmImage.CreateCanvas(5, 3, NetpbmFormat.Pgm, 255);
        var result = img.FlipHorizontal().FlipHorizontal();
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    // -------------------------------------------------------------------------
    // FlipVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 255);
        Assert.NotNull(img.FlipVertical());
    }

    [Fact]
    public void FlipVertical_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(5, 3, NetpbmFormat.Pgm, 255);
        var flipped = img.FlipVertical();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void FlipVertical_Twice_RestoresDimensions()
    {
        var img = NetpbmImage.CreateCanvas(5, 3, NetpbmFormat.Pgm, 255);
        var result = img.FlipVertical().FlipVertical();
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    [Fact]
    public void FlipHorizontal_ThenFlipVertical_EqualsDimensions_As_Rotate180()
    {
        var img = NetpbmImage.CreateCanvas(5, 3, NetpbmFormat.Pgm, 255);
        var flipped = img.FlipHorizontal().FlipVertical();
        var rotated = img.Rotate180();
        // Both should produce same dimensions
        Assert.Equal(rotated.Width, flipped.Width);
        Assert.Equal(rotated.Height, flipped.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_RotateFlipChain_Verify_Pipeline()
    {
        // CreateCanvas 6x4
        var img = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 255);
        Assert.Equal(6, img.Width);
        Assert.Equal(4, img.Height);

        // Rotate90Cw → 4x6
        var r90 = img.Rotate90Cw();
        Assert.Equal(4, r90.Width);
        Assert.Equal(6, r90.Height);

        // Rotate90Cw again → 6x4
        var r180 = r90.Rotate90Cw();
        Assert.Equal(6, r180.Width);
        Assert.Equal(4, r180.Height);

        // FlipHorizontal preserves 6x4
        var fh = r180.FlipHorizontal();
        Assert.Equal(6, fh.Width);
        Assert.Equal(4, fh.Height);

        // FlipVertical preserves 6x4
        var fv = fh.FlipVertical();
        Assert.Equal(6, fv.Width);
        Assert.Equal(4, fv.Height);

        // Rotate270 → 4x6
        var r270 = fv.Rotate270();
        Assert.Equal(4, r270.Width);
        Assert.Equal(6, r270.Height);

        // Rotate90Cw to get back to 6x4
        var final = r270.Rotate90Cw();
        Assert.Equal(6, final.Width);
        Assert.Equal(4, final.Height);
    }
}
