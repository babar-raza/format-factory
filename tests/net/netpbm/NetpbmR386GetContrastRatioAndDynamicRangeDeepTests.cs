// Tests for NetpbmImage.GetContrastRatio, GetDynamicRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R386

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R386: Tests for NetpbmImage.GetContrastRatio, GetDynamicRange deeper.
/// GetContrastRatio(): returns (max_intensity - min_intensity) / max_intensity; [0,1].
/// GetDynamicRange(): returns the number of distinct pixel intensity levels present.
/// Covers: GetContrastRatio no-throw; GetContrastRatio in-range; GetContrastRatio zero for uniform;
/// GetContrastRatio consistent; GetContrastRatio save-load;
/// GetDynamicRange no-throw; GetDynamicRange positive; GetDynamicRange one for uniform;
/// GetDynamicRange consistent; GetDynamicRange save-load;
/// dogfood pipeline.
/// </summary>
public class NetpbmR386GetContrastRatioAndDynamicRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR386GetContrastRatioAndDynamicRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR386_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateUniformPgm(string name, int w, int h, int intensity)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{w} {h}");
        sb.AppendLine("255");
        for (int y = 0; y < h; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < w; x++) { if (x > 0) row.Append(' '); row.Append(intensity); }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateHighContrastPgm(string name)
    {
        // Pure black (0) and pure white (255) halves
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("40 40");
        sb.AppendLine("255");
        for (int y = 0; y < 40; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < 40; x++) { if (x > 0) row.Append(' '); row.Append(x < 20 ? 0 : 255); }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateGradientPgm(string name)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("50 50");
        sb.AppendLine("255");
        for (int y = 0; y < 50; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < 50; x++) { if (x > 0) row.Append(' '); row.Append((int)(255.0 * x / 49)); }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetContrastRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContrastRatio_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateHighContrastPgm("high.pgm"));
        var ex = Record.Exception(() => img.GetContrastRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContrastRatio_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateHighContrastPgm("high.pgm"));
        var r = img.GetContrastRatio();
        Assert.True(r >= 0.0 && r <= 1.0);
    }

    [Fact]
    public void GetContrastRatio_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform.pgm", 40, 40, 128));
        Assert.Equal(0.0, img.GetContrastRatio(), precision: 6);
    }

    [Fact]
    public void GetContrastRatio_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateHighContrastPgm("high.pgm"));
        Assert.Equal(img.GetContrastRatio(), img.GetContrastRatio());
    }

    [Fact]
    public void GetContrastRatio_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm"));
        var before = img.GetContrastRatio();
        var path = TempFile("cr_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetContrastRatio(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetDynamicRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDynamicRange_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm"));
        var ex = Record.Exception(() => img.GetDynamicRange());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDynamicRange_Positive()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm"));
        Assert.True(img.GetDynamicRange() > 0);
    }

    [Fact]
    public void GetDynamicRange_One_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform.pgm", 40, 40, 200));
        Assert.Equal(1, img.GetDynamicRange());
    }

    [Fact]
    public void GetDynamicRange_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm"));
        Assert.Equal(img.GetDynamicRange(), img.GetDynamicRange());
    }

    [Fact]
    public void GetDynamicRange_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm"));
        var before = img.GetDynamicRange();
        var path = TempFile("dr_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetDynamicRange());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetContrastRatio_GetDynamicRange_Pipeline()
    {
        // Cultural Heritage — Historic England: Digital Survey of Grade I Listed Buildings
        // PGM photographs of architectural stonework for condition assessment
        // Contrast ratio detects weathering; dynamic range quantifies tonal richness

        // Image 1: High-quality external elevation photo (wide tonal range, high contrast)
        var path1 = TempFile("hist_eng_ely_cathedral_west_front.pgm");
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
                    // Wide tonal range: shadow areas 10-60, mid-tone masonry 100-170, highlight sky 200-250
                    int zone = x / (w / 3);
                    int val = zone == 0 ? rng.Next(10, 60) : zone == 1 ? rng.Next(100, 170) : rng.Next(200, 251);
                    row.Append(val);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path1, sb.ToString());
        }

        // Image 2: Weathered internal stonework (low contrast, narrow tonal range)
        var path2 = TempFile("hist_eng_durham_cathedral_interior.pgm");
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
                    // Uniform grey stone interior: 100-160 only (limited dynamic range)
                    row.Append(rng.Next(100, 161));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path2, sb.ToString());
        }

        // Image 3: Uniform reference (painted wall, single tone)
        var path3 = TempFile("hist_eng_reference_whitewash.pgm");
        {
            int w = 40, h = 40;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++) { if (x > 0) row.Append(' '); row.Append(230); }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path3, sb.ToString());
        }

        var img1 = NetpbmImage.LoadFile(path1);
        var img2 = NetpbmImage.LoadFile(path2);
        var img3 = NetpbmImage.LoadFile(path3);

        // Contrast ratio: exterior > interior > uniform
        var cr1 = img1.GetContrastRatio();
        var cr2 = img2.GetContrastRatio();
        var cr3 = img3.GetContrastRatio();
        Assert.True(cr1 >= 0.0 && cr1 <= 1.0);
        Assert.True(cr2 >= 0.0 && cr2 <= 1.0);
        Assert.Equal(0.0, cr3, precision: 6); // uniform → zero contrast
        Assert.True(cr1 > cr2); // exterior > interior
        Assert.Equal(cr1, img1.GetContrastRatio()); // consistent
        Assert.Equal(cr2, img2.GetContrastRatio()); // consistent

        // Dynamic range: exterior > interior > 1
        var dr1 = img1.GetDynamicRange();
        var dr2 = img2.GetDynamicRange();
        var dr3 = img3.GetDynamicRange();
        Assert.True(dr1 > 0);
        Assert.True(dr2 > 0);
        Assert.Equal(1, dr3); // uniform → exactly 1 distinct level
        Assert.True(dr1 > dr2); // exterior has more tonal variety
        Assert.Equal(dr1, img1.GetDynamicRange()); // consistent

        // SaveToFile
        var out1 = TempFile("ely_cathedral_out.pgm");
        img1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        var loaded1 = NetpbmImage.LoadFile(out1);
        Assert.Equal(cr1, loaded1.GetContrastRatio(), precision: 6);
        Assert.Equal(dr1, loaded1.GetDynamicRange());

        var out2 = TempFile("durham_cathedral_out.pgm");
        img2.SaveToFile(out2);
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.Equal(cr2, loaded2.GetContrastRatio(), precision: 6);
        Assert.Equal(dr2, loaded2.GetDynamicRange());

        var ex1 = Record.Exception(() => loaded1.GetContrastRatio());
        var ex2 = Record.Exception(() => loaded1.GetDynamicRange());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
