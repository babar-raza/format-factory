// Tests for FodtDocument.InsertImage dedicated coverage.
// Sprint: ff-sprint-s301-dotnet-deepening-20260630
// Ledger: PC-FODT-R316

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R316: Dedicated tests for FodtDocument.InsertImage(imagePath).
/// Null path throws exception.
/// Whitespace path throws exception.
/// Valid call no exception.
/// ParagraphCount unchanged or increases after InsertImage.
/// TableCount unchanged after InsertImage.
/// SectionCount unchanged after InsertImage.
/// Insert twice no exception.
/// Dogfood: insert image no exception.
/// Dogfood: insert image, save, no exception.
/// </summary>
public class FodtR316InsertImageDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string CreateTempPngPath()
    {
        var path = Path.Combine(Path.GetTempPath(), $"fodt_r316_{Guid.NewGuid():N}.png");
        _tempFiles.Add(path);
        // Create a minimal valid 1x1 PNG file (89 bytes)
        byte[] minimalPng = new byte[]
        {
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  // PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  // IHDR length + type
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  // 1x1
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,  // bit depth, color type, CRC
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  // IDAT length + type
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,  // IDAT data
            0x00, 0x00, 0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC,  // IDAT CRC
            0x33, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  // IEND length + type
            0x44, 0xAE, 0x42, 0x60, 0x82                      // IEND CRC
        };
        File.WriteAllBytes(path, minimalPng);
        return path;
    }

    public void Dispose()
    {
        foreach (var f in _tempFiles)
            if (File.Exists(f)) File.Delete(f);
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertImage_NullPath_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.InsertImage(null!));
    }

    [Fact]
    public void InsertImage_WhitespacePath_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.InsertImage("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertImage_ValidPath_NoException()
    {
        var doc = FodtDocument.CreateNew();
        string imgPath = CreateTempPngPath();
        var ex = Record.Exception(() => doc.InsertImage(imgPath));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertImage_ParagraphCountUnchangedOrIncreases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        string imgPath = CreateTempPngPath();
        doc.InsertImage(imgPath);
        int after = doc.ParagraphCount;
        Assert.True(after >= before);
    }

    [Fact]
    public void InsertImage_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int tableBefore = doc.TableCount;
        string imgPath = CreateTempPngPath();
        doc.InsertImage(imgPath);
        Assert.Equal(tableBefore, doc.TableCount);
    }

    [Fact]
    public void InsertImage_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int secBefore = doc.GetSectionCount();
        string imgPath = CreateTempPngPath();
        doc.InsertImage(imgPath);
        Assert.Equal(secBefore, doc.GetSectionCount());
    }

    [Fact]
    public void InsertImage_InsertTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        string imgPath = CreateTempPngPath();
        doc.InsertImage(imgPath);
        var ex = Record.Exception(() => doc.InsertImage(imgPath));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_InsertImage_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Before image");
        string imgPath = CreateTempPngPath();
        var ex = Record.Exception(() => doc.InsertImage(imgPath));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_InsertImageThenSave_NoException()
    {
        var doc = FodtDocument.CreateNew();
        string imgPath = CreateTempPngPath();
        doc.InsertImage(imgPath);
        string savePath = Path.Combine(Path.GetTempPath(), $"fodt_r316_save_{Guid.NewGuid():N}.fodt");
        _tempFiles.Add(savePath);
        var ex = Record.Exception(() => doc.Save(savePath));
        Assert.Null(ex);
    }
}
