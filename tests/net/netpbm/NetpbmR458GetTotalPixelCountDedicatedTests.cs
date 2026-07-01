// Tests for NetpbmImage.GetTotalPixelCount dedicated coverage.
// Sprint: ff-sprint-s440-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R458

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R458: Dedicated tests for NetpbmImage.GetTotalPixelCount().
/// Returns positive int for PBM/PGM/PPM.
/// Equals Width * Height.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM/PPM returns 16.
/// </summary>
public class NetpbmR458GetTotalPixelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTotalPixelCount_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int val = img.GetTotalPixelCount();
        Assert.True(val > 0);
    }

    [Fact]
    public void GetTotalPixelCount_EqualsWidthTimesHeight()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int val = img.GetTotalPixelCount();
        Assert.Equal(img.Width * img.Height, val);
    }

    [Fact]
    public void GetTotalPixelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetTotalPixelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetTotalPixelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetTotalPixelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetTotalPixelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetTotalPixelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetTotalPixelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetTotalPixelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetTotalPixelCount_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int first = img.GetTotalPixelCount();
        int second = img.GetTotalPixelCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTotalPixelCount_PBM_Positive()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        int val = img.GetTotalPixelCount();
        Assert.True(val > 0);
    }

    [Fact]
    public void GetTotalPixelCount_PPM_Positive()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        int val = img.GetTotalPixelCount();
        Assert.True(val > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_Returns16()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.Equal(16, img.GetTotalPixelCount());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_Returns16()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.Equal(16, img.GetTotalPixelCount());
    }
}
