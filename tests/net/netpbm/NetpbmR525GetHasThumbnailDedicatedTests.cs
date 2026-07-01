// Tests for NetpbmImage.GetHasThumbnail dedicated coverage.
// Sprint: ff-sprint-s507-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R525

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R525: Dedicated tests for NetpbmImage.GetHasThumbnail().
/// PBM image returns false (Netpbm has no embedded thumbnail).
/// PGM image returns false (Netpbm has no embedded thumbnail).
/// PPM image returns false (Netpbm has no embedded thumbnail).
/// Width unchanged after GetHasThumbnail.
/// Height unchanged after GetHasThumbnail.
/// Format unchanged after GetHasThumbnail.
/// MaxValue unchanged after GetHasThumbnail.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline has no thumbnail.
/// Dogfood: PGM pipeline has no thumbnail.
/// Dogfood: PPM pipeline has no thumbnail.
/// </summary>
public class NetpbmR525GetHasThumbnailDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHasThumbnail_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.False(img.GetHasThumbnail());
    }

    [Fact]
    public void GetHasThumbnail_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.False(img.GetHasThumbnail());
    }

    [Fact]
    public void GetHasThumbnail_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.False(img.GetHasThumbnail());
    }

    [Fact]
    public void GetHasThumbnail_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetHasThumbnail();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHasThumbnail_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetHasThumbnail();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHasThumbnail_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetHasThumbnail();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHasThumbnail_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetHasThumbnail();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHasThumbnail_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetHasThumbnail();
        bool second = img.GetHasThumbnail();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_HasNoThumbnail()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetHasThumbnail();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_HasNoThumbnail()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetHasThumbnail();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_HasNoThumbnail()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetHasThumbnail();
        Assert.False(result);
    }
}
