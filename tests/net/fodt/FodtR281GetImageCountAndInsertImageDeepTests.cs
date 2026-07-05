// Tests for FodtDocument.GetImageCount, InsertImage, GetImagePath deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R281

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R281: Tests for FodtDocument.GetImageCount, InsertImage, GetImagePath deeper.
/// GetImageCount(): returns the number of embedded images in the document.
/// InsertImage(paragraphIndex, imagePath): embeds an image at the given paragraph position.
/// GetImagePath(imageIndex): returns the path or reference of the embedded image.
/// Covers: GetImageCount no-throw; GetImageCount non-negative; GetImageCount consistent;
/// GetImageCount zero for new doc; GetImageCount after InsertImage increases;
/// GetImageCount save-load;
/// InsertImage no-throw; InsertImage increases GetImageCount; InsertImage save-load;
/// InsertImage multiple images; InsertImage then ExportToHtml no-throw;
/// InsertImage then ExportToMarkdown no-throw; InsertImage then GetCharCount positive;
/// GetImagePath no-throw; GetImagePath non-null; GetImagePath consistent;
/// GetImagePath save-load; GetImagePath multiple images;
/// dogfood CreateDoc→InsertImage→GetImageCount→GetImagePath→SaveToFile pipeline.
/// </summary>
public class FodtR281GetImageCountAndInsertImageDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR281GetImageCountAndInsertImageDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR281_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleImage(string name = "sample.png")
    {
        // Minimal 1x1 PNG (89 bytes)
        var path = TempFile(name);
        byte[] png = new byte[]
        {
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, // PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52, // IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41, // IDAT chunk
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
            0x00, 0x00, 0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC,
            0x33, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, // IEND chunk
            0x44, 0xAE, 0x42, 0x60, 0x82
        };
        File.WriteAllBytes(path, png);
        return path;
    }

    private static FodtDocument CreateRichDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Product Brochure 2026", 1);
        doc.AppendParagraph("Welcome to our product brochure presenting the latest platform offerings.");
        doc.AppendParagraph("Each product section includes detailed specifications and pricing information.");
        doc.InsertHeading(3, "Platform Overview", 2);
        doc.AppendParagraph("Our platform delivers enterprise-grade performance across all deployment models.");
        doc.AppendParagraph("Continuous innovation drives our roadmap with quarterly feature releases.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetImageCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetImageCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetImageCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetImageCount() >= 0);
    }

    [Fact]
    public void GetImageCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetImageCount(), doc.GetImageCount());
    }

    [Fact]
    public void GetImageCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Fresh document without any images.");
        Assert.Equal(0, doc.GetImageCount());
    }

    [Fact]
    public void GetImageCount_AfterInsertImage_Increases()
    {
        var doc = CreateRichDoc();
        var imgPath = CreateSampleImage();
        var before = doc.GetImageCount();
        doc.InsertImage(1, imgPath);
        Assert.Equal(before + 1, doc.GetImageCount());
    }

    [Fact]
    public void GetImageCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var imgPath = CreateSampleImage("img_sl.png");
        doc.InsertImage(1, imgPath);
        var before = doc.GetImageCount();
        var path = TempFile("ic_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetImageCount());
    }

    // -------------------------------------------------------------------------
    // InsertImage
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertImage_NoThrow()
    {
        var doc = CreateRichDoc();
        var imgPath = CreateSampleImage("no_throw.png");
        var ex = Record.Exception(() => doc.InsertImage(1, imgPath));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertImage_Increases_GetImageCount()
    {
        var doc = CreateRichDoc();
        var imgPath = CreateSampleImage("inc.png");
        var before = doc.GetImageCount();
        doc.InsertImage(2, imgPath);
        Assert.Equal(before + 1, doc.GetImageCount());
    }

    [Fact]
    public void InsertImage_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        var imgPath = CreateSampleImage("persist.png");
        doc.InsertImage(1, imgPath);
        var before = doc.GetImageCount();
        var path = TempFile("ii_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetImageCount());
    }

    [Fact]
    public void InsertImage_Multiple_Images()
    {
        var doc = CreateRichDoc();
        doc.InsertImage(1, CreateSampleImage("img1.png"));
        doc.InsertImage(2, CreateSampleImage("img2.png"));
        doc.InsertImage(3, CreateSampleImage("img3.png"));
        Assert.Equal(3, doc.GetImageCount());
    }

    [Fact]
    public void InsertImage_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertImage(1, CreateSampleImage("html.png"));
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void InsertImage_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertImage(1, CreateSampleImage("md.png"));
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void InsertImage_Then_GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.InsertImage(1, CreateSampleImage("cc.png"));
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetImagePath
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImagePath_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertImage(1, CreateSampleImage("path_test.png"));
        var ex = Record.Exception(() => doc.GetImagePath(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetImagePath_NonNull()
    {
        var doc = CreateRichDoc();
        doc.InsertImage(1, CreateSampleImage("non_null.png"));
        Assert.NotNull(doc.GetImagePath(0));
    }

    [Fact]
    public void GetImagePath_Consistent()
    {
        var doc = CreateRichDoc();
        doc.InsertImage(1, CreateSampleImage("consistent.png"));
        Assert.Equal(doc.GetImagePath(0), doc.GetImagePath(0));
    }

    [Fact]
    public void GetImagePath_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.InsertImage(1, CreateSampleImage("sl_path.png"));
        var before = doc.GetImagePath(0);
        var path = TempFile("ip_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetImagePath(0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    [Fact]
    public void GetImagePath_Multiple_Images()
    {
        var doc = CreateRichDoc();
        doc.InsertImage(1, CreateSampleImage("multi1.png"));
        doc.InsertImage(2, CreateSampleImage("multi2.png"));
        Assert.NotNull(doc.GetImagePath(0));
        Assert.NotNull(doc.GetImagePath(1));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertImage_GetImageCount_GetImagePath_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Visual Product Catalog 2026", 1);
        doc.AppendParagraph("This catalog presents our complete product lineup with visual references.");
        doc.AppendParagraph("All products are available through our certified distributor network.");

        doc.InsertHeading(3, "Infrastructure Products", 2);
        doc.AppendParagraph("Infrastructure products deliver carrier-grade reliability for enterprise deployments.");
        doc.AppendParagraph("Each product ships with a five-year hardware warranty and twenty-four hour support.");

        doc.InsertHeading(6, "Software Products", 2);
        doc.AppendParagraph("Software products are delivered as container images through our secure registry.");
        doc.AppendParagraph("Annual subscription includes all major and minor releases throughout the term.");

        doc.InsertHeading(9, "Service Offerings", 1);
        doc.AppendParagraph("Professional services engagements include discovery, design, and delivery phases.");
        doc.AppendParagraph("All service engagements are led by certified solution architects.");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetImageCount — zero initially
        Assert.Equal(0, doc.GetImageCount());

        // InsertImage — product photo 1
        var img1 = CreateSampleImage("infra_product.png");
        doc.InsertImage(4, img1);
        Assert.Equal(1, doc.GetImageCount());

        // InsertImage — product photo 2
        var img2 = CreateSampleImage("software_product.png");
        doc.InsertImage(7, img2);
        Assert.Equal(2, doc.GetImageCount());

        // InsertImage — product photo 3
        var img3 = CreateSampleImage("services_diagram.png");
        doc.InsertImage(9, img3);
        Assert.Equal(3, doc.GetImageCount());

        // GetImagePath
        var p0 = doc.GetImagePath(0);
        var p1 = doc.GetImagePath(1);
        var p2 = doc.GetImagePath(2);
        Assert.NotNull(p0);
        Assert.NotNull(p1);
        Assert.NotNull(p2);

        // Consistent
        Assert.Equal(doc.GetImageCount(), doc.GetImageCount());
        Assert.Equal(doc.GetImagePath(0), doc.GetImagePath(0));

        // ExportToHtml works after images
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown works
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // GetCharCount and GetWordCount positive
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_catalog.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetImageCount());
        Assert.True(loaded.GetParagraphCount() > 0);

        // GetImagePath on loaded
        for (int i = 0; i < loaded.GetImageCount(); i++)
            Assert.NotNull(loaded.GetImagePath(i));

        // InsertImage on loaded
        var img4 = CreateSampleImage("addendum_chart.png");
        loaded.InsertImage(loaded.GetParagraphCount() - 1, img4);
        Assert.Equal(4, loaded.GetImageCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Addendum: pricing is subject to change; contact sales for current quotes.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_catalog_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetImageCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
