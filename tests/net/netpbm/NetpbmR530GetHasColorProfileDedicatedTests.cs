// Tests for NetpbmImage.GetHasColorProfile dedicated coverage.
// Sprint: ff-sprint-s512-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R530

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R530: Dedicated tests for NetpbmImage.GetHasColorProfile().
/// PBM image returns false (Netpbm has no color profile support).
/// PGM image returns false (Netpbm has no color profile support).
/// PPM image returns false (Netpbm has no color profile support).
/// Width unchanged after GetHasColorProfile.
/// Height unchanged after GetHasColorProfile.
/// Format unchanged after GetHasColorProfile.
/// MaxValue unchanged after GetHasColorProfile.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline has no color profile.
/// Dogfood: PGM pipeline has no color profile.
/// Dogfood: PPM pipeline has no color profile.
/// </summary>
public class NetpbmR530GetHasColorProfileDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHasColorProfile_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.False(img.GetHasColorProfile());
    }

    [Fact]
    public void GetHasColorProfile_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.False(img.GetHasColorProfile());
    }

    [Fact]
    public void GetHasColorProfile_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.False(img.GetHasColorProfile());
    }

    [Fact]
    public void GetHasColorProfile_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetHasColorProfile();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHasColorProfile_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetHasColorProfile();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHasColorProfile_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetHasColorProfile();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHasColorProfile_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetHasColorProfile();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHasColorProfile_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetHasColorProfile();
        bool second = img.GetHasColorProfile();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_HasNoColorProfile()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetHasColorProfile();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_HasNoColorProfile()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetHasColorProfile();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_HasNoColorProfile()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetHasColorProfile();
        Assert.False(result);
    }
}
