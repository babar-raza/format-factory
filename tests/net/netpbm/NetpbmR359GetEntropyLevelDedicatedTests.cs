// Tests for NetpbmImage.GetEntropyLevel dedicated coverage.
// Sprint: ff-sprint-s346-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R359

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R359: Dedicated tests for NetpbmImage.GetEntropyLevel().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetEntropyLevel.
/// Height unchanged after GetEntropyLevel.
/// Format unchanged after GetEntropyLevel.
/// MaxValue unchanged after GetEntropyLevel.
/// All-zero image returns 0.0.
/// Uniform image returns 0.0.
/// Idempotent (called twice same result).
/// Dogfood: varied pixel values returns positive entropy.
/// </summary>
public class NetpbmR359GetEntropyLevelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEntropyLevel_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        double entropy = img.GetEntropyLevel();
        Assert.True(entropy >= 0.0);
    }

    [Fact]
    public void GetEntropyLevel_ResultIsNonNegative()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM, 255);
        double entropy = img.GetEntropyLevel();
        Assert.True(entropy >= 0.0);
    }

    [Fact]
    public void GetEntropyLevel_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetEntropyLevel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetEntropyLevel_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetEntropyLevel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetEntropyLevel_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        var before = img.Format;
        _ = img.GetEntropyLevel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetEntropyLevel_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 200);
        int before = img.MaxValue;
        _ = img.GetEntropyLevel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetEntropyLevel_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(0);
        double entropy = img.GetEntropyLevel();
        Assert.Equal(0.0, entropy, precision: 5);
    }

    [Fact]
    public void GetEntropyLevel_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(128);
        double entropy = img.GetEntropyLevel();
        Assert.Equal(0.0, entropy, precision: 5);
    }

    [Fact]
    public void GetEntropyLevel_Idempotent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM, 255);
        img.FillWithValue(64);
        double first = img.GetEntropyLevel();
        double second = img.GetEntropyLevel();
        Assert.Equal(first, second, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_VariedPixelValues_ReturnsPositiveEntropy()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        // Alternate between 0 and 255 for maximum entropy
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : 255);
        double entropy = img.GetEntropyLevel();
        Assert.True(entropy > 0.0);
    }
}
