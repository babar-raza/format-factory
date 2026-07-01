// Tests for NetpbmImage.GetIsSquare dedicated coverage.
// Sprint: ff-sprint-s470-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R488

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R488: Dedicated tests for NetpbmImage.GetIsSquare().
/// Square image (4x4) returns true.
/// Non-square image (4x8) returns false.
/// Width unchanged after GetIsSquare.
/// Height unchanged after GetIsSquare.
/// Format unchanged after GetIsSquare.
/// MaxValue unchanged after GetIsSquare.
/// Idempotent (called twice same result).
/// PBM square returns true.
/// PGM square returns true.
/// Dogfood: 4x4 PGM is square.
/// Dogfood: 4x8 PGM is not square.
/// </summary>
public class NetpbmR488GetIsSquareDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsSquare_SquareImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.True(img.GetIsSquare());
    }

    [Fact]
    public void GetIsSquare_NonSquareImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(4, 8, 255);
        Assert.False(img.GetIsSquare());
    }

    [Fact]
    public void GetIsSquare_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetIsSquare();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsSquare_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetIsSquare();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsSquare_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetIsSquare();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsSquare_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetIsSquare();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsSquare_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        bool first = img.GetIsSquare();
        bool second = img.GetIsSquare();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetIsSquare_PBM_Square_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.True(img.GetIsSquare());
    }

    [Fact]
    public void GetIsSquare_PGM_Square_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePGM(8, 8, 255);
        Assert.True(img.GetIsSquare());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_IsSquare()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.True(img.GetIsSquare());
    }

    [Fact]
    public void DogfoodPipeline_FourByEightPGM_IsNotSquare()
    {
        var img = NetpbmImage.CreatePGM(4, 8, 255);
        Assert.False(img.GetIsSquare());
    }
}
