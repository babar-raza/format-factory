// Tests for NetpbmImage.GetColorTemperature dedicated coverage.
// Sprint: ff-sprint-s435-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R453

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R453: Dedicated tests for NetpbmImage.GetColorTemperature().
/// Returns non-negative value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM color temperature non-negative.
/// </summary>
public class NetpbmR453GetColorTemperatureDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorTemperature_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetColorTemperature();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetColorTemperature_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetColorTemperature();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetColorTemperature_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetColorTemperature();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetColorTemperature_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetColorTemperature();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetColorTemperature_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetColorTemperature();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetColorTemperature_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetColorTemperature();
        double second = img.GetColorTemperature();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColorTemperature_PBM_NonNegative()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetColorTemperature();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetColorTemperature_PGM_NonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetColorTemperature();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetColorTemperature_PPM_NonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetColorTemperature();
        Assert.True(val >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ColorTemperatureNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetColorTemperature();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_ColorTemperatureNonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetColorTemperature();
        Assert.True(val >= 0.0);
    }
}
