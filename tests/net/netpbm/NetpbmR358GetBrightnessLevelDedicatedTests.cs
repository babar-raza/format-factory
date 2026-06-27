// Tests for NetpbmImage.GetBrightnessLevel dedicated coverage.
// Sprint: ff-sprint-s345-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R358

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R358: Dedicated tests for NetpbmImage.GetBrightnessLevel().
/// Valid image ok.
/// Returns value in [0.0, 1.0].
/// Width unchanged after GetBrightnessLevel.
/// Height unchanged after GetBrightnessLevel.
/// Format unchanged after GetBrightnessLevel.
/// MaxValue unchanged after GetBrightnessLevel.
/// All-zero image returns 0.0 brightness.
/// Full-brightness image returns 1.0 brightness.
/// Idempotent (called twice same result).
/// Dogfood: half-brightness image returns ~0.5.
/// </summary>
public class NetpbmR358GetBrightnessLevelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightnessLevel_ValidImage_Ok()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        var ex = Record.Exception(() => img.GetBrightnessLevel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBrightnessLevel_ReturnsInRange()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        double brightness = img.GetBrightnessLevel();
        Assert.InRange(brightness, 0.0, 1.0);
    }

    [Fact]
    public void GetBrightnessLevel_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Width;
        _ = img.GetBrightnessLevel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetBrightnessLevel_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Height;
        _ = img.GetBrightnessLevel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetBrightnessLevel_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        string before = img.Format;
        _ = img.GetBrightnessLevel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetBrightnessLevel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.MaxValue;
        _ = img.GetBrightnessLevel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetBrightnessLevel_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        double brightness = img.GetBrightnessLevel();
        Assert.Equal(0.0, brightness, precision: 10);
    }

    [Fact]
    public void GetBrightnessLevel_FullBrightnessImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.FillWithValue(255);
        double brightness = img.GetBrightnessLevel();
        Assert.Equal(1.0, brightness, precision: 10);
    }

    [Fact]
    public void GetBrightnessLevel_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        img.FillWithValue(128);
        double first = img.GetBrightnessLevel();
        double second = img.GetBrightnessLevel();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HalfBrightnessImage_NearHalf()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.FillWithValue(128); // ~128/255 ≈ 0.502
        double brightness = img.GetBrightnessLevel();
        Assert.InRange(brightness, 0.4, 0.6);
    }
}
