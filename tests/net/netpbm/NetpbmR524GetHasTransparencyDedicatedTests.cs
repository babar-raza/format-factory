// Tests for NetpbmImage.GetHasTransparency dedicated coverage.
// Sprint: ff-sprint-s506-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R524

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R524: Dedicated tests for NetpbmImage.GetHasTransparency().
/// PBM image returns false (no transparency support).
/// PGM image returns false (no transparency support).
/// PPM image returns false (no transparency support).
/// Width unchanged after GetHasTransparency.
/// Height unchanged after GetHasTransparency.
/// Format unchanged after GetHasTransparency.
/// MaxValue unchanged after GetHasTransparency.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline has no transparency.
/// Dogfood: PGM pipeline has no transparency.
/// Dogfood: PPM pipeline has no transparency.
/// </summary>
public class NetpbmR524GetHasTransparencyDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHasTransparency_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.False(img.GetHasTransparency());
    }

    [Fact]
    public void GetHasTransparency_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.False(img.GetHasTransparency());
    }

    [Fact]
    public void GetHasTransparency_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.False(img.GetHasTransparency());
    }

    [Fact]
    public void GetHasTransparency_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetHasTransparency();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHasTransparency_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetHasTransparency();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHasTransparency_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetHasTransparency();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHasTransparency_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetHasTransparency();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHasTransparency_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetHasTransparency();
        bool second = img.GetHasTransparency();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_HasNoTransparency()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetHasTransparency();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_HasNoTransparency()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetHasTransparency();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_HasNoTransparency()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetHasTransparency();
        Assert.False(result);
    }
}
