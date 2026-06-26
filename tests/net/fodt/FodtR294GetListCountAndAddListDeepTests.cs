// Tests for FodtDocument.GetListCount, AddBulletList, AddNumberedList deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R294

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R294: Tests for FodtDocument.GetListCount, AddBulletList, AddNumberedList deeper.
/// GetListCount(): returns the number of lists in the document.
/// AddBulletList(items): adds a bulleted list to the document.
/// AddNumberedList(items): adds a numbered list to the document.
/// Covers: GetListCount no-throw; GetListCount non-negative; GetListCount consistent;
/// GetListCount save-load; GetListCount zero for new doc;
/// AddBulletList no-throw; AddBulletList increases count; AddBulletList save-load;
/// AddBulletList multiple; AddBulletList then ExportToHtml no-throw;
/// AddBulletList then ExportToMarkdown no-throw; AddBulletList then GetCharCount positive;
/// AddNumberedList no-throw; AddNumberedList increases count; AddNumberedList save-load;
/// AddNumberedList multiple items; AddNumberedList then ExportToHtml no-throw;
/// dogfood CreateDoc→AddBulletList→AddNumberedList→GetListCount→SaveToFile pipeline.
/// </summary>
public class FodtR294GetListCountAndAddListDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR294GetListCountAndAddListDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR294_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static Fodt​Document CreateRichDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Urban Planning and Sustainable Development", 1);
        doc.AppendParagraph("Modern cities face complex challenges in balancing growth with sustainability goals.");
        doc.AppendParagraph("Transit-oriented development reduces car dependency and promotes walkable neighbourhoods.");
        doc.InsertHeading(3, "Green Infrastructure", 2);
        doc.AppendParagraph("Urban green spaces provide cooling effects, stormwater management, and biodiversity corridors.");
        doc.AppendParagraph("Living walls and green roofs reduce energy consumption and improve air quality in dense areas.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetListCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetListCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetListCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetListCount() >= 0);
    }

    [Fact]
    public void GetListCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetListCount(), doc.GetListCount());
    }

    [Fact]
    public void GetListCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No lists here.");
        Assert.Equal(0, doc.GetListCount());
    }

    [Fact]
    public void GetListCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddBulletList(new[] { "Item A", "Item B", "Item C" });
        var before = doc.GetListCount();
        var path = TempFile("lc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListCount());
    }

    // -------------------------------------------------------------------------
    // AddBulletList
    // -------------------------------------------------------------------------

    [Fact]
    public void AddBulletList_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddBulletList(new[] { "Compact cities reduce sprawl", "Mixed land use increases vibrancy" }));
        Assert.Null(ex);
    }

    [Fact]
    public void AddBulletList_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetListCount();
        doc.AddBulletList(new[] { "Green corridors connect habitats", "Parks reduce urban heat island" });
        Assert.Equal(before + 1, doc.GetListCount());
    }

    [Fact]
    public void AddBulletList_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddBulletList(new[] { "Transit nodes anchor development", "Pedestrian paths improve accessibility" });
        var before = doc.GetListCount();
        var path = TempFile("abl_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListCount());
    }

    [Fact]
    public void AddBulletList_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddBulletList(new[] { "First list item A", "First list item B" });
        doc.AddBulletList(new[] { "Second list item X", "Second list item Y" });
        Assert.Equal(2, doc.GetListCount());
    }

    [Fact]
    public void AddBulletList_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddBulletList(new[] { "HTML bullet item 1", "HTML bullet item 2", "HTML bullet item 3" });
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBulletList_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddBulletList(new[] { "Markdown item one", "Markdown item two" });
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBulletList_Then_GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.AddBulletList(new[] { "CharCount test item" });
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // AddNumberedList
    // -------------------------------------------------------------------------

    [Fact]
    public void AddNumberedList_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddNumberedList(new[] { "Step 1: Assess site conditions", "Step 2: Develop master plan" }));
        Assert.Null(ex);
    }

    [Fact]
    public void AddNumberedList_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetListCount();
        doc.AddNumberedList(new[] { "Phase 1: Consultation", "Phase 2: Design", "Phase 3: Implementation" });
        Assert.Equal(before + 1, doc.GetListCount());
    }

    [Fact]
    public void AddNumberedList_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddNumberedList(new[] { "First numbered item", "Second numbered item", "Third numbered item" });
        var before = doc.GetListCount();
        var path = TempFile("anl_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListCount());
    }

    [Fact]
    public void AddNumberedList_Multiple_Items()
    {
        var doc = CreateRichDoc();
        doc.AddNumberedList(new[] { "Item 1", "Item 2", "Item 3", "Item 4", "Item 5" });
        Assert.Equal(1, doc.GetListCount());
    }

    [Fact]
    public void AddNumberedList_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddNumberedList(new[] { "HTML numbered 1", "HTML numbered 2" });
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddBulletList_AddNumberedList_GetListCount_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Digital Transformation Strategy", 1);
        doc.AppendParagraph("Organisations undertaking digital transformation must align technology with business objectives.");
        doc.AppendParagraph("Cultural change is as critical as technology adoption in successful digital transformations.");

        doc.InsertHeading(3, "Key Enablers", 2);
        doc.AppendParagraph("Cloud infrastructure provides the scalability and agility required for digital services.");
        doc.AppendParagraph("Data governance frameworks ensure quality, security, and compliance across digital assets.");

        doc.InsertHeading(6, "Implementation Roadmap", 2);
        doc.AppendParagraph("A phased approach reduces risk while delivering tangible value at each milestone.");
        doc.AppendParagraph("Change management and training programmes must parallel technology deployment timelines.");

        Assert.Equal(7, doc.GetParagraphCount());

        // GetListCount — zero initially
        Assert.Equal(0, doc.GetListCount());

        // AddBulletList — key enablers
        doc.AddBulletList(new[] {
            "Cloud-native architecture for scalability",
            "API-first integration strategy",
            "Data mesh for distributed ownership",
            "DevSecOps for continuous delivery",
            "AI/ML platform for intelligent automation"
        });
        Assert.Equal(1, doc.GetListCount());

        // AddBulletList — success factors
        doc.AddBulletList(new[] {
            "Executive sponsorship and clear vision",
            "Cross-functional empowered teams",
            "Customer-centric design thinking",
            "Agile delivery methodology"
        });
        Assert.Equal(2, doc.GetListCount());

        // AddNumberedList — implementation phases
        doc.AddNumberedList(new[] {
            "Phase 1 (Months 1-3): Foundation — cloud migration and data platform",
            "Phase 2 (Months 4-6): Enablement — API gateway and integration layer",
            "Phase 3 (Months 7-9): Intelligence — analytics and AI capabilities",
            "Phase 4 (Months 10-12): Scale — digital products and customer experience"
        });
        Assert.Equal(3, doc.GetListCount());

        // AddNumberedList — governance steps
        doc.AddNumberedList(new[] {
            "Establish data stewardship council",
            "Define data quality standards",
            "Implement lineage and cataloguing tools",
            "Deploy access control and encryption",
            "Monitor compliance and audit trails"
        });
        Assert.Equal(4, doc.GetListCount());

        // Consistent
        Assert.Equal(doc.GetListCount(), doc.GetListCount());

        // ExportToHtml works
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown works
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // ExportToPlainText works
        var plain = doc.ExportToPlainText();
        Assert.NotNull(plain);
        Assert.NotEmpty(plain);

        // GetCharCount and GetWordCount positive
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_digital.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetListCount());
        Assert.True(loaded.GetParagraphCount() > 0);

        // AddBulletList on loaded
        loaded.AddBulletList(new[] { "Measure ROI and value realisation", "Iterate and continuously improve" });
        Assert.Equal(5, loaded.GetListCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: digital transformation is a continuous journey requiring sustained organisational commitment.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_digital_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetListCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.ExportToPlainText());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
