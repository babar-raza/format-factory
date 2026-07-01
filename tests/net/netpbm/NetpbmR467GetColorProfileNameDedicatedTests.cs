// Tests for NetpbmImage.GetColorProfileName dedicated coverage.
// Sprint: ff-sprint-s449-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R467

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R467: Dedicated tests for NetpbmImage.GetColorProfileName().
/// Returns non-null string for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM color profile name not null.
/// </summary>
public class NetpbmR467GetColorProfileNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorProfileName_ReturnsNotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetColorProfileName();
        Assert.NotNull(val);
    }

    [Fact]
    public void GetColorProfileName_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetColorProfileName();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetColorProfileName_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetColorProfileName();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetColorProfileName_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetColorProfileName();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetColorProfileName_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetColorProfileName();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetColorProfileName_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetColorProfileName();
        string second = img.GetColorProfileName();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColorProfileName_PBM_NotNull()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        string val = img.GetColorProfileName();
        Assert.NotNull(val);
    }

    [Fact]
    public void GetColorProfileName_PGM_NotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetColorProfileName();
        Assert.NotNull(val);
    }

    [Fact]
    public void GetColorProfileName_PPM_NotNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        string val = img.GetColorProfileName();
        Assert.NotNull(val);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ColorProfileNameNotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetColorProfileName();
        Assert.NotNull(val);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_ColorProfileNameNotNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        string val = img.GetColorProfileName();
        Assert.NotNull(val);
    }
}
