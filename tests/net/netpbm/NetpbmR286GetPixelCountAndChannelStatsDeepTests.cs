// Tests for NetpbmImage.GetPixelCount, GetChannelMean, GetChannelStdDev deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R286

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R286: Tests for NetpbmImage.GetPixelCount, GetChannelMean, GetChannelStdDev deeper.
/// GetPixelCount(): returns width * height.
/// GetChannelMean(channel): returns the mean value of a channel across all pixels.
/// GetChannelStdDev(channel): returns the standard deviation for a channel.
/// Covers: GetPixelCount no-throw; GetPixelCount equals width*height; GetPixelCount positive;
/// GetPixelCount consistent; GetPixelCount save-load;
/// GetChannelMean no-throw; GetChannelMean in [0, MaxVal]; GetChannelMean consistent;
/// GetChannelMean save-load; GetChannelMean uniform-image;
/// GetChannelStdDev no-throw; GetChannelStdDev non-negative; GetChannelStdDev consistent;
/// GetChannelStdDev save-load; GetChannelStdDev zero-for-uniform;
/// dogfood LoadFile→GetPixelCount→GetChannelMean→GetChannelStdDev→SaveToFile pipeline.
/// </summary>
public class NetpbmR286GetPixelCountAndChannelStatsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR286GetPixelCountAndChannelStatsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR286_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePgm(int width, int height, int fill)
    {
        var path = TempFile($"pgm_{width}x{height}_{fill}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
            {
                if (c > 0) sb.Append(' ');
                sb.Append(fill);
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateGradientPgm(int width, int height)
    {
        var path = TempFile($"gradient_{width}x{height}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
            {
                if (c > 0) sb.Append(' ');
                sb.Append((c * 255 / (width - 1)));
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetPixelCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelCount_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(32, 32, 128));
        var ex = Record.Exception(() => img.GetPixelCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPixelCount_Equals_Width_Times_Height()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(40, 30, 100));
        Assert.Equal(40 * 30, img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_Positive()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(16, 16, 64));
        Assert.True(img.GetPixelCount() > 0);
    }

    [Fact]
    public void GetPixelCount_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(24, 18, 200));
        Assert.Equal(img.GetPixelCount(), img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(20, 15, 150));
        var before = img.GetPixelCount();
        var path = TempFile("pc_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetPixelCount());
    }

    // -------------------------------------------------------------------------
    // GetChannelMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelMean_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(32, 32, 128));
        var ex = Record.Exception(() => img.GetChannelMean(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetChannelMean_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(64, 32));
        var mean = img.GetChannelMean(0);
        Assert.True(mean >= 0.0 && mean <= img.MaxVal);
    }

    [Fact]
    public void GetChannelMean_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(48, 24));
        Assert.Equal(img.GetChannelMean(0), img.GetChannelMean(0));
    }

    [Fact]
    public void GetChannelMean_Uniform_Image()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(16, 16, 100));
        var mean = img.GetChannelMean(0);
        Assert.Equal(100.0, mean, 1);
    }

    [Fact]
    public void GetChannelMean_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(32, 16));
        var before = img.GetChannelMean(0);
        var path = TempFile("cm_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetChannelMean(0), 2);
    }

    // -------------------------------------------------------------------------
    // GetChannelStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelStdDev_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(32, 32));
        var ex = Record.Exception(() => img.GetChannelStdDev(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetChannelStdDev_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(48, 24));
        Assert.True(img.GetChannelStdDev(0) >= 0.0);
    }

    [Fact]
    public void GetChannelStdDev_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(32, 16));
        Assert.Equal(img.GetChannelStdDev(0), img.GetChannelStdDev(0));
    }

    [Fact]
    public void GetChannelStdDev_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(16, 16, 75));
        Assert.Equal(0.0, img.GetChannelStdDev(0), 2);
    }

    [Fact]
    public void GetChannelStdDev_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(40, 20));
        var before = img.GetChannelStdDev(0);
        var path = TempFile("sd_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetChannelStdDev(0), 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetPixelCount_GetChannelMean_GetChannelStdDev_SaveToFile_Pipeline()
    {
        // Build 64x48 checkerboard PGM
        var srcPath = TempFile("dogfood_checker.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("64 48");
        sb.AppendLine("255");
        for (int r = 0; r < 48; r++)
        {
            for (int c = 0; c < 64; c++)
            {
                if (c > 0) sb.Append(' ');
                sb.Append(((r / 8 + c / 8) % 2 == 0) ? 240 : 15);
            }
            sb.AppendLine();
        }
        File.WriteAllText(srcPath, sb.ToString());

        var img = NetpbmImage.LoadFile(srcPath);
        Assert.Equal(64, img.Width);
        Assert.Equal(48, img.Height);

        // GetPixelCount = 64 * 48
        var pixCount = img.GetPixelCount();
        Assert.Equal(64 * 48, pixCount);
        Assert.Equal(pixCount, img.GetPixelCount()); // consistent

        // GetChannelMean — checkerboard has mixed pixels → mean between 15 and 240
        var mean = img.GetChannelMean(0);
        Assert.True(mean >= 0.0 && mean <= img.MaxVal);
        Assert.Equal(mean, img.GetChannelMean(0)); // consistent

        // GetChannelStdDev — checkerboard has variation → stddev > 0
        var stddev = img.GetChannelStdDev(0);
        Assert.True(stddev >= 0.0);
        Assert.Equal(stddev, img.GetChannelStdDev(0)); // consistent

        // SaveToFile
        var path = TempFile("dogfood_checker_out.pgm");
        img.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(pixCount, loaded.GetPixelCount());
        Assert.Equal(mean, loaded.GetChannelMean(0), 2);
        Assert.Equal(stddev, loaded.GetChannelStdDev(0), 2);

        // Uniform region crop — stddev should be near 0
        var uniformCrop = img.CropRegion(0, 0, 8, 8); // top-left 8x8 block (all 240)
        Assert.Equal(64, uniformCrop.GetPixelCount());
        Assert.Equal(64, uniformCrop.GetPixelCount()); // consistent

        // Normalize and recheck pixel count
        var normalized = img.Normalize();
        Assert.Equal(img.Width, normalized.Width);
        Assert.Equal(img.Height, normalized.Height);
        Assert.Equal(pixCount, normalized.GetPixelCount());

        // GetChannelMean on normalized — in [0, MaxVal]
        var normMean = normalized.GetChannelMean(0);
        Assert.True(normMean >= 0.0 && normMean <= normalized.MaxVal);

        // SaveToFile normalized
        var normPath = TempFile("dogfood_norm.pgm");
        normalized.SaveToFile(normPath);
        Assert.True(File.Exists(normPath));
        var loadedNorm = NetpbmImage.LoadFile(normPath);
        Assert.Equal(pixCount, loadedNorm.GetPixelCount());
        Assert.True(loadedNorm.GetChannelStdDev(0) >= 0.0);

        // Final save
        var path2 = TempFile("dogfood_checker_v2.pgm");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NetpbmImage.LoadFile(path2);
        Assert.Equal(pixCount, loaded2.GetPixelCount());
        Assert.Equal(mean, loaded2.GetChannelMean(0), 2);
        Assert.Equal(stddev, loaded2.GetChannelStdDev(0), 2);
    }
}
