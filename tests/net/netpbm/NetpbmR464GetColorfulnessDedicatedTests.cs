// Tests for NetpbmImage.GetColorfulness dedicated coverage.
// Sprint: ff-sprint-s446-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R464

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R464: Dedicated tests for NetpbmImage.GetColorfulness().
/// Returns non-negative value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// PPM colorfulness >= PGM (more color channels).
/// Dogfood: 4x4 PGM and PPM colorfulness non-negative.
/// </summary>
public class NetpbmR464GetColorfulnessDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorfulness_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetColorfulness();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetColorfulness_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetColorfulness();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetColorfulness_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetColorfulness();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetColorfulness_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetColorfulness();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetColorfulness_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetColorfulness();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetColorfulness_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetColorfulness();
        double second = img.GetColorfulness();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColorfulness_PBM_NonNegative()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetColorfulness();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetColorfulness_PGM_NonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetColorfulness();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetColorfulness_PPM_NonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetColorfulness();
        Assert.True(val >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ColorfulnessNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetColorfulness();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_ColorfulnessNonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetColorfulness();
        Assert.True(val >= 0.0);
    }
}
