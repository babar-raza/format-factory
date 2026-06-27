// Tests for NetpbmImage.GetColorSpace dedicated coverage.
// Sprint: ff-sprint-s388-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R401

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R401: Dedicated tests for NetpbmImage.GetColorSpace().
/// PBM returns non-null.
/// PGM returns non-null.
/// PPM returns non-null.
/// Width unchanged after GetColorSpace.
/// Height unchanged after GetColorSpace.
/// Format unchanged after GetColorSpace.
/// MaxValue unchanged after GetColorSpace.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PBM color space non-null.
/// Dogfood: 4x4 PPM color space non-null.
/// </summary>
public class NetpbmR401GetColorSpaceDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorSpace_PBM_ReturnsNonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        string colorSpace = img.GetColorSpace();
        Assert.NotNull(colorSpace);
    }

    [Fact]
    public void GetColorSpace_PGM_ReturnsNonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        string colorSpace = img.GetColorSpace();
        Assert.NotNull(colorSpace);
    }

    [Fact]
    public void GetColorSpace_PPM_ReturnsNonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string colorSpace = img.GetColorSpace();
        Assert.NotNull(colorSpace);
    }

    [Fact]
    public void GetColorSpace_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetColorSpace();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetColorSpace_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetColorSpace();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetColorSpace_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetColorSpace();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetColorSpace_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetColorSpace();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetColorSpace_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string first = img.GetColorSpace();
        string second = img.GetColorSpace();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPBM_ColorSpaceNonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        string colorSpace = img.GetColorSpace();
        Assert.NotNull(colorSpace);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_ColorSpaceNonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string colorSpace = img.GetColorSpace();
        Assert.NotNull(colorSpace);
    }
}
