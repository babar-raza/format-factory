// Tests for NetpbmImage.ApplySharpen dedicated coverage.
// Sprint: ff-sprint-s263-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R270

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R270: Dedicated tests for NetpbmImage.ApplySharpen().
/// ApplySharpen applies a sharpening filter in-place (void).
/// Width/height/format/MaxValue preserved.
/// All pixels remain in [0, MaxValue] after sharpening.
/// Valid PGM image: no exception.
/// Called twice: still valid.
/// Uniform image: no exception.
/// Dogfood: set pixels, apply sharpen, dims and range preserved.
/// Dogfood: uniform image, sharpen keeps pixels in range.
/// </summary>
public class NetpbmR270ApplySharpenerDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplySharpen_ValidImage_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 128);
        img.SetPixel(2, 2, 200);
        var ex = Record.Exception(() => img.ApplySharpen());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplySharpen_AllPixelsRemainInRange()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(2, 2, 150);
        img.SetPixel(4, 4, 230);
        img.ApplySharpen();
        for (int c = 0; c < 5; c++)
            for (int r = 0; r < 5; r++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }

    [Fact]
    public void ApplySharpen_UniformImage_NoException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int c = 0; c < 3; c++)
            for (int r = 0; r < 3; r++)
                img.SetPixel(c, r, 100);
        var ex = Record.Exception(() => img.ApplySharpen());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplySharpen_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.ApplySharpen();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void ApplySharpen_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.ApplySharpen();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void ApplySharpen_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.ApplySharpen();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void ApplySharpen_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 180);
        img.ApplySharpen();
        Assert.Equal(180, img.MaxValue);
    }

    [Fact]
    public void ApplySharpen_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 128);
        img.ApplySharpen();
        var ex = Record.Exception(() => img.ApplySharpen());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetPixelsThenSharpen_DimsAndRangePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 20);
        img.SetPixel(1, 1, 100);
        img.SetPixel(2, 2, 180);
        img.SetPixel(3, 3, 240);
        img.ApplySharpen();
        Assert.Equal(4, img.Width);
        Assert.Equal(4, img.Height);
        for (int c = 0; c < 4; c++)
            for (int r = 0; r < 4; r++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }

    [Fact]
    public void DogfoodPipeline_UniformSharpen_PixelsInRange()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int c = 0; c < 3; c++)
            for (int r = 0; r < 3; r++)
                img.SetPixel(c, r, 200);
        img.ApplySharpen();
        for (int c = 0; c < 3; c++)
            for (int r = 0; r < 3; r++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }
}
