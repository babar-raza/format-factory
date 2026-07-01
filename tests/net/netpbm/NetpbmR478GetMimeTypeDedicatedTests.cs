// Tests for NetpbmImage.GetMimeType dedicated coverage.
// Sprint: ff-sprint-s460-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R478

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R478: Dedicated tests for NetpbmImage.GetMimeType().
/// PBM returns "image/x-portable-bitmap".
/// PGM returns "image/x-portable-graymap".
/// PPM returns "image/x-portable-pixmap".
/// Width unchanged after GetMimeType.
/// Height unchanged after GetMimeType.
/// Format unchanged after GetMimeType.
/// MaxValue unchanged after GetMimeType.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM mime type contains "graymap".
/// Dogfood: 4x4 PPM mime type contains "pixmap".
/// Dogfood: all formats start with "image/".
/// </summary>
public class NetpbmR478GetMimeTypeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMimeType_PBM_ReturnsCorrectMime()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.Equal("image/x-portable-bitmap", img.GetMimeType());
    }

    [Fact]
    public void GetMimeType_PGM_ReturnsCorrectMime()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.Equal("image/x-portable-graymap", img.GetMimeType());
    }

    [Fact]
    public void GetMimeType_PPM_ReturnsCorrectMime()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.Equal("image/x-portable-pixmap", img.GetMimeType());
    }

    [Fact]
    public void GetMimeType_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetMimeType();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMimeType_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetMimeType();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMimeType_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetMimeType();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMimeType_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetMimeType();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMimeType_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetMimeType();
        string second = img.GetMimeType();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_MimeContainsGraymap()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.Contains("graymap", img.GetMimeType());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_MimeContainsPixmap()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.Contains("pixmap", img.GetMimeType());
    }

    [Fact]
    public void DogfoodPipeline_AllFormats_StartWithImage()
    {
        foreach (var img in new[] { NetpbmImage.CreatePBM(4, 4), NetpbmImage.CreatePGM(4, 4, 255), NetpbmImage.CreatePPM(4, 4, 255) })
        {
            Assert.StartsWith("image/", img.GetMimeType());
        }
    }
}
