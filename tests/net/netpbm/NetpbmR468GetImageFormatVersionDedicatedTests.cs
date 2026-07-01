// Tests for NetpbmImage.GetImageFormatVersion dedicated coverage.
// Sprint: ff-sprint-s450-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R468

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R468: Dedicated tests for NetpbmImage.GetImageFormatVersion().
/// Returns non-null string for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM format version not null.
/// </summary>
public class NetpbmR468GetImageFormatVersionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageFormatVersion_ReturnsNotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetImageFormatVersion();
        Assert.NotNull(val);
    }

    [Fact]
    public void GetImageFormatVersion_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetImageFormatVersion();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetImageFormatVersion_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetImageFormatVersion();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetImageFormatVersion_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetImageFormatVersion();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetImageFormatVersion_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetImageFormatVersion();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetImageFormatVersion_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetImageFormatVersion();
        string second = img.GetImageFormatVersion();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetImageFormatVersion_PBM_NotNull()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        string val = img.GetImageFormatVersion();
        Assert.NotNull(val);
    }

    [Fact]
    public void GetImageFormatVersion_PGM_NotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetImageFormatVersion();
        Assert.NotNull(val);
    }

    [Fact]
    public void GetImageFormatVersion_PPM_NotNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        string val = img.GetImageFormatVersion();
        Assert.NotNull(val);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_FormatVersionNotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetImageFormatVersion();
        Assert.NotNull(val);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_FormatVersionNotNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        string val = img.GetImageFormatVersion();
        Assert.NotNull(val);
    }
}
