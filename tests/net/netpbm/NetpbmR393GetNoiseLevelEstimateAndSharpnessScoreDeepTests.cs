// Tests for NetpbmImage.GetNoiseLevelEstimate, GetSharpnessScore deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R393

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R393: Tests for NetpbmImage.GetNoiseLevelEstimate, GetSharpnessScore deeper.
/// GetNoiseLevelEstimate(): returns an estimate of noise in the image; non-negative.
/// GetSharpnessScore(): returns an estimate of image sharpness; non-negative.
/// Covers: GetNoiseLevelEstimate no-throw; GetNoiseLevelEstimate non-negative;
/// GetNoiseLevelEstimate zero for uniform; GetNoiseLevelEstimate consistent; GetNoiseLevelEstimate save-load;
/// GetSharpnessScore no-throw; GetSharpnessScore non-negative;
/// GetSharpnessScore consistent; GetSharpnessScore save-load;
/// GetSharpnessScore higher for high-contrast image than uniform; dogfood pipeline.
/// </summary>
public class NetpbmR393GetNoiseLevelEstimateAndSharpnessScoreDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR393GetNoiseLevelEstimateAndSharpnessScoreDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR393_" + Guid.NewGuid().ToString("N"));
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

    private string CreateCheckerboardPgm(string name, int width, int height, int blockSize = 8)
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
                int block = (x / blockSize + y / blockSize) % 2;
                row.Append(block == 0 ? 0 : 255);
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateNoisyPgm(string name, int width, int height, int baseVal, int noiseAmp)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        var rng = new Random(999);
        for (int y = 0; y < height; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < width; x++)
            {
                if (x > 0) row.Append(' ');
                int val = Math.Max(0, Math.Min(255, baseVal + rng.Next(-noiseAmp, noiseAmp + 1)));
                row.Append(val);
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetNoiseLevelEstimate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNoiseLevelEstimate_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm("noisy.pgm", 40, 40, 128, 30));
        var ex = Record.Exception(() => img.GetNoiseLevelEstimate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetNoiseLevelEstimate_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm("noisy.pgm", 40, 40, 128, 30));
        Assert.True(img.GetNoiseLevelEstimate() >= 0.0);
    }

    [Fact]
    public void GetNoiseLevelEstimate_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform.pgm", 40, 40, 128));
        Assert.Equal(0.0, img.GetNoiseLevelEstimate(), precision: 6);
    }

    [Fact]
    public void GetNoiseLevelEstimate_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm("noisy.pgm", 40, 40, 128, 30));
        Assert.Equal(img.GetNoiseLevelEstimate(), img.GetNoiseLevelEstimate());
    }

    [Fact]
    public void GetNoiseLevelEstimate_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm("noisy.pgm", 40, 40, 128, 30));
        var before = img.GetNoiseLevelEstimate();
        var path = TempFile("noise_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetNoiseLevelEstimate(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetSharpnessScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSharpnessScore_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm("checker.pgm", 40, 40));
        var ex = Record.Exception(() => img.GetSharpnessScore());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSharpnessScore_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm("checker.pgm", 40, 40));
        Assert.True(img.GetSharpnessScore() >= 0.0);
    }

    [Fact]
    public void GetSharpnessScore_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm("checker.pgm", 40, 40));
        Assert.Equal(img.GetSharpnessScore(), img.GetSharpnessScore());
    }

    [Fact]
    public void GetSharpnessScore_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm("checker.pgm", 40, 40));
        var before = img.GetSharpnessScore();
        var path = TempFile("sharp_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetSharpnessScore(), precision: 6);
    }

    [Fact]
    public void GetSharpnessScore_Higher_ForHighContrastImage()
    {
        var checker = NetpbmImage.LoadFile(CreateCheckerboardPgm("checker.pgm", 40, 40));
        var uniform = NetpbmImage.LoadFile(CreateUniformPgm("uniform.pgm", 40, 40, 128));
        Assert.True(checker.GetSharpnessScore() >= uniform.GetSharpnessScore());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetNoiseLevelEstimate_GetSharpnessScore_Pipeline()
    {
        // Space — UK Space Agency / SSTL: Earth Observation Satellite Imagery QA
        // PGM images from small satellite sensors: noise and sharpness QA for data publication
        // Noise level determines required preprocessing; sharpness gates product tier classification

        // Scene 1: Clean, well-focused optical sensor image (low noise, high sharpness)
        var path1 = TempFile("sstl_clean_optical.pgm");
        {
            int w = 64, h = 64;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            // Simulate crisp urban scene: strong edges at regular intervals, minimal noise
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    int block = (x / 8 + y / 8) % 2;
                    row.Append(block == 0 ? 20 : 210);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path1, sb.ToString());
        }

        // Scene 2: Noisy SAR-like image (high noise, moderate sharpness)
        var path2 = TempFile("sstl_noisy_sar.pgm");
        {
            int w = 64, h = 64;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240701);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // SAR speckle: random variation around 128
                    int base_val = (x / 16 + y / 16) % 2 == 0 ? 80 : 170;
                    int speckle = rng.Next(-40, 41);
                    row.Append(Math.Max(0, Math.Min(255, base_val + speckle)));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path2, sb.ToString());
        }

        // Scene 3: Smooth cloud/ocean image (low noise, low sharpness)
        var path3 = TempFile("sstl_smooth_ocean.pgm");
        {
            int w = 64, h = 64;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240702);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // Gentle gradient variation — smooth ocean surface
                    int val = 100 + (int)(30 * Math.Sin(x * 0.3) * Math.Cos(y * 0.2)) + rng.Next(-3, 4);
                    row.Append(Math.Max(0, Math.Min(255, val)));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path3, sb.ToString());
        }

        var img1 = NetpbmImage.LoadFile(path1);
        var img2 = NetpbmImage.LoadFile(path2);
        var img3 = NetpbmImage.LoadFile(path3);

        // Noise level estimates
        var noise1 = img1.GetNoiseLevelEstimate();
        var noise2 = img2.GetNoiseLevelEstimate();
        var noise3 = img3.GetNoiseLevelEstimate();
        Assert.True(noise1 >= 0.0);
        Assert.True(noise2 >= 0.0);
        Assert.True(noise3 >= 0.0);
        // SAR image should have more noise than smooth ocean
        Assert.True(noise2 >= noise3);
        Assert.Equal(noise1, img1.GetNoiseLevelEstimate()); // consistent
        Assert.Equal(noise2, img2.GetNoiseLevelEstimate()); // consistent

        // Sharpness scores
        var sharp1 = img1.GetSharpnessScore();
        var sharp2 = img2.GetSharpnessScore();
        var sharp3 = img3.GetSharpnessScore();
        Assert.True(sharp1 >= 0.0);
        Assert.True(sharp2 >= 0.0);
        Assert.True(sharp3 >= 0.0);
        // Clean optical (checkerboard-like) should be sharper than smooth ocean
        Assert.True(sharp1 >= sharp3);
        Assert.Equal(sharp1, img1.GetSharpnessScore()); // consistent
        Assert.Equal(sharp3, img3.GetSharpnessScore()); // consistent

        // Uniform reference: zero noise
        var uniformPath = TempFile("sstl_uniform_ref.pgm");
        {
            var sb = new StringBuilder();
            sb.AppendLine("P2"); sb.AppendLine("32 32"); sb.AppendLine("255");
            for (int y = 0; y < 32; y++) { var row = new StringBuilder(); for (int x = 0; x < 32; x++) { if (x > 0) row.Append(' '); row.Append(100); } sb.AppendLine(row.ToString()); }
            File.WriteAllText(uniformPath, sb.ToString());
        }
        var uniform = NetpbmImage.LoadFile(uniformPath);
        Assert.Equal(0.0, uniform.GetNoiseLevelEstimate(), precision: 6);

        // SaveToFile
        var out1 = TempFile("sstl_clean_out.pgm");
        img1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        var loaded1 = NetpbmImage.LoadFile(out1);
        Assert.Equal(noise1, loaded1.GetNoiseLevelEstimate(), precision: 6);
        Assert.Equal(sharp1, loaded1.GetSharpnessScore(), precision: 6);

        var out2 = TempFile("sstl_sar_out.pgm");
        img2.SaveToFile(out2);
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.Equal(noise2, loaded2.GetNoiseLevelEstimate(), precision: 6);
        Assert.Equal(sharp2, loaded2.GetSharpnessScore(), precision: 6);

        var ex1 = Record.Exception(() => loaded1.GetNoiseLevelEstimate());
        var ex2 = Record.Exception(() => loaded2.GetSharpnessScore());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
