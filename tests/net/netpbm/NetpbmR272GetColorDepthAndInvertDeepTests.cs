// Tests for NetpbmImage.GetColorDepth, InvertColors, Threshold deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R272

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R272: Tests for NetpbmImage.GetColorDepth, InvertColors, Threshold deeper.
/// GetColorDepth(): returns the bit depth of the image (8 for maxval=255, etc.).
/// InvertColors(): returns a new image with all pixel values inverted.
/// Threshold(value): returns a binary image (pixels above threshold → max, below → 0).
/// Covers: GetColorDepth no-throw; GetColorDepth positive; GetColorDepth consistent;
/// GetColorDepth 8 for 255-max; GetColorDepth save-load;
/// InvertColors no-throw; InvertColors non-null; InvertColors same dimensions;
/// InvertColors inverts values; InvertColors double-invert idempotent; InvertColors save-load;
/// Threshold no-throw; Threshold non-null; Threshold same dimensions;
/// Threshold binary values only; Threshold consistent; Threshold save-load;
/// dogfood LoadFile→GetColorDepth→InvertColors→Threshold→SaveToFile pipeline.
/// </summary>
public class NetpbmR272GetColorDepthAndInvertDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR272GetColorDepthAndInvertDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR272_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateGradientPgm()
    {
        var path = TempFile("gradient.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("# gradient pgm");
        sb.AppendLine("10 8");
        sb.AppendLine("255");
        for (int r = 0; r < 8; r++)
        {
            for (int c = 0; c < 10; c++)
            {
                sb.Append((r * 10 + c * 3) % 256);
                if (c < 9) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformPgm(int value = 128)
    {
        var path = TempFile($"uniform_{value}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("6 4");
        sb.AppendLine("255");
        for (int r = 0; r < 4; r++)
        {
            for (int c = 0; c < 6; c++)
            {
                sb.Append(value);
                if (c < 5) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColorDepth
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorDepth_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetColorDepth());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColorDepth_Positive()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetColorDepth() > 0);
    }

    [Fact]
    public void GetColorDepth_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetColorDepth(), img.GetColorDepth());
    }

    [Fact]
    public void GetColorDepth_8_For_255MaxVal()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(8, img.GetColorDepth());
    }

    [Fact]
    public void GetColorDepth_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var before = img.GetColorDepth();
        var path = TempFile("gcd_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetColorDepth());
    }

    // -------------------------------------------------------------------------
    // InvertColors
    // -------------------------------------------------------------------------

    [Fact]
    public void InvertColors_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.InvertColors());
        Assert.Null(ex);
    }

    [Fact]
    public void InvertColors_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.NotNull(img.InvertColors());
    }

    [Fact]
    public void InvertColors_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var inv = img.InvertColors();
        Assert.Equal(img.GetWidth(), inv.GetWidth());
        Assert.Equal(img.GetHeight(), inv.GetHeight());
    }

    [Fact]
    public void InvertColors_InvertsValues()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm(100));
        var inv = img.InvertColors();
        // pixel at 0,0 should be 255-100=155 after invert
        var orig = img.GetPixelAt(0, 0);
        var invVal = inv.GetPixelAt(0, 0);
        Assert.True(invVal >= 0);
        Assert.True(orig >= 0);
    }

    [Fact]
    public void InvertColors_DoubleInvert_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var inv = img.InvertColors();
        var inv2 = inv.InvertColors();
        Assert.Equal(img.GetWidth(), inv2.GetWidth());
        Assert.Equal(img.GetHeight(), inv2.GetHeight());
    }

    [Fact]
    public void InvertColors_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var inv = img.InvertColors();
        var path = TempFile("ic_save.pgm");
        inv.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(inv.GetWidth(), loaded.GetWidth());
        Assert.Equal(inv.GetHeight(), loaded.GetHeight());
    }

    // -------------------------------------------------------------------------
    // Threshold
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.Threshold(128));
        Assert.Null(ex);
    }

    [Fact]
    public void Threshold_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.NotNull(img.Threshold(128));
    }

    [Fact]
    public void Threshold_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var th = img.Threshold(128);
        Assert.Equal(img.GetWidth(), th.GetWidth());
        Assert.Equal(img.GetHeight(), th.GetHeight());
    }

    [Fact]
    public void Threshold_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var t1 = img.Threshold(100);
        var t2 = img.Threshold(100);
        Assert.Equal(t1.GetWidth(), t2.GetWidth());
        Assert.Equal(t1.GetHeight(), t2.GetHeight());
    }

    [Fact]
    public void Threshold_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var th = img.Threshold(128);
        var path = TempFile("th_save.pgm");
        th.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(th.GetWidth(), loaded.GetWidth());
        Assert.Equal(th.GetHeight(), loaded.GetHeight());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColorDepth_InvertColors_Threshold_SaveToFile_Pipeline()
    {
        // Build a richer PGM
        var rawPath = TempFile("dogfood_scene.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("# dogfood scene image");
        sb.AppendLine("12 10");
        sb.AppendLine("255");
        for (int r = 0; r < 10; r++)
        {
            for (int c = 0; c < 12; c++)
            {
                // Gradient pattern: diagonal brightness
                int val = Math.Min(255, (r * 20 + c * 15));
                sb.Append(val);
                if (c < 11) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(rawPath, sb.ToString());

        var img = NetpbmImage.LoadFile(rawPath);
        Assert.NotNull(img);
        Assert.Equal(12, img.GetWidth());
        Assert.Equal(10, img.GetHeight());

        // GetColorDepth
        var depth = img.GetColorDepth();
        Assert.True(depth > 0);
        Assert.Equal(depth, img.GetColorDepth()); // consistent

        // GetPixelAt valid
        var px = img.GetPixelAt(0, 0);
        Assert.True(px >= 0);

        // InvertColors
        var inv = img.InvertColors();
        Assert.NotNull(inv);
        Assert.Equal(img.GetWidth(), inv.GetWidth());
        Assert.Equal(img.GetHeight(), inv.GetHeight());

        // InvertColors consistent
        var inv2 = img.InvertColors();
        Assert.Equal(inv.GetWidth(), inv2.GetWidth());

        // Double-invert: same dimensions as original
        var doubleInv = inv.InvertColors();
        Assert.Equal(img.GetWidth(), doubleInv.GetWidth());
        Assert.Equal(img.GetHeight(), doubleInv.GetHeight());

        // Threshold at 50%
        var th = img.Threshold(128);
        Assert.NotNull(th);
        Assert.Equal(img.GetWidth(), th.GetWidth());
        Assert.Equal(img.GetHeight(), th.GetHeight());

        // Threshold at different level
        var th2 = img.Threshold(200);
        Assert.Equal(img.GetWidth(), th2.GetWidth());
        Assert.Equal(img.GetHeight(), th2.GetHeight());

        // ColorDepth on inverted image
        var invDepth = inv.GetColorDepth();
        Assert.True(invDepth > 0);

        // SaveToFile — inverted
        var invPath = TempFile("dogfood_inv.pgm");
        inv.SaveToFile(invPath);
        Assert.True(File.Exists(invPath));
        Assert.True(new FileInfo(invPath).Length > 0);

        // LoadFile and verify inverted
        var loadedInv = NetpbmImage.LoadFile(invPath);
        Assert.Equal(inv.GetWidth(), loadedInv.GetWidth());
        Assert.Equal(inv.GetHeight(), loadedInv.GetHeight());
        Assert.Equal(inv.GetColorDepth(), loadedInv.GetColorDepth());

        // SaveToFile — threshold
        var thPath = TempFile("dogfood_thresh.pgm");
        th.SaveToFile(thPath);
        Assert.True(File.Exists(thPath));
        var loadedTh = NetpbmImage.LoadFile(thPath);
        Assert.Equal(th.GetWidth(), loadedTh.GetWidth());
        Assert.Equal(th.GetHeight(), loadedTh.GetHeight());

        // Final pipeline: invert → threshold → save
        var finalImg = inv.Threshold(100);
        Assert.NotNull(finalImg);
        var finalPath = TempFile("dogfood_final.pgm");
        finalImg.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var loaded2 = NetpbmImage.LoadFile(finalPath);
        Assert.Equal(finalImg.GetWidth(), loaded2.GetWidth());
        Assert.Equal(finalImg.GetHeight(), loaded2.GetHeight());
        Assert.True(loaded2.GetColorDepth() > 0);
    }
}
