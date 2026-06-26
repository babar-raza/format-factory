// Tests for NetpbmImage.FlipHorizontal, FlipVertical, Rotate90 deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R280

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R280: Tests for NetpbmImage.FlipHorizontal, FlipVertical, Rotate90 deeper.
/// FlipHorizontal(): returns a new image mirrored left-to-right.
/// FlipVertical(): returns a new image mirrored top-to-bottom.
/// Rotate90(): returns a new image rotated 90 degrees clockwise.
/// Covers: FlipHorizontal no-throw; FlipHorizontal same dims; FlipHorizontal consistent;
/// FlipHorizontal save-load; FlipHorizontal double-flip same as original;
/// FlipVertical no-throw; FlipVertical same dims; FlipVertical consistent;
/// FlipVertical save-load; FlipVertical double-flip same as original;
/// Rotate90 no-throw; Rotate90 swaps width and height; Rotate90 consistent;
/// Rotate90 save-load; Rotate90 four-times same as original dims;
/// dogfood LoadFile→FlipHorizontal→FlipVertical→Rotate90→SaveToFile pipeline.
/// </summary>
public class NetpbmR280FlipAndRotateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR280FlipAndRotateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR280_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateRectPgm(int width = 12, int height = 8)
    {
        var path = TempFile($"rect_{width}x{height}.pgm");
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{width} {height}");
        sw.WriteLine("255");
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                // Gradient: x component (left=dark, right=bright)
                int val = (x * 255) / Math.Max(1, width - 1);
                sw.Write(val);
                if (x < width - 1) sw.Write(' ');
            }
            sw.WriteLine();
        }
        return path;
    }

    private string CreateSquarePgm(int size = 8)
    {
        var path = TempFile($"square_{size}x{size}.pgm");
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{size} {size}");
        sw.WriteLine("255");
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                int val = (x + y) * 255 / (2 * (size - 1));
                sw.Write(val);
                if (x < size - 1) sw.Write(' ');
            }
            sw.WriteLine();
        }
        return path;
    }

    // -------------------------------------------------------------------------
    // FlipHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm());
        var ex = Record.Exception(() => img.FlipHorizontal());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipHorizontal_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm());
        var flipped = img.FlipHorizontal();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void FlipHorizontal_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm());
        var f1 = img.FlipHorizontal();
        var f2 = img.FlipHorizontal();
        Assert.Equal(f1.Width, f2.Width);
        Assert.Equal(f1.Height, f2.Height);
    }

    [Fact]
    public void FlipHorizontal_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm());
        var flipped = img.FlipHorizontal();
        var path = TempFile("fh_save.pgm");
        flipped.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(flipped.Width, loaded.Width);
        Assert.Equal(flipped.Height, loaded.Height);
    }

    [Fact]
    public void FlipHorizontal_DoubleFlip_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm());
        var doubleFlipped = img.FlipHorizontal().FlipHorizontal();
        Assert.Equal(img.Width, doubleFlipped.Width);
        Assert.Equal(img.Height, doubleFlipped.Height);
    }

    // -------------------------------------------------------------------------
    // FlipVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm());
        var ex = Record.Exception(() => img.FlipVertical());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipVertical_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm());
        var flipped = img.FlipVertical();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void FlipVertical_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm());
        var f1 = img.FlipVertical();
        var f2 = img.FlipVertical();
        Assert.Equal(f1.Width, f2.Width);
        Assert.Equal(f1.Height, f2.Height);
    }

    [Fact]
    public void FlipVertical_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm());
        var flipped = img.FlipVertical();
        var path = TempFile("fv_save.pgm");
        flipped.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(flipped.Width, loaded.Width);
        Assert.Equal(flipped.Height, loaded.Height);
    }

    [Fact]
    public void FlipVertical_DoubleFlip_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm());
        var doubleFlipped = img.FlipVertical().FlipVertical();
        Assert.Equal(img.Width, doubleFlipped.Width);
        Assert.Equal(img.Height, doubleFlipped.Height);
    }

    // -------------------------------------------------------------------------
    // Rotate90
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate90_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm());
        var ex = Record.Exception(() => img.Rotate90());
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate90_SwapsWidthAndHeight()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm(12, 8));
        var rotated = img.Rotate90();
        Assert.Equal(img.Height, rotated.Width);
        Assert.Equal(img.Width, rotated.Height);
    }

    [Fact]
    public void Rotate90_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm());
        var r1 = img.Rotate90();
        var r2 = img.Rotate90();
        Assert.Equal(r1.Width, r2.Width);
        Assert.Equal(r1.Height, r2.Height);
    }

    [Fact]
    public void Rotate90_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm());
        var rotated = img.Rotate90();
        var path = TempFile("r90_save.pgm");
        rotated.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(rotated.Width, loaded.Width);
        Assert.Equal(rotated.Height, loaded.Height);
    }

    [Fact]
    public void Rotate90_FourTimes_RestoresDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateRectPgm(12, 8));
        var rotated4 = img.Rotate90().Rotate90().Rotate90().Rotate90();
        Assert.Equal(img.Width, rotated4.Width);
        Assert.Equal(img.Height, rotated4.Height);
    }

    [Fact]
    public void Rotate90_Square_SameWidthHeight()
    {
        var img = NetpbmImage.LoadFile(CreateSquarePgm(8));
        var rotated = img.Rotate90();
        Assert.Equal(img.Width, rotated.Width);
        Assert.Equal(img.Height, rotated.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FlipHorizontal_FlipVertical_Rotate90_SaveToFile_Pipeline()
    {
        // Asymmetric image: 16x10
        var srcPath = TempFile("dogfood_src.pgm");
        using (var sw = new StreamWriter(srcPath))
        {
            sw.WriteLine("P2");
            sw.WriteLine("16 10");
            sw.WriteLine("255");
            for (int y = 0; y < 10; y++)
            {
                for (int x = 0; x < 16; x++)
                {
                    int val = (x * y * 255) / (15 * 9);
                    sw.Write(Math.Min(255, val));
                    if (x < 15) sw.Write(' ');
                }
                sw.WriteLine();
            }
        }

        var img = NetpbmImage.LoadFile(srcPath);
        Assert.Equal(16, img.Width);
        Assert.Equal(10, img.Height);

        // FlipHorizontal
        var fh = img.FlipHorizontal();
        Assert.Equal(16, fh.Width);
        Assert.Equal(10, fh.Height);
        var fhPath = TempFile("dogfood_fh.pgm");
        fh.SaveToFile(fhPath);
        Assert.True(File.Exists(fhPath));
        var fhLoaded = NetpbmImage.LoadFile(fhPath);
        Assert.Equal(16, fhLoaded.Width);
        Assert.Equal(10, fhLoaded.Height);

        // Double flip = original dims
        var fhh = fh.FlipHorizontal();
        Assert.Equal(img.Width, fhh.Width);
        Assert.Equal(img.Height, fhh.Height);

        // FlipVertical
        var fv = img.FlipVertical();
        Assert.Equal(16, fv.Width);
        Assert.Equal(10, fv.Height);
        var fvPath = TempFile("dogfood_fv.pgm");
        fv.SaveToFile(fvPath);
        Assert.True(File.Exists(fvPath));
        var fvLoaded = NetpbmImage.LoadFile(fvPath);
        Assert.Equal(16, fvLoaded.Width);
        Assert.Equal(10, fvLoaded.Height);

        // Rotate90 — width/height swap
        var r90 = img.Rotate90();
        Assert.Equal(10, r90.Width);  // old height
        Assert.Equal(16, r90.Height); // old width
        var r90Path = TempFile("dogfood_r90.pgm");
        r90.SaveToFile(r90Path);
        Assert.True(File.Exists(r90Path));
        var r90Loaded = NetpbmImage.LoadFile(r90Path);
        Assert.Equal(10, r90Loaded.Width);
        Assert.Equal(16, r90Loaded.Height);

        // 4 rotations restore original dims
        var r360 = img.Rotate90().Rotate90().Rotate90().Rotate90();
        Assert.Equal(img.Width, r360.Width);
        Assert.Equal(img.Height, r360.Height);

        // Chain: FlipH + FlipV + Rotate90
        var chain = img.FlipHorizontal().FlipVertical().Rotate90();
        Assert.Equal(img.Height, chain.Width);
        Assert.Equal(img.Width, chain.Height);
        var chainPath = TempFile("dogfood_chain.pgm");
        chain.SaveToFile(chainPath);
        Assert.True(File.Exists(chainPath));
        Assert.True(new FileInfo(chainPath).Length > 0);
        var chainLoaded = NetpbmImage.LoadFile(chainPath);
        Assert.Equal(chain.Width, chainLoaded.Width);
        Assert.Equal(chain.Height, chainLoaded.Height);

        // MaxVal preserved across operations
        Assert.Equal(img.MaxVal, fh.MaxVal);
        Assert.Equal(img.MaxVal, fv.MaxVal);
        Assert.Equal(img.MaxVal, r90.MaxVal);

        // GetBrightness preserved by flip (same pixels, just reordered)
        Assert.Equal(img.GetBrightness(), fh.GetBrightness(), 3);
        Assert.Equal(img.GetBrightness(), fv.GetBrightness(), 3);

        // Second doc — square image (8x8)
        var sq = NetpbmImage.LoadFile(CreateSquarePgm(8));
        var sqR = sq.Rotate90();
        Assert.Equal(sq.Width, sqR.Width); // square: unchanged
        Assert.Equal(sq.Height, sqR.Height);
        var sqPath = TempFile("dogfood_sq_r90.pgm");
        sqR.SaveToFile(sqPath);
        Assert.True(File.Exists(sqPath));
        var sqLoaded = NetpbmImage.LoadFile(sqPath);
        Assert.Equal(8, sqLoaded.Width);
        Assert.Equal(8, sqLoaded.Height);
    }
}
