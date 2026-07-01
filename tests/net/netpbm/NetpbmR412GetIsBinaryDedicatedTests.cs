// Tests for NetpbmImage.GetIsBinary dedicated coverage.
// Sprint: ff-sprint-s394-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R412

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R412: Dedicated tests for NetpbmImage.IsBinary (or GetIsBinary()).
/// PBM returns true (binary/bitmap format).
/// PGM returns false (not binary).
/// PPM returns false (not binary).
/// Width unchanged after IsBinary.
/// Height unchanged after IsBinary.
/// Format unchanged after IsBinary.
/// MaxValue unchanged after IsBinary.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PBM is binary.
/// Dogfood: 4x4 PGM is not binary.
/// </summary>
public class NetpbmR412GetIsBinaryDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void IsBinary_PBM_ReturnsTrue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.IsBinary);
    }

    [Fact]
    public void IsBinary_PGM_ReturnsFalse()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.False(img.IsBinary);
    }

    [Fact]
    public void IsBinary_PPM_ReturnsFalse()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.False(img.IsBinary);
    }

    [Fact]
    public void IsBinary_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PBM);
        int before = img.Width;
        _ = img.IsBinary;
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void IsBinary_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PBM);
        int before = img.Height;
        _ = img.IsBinary;
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void IsBinary_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        NetpbmFormat before = img.Format;
        _ = img.IsBinary;
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void IsBinary_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.IsBinary;
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void IsBinary_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        bool first = img.IsBinary;
        bool second = img.IsBinary;
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPBM_IsBinary()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.IsBinary);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_IsNotBinary()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.False(img.IsBinary);
    }
}
