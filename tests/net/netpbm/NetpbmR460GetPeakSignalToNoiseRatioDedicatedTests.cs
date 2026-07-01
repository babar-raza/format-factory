// Tests for NetpbmImage.GetPeakSignalToNoiseRatio dedicated coverage.
// Sprint: ff-sprint-s442-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R460

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R460: Dedicated tests for NetpbmImage.GetPeakSignalToNoiseRatio().
/// Returns non-negative value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM PSNR non-negative.
/// </summary>
public class NetpbmR460GetPeakSignalToNoiseRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPeakSignalToNoiseRatio_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetPeakSignalToNoiseRatio();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetPeakSignalToNoiseRatio_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetPeakSignalToNoiseRatio();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPeakSignalToNoiseRatio_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetPeakSignalToNoiseRatio();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPeakSignalToNoiseRatio_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetPeakSignalToNoiseRatio();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPeakSignalToNoiseRatio_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetPeakSignalToNoiseRatio();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPeakSignalToNoiseRatio_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetPeakSignalToNoiseRatio();
        double second = img.GetPeakSignalToNoiseRatio();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPeakSignalToNoiseRatio_PBM_NonNegative()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetPeakSignalToNoiseRatio();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetPeakSignalToNoiseRatio_PGM_NonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetPeakSignalToNoiseRatio();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetPeakSignalToNoiseRatio_PPM_NonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetPeakSignalToNoiseRatio();
        Assert.True(val >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_PSNRNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetPeakSignalToNoiseRatio();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_PSNRNonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetPeakSignalToNoiseRatio();
        Assert.True(val >= 0.0);
    }
}
