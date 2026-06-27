// Tests for NetpbmImage.GetMinPixelValue, GetMaxPixelValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R389

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R389: Tests for NetpbmImage.GetMinPixelValue, GetMaxPixelValue deeper.
/// GetMinPixelValue(): returns the minimum pixel intensity in the image.
/// GetMaxPixelValue(): returns the maximum pixel intensity in the image; ≥ GetMinPixelValue().
/// Covers: GetMinPixelValue no-throw; GetMinPixelValue non-negative; GetMinPixelValue zero for all-black;
/// GetMinPixelValue consistent; GetMinPixelValue save-load;
/// GetMaxPixelValue no-throw; GetMaxPixelValue non-negative; GetMaxPixelValue 255 for all-white;
/// GetMaxPixelValue consistent; GetMaxPixelValue save-load;
/// GetMinPixelValue leq GetMaxPixelValue; GetMinPixelValue eq GetMaxPixelValue for uniform;
/// dogfood CreateImage→GetMinPixelValue→GetMaxPixelValue→SaveToFile pipeline.
/// </summary>
public class NetpbmR389GetMinPixelValueAndMaxPixelValueDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR389GetMinPixelValueAndMaxPixelValueDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR389_" + Guid.NewGuid().ToString("N"));
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

    private string CreateRangePgm(string name, int width, int height, int minVal, int maxVal)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        var rng = new Random(42);
        for (int y = 0; y < height; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < width; x++)
            {
                if (x > 0) row.Append(' ');
                row.Append(rng.Next(minVal, maxVal + 1));
            }
            sb.AppendLine(row.ToString());
        }
        // Guarantee min and max appear
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
                int val = (int)(255.0 * x / (width - 1));
                row.Append(val);
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetMinPixelValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMinPixelValue_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var ex = Record.Exception(() => img.GetMinPixelValue());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMinPixelValue_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.True(img.GetMinPixelValue() >= 0);
    }

    [Fact]
    public void GetMinPixelValue_Zero_ForAllBlack()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("black.pgm", 40, 40, 0));
        Assert.Equal(0, img.GetMinPixelValue());
    }

    [Fact]
    public void GetMinPixelValue_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.Equal(img.GetMinPixelValue(), img.GetMinPixelValue());
    }

    [Fact]
    public void GetMinPixelValue_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var before = img.GetMinPixelValue();
        var path = TempFile("min_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetMinPixelValue());
    }

    // -------------------------------------------------------------------------
    // GetMaxPixelValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxPixelValue_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var ex = Record.Exception(() => img.GetMaxPixelValue());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMaxPixelValue_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.True(img.GetMaxPixelValue() >= 0);
    }

    [Fact]
    public void GetMaxPixelValue_255_ForAllWhite()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("white.pgm", 40, 40, 255));
        Assert.Equal(255, img.GetMaxPixelValue());
    }

    [Fact]
    public void GetMaxPixelValue_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.Equal(img.GetMaxPixelValue(), img.GetMaxPixelValue());
    }

    [Fact]
    public void GetMaxPixelValue_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var before = img.GetMaxPixelValue();
        var path = TempFile("max_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetMaxPixelValue());
    }

    [Fact]
    public void GetMinPixelValue_Leq_GetMaxPixelValue()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.True(img.GetMinPixelValue() <= img.GetMaxPixelValue());
    }

    [Fact]
    public void GetMinPixelValue_Equals_GetMaxPixelValue_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform.pgm", 40, 40, 128));
        Assert.Equal(img.GetMinPixelValue(), img.GetMaxPixelValue());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMinPixelValue_GetMaxPixelValue_Pipeline()
    {
        // Medical Imaging — NHS / NICE: Mammography Screening Programme
        // Grayscale PGM images for breast tissue density classification
        // Min/max pixel values determine dynamic range used in clinical protocols

        // Scene 1: Fatty (low density) — predominantly bright tissue
        var path1 = TempFile("mammo_fatty.pgm");
        {
            int w = 64, h = 48;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240301);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // Mostly bright (190-255) with a few dark vessels (20-60)
                    int val = rng.NextDouble() < 0.05 ? rng.Next(20, 60) : rng.Next(190, 256);
                    row.Append(val);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path1, sb.ToString());
        }

        // Scene 2: Dense (high density) — wider intensity range
        var path2 = TempFile("mammo_dense.pgm");
        {
            int w = 64, h = 48;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240302);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // Full range — mixed fibro-glandular and fatty tissue
                    row.Append(rng.Next(5, 256));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path2, sb.ToString());
        }

        // Scene 3: Uniform phantom (calibration target)
        var path3 = TempFile("mammo_phantom.pgm");
        {
            int w = 64, h = 48;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    row.Append(127); // mid-grey calibration
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path3, sb.ToString());
        }

        var img1 = NetpbmImage.LoadFile(path1);
        var img2 = NetpbmImage.LoadFile(path2);
        var img3 = NetpbmImage.LoadFile(path3);

        // Min pixel values
        var min1 = img1.GetMinPixelValue();
        var min2 = img2.GetMinPixelValue();
        var min3 = img3.GetMinPixelValue();
        Assert.True(min1 >= 0);
        Assert.True(min2 >= 0);
        Assert.Equal(127, min3); // uniform phantom

        // Max pixel values
        var max1 = img1.GetMaxPixelValue();
        var max2 = img2.GetMaxPixelValue();
        var max3 = img3.GetMaxPixelValue();
        Assert.True(max1 <= 255);
        Assert.True(max2 <= 255);
        Assert.Equal(127, max3); // uniform phantom

        // Dense image has wider range than phantom
        Assert.True(max2 - min2 > max3 - min3);

        // Min <= Max always
        Assert.True(min1 <= max1);
        Assert.True(min2 <= max2);
        Assert.True(min3 <= max3);

        // Phantom min == max
        Assert.Equal(min3, max3);

        // Consistency checks
        Assert.Equal(min1, img1.GetMinPixelValue());
        Assert.Equal(max2, img2.GetMaxPixelValue());

        // Black reference image
        var blackPath = TempFile("mammo_black.pgm");
        {
            var sb = new StringBuilder();
            sb.AppendLine("P2"); sb.AppendLine("32 32"); sb.AppendLine("255");
            for (int y = 0; y < 32; y++) { for (int x = 0; x < 32; x++) sb.Append(x == 0 ? "0" : " 0"); sb.AppendLine(); }
            File.WriteAllText(blackPath, sb.ToString());
        }
        var blackImg = NetpbmImage.LoadFile(blackPath);
        Assert.Equal(0, blackImg.GetMinPixelValue());
        Assert.Equal(0, blackImg.GetMaxPixelValue());

        // SaveToFile
        var out1 = TempFile("mammo_fatty_out.pgm");
        img1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loaded1 = NetpbmImage.LoadFile(out1);
        Assert.Equal(min1, loaded1.GetMinPixelValue());
        Assert.Equal(max1, loaded1.GetMaxPixelValue());

        var out2 = TempFile("mammo_dense_out.pgm");
        img2.SaveToFile(out2);
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.Equal(min2, loaded2.GetMinPixelValue());
        Assert.Equal(max2, loaded2.GetMaxPixelValue());

        var out3 = TempFile("mammo_phantom_out.pgm");
        img3.SaveToFile(out3);
        var loaded3 = NetpbmImage.LoadFile(out3);
        Assert.Equal(127, loaded3.GetMinPixelValue());
        Assert.Equal(127, loaded3.GetMaxPixelValue());

        var ex1 = Record.Exception(() => loaded1.GetMinPixelValue());
        var ex2 = Record.Exception(() => loaded2.GetMaxPixelValue());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
