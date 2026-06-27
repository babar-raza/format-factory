// Tests for NetpbmImage.GetEdgeDensity, GetLaplacianVariance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R366

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R366: Tests for NetpbmImage.GetEdgeDensity, GetLaplacianVariance deeper.
/// GetEdgeDensity(): returns the fraction of pixels identified as edges (0.0–1.0).
/// GetLaplacianVariance(): returns the variance of the Laplacian-filtered image (focus/sharpness metric).
/// Covers: GetEdgeDensity no-throw; GetEdgeDensity in-range; GetEdgeDensity consistent;
/// GetEdgeDensity zero for uniform; GetEdgeDensity save-load;
/// GetLaplacianVariance no-throw; GetLaplacianVariance non-negative;
/// GetLaplacianVariance zero for uniform; GetLaplacianVariance consistent;
/// GetLaplacianVariance save-load; GetLaplacianVariance higher for detailed;
/// dogfood CreateImage→GetEdgeDensity→GetLaplacianVariance→SaveToFile pipeline.
/// </summary>
public class NetpbmR366GetEdgeDensityAndLaplacianVarianceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR366GetEdgeDensityAndLaplacianVarianceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR366_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateUniformPgm(int width = 40, int height = 40, int value = 128)
    {
        var path = TempFile($"uniform_{value}.pgm");
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int r = 0; r < height; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < width; c++)
            {
                if (c > 0) row.Append(' ');
                row.Append(value);
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateCheckerboardPgm(int width = 40, int height = 40)
    {
        var path = TempFile("checkerboard.pgm");
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int r = 0; r < height; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < width; c++)
            {
                if (c > 0) row.Append(' ');
                int v = ((r / 4) + (c / 4)) % 2 == 0 ? 255 : 0;
                row.Append(v);
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateGradientPgm(int width = 40, int height = 40)
    {
        var path = TempFile("gradient.pgm");
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int r = 0; r < height; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < width; c++)
            {
                if (c > 0) row.Append(' ');
                int v = (c * 255) / (width - 1);
                row.Append(v);
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetEdgeDensity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEdgeDensity_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var ex = Record.Exception(() => img.GetEdgeDensity());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEdgeDensity_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var ed = img.GetEdgeDensity();
        Assert.True(ed >= 0.0 && ed <= 1.0);
    }

    [Fact]
    public void GetEdgeDensity_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        Assert.Equal(img.GetEdgeDensity(), img.GetEdgeDensity());
    }

    [Fact]
    public void GetEdgeDensity_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, img.GetEdgeDensity(), precision: 6);
    }

    [Fact]
    public void GetEdgeDensity_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var before = img.GetEdgeDensity();
        var path = TempFile("ed_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetEdgeDensity(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetLaplacianVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLaplacianVariance_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var ex = Record.Exception(() => img.GetLaplacianVariance());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLaplacianVariance_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        Assert.True(img.GetLaplacianVariance() >= 0.0);
    }

    [Fact]
    public void GetLaplacianVariance_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, img.GetLaplacianVariance(), precision: 6);
    }

    [Fact]
    public void GetLaplacianVariance_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        Assert.Equal(img.GetLaplacianVariance(), img.GetLaplacianVariance());
    }

    [Fact]
    public void GetLaplacianVariance_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var before = img.GetLaplacianVariance();
        var path = TempFile("lv_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetLaplacianVariance(), precision: 6);
    }

    [Fact]
    public void GetLaplacianVariance_Higher_ForCheckerboard_Than_Gradient()
    {
        var imgChecker = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var imgGradient = NetpbmImage.LoadFile(CreateGradientPgm());
        // Checkerboard has sharp transitions → higher Laplacian variance than smooth gradient
        Assert.True(imgChecker.GetLaplacianVariance() >= imgGradient.GetLaplacianVariance());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetEdgeDensity_GetLaplacianVariance_SaveToFile_Pipeline()
    {
        // Medical imaging — NICE Digital Health Technology Assessment
        // OCT (Optical Coherence Tomography) retinal layer images for diabetic macular oedema
        // Edge density and Laplacian variance to quantify image sharpness and layer boundary clarity
        var rng = new Random(20240901);

        // Image 1: Sharp retinal layer boundaries (high quality OCT)
        var pathSharp = TempFile("oct_sharp.pgm");
        {
            int w = 80, h = 60;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            for (int r = 0; r < h; r++)
            {
                var row = new StringBuilder();
                for (int c = 0; c < w; c++)
                {
                    if (c > 0) row.Append(' ');
                    // Simulate retinal layers: distinct bands with sharp transitions
                    int v;
                    if (r < 8) v = 180 + rng.Next(15);           // RNFL
                    else if (r < 12) v = 20 + rng.Next(10);      // dark band
                    else if (r < 22) v = 140 + rng.Next(20);     // GCL/IPL
                    else if (r < 26) v = 25 + rng.Next(10);      // dark band
                    else if (r < 38) v = 200 + rng.Next(15);     // INL
                    else if (r < 42) v = 30 + rng.Next(10);      // OPL dark
                    else if (r < 54) v = 160 + rng.Next(20);     // ONL
                    else v = 100 + rng.Next(30);                   // RPE
                    row.Append(Math.Min(255, v));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathSharp, sb.ToString());
        }

        // Image 2: Blurry OCT (poor quality, heavy speckle noise)
        var pathBlurry = TempFile("oct_blurry.pgm");
        {
            int w = 80, h = 60;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            int baseVal = 128;
            for (int r = 0; r < h; r++)
            {
                var row = new StringBuilder();
                for (int c = 0; c < w; c++)
                {
                    if (c > 0) row.Append(' ');
                    // Slowly varying background — low frequency, minimal edges
                    int v = baseVal + (int)(10 * Math.Sin(r * 0.3) + 5 * Math.Cos(c * 0.2));
                    row.Append(Math.Max(0, Math.Min(255, v)));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathBlurry, sb.ToString());
        }

        var imgSharp = NetpbmImage.LoadFile(pathSharp);
        var imgBlurry = NetpbmImage.LoadFile(pathBlurry);

        // Edge density assertions
        var edSharp = imgSharp.GetEdgeDensity();
        var edBlurry = imgBlurry.GetEdgeDensity();
        Assert.True(edSharp >= 0.0 && edSharp <= 1.0);
        Assert.True(edBlurry >= 0.0 && edBlurry <= 1.0);
        Assert.Equal(edSharp, imgSharp.GetEdgeDensity()); // consistent
        // Sharp image should have more edges than smooth blurry
        Assert.True(edSharp >= edBlurry);

        // Laplacian variance assertions
        var lvSharp = imgSharp.GetLaplacianVariance();
        var lvBlurry = imgBlurry.GetLaplacianVariance();
        Assert.True(lvSharp >= 0.0);
        Assert.True(lvBlurry >= 0.0);
        Assert.Equal(lvSharp, imgSharp.GetLaplacianVariance()); // consistent
        // Sharp image: higher Laplacian variance (sharper focus)
        Assert.True(lvSharp >= lvBlurry);

        // Uniform image: both metrics should be zero
        var imgUniform = NetpbmImage.LoadFile(CreateUniformPgm(80, 60, 150));
        Assert.Equal(0.0, imgUniform.GetEdgeDensity(), precision: 6);
        Assert.Equal(0.0, imgUniform.GetLaplacianVariance(), precision: 6);

        // Additional basic metrics
        Assert.True(imgSharp.Width > 0);
        Assert.True(imgSharp.Height > 0);
        Assert.True(imgSharp.GetGlobalMean() > 0);

        // SaveToFile and reload
        var outSharp = TempFile("oct_sharp_out.pgm");
        imgSharp.SaveToFile(outSharp);
        Assert.True(File.Exists(outSharp));
        Assert.True(new FileInfo(outSharp).Length > 0);

        var loadedSharp = NetpbmImage.LoadFile(outSharp);
        Assert.Equal(edSharp, loadedSharp.GetEdgeDensity(), precision: 6);
        Assert.Equal(lvSharp, loadedSharp.GetLaplacianVariance(), precision: 6);
        Assert.Equal(imgSharp.Width, loadedSharp.Width);
        Assert.Equal(imgSharp.Height, loadedSharp.Height);

        var outBlurry = TempFile("oct_blurry_out.pgm");
        imgBlurry.SaveToFile(outBlurry);
        Assert.True(File.Exists(outBlurry));
        var loadedBlurry = NetpbmImage.LoadFile(outBlurry);
        Assert.Equal(edBlurry, loadedBlurry.GetEdgeDensity(), precision: 6);
        Assert.Equal(lvBlurry, loadedBlurry.GetLaplacianVariance(), precision: 6);

        var ex1 = Record.Exception(() => loadedSharp.GetEdgeDensity());
        var ex2 = Record.Exception(() => loadedSharp.GetLaplacianVariance());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
