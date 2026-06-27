// Tests for NetpbmImage.GetContrastRatio dedicated coverage.
// Sprint: ff-sprint-s342-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R355

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R355: Dedicated tests for NetpbmImage.GetContrastRatio().
/// Valid image ok.
/// Returns non-negative value.
/// Width unchanged after GetContrastRatio.
/// Height unchanged after GetContrastRatio.
/// Format unchanged after GetContrastRatio.
/// MaxValue unchanged after GetContrastRatio.
/// All-zero image returns 0.0 contrast.
/// Uniform non-zero image returns 0.0 contrast.
/// Idempotent (called twice same result).
/// Dogfood: high-contrast image (0 and MaxValue) returns positive contrast.
/// </summary>
public class NetpbmR355GetContrastRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContrastRatio_ValidImage_Ok()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        var ex = Record.Exception(() => img.GetContrastRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContrastRatio_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        double ratio = img.GetContrastRatio();
        Assert.True(ratio >= 0.0);
    }

    [Fact]
    public void GetContrastRatio_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Width;
        _ = img.GetContrastRatio();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetContrastRatio_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Height;
        _ = img.GetContrastRatio();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetContrastRatio_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        string before = img.Format;
        _ = img.GetContrastRatio();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetContrastRatio_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.MaxValue;
        _ = img.GetContrastRatio();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetContrastRatio_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        double ratio = img.GetContrastRatio();
        Assert.Equal(0.0, ratio, precision: 10);
    }

    [Fact]
    public void GetContrastRatio_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.FillWithValue(128);
        double ratio = img.GetContrastRatio();
        Assert.Equal(0.0, ratio, precision: 10);
    }

    [Fact]
    public void GetContrastRatio_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 255);
        double first = img.GetContrastRatio();
        double second = img.GetContrastRatio();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HighContrastImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        // Half dark, half bright
        for (int x = 0; x < 2; x++)
            for (int y = 0; y < 4; y++)
                img.SetPixel(x, y, 0);
        for (int x = 2; x < 4; x++)
            for (int y = 0; y < 4; y++)
                img.SetPixel(x, y, 255);
        double ratio = img.GetContrastRatio();
        Assert.True(ratio > 0.0);
    }
}
