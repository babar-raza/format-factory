// Tests for NetpbmImage.GetModePixelValue dedicated coverage.
// Sprint: ff-sprint-s421-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R439

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R439: Dedicated tests for NetpbmImage.GetModePixelValue().
/// Returns non-negative value.
/// Result within [0, MaxValue].
/// Width unchanged after GetModePixelValue.
/// Height unchanged after GetModePixelValue.
/// Format unchanged after GetModePixelValue.
/// MaxValue unchanged after GetModePixelValue.
/// Idempotent (called twice same result).
/// PBM mode non-negative.
/// PGM mode non-negative.
/// PPM mode non-negative.
/// Dogfood: 4x4 PGM mode within MaxValue.
/// </summary>
public class NetpbmR439GetModePixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetModePixelValue_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int mode = img.GetModePixelValue();
        Assert.True(mode >= 0);
    }

    [Fact]
    public void GetModePixelValue_WithinMaxValueRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int mode = img.GetModePixelValue();
        Assert.True(mode <= img.MaxValue);
    }

    [Fact]
    public void GetModePixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetModePixelValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetModePixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetModePixelValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetModePixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetModePixelValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetModePixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetModePixelValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetModePixelValue_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetModePixelValue();
        int second = img.GetModePixelValue();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetModePixelValue_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetModePixelValue() >= 0);
    }

    [Fact]
    public void GetModePixelValue_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetModePixelValue() >= 0);
    }

    [Fact]
    public void GetModePixelValue_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetModePixelValue() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ModeWithinMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int mode = img.GetModePixelValue();
        Assert.True(mode >= 0 && mode <= img.MaxValue);
    }
}
