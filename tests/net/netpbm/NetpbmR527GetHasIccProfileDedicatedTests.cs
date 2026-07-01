// Tests for NetpbmImage.GetHasIccProfile dedicated coverage.
// Sprint: ff-sprint-s509-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R527

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R527: Dedicated tests for NetpbmImage.GetHasIccProfile().
/// PBM image returns false (Netpbm has no ICC profile support).
/// PGM image returns false (Netpbm has no ICC profile support).
/// PPM image returns false (Netpbm has no ICC profile support).
/// Width unchanged after GetHasIccProfile.
/// Height unchanged after GetHasIccProfile.
/// Format unchanged after GetHasIccProfile.
/// MaxValue unchanged after GetHasIccProfile.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline has no ICC profile.
/// Dogfood: PGM pipeline has no ICC profile.
/// Dogfood: PPM pipeline has no ICC profile.
/// </summary>
public class NetpbmR527GetHasIccProfileDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHasIccProfile_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.False(img.GetHasIccProfile());
    }

    [Fact]
    public void GetHasIccProfile_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.False(img.GetHasIccProfile());
    }

    [Fact]
    public void GetHasIccProfile_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.False(img.GetHasIccProfile());
    }

    [Fact]
    public void GetHasIccProfile_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetHasIccProfile();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHasIccProfile_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetHasIccProfile();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHasIccProfile_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetHasIccProfile();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHasIccProfile_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetHasIccProfile();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHasIccProfile_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetHasIccProfile();
        bool second = img.GetHasIccProfile();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_HasNoIccProfile()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetHasIccProfile();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_HasNoIccProfile()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetHasIccProfile();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_HasNoIccProfile()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetHasIccProfile();
        Assert.False(result);
    }
}
