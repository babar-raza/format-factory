// Tests for NetpbmImage.GetFormatVersion dedicated coverage.
// Sprint: ff-sprint-s519-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R537

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R537: Dedicated tests for NetpbmImage.GetFormatVersion().
/// PBM image returns non-null version string.
/// PGM image returns non-null version string.
/// PPM image returns non-null version string.
/// Width unchanged after GetFormatVersion.
/// Height unchanged after GetFormatVersion.
/// Format unchanged after GetFormatVersion.
/// MaxValue unchanged after GetFormatVersion.
/// Idempotent (called twice same result).
/// Dogfood: PBM version is non-empty.
/// Dogfood: PGM version is non-empty.
/// Dogfood: PPM version is non-empty.
/// </summary>
public class NetpbmR537GetFormatVersionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFormatVersion_PbmImage_ReturnsNonNull()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.NotNull(img.GetFormatVersion());
    }

    [Fact]
    public void GetFormatVersion_PgmImage_ReturnsNonNull()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.NotNull(img.GetFormatVersion());
    }

    [Fact]
    public void GetFormatVersion_PpmImage_ReturnsNonNull()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.NotNull(img.GetFormatVersion());
    }

    [Fact]
    public void GetFormatVersion_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetFormatVersion();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetFormatVersion_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetFormatVersion();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetFormatVersion_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetFormatVersion();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetFormatVersion_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetFormatVersion();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetFormatVersion_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        string first = img.GetFormatVersion();
        string second = img.GetFormatVersion();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_VersionNonEmpty()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        string version = img.GetFormatVersion();
        Assert.False(string.IsNullOrEmpty(version));
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_VersionNonEmpty()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        string version = img.GetFormatVersion();
        Assert.False(string.IsNullOrEmpty(version));
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_VersionNonEmpty()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        string version = img.GetFormatVersion();
        Assert.False(string.IsNullOrEmpty(version));
    }
}
