// Tests for NetpbmImage.GetSharpness dedicated coverage.
// Sprint: ff-sprint-s357-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R370

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R370: Dedicated tests for NetpbmImage.GetSharpness().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetSharpness.
/// Height unchanged after GetSharpness.
/// Format unchanged after GetSharpness.
/// MaxValue unchanged after GetSharpness.
/// Uniform image returns 0.0.
/// Idempotent (called twice same result).
/// Dogfood: high-frequency pattern returns positive sharpness.
/// Dogfood: all-zero image returns 0.0.
/// </summary>
public class NetpbmR370GetSharpenessDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSharpness_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        double sharpness = img.GetSharpness();
        Assert.True(sharpness >= 0.0);
    }

    [Fact]
    public void GetSharpness_ResultIsNonNegative()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM, 255);
        double sharpness = img.GetSharpness();
        Assert.True(sharpness >= 0.0);
    }

    [Fact]
    public void GetSharpness_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetSharpness();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetSharpness_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetSharpness();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetSharpness_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        var before = img.Format;
        _ = img.GetSharpness();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetSharpness_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 200);
        int before = img.MaxValue;
        _ = img.GetSharpness();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetSharpness_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(100);
        double sharpness = img.GetSharpness();
        Assert.Equal(0.0, sharpness, precision: 5);
    }

    [Fact]
    public void GetSharpness_Idempotent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM, 255);
        img.FillWithValue(50);
        double first = img.GetSharpness();
        double second = img.GetSharpness();
        Assert.Equal(first, second, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CheckerboardPattern_ReturnsPositive()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : 255);
        double sharpness = img.GetSharpness();
        Assert.True(sharpness > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(0);
        double sharpness = img.GetSharpness();
        Assert.Equal(0.0, sharpness, precision: 5);
    }
}
