// Tests for NetpbmImage.GetSaturationLevel dedicated coverage.
// Sprint: ff-sprint-s341-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R354

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R354: Dedicated tests for NetpbmImage.GetSaturationLevel().
/// Valid image ok.
/// Returns value in [0.0, 1.0].
/// Width unchanged after GetSaturationLevel.
/// Height unchanged after GetSaturationLevel.
/// Format unchanged after GetSaturationLevel.
/// MaxValue unchanged after GetSaturationLevel.
/// All-zero image returns 0.0 saturation.
/// Idempotent (called twice same result).
/// Dogfood: uniform image returns 0.0 saturation.
/// Dogfood: mixed image returns value in [0.0, 1.0].
/// </summary>
public class NetpbmR354GetSaturationLevelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSaturationLevel_ValidImage_Ok()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        var ex = Record.Exception(() => img.GetSaturationLevel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSaturationLevel_ReturnsInRange()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        double saturation = img.GetSaturationLevel();
        Assert.InRange(saturation, 0.0, 1.0);
    }

    [Fact]
    public void GetSaturationLevel_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Width;
        _ = img.GetSaturationLevel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetSaturationLevel_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Height;
        _ = img.GetSaturationLevel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetSaturationLevel_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        string before = img.Format;
        _ = img.GetSaturationLevel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetSaturationLevel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.MaxValue;
        _ = img.GetSaturationLevel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetSaturationLevel_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        // All pixels default to 0
        double saturation = img.GetSaturationLevel();
        Assert.Equal(0.0, saturation, precision: 10);
    }

    [Fact]
    public void GetSaturationLevel_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        img.FillWithValue(100);
        double first = img.GetSaturationLevel();
        double second = img.GetSaturationLevel();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UniformImage_ReturnsZeroSaturation()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.FillWithValue(128);
        double saturation = img.GetSaturationLevel();
        Assert.Equal(0.0, saturation, precision: 10);
    }

    [Fact]
    public void DogfoodPipeline_MixedImage_InRange()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 128);
        img.SetPixel(2, 0, 255);
        double saturation = img.GetSaturationLevel();
        Assert.InRange(saturation, 0.0, 1.0);
    }
}
