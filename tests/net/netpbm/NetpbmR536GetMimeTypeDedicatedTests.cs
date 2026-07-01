// Tests for NetpbmImage.GetMimeType dedicated coverage.
// Sprint: ff-sprint-s518-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R536

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R536: Dedicated tests for NetpbmImage.GetMimeType().
/// PBM image returns "image/x-portable-bitmap".
/// PGM image returns "image/x-portable-graymap".
/// PPM image returns "image/x-portable-pixmap".
/// Width unchanged after GetMimeType.
/// Height unchanged after GetMimeType.
/// Format unchanged after GetMimeType.
/// MaxValue unchanged after GetMimeType.
/// Idempotent (called twice same result).
/// Dogfood: PBM mime type contains image.
/// Dogfood: PGM mime type contains image.
/// Dogfood: PPM mime type contains image.
/// </summary>
public class NetpbmR536GetMimeTypeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMimeType_PbmImage_ReturnsBitmapMime()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.Equal("image/x-portable-bitmap", img.GetMimeType());
    }

    [Fact]
    public void GetMimeType_PgmImage_ReturnsGraymapMime()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.Equal("image/x-portable-graymap", img.GetMimeType());
    }

    [Fact]
    public void GetMimeType_PpmImage_ReturnsPixmapMime()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.Equal("image/x-portable-pixmap", img.GetMimeType());
    }

    [Fact]
    public void GetMimeType_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetMimeType();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMimeType_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetMimeType();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMimeType_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetMimeType();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMimeType_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetMimeType();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMimeType_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        string first = img.GetMimeType();
        string second = img.GetMimeType();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_MimeContainsImage()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        Assert.Contains("image", img.GetMimeType());
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_MimeContainsImage()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        Assert.Contains("image", img.GetMimeType());
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_MimeContainsImage()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        Assert.Contains("image", img.GetMimeType());
    }
}
