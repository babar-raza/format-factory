// Tests for NetpbmImage.FlipHorizontal, FlipVertical, Rotate90 deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R266

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R266: Tests for NetpbmImage.FlipHorizontal, FlipVertical, Rotate90 deeper.
/// FlipHorizontal(): returns a new image mirrored left-to-right.
/// FlipVertical(): returns a new image mirrored top-to-bottom.
/// Rotate90(): returns a new image rotated 90 degrees clockwise.
/// Covers: FlipHorizontal non-null; FlipHorizontal no-throw; FlipHorizontal preserves dims;
/// FlipHorizontal double-flip restores; FlipHorizontal consistent; FlipHorizontal save-load;
/// FlipHorizontal GetPixelValue at edge; FlipHorizontal then ExportToHtml no-throw;
/// FlipVertical non-null; FlipVertical no-throw; FlipVertical preserves dims;
/// FlipVertical double-flip restores; FlipVertical consistent; FlipVertical save-load;
/// Rotate90 non-null; Rotate90 no-throw; Rotate90 swaps width/height;
/// Rotate90 consistent; Rotate90 four-times restores; Rotate90 save-load;
/// Rotate90 GetWidth/GetHeight swapped; Rotate90 then FlipHorizontal no-throw;
/// dogfood CreateImage→FlipHorizontal→FlipVertical→Rotate90→SaveToFile pipeline.
/// </summary>
public class NetpbmR266FlipAndRotateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR266FlipAndRotateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR266_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateGradientPgm(int width = 80, int height = 60)
    {
        var path = TempFile($"gradient_{width}x{height}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int val = (x * 255) / (width - 1);
                sb.Append(val);
                if (x < width - 1) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateRectPgm(int width = 80, int height = 50)
    {
        var path = TempFile($"rect_{width}x{height}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                sb.Append(128);
                if (x < width - 1) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // FlipHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.NotNull(img.FlipHorizontal());
    }

    [Fact]
    public void FlipHorizontal_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.FlipHorizontal());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipHorizontal_PreservesDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var flipped = img.FlipHorizontal();
        Assert.Equal(img.GetWidth(), flipped.GetWidth());
        Assert.Equal(img.GetHeight(), flipped.GetHeight());
    }

    [Fact]
    public void FlipHorizontal_DoubleFlip_Restores()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var doubled = img.FlipHorizontal().FlipHorizontal();
        Assert.Equal(img.GetWidth(), doubled.GetWidth());
        Assert.Equal(img.GetHeight(), doubled.GetHeight());
        // Pixel values should match after double flip
        Assert.Equal(img.GetPixelValue(0, 0), doubled.GetPixelValue(0, 0));
    }

    [Fact]
    public void FlipHorizontal_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var f1 = img.FlipHorizontal();
        var f2 = img.FlipHorizontal();
        Assert.Equal(f1.GetWidth(), f2.GetWidth());
        Assert.Equal(f1.GetPixelValue(0, 0), f2.GetPixelValue(0, 0));
    }

    [Fact]
    public void FlipHorizontal_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var flipped = img.FlipHorizontal();
        var path = TempFile("fh_save.pgm");
        flipped.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(flipped.GetWidth(), loaded.GetWidth());
        Assert.Equal(flipped.GetHeight(), loaded.GetHeight());
    }

    [Fact]
    public void FlipHorizontal_Then_ExportToHtml_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var flipped = img.FlipHorizontal();
        var ex = Record.Exception(() => flipped.ExportToHtml());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // FlipVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.NotNull(img.FlipVertical());
    }

    [Fact]
    public void FlipVertical_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.FlipVertical());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipVertical_PreservesDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var flipped = img.FlipVertical();
        Assert.Equal(img.GetWidth(), flipped.GetWidth());
        Assert.Equal(img.GetHeight(), flipped.GetHeight());
    }

    [Fact]
    public void FlipVertical_DoubleFlip_Restores()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var doubled = img.FlipVertical().FlipVertical();
        Assert.Equal(img.GetWidth(), doubled.GetWidth());
        Assert.Equal(img.GetHeight(), doubled.GetHeight());
        Assert.Equal(img.GetPixelValue(0, 0), doubled.GetPixelValue(0, 0));
    }

    [Fact]
    public void FlipVertical_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var f1 = img.FlipVertical();
        var f2 = img.FlipVertical();
        Assert.Equal(f1.GetWidth(), f2.GetWidth());
    }

    [Fact]
    public void FlipVertical_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var flipped = img.FlipVertical();
        var path = TempFile("fv_save.pgm");
        flipped.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(flipped.GetWidth(), loaded.GetWidth());
        Assert.Equal(flipped.GetHeight(), loaded.GetHeight());
    }

    // -------------------------------------------------------------------------
    // Rotate90
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate90_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.NotNull(img.Rotate90());
    }

    [Fact]
    public void Rotate90_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.Rotate90());
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate90_Swaps_Width_And_Height()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm(80, 50));
        var rotated = img.Rotate90();
        Assert.Equal(img.GetHeight(), rotated.GetWidth());
        Assert.Equal(img.GetWidth(), rotated.GetHeight());
    }

    [Fact]
    public void Rotate90_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var r1 = img.Rotate90();
        var r2 = img.Rotate90();
        Assert.Equal(r1.GetWidth(), r2.GetWidth());
        Assert.Equal(r1.GetHeight(), r2.GetHeight());
    }

    [Fact]
    public void Rotate90_FourTimes_RestoresOriginal()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 80));
        var restored = img.Rotate90().Rotate90().Rotate90().Rotate90();
        Assert.Equal(img.GetWidth(), restored.GetWidth());
        Assert.Equal(img.GetHeight(), restored.GetHeight());
        Assert.Equal(img.GetPixelValue(0, 0), restored.GetPixelValue(0, 0));
    }

    [Fact]
    public void Rotate90_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm(80, 50));
        var rotated = img.Rotate90();
        var path = TempFile("r90_save.pgm");
        rotated.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(rotated.GetWidth(), loaded.GetWidth());
        Assert.Equal(rotated.GetHeight(), loaded.GetHeight());
    }

    [Fact]
    public void Rotate90_Then_FlipHorizontal_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.Rotate90().FlipHorizontal());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FlipHorizontal_FlipVertical_Rotate90_SaveToFile_Pipeline()
    {
        // Create asymmetric gradient image (wide rectangle)
        var path = TempFile("dogfood_gradient.pgm");
        int width = 100, height = 60;
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int val = (x * 255) / (width - 1);
                sb.Append(val);
                if (x < width - 1) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(width, img.GetWidth());
        Assert.Equal(height, img.GetHeight());

        // FlipHorizontal
        var fh = img.FlipHorizontal();
        Assert.NotNull(fh);
        Assert.Equal(width, fh.GetWidth());
        Assert.Equal(height, fh.GetHeight());

        // Double flip restores
        var dblFh = fh.FlipHorizontal();
        Assert.Equal(img.GetPixelValue(0, 0), dblFh.GetPixelValue(0, 0));
        Assert.Equal(img.GetPixelValue(width - 1, 0), dblFh.GetPixelValue(width - 1, 0));

        // FlipVertical
        var fv = img.FlipVertical();
        Assert.NotNull(fv);
        Assert.Equal(width, fv.GetWidth());
        Assert.Equal(height, fv.GetHeight());

        // Double vertical flip restores
        var dblFv = fv.FlipVertical();
        Assert.Equal(img.GetPixelValue(0, 0), dblFv.GetPixelValue(0, 0));

        // Rotate90 — swaps width/height
        var r90 = img.Rotate90();
        Assert.NotNull(r90);
        Assert.Equal(height, r90.GetWidth());
        Assert.Equal(width, r90.GetHeight());

        // Rotate90 consistent
        Assert.Equal(r90.GetWidth(), img.Rotate90().GetWidth());

        // Four rotations restore original
        var restored = img.Rotate90().Rotate90().Rotate90().Rotate90();
        Assert.Equal(img.GetWidth(), restored.GetWidth());
        Assert.Equal(img.GetHeight(), restored.GetHeight());

        // Chained: FlipH + FlipV + Rotate90
        var chained = img.FlipHorizontal().FlipVertical().Rotate90();
        Assert.NotNull(chained);
        Assert.Equal(height, chained.GetWidth());
        Assert.Equal(width, chained.GetHeight());

        // SaveToFile flipped
        var fhPath = TempFile("dogfood_fliph.pgm");
        fh.SaveToFile(fhPath);
        Assert.True(File.Exists(fhPath));
        var loadedFh = NetpbmImage.LoadFile(fhPath);
        Assert.Equal(width, loadedFh.GetWidth());
        Assert.Equal(height, loadedFh.GetHeight());

        // SaveToFile rotated
        var r90Path = TempFile("dogfood_rot90.pgm");
        r90.SaveToFile(r90Path);
        Assert.True(File.Exists(r90Path));
        var loadedR90 = NetpbmImage.LoadFile(r90Path);
        Assert.Equal(height, loadedR90.GetWidth());
        Assert.Equal(width, loadedR90.GetHeight());

        // ExportToHtml on all transforms
        var ex1 = Record.Exception(() => fh.ExportToHtml());
        var ex2 = Record.Exception(() => fv.ExportToHtml());
        var ex3 = Record.Exception(() => r90.ExportToHtml());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);

        // GetMeanValue preserved through flip (should be same since same pixel values)
        Assert.Equal(img.GetMeanValue(), fv.GetMeanValue(), 1);

        // Final save — chained transform
        var finalPath = TempFile("dogfood_chained.pgm");
        chained.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = NetpbmImage.LoadFile(finalPath);
        Assert.Equal(chained.GetWidth(), final.GetWidth());
        Assert.Equal(chained.GetHeight(), final.GetHeight());
        Assert.True(final.GetWidth() > 0);
        Assert.True(final.GetHeight() > 0);
    }
}
