// Tests for NetpbmImage.GetAverageBrightness dedicated coverage.
// Sprint: ff-sprint-s355-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R368

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R368: Dedicated tests for NetpbmImage.GetAverageBrightness().
/// Valid image returns ok.
/// Result is in [0.0, 1.0].
/// Width unchanged after GetAverageBrightness.
/// Height unchanged after GetAverageBrightness.
/// Format unchanged after GetAverageBrightness.
/// MaxValue unchanged after GetAverageBrightness.
/// All-zero image returns 0.0.
/// All-max image returns 1.0.
/// Idempotent (called twice same result).
/// Dogfood: half-filled image returns approx 0.5.
/// </summary>
public class NetpbmR368GetAverageBrightnessDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAverageBrightness_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        double brightness = img.GetAverageBrightness();
        Assert.InRange(brightness, 0.0, 1.0);
    }

    [Fact]
    public void GetAverageBrightness_ResultInRange()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM, 255);
        double brightness = img.GetAverageBrightness();
        Assert.InRange(brightness, 0.0, 1.0);
    }

    [Fact]
    public void GetAverageBrightness_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetAverageBrightness();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetAverageBrightness_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetAverageBrightness();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetAverageBrightness_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        var before = img.Format;
        _ = img.GetAverageBrightness();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetAverageBrightness_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 200);
        int before = img.MaxValue;
        _ = img.GetAverageBrightness();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetAverageBrightness_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(0);
        double brightness = img.GetAverageBrightness();
        Assert.Equal(0.0, brightness, precision: 5);
    }

    [Fact]
    public void GetAverageBrightness_AllMaxImage_ReturnsOne()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(255);
        double brightness = img.GetAverageBrightness();
        Assert.Equal(1.0, brightness, precision: 5);
    }

    [Fact]
    public void GetAverageBrightness_Idempotent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM, 255);
        img.FillWithValue(128);
        double first = img.GetAverageBrightness();
        double second = img.GetAverageBrightness();
        Assert.Equal(first, second, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HalfFilledImage_ReturnsApproxHalf()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(128);
        double brightness = img.GetAverageBrightness();
        Assert.InRange(brightness, 0.4, 0.6);
    }
}
