// Tests for NetpbmImage.GetEncodingName dedicated coverage.
// Sprint: ff-sprint-s520-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R538

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R538: Dedicated tests for NetpbmImage.GetEncodingName().
/// PBM image returns non-null encoding name.
/// PGM image returns non-null encoding name.
/// PPM image returns non-null encoding name.
/// Width unchanged after GetEncodingName.
/// Height unchanged after GetEncodingName.
/// Format unchanged after GetEncodingName.
/// MaxValue unchanged after GetEncodingName.
/// Idempotent (called twice same result).
/// Dogfood: PBM encoding name is non-empty.
/// Dogfood: PGM encoding name is non-empty.
/// Dogfood: PPM encoding name is non-empty.
/// </summary>
public class NetpbmR538GetEncodingNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEncodingName_PbmImage_ReturnsNonNull()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.NotNull(img.GetEncodingName());
    }

    [Fact]
    public void GetEncodingName_PgmImage_ReturnsNonNull()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.NotNull(img.GetEncodingName());
    }

    [Fact]
    public void GetEncodingName_PpmImage_ReturnsNonNull()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.NotNull(img.GetEncodingName());
    }

    [Fact]
    public void GetEncodingName_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetEncodingName();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetEncodingName_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetEncodingName();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetEncodingName_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetEncodingName();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetEncodingName_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetEncodingName();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetEncodingName_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        string first = img.GetEncodingName();
        string second = img.GetEncodingName();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_EncodingNonEmpty()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        string name = img.GetEncodingName();
        Assert.False(string.IsNullOrEmpty(name));
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_EncodingNonEmpty()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        string name = img.GetEncodingName();
        Assert.False(string.IsNullOrEmpty(name));
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_EncodingNonEmpty()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        string name = img.GetEncodingName();
        Assert.False(string.IsNullOrEmpty(name));
    }
}
