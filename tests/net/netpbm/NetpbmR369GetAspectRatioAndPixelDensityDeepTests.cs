// Tests for NetpbmImage.GetAspectRatio, GetPixelDensity deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R369

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R369: Tests for NetpbmImage.GetAspectRatio, GetPixelDensity deeper.
/// GetAspectRatio(): returns width/height as a double (1.0 for square images).
/// GetPixelDensity(): returns the total number of pixels (width * height).
/// Covers: GetAspectRatio no-throw; GetAspectRatio positive; GetAspectRatio consistent;
/// GetAspectRatio one for square; GetAspectRatio save-load;
/// GetPixelDensity no-throw; GetPixelDensity equals width times height;
/// GetPixelDensity consistent; GetPixelDensity save-load;
/// GetAspectRatio greater than one for landscape; GetAspectRatio less than one for portrait;
/// dogfood CreateImage→GetAspectRatio→GetPixelDensity→SaveToFile pipeline.
/// </summary>
public class NetpbmR369GetAspectRatioAndPixelDensityDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR369GetAspectRatioAndPixelDensityDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR369_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePgm(int width, int height, int value = 128)
    {
        var path = TempFile($"pgm_{width}x{height}.pgm");
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        var rng = new Random(width * 1000 + height);
        for (int r = 0; r < height; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < width; c++)
            {
                if (c > 0) row.Append(' ');
                row.Append(value > 0 ? value : rng.Next(256));
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateSquarePgm() => CreatePgm(40, 40);
    private string CreateLandscapePgm() => CreatePgm(80, 40);
    private string CreatePortraitPgm() => CreatePgm(40, 80);

    // -------------------------------------------------------------------------
    // GetAspectRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAspectRatio_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSquarePgm());
        var ex = Record.Exception(() => img.GetAspectRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetAspectRatio_Positive()
    {
        var img = NetpbmImage.LoadFile(CreateLandscapePgm());
        Assert.True(img.GetAspectRatio() > 0.0);
    }

    [Fact]
    public void GetAspectRatio_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateLandscapePgm());
        Assert.Equal(img.GetAspectRatio(), img.GetAspectRatio());
    }

    [Fact]
    public void GetAspectRatio_One_ForSquare()
    {
        var img = NetpbmImage.LoadFile(CreateSquarePgm());
        Assert.Equal(1.0, img.GetAspectRatio(), precision: 8);
    }

    [Fact]
    public void GetAspectRatio_GreaterThanOne_ForLandscape()
    {
        var img = NetpbmImage.LoadFile(CreateLandscapePgm());
        Assert.True(img.GetAspectRatio() > 1.0);
    }

    [Fact]
    public void GetAspectRatio_LessThanOne_ForPortrait()
    {
        var img = NetpbmImage.LoadFile(CreatePortraitPgm());
        Assert.True(img.GetAspectRatio() < 1.0);
    }

    [Fact]
    public void GetAspectRatio_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateLandscapePgm());
        var before = img.GetAspectRatio();
        var path = TempFile("ar_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetAspectRatio(), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetPixelDensity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelDensity_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSquarePgm());
        var ex = Record.Exception(() => img.GetPixelDensity());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPixelDensity_Equals_Width_Times_Height()
    {
        var img = NetpbmImage.LoadFile(CreateLandscapePgm());
        Assert.Equal(img.Width * img.Height, img.GetPixelDensity());
    }

    [Fact]
    public void GetPixelDensity_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSquarePgm());
        Assert.Equal(img.GetPixelDensity(), img.GetPixelDensity());
    }

    [Fact]
    public void GetPixelDensity_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateLandscapePgm());
        var before = img.GetPixelDensity();
        var path = TempFile("pd_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetPixelDensity());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetAspectRatio_GetPixelDensity_SaveToFile_Pipeline()
    {
        // Remote sensing — UKHSA Environmental Monitoring: Air Quality Sensor Maps
        // PGM images representing pollution concentration maps at different spatial resolutions
        // Aspect ratio verification for grid alignment; pixel density for resolution adequacy

        // Full HD landscape map (England & Wales coverage, 16:9)
        var pathLandscape = TempFile("aq_map_landscape.pgm");
        {
            int w = 160, h = 90;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240901);
            for (int r = 0; r < h; r++)
            {
                var row = new StringBuilder();
                for (int c = 0; c < w; c++)
                {
                    if (c > 0) row.Append(' ');
                    // NO2 concentration gradient — higher in urban corridors (vertical bands)
                    int baseVal = 40 + (int)(60 * Math.Sin(c * Math.PI / w));
                    int v = Math.Max(0, Math.Min(255, baseVal + rng.Next(30)));
                    row.Append(v);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathLandscape, sb.ToString());
        }

        // Portrait map (Scotland-only, 3:4)
        var pathPortrait = TempFile("aq_map_portrait.pgm");
        {
            int w = 60, h = 80;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240902);
            for (int r = 0; r < h; r++)
            {
                var row = new StringBuilder();
                for (int c = 0; c < w; c++)
                {
                    if (c > 0) row.Append(' ');
                    int v = 20 + rng.Next(60); // Lower pollution (Scotland)
                    row.Append(v);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathPortrait, sb.ToString());
        }

        // Square map (Local authority grid, 1:1)
        var pathSquare = TempFile("aq_map_square.pgm");
        {
            int w = 100, h = 100;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240903);
            for (int r = 0; r < h; r++)
            {
                var row = new StringBuilder();
                for (int c = 0; c < w; c++)
                {
                    if (c > 0) row.Append(' ');
                    int v = 30 + rng.Next(100);
                    row.Append(v);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathSquare, sb.ToString());
        }

        var imgLandscape = NetpbmImage.LoadFile(pathLandscape);
        var imgPortrait = NetpbmImage.LoadFile(pathPortrait);
        var imgSquare = NetpbmImage.LoadFile(pathSquare);

        // Aspect ratio checks
        Assert.True(imgLandscape.GetAspectRatio() > 1.0); // 160:90 > 1
        Assert.True(imgPortrait.GetAspectRatio() < 1.0);  // 60:80 < 1
        Assert.Equal(1.0, imgSquare.GetAspectRatio(), precision: 8); // 100:100 = 1
        Assert.Equal(imgLandscape.GetAspectRatio(), imgLandscape.GetAspectRatio()); // consistent
        Assert.Equal(imgPortrait.GetAspectRatio(), imgPortrait.GetAspectRatio());

        // Pixel density checks
        Assert.Equal(160 * 90, imgLandscape.GetPixelDensity()); // 14400
        Assert.Equal(60 * 80, imgPortrait.GetPixelDensity());   // 4800
        Assert.Equal(100 * 100, imgSquare.GetPixelDensity());   // 10000
        Assert.True(imgLandscape.GetPixelDensity() > imgPortrait.GetPixelDensity());

        // Exact aspect ratio values
        Assert.Equal(160.0 / 90.0, imgLandscape.GetAspectRatio(), precision: 6);
        Assert.Equal(60.0 / 80.0, imgPortrait.GetAspectRatio(), precision: 6);

        // Basic image properties
        Assert.Equal(160, imgLandscape.Width);
        Assert.Equal(90, imgLandscape.Height);
        Assert.True(imgLandscape.GetGlobalMean() > 0);

        // SaveToFile
        var outLandscape = TempFile("aq_map_landscape_out.pgm");
        imgLandscape.SaveToFile(outLandscape);
        Assert.True(File.Exists(outLandscape));
        var loadedL = NetpbmImage.LoadFile(outLandscape);
        Assert.Equal(imgLandscape.GetAspectRatio(), loadedL.GetAspectRatio(), precision: 8);
        Assert.Equal(imgLandscape.GetPixelDensity(), loadedL.GetPixelDensity());

        var outPortrait = TempFile("aq_map_portrait_out.pgm");
        imgPortrait.SaveToFile(outPortrait);
        Assert.True(File.Exists(outPortrait));
        var loadedP = NetpbmImage.LoadFile(outPortrait);
        Assert.Equal(imgPortrait.GetAspectRatio(), loadedP.GetAspectRatio(), precision: 8);
        Assert.Equal(imgPortrait.GetPixelDensity(), loadedP.GetPixelDensity());

        var outSquare = TempFile("aq_map_square_out.pgm");
        imgSquare.SaveToFile(outSquare);
        var loadedS = NetpbmImage.LoadFile(outSquare);
        Assert.Equal(1.0, loadedS.GetAspectRatio(), precision: 8);
        Assert.Equal(10000, loadedS.GetPixelDensity());

        var ex1 = Record.Exception(() => loadedL.GetAspectRatio());
        var ex2 = Record.Exception(() => loadedL.GetPixelDensity());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
