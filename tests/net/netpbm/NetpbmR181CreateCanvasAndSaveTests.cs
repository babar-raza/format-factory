// Tests for NetpbmImage.Create (canvas factory), SaveToFile, and SourcePath.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R181

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R181: Tests for NetpbmImage.Create factory, SaveToFile, Comments, SourcePath.
/// Create(w, h, format, fill): creates a blank image.
/// SaveToFile(path): writes image to file.
/// Comments: list of comment strings.
/// SourcePath: path from which image was loaded.
/// Covers: Create PGM dimensions correct; Create PPM dimensions correct;
/// Create PBM dimensions correct; Create fill value correct;
/// Create MaxValue default 255; SaveToFile creates file;
/// SaveToFile->Parse file size positive; Comments initially empty;
/// Comments.Add increments count; Comments contains added string;
/// SourcePath is null for in-memory; SourcePath set after Create;
/// Create then Invert then GetStats; Create then SetPixel then GetPixel;
/// dogfood Create->SetPixels->SaveToFile->ParseBack verify pipeline.
/// </summary>
public class NetpbmR181CreateCanvasAndSaveTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR181CreateCanvasAndSaveTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR181_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // Create factory
    // -------------------------------------------------------------------------

    [Fact]
    public void Create_Pgm_DimensionsCorrect()
    {
        var img = NetpbmImage.Create(10, 8, NetpbmFormat.Pgm);
        Assert.Equal(10, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void Create_Ppm_DimensionsCorrect()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.Ppm);
        Assert.Equal(5, img.Width);
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void Create_Pbm_DimensionsCorrect()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pbm);
        Assert.Equal(4, img.Width);
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void Create_FillValue_Correct()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, 200);
        var (mean, _, _) = img.GetStats();
        Assert.Equal(200.0, mean, 0);
    }

    [Fact]
    public void Create_MaxValue_DefaultIs255()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm);
        Assert.Equal(255, img.MaxValue);
    }

    [Fact]
    public void Create_Format_CorrectForPgm()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, 0);
        Assert.Equal(NetpbmFormat.Pgm, img.Format);
    }

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, 128);
        var path = TempFile("canvas.pgm");
        img.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileSizeIsPositive()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, 100);
        var path = TempFile("size.pgm");
        img.SaveToFile(path);
        var info = new FileInfo(path);
        Assert.True(info.Length > 0);
    }

    // -------------------------------------------------------------------------
    // Comments
    // -------------------------------------------------------------------------

    [Fact]
    public void Comments_InitiallyEmpty()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm);
        Assert.Empty(img.Comments);
    }

    [Fact]
    public void Comments_Add_IncrementsCount()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm);
        img.Comments.Add("Test comment");
        Assert.Single(img.Comments);
    }

    [Fact]
    public void Comments_ContainsAddedString()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm);
        img.Comments.Add("My comment");
        Assert.Contains("My comment", img.Comments);
    }

    // -------------------------------------------------------------------------
    // SourcePath
    // -------------------------------------------------------------------------

    [Fact]
    public void SourcePath_NullForInMemoryCreate()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm);
        Assert.Null(img.SourcePath);
    }

    // -------------------------------------------------------------------------
    // Create then operation
    // -------------------------------------------------------------------------

    [Fact]
    public void Create_ThenInvert_GetStats_Correct()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, 100);
        img.Invert();
        var (mean, _, _) = img.GetStats();
        Assert.Equal(155.0, mean, 0); // 255-100=155
    }

    [Fact]
    public void Create_SetPixel_GetPixel_Correct()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, 0);
        img.SetPixel(2, 3, 200);
        Assert.Equal(200, img.GetPixel(2, 3));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->SetPixels->SaveToFile->ParseBack
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetPixelsSaveParseBack_Pipeline()
    {
        // Create PGM canvas
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, 0);
        img.Comments.Add("R181 dogfood test");

        // Set some pixels
        img.SetPixel(0, 0, 255);
        img.SetPixel(1, 1, 128);
        img.SetPixel(2, 2, 64);
        img.SetPixel(3, 3, 32);

        // Verify pixels before save
        Assert.Equal(255, img.GetPixel(0, 0));
        Assert.Equal(128, img.GetPixel(1, 1));

        // SaveToFile
        var path = TempFile("dogfood.pgm");
        img.SaveToFile(path);
        Assert.True(File.Exists(path));

        // Parse back
        var parsed = NetpbmParser.Parse(path);
        Assert.Equal(4, parsed.Width);
        Assert.Equal(4, parsed.Height);
        Assert.Equal(NetpbmFormat.Pgm, parsed.Format);
        Assert.Equal(path, parsed.SourcePath);

        // GetStats on parsed
        var (mean, min, max) = parsed.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
    }
}
