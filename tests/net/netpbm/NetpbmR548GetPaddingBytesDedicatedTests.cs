// Tests for NetpbmImage.GetPaddingBytes dedicated coverage.
// Sprint: ff-sprint-s530-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R548

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R548: Dedicated tests for NetpbmImage.GetPaddingBytes().
/// PBM image returns non-negative padding bytes.
/// PGM image returns non-negative padding bytes.
/// PPM image returns non-negative padding bytes.
/// Width unchanged after GetPaddingBytes.
/// Height unchanged after GetPaddingBytes.
/// Format unchanged after GetPaddingBytes.
/// MaxValue unchanged after GetPaddingBytes.
/// Idempotent (called twice same result).
/// Dogfood: PBM padding bytes non-negative.
/// Dogfood: PGM padding bytes non-negative.
/// Dogfood: PPM padding bytes non-negative.
/// </summary>
public class NetpbmR548GetPaddingBytesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPaddingBytes_PbmImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetPaddingBytes() >= 0);
    }

    [Fact]
    public void GetPaddingBytes_PgmImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetPaddingBytes() >= 0);
    }

    [Fact]
    public void GetPaddingBytes_PpmImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetPaddingBytes() >= 0);
    }

    [Fact]
    public void GetPaddingBytes_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetPaddingBytes();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPaddingBytes_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetPaddingBytes();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPaddingBytes_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetPaddingBytes();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPaddingBytes_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetPaddingBytes();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPaddingBytes_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetPaddingBytes();
        int second = img.GetPaddingBytes();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_PaddingNonNegative()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        Assert.True(img.GetPaddingBytes() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_PaddingNonNegative()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        Assert.True(img.GetPaddingBytes() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_PaddingNonNegative()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        Assert.True(img.GetPaddingBytes() >= 0);
    }
}
