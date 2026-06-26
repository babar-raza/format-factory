// Tests for NetpbmImage.GetHistogram, Normalize, GetBrightness deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R277

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R277: Tests for NetpbmImage.GetHistogram, Normalize, GetBrightness deeper.
/// GetHistogram(): returns an array of pixel frequency counts by intensity level.
/// Normalize(): returns a new image where pixel values are linearly scaled to [0, maxVal].
/// GetBrightness(): returns the mean pixel value normalized to [0.0, 1.0].
/// Covers: GetHistogram no-throw; GetHistogram non-null; GetHistogram length equals maxVal+1;
/// GetHistogram sum equals pixel count; GetHistogram consistent;
/// GetHistogram save-load;
/// Normalize no-throw; Normalize same dimensions; Normalize maxVal in range;
/// Normalize consistent; Normalize save-load;
/// GetBrightness no-throw; GetBrightness in [0,1]; GetBrightness consistent;
/// GetBrightness uniform near expected; GetBrightness save-load;
/// dogfood LoadFile→GetHistogram→Normalize→GetBrightness→SaveToFile pipeline.
/// </summary>
public class NetpbmR277GetHistogramAndNormalizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR277GetHistogramAndNormalizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR277_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateGradientPgm(int width = 16, int height = 16)
    {
        var path = TempFile($"gradient_{width}x{height}.pgm");
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{width} {height}");
        sw.WriteLine("255");
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int val = (x * 255) / (width - 1);
                sw.Write(val);
                if (x < width - 1) sw.Write(' ');
            }
            sw.WriteLine();
        }
        return path;
    }

    private string CreateUniformPgm(int intensity, int width = 8, int height = 8)
    {
        var path = TempFile($"uniform_{intensity}.pgm");
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{width} {height}");
        sw.WriteLine("255");
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                sw.Write(intensity);
                if (x < width - 1) sw.Write(' ');
            }
            sw.WriteLine();
        }
        return path;
    }

    // -------------------------------------------------------------------------
    // GetHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetHistogram());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHistogram_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.NotNull(img.GetHistogram());
    }

    [Fact]
    public void GetHistogram_LengthEqualsMaxValPlusOne()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var hist = img.GetHistogram();
        Assert.Equal(img.MaxVal + 1, hist.Length);
    }

    [Fact]
    public void GetHistogram_SumEqualsPixelCount()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(16, 16));
        var hist = img.GetHistogram();
        long sum = 0;
        foreach (var count in hist) sum += count;
        Assert.Equal(16 * 16, (int)sum);
    }

    [Fact]
    public void GetHistogram_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var h1 = img.GetHistogram();
        var h2 = img.GetHistogram();
        Assert.Equal(h1.Length, h2.Length);
        for (int i = 0; i < h1.Length; i++)
            Assert.Equal(h1[i], h2[i]);
    }

    [Fact]
    public void GetHistogram_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var histBefore = img.GetHistogram();
        var path = TempFile("hist_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        var histAfter = loaded.GetHistogram();
        Assert.Equal(histBefore.Length, histAfter.Length);
        for (int i = 0; i < histBefore.Length; i++)
            Assert.Equal(histBefore[i], histAfter[i]);
    }

    [Fact]
    public void GetHistogram_Uniform_SingleBinFull()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm(128));
        var hist = img.GetHistogram();
        // All pixels at intensity 128 → hist[128] == total pixels
        Assert.Equal(8 * 8, (int)hist[128]);
        // All other bins == 0
        for (int i = 0; i < hist.Length; i++)
            if (i != 128) Assert.Equal(0, (int)hist[i]);
    }

    // -------------------------------------------------------------------------
    // Normalize
    // -------------------------------------------------------------------------

    [Fact]
    public void Normalize_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.Normalize());
        Assert.Null(ex);
    }

    [Fact]
    public void Normalize_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var norm = img.Normalize();
        Assert.Equal(img.Width, norm.Width);
        Assert.Equal(img.Height, norm.Height);
    }

    [Fact]
    public void Normalize_MaxValInRange()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var norm = img.Normalize();
        Assert.True(norm.MaxVal >= 1);
        Assert.True(norm.MaxVal <= 65535);
    }

    [Fact]
    public void Normalize_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var n1 = img.Normalize();
        var n2 = img.Normalize();
        Assert.Equal(n1.Width, n2.Width);
        Assert.Equal(n1.Height, n2.Height);
        Assert.Equal(n1.MaxVal, n2.MaxVal);
    }

    [Fact]
    public void Normalize_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var norm = img.Normalize();
        var path = TempFile("norm_save.pgm");
        norm.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(norm.Width, loaded.Width);
        Assert.Equal(norm.Height, loaded.Height);
        Assert.Equal(norm.MaxVal, loaded.MaxVal);
    }

    // -------------------------------------------------------------------------
    // GetBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetBrightness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBrightness_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var b = img.GetBrightness();
        Assert.True(b >= 0.0 && b <= 1.0);
    }

    [Fact]
    public void GetBrightness_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetBrightness(), img.GetBrightness());
    }

    [Fact]
    public void GetBrightness_Uniform_Near_ExpectedValue()
    {
        // Uniform image at intensity 128 → brightness ≈ 128/255 ≈ 0.502
        var img = NetpbmImage.LoadFile(CreateUniformPgm(128));
        var brightness = img.GetBrightness();
        Assert.InRange(brightness, 0.49, 0.52);
    }

    [Fact]
    public void GetBrightness_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var before = img.GetBrightness();
        var path = TempFile("bright_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetBrightness(), 4);
    }

    [Fact]
    public void GetBrightness_White_IsOne()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm(255));
        Assert.Equal(1.0, img.GetBrightness(), 3);
    }

    [Fact]
    public void GetBrightness_Black_IsZero()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm(0));
        Assert.Equal(0.0, img.GetBrightness(), 3);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetHistogram_Normalize_GetBrightness_SaveToFile_Pipeline()
    {
        // Create a gradient image: left=dark, right=bright (32×32)
        var srcPath = TempFile("dogfood_src.pgm");
        using (var sw = new StreamWriter(srcPath))
        {
            sw.WriteLine("P2");
            sw.WriteLine("32 32");
            sw.WriteLine("255");
            for (int y = 0; y < 32; y++)
            {
                for (int x = 0; x < 32; x++)
                {
                    int val = (x * 255) / 31;
                    sw.Write(val);
                    if (x < 31) sw.Write(' ');
                }
                sw.WriteLine();
            }
        }

        var img = NetpbmImage.LoadFile(srcPath);
        Assert.NotNull(img);
        Assert.Equal(32, img.Width);
        Assert.Equal(32, img.Height);

        // GetHistogram
        var hist = img.GetHistogram();
        Assert.NotNull(hist);
        Assert.Equal(img.MaxVal + 1, hist.Length);

        // Sum of histogram == total pixels
        long pixelSum = 0;
        foreach (var c in hist) pixelSum += c;
        Assert.Equal(32 * 32, (int)pixelSum);

        // No negative counts
        foreach (var c in hist) Assert.True(c >= 0);

        // GetBrightness
        var brightness = img.GetBrightness();
        Assert.True(brightness >= 0.0 && brightness <= 1.0);
        Assert.True(brightness > 0.4 && brightness < 0.6); // gradient average near 0.5

        // Normalize
        var norm = img.Normalize();
        Assert.NotNull(norm);
        Assert.Equal(img.Width, norm.Width);
        Assert.Equal(img.Height, norm.Height);
        Assert.True(norm.MaxVal >= 1);

        // Normalized brightness also in range
        var normBrightness = norm.GetBrightness();
        Assert.True(normBrightness >= 0.0 && normBrightness <= 1.0);

        // SaveToFile — normalized
        var normPath = TempFile("dogfood_norm.pgm");
        norm.SaveToFile(normPath);
        Assert.True(File.Exists(normPath));
        Assert.True(new FileInfo(normPath).Length > 0);

        // LoadFile — normalized
        var loadedNorm = NetpbmImage.LoadFile(normPath);
        Assert.Equal(norm.Width, loadedNorm.Width);
        Assert.Equal(norm.Height, loadedNorm.Height);

        // GetHistogram on loaded
        var loadedHist = loadedNorm.GetHistogram();
        Assert.NotNull(loadedHist);
        Assert.Equal(loadedNorm.MaxVal + 1, loadedHist.Length);

        // Histogram sum unchanged
        long loadedSum = 0;
        foreach (var c in loadedHist) loadedSum += c;
        Assert.Equal(32 * 32, (int)loadedSum);

        // GetBrightness consistent after save-load
        Assert.Equal(norm.GetBrightness(), loadedNorm.GetBrightness(), 3);

        // Original image operations still valid
        var origHist2 = img.GetHistogram();
        Assert.Equal(hist.Length, origHist2.Length);

        // Uniform images: brightness near extremes
        var dark = NetpbmImage.LoadFile(CreateUniformPgm(0));
        var bright = NetpbmImage.LoadFile(CreateUniformPgm(255));
        Assert.True(dark.GetBrightness() < 0.01);
        Assert.True(bright.GetBrightness() > 0.99);

        // Uniform histogram: single bin
        var darkHist = dark.GetHistogram();
        Assert.Equal(8 * 8, (int)darkHist[0]);

        // Second normalize round-trip
        var norm2 = loadedNorm.Normalize();
        var path2 = TempFile("dogfood_norm2.pgm");
        norm2.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NetpbmImage.LoadFile(path2);
        Assert.Equal(norm2.Width, loaded2.Width);
        Assert.Equal(norm2.Height, loaded2.Height);
        Assert.True(loaded2.GetBrightness() >= 0.0 && loaded2.GetBrightness() <= 1.0);
    }
}
