// Tests for NetpbmImage.GetLocalContrast, GetAdaptiveThreshold deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R351

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R351: Tests for NetpbmImage.GetLocalContrast, GetAdaptiveThreshold deeper.
/// GetLocalContrast(): returns mean local contrast (local std dev in neighborhood).
/// GetAdaptiveThreshold(): returns the computed adaptive threshold value (e.g., Otsu/Bradley).
/// Covers: GetLocalContrast no-throw; GetLocalContrast non-negative;
/// GetLocalContrast consistent; GetLocalContrast zero for uniform; GetLocalContrast save-load;
/// GetAdaptiveThreshold no-throw; GetAdaptiveThreshold non-negative; GetAdaptiveThreshold in [0,255];
/// GetAdaptiveThreshold consistent; GetAdaptiveThreshold save-load;
/// dogfood CreateImage→GetLocalContrast→GetAdaptiveThreshold pipeline.
/// </summary>
public class NetpbmR351GetLocalContrastAndAdaptiveThresholdDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR351GetLocalContrastAndAdaptiveThresholdDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR351_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateHighContrastImage()
    {
        // PGM 80x80 — alternating blocks (high local contrast)
        int w = 80, h = 80;
        var pixels = new byte[h * w];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                pixels[y * w + x] = ((x / 8 + y / 8) % 2 == 0) ? (byte)220 : (byte)30;
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    private static NetpbmImage CreateLowContrastImage()
    {
        // PGM 80x80 — very similar values (low contrast)
        int w = 80, h = 80;
        var pixels = new byte[h * w];
        var rng = new Random(42);
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)(120 + rng.Next(10));
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    private static NetpbmImage CreateUniformImage()
    {
        int w = 80, h = 80;
        var pixels = new byte[h * w];
        Array.Fill(pixels, (byte)128);
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    // -------------------------------------------------------------------------
    // GetLocalContrast
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLocalContrast_NoThrow()
    {
        var img = CreateHighContrastImage();
        var ex = Record.Exception(() => img.GetLocalContrast());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLocalContrast_NonNegative()
    {
        var img = CreateHighContrastImage();
        Assert.True(img.GetLocalContrast() >= 0.0);
    }

    [Fact]
    public void GetLocalContrast_Consistent()
    {
        var img = CreateHighContrastImage();
        Assert.Equal(img.GetLocalContrast(), img.GetLocalContrast());
    }

    [Fact]
    public void GetLocalContrast_Zero_ForUniform()
    {
        var img = CreateUniformImage();
        Assert.Equal(0.0, img.GetLocalContrast(), precision: 4);
    }

    [Fact]
    public void GetLocalContrast_SaveLoad_Consistent()
    {
        var img = CreateHighContrastImage();
        var before = img.GetLocalContrast();
        var path = TempFile("lc_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetLocalContrast(), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetAdaptiveThreshold
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAdaptiveThreshold_NoThrow()
    {
        var img = CreateHighContrastImage();
        var ex = Record.Exception(() => img.GetAdaptiveThreshold());
        Assert.Null(ex);
    }

    [Fact]
    public void GetAdaptiveThreshold_NonNegative()
    {
        var img = CreateHighContrastImage();
        Assert.True(img.GetAdaptiveThreshold() >= 0.0);
    }

    [Fact]
    public void GetAdaptiveThreshold_InRange()
    {
        var img = CreateHighContrastImage();
        var threshold = img.GetAdaptiveThreshold();
        Assert.True(threshold >= 0.0 && threshold <= 255.0);
    }

    [Fact]
    public void GetAdaptiveThreshold_Consistent()
    {
        var img = CreateHighContrastImage();
        Assert.Equal(img.GetAdaptiveThreshold(), img.GetAdaptiveThreshold());
    }

    [Fact]
    public void GetAdaptiveThreshold_SaveLoad_Consistent()
    {
        var img = CreateHighContrastImage();
        var before = img.GetAdaptiveThreshold();
        var path = TempFile("at_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetAdaptiveThreshold(), precision: 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetLocalContrast_GetAdaptiveThreshold_Pipeline()
    {
        // Document digitisation — HMRC Self Assessment paper form batch scanning
        // Local contrast and adaptive threshold for binarisation quality control in optical mark recognition
        var rng = new Random(20241220);

        // High quality scan — clear text on white background
        int w = 100, h = 100;
        var scanGoodPixels = new byte[h * w];
        Array.Fill(scanGoodPixels, (byte)248); // white background
        // Simulate printed text (dark marks on white)
        string[] textAreas = { "NAME:", "UTR:", "INCOME:", "TAX_PAID:", "SIGNATURE:" };
        for (int area = 0; area < textAreas.Length; area++)
        {
            int y0 = 10 + area * 18;
            // Label area (dark text)
            for (int y = y0; y < y0 + 8; y++)
                for (int x = 5; x < 30; x++)
                    scanGoodPixels[y * w + x] = (byte)(15 + rng.Next(20));
            // Value area (handwritten marks, slightly lighter)
            for (int y = y0; y < y0 + 8; y++)
                for (int x = 35; x < 90; x++)
                    if (rng.NextDouble() < 0.3)
                        scanGoodPixels[y * w + x] = (byte)(40 + rng.Next(60));
        }
        var scanGoodImg = NetpbmImage.FromGrayscalePixels(scanGoodPixels, w, h, 255);

        // Poor quality scan — yellowed paper, staining, bleed-through
        var scanPoorPixels = new byte[h * w];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                // Background degradation
                double yellowing = 0.8 + rng.NextDouble() * 0.15;
                scanPoorPixels[y * w + x] = (byte)(200 * yellowing + rng.Next(20));
            }
        // Overlapping shadow from page curl
        for (int y = 60; y < h; y++)
            for (int x = 0; x < w; x++)
                scanPoorPixels[y * w + x] = (byte)Math.Max(0, scanPoorPixels[y * w + x] - (y - 60));
        var scanPoorImg = NetpbmImage.FromGrayscalePixels(scanPoorPixels, w, h, 255);

        // Binary checkbox grid — OMR
        var omrPixels = new byte[h * w];
        Array.Fill(omrPixels, (byte)245);
        // Draw checkbox grid
        for (int row = 0; row < 5; row++)
            for (int col = 0; col < 4; col++)
            {
                int y0 = 10 + row * 18;
                int x0 = 10 + col * 22;
                // Box outline
                for (int x = x0; x < x0 + 12; x++) { omrPixels[y0 * w + x] = 30; omrPixels[(y0 + 10) * w + x] = 30; }
                for (int y = y0; y < y0 + 10; y++) { omrPixels[y * w + x0] = 30; omrPixels[y * w + x0 + 12] = 30; }
                // Fill some checkboxes
                if ((row + col) % 3 == 0)
                    for (int y = y0 + 2; y < y0 + 9; y++)
                        for (int x = x0 + 2; x < x0 + 11; x++)
                            omrPixels[y * w + x] = 25;
            }
        var omrImg = NetpbmImage.FromGrayscalePixels(omrPixels, w, h, 255);

        // GetLocalContrast
        var lcGood = scanGoodImg.GetLocalContrast();
        Assert.True(lcGood >= 0.0);
        Assert.Equal(lcGood, scanGoodImg.GetLocalContrast()); // consistent

        var lcPoor = scanPoorImg.GetLocalContrast();
        Assert.True(lcPoor >= 0.0);

        var lcOmr = omrImg.GetLocalContrast();
        Assert.True(lcOmr >= 0.0);

        // Uniform image = zero contrast
        var uniformPixels = new byte[h * w];
        Array.Fill(uniformPixels, (byte)200);
        var uniformImg = NetpbmImage.FromGrayscalePixels(uniformPixels, w, h, 255);
        Assert.Equal(0.0, uniformImg.GetLocalContrast(), precision: 4);

        // GetAdaptiveThreshold
        var atGood = scanGoodImg.GetAdaptiveThreshold();
        Assert.True(atGood >= 0.0 && atGood <= 255.0);
        Assert.Equal(atGood, scanGoodImg.GetAdaptiveThreshold()); // consistent

        var atPoor = scanPoorImg.GetAdaptiveThreshold();
        Assert.True(atPoor >= 0.0 && atPoor <= 255.0);

        var atOmr = omrImg.GetAdaptiveThreshold();
        Assert.True(atOmr >= 0.0 && atOmr <= 255.0);

        // Image dimensions
        Assert.Equal(w, scanGoodImg.Width);
        Assert.Equal(h, scanGoodImg.Height);

        // SaveToFile
        var pathGood = TempFile("hmrc_scan_good.pgm");
        scanGoodImg.SaveToFile(pathGood);
        Assert.True(File.Exists(pathGood));
        Assert.True(new FileInfo(pathGood).Length > 0);

        var pathOmr = TempFile("hmrc_omr.pgm");
        omrImg.SaveToFile(pathOmr);
        Assert.True(File.Exists(pathOmr));

        // LoadFile and verify
        var loadedGood = NetpbmImage.LoadFile(pathGood);
        Assert.Equal(w, loadedGood.Width);
        Assert.Equal(h, loadedGood.Height);
        Assert.Equal(lcGood, loadedGood.GetLocalContrast(), precision: 4);
        Assert.Equal(atGood, loadedGood.GetAdaptiveThreshold(), precision: 2);

        var loadedOmr = NetpbmImage.LoadFile(pathOmr);
        Assert.Equal(lcOmr, loadedOmr.GetLocalContrast(), precision: 4);

        // Additional operations
        var ex1 = Record.Exception(() => scanGoodImg.GetGradientMagnitude());
        var ex2 = Record.Exception(() => omrImg.GetStandardDeviation());
        var ex3 = Record.Exception(() => scanPoorImg.GetHistogram());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
