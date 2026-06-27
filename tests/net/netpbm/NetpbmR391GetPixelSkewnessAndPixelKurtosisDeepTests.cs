// Tests for NetpbmImage.GetPixelSkewness, GetPixelKurtosis deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R391

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R391: Tests for NetpbmImage.GetPixelSkewness, GetPixelKurtosis deeper.
/// GetPixelSkewness(): returns the skewness of the pixel intensity distribution.
/// GetPixelKurtosis(): returns the kurtosis of the pixel intensity distribution.
/// Covers: GetPixelSkewness no-throw; GetPixelSkewness finite;
/// GetPixelSkewness zero for uniform; GetPixelSkewness consistent; GetPixelSkewness save-load;
/// GetPixelKurtosis no-throw; GetPixelKurtosis finite;
/// GetPixelKurtosis consistent; GetPixelKurtosis save-load;
/// dogfood CreateImage→GetPixelSkewness→GetPixelKurtosis→SaveToFile pipeline.
/// </summary>
public class NetpbmR391GetPixelSkewnessAndPixelKurtosisDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR391GetPixelSkewnessAndPixelKurtosisDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR391_" + Guid.NewGuid().ToString("N"));
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

    private string CreateLeftSkewedPgm(string name, int width, int height)
    {
        // Predominantly dark pixels with rare bright outliers → right-skewed (positive skewness)
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        var rng = new Random(101);
        for (int y = 0; y < height; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < width; x++)
            {
                if (x > 0) row.Append(' ');
                int val = rng.NextDouble() < 0.05 ? rng.Next(200, 256) : rng.Next(0, 80);
                row.Append(val);
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
                int val = (int)(255.0 * x / (width - 1));
                row.Append(val);
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetPixelSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelSkewness_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var ex = Record.Exception(() => img.GetPixelSkewness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPixelSkewness_Finite()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var sk = img.GetPixelSkewness();
        Assert.True(!double.IsNaN(sk) && !double.IsInfinity(sk));
    }

    [Fact]
    public void GetPixelSkewness_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform.pgm", 40, 40, 128));
        Assert.Equal(0.0, img.GetPixelSkewness(), precision: 6);
    }

    [Fact]
    public void GetPixelSkewness_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.Equal(img.GetPixelSkewness(), img.GetPixelSkewness());
    }

    [Fact]
    public void GetPixelSkewness_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var before = img.GetPixelSkewness();
        var path = TempFile("sk_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetPixelSkewness(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetPixelKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelKurtosis_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var ex = Record.Exception(() => img.GetPixelKurtosis());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPixelKurtosis_Finite()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var kurt = img.GetPixelKurtosis();
        Assert.True(!double.IsNaN(kurt) && !double.IsInfinity(kurt));
    }

    [Fact]
    public void GetPixelKurtosis_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.Equal(img.GetPixelKurtosis(), img.GetPixelKurtosis());
    }

    [Fact]
    public void GetPixelKurtosis_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var before = img.GetPixelKurtosis();
        var path = TempFile("kurt_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetPixelKurtosis(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetPixelSkewness_GetPixelKurtosis_Pipeline()
    {
        // Forensics — Home Office / NPCC: Facial Recognition System Validation
        // Grayscale passport photos processed through facial recognition pipeline
        // Skewness/kurtosis of intensity distribution characterise image quality and exposure

        // Scene 1: Well-exposed reference face (normal distribution, near-zero skew)
        var path1 = TempFile("face_well_exposed.pgm");
        {
            int w = 60, h = 80;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240610);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // Normal around 128 ± 40
                    double u1 = rng.NextDouble(), u2 = rng.NextDouble();
                    double normal = Math.Sqrt(-2 * Math.Log(u1)) * Math.Cos(2 * Math.PI * u2);
                    int val = Math.Max(0, Math.Min(255, (int)(128 + 40 * normal)));
                    row.Append(val);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path1, sb.ToString());
        }

        // Scene 2: Over-exposed (right-skewed, heavy tail at 255)
        var path2 = TempFile("face_over_exposed.pgm");
        {
            int w = 60, h = 80;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240611);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // Clustered around 200-255 with some clipping
                    int val = Math.Min(255, 190 + rng.Next(0, 70));
                    row.Append(val);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path2, sb.ToString());
        }

        // Scene 3: Under-exposed (left-skewed, heavy at 0-50)
        var path3 = TempFile("face_under_exposed.pgm");
        {
            int w = 60, h = 80;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240612);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // Clustered around 0-60
                    int val = Math.Max(0, rng.Next(0, 65));
                    row.Append(val);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path3, sb.ToString());
        }

        var img1 = NetpbmImage.LoadFile(path1);
        var img2 = NetpbmImage.LoadFile(path2);
        var img3 = NetpbmImage.LoadFile(path3);

        // Skewness — finite and consistent
        var sk1 = img1.GetPixelSkewness();
        var sk2 = img2.GetPixelSkewness();
        var sk3 = img3.GetPixelSkewness();
        Assert.True(!double.IsNaN(sk1) && !double.IsInfinity(sk1));
        Assert.True(!double.IsNaN(sk2) && !double.IsInfinity(sk2));
        Assert.True(!double.IsNaN(sk3) && !double.IsInfinity(sk3));
        Assert.Equal(sk1, img1.GetPixelSkewness()); // consistent
        Assert.Equal(sk2, img2.GetPixelSkewness()); // consistent

        // Kurtosis — finite and consistent
        var kurt1 = img1.GetPixelKurtosis();
        var kurt2 = img2.GetPixelKurtosis();
        var kurt3 = img3.GetPixelKurtosis();
        Assert.True(!double.IsNaN(kurt1) && !double.IsInfinity(kurt1));
        Assert.True(!double.IsNaN(kurt2) && !double.IsInfinity(kurt2));
        Assert.True(!double.IsNaN(kurt3) && !double.IsInfinity(kurt3));
        Assert.Equal(kurt1, img1.GetPixelKurtosis()); // consistent
        Assert.Equal(kurt3, img3.GetPixelKurtosis()); // consistent

        // Uniform image
        var uniformPath = TempFile("uniform_passport.pgm");
        {
            var sb = new StringBuilder();
            sb.AppendLine("P2"); sb.AppendLine("40 40"); sb.AppendLine("255");
            for (int y = 0; y < 40; y++) { var row = new StringBuilder(); for (int x = 0; x < 40; x++) { if (x > 0) row.Append(' '); row.Append(150); } sb.AppendLine(row.ToString()); }
            File.WriteAllText(uniformPath, sb.ToString());
        }
        var uniform = NetpbmImage.LoadFile(uniformPath);
        Assert.Equal(0.0, uniform.GetPixelSkewness(), precision: 6);

        // SaveToFile
        var out1 = TempFile("face_well_out.pgm");
        img1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loaded1 = NetpbmImage.LoadFile(out1);
        Assert.Equal(sk1, loaded1.GetPixelSkewness(), precision: 6);
        Assert.Equal(kurt1, loaded1.GetPixelKurtosis(), precision: 6);

        var out2 = TempFile("face_over_out.pgm");
        img2.SaveToFile(out2);
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.Equal(sk2, loaded2.GetPixelSkewness(), precision: 6);
        Assert.Equal(kurt2, loaded2.GetPixelKurtosis(), precision: 6);

        var ex1 = Record.Exception(() => loaded1.GetPixelSkewness());
        var ex2 = Record.Exception(() => loaded2.GetPixelKurtosis());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
