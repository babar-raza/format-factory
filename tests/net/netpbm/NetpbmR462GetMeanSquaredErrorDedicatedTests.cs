// Tests for NetpbmImage.GetMeanSquaredError dedicated coverage.
// Sprint: ff-sprint-s444-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R462

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R462: Dedicated tests for NetpbmImage.GetMeanSquaredError().
/// Returns non-negative value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM MSE non-negative.
/// </summary>
public class NetpbmR462GetMeanSquaredErrorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMeanSquaredError_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetMeanSquaredError();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetMeanSquaredError_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetMeanSquaredError();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMeanSquaredError_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetMeanSquaredError();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMeanSquaredError_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetMeanSquaredError();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMeanSquaredError_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetMeanSquaredError();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMeanSquaredError_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetMeanSquaredError();
        double second = img.GetMeanSquaredError();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMeanSquaredError_PBM_NonNegative()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetMeanSquaredError();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetMeanSquaredError_PGM_NonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetMeanSquaredError();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetMeanSquaredError_PPM_NonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetMeanSquaredError();
        Assert.True(val >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_MSENonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetMeanSquaredError();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_MSENonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetMeanSquaredError();
        Assert.True(val >= 0.0);
    }
}
