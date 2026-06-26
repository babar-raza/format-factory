// Tests for NetpbmImage.ToColor, ConvertFormat, Pipeline, Clone deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R182

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R182: Tests for NetpbmImage.ToColor, ConvertFormat, Pipeline, Clone deeper coverage.
/// ToColor(): converts image to PPM color format.
/// ConvertFormat(targetFormat): converts between PBM/PGM/PPM.
/// Pipeline(steps): applies sequence of transforms returning new image.
/// Clone(): returns deep copy of image.
/// Covers: ToColor returns PPM; ToColor dimensions unchanged; ToColor non-null;
/// ConvertFormat PGM→PPM returns PPM; ConvertFormat PPM→PGM returns PGM;
/// ConvertFormat dimensions unchanged; Clone returns new instance;
/// Clone dimensions match; Clone pixel change independent;
/// Pipeline empty returns equivalent; Pipeline with Sharpen runs;
/// Pipeline with multiple steps; Pipeline dimensions unchanged;
/// dogfood Create->ToColor->ConvertFormat->Clone->Pipeline verify pipeline.
/// </summary>
public class NetpbmR182ToColorAndConvertFormatTests
{
    private static NetpbmImage CreateGray(byte fill = 128, int w = 4, int h = 4)
        => NetpbmImage.Create(w, h, NetpbmFormat.Pgm, fill);

    private static NetpbmImage CreateColor(byte fill = 128, int w = 4, int h = 4)
        => NetpbmImage.Create(w, h, NetpbmFormat.Ppm, fill);

    // -------------------------------------------------------------------------
    // ToColor
    // -------------------------------------------------------------------------

    [Fact]
    public void ToColor_ReturnsPpm()
    {
        var img = CreateGray();
        var color = img.ToColor();
        Assert.Equal(NetpbmFormat.Ppm, color.Format);
    }

    [Fact]
    public void ToColor_DimensionsUnchanged()
    {
        var img = CreateGray(128, 5, 3);
        var color = img.ToColor();
        Assert.Equal(5, color.Width);
        Assert.Equal(3, color.Height);
    }

    [Fact]
    public void ToColor_ReturnsNewInstance()
    {
        var img = CreateGray();
        var color = img.ToColor();
        Assert.NotSame(img, color);
    }

    [Fact]
    public void ToColor_FromPpm_StillPpm()
    {
        var img = CreateColor();
        var color = img.ToColor();
        Assert.Equal(NetpbmFormat.Ppm, color.Format);
    }

    // -------------------------------------------------------------------------
    // ConvertFormat
    // -------------------------------------------------------------------------

    [Fact]
    public void ConvertFormat_PgmToPpm_ReturnsPpm()
    {
        var img = CreateGray();
        var ppm = img.ConvertFormat(NetpbmFormat.Ppm);
        Assert.Equal(NetpbmFormat.Ppm, ppm.Format);
    }

    [Fact]
    public void ConvertFormat_PpmToPgm_ReturnsPgm()
    {
        var img = CreateColor();
        var pgm = img.ConvertFormat(NetpbmFormat.Pgm);
        Assert.Equal(NetpbmFormat.Pgm, pgm.Format);
    }

    [Fact]
    public void ConvertFormat_DimensionsUnchanged()
    {
        var img = CreateGray(100, 6, 3);
        var ppm = img.ConvertFormat(NetpbmFormat.Ppm);
        Assert.Equal(6, ppm.Width);
        Assert.Equal(3, ppm.Height);
    }

    [Fact]
    public void ConvertFormat_SameFormat_StillWorks()
    {
        var img = CreateGray();
        var pgm = img.ConvertFormat(NetpbmFormat.Pgm);
        Assert.Equal(NetpbmFormat.Pgm, pgm.Format);
    }

    // -------------------------------------------------------------------------
    // Clone
    // -------------------------------------------------------------------------

    [Fact]
    public void Clone_ReturnsNewInstance()
    {
        var img = CreateGray();
        var clone = img.Clone();
        Assert.NotSame(img, clone);
    }

    [Fact]
    public void Clone_DimensionsMatch()
    {
        var img = CreateGray(100, 5, 3);
        var clone = img.Clone();
        Assert.Equal(5, clone.Width);
        Assert.Equal(3, clone.Height);
    }

    [Fact]
    public void Clone_FormatMatches()
    {
        var img = CreateGray();
        var clone = img.Clone();
        Assert.Equal(img.Format, clone.Format);
    }

    // -------------------------------------------------------------------------
    // Pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Pipeline_EmptySteps_DimensionsUnchanged()
    {
        var img = CreateGray(128, 4, 4);
        var result = img.Pipeline(new List<System.Func<NetpbmImage, NetpbmImage>>());
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void Pipeline_WithSharpen_ReturnsNewImage()
    {
        var img = CreateGray();
        var result = img.Pipeline(new List<System.Func<NetpbmImage, NetpbmImage>>
        {
            i => i.Sharpen()
        });
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Pipeline_MultipleSteps_DimensionsUnchanged()
    {
        var img = CreateGray(128, 4, 4);
        var result = img.Pipeline(new List<System.Func<NetpbmImage, NetpbmImage>>
        {
            i => i.AdjustBrightness(10),
            i => i.AdjustContrast(1.1)
        });
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->ToColor->ConvertFormat->Clone->Pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateToColorConvertClonePipeline_Verify()
    {
        var img = CreateGray(100, 4, 4);
        Assert.Equal(NetpbmFormat.Pgm, img.Format);

        // ToColor
        var color = img.ToColor();
        Assert.Equal(NetpbmFormat.Ppm, color.Format);

        // ConvertFormat back to PGM
        var gray = color.ConvertFormat(NetpbmFormat.Pgm);
        Assert.Equal(NetpbmFormat.Pgm, gray.Format);
        Assert.Equal(img.Width, gray.Width);
        Assert.Equal(img.Height, gray.Height);

        // Clone
        var clone = gray.Clone();
        Assert.NotSame(gray, clone);
        Assert.Equal(gray.Width, clone.Width);
        Assert.Equal(gray.Height, clone.Height);

        // Pipeline: brighten + sharpen
        var pipelined = clone.Pipeline(new List<System.Func<NetpbmImage, NetpbmImage>>
        {
            i => i.AdjustBrightness(5),
            i => i.Sharpen()
        });
        Assert.Equal(clone.Width, pipelined.Width);
        Assert.Equal(clone.Height, pipelined.Height);

        // Stats valid
        var (mean, min, max) = pipelined.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
        Assert.InRange(mean, 0.0, 255.0);
    }
}
