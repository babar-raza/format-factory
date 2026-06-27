// Tests for NetpbmImage.GetHorizontalSymmetry, GetVerticalSymmetry deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R372

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R372: Tests for NetpbmImage.GetHorizontalSymmetry, GetVerticalSymmetry deeper.
/// GetHorizontalSymmetry(): returns 1 - normalised pixel difference when flipped horizontally (1.0 = perfect).
/// GetVerticalSymmetry(): returns 1 - normalised pixel difference when flipped vertically (1.0 = perfect).
/// Covers: GetHorizontalSymmetry no-throw; GetHorizontalSymmetry in-range; GetHorizontalSymmetry consistent;
/// GetHorizontalSymmetry one for symmetric image; GetHorizontalSymmetry save-load;
/// GetVerticalSymmetry no-throw; GetVerticalSymmetry in-range; GetVerticalSymmetry consistent;
/// GetVerticalSymmetry one for symmetric image; GetVerticalSymmetry save-load;
/// dogfood CreateImage→GetHorizontalSymmetry→GetVerticalSymmetry→SaveToFile pipeline.
/// </summary>
public class NetpbmR372GetHorizontalSymmetryAndVerticalSymmetryDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR372GetHorizontalSymmetryAndVerticalSymmetryDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR372_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSymmetricPgm()
    {
        // Left-right symmetric (each row is a palindrome)
        var path = TempFile("symmetric.pgm");
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
                int mirror = Math.Min(c, w - 1 - c);
                row.Append(mirror * 255 / (w / 2));
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateAsymmetricPgm()
    {
        var path = TempFile("asymmetric.pgm");
        var sb = new StringBuilder();
        int w = 40, h = 40;
        sb.AppendLine("P2");
        sb.AppendLine($"{w} {h}");
        sb.AppendLine("255");
        var rng = new Random(42);
        for (int r = 0; r < h; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < w; c++)
            {
                if (c > 0) row.Append(' ');
                row.Append(rng.Next(256)); // random → not symmetric
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformPgm()
    {
        var path = TempFile("uniform.pgm");
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("40 40");
        sb.AppendLine("255");
        for (int r = 0; r < 40; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < 40; c++) { if (c > 0) row.Append(' '); row.Append(128); }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetHorizontalSymmetry
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHorizontalSymmetry_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSymmetricPgm());
        var ex = Record.Exception(() => img.GetHorizontalSymmetry());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHorizontalSymmetry_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateAsymmetricPgm());
        var hs = img.GetHorizontalSymmetry();
        Assert.True(hs >= 0.0 && hs <= 1.0);
    }

    [Fact]
    public void GetHorizontalSymmetry_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSymmetricPgm());
        Assert.Equal(img.GetHorizontalSymmetry(), img.GetHorizontalSymmetry());
    }

    [Fact]
    public void GetHorizontalSymmetry_One_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(1.0, img.GetHorizontalSymmetry(), precision: 6);
    }

    [Fact]
    public void GetHorizontalSymmetry_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSymmetricPgm());
        var before = img.GetHorizontalSymmetry();
        var path = TempFile("hs_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetHorizontalSymmetry(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetVerticalSymmetry
    // -------------------------------------------------------------------------

    [Fact]
    public void GetVerticalSymmetry_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSymmetricPgm());
        var ex = Record.Exception(() => img.GetVerticalSymmetry());
        Assert.Null(ex);
    }

    [Fact]
    public void GetVerticalSymmetry_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateAsymmetricPgm());
        var vs = img.GetVerticalSymmetry();
        Assert.True(vs >= 0.0 && vs <= 1.0);
    }

    [Fact]
    public void GetVerticalSymmetry_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSymmetricPgm());
        Assert.Equal(img.GetVerticalSymmetry(), img.GetVerticalSymmetry());
    }

    [Fact]
    public void GetVerticalSymmetry_One_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(1.0, img.GetVerticalSymmetry(), precision: 6);
    }

    [Fact]
    public void GetVerticalSymmetry_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSymmetricPgm());
        var before = img.GetVerticalSymmetry();
        var path = TempFile("vs_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetVerticalSymmetry(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetHorizontalSymmetry_GetVerticalSymmetry_SaveToFile_Pipeline()
    {
        // Structural engineering — Network Rail: Track Geometry Defect Images
        // PGM images of rail profile cross-sections — symmetry analysis for wear detection

        // Image 1: Pristine symmetric rail head (bilateral symmetry)
        var pathSymmetric = TempFile("rail_head_pristine.pgm");
        {
            int w = 60, h = 40;
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
                    // Symmetric: bell-curve shape centred at w/2
                    double dist = Math.Abs(c - w / 2.0) / (w / 2.0);
                    int v = (int)(255 * (1 - dist * dist));
                    row.Append(Math.Max(0, Math.Min(255, v)));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathSymmetric, sb.ToString());
        }

        // Image 2: Worn rail head (asymmetric due to lateral wear on gauge side)
        var pathWorn = TempFile("rail_head_worn.pgm");
        {
            int w = 60, h = 40;
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
                    // Asymmetric: more material worn from the right (gauge) side
                    double normalised = (double)c / w;
                    int v = c < w / 2
                        ? (int)(200 + rng.Next(30)) // intact field side
                        : (int)(80 + rng.NextDouble() * 60); // worn gauge side
                    row.Append(Math.Max(0, Math.Min(255, v)));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathWorn, sb.ToString());
        }

        // Image 3: Uniform (reference background)
        var pathUniform = TempFile("rail_background.pgm");
        {
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine("60 40");
            sb.AppendLine("255");
            for (int r = 0; r < 40; r++)
            {
                var row = new StringBuilder();
                for (int c = 0; c < 60; c++) { if (c > 0) row.Append(' '); row.Append(128); }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathUniform, sb.ToString());
        }

        var imgSym = NetpbmImage.LoadFile(pathSymmetric);
        var imgWorn = NetpbmImage.LoadFile(pathWorn);
        var imgUniform = NetpbmImage.LoadFile(pathUniform);

        // Horizontal symmetry
        var hsSym = imgSym.GetHorizontalSymmetry();
        var hsWorn = imgWorn.GetHorizontalSymmetry();
        var hsUniform = imgUniform.GetHorizontalSymmetry();
        Assert.True(hsSym >= 0.0 && hsSym <= 1.0);
        Assert.True(hsWorn >= 0.0 && hsWorn <= 1.0);
        Assert.Equal(1.0, hsUniform, precision: 6); // uniform = perfectly symmetric
        Assert.True(hsSym > hsWorn); // pristine more symmetric than worn
        Assert.Equal(hsSym, imgSym.GetHorizontalSymmetry()); // consistent
        Assert.Equal(hsWorn, imgWorn.GetHorizontalSymmetry());

        // Vertical symmetry
        var vsSym = imgSym.GetVerticalSymmetry();
        var vsWorn = imgWorn.GetVerticalSymmetry();
        var vsUniform = imgUniform.GetVerticalSymmetry();
        Assert.True(vsSym >= 0.0 && vsSym <= 1.0);
        Assert.True(vsWorn >= 0.0 && vsWorn <= 1.0);
        Assert.Equal(1.0, vsUniform, precision: 6);
        Assert.Equal(vsSym, imgSym.GetVerticalSymmetry()); // consistent
        Assert.Equal(vsWorn, imgWorn.GetVerticalSymmetry());

        // Image properties
        Assert.Equal(60, imgSym.Width);
        Assert.Equal(40, imgSym.Height);

        // SaveToFile
        var outSym = TempFile("rail_head_pristine_out.pgm");
        imgSym.SaveToFile(outSym);
        Assert.True(File.Exists(outSym));
        var loadedSym = NetpbmImage.LoadFile(outSym);
        Assert.Equal(hsSym, loadedSym.GetHorizontalSymmetry(), precision: 6);
        Assert.Equal(vsSym, loadedSym.GetVerticalSymmetry(), precision: 6);

        var outWorn = TempFile("rail_head_worn_out.pgm");
        imgWorn.SaveToFile(outWorn);
        var loadedWorn = NetpbmImage.LoadFile(outWorn);
        Assert.Equal(hsWorn, loadedWorn.GetHorizontalSymmetry(), precision: 6);
        Assert.Equal(vsWorn, loadedWorn.GetVerticalSymmetry(), precision: 6);

        var ex1 = Record.Exception(() => loadedSym.GetHorizontalSymmetry());
        var ex2 = Record.Exception(() => loadedSym.GetVerticalSymmetry());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
