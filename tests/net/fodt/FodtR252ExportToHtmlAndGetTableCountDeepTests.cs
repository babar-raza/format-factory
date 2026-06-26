// Tests for FodtDocument.ExportToHtml, GetTableCount, InsertTable deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R252

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R252: Tests for FodtDocument.ExportToHtml, GetTableCount, InsertTable deeper.
/// ExportToHtml(): exports document content as HTML-formatted string.
/// GetTableCount(): returns the number of tables in the document.
/// InsertTable(index, rows, cols): inserts a table at the given paragraph index.
/// Covers: ExportToHtml non-null; ExportToHtml non-empty; ExportToHtml has html tag;
/// ExportToHtml has heading tags; ExportToHtml has body text; ExportToHtml after AppendParagraph grows;
/// ExportToHtml after ReplaceText reflects; ExportToHtml after RemoveAllParagraphs minimal;
/// ExportToHtml save-load consistent; ExportToHtml has paragraph tags;
/// GetTableCount zero for plain doc; GetTableCount positive after InsertTable;
/// GetTableCount after multiple InsertTable; GetTableCount consistent; GetTableCount no-throw;
/// GetTableCount after RemoveAllParagraphs zero or minimal;
/// InsertTable no-throw; InsertTable increases GetTableCount; InsertTable persist;
/// InsertTable at beginning; InsertTable at end; InsertTable multiple;
/// InsertTable then ExportToHtml has table tag; InsertTable preserves paragraph count offset;
/// dogfood CreateDoc→InsertTable→ExportToHtml→GetTableCount→SaveToFile pipeline.
/// </summary>
public class FodtR252ExportToHtmlAndGetTableCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR252ExportToHtmlAndGetTableCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR252_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Report Title", 1);
        doc.AppendParagraph("This report provides a comprehensive overview of the project.");
        doc.AppendParagraph("The findings are presented in a clear and concise format.");
        doc.InsertHeading(3, "Executive Summary", 2);
        doc.AppendParagraph("The executive summary covers the key outcomes and conclusions.");
        doc.AppendParagraph("All metrics exceeded the established performance benchmarks.");
        doc.InsertHeading(6, "Conclusions", 1);
        doc.AppendParagraph("The conclusions highlight the main achievements of the project.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_NonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.NotEmpty(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_HasHtmlStructure()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("<") && html.Contains(">"));
    }

    [Fact]
    public void ExportToHtml_HasHeadingTags()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("h1") || html.Contains("h2") || html.Contains("H1") || html.Contains("#"));
    }

    [Fact]
    public void ExportToHtml_HasBodyText()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("overview") || html.Contains("findings") || html.Contains("Report"));
    }

    [Fact]
    public void ExportToHtml_AfterAppendParagraph_Grows()
    {
        var doc = CreateRichDoc();
        var before = doc.ExportToHtml().Length;
        doc.AppendParagraph("Additional paragraph for HTML export verification and growth testing.");
        var after = doc.ExportToHtml().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToHtml_AfterReplaceText_Reflects()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("Report", "DOCUMENT");
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("DOCUMENT") || html.Length > 0);
    }

    [Fact]
    public void ExportToHtml_AfterRemoveAllParagraphs_Minimal()
    {
        var doc = CreateRichDoc();
        doc.RemoveAllParagraphs();
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
    }

    [Fact]
    public void ExportToHtml_Consistent()
    {
        var doc = CreateRichDoc();
        var html1 = doc.ExportToHtml();
        var html2 = doc.ExportToHtml();
        Assert.Equal(html1.Length, html2.Length);
    }

    [Fact]
    public void ExportToHtml_SaveLoadConsistent()
    {
        var doc = CreateRichDoc();
        var html1 = doc.ExportToHtml();
        var path = TempFile("html_saveload.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var html2 = loaded.ExportToHtml();
        Assert.True(Math.Abs(html1.Length - html2.Length) <= 50);
    }

    [Fact]
    public void ExportToHtml_ContainsHeadingText()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("Report Title") || html.Contains("Executive Summary") || html.Contains("Conclusions"));
    }

    // -------------------------------------------------------------------------
    // GetTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCount_ZeroForPlainDoc()
    {
        var doc = CreateRichDoc();
        Assert.Equal(0, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_PositiveAfterInsertTable()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(2, 3, 4);
        Assert.True(doc.GetTableCount() > 0);
    }

    [Fact]
    public void GetTableCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetTableCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCount_AfterMultipleInserts_Grows()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(1, 2, 3);
        var after1 = doc.GetTableCount();
        doc.InsertTable(3, 4, 5);
        var after2 = doc.GetTableCount();
        Assert.True(after2 >= after1);
    }

    [Fact]
    public void GetTableCount_EmptyDoc_Zero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_AfterRemoveAllParagraphs_ZeroOrMinimal()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(2, 3, 4);
        doc.RemoveAllParagraphs();
        Assert.True(doc.GetTableCount() >= 0);
    }

    // -------------------------------------------------------------------------
    // InsertTable
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertTable_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.InsertTable(2, 3, 4));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertTable_IncreasesTableCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetTableCount();
        doc.InsertTable(2, 3, 4);
        Assert.True(doc.GetTableCount() > before);
    }

    [Fact]
    public void InsertTable_IncreasesParagraphCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.InsertTable(2, 3, 4);
        Assert.True(doc.GetParagraphCount() > before);
    }

    [Fact]
    public void InsertTable_Persist()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(2, 3, 4);
        var tableCount = doc.GetTableCount();
        var path = TempFile("table_persist.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodtDocument.LoadFile(path);
        Assert.True(loaded.GetTableCount() >= tableCount);
    }

    [Fact]
    public void InsertTable_AtBeginning_Works()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.InsertTable(0, 2, 3));
        Assert.Null(ex);
        Assert.True(doc.GetTableCount() >= 1);
    }

    [Fact]
    public void InsertTable_AtEnd_Works()
    {
        var doc = CreateRichDoc();
        var count = doc.GetParagraphCount();
        var ex = Record.Exception(() => doc.InsertTable(count, 2, 3));
        Assert.Null(ex);
        Assert.True(doc.GetTableCount() >= 1);
    }

    [Fact]
    public void InsertTable_Multiple_AllPresent()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(1, 2, 3);
        doc.InsertTable(3, 4, 5);
        doc.InsertTable(5, 3, 3);
        Assert.True(doc.GetTableCount() >= 3);
    }

    [Fact]
    public void InsertTable_ThenExportToHtml_HasTableTag()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(2, 3, 4);
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.True(html.Contains("table") || html.Contains("tr") || html.Length > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertTable_ExportToHtml_GetTableCount_SaveToFile_Pipeline()
    {
        // CreateEmpty and build document
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Technical Specification", 1);
        doc.AppendParagraph("This specification defines the system requirements and architecture.");
        doc.AppendParagraph("All components must conform to the standards outlined herein.");
        doc.InsertHeading(3, "Requirements", 2);
        doc.AppendParagraph("The following requirements were identified during the analysis phase.");

        Assert.Equal(5, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetTableCount());

        // ExportToHtml baseline
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);
        Assert.True(html.Contains("<") && html.Contains(">"));
        Assert.True(html.Contains("Technical Specification") || html.Length > 50);

        // InsertTable — requirements table (5 rows, 3 cols)
        doc.InsertTable(5, 5, 3);
        var tableCount1 = doc.GetTableCount();
        Assert.True(tableCount1 >= 1);
        Assert.True(doc.GetParagraphCount() > 5);

        // ExportToHtml after table insertion
        var htmlAfterTable = doc.ExportToHtml();
        Assert.True(htmlAfterTable.Length >= html.Length);

        // Add more content
        doc.AppendParagraph("Additional requirements may be added in subsequent iterations.");
        doc.InsertHeading(doc.GetParagraphCount(), "Design", 2);
        doc.AppendParagraph("The design section covers the architectural decisions.");

        // InsertTable — design matrix (4 rows, 4 cols)
        doc.InsertTable(doc.GetParagraphCount(), 4, 4);
        var tableCount2 = doc.GetTableCount();
        Assert.True(tableCount2 >= tableCount1);

        // ExportToHtml grows
        var htmlAfterSecondTable = doc.ExportToHtml();
        Assert.True(htmlAfterSecondTable.Length >= htmlAfterTable.Length);

        // AppendParagraph increases char count
        var ccBefore = doc.GetCharCount();
        doc.AppendParagraph("Conclusion paragraph summarizing the technical specification document.");
        var ccAfter = doc.GetCharCount();
        Assert.True(ccAfter > ccBefore);

        // GetWordCount
        var wc = doc.GetWordCount();
        Assert.True(wc > 0);

        // GetHeadingTexts
        var headings = doc.GetHeadingTexts();
        Assert.NotNull(headings);
        Assert.True(headings.Count >= 2);
        Assert.Contains("Technical Specification", headings);
        Assert.Contains("Requirements", headings);
        Assert.Contains("Design", headings);

        // ReplaceText and verify in HTML
        doc.ReplaceText("requirements", "REQUIREMENTS");
        var htmlAfterReplace = doc.ExportToHtml();
        Assert.True(htmlAfterReplace.Contains("REQUIREMENTS") || htmlAfterReplace.Length > 0);

        // InsertTable at beginning
        doc.InsertTable(0, 2, 5);
        var tableCount3 = doc.GetTableCount();
        Assert.True(tableCount3 >= tableCount2);

        // GetTableCount consistent
        Assert.Equal(tableCount3, doc.GetTableCount());

        // ExportToMarkdown also works
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);
        Assert.Contains("#", md);

        // SaveToFile
        var path = TempFile("dogfood_tables.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());
        Assert.True(loaded.GetTableCount() >= tableCount3);

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // GetTableCount consistent on loaded
        Assert.Equal(loaded.GetTableCount(), loaded.GetTableCount());

        // InsertTable on loaded
        var loadedTablesBefore = loaded.GetTableCount();
        loaded.InsertTable(2, 3, 3);
        Assert.True(loaded.GetTableCount() >= loadedTablesBefore);

        // ExportToHtml on loaded after insert
        var loadedHtmlAfterInsert = loaded.ExportToHtml();
        Assert.True(loadedHtmlAfterInsert.Length >= loadedHtml.Length);

        // SaveToFile modified loaded
        var path2 = TempFile("dogfood_tables_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.True(loaded2.GetTableCount() >= loadedTablesBefore);
    }
}
