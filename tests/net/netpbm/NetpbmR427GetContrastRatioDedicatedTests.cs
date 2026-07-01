// Tests for NetpbmImage.GetContrastRatio dedicated coverage.
// Sprint: ff-sprint-s409-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R427

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R427: Dedicated tests for NetpbmImage.GetContrastRatio().
/// Returns non-negative value.
/// Width unchanged after GetContrastRatio.
/// Height unchanged after GetContrastRatio.
/// Format unchanged after GetContrastRatio.
/// MaxValue unchanged after GetContrastRatio.
/// Idempotent (called twice same result).
/// PBM contrast non-negative.
/// PGM contrast non-negative.
/// PPM contrast non-negative.
/// Dogfood: 4x4 PGM contrast non-negative.
/// Dogfood: 4x4 PPM contrast non-negative.
/// </summary>
public class NetpbmR427GetContrastRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContrastRatio_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double contrast = img.GetContrastRatio();
        Assert.True(contrast >= 0);
    }

    [Fact]
    public void GetContrastRatio_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetContrastRatio();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetContrastRatio_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetContrastRatio();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetContrastRatio_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetContrastRatio();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetContrastRatio_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetContrastRatio();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetContrastRatio_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double first = img.GetContrastRatio();
        double second = img.GetContrastRatio();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetContrastRatio_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetContrastRatio() >= 0);
    }

    [Fact]
    public void GetContrastRatio_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetContrastRatio() >= 0);
    }

    [Fact]
    public void GetContrastRatio_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetContrastRatio() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ContrastNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetContrastRatio() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_ContrastNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetContrastRatio() >= 0);
    }
}
