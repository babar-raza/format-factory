// Tests for NetpbmImage.GetLocalContrast, GetGlobalVariance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R376

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R376: Tests for NetpbmImage.GetLocalContrast, GetGlobalVariance deeper.
/// GetLocalContrast(): returns a measure of local contrast (average local pixel difference).
/// GetGlobalVariance(): returns the variance of pixel intensities across the entire image.
/// Covers: GetLocalContrast no-throw; GetLocalContrast non-negative; GetLocalContrast consistent;
/// GetLocalContrast zero for uniform; GetLocalContrast save-load;
/// GetGlobalVariance no-throw; GetGlobalVariance non-negative; GetGlobalVariance zero for uniform;
/// GetGlobalVariance consistent; GetGlobalVariance save-load;
/// GetGlobalVariance higher for high-contrast image; dogfood pipeline.
/// </summary>
public class NetpbmR376GetLocalContrastAndGlobalVarianceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR376GetLocalContrastAndGlobalVarianceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR376_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateUniformPgm(int w = 40, int h = 40, int v = 128)
    {
        var path = TempFile($"uniform_{v}.pgm");
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{w} {h}");
        sb.AppendLine("255");
        for (int r = 0; r < h; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < w; c++) { if (c > 0) row.Append(' '); row.Append(v); }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateHighContrastPgm()
    {
        // Alternating 0 and 255 — maximum contrast
        var path = TempFile("high_contrast.pgm");
        var sb = new StringBuilder();
        int w = 40, h = 40;
        sb.AppendLine("P2");
        sb.AppendLine($"{w} {h}");
        sb.AppendLine("255");
        for (int r = 0; r < h; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < w; c++)
            {
                if (c > 0) row.Append(' ');
                row.Append((r + c) % 2 == 0 ? 0 : 255);
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateGradientPgm()
    {
        var path = TempFile("gradient.pgm");
        var sb = new StringBuilder();
        int w = 40, h = 40;
        sb.AppendLine("P2");
        sb.AppendLine($"{w} {h}");
        sb.AppendLine("255");
        for (int r = 0; r < h; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < w; c++)
            {
                if (c > 0) row.Append(' ');
                row.Append((c * 255) / (w - 1));
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetLocalContrast
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLocalContrast_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateHighContrastPgm());
        var ex = Record.Exception(() => img.GetLocalContrast());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLocalContrast_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateHighContrastPgm());
        Assert.True(img.GetLocalContrast() >= 0.0);
    }

    [Fact]
    public void GetLocalContrast_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateHighContrastPgm());
        Assert.Equal(img.GetLocalContrast(), img.GetLocalContrast());
    }

    [Fact]
    public void GetLocalContrast_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, img.GetLocalContrast(), precision: 6);
    }

    [Fact]
    public void GetLocalContrast_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateHighContrastPgm());
        var before = img.GetLocalContrast();
        var path = TempFile("lc_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetLocalContrast(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetGlobalVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGlobalVariance_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetGlobalVariance());
        Assert.Null(ex);
    }

    [Fact]
    public void GetGlobalVariance_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetGlobalVariance() >= 0.0);
    }

    [Fact]
    public void GetGlobalVariance_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, img.GetGlobalVariance(), precision: 6);
    }

    [Fact]
    public void GetGlobalVariance_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateHighContrastPgm());
        Assert.Equal(img.GetGlobalVariance(), img.GetGlobalVariance());
    }

    [Fact]
    public void GetGlobalVariance_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var before = img.GetGlobalVariance();
        var path = TempFile("gv_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetGlobalVariance(), precision: 6);
    }

    [Fact]
    public void GetGlobalVariance_Higher_ForHighContrast_Than_Gradient()
    {
        var imgHigh = NetpbmImage.LoadFile(CreateHighContrastPgm());
        var imgGrad = NetpbmImage.LoadFile(CreateGradientPgm());
        // Alternating 0/255 has max variance; gradient is lower
        Assert.True(imgHigh.GetGlobalVariance() >= imgGrad.GetGlobalVariance());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetLocalContrast_GetGlobalVariance_SaveToFile_Pipeline()
    {
        // Geospatial — Ordnance Survey: Digital Terrain Model (DTM) Raster Data
        // Elevation PGM images derived from OS Terrain 50 grid — contrast and variance
        // indicate terrain roughness for civil engineering and flood-risk applications

        // Image 1: Flat terrain (fenland — very uniform elevation)
        var pathFlat = TempFile("os_dtm_fenland.pgm");
        {
            int w = 80, h = 60;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240601);
            for (int r = 0; r < h; r++)
            {
                var row = new StringBuilder();
                for (int c = 0; c < w; c++)
                {
                    if (c > 0) row.Append(' ');
                    // Flat fenland: 5-15m elevation (near sea level, very little variation)
                    int v = 10 + rng.Next(5); // 10-14 out of 255
                    row.Append(v);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathFlat, sb.ToString());
        }

        // Image 2: Highland terrain (Scottish Highlands — high variance and contrast)
        var pathHighland = TempFile("os_dtm_highlands.pgm");
        {
            int w = 80, h = 60;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240602);
            for (int r = 0; r < h; r++)
            {
                var row = new StringBuilder();
                for (int c = 0; c < w; c++)
                {
                    if (c > 0) row.Append(' ');
                    // Highland terrain: 0-1200m range mapped to 0-255
                    // Creates ridges and valleys with sharp transitions
                    double freq1 = 0.15, freq2 = 0.08;
                    int v = (int)(127 + 80 * Math.Sin(r * freq1) + 60 * Math.Cos(c * freq2)
                                     + 30 * Math.Sin((r + c) * 0.05) + rng.Next(20) - 10);
                    row.Append(Math.Max(0, Math.Min(255, v)));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathHighland, sb.ToString());
        }

        // Image 3: Coastal transition zone (mixed — moderate variance)
        var pathCoastal = TempFile("os_dtm_coastal.pgm");
        {
            int w = 80, h = 60;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240603);
            for (int r = 0; r < h; r++)
            {
                var row = new StringBuilder();
                for (int c = 0; c < w; c++)
                {
                    if (c > 0) row.Append(' ');
                    // Coastal: cliffs on left, sea on right
                    double normC = (double)c / w;
                    int v = c < w / 2
                        ? (int)(80 + normC * 120 + rng.Next(15)) // ascending cliff
                        : (int)(20 - (normC - 0.5) * 40 + rng.Next(8)); // descending to sea
                    row.Append(Math.Max(0, Math.Min(255, v)));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathCoastal, sb.ToString());
        }

        var imgFlat = NetpbmImage.LoadFile(pathFlat);
        var imgHighland = NetpbmImage.LoadFile(pathHighland);
        var imgCoastal = NetpbmImage.LoadFile(pathCoastal);

        // Local contrast assertions
        var lcFlat = imgFlat.GetLocalContrast();
        var lcHighland = imgHighland.GetLocalContrast();
        var lcCoastal = imgCoastal.GetLocalContrast();
        Assert.True(lcFlat >= 0.0);
        Assert.True(lcHighland >= 0.0);
        Assert.True(lcCoastal >= 0.0);
        Assert.True(lcHighland >= lcFlat); // highlands have more contrast than flat fenland
        Assert.Equal(lcFlat, imgFlat.GetLocalContrast()); // consistent

        // Global variance assertions
        var gvFlat = imgFlat.GetGlobalVariance();
        var gvHighland = imgHighland.GetGlobalVariance();
        var gvCoastal = imgCoastal.GetGlobalVariance();
        Assert.True(gvFlat >= 0.0);
        Assert.True(gvHighland >= 0.0);
        Assert.True(gvCoastal >= 0.0);
        Assert.True(gvHighland >= gvFlat); // highland terrain has more variance
        Assert.Equal(gvHighland, imgHighland.GetGlobalVariance()); // consistent

        // Uniform image — both metrics should be zero
        var imgUniform = NetpbmImage.LoadFile(CreateUniformPgm(80, 60, 100));
        Assert.Equal(0.0, imgUniform.GetLocalContrast(), precision: 6);
        Assert.Equal(0.0, imgUniform.GetGlobalVariance(), precision: 6);

        // Image dimensions
        Assert.Equal(80, imgFlat.Width);
        Assert.Equal(60, imgFlat.Height);

        // SaveToFile
        var outHighland = TempFile("os_dtm_highlands_out.pgm");
        imgHighland.SaveToFile(outHighland);
        Assert.True(File.Exists(outHighland));
        Assert.True(new FileInfo(outHighland).Length > 0);
        var loadedHighland = NetpbmImage.LoadFile(outHighland);
        Assert.Equal(lcHighland, loadedHighland.GetLocalContrast(), precision: 6);
        Assert.Equal(gvHighland, loadedHighland.GetGlobalVariance(), precision: 6);

        var outFlat = TempFile("os_dtm_fenland_out.pgm");
        imgFlat.SaveToFile(outFlat);
        var loadedFlat = NetpbmImage.LoadFile(outFlat);
        Assert.Equal(lcFlat, loadedFlat.GetLocalContrast(), precision: 6);
        Assert.Equal(gvFlat, loadedFlat.GetGlobalVariance(), precision: 6);

        var ex1 = Record.Exception(() => loadedHighland.GetLocalContrast());
        var ex2 = Record.Exception(() => loadedHighland.GetGlobalVariance());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
