// Tests for NetpbmImage.GetSupportedFeatures dedicated coverage.
// Sprint: ff-sprint-s496-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R514

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R514: Dedicated tests for NetpbmImage.GetSupportedFeatures().
/// PBM image returns non-null non-empty string.
/// PGM image returns non-null non-empty string.
/// PPM image returns non-null non-empty string.
/// Width unchanged after GetSupportedFeatures.
/// Height unchanged after GetSupportedFeatures.
/// Format unchanged after GetSupportedFeatures.
/// MaxValue unchanged after GetSupportedFeatures.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline features string is non-null.
/// Dogfood: PGM pipeline features string is non-null.
/// Dogfood: PPM pipeline features string is non-null.
/// </summary>
public class NetpbmR514GetSupportedFeaturesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSupportedFeatures_PbmImage_ReturnsNonNullNonEmpty()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        string features = img.GetSupportedFeatures();
        Assert.NotNull(features);
        Assert.NotEmpty(features);
    }

    [Fact]
    public void GetSupportedFeatures_PgmImage_ReturnsNonNullNonEmpty()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        string features = img.GetSupportedFeatures();
        Assert.NotNull(features);
        Assert.NotEmpty(features);
    }

    [Fact]
    public void GetSupportedFeatures_PpmImage_ReturnsNonNullNonEmpty()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        string features = img.GetSupportedFeatures();
        Assert.NotNull(features);
        Assert.NotEmpty(features);
    }

    [Fact]
    public void GetSupportedFeatures_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetSupportedFeatures();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetSupportedFeatures_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetSupportedFeatures();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetSupportedFeatures_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetSupportedFeatures();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetSupportedFeatures_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetSupportedFeatures();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetSupportedFeatures_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        string first = img.GetSupportedFeatures();
        string second = img.GetSupportedFeatures();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_FeaturesIsNonNull()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        string result = img.GetSupportedFeatures();
        Assert.NotNull(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_FeaturesIsNonNull()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        string result = img.GetSupportedFeatures();
        Assert.NotNull(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_FeaturesIsNonNull()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        string result = img.GetSupportedFeatures();
        Assert.NotNull(result);
    }
}
