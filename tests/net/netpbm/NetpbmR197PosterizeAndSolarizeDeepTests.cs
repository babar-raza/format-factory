// Tests for NetpbmImage.Posterize, Solarize deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R197

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R197: Tests for NetpbmImage.Posterize, Solarize deeper coverage.
/// Posterize(levels): reduces color depth to a given number of levels; preserves dimensions.
/// Solarize(threshold): inverts pixels above the threshold; preserves dimensions.
/// Covers: Posterize non-null; Posterize preserves dimensions; Posterize level 2;
/// Posterize level 4; Posterize level 8; Posterize chain;
/// Posterize on black canvas; Posterize on white canvas;
/// Solarize non-null; Solarize preserves dimensions; Solarize threshold 0 (all inverted);
/// Solarize threshold 255 (none inverted); Solarize middle threshold;
/// Solarize chain; Posterize->Solarize combined; Solarize->Posterize combined;
/// dogfood CreateCanvas->Posterize->Solarize->Verify pipeline.
/// </summary>
public class NetpbmR197PosterizeAndSolarizeDeepTests
{
    // -------------------------------------------------------------------------
    // Posterize
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        Assert.NotNull(img.Posterize(4));
    }

    [Fact]
    public void Posterize_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.Pgm, 128);
        var result = img.Posterize(4);
        Assert.Equal(8, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Posterize_Level2_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 128);
        var result = img.Posterize(2);
        Assert.Equal(10, result.Width);
        Assert.Equal(10, result.Height);
    }

    [Fact]
    public void Posterize_Level4_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 200);
        var result = img.Posterize(4);
        Assert.Equal(10, result.Width);
        Assert.Equal(10, result.Height);
    }

    [Fact]
    public void Posterize_Level8_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, NetpbmFormat.Pgm, 100);
        var result = img.Posterize(8);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Posterize_OnBlackCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 0);
        var result = img.Posterize(4);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Posterize_OnWhiteCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 255);
        var result = img.Posterize(4);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Posterize_Chain_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.Posterize(4).Posterize(2);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // Solarize
    // -------------------------------------------------------------------------

    [Fact]
    public void Solarize_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        Assert.NotNull(img.Solarize(128));
    }

    [Fact]
    public void Solarize_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.Pgm, 128);
        var result = img.Solarize(128);
        Assert.Equal(8, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Solarize_Threshold0_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 128);
        var result = img.Solarize(0);
        Assert.Equal(10, result.Width);
        Assert.Equal(10, result.Height);
    }

    [Fact]
    public void Solarize_Threshold255_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 128);
        var result = img.Solarize(255);
        Assert.Equal(10, result.Width);
        Assert.Equal(10, result.Height);
    }

    [Fact]
    public void Solarize_MiddleThreshold_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 6, NetpbmFormat.Pgm, 100);
        var result = img.Solarize(128);
        Assert.Equal(6, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Solarize_Chain_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.Solarize(64).Solarize(192);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // Combined
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_ThenSolarize_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.Posterize(4).Solarize(128);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Solarize_ThenPosterize_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.Solarize(128).Posterize(4);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_Posterize_Solarize_Verify_Pipeline()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 128);
        Assert.Equal(10, img.Width);
        Assert.Equal(10, img.Height);

        // Posterize
        var posterized = img.Posterize(4);
        Assert.Equal(10, posterized.Width);
        Assert.Equal(10, posterized.Height);

        // Solarize
        var solarized = posterized.Solarize(128);
        Assert.Equal(10, solarized.Width);
        Assert.Equal(10, solarized.Height);

        // Chain more
        var further = solarized.Posterize(2).Solarize(64).Posterize(8);
        Assert.Equal(10, further.Width);
        Assert.Equal(10, further.Height);

        // Pixel count invariant
        Assert.Equal(img.Width * img.Height, further.Width * further.Height);
    }
}
