// Tests for NetpbmImage.GetIsPortableFormat dedicated coverage.
// Sprint: ff-sprint-s499-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R517

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R517: Dedicated tests for NetpbmImage.GetIsPortableFormat().
/// PBM image returns true (portable bitmap format).
/// PGM image returns true (portable graymap format).
/// PPM image returns true (portable pixmap format).
/// Width unchanged after GetIsPortableFormat.
/// Height unchanged after GetIsPortableFormat.
/// Format unchanged after GetIsPortableFormat.
/// MaxValue unchanged after GetIsPortableFormat.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline is portable format.
/// Dogfood: PGM pipeline is portable format.
/// Dogfood: PPM pipeline is portable format.
/// </summary>
public class NetpbmR517GetIsPortableFormatDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsPortableFormat_PbmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetIsPortableFormat());
    }

    [Fact]
    public void GetIsPortableFormat_PgmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetIsPortableFormat());
    }

    [Fact]
    public void GetIsPortableFormat_PpmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetIsPortableFormat());
    }

    [Fact]
    public void GetIsPortableFormat_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetIsPortableFormat();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsPortableFormat_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetIsPortableFormat();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsPortableFormat_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetIsPortableFormat();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsPortableFormat_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetIsPortableFormat();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsPortableFormat_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetIsPortableFormat();
        bool second = img.GetIsPortableFormat();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_IsPortableFormat()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetIsPortableFormat();
        Assert.True(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_IsPortableFormat()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetIsPortableFormat();
        Assert.True(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_IsPortableFormat()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetIsPortableFormat();
        Assert.True(result);
    }
}
