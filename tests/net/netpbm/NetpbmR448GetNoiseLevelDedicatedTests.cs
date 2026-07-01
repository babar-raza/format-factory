// Tests for NetpbmImage.GetNoiseLevel dedicated coverage.
// Sprint: ff-sprint-s430-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R448

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R448: Dedicated tests for NetpbmImage.GetNoiseLevel().
/// Returns non-negative value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM noise level non-negative.
/// </summary>
public class NetpbmR448GetNoiseLevelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNoiseLevel_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetNoiseLevel();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetNoiseLevel_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetNoiseLevel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetNoiseLevel_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetNoiseLevel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetNoiseLevel_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetNoiseLevel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetNoiseLevel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetNoiseLevel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetNoiseLevel_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetNoiseLevel();
        double second = img.GetNoiseLevel();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetNoiseLevel_PBM_NonNegative()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetNoiseLevel();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetNoiseLevel_PGM_NonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetNoiseLevel();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetNoiseLevel_PPM_NonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetNoiseLevel();
        Assert.True(val >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_NoiseLevelNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetNoiseLevel();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_NoiseLevelNonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetNoiseLevel();
        Assert.True(val >= 0.0);
    }
}
