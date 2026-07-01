// Tests for NetpbmImage.GetFormatDescription dedicated coverage.
// Sprint: ff-sprint-s493-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R511

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R511: Dedicated tests for NetpbmImage.GetFormatDescription().
/// PBM image returns non-null non-empty description.
/// PGM image returns non-null non-empty description.
/// PPM image returns non-null non-empty description.
/// Width unchanged after GetFormatDescription.
/// Height unchanged after GetFormatDescription.
/// Format unchanged after GetFormatDescription.
/// MaxValue unchanged after GetFormatDescription.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline description contains format identifier.
/// Dogfood: PGM pipeline description contains format identifier.
/// Dogfood: PPM pipeline description contains format identifier.
/// </summary>
public class NetpbmR511GetFormatDescriptionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFormatDescription_PbmImage_ReturnsNonNullNonEmpty()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        string desc = img.GetFormatDescription();
        Assert.NotNull(desc);
        Assert.NotEmpty(desc);
    }

    [Fact]
    public void GetFormatDescription_PgmImage_ReturnsNonNullNonEmpty()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        string desc = img.GetFormatDescription();
        Assert.NotNull(desc);
        Assert.NotEmpty(desc);
    }

    [Fact]
    public void GetFormatDescription_PpmImage_ReturnsNonNullNonEmpty()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        string desc = img.GetFormatDescription();
        Assert.NotNull(desc);
        Assert.NotEmpty(desc);
    }

    [Fact]
    public void GetFormatDescription_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetFormatDescription();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetFormatDescription_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetFormatDescription();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetFormatDescription_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetFormatDescription();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetFormatDescription_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetFormatDescription();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetFormatDescription_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        string first = img.GetFormatDescription();
        string second = img.GetFormatDescription();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_DescriptionContainsPbm()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        string result = img.GetFormatDescription();
        Assert.Contains("pbm", result, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_DescriptionContainsPgm()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        string result = img.GetFormatDescription();
        Assert.Contains("pgm", result, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_DescriptionContainsPpm()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        string result = img.GetFormatDescription();
        Assert.Contains("ppm", result, StringComparison.OrdinalIgnoreCase);
    }
}
