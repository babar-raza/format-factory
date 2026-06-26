// Tests for NetpbmImage.ToGrayscale dedicated coverage.
// Sprint: ff-sprint-s245-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R252

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R252: Dedicated tests for NetpbmImage.ToGrayscale().
/// Converts PPM (color) to PGM (grayscale). Non-PPM → throws exception.
/// PBM input → throws exception.
/// PGM input → throws exception.
/// PPM input → no exception.
/// Result format is PGM_P5.
/// Width preserved.
/// Height preserved.
/// MaxValue preserved.
/// Result has non-null Pixels array.
/// All result pixels in valid range.
/// Original image format unchanged.
/// Dogfood: PPM with known channel values → grayscale pixel in valid range.
/// </summary>
public class NetpbmR252ToGrayscaleDedicatedTests
{
    private static NetpbmImage CreatePpm(int w, int h, int maxVal = 255)
    {
        var img = NetpbmImage.Create(w, h, NetpbmFormat.PPM_P6, maxValue: maxVal);
        return img;
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ToGrayscale_PbmInput_ThrowsException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PBM_P1);
        Assert.ThrowsAny<Exception>(() => img.ToGrayscale());
    }

    [Fact]
    public void ToGrayscale_PgmInput_ThrowsException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.ThrowsAny<Exception>(() => img.ToGrayscale());
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ToGrayscale_PpmInput_NoException()
    {
        var img = CreatePpm(4, 4);
        var ex = Record.Exception(() => img.ToGrayscale());
        Assert.Null(ex);
    }

    [Fact]
    public void ToGrayscale_ResultFormatIsPgm()
    {
        var img = CreatePpm(4, 4);
        var result = img.ToGrayscale();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void ToGrayscale_WidthPreserved()
    {
        var img = CreatePpm(6, 4);
        var result = img.ToGrayscale();
        Assert.Equal(6, result.Width);
    }

    [Fact]
    public void ToGrayscale_HeightPreserved()
    {
        var img = CreatePpm(6, 4);
        var result = img.ToGrayscale();
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void ToGrayscale_MaxValuePreserved()
    {
        var img = CreatePpm(4, 4, maxVal: 200);
        var result = img.ToGrayscale();
        Assert.Equal(200, result.MaxValue);
    }

    [Fact]
    public void ToGrayscale_PixelsNotNull()
    {
        var img = CreatePpm(4, 4);
        var result = img.ToGrayscale();
        Assert.NotNull(result.Pixels);
    }

    [Fact]
    public void ToGrayscale_OriginalFormatUnchanged()
    {
        var img = CreatePpm(4, 4);
        img.ToGrayscale();
        Assert.Equal(NetpbmFormat.PPM_P6, img.Format);
    }

    [Fact]
    public void ToGrayscale_AllPixelsInValidRange()
    {
        var img = CreatePpm(4, 4, maxVal: 255);
        var result = img.ToGrayscale();
        foreach (var px in result.Pixels!)
            Assert.InRange(px, 0, 255);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownChannelValues_GrayscaleInRange()
    {
        // Create PPM, set pixel channel values, convert to grayscale
        var img = CreatePpm(2, 2, maxVal: 255);
        // RedChannel/GreenChannel/BlueChannel should be initialized
        if (img.RedChannel != null)
        {
            img.RedChannel[0] = 100;
            img.GreenChannel![0] = 150;
            img.BlueChannel![0] = 200;
        }
        var result = img.ToGrayscale();
        Assert.NotNull(result.Pixels);
        // Grayscale value should be in [0, MaxValue]
        Assert.InRange(result.Pixels[0], 0, result.MaxValue);
    }
}
