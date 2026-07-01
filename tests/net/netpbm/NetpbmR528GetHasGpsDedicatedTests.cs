// Tests for NetpbmImage.GetHasGps dedicated coverage.
// Sprint: ff-sprint-s510-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R528

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R528: Dedicated tests for NetpbmImage.GetHasGps().
/// PBM image returns false (Netpbm has no GPS metadata support).
/// PGM image returns false (Netpbm has no GPS metadata support).
/// PPM image returns false (Netpbm has no GPS metadata support).
/// Width unchanged after GetHasGps.
/// Height unchanged after GetHasGps.
/// Format unchanged after GetHasGps.
/// MaxValue unchanged after GetHasGps.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline has no GPS.
/// Dogfood: PGM pipeline has no GPS.
/// Dogfood: PPM pipeline has no GPS.
/// </summary>
public class NetpbmR528GetHasGpsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHasGps_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.False(img.GetHasGps());
    }

    [Fact]
    public void GetHasGps_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.False(img.GetHasGps());
    }

    [Fact]
    public void GetHasGps_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.False(img.GetHasGps());
    }

    [Fact]
    public void GetHasGps_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetHasGps();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHasGps_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetHasGps();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHasGps_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetHasGps();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHasGps_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetHasGps();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHasGps_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetHasGps();
        bool second = img.GetHasGps();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_HasNoGps()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetHasGps();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_HasNoGps()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetHasGps();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_HasNoGps()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetHasGps();
        Assert.False(result);
    }
}
