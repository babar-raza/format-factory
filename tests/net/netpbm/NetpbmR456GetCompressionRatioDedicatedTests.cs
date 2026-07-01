// Tests for NetpbmImage.GetCompressionRatio dedicated coverage.
// Sprint: ff-sprint-s438-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R456

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R456: Dedicated tests for NetpbmImage.GetCompressionRatio().
/// Returns positive value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM compression ratio positive.
/// </summary>
public class NetpbmR456GetCompressionRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionRatio_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetCompressionRatio();
        Assert.True(val > 0.0);
    }

    [Fact]
    public void GetCompressionRatio_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetCompressionRatio();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetCompressionRatio_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetCompressionRatio();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetCompressionRatio_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetCompressionRatio();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetCompressionRatio_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetCompressionRatio();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetCompressionRatio_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetCompressionRatio();
        double second = img.GetCompressionRatio();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCompressionRatio_PBM_Positive()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetCompressionRatio();
        Assert.True(val > 0.0);
    }

    [Fact]
    public void GetCompressionRatio_PGM_Positive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetCompressionRatio();
        Assert.True(val > 0.0);
    }

    [Fact]
    public void GetCompressionRatio_PPM_Positive()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetCompressionRatio();
        Assert.True(val > 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_CompressionRatioPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetCompressionRatio();
        Assert.True(val > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_CompressionRatioPositive()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetCompressionRatio();
        Assert.True(val > 0.0);
    }
}
