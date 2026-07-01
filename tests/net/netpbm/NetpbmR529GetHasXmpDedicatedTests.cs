// Tests for NetpbmImage.GetHasXmp dedicated coverage.
// Sprint: ff-sprint-s511-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R529

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R529: Dedicated tests for NetpbmImage.GetHasXmp().
/// PBM image returns false (Netpbm has no XMP metadata support).
/// PGM image returns false (Netpbm has no XMP metadata support).
/// PPM image returns false (Netpbm has no XMP metadata support).
/// Width unchanged after GetHasXmp.
/// Height unchanged after GetHasXmp.
/// Format unchanged after GetHasXmp.
/// MaxValue unchanged after GetHasXmp.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline has no XMP.
/// Dogfood: PGM pipeline has no XMP.
/// Dogfood: PPM pipeline has no XMP.
/// </summary>
public class NetpbmR529GetHasXmpDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHasXmp_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.False(img.GetHasXmp());
    }

    [Fact]
    public void GetHasXmp_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.False(img.GetHasXmp());
    }

    [Fact]
    public void GetHasXmp_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.False(img.GetHasXmp());
    }

    [Fact]
    public void GetHasXmp_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetHasXmp();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHasXmp_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetHasXmp();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHasXmp_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetHasXmp();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHasXmp_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetHasXmp();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHasXmp_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetHasXmp();
        bool second = img.GetHasXmp();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_HasNoXmp()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetHasXmp();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_HasNoXmp()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetHasXmp();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_HasNoXmp()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetHasXmp();
        Assert.False(result);
    }
}
