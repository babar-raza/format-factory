// Tests for NetpbmImage.GetEdgePixelRatio, GetBrightPixelRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R382

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R382: Tests for NetpbmImage.GetEdgePixelRatio, GetBrightPixelRatio deeper.
/// GetEdgePixelRatio(): returns the fraction of pixels classified as edges (local gradient ≥ threshold); [0,1].
/// GetBrightPixelRatio(): returns the fraction of pixels with intensity above mid-range (>127 for 8-bit); [0,1].
/// Covers: GetEdgePixelRatio no-throw; GetEdgePixelRatio in-range; GetEdgePixelRatio zero for uniform;
/// GetEdgePixelRatio consistent; GetEdgePixelRatio save-load;
/// GetBrightPixelRatio no-throw; GetBrightPixelRatio in-range; GetBrightPixelRatio one for all-white;
/// GetBrightPixelRatio zero for all-black; GetBrightPixelRatio consistent; GetBrightPixelRatio save-load;
/// dogfood CreateImage→GetEdgePixelRatio→GetBrightPixelRatio→SaveToFile pipeline.
/// </summary>
public class NetpbmR382GetEdgePixelRatioAndBrightPixelRatioDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR382GetEdgePixelRatioAndBrightPixelRatioDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR382_" + Guid.NewGuid().ToString("N"));
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

    private string CreateCheckerboardPgm(string name, int width, int height, int blockSize = 4)
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
    // GetEdgePixelRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEdgePixelRatio_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm("checker.pgm", 40, 40));
        var ex = Record.Exception(() => img.GetEdgePixelRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEdgePixelRatio_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm("checker.pgm", 40, 40));
        var r = img.GetEdgePixelRatio();
        Assert.True(r >= 0.0 && r <= 1.0);
    }

    [Fact]
    public void GetEdgePixelRatio_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform.pgm", 40, 40, 128));
        Assert.Equal(0.0, img.GetEdgePixelRatio(), precision: 6);
    }

    [Fact]
    public void GetEdgePixelRatio_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm("checker.pgm", 40, 40));
        Assert.Equal(img.GetEdgePixelRatio(), img.GetEdgePixelRatio());
    }

    [Fact]
    public void GetEdgePixelRatio_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm("checker.pgm", 40, 40));
        var before = img.GetEdgePixelRatio();
        var path = TempFile("edge_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetEdgePixelRatio(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetBrightPixelRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightPixelRatio_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var ex = Record.Exception(() => img.GetBrightPixelRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBrightPixelRatio_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var r = img.GetBrightPixelRatio();
        Assert.True(r >= 0.0 && r <= 1.0);
    }

    [Fact]
    public void GetBrightPixelRatio_One_ForAllWhite()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("white.pgm", 40, 40, 255));
        Assert.Equal(1.0, img.GetBrightPixelRatio(), precision: 6);
    }

    [Fact]
    public void GetBrightPixelRatio_Zero_ForAllBlack()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("black.pgm", 40, 40, 0));
        Assert.Equal(0.0, img.GetBrightPixelRatio(), precision: 6);
    }

    [Fact]
    public void GetBrightPixelRatio_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.Equal(img.GetBrightPixelRatio(), img.GetBrightPixelRatio());
    }

    [Fact]
    public void GetBrightPixelRatio_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var before = img.GetBrightPixelRatio();
        var path = TempFile("bright_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetBrightPixelRatio(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetEdgePixelRatio_GetBrightPixelRatio_Pipeline()
    {
        // Remote Sensing — UKSA / DSTL: Sentinel-2 Satellite Imagery Analysis
        // Multi-scene PGM imagery for land cover classification validation
        // Edge ratio detects urban/natural boundaries; bright ratio detects cloud cover / snow

        // Scene 1: Urban area (dense edges between buildings and roads, moderate brightness)
        var path1 = TempFile("sentinel2_urban_scene.pgm");
        {
            int w = 80, h = 60;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20241015);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // Simulate urban grid with alternating dark roads (0-60) and bright buildings (120-200)
                    int streetGrid = (x % 8 < 2 || y % 6 < 1) ? 1 : 0;
                    int val = streetGrid == 1
                        ? rng.Next(0, 60)
                        : rng.Next(120, 200);
                    row.Append(val);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path1, sb.ToString());
        }

        // Scene 2: Cloud-covered scene (very high brightness, few structural edges)
        var path2 = TempFile("sentinel2_cloud_scene.pgm");
        {
            int w = 80, h = 60;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20241016);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // High-brightness cloud deck: 200-255 with minor variation
                    row.Append(rng.Next(200, 256));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path2, sb.ToString());
        }

        // Scene 3: Dense forest (dark, few bright pixels, smooth texture)
        var path3 = TempFile("sentinel2_forest_scene.pgm");
        {
            int w = 80, h = 60;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20241017);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // Dark canopy: 10-80 with slow spatial variation
                    int base_val = 20 + (int)(30.0 * Math.Sin(x * 0.2) * Math.Cos(y * 0.15));
                    row.Append(Math.Max(10, Math.Min(80, base_val + rng.Next(-5, 5))));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path3, sb.ToString());
        }

        var img1 = NetpbmImage.LoadFile(path1);
        var img2 = NetpbmImage.LoadFile(path2);
        var img3 = NetpbmImage.LoadFile(path3);

        // Edge pixel ratio — urban has more edges than cloud or forest
        var edge1 = img1.GetEdgePixelRatio();
        var edge2 = img2.GetEdgePixelRatio();
        var edge3 = img3.GetEdgePixelRatio();
        Assert.True(edge1 >= 0.0 && edge1 <= 1.0);
        Assert.True(edge2 >= 0.0 && edge2 <= 1.0);
        Assert.True(edge3 >= 0.0 && edge3 <= 1.0);
        Assert.True(edge1 > edge2); // urban has more edges than uniform cloud
        Assert.Equal(edge1, img1.GetEdgePixelRatio()); // consistent
        Assert.Equal(edge2, img2.GetEdgePixelRatio()); // consistent

        // Bright pixel ratio — cloud >> urban >> forest
        var bright1 = img1.GetBrightPixelRatio();
        var bright2 = img2.GetBrightPixelRatio();
        var bright3 = img3.GetBrightPixelRatio();
        Assert.True(bright1 >= 0.0 && bright1 <= 1.0);
        Assert.True(bright2 >= 0.0 && bright2 <= 1.0);
        Assert.True(bright3 >= 0.0 && bright3 <= 1.0);
        Assert.True(bright2 > bright1); // cloud brighter than urban
        Assert.True(bright1 > bright3); // urban brighter than forest
        Assert.Equal(bright1, img1.GetBrightPixelRatio()); // consistent
        Assert.Equal(bright3, img3.GetBrightPixelRatio()); // consistent

        // Uniform reference
        var uniformPath = TempFile("uniform_grey.pgm");
        {
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine("40 40");
            sb.AppendLine("255");
            for (int y = 0; y < 40; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < 40; x++)
                {
                    if (x > 0) row.Append(' ');
                    row.Append(128);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(uniformPath, sb.ToString());
        }
        var uniform = NetpbmImage.LoadFile(uniformPath);
        Assert.Equal(0.0, uniform.GetEdgePixelRatio(), precision: 6); // no edges in uniform

        // SaveToFile
        var out1 = TempFile("sentinel2_urban_out.pgm");
        img1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loaded1 = NetpbmImage.LoadFile(out1);
        Assert.Equal(edge1, loaded1.GetEdgePixelRatio(), precision: 6);
        Assert.Equal(bright1, loaded1.GetBrightPixelRatio(), precision: 6);

        var out2 = TempFile("sentinel2_cloud_out.pgm");
        img2.SaveToFile(out2);
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.Equal(edge2, loaded2.GetEdgePixelRatio(), precision: 6);
        Assert.Equal(bright2, loaded2.GetBrightPixelRatio(), precision: 6);

        var out3 = TempFile("sentinel2_forest_out.pgm");
        img3.SaveToFile(out3);
        var loaded3 = NetpbmImage.LoadFile(out3);
        Assert.Equal(edge3, loaded3.GetEdgePixelRatio(), precision: 6);
        Assert.Equal(bright3, loaded3.GetBrightPixelRatio(), precision: 6);

        var ex1 = Record.Exception(() => loaded1.GetEdgePixelRatio());
        var ex2 = Record.Exception(() => loaded1.GetBrightPixelRatio());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
