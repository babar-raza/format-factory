// Tests for NetpbmImage.CropRegion, ResizeToFit, GetAspectRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R284

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R284: Tests for NetpbmImage.CropRegion, ResizeToFit, GetAspectRatio deeper.
/// CropRegion(x, y, width, height): returns a cropped sub-image.
/// ResizeToFit(maxWidth, maxHeight): returns image scaled to fit within bounds.
/// GetAspectRatio(): returns width/height as a double.
/// Covers: CropRegion no-throw; CropRegion dims leq original; CropRegion non-null;
/// CropRegion save-load; CropRegion consistent MaxVal;
/// ResizeToFit no-throw; ResizeToFit dims leq constraints; ResizeToFit non-null;
/// ResizeToFit save-load; ResizeToFit preserves MaxVal;
/// GetAspectRatio no-throw; GetAspectRatio positive; GetAspectRatio consistent;
/// GetAspectRatio save-load; GetAspectRatio square-is-one;
/// dogfood LoadFile→CropRegion→ResizeToFit→GetAspectRatio→SaveToFile pipeline.
/// </summary>
public class NetpbmR284CropRegionAndResizeToFitDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR284CropRegionAndResizeToFitDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR284_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePgm(int width, int height, int fill = 128)
    {
        var path = TempFile($"img_{width}x{height}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
            {
                if (c > 0) sb.Append(' ');
                sb.Append(fill);
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateSquarePgm()  => CreatePgm(64, 64, 100);
    private string CreateWidePgm()    => CreatePgm(80, 40, 200);

    // -------------------------------------------------------------------------
    // CropRegion
    // -------------------------------------------------------------------------

    [Fact]
    public void CropRegion_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSquarePgm());
        var ex = Record.Exception(() => img.CropRegion(0, 0, 32, 32));
        Assert.Null(ex);
    }

    [Fact]
    public void CropRegion_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateSquarePgm());
        Assert.NotNull(img.CropRegion(0, 0, 32, 32));
    }

    [Fact]
    public void CropRegion_Dims_Leq_Original()
    {
        var img = NetpbmImage.LoadFile(CreateSquarePgm());
        var crop = img.CropRegion(8, 8, 24, 24);
        Assert.True(crop.Width <= img.Width);
        Assert.True(crop.Height <= img.Height);
    }

    [Fact]
    public void CropRegion_Exact_Size()
    {
        var img = NetpbmImage.LoadFile(CreateSquarePgm());
        var crop = img.CropRegion(0, 0, 20, 15);
        Assert.Equal(20, crop.Width);
        Assert.Equal(15, crop.Height);
    }

    [Fact]
    public void CropRegion_Consistent_MaxVal()
    {
        var img = NetpbmImage.LoadFile(CreateSquarePgm());
        var crop = img.CropRegion(4, 4, 16, 16);
        Assert.Equal(img.MaxVal, crop.MaxVal);
    }

    [Fact]
    public void CropRegion_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSquarePgm());
        var crop = img.CropRegion(0, 0, 20, 20);
        var path = TempFile("crop_save.pgm");
        crop.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(crop.Width, loaded.Width);
        Assert.Equal(crop.Height, loaded.Height);
        Assert.Equal(crop.MaxVal, loaded.MaxVal);
    }

    // -------------------------------------------------------------------------
    // ResizeToFit
    // -------------------------------------------------------------------------

    [Fact]
    public void ResizeToFit_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateWidePgm());
        var ex = Record.Exception(() => img.ResizeToFit(40, 40));
        Assert.Null(ex);
    }

    [Fact]
    public void ResizeToFit_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateWidePgm());
        Assert.NotNull(img.ResizeToFit(40, 40));
    }

    [Fact]
    public void ResizeToFit_Dims_Leq_Constraints()
    {
        var img = NetpbmImage.LoadFile(CreateWidePgm());
        var resized = img.ResizeToFit(40, 40);
        Assert.True(resized.Width <= 40);
        Assert.True(resized.Height <= 40);
    }

    [Fact]
    public void ResizeToFit_NonZero_Dims()
    {
        var img = NetpbmImage.LoadFile(CreateWidePgm());
        var resized = img.ResizeToFit(40, 40);
        Assert.True(resized.Width > 0);
        Assert.True(resized.Height > 0);
    }

    [Fact]
    public void ResizeToFit_Preserves_MaxVal()
    {
        var img = NetpbmImage.LoadFile(CreateSquarePgm());
        var resized = img.ResizeToFit(32, 32);
        Assert.Equal(img.MaxVal, resized.MaxVal);
    }

    [Fact]
    public void ResizeToFit_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateWidePgm());
        var resized = img.ResizeToFit(30, 30);
        var path = TempFile("resized_save.pgm");
        resized.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(resized.Width, loaded.Width);
        Assert.Equal(resized.Height, loaded.Height);
    }

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
        var img = NetpbmImage.LoadFile(CreateWidePgm());
        Assert.True(img.GetAspectRatio() > 0.0);
    }

    [Fact]
    public void GetAspectRatio_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateWidePgm());
        Assert.Equal(img.GetAspectRatio(), img.GetAspectRatio());
    }

    [Fact]
    public void GetAspectRatio_Square_IsOne()
    {
        var img = NetpbmImage.LoadFile(CreateSquarePgm());
        Assert.Equal(1.0, img.GetAspectRatio(), 4);
    }

    [Fact]
    public void GetAspectRatio_Wide_GreaterThanOne()
    {
        var img = NetpbmImage.LoadFile(CreateWidePgm()); // 80x40
        Assert.True(img.GetAspectRatio() > 1.0);
    }

    [Fact]
    public void GetAspectRatio_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateWidePgm());
        var before = img.GetAspectRatio();
        var path = TempFile("ar_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetAspectRatio(), 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CropRegion_ResizeToFit_GetAspectRatio_SaveToFile_Pipeline()
    {
        // Build a 96x64 gradient PGM
        var srcPath = TempFile("dogfood_src.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("96 64");
        sb.AppendLine("255");
        for (int r = 0; r < 64; r++)
        {
            for (int c = 0; c < 96; c++)
            {
                if (c > 0) sb.Append(' ');
                sb.Append((r * 4) % 256);
            }
            sb.AppendLine();
        }
        File.WriteAllText(srcPath, sb.ToString());

        var img = NetpbmImage.LoadFile(srcPath);
        Assert.Equal(96, img.Width);
        Assert.Equal(64, img.Height);

        // GetAspectRatio — wider than tall → > 1.0
        var ar = img.GetAspectRatio();
        Assert.True(ar > 1.0);
        Assert.Equal(ar, img.GetAspectRatio()); // consistent

        // CropRegion — top-left 48x32 quadrant
        var crop = img.CropRegion(0, 0, 48, 32);
        Assert.NotNull(crop);
        Assert.Equal(48, crop.Width);
        Assert.Equal(32, crop.Height);
        Assert.Equal(img.MaxVal, crop.MaxVal);
        Assert.True(crop.GetAspectRatio() > 0);

        // CropRegion — bottom-right 48x32 quadrant
        var crop2 = img.CropRegion(48, 32, 48, 32);
        Assert.NotNull(crop2);
        Assert.Equal(48, crop2.Width);
        Assert.Equal(32, crop2.Height);

        // ResizeToFit — 48x48 box (should produce ≤48x48 image)
        var resized = img.ResizeToFit(48, 48);
        Assert.NotNull(resized);
        Assert.True(resized.Width <= 48);
        Assert.True(resized.Height <= 48);
        Assert.True(resized.Width > 0 && resized.Height > 0);
        Assert.Equal(img.MaxVal, resized.MaxVal);

        // Consistent aspect ratio of resized
        Assert.Equal(resized.GetAspectRatio(), resized.GetAspectRatio());

        // SaveToFile — crop
        var cropPath = TempFile("dogfood_crop.pgm");
        crop.SaveToFile(cropPath);
        Assert.True(File.Exists(cropPath));
        Assert.True(new FileInfo(cropPath).Length > 0);

        // LoadFile and verify crop
        var loadedCrop = NetpbmImage.LoadFile(cropPath);
        Assert.Equal(48, loadedCrop.Width);
        Assert.Equal(32, loadedCrop.Height);
        Assert.Equal(img.MaxVal, loadedCrop.MaxVal);
        Assert.Equal(crop.GetAspectRatio(), loadedCrop.GetAspectRatio(), 4);

        // SaveToFile — resized
        var resizedPath = TempFile("dogfood_resized.pgm");
        resized.SaveToFile(resizedPath);
        Assert.True(File.Exists(resizedPath));
        var loadedResized = NetpbmImage.LoadFile(resizedPath);
        Assert.Equal(resized.Width, loadedResized.Width);
        Assert.Equal(resized.Height, loadedResized.Height);

        // CropRegion from resized
        var cropFromResized = resized.CropRegion(0, 0, resized.Width / 2, resized.Height / 2);
        Assert.NotNull(cropFromResized);
        Assert.True(cropFromResized.Width > 0);
        Assert.True(cropFromResized.Height > 0);

        // Final save
        var finalPath = TempFile("dogfood_final.pgm");
        cropFromResized.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var loaded2 = NetpbmImage.LoadFile(finalPath);
        Assert.Equal(cropFromResized.Width, loaded2.Width);
        Assert.Equal(cropFromResized.Height, loaded2.Height);
        Assert.True(loaded2.GetAspectRatio() > 0);
    }
}
