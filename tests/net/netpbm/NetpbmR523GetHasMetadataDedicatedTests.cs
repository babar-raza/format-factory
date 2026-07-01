// Tests for NetpbmImage.GetHasMetadata dedicated coverage.
// Sprint: ff-sprint-s505-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R523

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R523: Dedicated tests for NetpbmImage.GetHasMetadata().
/// PBM image returns false (Netpbm has no embedded metadata).
/// PGM image returns false (Netpbm has no embedded metadata).
/// PPM image returns false (Netpbm has no embedded metadata).
/// Width unchanged after GetHasMetadata.
/// Height unchanged after GetHasMetadata.
/// Format unchanged after GetHasMetadata.
/// MaxValue unchanged after GetHasMetadata.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline has no metadata.
/// Dogfood: PGM pipeline has no metadata.
/// Dogfood: PPM pipeline has no metadata.
/// </summary>
public class NetpbmR523GetHasMetadataDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHasMetadata_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.False(img.GetHasMetadata());
    }

    [Fact]
    public void GetHasMetadata_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.False(img.GetHasMetadata());
    }

    [Fact]
    public void GetHasMetadata_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.False(img.GetHasMetadata());
    }

    [Fact]
    public void GetHasMetadata_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetHasMetadata();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHasMetadata_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetHasMetadata();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHasMetadata_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetHasMetadata();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHasMetadata_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetHasMetadata();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHasMetadata_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetHasMetadata();
        bool second = img.GetHasMetadata();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_HasNoMetadata()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetHasMetadata();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_HasNoMetadata()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetHasMetadata();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_HasNoMetadata()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetHasMetadata();
        Assert.False(result);
    }
}
