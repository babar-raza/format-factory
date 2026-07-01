// Tests for NetpbmImage.GetRootMeanSquareError dedicated coverage.
// Sprint: ff-sprint-s445-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R463

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R463: Dedicated tests for NetpbmImage.GetRootMeanSquareError().
/// Returns non-negative value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM RMSE non-negative.
/// </summary>
public class NetpbmR463GetRootMeanSquareErrorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRootMeanSquareError_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetRootMeanSquareError();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetRootMeanSquareError_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetRootMeanSquareError();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetRootMeanSquareError_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetRootMeanSquareError();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetRootMeanSquareError_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetRootMeanSquareError();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetRootMeanSquareError_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetRootMeanSquareError();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetRootMeanSquareError_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetRootMeanSquareError();
        double second = img.GetRootMeanSquareError();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetRootMeanSquareError_PBM_NonNegative()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetRootMeanSquareError();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetRootMeanSquareError_PGM_NonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetRootMeanSquareError();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetRootMeanSquareError_PPM_NonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetRootMeanSquareError();
        Assert.True(val >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_RMSENonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetRootMeanSquareError();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_RMSENonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetRootMeanSquareError();
        Assert.True(val >= 0.0);
    }
}
