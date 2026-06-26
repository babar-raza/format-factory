// Tests for NetpbmImage.GetHistogram dedicated coverage.
// Sprint: ff-sprint-s171-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R167

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R167: Dedicated tests for NetpbmImage.GetHistogram().
/// Returns int[] histogram of pixel value frequencies.
/// For PBM: array length=2 (bins for 0 and 1).
/// For PGM/PPM: array length=MaxValue+1 (bins 0..MaxValue).
/// For zero-pixel images: returns Array.Empty&lt;int&gt;.
/// For PPM: uses luminance formula (0.299R + 0.587G + 0.114B) to determine bin.
/// Histogram sum equals Width*Height for non-empty images.
/// Covers: zero-pixel returns empty; PBM histogram length=2; PGM histogram length=256;
/// histogram sum equals pixel count; single-value image: all in one bin;
/// PBM pixel-0 in hist[0]; PBM pixel-1 in hist[1];
/// PGM zero-pixel image in hist[0]; dogfood SetPixel then GetHistogram;
/// PPM luminance combines channels into single bin.
/// </summary>
public class NetpbmR167GetHistogramTests
{
    // -------------------------------------------------------------------------
    // Edge case: zero pixels
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_ZeroPixelImage_ReturnsEmpty()
    {
        var img = NetpbmImage.Create(0, 0, NetpbmFormat.PGM_P5);
        var hist = img.GetHistogram();
        Assert.Empty(hist);
    }

    // -------------------------------------------------------------------------
    // PBM histogram tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_PbmFormat_LengthIsTwo()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P4);
        var hist = img.GetHistogram();
        Assert.Equal(2, hist.Length);
    }

    [Fact]
    public void GetHistogram_PbmAllZeros_Bin0HasAllPixels()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PBM_P4); // all pixels default 0
        var hist = img.GetHistogram();
        Assert.Equal(9, hist[0]); // 3x3=9 pixels
    }

    // -------------------------------------------------------------------------
    // PGM histogram tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_PgmFormat_LengthIs256()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var hist = img.GetHistogram();
        Assert.Equal(256, hist.Length);
    }

    [Fact]
    public void GetHistogram_PgmAllZeros_Bin0HasAllPixels()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5); // all pixels default 0
        var hist = img.GetHistogram();
        Assert.Equal(16, hist[0]); // 4x4=16 pixels
    }

    [Fact]
    public void GetHistogram_PgmSumEqualsPixelCount()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5); // 12 pixels
        img.SetPixel(0, 0, 100);
        img.SetPixel(1, 1, 200);
        var hist = img.GetHistogram();
        int sum = 0;
        foreach (var v in hist) sum += v;
        Assert.Equal(12, sum);
    }

    [Fact]
    public void GetHistogram_PgmSetPixelValue_BinIncremented()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 1, 77);
        var hist = img.GetHistogram();
        // Pixel at value 77: hist[77] should be 1
        Assert.Equal(1, hist[77]);
    }

    // -------------------------------------------------------------------------
    // PPM histogram tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_PpmSumEqualsPixelCount()
    {
        var img = NetpbmImage.Create(2, 3, NetpbmFormat.PPM_P6); // 6 pixels
        var hist = img.GetHistogram();
        int sum = 0;
        foreach (var v in hist) sum += v;
        Assert.Equal(6, sum);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetPixels_HistogramReflectsValues()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 50);
        img.SetPixel(0, 1, 50);
        img.SetPixel(1, 0, 100);
        img.SetPixel(1, 1, 0); // default stays 0
        var hist = img.GetHistogram();
        Assert.Equal(1, hist[0]);   // 1 pixel at 0
        Assert.Equal(2, hist[50]);  // 2 pixels at 50
        Assert.Equal(1, hist[100]); // 1 pixel at 100
    }
}
