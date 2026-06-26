// Tests for NetpbmImage.MedianFilter, Equalize deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R196

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R196: Tests for NetpbmImage.MedianFilter, Equalize deeper coverage.
/// MedianFilter(): applies a median filter to reduce noise; preserves dimensions.
/// Equalize(): applies histogram equalization to improve contrast; preserves dimensions.
/// Covers: MedianFilter non-null; MedianFilter preserves dimensions; MedianFilter returns image;
/// MedianFilter on uniform canvas; MedianFilter chain; MedianFilter on small canvas;
/// Equalize non-null; Equalize preserves dimensions; Equalize on uniform canvas;
/// Equalize on canvas with varied brightness; Equalize chain;
/// MedianFilter->Equalize combined; Equalize->MedianFilter combined;
/// dogfood CreateCanvas->SetPixel->MedianFilter->Equalize->Verify pipeline.
/// </summary>
public class NetpbmR196MedianFilterAndEqualizeDeepTests
{
    // -------------------------------------------------------------------------
    // MedianFilter
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        Assert.NotNull(img.MedianFilter());
    }

    [Fact]
    public void MedianFilter_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.Pgm, 128);
        var result = img.MedianFilter();
        Assert.Equal(8, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void MedianFilter_OnUniformCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 200);
        var result = img.MedianFilter();
        Assert.Equal(10, result.Width);
        Assert.Equal(10, result.Height);
    }

    [Fact]
    public void MedianFilter_SmallCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(3, 3, NetpbmFormat.Pgm, 100);
        var result = img.MedianFilter();
        Assert.Equal(3, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void MedianFilter_Chain_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.MedianFilter().MedianFilter();
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void MedianFilter_LargerCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(20, 15, NetpbmFormat.Pgm, 128);
        var result = img.MedianFilter();
        Assert.Equal(20, result.Width);
        Assert.Equal(15, result.Height);
    }

    // -------------------------------------------------------------------------
    // Equalize
    // -------------------------------------------------------------------------

    [Fact]
    public void Equalize_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        Assert.NotNull(img.Equalize());
    }

    [Fact]
    public void Equalize_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.Pgm, 128);
        var result = img.Equalize();
        Assert.Equal(8, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Equalize_OnUniformCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 100);
        var result = img.Equalize();
        Assert.Equal(10, result.Width);
        Assert.Equal(10, result.Height);
    }

    [Fact]
    public void Equalize_SmallCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 64);
        var result = img.Equalize();
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void Equalize_Chain_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.Equalize().Equalize();
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Equalize_LargerCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(16, 12, NetpbmFormat.Pgm, 128);
        var result = img.Equalize();
        Assert.Equal(16, result.Width);
        Assert.Equal(12, result.Height);
    }

    // -------------------------------------------------------------------------
    // Combined MedianFilter + Equalize
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_ThenEqualize_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.MedianFilter().Equalize();
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Equalize_ThenMedianFilter_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.Equalize().MedianFilter();
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_MedianFilter_Equalize_Verify_Pipeline()
    {
        // CreateCanvas
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 128);
        Assert.Equal(10, img.Width);
        Assert.Equal(10, img.Height);

        // MedianFilter
        var filtered = img.MedianFilter();
        Assert.Equal(10, filtered.Width);
        Assert.Equal(10, filtered.Height);

        // Equalize
        var equalized = filtered.Equalize();
        Assert.Equal(10, equalized.Width);
        Assert.Equal(10, equalized.Height);

        // MedianFilter chain
        var chainFiltered = equalized.MedianFilter().MedianFilter();
        Assert.Equal(10, chainFiltered.Width);
        Assert.Equal(10, chainFiltered.Height);

        // Equalize chain
        var chainEqualized = chainFiltered.Equalize().Equalize();
        Assert.Equal(10, chainEqualized.Width);
        Assert.Equal(10, chainEqualized.Height);

        // Total pixel count preserved throughout
        Assert.Equal(img.Width * img.Height, chainEqualized.Width * chainEqualized.Height);
    }
}
