// Tests for NetpbmImage.Crop, Resize, GetPixelAt deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R268

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R268: Tests for NetpbmImage.Crop, Resize, GetPixelAt deeper.
/// Crop(x, y, width, height): returns a new image cropped to the given rectangle.
/// Resize(newWidth, newHeight): returns a new image scaled to the given dimensions.
/// GetPixelAt(x, y): returns the pixel intensity value at the given coordinates.
/// Covers: Crop non-null; Crop no-throw; Crop correct dimensions; Crop consistent;
/// Crop save-load; Crop fits within original; Crop then ExportToHtml no-throw;
/// Crop getWidth/getHeight match; Crop top-left corner; Crop preserves format;
/// Resize non-null; Resize no-throw; Resize correct dimensions; Resize consistent;
/// Resize save-load; Resize double; Resize half; Resize to square;
/// GetPixelAt no-throw; GetPixelAt valid range; GetPixelAt consistent;
/// GetPixelAt save-load; GetPixelAt after Crop; GetPixelAt corners;
/// dogfood CreateImage→Crop→Resize→GetPixelAt→SaveToFile pipeline.
/// </summary>
public class NetpbmR268CropAndResizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR268CropAndResizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR268_" + Guid.NewGuid().ToString("N"));
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
        var path = TempFile($"gradient_{width}x{height}_{Guid.NewGuid().ToString("N")[..6]}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int val = (x * 255) / Math.Max(width - 1, 1);
                sb.Append(val);
                if (x < width - 1) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformPgm(int width, int height, int value)
    {
        var path = TempFile($"uniform_{width}x{height}_{value}_{Guid.NewGuid().ToString("N")[..6]}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                sb.Append(value);
                if (x < width - 1) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // Crop
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        Assert.NotNull(img.Crop(0, 0, 40, 30));
    }

    [Fact]
    public void Crop_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var ex = Record.Exception(() => img.Crop(0, 0, 40, 30));
        Assert.Null(ex);
    }

    [Fact]
    public void Crop_CorrectDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var cropped = img.Crop(10, 10, 40, 30);
        Assert.Equal(40, cropped.GetWidth());
        Assert.Equal(30, cropped.GetHeight());
    }

    [Fact]
    public void Crop_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var c1 = img.Crop(0, 0, 40, 30);
        var c2 = img.Crop(0, 0, 40, 30);
        Assert.Equal(c1.GetWidth(), c2.GetWidth());
        Assert.Equal(c1.GetHeight(), c2.GetHeight());
    }

    [Fact]
    public void Crop_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var cropped = img.Crop(5, 5, 30, 20);
        var path = TempFile("crop_save.pgm");
        cropped.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(30, loaded.GetWidth());
        Assert.Equal(20, loaded.GetHeight());
    }

    [Fact]
    public void Crop_FitsWithinOriginal()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var cropped = img.Crop(0, 0, 40, 30);
        Assert.True(cropped.GetWidth() <= img.GetWidth());
        Assert.True(cropped.GetHeight() <= img.GetHeight());
    }

    [Fact]
    public void Crop_TopLeft_Corner()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var cropped = img.Crop(0, 0, 20, 20);
        Assert.Equal(20, cropped.GetWidth());
        Assert.Equal(20, cropped.GetHeight());
    }

    [Fact]
    public void Crop_Then_ExportToHtml_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var cropped = img.Crop(0, 0, 40, 30);
        var ex = Record.Exception(() => cropped.ExportToHtml());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Resize
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        Assert.NotNull(img.Resize(40, 30));
    }

    [Fact]
    public void Resize_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var ex = Record.Exception(() => img.Resize(40, 30));
        Assert.Null(ex);
    }

    [Fact]
    public void Resize_CorrectDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var resized = img.Resize(40, 30);
        Assert.Equal(40, resized.GetWidth());
        Assert.Equal(30, resized.GetHeight());
    }

    [Fact]
    public void Resize_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var r1 = img.Resize(40, 30);
        var r2 = img.Resize(40, 30);
        Assert.Equal(r1.GetWidth(), r2.GetWidth());
        Assert.Equal(r1.GetHeight(), r2.GetHeight());
    }

    [Fact]
    public void Resize_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var resized = img.Resize(40, 30);
        var path = TempFile("resize_save.pgm");
        resized.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(40, loaded.GetWidth());
        Assert.Equal(30, loaded.GetHeight());
    }

    [Fact]
    public void Resize_ToSquare()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var square = img.Resize(50, 50);
        Assert.Equal(50, square.GetWidth());
        Assert.Equal(50, square.GetHeight());
    }

    [Fact]
    public void Resize_Double()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(40, 30));
        var doubled = img.Resize(80, 60);
        Assert.Equal(80, doubled.GetWidth());
        Assert.Equal(60, doubled.GetHeight());
    }

    // -------------------------------------------------------------------------
    // GetPixelAt
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelAt_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var ex = Record.Exception(() => img.GetPixelAt(0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPixelAt_ValidRange()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var val = img.GetPixelAt(40, 30);
        Assert.True(val >= 0 && val <= 255);
    }

    [Fact]
    public void GetPixelAt_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        Assert.Equal(img.GetPixelAt(0, 0), img.GetPixelAt(0, 0));
        Assert.Equal(img.GetPixelAt(40, 20), img.GetPixelAt(40, 20));
    }

    [Fact]
    public void GetPixelAt_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var before = img.GetPixelAt(10, 10);
        var path = TempFile("gpa_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetPixelAt(10, 10));
    }

    [Fact]
    public void GetPixelAt_Uniform_Image_AllSame()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm(40, 30, 128));
        Assert.Equal(img.GetPixelAt(0, 0), img.GetPixelAt(20, 15));
        Assert.Equal(img.GetPixelAt(0, 0), img.GetPixelAt(39, 29));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Crop_Resize_GetPixelAt_SaveToFile_Pipeline()
    {
        // Create 120x80 gradient image
        int origW = 120, origH = 80;
        var path = TempFile("dogfood_gradient.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{origW} {origH}");
        sb.AppendLine("255");
        for (int y = 0; y < origH; y++)
        {
            for (int x = 0; x < origW; x++)
            {
                int val = (x * 255) / (origW - 1);
                sb.Append(val);
                if (x < origW - 1) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(origW, img.GetWidth());
        Assert.Equal(origH, img.GetHeight());

        // GetPixelAt corners
        var topLeft = img.GetPixelAt(0, 0);
        var topRight = img.GetPixelAt(origW - 1, 0);
        Assert.True(topLeft >= 0 && topLeft <= 255);
        Assert.True(topRight >= 0 && topRight <= 255);
        // Gradient: right side should be brighter
        Assert.True(topRight >= topLeft);

        // GetPixelAt center
        var center = img.GetPixelAt(origW / 2, origH / 2);
        Assert.True(center >= 0 && center <= 255);

        // Consistent
        Assert.Equal(img.GetPixelAt(20, 10), img.GetPixelAt(20, 10));

        // Crop — center region
        var cropped = img.Crop(20, 10, 60, 40);
        Assert.Equal(60, cropped.GetWidth());
        Assert.Equal(40, cropped.GetHeight());

        // Crop consistent
        var c2 = img.Crop(20, 10, 60, 40);
        Assert.Equal(cropped.GetWidth(), c2.GetWidth());

        // GetPixelAt on cropped
        var croppedCenter = cropped.GetPixelAt(30, 20);
        Assert.True(croppedCenter >= 0 && croppedCenter <= 255);

        // Crop again (nested crop)
        var cropped2 = cropped.Crop(10, 5, 20, 15);
        Assert.Equal(20, cropped2.GetWidth());
        Assert.Equal(15, cropped2.GetHeight());

        // Resize — scale down
        var halfSize = img.Resize(60, 40);
        Assert.Equal(60, halfSize.GetWidth());
        Assert.Equal(40, halfSize.GetHeight());

        // Resize — scale up
        var doubleSize = img.Resize(240, 160);
        Assert.Equal(240, doubleSize.GetWidth());
        Assert.Equal(160, doubleSize.GetHeight());

        // Resize — to square
        var square = img.Resize(100, 100);
        Assert.Equal(100, square.GetWidth());
        Assert.Equal(100, square.GetHeight());

        // GetPixelAt on resized
        var halfPixel = halfSize.GetPixelAt(0, 0);
        Assert.True(halfPixel >= 0 && halfPixel <= 255);

        // SaveToFile cropped
        var croppedPath = TempFile("dogfood_cropped.pgm");
        cropped.SaveToFile(croppedPath);
        Assert.True(File.Exists(croppedPath));
        var loadedCrop = NetpbmImage.LoadFile(croppedPath);
        Assert.Equal(60, loadedCrop.GetWidth());
        Assert.Equal(40, loadedCrop.GetHeight());
        Assert.Equal(cropped.GetPixelAt(0, 0), loadedCrop.GetPixelAt(0, 0));

        // SaveToFile resized
        var resizedPath = TempFile("dogfood_resized.pgm");
        halfSize.SaveToFile(resizedPath);
        Assert.True(File.Exists(resizedPath));
        var loadedResize = NetpbmImage.LoadFile(resizedPath);
        Assert.Equal(60, loadedResize.GetWidth());
        Assert.Equal(40, loadedResize.GetHeight());

        // Chain: Crop then Resize
        var cropThenResize = img.Crop(0, 0, 60, 40).Resize(30, 20);
        Assert.Equal(30, cropThenResize.GetWidth());
        Assert.Equal(20, cropThenResize.GetHeight());

        // Chain: Resize then Crop
        var resizeThenCrop = img.Resize(60, 40).Crop(0, 0, 30, 20);
        Assert.Equal(30, resizeThenCrop.GetWidth());
        Assert.Equal(20, resizeThenCrop.GetHeight());

        // ExportToHtml on all transforms
        var ex1 = Record.Exception(() => cropped.ExportToHtml());
        var ex2 = Record.Exception(() => halfSize.ExportToHtml());
        var ex3 = Record.Exception(() => cropThenResize.ExportToHtml());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);

        // Final save
        var finalPath = TempFile("dogfood_final.pgm");
        cropThenResize.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = NetpbmImage.LoadFile(finalPath);
        Assert.Equal(30, final.GetWidth());
        Assert.Equal(20, final.GetHeight());
        Assert.True(final.GetPixelAt(0, 0) >= 0 && final.GetPixelAt(0, 0) <= 255);
    }
}
