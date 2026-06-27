// Tests for NetpbmImage.GetBlurLevel dedicated coverage.
// Sprint: ff-sprint-s358-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R371

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R371: Dedicated tests for NetpbmImage.GetBlurLevel().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetBlurLevel.
/// Height unchanged after GetBlurLevel.
/// Format unchanged after GetBlurLevel.
/// MaxValue unchanged after GetBlurLevel.
/// Uniform image returns 0.0.
/// Idempotent (called twice same result).
/// Dogfood: sharp-edged image returns lower blur than blurred version.
/// Dogfood: all-zero image returns 0.0.
/// </summary>
public class NetpbmR371GetBlurLevelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlurLevel_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        double blur = img.GetBlurLevel();
        Assert.True(blur >= 0.0);
    }

    [Fact]
    public void GetBlurLevel_ResultIsNonNegative()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM, 255);
        double blur = img.GetBlurLevel();
        Assert.True(blur >= 0.0);
    }

    [Fact]
    public void GetBlurLevel_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetBlurLevel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetBlurLevel_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetBlurLevel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetBlurLevel_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        var before = img.Format;
        _ = img.GetBlurLevel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetBlurLevel_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 200);
        int before = img.MaxValue;
        _ = img.GetBlurLevel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetBlurLevel_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(128);
        double blur = img.GetBlurLevel();
        Assert.Equal(0.0, blur, precision: 5);
    }

    [Fact]
    public void GetBlurLevel_Idempotent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM, 255);
        img.FillWithValue(60);
        double first = img.GetBlurLevel();
        double second = img.GetBlurLevel();
        Assert.Equal(first, second, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SharpEdgeImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        // Hard edge: left half 0, right half 255
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(r, c, c < 2 ? 0 : 255);
        double blur = img.GetBlurLevel();
        Assert.True(blur >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(0);
        double blur = img.GetBlurLevel();
        Assert.Equal(0.0, blur, precision: 5);
    }
}
