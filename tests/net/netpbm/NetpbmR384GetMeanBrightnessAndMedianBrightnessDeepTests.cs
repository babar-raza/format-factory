// Tests for NetpbmImage.GetMeanBrightness, GetMedianBrightness deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R384

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R384: Tests for NetpbmImage.GetMeanBrightness, GetMedianBrightness deeper.
/// GetMeanBrightness(): returns the arithmetic mean of pixel intensities; [0,255] for 8-bit.
/// GetMedianBrightness(): returns the median pixel intensity; [0,255] for 8-bit.
/// Covers: GetMeanBrightness no-throw; GetMeanBrightness in-range; GetMeanBrightness exact for uniform;
/// GetMeanBrightness consistent; GetMeanBrightness save-load;
/// GetMedianBrightness no-throw; GetMedianBrightness in-range; GetMedianBrightness exact for uniform;
/// GetMedianBrightness consistent; GetMedianBrightness save-load;
/// MeanBrightness and MedianBrightness agree for symmetric distribution;
/// dogfood pipeline.
/// </summary>
public class NetpbmR384GetMeanBrightnessAndMedianBrightnessDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR384GetMeanBrightnessAndMedianBrightnessDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR384_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateUniformPgm(string name, int width, int height, int intensity)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int y = 0; y < height; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < width; x++)
            {
                if (x > 0) row.Append(' ');
                row.Append(intensity);
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateGradientPgm(string name, int width, int height)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int y = 0; y < height; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < width; x++)
            {
                if (x > 0) row.Append(' ');
                row.Append((int)(255.0 * x / (width - 1)));
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateSkewedPgm(string name)
    {
        // Mostly dark pixels with a few very bright ones → mean > median
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("50 50");
        sb.AppendLine("255");
        var rng = new Random(7777);
        for (int y = 0; y < 50; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < 50; x++)
            {
                if (x > 0) row.Append(' ');
                // 90% dark (10-30), 10% bright (220-255)
                int val = rng.NextDouble() < 0.9 ? rng.Next(10, 31) : rng.Next(220, 256);
                row.Append(val);
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetMeanBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMeanBrightness_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 50, 50));
        var ex = Record.Exception(() => img.GetMeanBrightness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMeanBrightness_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 50, 50));
        var m = img.GetMeanBrightness();
        Assert.True(m >= 0.0 && m <= 255.0);
    }

    [Fact]
    public void GetMeanBrightness_Exact_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform128.pgm", 40, 40, 128));
        Assert.Equal(128.0, img.GetMeanBrightness(), precision: 3);
    }

    [Fact]
    public void GetMeanBrightness_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 50, 50));
        Assert.Equal(img.GetMeanBrightness(), img.GetMeanBrightness());
    }

    [Fact]
    public void GetMeanBrightness_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 50, 50));
        var before = img.GetMeanBrightness();
        var path = TempFile("mb_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetMeanBrightness(), precision: 3);
    }

    // -------------------------------------------------------------------------
    // GetMedianBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMedianBrightness_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 50, 50));
        var ex = Record.Exception(() => img.GetMedianBrightness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMedianBrightness_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 50, 50));
        var m = img.GetMedianBrightness();
        Assert.True(m >= 0.0 && m <= 255.0);
    }

    [Fact]
    public void GetMedianBrightness_Exact_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform200.pgm", 40, 40, 200));
        Assert.Equal(200.0, img.GetMedianBrightness(), precision: 3);
    }

    [Fact]
    public void GetMedianBrightness_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 50, 50));
        Assert.Equal(img.GetMedianBrightness(), img.GetMedianBrightness());
    }

    [Fact]
    public void GetMedianBrightness_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 50, 50));
        var before = img.GetMedianBrightness();
        var path = TempFile("med_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetMedianBrightness(), precision: 3);
    }

    [Fact]
    public void MeanAndMedian_Equal_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform100.pgm", 40, 40, 100));
        Assert.Equal(img.GetMeanBrightness(), img.GetMedianBrightness(), precision: 3);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMeanBrightness_GetMedianBrightness_Pipeline()
    {
        // Medical Imaging — NHS England / NHSX: Chest X-Ray AI Validation Dataset
        // PGM radiograph images for AI model validation
        // Mean and median brightness quantify exposure quality and detect over/under-exposed images

        // Image 1: Normal exposure chest X-ray (mid-range brightness, balanced)
        var path1 = TempFile("cxr_normal_exposure.pgm");
        {
            int w = 80, h = 60;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20241001);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // Normal X-ray: lungs (bright 180-220), ribs (medium 100-150), spine (dark 30-70)
                    double dist = Math.Sqrt((x - w / 2.0) * (x - w / 2.0) + (y - h / 2.0) * (y - h / 2.0));
                    int val = dist < 15 ? rng.Next(30, 70) : dist < 30 ? rng.Next(100, 150) : rng.Next(180, 220);
                    row.Append(Math.Min(255, val));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path1, sb.ToString());
        }

        // Image 2: Over-exposed X-ray (very high brightness, washed out)
        var path2 = TempFile("cxr_overexposed.pgm");
        {
            int w = 80, h = 60;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20241002);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    row.Append(rng.Next(210, 256)); // over-exposed
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path2, sb.ToString());
        }

        // Image 3: Under-exposed X-ray (very dark)
        var path3 = TempFile("cxr_underexposed.pgm");
        {
            int w = 80, h = 60;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20241003);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    row.Append(rng.Next(0, 45)); // under-exposed
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path3, sb.ToString());
        }

        var img1 = NetpbmImage.LoadFile(path1);
        var img2 = NetpbmImage.LoadFile(path2);
        var img3 = NetpbmImage.LoadFile(path3);

        // Mean brightness: over-exposed >> normal >> under-exposed
        var mean1 = img1.GetMeanBrightness();
        var mean2 = img2.GetMeanBrightness();
        var mean3 = img3.GetMeanBrightness();
        Assert.True(mean1 >= 0.0 && mean1 <= 255.0);
        Assert.True(mean2 >= 0.0 && mean2 <= 255.0);
        Assert.True(mean3 >= 0.0 && mean3 <= 255.0);
        Assert.True(mean2 > mean1); // over-exposed brighter than normal
        Assert.True(mean1 > mean3); // normal brighter than under-exposed
        Assert.Equal(mean1, img1.GetMeanBrightness()); // consistent
        Assert.Equal(mean2, img2.GetMeanBrightness()); // consistent

        // Median brightness
        var med1 = img1.GetMedianBrightness();
        var med2 = img2.GetMedianBrightness();
        var med3 = img3.GetMedianBrightness();
        Assert.True(med1 >= 0.0 && med1 <= 255.0);
        Assert.True(med2 >= 0.0 && med2 <= 255.0);
        Assert.True(med3 >= 0.0 && med3 <= 255.0);
        Assert.True(med2 > med1); // over-exposed median higher
        Assert.True(med1 > med3); // normal median higher than under-exposed
        Assert.Equal(med1, img1.GetMedianBrightness()); // consistent

        // Uniform reference
        var uniformImg = NetpbmImage.LoadFile(CreateUniformPgm("uniform150.pgm", 30, 30, 150));
        Assert.Equal(150.0, uniformImg.GetMeanBrightness(), precision: 2);
        Assert.Equal(150.0, uniformImg.GetMedianBrightness(), precision: 2);

        // SaveToFile and verify
        var out1 = TempFile("cxr_normal_out.pgm");
        img1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        var loaded1 = NetpbmImage.LoadFile(out1);
        Assert.Equal(mean1, loaded1.GetMeanBrightness(), precision: 3);
        Assert.Equal(med1, loaded1.GetMedianBrightness(), precision: 3);

        var out2 = TempFile("cxr_overexposed_out.pgm");
        img2.SaveToFile(out2);
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.Equal(mean2, loaded2.GetMeanBrightness(), precision: 3);
        Assert.Equal(med2, loaded2.GetMedianBrightness(), precision: 3);

        var out3 = TempFile("cxr_underexposed_out.pgm");
        img3.SaveToFile(out3);
        var loaded3 = NetpbmImage.LoadFile(out3);
        Assert.Equal(mean3, loaded3.GetMeanBrightness(), precision: 3);
        Assert.Equal(med3, loaded3.GetMedianBrightness(), precision: 3);

        var ex1 = Record.Exception(() => loaded1.GetMeanBrightness());
        var ex2 = Record.Exception(() => loaded1.GetMedianBrightness());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
