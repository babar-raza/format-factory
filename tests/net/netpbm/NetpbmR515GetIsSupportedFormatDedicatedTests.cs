// Tests for NetpbmImage.GetIsSupportedFormat dedicated coverage.
// Sprint: ff-sprint-s497-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R515

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R515: Dedicated tests for NetpbmImage.GetIsSupportedFormat().
/// PBM image returns true (supported format).
/// PGM image returns true (supported format).
/// PPM image returns true (supported format).
/// Width unchanged after GetIsSupportedFormat.
/// Height unchanged after GetIsSupportedFormat.
/// Format unchanged after GetIsSupportedFormat.
/// MaxValue unchanged after GetIsSupportedFormat.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline is supported format.
/// Dogfood: PGM pipeline is supported format.
/// Dogfood: PPM pipeline is supported format.
/// </summary>
public class NetpbmR515GetIsSupportedFormatDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsSupportedFormat_PbmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetIsSupportedFormat());
    }

    [Fact]
    public void GetIsSupportedFormat_PgmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetIsSupportedFormat());
    }

    [Fact]
    public void GetIsSupportedFormat_PpmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetIsSupportedFormat());
    }

    [Fact]
    public void GetIsSupportedFormat_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetIsSupportedFormat();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsSupportedFormat_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetIsSupportedFormat();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsSupportedFormat_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetIsSupportedFormat();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsSupportedFormat_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetIsSupportedFormat();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsSupportedFormat_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetIsSupportedFormat();
        bool second = img.GetIsSupportedFormat();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_IsSupportedFormat()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetIsSupportedFormat();
        Assert.True(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_IsSupportedFormat()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetIsSupportedFormat();
        Assert.True(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_IsSupportedFormat()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetIsSupportedFormat();
        Assert.True(result);
    }
}
