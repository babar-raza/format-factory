// Tests for NetpbmImage.GetIsBinary dedicated coverage.
// Sprint: ff-sprint-s468-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R486

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R486: Dedicated tests for NetpbmImage.GetIsBinary().
/// PBM returns true (binary format).
/// PGM returns false (multi-level gray).
/// PPM returns false (color).
/// Width unchanged after GetIsBinary.
/// Height unchanged after GetIsBinary.
/// Format unchanged after GetIsBinary.
/// MaxValue unchanged after GetIsBinary.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PBM is binary.
/// Dogfood: 4x4 PGM is not binary.
/// Dogfood: 4x4 PPM is not binary.
/// </summary>
public class NetpbmR486GetIsBinaryDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsBinary_PBM_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.True(img.GetIsBinary());
    }

    [Fact]
    public void GetIsBinary_PGM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsBinary());
    }

    [Fact]
    public void GetIsBinary_PPM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsBinary());
    }

    [Fact]
    public void GetIsBinary_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        int before = img.Width;
        _ = img.GetIsBinary();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsBinary_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        int before = img.Height;
        _ = img.GetIsBinary();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsBinary_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        string before = img.Format;
        _ = img.GetIsBinary();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsBinary_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetIsBinary();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsBinary_Idempotent()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        bool first = img.GetIsBinary();
        bool second = img.GetIsBinary();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPBM_IsBinary()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.True(img.GetIsBinary());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_IsNotBinary()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsBinary());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_IsNotBinary()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsBinary());
    }
}
