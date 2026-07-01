// Tests for NetpbmImage.GetCompressionType dedicated coverage.
// Sprint: ff-sprint-s488-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R506

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R506: Dedicated tests for NetpbmImage.GetCompressionType().
/// PBM image returns "none" (Netpbm is uncompressed).
/// PGM image returns "none" (Netpbm is uncompressed).
/// PPM image returns "none" (Netpbm is uncompressed).
/// Width unchanged after GetCompressionType.
/// Height unchanged after GetCompressionType.
/// Format unchanged after GetCompressionType.
/// MaxValue unchanged after GetCompressionType.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline returns "none".
/// Dogfood: PGM pipeline returns "none".
/// Dogfood: PPM pipeline returns "none".
/// </summary>
public class NetpbmR506GetCompressionTypeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionType_PbmImage_ReturnsNone()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.Equal("none", img.GetCompressionType());
    }

    [Fact]
    public void GetCompressionType_PgmImage_ReturnsNone()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.Equal("none", img.GetCompressionType());
    }

    [Fact]
    public void GetCompressionType_PpmImage_ReturnsNone()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.Equal("none", img.GetCompressionType());
    }

    [Fact]
    public void GetCompressionType_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetCompressionType();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetCompressionType_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetCompressionType();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetCompressionType_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetCompressionType();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetCompressionType_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetCompressionType();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetCompressionType_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        string first = img.GetCompressionType();
        string second = img.GetCompressionType();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ReturnsNone()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        string result = img.GetCompressionType();
        Assert.Equal("none", result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ReturnsNone()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        string result = img.GetCompressionType();
        Assert.Equal("none", result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ReturnsNone()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        string result = img.GetCompressionType();
        Assert.Equal("none", result);
    }
}
