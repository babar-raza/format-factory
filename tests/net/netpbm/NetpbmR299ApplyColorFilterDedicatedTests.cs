// Tests for NetpbmImage.ApplyColorFilter dedicated coverage.
// Sprint: ff-sprint-s291-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R299

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R299: Dedicated tests for NetpbmImage.ApplyColorFilter(r, g, b).
/// Valid call no exception.
/// All pixels in [0, MaxValue] after ApplyColorFilter.
/// Width unchanged after ApplyColorFilter.
/// Height unchanged after ApplyColorFilter.
/// Format unchanged after ApplyColorFilter.
/// MaxValue unchanged after ApplyColorFilter.
/// Called twice no exception.
/// All-zero filter no exception.
/// Dogfood: standard filter coefficients no exception.
/// Dogfood: mixed image filtered pixels in range.
/// </summary>
public class NetpbmR299ApplyColorFilterDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyColorFilter_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        var ex = Record.Exception(() => img.ApplyColorFilter(0.5, 0.5, 0.5));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyColorFilter_AllPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(2, 2, 200);
        img.ApplyColorFilter(0.3, 0.6, 0.1);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void ApplyColorFilter_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.ApplyColorFilter(0.5, 0.5, 0.5);
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void ApplyColorFilter_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.ApplyColorFilter(0.5, 0.5, 0.5);
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void ApplyColorFilter_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.ApplyColorFilter(0.5, 0.5, 0.5);
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void ApplyColorFilter_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.ApplyColorFilter(0.5, 0.5, 0.5);
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void ApplyColorFilter_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        img.ApplyColorFilter(0.5, 0.5, 0.5);
        var ex = Record.Exception(() => img.ApplyColorFilter(0.2, 0.5, 0.3));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyColorFilter_AllZeroFilter_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.ApplyColorFilter(0.0, 0.0, 0.0));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StandardLuminanceCoefficients_NoException()
    {
        // Standard luminance: 0.2126 R + 0.7152 G + 0.0722 B
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 200);
        var ex = Record.Exception(() => img.ApplyColorFilter(0.2126, 0.7152, 0.0722));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_MixedImage_FilteredPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 0, 150);
        img.SetPixel(2, 0, 200);
        img.ApplyColorFilter(0.4, 0.4, 0.2);
        for (int x = 0; x < 3; x++)
            Assert.InRange(img.GetPixel(x, 0), 0, img.MaxValue);
    }
}
