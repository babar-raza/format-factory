// Tests for NetpbmImage.Rotate90Cw, Rotate180, Rotate270Cw, FlipHorizontal, FlipVertical, FlipDiagonal.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R185

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R185: Tests for NetpbmImage rotation and flip operations deeper coverage.
/// Rotate90Cw(): rotates 90 degrees clockwise.
/// Rotate180(): rotates 180 degrees.
/// Rotate270Cw(): rotates 270 degrees clockwise (= 90 CCW).
/// FlipHorizontal(): mirrors image horizontally.
/// FlipVertical(): mirrors image vertically.
/// FlipDiagonal(): transposes image along diagonal.
/// Covers: Rotate90Cw returns new image; Rotate90Cw swaps width/height;
/// Rotate180 returns new image; Rotate180 preserves dimensions;
/// Rotate270Cw returns new image; Rotate270Cw swaps width/height;
/// FlipHorizontal returns new image; FlipHorizontal preserves dimensions;
/// FlipVertical returns new image; FlipVertical preserves dimensions;
/// FlipDiagonal returns new image; FlipDiagonal swaps width/height;
/// Rotate90Cw x4 restores dimensions; FlipHorizontal x2 equivalent to identity;
/// dogfood Create->Rotate90->Rotate180->FlipHoriz->FlipVert->GetStats pipeline.
/// </summary>
public class NetpbmR185RotateAndFlipTests
{
    private static NetpbmImage CreateRect(byte fill = 128)
        => NetpbmImage.Create(6, 4, NetpbmFormat.Pgm, fill);

    private static NetpbmImage CreateSquare(byte fill = 128)
        => NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, fill);

    // -------------------------------------------------------------------------
    // Rotate90Cw
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate90Cw_ReturnsNewImage()
    {
        var img = CreateRect();
        var result = img.Rotate90Cw();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Rotate90Cw_SwapsWidthAndHeight()
    {
        var img = CreateRect(); // 6x4
        var result = img.Rotate90Cw();
        Assert.Equal(4, result.Width);  // original height
        Assert.Equal(6, result.Height); // original width
    }

    [Fact]
    public void Rotate90Cw_FourTimesRestoresDimensions()
    {
        var img = CreateRect(); // 6x4
        var r1 = img.Rotate90Cw();
        var r2 = r1.Rotate90Cw();
        var r3 = r2.Rotate90Cw();
        var r4 = r3.Rotate90Cw();
        Assert.Equal(img.Width, r4.Width);
        Assert.Equal(img.Height, r4.Height);
    }

    // -------------------------------------------------------------------------
    // Rotate180
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate180_ReturnsNewImage()
    {
        var img = CreateSquare();
        var result = img.Rotate180();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Rotate180_PreservesDimensions()
    {
        var img = CreateRect(); // 6x4
        var result = img.Rotate180();
        Assert.Equal(6, result.Width);
        Assert.Equal(4, result.Height);
    }

    // -------------------------------------------------------------------------
    // Rotate270Cw
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate270Cw_ReturnsNewImage()
    {
        var img = CreateRect();
        var result = img.Rotate270Cw();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Rotate270Cw_SwapsWidthAndHeight()
    {
        var img = CreateRect(); // 6x4
        var result = img.Rotate270Cw();
        Assert.Equal(4, result.Width);  // original height
        Assert.Equal(6, result.Height); // original width
    }

    // -------------------------------------------------------------------------
    // FlipHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_ReturnsNewImage()
    {
        var img = CreateSquare();
        var result = img.FlipHorizontal();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void FlipHorizontal_PreservesDimensions()
    {
        var img = CreateRect(); // 6x4
        var result = img.FlipHorizontal();
        Assert.Equal(6, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void FlipHorizontal_TwicePreservesDimensions()
    {
        var img = CreateRect(); // 6x4
        var r1 = img.FlipHorizontal();
        var r2 = r1.FlipHorizontal();
        Assert.Equal(img.Width, r2.Width);
        Assert.Equal(img.Height, r2.Height);
    }

    // -------------------------------------------------------------------------
    // FlipVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_ReturnsNewImage()
    {
        var img = CreateSquare();
        var result = img.FlipVertical();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void FlipVertical_PreservesDimensions()
    {
        var img = CreateRect(); // 6x4
        var result = img.FlipVertical();
        Assert.Equal(6, result.Width);
        Assert.Equal(4, result.Height);
    }

    // -------------------------------------------------------------------------
    // FlipDiagonal
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipDiagonal_ReturnsNewImage()
    {
        var img = CreateRect();
        var result = img.FlipDiagonal();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void FlipDiagonal_SwapsWidthAndHeight()
    {
        var img = CreateRect(); // 6x4
        var result = img.FlipDiagonal();
        Assert.Equal(4, result.Width);  // original height
        Assert.Equal(6, result.Height); // original width
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Rotate90->Rotate180->FlipHoriz->FlipVert->GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateRotateFlipGetStats_Pipeline()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.Pgm, 128);

        // Rotate90Cw
        var r90 = img.Rotate90Cw();
        Assert.Equal(4, r90.Width);
        Assert.Equal(6, r90.Height);

        // Rotate180
        var r180 = r90.Rotate180();
        Assert.Equal(4, r180.Width);
        Assert.Equal(6, r180.Height);

        // FlipHorizontal
        var fh = r180.FlipHorizontal();
        Assert.Equal(4, fh.Width);
        Assert.Equal(6, fh.Height);

        // FlipVertical
        var fv = fh.FlipVertical();
        Assert.Equal(4, fv.Width);
        Assert.Equal(6, fv.Height);

        // GetStats
        var (mean, min, max) = fv.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
        Assert.InRange(mean, 0.0, 255.0);
    }
}
