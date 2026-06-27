// Tests for NetpbmImage.GetPixelStdDev, GetPixelVariance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R399

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R399: Tests for NetpbmImage.GetPixelStdDev, GetPixelVariance deeper.
/// GetPixelStdDev(): returns the standard deviation of pixel intensities.
/// GetPixelVariance(): returns the variance of pixel intensities; equals stddev².
/// Covers: GetPixelStdDev no-throw; GetPixelStdDev non-negative; GetPixelStdDev zero for uniform;
/// GetPixelStdDev consistent; GetPixelStdDev save-load;
/// GetPixelVariance no-throw; GetPixelVariance non-negative; GetPixelVariance zero for uniform;
/// GetPixelVariance consistent; GetPixelVariance save-load;
/// GetPixelVariance equals GetPixelStdDev squared; dogfood pipeline.
/// </summary>
public class NetpbmR399GetPixelStdDevAndPixelVarianceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR399GetPixelStdDevAndPixelVarianceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR399_" + Guid.NewGuid().ToString("N"));
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

    // -------------------------------------------------------------------------
    // GetPixelStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelStdDev_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var ex = Record.Exception(() => img.GetPixelStdDev());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPixelStdDev_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.True(img.GetPixelStdDev() >= 0.0);
    }

    [Fact]
    public void GetPixelStdDev_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform.pgm", 40, 40, 128));
        Assert.Equal(0.0, img.GetPixelStdDev(), precision: 4);
    }

    [Fact]
    public void GetPixelStdDev_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.Equal(img.GetPixelStdDev(), img.GetPixelStdDev());
    }

    [Fact]
    public void GetPixelStdDev_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var before = img.GetPixelStdDev();
        var path = TempFile("sd_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetPixelStdDev(), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetPixelVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelVariance_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var ex = Record.Exception(() => img.GetPixelVariance());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPixelVariance_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.True(img.GetPixelVariance() >= 0.0);
    }

    [Fact]
    public void GetPixelVariance_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform.pgm", 40, 40, 64));
        Assert.Equal(0.0, img.GetPixelVariance(), precision: 4);
    }

    [Fact]
    public void GetPixelVariance_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.Equal(img.GetPixelVariance(), img.GetPixelVariance());
    }

    [Fact]
    public void GetPixelVariance_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var before = img.GetPixelVariance();
        var path = TempFile("var_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetPixelVariance(), precision: 4);
    }

    [Fact]
    public void GetPixelVariance_Equals_StdDev_Squared()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var sd = img.GetPixelStdDev();
        var var_ = img.GetPixelVariance();
        Assert.Equal(sd * sd, var_, precision: 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetPixelStdDev_GetPixelVariance_Pipeline()
    {
        // Materials Science — EPSRC / Diamond Light Source: X-ray Diffraction Pattern Analysis
        // Grayscale detector images from powder diffraction experiments on pharmaceutical crystals
        // Pixel variance measures diffraction ring intensity spread; StdDev detects peak broadening

        // Sample 1: Sharp diffraction rings (crystalline — low variance within rings)
        var path1 = TempFile("xrd_crystalline_paracetamol.pgm");
        {
            int w = 64, h = 64;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240901);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // Simulate diffraction: bright rings at specific radii, dark background
                    double r = Math.Sqrt((x - w / 2.0) * (x - w / 2.0) + (y - h / 2.0) * (y - h / 2.0));
                    double rings = Math.Exp(-Math.Pow((r - 15) / 1.5, 2)) * 200
                                 + Math.Exp(-Math.Pow((r - 25) / 1.5, 2)) * 180
                                 + Math.Exp(-Math.Pow((r - 30) / 1.5, 2)) * 150;
                    int val = (int)Math.Min(255, rings + rng.Next(5));
                    row.Append(val);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path1, sb.ToString());
        }

        // Sample 2: Amorphous halo (no crystalline order — high variance, broad features)
        var path2 = TempFile("xrd_amorphous_peg.pgm");
        {
            int w = 64, h = 64;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240902);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    row.Append(rng.Next(0, 256)); // broad random distribution
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path2, sb.ToString());
        }

        // Sample 3: Uniform background (beam stop — zero variance)
        var path3 = TempFile("xrd_beamstop.pgm");
        {
            int w = 40, h = 40;
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
                    row.Append(10); // uniform dark beam stop region
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path3, sb.ToString());
        }

        var img1 = NetpbmImage.LoadFile(path1);
        var img2 = NetpbmImage.LoadFile(path2);
        var img3 = NetpbmImage.LoadFile(path3);

        // StdDev
        var sd1 = img1.GetPixelStdDev();
        var sd2 = img2.GetPixelStdDev();
        var sd3 = img3.GetPixelStdDev();

        Assert.True(sd1 >= 0.0);
        Assert.True(sd2 >= 0.0);
        Assert.Equal(0.0, sd3, precision: 4); // uniform beam stop

        // Variance
        var var1 = img1.GetPixelVariance();
        var var2 = img2.GetPixelVariance();
        var var3 = img3.GetPixelVariance();

        Assert.True(var1 >= 0.0);
        Assert.True(var2 >= 0.0);
        Assert.Equal(0.0, var3, precision: 4); // uniform beam stop

        // Variance = StdDev²
        Assert.Equal(sd1 * sd1, var1, precision: 2);
        Assert.Equal(sd2 * sd2, var2, precision: 2);

        // Consistency
        Assert.Equal(sd1, img1.GetPixelStdDev());
        Assert.Equal(var2, img2.GetPixelVariance());

        // SaveToFile
        var out1 = TempFile("xrd_crystalline_out.pgm");
        img1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loaded1 = NetpbmImage.LoadFile(out1);
        Assert.Equal(sd1, loaded1.GetPixelStdDev(), precision: 4);
        Assert.Equal(var1, loaded1.GetPixelVariance(), precision: 2);

        var out3 = TempFile("xrd_beamstop_out.pgm");
        img3.SaveToFile(out3);
        var loaded3 = NetpbmImage.LoadFile(out3);
        Assert.Equal(0.0, loaded3.GetPixelStdDev(), precision: 4);
        Assert.Equal(0.0, loaded3.GetPixelVariance(), precision: 4);

        var ex1 = Record.Exception(() => loaded1.GetPixelStdDev());
        var ex2 = Record.Exception(() => loaded3.GetPixelVariance());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
