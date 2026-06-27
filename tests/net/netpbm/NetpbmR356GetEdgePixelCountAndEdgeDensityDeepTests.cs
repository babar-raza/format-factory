// Tests for NetpbmImage.GetEdgePixelCount, GetEdgeDensity deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R356

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R356: Tests for NetpbmImage.GetEdgePixelCount, GetEdgeDensity deeper.
/// GetEdgePixelCount(): returns the count of pixels classified as edge pixels.
/// GetEdgeDensity(): returns the fraction of pixels that are edge pixels (count / totalPixels).
/// Covers: GetEdgePixelCount no-throw; GetEdgePixelCount non-negative;
/// GetEdgePixelCount zero for uniform; GetEdgePixelCount consistent;
/// GetEdgePixelCount save-load; GetEdgePixelCount positive for image with edges;
/// GetEdgeDensity no-throw; GetEdgeDensity in [0,1]; GetEdgeDensity consistent;
/// GetEdgeDensity zero for uniform; GetEdgeDensity save-load;
/// GetEdgeDensity equals EdgePixelCount / total pixels;
/// dogfood CreateImage→GetEdgePixelCount→GetEdgeDensity pipeline.
/// </summary>
public class NetpbmR356GetEdgePixelCountAndEdgeDensityDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR356GetEdgePixelCountAndEdgeDensityDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR356_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateUniformImage()
    {
        int w = 64, h = 64;
        var pixels = new byte[w * h];
        Array.Fill(pixels, (byte)128);
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    private static NetpbmImage CreateEdgeImage()
    {
        // Horizontal step edge across the middle
        int w = 64, h = 64;
        var pixels = new byte[w * h];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                pixels[y * w + x] = y < h / 2 ? (byte)30 : (byte)220;
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    private static NetpbmImage CreateCheckerImage()
    {
        // 8x8 checkerboard — many edges
        int w = 64, h = 64;
        var pixels = new byte[w * h];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                pixels[y * w + x] = ((x / 8 + y / 8) % 2 == 0) ? (byte)30 : (byte)220;
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    // -------------------------------------------------------------------------
    // GetEdgePixelCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEdgePixelCount_NoThrow()
    {
        var img = CreateEdgeImage();
        var ex = Record.Exception(() => img.GetEdgePixelCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEdgePixelCount_NonNegative()
    {
        var img = CreateEdgeImage();
        Assert.True(img.GetEdgePixelCount() >= 0);
    }

    [Fact]
    public void GetEdgePixelCount_Zero_ForUniform()
    {
        var img = CreateUniformImage();
        Assert.Equal(0, img.GetEdgePixelCount());
    }

    [Fact]
    public void GetEdgePixelCount_Positive_ForEdgeImage()
    {
        var img = CreateEdgeImage();
        Assert.True(img.GetEdgePixelCount() > 0);
    }

    [Fact]
    public void GetEdgePixelCount_Consistent()
    {
        var img = CreateEdgeImage();
        Assert.Equal(img.GetEdgePixelCount(), img.GetEdgePixelCount());
    }

    [Fact]
    public void GetEdgePixelCount_SaveLoad_Consistent()
    {
        var img = CreateEdgeImage();
        var before = img.GetEdgePixelCount();
        var path = TempFile("ep_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetEdgePixelCount());
    }

    // -------------------------------------------------------------------------
    // GetEdgeDensity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEdgeDensity_NoThrow()
    {
        var img = CreateEdgeImage();
        var ex = Record.Exception(() => img.GetEdgeDensity());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEdgeDensity_InRange()
    {
        var img = CreateEdgeImage();
        var d = img.GetEdgeDensity();
        Assert.True(d >= 0.0 && d <= 1.0);
    }

    [Fact]
    public void GetEdgeDensity_Consistent()
    {
        var img = CreateCheckerImage();
        Assert.Equal(img.GetEdgeDensity(), img.GetEdgeDensity());
    }

    [Fact]
    public void GetEdgeDensity_Zero_ForUniform()
    {
        var img = CreateUniformImage();
        Assert.Equal(0.0, img.GetEdgeDensity(), precision: 6);
    }

    [Fact]
    public void GetEdgeDensity_SaveLoad_Consistent()
    {
        var img = CreateEdgeImage();
        var before = img.GetEdgeDensity();
        var path = TempFile("ed_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetEdgeDensity(), precision: 6);
    }

    [Fact]
    public void GetEdgeDensity_EqualsEdgePixelCountOverTotal()
    {
        var img = CreateEdgeImage();
        int epc = img.GetEdgePixelCount();
        int total = img.Width * img.Height;
        double expected = (double)epc / total;
        Assert.Equal(expected, img.GetEdgeDensity(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetEdgePixelCount_GetEdgeDensity_Pipeline()
    {
        // Medical imaging — NICE-approved AI-assisted mammography screening QA
        // Digital breast tomosynthesis (DBT) image quality metrics for regulatory submission
        var rng = new Random(20241115);
        int w = 100, h = 100;

        // Normal breast tissue: smooth density gradient — few edges
        var normalPixels = new byte[w * h];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                // Smooth radial gradient simulating breast parenchyma
                double dx = x - w / 2.0, dy = y - h / 2.0;
                double dist = Math.Sqrt(dx * dx + dy * dy) / (w / 2.0);
                normalPixels[y * w + x] = (byte)(180 - dist * 120 + rng.Next(10));
            }
        var normalImg = NetpbmImage.FromGrayscalePixels(normalPixels, w, h, 255);

        // Suspicious mass: hard boundary with internal heterogeneity — many edges
        var massPixels = new byte[w * h];
        Array.Fill(massPixels, (byte)160);
        // Circular mass with irregular spiculated boundary
        int cx = 55, cy = 45, baseR = 20;
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                double dx = x - cx, dy = y - cy;
                double dist = Math.Sqrt(dx * dx + dy * dy);
                double angle = Math.Atan2(dy, dx);
                // Spiculated boundary
                double boundary = baseR + 6 * Math.Abs(Math.Sin(angle * 5)) + rng.NextDouble() * 4;
                if (dist <= boundary)
                    massPixels[y * w + x] = (byte)(50 + rng.Next(40));  // mass interior
                else if (dist <= boundary + 3)
                    massPixels[y * w + x] = (byte)(30 + rng.Next(20));  // spicule tip
            }
        var massImg = NetpbmImage.FromGrayscalePixels(massPixels, w, h, 255);

        // Calcification cluster: multiple tiny bright spots — dense edges
        var calcPixels = new byte[w * h];
        Array.Fill(calcPixels, (byte)80);
        for (int i = 0; i < 30; i++)
        {
            int px = 20 + rng.Next(60), py = 20 + rng.Next(60);
            for (int dy2 = -2; dy2 <= 2; dy2++)
                for (int dx2 = -2; dx2 <= 2; dx2++)
                {
                    int nx = px + dx2, ny = py + dy2;
                    if (nx >= 0 && nx < w && ny >= 0 && ny < h)
                        calcPixels[ny * w + nx] = (byte)(220 + rng.Next(35));
                }
        }
        var calcImg = NetpbmImage.FromGrayscalePixels(calcPixels, w, h, 255);

        // GetEdgePixelCount
        var epcNormal = normalImg.GetEdgePixelCount();
        Assert.True(epcNormal >= 0);
        Assert.Equal(epcNormal, normalImg.GetEdgePixelCount()); // consistent

        var epcMass = massImg.GetEdgePixelCount();
        Assert.True(epcMass >= 0);
        // Mass should have more edges than smooth normal tissue
        Assert.True(epcMass > epcNormal);

        var epcCalc = calcImg.GetEdgePixelCount();
        Assert.True(epcCalc >= 0);
        Assert.Equal(epcCalc, calcImg.GetEdgePixelCount()); // consistent

        // GetEdgeDensity
        var edNormal = normalImg.GetEdgeDensity();
        Assert.True(edNormal >= 0.0 && edNormal <= 1.0);
        Assert.Equal(edNormal, normalImg.GetEdgeDensity()); // consistent

        var edMass = massImg.GetEdgeDensity();
        Assert.True(edMass >= 0.0 && edMass <= 1.0);

        var edCalc = calcImg.GetEdgeDensity();
        Assert.True(edCalc >= 0.0 && edCalc <= 1.0);

        // Density = count / total
        int total = w * h;
        Assert.Equal((double)epcNormal / total, edNormal, precision: 6);
        Assert.Equal((double)epcMass / total, edMass, precision: 6);
        Assert.Equal((double)epcCalc / total, edCalc, precision: 6);

        // Image dimensions
        Assert.Equal(w, normalImg.Width);
        Assert.Equal(h, normalImg.Height);
        Assert.True(normalImg.GetMeanIntensity() >= 0.0 && normalImg.GetMeanIntensity() <= 255.0);

        // SaveToFile
        var pathNormal = TempFile("mammo_normal.pgm");
        normalImg.SaveToFile(pathNormal);
        Assert.True(File.Exists(pathNormal));

        var pathMass = TempFile("mammo_mass.pgm");
        massImg.SaveToFile(pathMass);
        Assert.True(File.Exists(pathMass));

        var pathCalc = TempFile("mammo_calc.pgm");
        calcImg.SaveToFile(pathCalc);
        Assert.True(File.Exists(pathCalc));

        // LoadFile and verify
        var loadedNormal = NetpbmImage.LoadFile(pathNormal);
        Assert.Equal(epcNormal, loadedNormal.GetEdgePixelCount());
        Assert.Equal(edNormal, loadedNormal.GetEdgeDensity(), precision: 6);

        var loadedMass = NetpbmImage.LoadFile(pathMass);
        Assert.Equal(epcMass, loadedMass.GetEdgePixelCount());
        Assert.Equal(edMass, loadedMass.GetEdgeDensity(), precision: 6);

        var loadedCalc = NetpbmImage.LoadFile(pathCalc);
        Assert.Equal(epcCalc, loadedCalc.GetEdgePixelCount());
        Assert.Equal(edCalc, loadedCalc.GetEdgeDensity(), precision: 6);

        // Additional checks
        var ex1 = Record.Exception(() => normalImg.GetStandardDeviation());
        var ex2 = Record.Exception(() => massImg.GetHistogram());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
