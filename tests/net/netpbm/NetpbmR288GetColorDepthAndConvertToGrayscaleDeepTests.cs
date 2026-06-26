// Tests for NetpbmImage.GetColorDepth, ConvertToGrayscale, GetChannelCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R288

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R288: Tests for NetpbmImage.GetColorDepth, ConvertToGrayscale, GetChannelCount deeper.
/// GetColorDepth(): returns the bit depth per channel (log2(MaxVal+1)).
/// ConvertToGrayscale(): returns a PGM-format grayscale version of the image.
/// GetChannelCount(): returns the number of channels (1 for PGM, 3 for PPM).
/// Covers: GetColorDepth no-throw; GetColorDepth positive; GetColorDepth consistent;
/// GetColorDepth save-load; GetColorDepth leq 16 for standard images;
/// ConvertToGrayscale no-throw; ConvertToGrayscale same dims; ConvertToGrayscale channel-count-1;
/// ConvertToGrayscale save-load; ConvertToGrayscale consistent MaxVal;
/// GetChannelCount no-throw; GetChannelCount positive; GetChannelCount consistent;
/// GetChannelCount save-load; GetChannelCount pgm-is-1;
/// dogfood LoadFile→GetColorDepth→ConvertToGrayscale→GetChannelCount→SaveToFile pipeline.
/// </summary>
public class NetpbmR288GetColorDepthAndConvertToGrayscaleDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR288GetColorDepthAndConvertToGrayscaleDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR288_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePgm(int width, int height, int fill = 128)
    {
        var path = TempFile($"pgm_{width}x{height}.pgm");
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

    private string CreatePpm(int width, int height)
    {
        var path = TempFile($"ppm_{width}x{height}.ppm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P3");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
            {
                if (c > 0) sb.Append(' ');
                sb.Append($"{c % 256} {r % 256} {(c + r) % 256}");
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColorDepth
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorDepth_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(32, 32));
        var ex = Record.Exception(() => img.GetColorDepth());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColorDepth_Positive()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(16, 16));
        Assert.True(img.GetColorDepth() > 0);
    }

    [Fact]
    public void GetColorDepth_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(24, 24));
        Assert.Equal(img.GetColorDepth(), img.GetColorDepth());
    }

    [Fact]
    public void GetColorDepth_Leq_16_ForStandard()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(16, 16));
        Assert.True(img.GetColorDepth() <= 16);
    }

    [Fact]
    public void GetColorDepth_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(20, 20));
        var before = img.GetColorDepth();
        var path = TempFile("cd_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetColorDepth());
    }

    // -------------------------------------------------------------------------
    // ConvertToGrayscale
    // -------------------------------------------------------------------------

    [Fact]
    public void ConvertToGrayscale_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(32, 32));
        var ex = Record.Exception(() => img.ConvertToGrayscale());
        Assert.Null(ex);
    }

    [Fact]
    public void ConvertToGrayscale_Same_Dims()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(40, 30));
        var gray = img.ConvertToGrayscale();
        Assert.Equal(img.Width, gray.Width);
        Assert.Equal(img.Height, gray.Height);
    }

    [Fact]
    public void ConvertToGrayscale_Channel_Count_One()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(16, 16));
        var gray = img.ConvertToGrayscale();
        Assert.Equal(1, gray.GetChannelCount());
    }

    [Fact]
    public void ConvertToGrayscale_Consistent_MaxVal()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(24, 24));
        var gray = img.ConvertToGrayscale();
        Assert.Equal(img.MaxVal, gray.MaxVal);
    }

    [Fact]
    public void ConvertToGrayscale_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(32, 32));
        var gray = img.ConvertToGrayscale();
        var path = TempFile("gray_save.pgm");
        gray.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(gray.Width, loaded.Width);
        Assert.Equal(gray.Height, loaded.Height);
        Assert.Equal(1, loaded.GetChannelCount());
    }

    // -------------------------------------------------------------------------
    // GetChannelCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelCount_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(16, 16));
        var ex = Record.Exception(() => img.GetChannelCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChannelCount_Positive()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(16, 16));
        Assert.True(img.GetChannelCount() > 0);
    }

    [Fact]
    public void GetChannelCount_Pgm_Is_One()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(16, 16));
        Assert.Equal(1, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(20, 20));
        Assert.Equal(img.GetChannelCount(), img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(16, 16));
        var before = img.GetChannelCount();
        var path = TempFile("cc_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetChannelCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColorDepth_ConvertToGrayscale_GetChannelCount_SaveToFile_Pipeline()
    {
        // Build 48x36 gradient PGM
        var srcPath = TempFile("dogfood_gradient.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("48 36");
        sb.AppendLine("255");
        for (int r = 0; r < 36; r++)
        {
            for (int c = 0; c < 48; c++)
            {
                if (c > 0) sb.Append(' ');
                sb.Append((r * 7 + c * 3) % 256);
            }
            sb.AppendLine();
        }
        File.WriteAllText(srcPath, sb.ToString());

        var img = NetpbmImage.LoadFile(srcPath);
        Assert.Equal(48, img.Width);
        Assert.Equal(36, img.Height);

        // GetChannelCount — PGM is 1
        var channels = img.GetChannelCount();
        Assert.True(channels > 0);
        Assert.Equal(channels, img.GetChannelCount()); // consistent

        // GetColorDepth — MaxVal=255 → 8 bits
        var depth = img.GetColorDepth();
        Assert.True(depth > 0);
        Assert.True(depth <= 16);
        Assert.Equal(depth, img.GetColorDepth()); // consistent

        // ConvertToGrayscale — PGM is already grayscale
        var gray = img.ConvertToGrayscale();
        Assert.NotNull(gray);
        Assert.Equal(img.Width, gray.Width);
        Assert.Equal(img.Height, gray.Height);
        Assert.Equal(img.MaxVal, gray.MaxVal);
        Assert.Equal(1, gray.GetChannelCount());
        Assert.Equal(depth, gray.GetColorDepth());

        // Grayscale of grayscale is consistent
        var grayOfGray = gray.ConvertToGrayscale();
        Assert.Equal(gray.Width, grayOfGray.Width);
        Assert.Equal(gray.Height, grayOfGray.Height);
        Assert.Equal(1, grayOfGray.GetChannelCount());

        // SaveToFile — original
        var path = TempFile("dogfood_gradient_out.pgm");
        img.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify original
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);
        Assert.Equal(channels, loaded.GetChannelCount());
        Assert.Equal(depth, loaded.GetColorDepth());

        // SaveToFile — grayscale
        var grayPath = TempFile("dogfood_gray.pgm");
        gray.SaveToFile(grayPath);
        Assert.True(File.Exists(grayPath));
        var loadedGray = NetpbmImage.LoadFile(grayPath);
        Assert.Equal(gray.Width, loadedGray.Width);
        Assert.Equal(gray.Height, loadedGray.Height);
        Assert.Equal(1, loadedGray.GetChannelCount());
        Assert.Equal(gray.MaxVal, loadedGray.MaxVal);

        // Normalize and check channel count preserved
        var norm = img.Normalize();
        Assert.Equal(img.GetChannelCount(), norm.GetChannelCount());
        Assert.Equal(img.GetColorDepth(), norm.GetColorDepth());

        // Final save
        var path2 = TempFile("dogfood_gradient_v2.pgm");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NetpbmImage.LoadFile(path2);
        Assert.Equal(img.Width, loaded2.Width);
        Assert.Equal(img.Height, loaded2.Height);
        Assert.Equal(channels, loaded2.GetChannelCount());
        Assert.Equal(depth, loaded2.GetColorDepth());
    }
}
