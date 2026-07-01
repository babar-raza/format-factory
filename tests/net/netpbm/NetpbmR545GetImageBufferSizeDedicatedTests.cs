// Tests for NetpbmImage.GetImageBufferSize dedicated coverage.
// Sprint: ff-sprint-s527-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R545

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R545: Dedicated tests for NetpbmImage.GetImageBufferSize().
/// PBM image returns positive buffer size.
/// PGM image returns positive buffer size.
/// PPM image returns positive buffer size.
/// Width unchanged after GetImageBufferSize.
/// Height unchanged after GetImageBufferSize.
/// Format unchanged after GetImageBufferSize.
/// MaxValue unchanged after GetImageBufferSize.
/// Idempotent (called twice same result).
/// Dogfood: PBM buffer size positive.
/// Dogfood: PGM buffer size positive.
/// Dogfood: PPM buffer size positive.
/// </summary>
public class NetpbmR545GetImageBufferSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageBufferSize_PbmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetImageBufferSize() > 0);
    }

    [Fact]
    public void GetImageBufferSize_PgmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetImageBufferSize() > 0);
    }

    [Fact]
    public void GetImageBufferSize_PpmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetImageBufferSize() > 0);
    }

    [Fact]
    public void GetImageBufferSize_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetImageBufferSize();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetImageBufferSize_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetImageBufferSize();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetImageBufferSize_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetImageBufferSize();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetImageBufferSize_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetImageBufferSize();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetImageBufferSize_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetImageBufferSize();
        int second = img.GetImageBufferSize();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_BufferSizePositive()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        Assert.True(img.GetImageBufferSize() > 0);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_BufferSizePositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        Assert.True(img.GetImageBufferSize() > 0);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_BufferSizePositive()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        Assert.True(img.GetImageBufferSize() > 0);
    }
}
