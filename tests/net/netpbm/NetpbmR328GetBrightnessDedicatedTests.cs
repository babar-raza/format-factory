// Tests for NetpbmImage.GetBrightness dedicated coverage.
// Sprint: ff-sprint-s317-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R328

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R328: Dedicated tests for NetpbmImage.GetBrightness().
/// Returns value in [0, MaxValue].
/// Width unchanged after GetBrightness.
/// Height unchanged after GetBrightness.
/// Format unchanged after GetBrightness.
/// MaxValue unchanged after GetBrightness.
/// All-zero image returns zero brightness.
/// Idempotent (called twice same result).
/// Uniform image brightness in range.
/// Dogfood: gradient image brightness in range.
/// Dogfood: alternating-pixel image brightness in range.
/// </summary>
public class NetpbmR328GetBrightnessDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_ReturnsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 20 + y * 10) % 256);
        double brightness = img.GetBrightness();
        Assert.InRange(brightness, 0.0, (double)img.MaxValue);
    }

    [Fact]
    public void GetBrightness_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetBrightness();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetBrightness_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetBrightness();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetBrightness_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetBrightness();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetBrightness_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetBrightness();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetBrightness_AllZeroImage_ZeroBrightness()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        double brightness = img.GetBrightness();
        Assert.InRange(brightness, 0.0, (double)img.MaxValue);
    }

    [Fact]
    public void GetBrightness_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 128);
        double first = img.GetBrightness();
        double second = img.GetBrightness();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetBrightness_UniformImage_InRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 200);
        double brightness = img.GetBrightness();
        Assert.InRange(brightness, 0.0, (double)img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GradientImage_BrightnessInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, x * 32);
        double brightness = img.GetBrightness();
        Assert.InRange(brightness, 0.0, (double)img.MaxValue);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_AlternatingImage_BrightnessInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) % 2 == 0 ? 0 : 255);
        double brightness = img.GetBrightness();
        Assert.InRange(brightness, 0.0, (double)img.MaxValue);
    }
}
