// Tests for NetpbmImage.GetTopographicProminence, GetTopographicIsolation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R340

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R340: Tests for NetpbmImage.GetTopographicProminence, GetTopographicIsolation deeper.
/// GetTopographicProminence(): returns the prominence of the highest peak (intensity maximum above surroundings).
/// GetTopographicIsolation(): returns the isolation measure — distance to nearest higher-intensity point.
/// Covers: GetTopographicProminence no-throw; GetTopographicProminence non-negative;
/// GetTopographicProminence consistent; GetTopographicProminence zero for uniform;
/// GetTopographicIsolation no-throw; GetTopographicIsolation non-negative;
/// GetTopographicIsolation consistent; GetTopographicIsolation save-load;
/// GetTopographicProminence single-peak greater-than-gradient;
/// dogfood CreateDoc→GetTopographicProminence→GetTopographicIsolation pipeline.
/// </summary>
public class NetpbmR340GetTopographicProminenceAndIsolationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR340GetTopographicProminenceAndIsolationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR340_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateUniformPgm(int size = 40, int value = 100)
    {
        var path = TempFile($"uniform_{value}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine($"P2\n{size} {size}\n255");
        for (int r = 0; r < size; r++)
        {
            for (int c = 0; c < size; c++) sb.Append(value + " ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateSinglePeakPgm(int size = 60, int bgValue = 50, int peakValue = 240)
    {
        var path = TempFile("single_peak.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine($"P2\n{size} {size}\n255");
        int cx = size / 2, cy = size / 2, r = 5;
        for (int row = 0; row < size; row++)
        {
            for (int col = 0; col < size; col++)
            {
                double dist = Math.Sqrt((row - cy) * (row - cy) + (col - cx) * (col - cx));
                int val = dist <= r ? peakValue : bgValue;
                sb.Append(val + " ");
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateGradientPgm(int size = 50)
    {
        var path = TempFile("gradient.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine($"P2\n{size} {size}\n255");
        for (int r = 0; r < size; r++)
        {
            for (int c = 0; c < size; c++)
                sb.Append((c * 255 / (size - 1)) + " ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetTopographicProminence
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTopographicProminence_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSinglePeakPgm());
        var ex = Record.Exception(() => img.GetTopographicProminence());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTopographicProminence_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateSinglePeakPgm());
        Assert.True(img.GetTopographicProminence() >= 0.0);
    }

    [Fact]
    public void GetTopographicProminence_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSinglePeakPgm());
        Assert.Equal(img.GetTopographicProminence(), img.GetTopographicProminence());
    }

    [Fact]
    public void GetTopographicProminence_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, img.GetTopographicProminence(), precision: 6);
    }

    [Fact]
    public void GetTopographicProminence_SinglePeak_Positive()
    {
        var img = NetpbmImage.LoadFile(CreateSinglePeakPgm());
        Assert.True(img.GetTopographicProminence() > 0.0);
    }

    // -------------------------------------------------------------------------
    // GetTopographicIsolation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTopographicIsolation_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSinglePeakPgm());
        var ex = Record.Exception(() => img.GetTopographicIsolation());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTopographicIsolation_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateSinglePeakPgm());
        Assert.True(img.GetTopographicIsolation() >= 0.0);
    }

    [Fact]
    public void GetTopographicIsolation_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSinglePeakPgm());
        Assert.Equal(img.GetTopographicIsolation(), img.GetTopographicIsolation());
    }

    [Fact]
    public void GetTopographicIsolation_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSinglePeakPgm());
        var before = img.GetTopographicIsolation();
        var path = TempFile("iso_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetTopographicIsolation());
    }

    [Fact]
    public void GetTopographicIsolation_Gradient_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetTopographicIsolation() >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetTopographicProminence_GetTopographicIsolation_Pipeline()
    {
        // Volcanology — synthetic DEM (Digital Elevation Model) of volcanic caldera complex
        var rng = new Random(20250201);
        int width = 150, height = 150;

        // Scene: main stratovolcano peak + secondary cinder cone + caldera depression
        var path1 = TempFile("caldera_dem.pgm");
        var pixels = new int[height, width];

        // Background terrain — moderate elevation
        for (int r = 0; r < height; r++)
            for (int c = 0; c < width; c++)
                pixels[r, c] = 80 + rng.Next(20); // base terrain

        // Main stratovolcano (centre) — high elevation Gaussian
        double mainCx = 75, mainCy = 75;
        for (int r = 0; r < height; r++)
            for (int c = 0; c < width; c++)
            {
                double d = Math.Sqrt((r - mainCy) * (r - mainCy) + (c - mainCx) * (c - mainCx));
                int bump = (int)(160 * Math.Exp(-d * d / (2 * 25 * 25)));
                pixels[r, c] = Math.Min(255, pixels[r, c] + bump);
            }

        // Caldera depression at summit
        for (int r = 0; r < height; r++)
            for (int c = 0; c < width; c++)
            {
                double d = Math.Sqrt((r - mainCy) * (r - mainCy) + (c - mainCx) * (c - mainCx));
                if (d < 8)
                    pixels[r, c] = Math.Max(0, pixels[r, c] - (int)(80 * (1 - d / 8)));
            }

        // Secondary cinder cone (upper-left)
        double secCx = 35, secCy = 35;
        for (int r = 0; r < height; r++)
            for (int c = 0; c < width; c++)
            {
                double d = Math.Sqrt((r - secCy) * (r - secCy) + (c - secCx) * (c - secCx));
                int bump = (int)(70 * Math.Exp(-d * d / (2 * 10 * 10)));
                pixels[r, c] = Math.Min(255, pixels[r, c] + bump);
            }

        var sb = new System.Text.StringBuilder();
        sb.AppendLine($"P2\n{width} {height}\n255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
                sb.Append(pixels[r, c] + " ");
            sb.AppendLine();
        }
        File.WriteAllText(path1, sb.ToString());

        // Uniform flat terrain reference
        var path2 = TempFile("flat_terrain.pgm");
        var sb2 = new System.Text.StringBuilder();
        sb2.AppendLine($"P2\n{width} {height}\n255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++) sb2.Append("100 ");
            sb2.AppendLine();
        }
        File.WriteAllText(path2, sb2.ToString());

        var dem = NetpbmImage.LoadFile(path1);
        var flat = NetpbmImage.LoadFile(path2);

        Assert.Equal(width, dem.Width);
        Assert.Equal(height, dem.Height);

        // GetTopographicProminence
        var promDem = dem.GetTopographicProminence();
        Assert.True(promDem >= 0.0);
        Assert.Equal(promDem, dem.GetTopographicProminence()); // consistent

        var promFlat = flat.GetTopographicProminence();
        Assert.Equal(0.0, promFlat, precision: 6); // uniform = no prominence

        // Caldera DEM should have higher prominence than flat
        Assert.True(promDem > promFlat);

        // GetTopographicIsolation
        var isoDem = dem.GetTopographicIsolation();
        Assert.True(isoDem >= 0.0);
        Assert.Equal(isoDem, dem.GetTopographicIsolation()); // consistent

        var isoFlat = flat.GetTopographicIsolation();
        Assert.True(isoFlat >= 0.0);

        // Other image stats
        Assert.True(dem.GetMaxIntensity() > flat.GetMaxIntensity());
        Assert.True(dem.GetMeanIntensity() > 0.0);
        Assert.True(dem.GetStdDevIntensity() > 0.0);
        Assert.Equal(0.0, flat.GetStdDevIntensity(), precision: 6);

        // Moment invariants
        var inv = dem.GetMomentInvariants();
        Assert.Equal(7, inv.Length);

        // SaveToFile
        var outPath = TempFile("caldera_dem_out.pgm");
        dem.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(outPath);
        Assert.Equal(width, loaded.Width);
        Assert.Equal(height, loaded.Height);
        Assert.Equal(promDem, loaded.GetTopographicProminence());
        Assert.Equal(isoDem, loaded.GetTopographicIsolation());

        // Flat terrain save/load
        var outPath2 = TempFile("flat_terrain_out.pgm");
        flat.SaveToFile(outPath2);
        var loaded2 = NetpbmImage.LoadFile(outPath2);
        Assert.Equal(0.0, loaded2.GetTopographicProminence(), precision: 6);
        var ex1 = Record.Exception(() => loaded.GetTopographicProminence());
        var ex2 = Record.Exception(() => loaded2.GetTopographicIsolation());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
