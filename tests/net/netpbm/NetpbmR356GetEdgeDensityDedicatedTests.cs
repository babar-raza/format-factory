// Tests for NetpbmImage.GetEdgeDensity dedicated coverage.
// Sprint: ff-sprint-s343-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R356

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R356: Dedicated tests for NetpbmImage.GetEdgeDensity().
/// Valid image ok.
/// Returns non-negative value.
/// Width unchanged after GetEdgeDensity.
/// Height unchanged after GetEdgeDensity.
/// Format unchanged after GetEdgeDensity.
/// MaxValue unchanged after GetEdgeDensity.
/// All-zero image returns 0.0 edge density.
/// Uniform image returns 0.0 edge density.
/// Idempotent (called twice same result).
/// Dogfood: image with sharp edges returns positive edge density.
/// </summary>
public class NetpbmR356GetEdgeDensityDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEdgeDensity_ValidImage_Ok()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        var ex = Record.Exception(() => img.GetEdgeDensity());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEdgeDensity_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        double density = img.GetEdgeDensity();
        Assert.True(density >= 0.0);
    }

    [Fact]
    public void GetEdgeDensity_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Width;
        _ = img.GetEdgeDensity();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetEdgeDensity_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Height;
        _ = img.GetEdgeDensity();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetEdgeDensity_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        string before = img.Format;
        _ = img.GetEdgeDensity();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetEdgeDensity_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.MaxValue;
        _ = img.GetEdgeDensity();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetEdgeDensity_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        double density = img.GetEdgeDensity();
        Assert.Equal(0.0, density, precision: 10);
    }

    [Fact]
    public void GetEdgeDensity_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.FillWithValue(200);
        double density = img.GetEdgeDensity();
        Assert.Equal(0.0, density, precision: 10);
    }

    [Fact]
    public void GetEdgeDensity_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        img.SetPixel(0, 0, 255);
        img.SetPixel(1, 0, 0);
        double first = img.GetEdgeDensity();
        double second = img.GetEdgeDensity();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SharpEdgeImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        // Create checkerboard pattern for maximum edges
        for (int x = 0; x < 4; x++)
            for (int y = 0; y < 4; y++)
                img.SetPixel(x, y, (x + y) % 2 == 0 ? 0 : 255);
        double density = img.GetEdgeDensity();
        Assert.True(density > 0.0);
    }
}
