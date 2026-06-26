// Tests for NetpbmImage.ApplyEmboss dedicated coverage.
// Sprint: ff-sprint-s266-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R273

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R273: Dedicated tests for NetpbmImage.ApplyEmboss().
/// ApplyEmboss applies an emboss effect in-place (void).
/// Width/height/format/MaxValue preserved.
/// All pixels remain in [0, MaxValue] after emboss.
/// Valid PGM image: no exception.
/// Uniform image: no exception.
/// Called twice: no exception.
/// Dogfood: set pixels, apply emboss, dims and range preserved.
/// Dogfood: uniform image, emboss keeps pixels in range.
/// </summary>
public class NetpbmR273ApplyEmbossDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyEmboss_ValidImage_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 120);
        img.SetPixel(2, 2, 200);
        var ex = Record.Exception(() => img.ApplyEmboss());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyEmboss_AllPixelsRemainInRange()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 30);
        img.SetPixel(2, 2, 130);
        img.SetPixel(4, 4, 220);
        img.ApplyEmboss();
        for (int c = 0; c < 5; c++)
            for (int r = 0; r < 5; r++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }

    [Fact]
    public void ApplyEmboss_UniformImage_NoException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int c = 0; c < 3; c++)
            for (int r = 0; r < 3; r++)
                img.SetPixel(c, r, 128);
        var ex = Record.Exception(() => img.ApplyEmboss());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyEmboss_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.ApplyEmboss();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void ApplyEmboss_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.ApplyEmboss();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void ApplyEmboss_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.ApplyEmboss();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void ApplyEmboss_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 200);
        img.ApplyEmboss();
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void ApplyEmboss_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(2, 2, 100);
        img.ApplyEmboss();
        var ex = Record.Exception(() => img.ApplyEmboss());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetPixelsThenEmboss_DimsAndRangePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 10);
        img.SetPixel(1, 1, 80);
        img.SetPixel(2, 2, 160);
        img.SetPixel(3, 3, 240);
        img.ApplyEmboss();
        Assert.Equal(4, img.Width);
        Assert.Equal(4, img.Height);
        for (int c = 0; c < 4; c++)
            for (int r = 0; r < 4; r++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }

    [Fact]
    public void DogfoodPipeline_UniformEmboss_PixelsInRange()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int c = 0; c < 3; c++)
            for (int r = 0; r < 3; r++)
                img.SetPixel(c, r, 180);
        img.ApplyEmboss();
        for (int c = 0; c < 3; c++)
            for (int r = 0; r < 3; r++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }
}
