// Tests for NetpbmImage.GetPixelDepth dedicated coverage.
// Sprint: ff-sprint-s521-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R539

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R539: Dedicated tests for NetpbmImage.GetPixelDepth().
/// PBM image returns 1 (single bit per pixel).
/// PGM image returns 8 (8-bit grayscale depth).
/// PPM image returns 24 (8 bits per channel × 3 channels).
/// Width unchanged after GetPixelDepth.
/// Height unchanged after GetPixelDepth.
/// Format unchanged after GetPixelDepth.
/// MaxValue unchanged after GetPixelDepth.
/// Idempotent (called twice same result).
/// Dogfood: PBM depth is 1.
/// Dogfood: PGM depth is 8.
/// Dogfood: PPM depth is 24.
/// </summary>
public class NetpbmR539GetPixelDepthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelDepth_PbmImage_Returns1()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.Equal(1, img.GetPixelDepth());
    }

    [Fact]
    public void GetPixelDepth_PgmImage_Returns8()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.Equal(8, img.GetPixelDepth());
    }

    [Fact]
    public void GetPixelDepth_PpmImage_Returns24()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.Equal(24, img.GetPixelDepth());
    }

    [Fact]
    public void GetPixelDepth_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetPixelDepth();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelDepth_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetPixelDepth();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelDepth_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetPixelDepth();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelDepth_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetPixelDepth();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelDepth_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetPixelDepth();
        int second = img.GetPixelDepth();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_DepthIs1()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        Assert.Equal(1, img.GetPixelDepth());
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_DepthIs8()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        Assert.Equal(8, img.GetPixelDepth());
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_DepthIs24()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        Assert.Equal(24, img.GetPixelDepth());
    }
}
