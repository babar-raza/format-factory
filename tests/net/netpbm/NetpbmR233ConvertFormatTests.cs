// Tests for NetpbmImage.ConvertFormat dedicated coverage.
// Sprint: ff-sprint-s226-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R233

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R233: Dedicated tests for NetpbmImage.ConvertFormat(targetFormat).
/// Returns new image (not same reference).
/// Target format set correctly.
/// MaxValue preserved.
/// Width preserved.
/// Height preserved.
/// All pixels in valid range.
/// Original image format unchanged.
/// PGM to PPM conversion: no exception.
/// PPM to PGM conversion: no exception.
/// Dogfood: convert back-and-forth produces valid image.
/// </summary>
public class NetpbmR233ConvertFormatTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ConvertFormat_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ConvertFormat(NetpbmFormat.PPM_P6);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void ConvertFormat_TargetFormatSet()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ConvertFormat(NetpbmFormat.PPM_P6);
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void ConvertFormat_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.ConvertFormat(NetpbmFormat.PPM_P6);
        Assert.Equal(200, result.MaxValue);
    }

    [Fact]
    public void ConvertFormat_WidthPreserved()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ConvertFormat(NetpbmFormat.PPM_P6);
        Assert.Equal(6, result.Width);
    }

    [Fact]
    public void ConvertFormat_HeightPreserved()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.ConvertFormat(NetpbmFormat.PPM_P6);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void ConvertFormat_AllPixelsInValidRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 15);
        img.SetPixel(0, 0, 10);
        var result = img.ConvertFormat(NetpbmFormat.PPM_P6);
        for (int y = 0; y < result.Height; y++)
            for (int x = 0; x < result.Width; x++)
                Assert.InRange(result.GetPixel(x, y), 0, 15);
    }

    [Fact]
    public void ConvertFormat_OriginalFormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.ConvertFormat(NetpbmFormat.PPM_P6);
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void ConvertFormat_PgmToPpm_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var ex = Record.Exception(() => img.ConvertFormat(NetpbmFormat.PPM_P6));
        Assert.Null(ex);
    }

    [Fact]
    public void ConvertFormat_PpmToPgm_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6, maxValue: 255);
        var ex = Record.Exception(() => img.ConvertFormat(NetpbmFormat.PGM_P5));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ConvertBackAndForth_ValidImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 15);
        img.SetPixel(1, 1, 7);
        var converted = img.ConvertFormat(NetpbmFormat.PPM_P6).ConvertFormat(NetpbmFormat.PGM_P5);
        Assert.Equal(NetpbmFormat.PGM_P5, converted.Format);
        Assert.Equal(4, converted.Width);
        Assert.Equal(4, converted.Height);
    }
}
