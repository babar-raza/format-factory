// Tests for NetpbmImage.GetVersionString dedicated coverage.
// Sprint: ff-sprint-s462-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R480

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R480: Dedicated tests for NetpbmImage.GetVersionString().
/// Returns non-null non-empty string.
/// Width unchanged after GetVersionString.
/// Height unchanged after GetVersionString.
/// Format unchanged after GetVersionString.
/// MaxValue unchanged after GetVersionString.
/// Idempotent (called twice same result).
/// PBM returns non-null.
/// PGM returns non-null.
/// PPM returns non-null.
/// Dogfood: 4x4 PGM version non-null.
/// Dogfood: 4x4 PPM version non-null.
/// </summary>
public class NetpbmR480GetVersionStringDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetVersionString_ReturnsNonNullNonEmpty()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(string.IsNullOrEmpty(img.GetVersionString()));
    }

    [Fact]
    public void GetVersionString_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetVersionString();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetVersionString_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetVersionString();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetVersionString_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetVersionString();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetVersionString_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetVersionString();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetVersionString_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetVersionString();
        string second = img.GetVersionString();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetVersionString_PBM_NonNull()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.NotNull(img.GetVersionString());
    }

    [Fact]
    public void GetVersionString_PGM_NonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetVersionString());
    }

    [Fact]
    public void GetVersionString_PPM_NonNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.NotNull(img.GetVersionString());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_VersionNonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetVersionString());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_VersionNonNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.NotNull(img.GetVersionString());
    }
}
