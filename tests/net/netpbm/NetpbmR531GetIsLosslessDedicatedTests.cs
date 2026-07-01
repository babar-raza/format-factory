// Tests for NetpbmImage.GetIsLossless dedicated coverage.
// Sprint: ff-sprint-s513-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R531

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R531: Dedicated tests for NetpbmImage.GetIsLossless().
/// PBM image returns true (Netpbm is a lossless format).
/// PGM image returns true (Netpbm is a lossless format).
/// PPM image returns true (Netpbm is a lossless format).
/// Width unchanged after GetIsLossless.
/// Height unchanged after GetIsLossless.
/// Format unchanged after GetIsLossless.
/// MaxValue unchanged after GetIsLossless.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline is lossless.
/// Dogfood: PGM pipeline is lossless.
/// Dogfood: PPM pipeline is lossless.
/// </summary>
public class NetpbmR531GetIsLosslessDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsLossless_PbmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetIsLossless());
    }

    [Fact]
    public void GetIsLossless_PgmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetIsLossless());
    }

    [Fact]
    public void GetIsLossless_PpmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetIsLossless());
    }

    [Fact]
    public void GetIsLossless_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetIsLossless();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsLossless_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetIsLossless();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsLossless_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetIsLossless();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsLossless_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetIsLossless();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsLossless_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetIsLossless();
        bool second = img.GetIsLossless();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_IsLossless()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetIsLossless();
        Assert.True(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_IsLossless()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetIsLossless();
        Assert.True(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_IsLossless()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetIsLossless();
        Assert.True(result);
    }
}
