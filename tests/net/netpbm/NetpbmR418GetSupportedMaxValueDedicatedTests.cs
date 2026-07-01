// Tests for NetpbmImage.GetSupportedMaxValue dedicated coverage.
// Sprint: ff-sprint-s400-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R418

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R418: Dedicated tests for NetpbmImage.GetSupportedMaxValue().
/// PBM supported max is 1.
/// PGM supported max is positive.
/// PPM supported max is positive.
/// Width unchanged after GetSupportedMaxValue.
/// Height unchanged after GetSupportedMaxValue.
/// Format unchanged after GetSupportedMaxValue.
/// MaxValue unchanged after GetSupportedMaxValue.
/// Idempotent (called twice same result).
/// Result positive for all formats.
/// Result ≥ actual MaxValue.
/// </summary>
public class NetpbmR418GetSupportedMaxValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSupportedMaxValue_PBM_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        int maxVal = img.GetSupportedMaxValue();
        Assert.Equal(1, maxVal);
    }

    [Fact]
    public void GetSupportedMaxValue_PGM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int maxVal = img.GetSupportedMaxValue();
        Assert.True(maxVal > 0);
    }

    [Fact]
    public void GetSupportedMaxValue_PPM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int maxVal = img.GetSupportedMaxValue();
        Assert.True(maxVal > 0);
    }

    [Fact]
    public void GetSupportedMaxValue_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetSupportedMaxValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetSupportedMaxValue_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetSupportedMaxValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetSupportedMaxValue_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetSupportedMaxValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetSupportedMaxValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetSupportedMaxValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetSupportedMaxValue_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetSupportedMaxValue();
        int second = img.GetSupportedMaxValue();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ResultPositiveAllFormats()
    {
        foreach (var fmt in new[] { NetpbmFormat.PBM, NetpbmFormat.PGM, NetpbmFormat.PPM })
        {
            var img = NetpbmImage.CreateNew(4, 4, fmt);
            Assert.True(img.GetSupportedMaxValue() > 0);
        }
    }

    [Fact]
    public void DogfoodPipeline_SupportedMaxGeActualMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetSupportedMaxValue() >= img.MaxValue);
    }
}
