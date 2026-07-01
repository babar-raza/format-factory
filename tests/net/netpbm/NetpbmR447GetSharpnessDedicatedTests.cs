// Tests for NetpbmImage.GetSharpness dedicated coverage.
// Sprint: ff-sprint-s429-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R447

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R447: Dedicated tests for NetpbmImage.GetSharpness().
/// Returns non-negative value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM sharpness non-negative.
/// </summary>
public class NetpbmR447GetSharpnessDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSharpness_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetSharpness();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetSharpness_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetSharpness();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetSharpness_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetSharpness();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetSharpness_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetSharpness();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetSharpness_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetSharpness();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetSharpness_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetSharpness();
        double second = img.GetSharpness();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSharpness_PBM_NonNegative()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetSharpness();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetSharpness_PGM_NonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetSharpness();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetSharpness_PPM_NonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetSharpness();
        Assert.True(val >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_SharpnessNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetSharpness();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_SharpnessNonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetSharpness();
        Assert.True(val >= 0.0);
    }
}
