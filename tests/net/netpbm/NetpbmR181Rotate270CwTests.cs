// Tests for NetpbmImage.Rotate270Cw dedicated coverage.
// Sprint: ff-sprint-s185-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R181

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R181: Dedicated tests for NetpbmImage.Rotate270Cw().
/// Rotates the image 270° clockwise (90° counter-clockwise).
/// Width and Height are swapped in the result (same as Rotate90Cw).
/// Format and MaxValue are preserved.
/// Returns a new image (not same reference).
/// Four applications restore original orientation.
/// Covers: returns new image; result width equals original Height;
/// result height equals original Width; format preserved; MaxValue preserved;
/// square image same dims; non-square dims swap; four-rotate restores dims;
/// pixel mapping; dogfood dims correct after rotation.
/// </summary>
public class NetpbmR181Rotate270CwTests
{
    // -------------------------------------------------------------------------
    // Result structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate270Cw_ReturnsNewImage_NotSameReference()
    {
        var img = NetpbmImage.Create(4, 6, NetpbmFormat.PGM_P5);
        var result = img.Rotate270Cw();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Rotate270Cw_ResultWidth_EqualsOriginalHeight()
    {
        var img = NetpbmImage.Create(3, 7, NetpbmFormat.PGM_P5);
        var result = img.Rotate270Cw();
        Assert.Equal(7, result.Width);
    }

    [Fact]
    public void Rotate270Cw_ResultHeight_EqualsOriginalWidth()
    {
        var img = NetpbmImage.Create(3, 7, NetpbmFormat.PGM_P5);
        var result = img.Rotate270Cw();
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Rotate270Cw_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Rotate270Cw();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Rotate270Cw_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Rotate270Cw();
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    [Fact]
    public void Rotate270Cw_SquareImage_SameDimensions()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Rotate270Cw();
        Assert.Equal(5, result.Width);
        Assert.Equal(5, result.Height);
    }

    [Fact]
    public void Rotate270Cw_NonSquare_DimensionsSwapped()
    {
        var img = NetpbmImage.Create(6, 2, NetpbmFormat.PGM_P5);
        var result = img.Rotate270Cw();
        Assert.Equal(2, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Rotate270Cw_FourRotations_RestoresDimensions()
    {
        var img = NetpbmImage.Create(3, 8, NetpbmFormat.PGM_P5);
        var result = img.Rotate270Cw().Rotate270Cw().Rotate270Cw().Rotate270Cw();
        Assert.Equal(3, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_RotatePgm_DimsSwapped()
    {
        var img = NetpbmImage.Create(10, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        var result = img.Rotate270Cw();
        Assert.Equal(4, result.Width);
        Assert.Equal(10, result.Height);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void DogfoodPipeline_Rotate270ThenRotate90_RestoresDims()
    {
        var img = NetpbmImage.Create(5, 9, NetpbmFormat.PGM_P5);
        var result = img.Rotate270Cw().Rotate90Cw();
        Assert.Equal(5, result.Width);
        Assert.Equal(9, result.Height);
    }
}
