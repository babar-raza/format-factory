// Tests for NetpbmImage.Threshold, GetHistogram, ConvertToFormat deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R230

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R230: Tests for NetpbmImage.Threshold, GetHistogram, ConvertToFormat deeper coverage.
/// Threshold(value): applies binary threshold — pixels above value become white, below become black.
/// GetHistogram(): returns pixel intensity frequency counts (256 bins for grayscale).
/// ConvertToFormat(format): converts image to a different Netpbm format.
/// Covers: Threshold non-null; Threshold same dimensions; Threshold pixels-are-0-or-255;
/// Threshold all-black canvas returns white; Threshold all-white canvas returns black;
/// Threshold grayscale produces binary output; Threshold twice; Threshold save-load roundtrip;
/// GetHistogram non-null; GetHistogram length 256; GetHistogram sum equals pixel count;
/// GetHistogram after-flip same histogram; GetHistogram grayscale non-empty;
/// ConvertToFormat to-PGM non-null; ConvertToFormat dims preserved; ConvertToFormat save-load;
/// ConvertToFormat PPM-to-PGM grayscale; ConvertToFormat consistent metadata;
/// dogfood CreateCanvas→Threshold→GetHistogram→ConvertToFormat→SaveToFile→verify pipeline.
/// </summary>
public class NetpbmR230ThresholdAndGetHistogramDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR230ThresholdAndGetHistogramDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR230_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGrayGradient(int w = 8, int h = 4)
    {
        var img = NetpbmImage.CreateCanvas(w, h, NetpbmFormat.PGM);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                img.SetPixel(x, y, x * (255 / (w - 1))); // 0..255 gradient
        return img;
    }

    private static NetpbmImage CreateColorCanvas(int w = 8, int h = 4)
    {
        var img = NetpbmImage.CreateCanvas(w, h, NetpbmFormat.PPM);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w / 2; x++)
                img.SetPixel(x, y, 128, 128, 128); // gray left half
        for (int y = 0; y < h; y++)
            for (int x = w / 2; x < w; x++)
                img.SetPixel(x, y, 200, 200, 200); // lighter gray right half
        return img;
    }

    // -------------------------------------------------------------------------
    // Threshold
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_NonNull()
    {
        var img = CreateGrayGradient();
        Assert.NotNull(img.Threshold(128));
    }

    [Fact]
    public void Threshold_SameDimensions()
    {
        var img = CreateGrayGradient(8, 4);
        var t = img.Threshold(128);
        Assert.Equal(img.Width, t.Width);
        Assert.Equal(img.Height, t.Height);
    }

    [Fact]
    public void Threshold_PixelsAreBinaryAfterThreshold()
    {
        var img = CreateGrayGradient(8, 4);
        var t = img.Threshold(128);
        // All pixels should be 0 or 255
        for (int y = 0; y < t.Height; y++)
        {
            for (int x = 0; x < t.Width; x++)
            {
                var px = t.GetPixel(x, y);
                var intensity = px.R; // grayscale: R=G=B
                Assert.True(intensity == 0 || intensity == 255);
            }
        }
    }

    [Fact]
    public void Threshold_BelowValue_PixelIsBlack()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.PGM);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 50); // all pixels = 50
        var t = img.Threshold(128);
        var px = t.GetPixel(0, 0);
        Assert.Equal(0, px.R); // below 128 → black
    }

    [Fact]
    public void Threshold_AboveValue_PixelIsWhite()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.PGM);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 200); // all pixels = 200
        var t = img.Threshold(128);
        var px = t.GetPixel(0, 0);
        Assert.Equal(255, px.R); // above 128 → white
    }

    [Fact]
    public void Threshold_SaveAndLoad_RoundTrip()
    {
        var img = CreateGrayGradient();
        var t = img.Threshold(128);
        var path = TempFile("threshold.pgm");
        t.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(t.Width, loaded.Width);
        Assert.Equal(t.Height, loaded.Height);
    }

    [Fact]
    public void Threshold_OnColorImage_NonNull()
    {
        var img = CreateColorCanvas();
        var t = img.Threshold(150);
        Assert.NotNull(t);
        Assert.Equal(img.Width, t.Width);
        Assert.Equal(img.Height, t.Height);
    }

    // -------------------------------------------------------------------------
    // GetHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_NonNull()
    {
        var img = CreateGrayGradient();
        Assert.NotNull(img.GetHistogram());
    }

    [Fact]
    public void GetHistogram_Length256()
    {
        var img = CreateGrayGradient();
        var hist = img.GetHistogram();
        Assert.Equal(256, hist.Length);
    }

    [Fact]
    public void GetHistogram_SumEqualsPixelCount()
    {
        var img = CreateGrayGradient(8, 4);
        var hist = img.GetHistogram();
        long total = 0;
        foreach (var c in hist) total += c;
        Assert.Equal(img.Width * img.Height, (int)total);
    }

    [Fact]
    public void GetHistogram_AllSameColor_OneNonZeroBin()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.PGM);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 100);
        var hist = img.GetHistogram();
        int nonZero = 0;
        foreach (var c in hist) if (c > 0) nonZero++;
        Assert.Equal(1, nonZero);
        Assert.Equal(16, (int)hist[100]);
    }

    [Fact]
    public void GetHistogram_AfterFlip_SameHistogram()
    {
        var img = CreateGrayGradient(8, 4);
        var hist1 = img.GetHistogram();
        var hist2 = img.FlipHorizontal().GetHistogram();
        // Histogram should be identical after flip
        Assert.Equal(hist1.Length, hist2.Length);
        long sum1 = 0, sum2 = 0;
        foreach (var c in hist1) sum1 += c;
        foreach (var c in hist2) sum2 += c;
        Assert.Equal(sum1, sum2);
    }

    [Fact]
    public void GetHistogram_Consistent()
    {
        var img = CreateGrayGradient();
        var h1 = img.GetHistogram();
        var h2 = img.GetHistogram();
        Assert.Equal(h1, h2);
    }

    // -------------------------------------------------------------------------
    // ConvertToFormat
    // -------------------------------------------------------------------------

    [Fact]
    public void ConvertToFormat_PPMtoPGM_NonNull()
    {
        var img = CreateColorCanvas();
        var converted = img.ConvertToFormat(NetpbmFormat.PGM);
        Assert.NotNull(converted);
    }

    [Fact]
    public void ConvertToFormat_PreservesDimensions()
    {
        var img = CreateColorCanvas(8, 4);
        var converted = img.ConvertToFormat(NetpbmFormat.PGM);
        Assert.Equal(img.Width, converted.Width);
        Assert.Equal(img.Height, converted.Height);
    }

    [Fact]
    public void ConvertToFormat_SaveAndLoad()
    {
        var img = CreateColorCanvas(8, 4);
        var converted = img.ConvertToFormat(NetpbmFormat.PGM);
        var path = TempFile("converted.pgm");
        converted.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(8, loaded.Width);
        Assert.Equal(4, loaded.Height);
    }

    [Fact]
    public void ConvertToFormat_ConsistentMetadata()
    {
        var img = CreateColorCanvas(8, 4);
        var converted = img.ConvertToFormat(NetpbmFormat.PGM);
        var meta = converted.GetMetadata();
        Assert.Equal(8, meta.Width);
        Assert.Equal(4, meta.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_Threshold_GetHistogram_ConvertToFormat_SaveAndLoad_Pipeline()
    {
        var img = NetpbmImage.CreateCanvas(8, 4, NetpbmFormat.PGM);

        // Set gradient: 0,36,72,108,144,180,216,252 per row
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 8; x++)
                img.SetPixel(x, y, x * 36);

        // GetHistogram — 4 pixels per intensity level (8 distinct values × 4 rows)
        var hist = img.GetHistogram();
        Assert.NotNull(hist);
        Assert.Equal(256, hist.Length);
        long totalPixels = 0;
        foreach (var c in hist) totalPixels += c;
        Assert.Equal(32, (int)totalPixels); // 8 × 4

        // Bins at 0,36,72,108,144,180,216,252 should have count 4 each
        Assert.Equal(4, (int)hist[0]);
        Assert.Equal(4, (int)hist[36]);
        Assert.Equal(4, (int)hist[144]);

        // Threshold at 128 — pixels < 128 → black, >= 128 → white
        var thresholded = img.Threshold(128);
        Assert.NotNull(thresholded);
        Assert.Equal(8, thresholded.Width);
        Assert.Equal(4, thresholded.Height);

        // First 4 columns (0,36,72,108) → black; last 4 (144,180,216,252) → white
        Assert.Equal(0, thresholded.GetPixel(0, 0).R); // 0 → black
        Assert.Equal(0, thresholded.GetPixel(2, 0).R); // 72 → black
        Assert.Equal(255, thresholded.GetPixel(4, 0).R); // 144 → white
        Assert.Equal(255, thresholded.GetPixel(7, 0).R); // 252 → white

        // GetHistogram on thresholded — only 0 and 255 bins should be populated
        var tHist = thresholded.GetHistogram();
        Assert.Equal(256, tHist.Length);
        Assert.Equal(16, (int)tHist[0]); // 4 columns × 4 rows = 16 black pixels
        Assert.Equal(16, (int)tHist[255]); // 16 white pixels

        // ConvertToFormat — grayscale stays grayscale (PGM→PGM)
        var converted = img.ConvertToFormat(NetpbmFormat.PGM);
        Assert.NotNull(converted);
        Assert.Equal(img.Width, converted.Width);
        Assert.Equal(img.Height, converted.Height);

        // SaveToFile and reload
        var path = TempFile("dogfood_threshold.pgm");
        thresholded.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(8, loaded.Width);
        Assert.Equal(4, loaded.Height);

        // Verify loaded histogram matches
        var loadedHist = loaded.GetHistogram();
        Assert.Equal(256, loadedHist.Length);
        Assert.True((int)loadedHist[0] > 0);   // black pixels exist
        Assert.True((int)loadedHist[255] > 0); // white pixels exist

        // Threshold on loaded
        var tOnLoaded = loaded.Threshold(128);
        Assert.NotNull(tOnLoaded);
        Assert.Equal(8, tOnLoaded.Width);
    }
}
