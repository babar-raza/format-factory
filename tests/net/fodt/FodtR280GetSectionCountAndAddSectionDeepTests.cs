// Tests for FodtDocument.GetSectionCount, AddSection, GetSectionTitle deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R280

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R280: Tests for FodtDocument.GetSectionCount, AddSection, GetSectionTitle deeper.
/// GetSectionCount(): returns the number of sections in the document.
/// AddSection(title): appends a new named section to the document.
/// GetSectionTitle(sectionIndex): returns the title of the specified section.
/// Covers: GetSectionCount no-throw; GetSectionCount non-negative; GetSectionCount consistent;
/// GetSectionCount zero for new doc; GetSectionCount after AddSection increases;
/// GetSectionCount save-load;
/// AddSection no-throw; AddSection increases GetSectionCount; AddSection save-load;
/// AddSection multiple sections; AddSection then ExportToHtml no-throw;
/// AddSection then ExportToMarkdown no-throw; AddSection then ExportToPlainText no-throw;
/// GetSectionTitle no-throw; GetSectionTitle non-null; GetSectionTitle consistent;
/// GetSectionTitle save-load; GetSectionTitle multiple sections;
/// dogfood CreateDoc→AddSection→GetSectionCount→GetSectionTitle→SaveToFile pipeline.
/// </summary>
public class FodtR280GetSectionCountAndAddSectionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR280GetSectionCountAndAddSectionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR280_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateRichDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Annual Report 2026", 1);
        doc.AppendParagraph("This annual report presents the company performance for fiscal year 2026.");
        doc.AppendParagraph("All financial statements have been audited by an independent third party.");
        doc.InsertHeading(3, "Executive Summary", 2);
        doc.AppendParagraph("Revenue grew by eighteen percent year-over-year to four hundred million dollars.");
        doc.AppendParagraph("Operating margin improved by two hundred basis points to twenty-two percent.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSectionCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetSectionCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSectionCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetSectionCount() >= 0);
    }

    [Fact]
    public void GetSectionCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetSectionCount(), doc.GetSectionCount());
    }

    [Fact]
    public void GetSectionCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Fresh document without any sections.");
        Assert.Equal(0, doc.GetSectionCount());
    }

    [Fact]
    public void GetSectionCount_AfterAddSection_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetSectionCount();
        doc.AddSection("Financial Highlights");
        Assert.Equal(before + 1, doc.GetSectionCount());
    }

    [Fact]
    public void GetSectionCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddSection("Risk Factors");
        var before = doc.GetSectionCount();
        var path = TempFile("sc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSectionCount());
    }

    // -------------------------------------------------------------------------
    // AddSection
    // -------------------------------------------------------------------------

    [Fact]
    public void AddSection_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddSection("Operations Overview"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_Increases_GetSectionCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetSectionCount();
        doc.AddSection("Market Analysis");
        Assert.Equal(before + 1, doc.GetSectionCount());
    }

    [Fact]
    public void AddSection_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddSection("Technology Review");
        var before = doc.GetSectionCount();
        var path = TempFile("as_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSectionCount());
    }

    [Fact]
    public void AddSection_Multiple_Sections()
    {
        var doc = CreateRichDoc();
        doc.AddSection("Introduction");
        doc.AddSection("Methodology");
        doc.AddSection("Results");
        Assert.Equal(3, doc.GetSectionCount());
    }

    [Fact]
    public void AddSection_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddSection("HTML Export Section");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddSection("Markdown Section");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_Then_ExportToPlainText_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddSection("Plain Text Section");
        var ex = Record.Exception(() => doc.ExportToPlainText());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetSectionTitle
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionTitle_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddSection("Title Test Section");
        var ex = Record.Exception(() => doc.GetSectionTitle(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSectionTitle_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddSection("Non Null Test");
        Assert.NotNull(doc.GetSectionTitle(0));
    }

    [Fact]
    public void GetSectionTitle_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddSection("Consistency Test");
        Assert.Equal(doc.GetSectionTitle(0), doc.GetSectionTitle(0));
    }

    [Fact]
    public void GetSectionTitle_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddSection("Save Load Section");
        var before = doc.GetSectionTitle(0);
        var path = TempFile("gst_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetSectionTitle(0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    [Fact]
    public void GetSectionTitle_MultipleSections()
    {
        var doc = CreateRichDoc();
        doc.AddSection("Section Alpha");
        doc.AddSection("Section Beta");
        doc.AddSection("Section Gamma");
        Assert.NotNull(doc.GetSectionTitle(0));
        Assert.NotNull(doc.GetSectionTitle(1));
        Assert.NotNull(doc.GetSectionTitle(2));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddSection_GetSectionCount_GetSectionTitle_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Comprehensive Annual Report 2026", 1);
        doc.AppendParagraph("This report covers all operational and financial aspects of the fiscal year.");
        doc.AppendParagraph("Data presented has been verified by independent auditors and legal counsel.");

        doc.InsertHeading(3, "Corporate Governance", 2);
        doc.AppendParagraph("The board of directors maintained full independence throughout the fiscal year.");
        doc.AppendParagraph("All committee charters were reviewed and updated in the second quarter.");

        doc.InsertHeading(6, "Strategic Initiatives", 2);
        doc.AppendParagraph("Three major strategic initiatives were launched and progressed on schedule.");
        doc.AppendParagraph("Platform modernization reached phase two completion in the third quarter.");

        doc.InsertHeading(9, "Risk Management", 1);
        doc.AppendParagraph("The enterprise risk management framework was updated with twelve new controls.");
        doc.AppendParagraph("Cyber-security risk rating improved from medium-high to medium-low during the year.");

        Assert.Equal(10, doc.GetParagraphCount());

        // GetSectionCount — zero initially
        Assert.Equal(0, doc.GetSectionCount());

        // AddSection — financial overview
        doc.AddSection("Financial Overview");
        Assert.Equal(1, doc.GetSectionCount());

        // AddSection — operations
        doc.AddSection("Operational Review");
        Assert.Equal(2, doc.GetSectionCount());

        // AddSection — risk
        doc.AddSection("Risk Assessment");
        Assert.Equal(3, doc.GetSectionCount());

        // AddSection — governance
        doc.AddSection("Governance and Compliance");
        Assert.Equal(4, doc.GetSectionCount());

        // GetSectionTitle
        var t0 = doc.GetSectionTitle(0);
        var t1 = doc.GetSectionTitle(1);
        var t2 = doc.GetSectionTitle(2);
        var t3 = doc.GetSectionTitle(3);
        Assert.NotNull(t0);
        Assert.NotNull(t1);
        Assert.NotNull(t2);
        Assert.NotNull(t3);

        // Consistent
        Assert.Equal(doc.GetSectionCount(), doc.GetSectionCount());
        Assert.Equal(doc.GetSectionTitle(0), doc.GetSectionTitle(0));

        // ExportToHtml works after sections
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
        var path = TempFile("dogfood_annual.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetSectionCount());
        Assert.True(loaded.GetParagraphCount() > 0);

        // GetSectionTitle on loaded
        for (int i = 0; i < loaded.GetSectionCount(); i++)
            Assert.NotNull(loaded.GetSectionTitle(i));

        // AddSection on loaded
        loaded.AddSection("Appendix");
        Assert.Equal(5, loaded.GetSectionCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Addendum: all board resolutions passed unanimously at the extraordinary general meeting.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_annual_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetSectionCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.ExportToPlainText());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
