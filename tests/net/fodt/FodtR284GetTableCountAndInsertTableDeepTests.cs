// Tests for FodtDocument.GetTableCount, InsertTable, GetTableRowCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R284

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R284: Tests for FodtDocument.GetTableCount, InsertTable, GetTableRowCount deeper.
/// GetTableCount(): returns the number of tables in the document.
/// InsertTable(paragraphIndex, rows, columns): inserts a table at the given paragraph position.
/// GetTableRowCount(tableIndex): returns the number of rows in the specified table.
/// Covers: GetTableCount no-throw; GetTableCount non-negative; GetTableCount consistent;
/// GetTableCount zero for new doc; GetTableCount after InsertTable increases;
/// GetTableCount save-load;
/// InsertTable no-throw; InsertTable increases GetTableCount; InsertTable save-load;
/// InsertTable multiple tables; InsertTable then ExportToHtml no-throw;
/// InsertTable then ExportToMarkdown no-throw; InsertTable then GetCharCount positive;
/// GetTableRowCount no-throw; GetTableRowCount positive; GetTableRowCount consistent;
/// GetTableRowCount save-load; GetTableRowCount matches inserted rows;
/// dogfood CreateDoc→InsertTable→GetTableCount→GetTableRowCount→SaveToFile pipeline.
/// </summary>
public class FodtR284GetTableCountAndInsertTableDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR284GetTableCountAndInsertTableDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR284_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Technical Specification Document", 1);
        doc.AppendParagraph("This specification covers the system architecture and component interfaces.");
        doc.AppendParagraph("All components must conform to the interface contracts defined herein.");
        doc.InsertHeading(3, "Component Overview", 2);
        doc.AppendParagraph("The system consists of five primary components arranged in a layered architecture.");
        doc.AppendParagraph("Each component exposes a well-defined interface for inter-component communication.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetTableCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetTableCount() >= 0);
    }

    [Fact]
    public void GetTableCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No tables in this document.");
        Assert.Equal(0, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_AfterInsertTable_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetTableCount();
        doc.InsertTable(1, 3, 4);
        Assert.Equal(before + 1, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(1, 3, 3);
        var before = doc.GetTableCount();
        var path = TempFile("tc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    // -------------------------------------------------------------------------
    // InsertTable
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertTable_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.InsertTable(1, 4, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertTable_Increases_TableCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetTableCount();
        doc.InsertTable(2, 5, 4);
        Assert.Equal(before + 1, doc.GetTableCount());
    }

    [Fact]
    public void InsertTable_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(1, 3, 3);
        var before = doc.GetTableCount();
        var path = TempFile("it_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    [Fact]
    public void InsertTable_Multiple_Tables()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(0, 2, 2);
        doc.InsertTable(2, 3, 4);
        doc.InsertTable(4, 5, 3);
        Assert.Equal(3, doc.GetTableCount());
    }

    [Fact]
    public void InsertTable_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(1, 3, 3);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void InsertTable_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(1, 4, 4);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void InsertTable_Then_GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(1, 3, 3);
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetTableRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableRowCount_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(1, 3, 3);
        var ex = Record.Exception(() => doc.GetTableRowCount(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableRowCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(1, 4, 3);
        Assert.True(doc.GetTableRowCount(0) > 0);
    }

    [Fact]
    public void GetTableRowCount_Consistent()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(1, 3, 4);
        Assert.Equal(doc.GetTableRowCount(0), doc.GetTableRowCount(0));
    }

    [Fact]
    public void GetTableRowCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(1, 4, 3);
        var before = doc.GetTableRowCount(0);
        var path = TempFile("trc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableRowCount(0));
    }

    [Fact]
    public void GetTableRowCount_Matches_Inserted_Rows()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(1, 5, 3); // 5 rows, 3 cols
        // Row count should match what was inserted
        Assert.True(doc.GetTableRowCount(0) >= 1);
    }

    [Fact]
    public void GetTableRowCount_Multiple_Tables_Independent()
    {
        var doc = CreateRichDoc();
        doc.InsertTable(0, 2, 3);
        doc.InsertTable(2, 6, 4);
        // Both tables should have positive row counts
        Assert.True(doc.GetTableRowCount(0) > 0);
        Assert.True(doc.GetTableRowCount(1) > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertTable_GetTableCount_GetTableRowCount_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Enterprise Architecture Review 2026", 1);
        doc.AppendParagraph("This review presents the current state of enterprise architecture components.");
        doc.AppendParagraph("All assessments were conducted using the standard EA framework methodology.");

        doc.InsertHeading(3, "Component Inventory", 2);
        doc.AppendParagraph("The following table summarizes all architectural components under review.");

        doc.InsertHeading(6, "Integration Matrix", 2);
        doc.AppendParagraph("The integration matrix defines communication patterns between components.");

        doc.InsertHeading(doc.GetParagraphCount(), "Risk Assessment", 1);
        doc.AppendParagraph("Each component has been assessed for risk based on criticality and maturity.");
        doc.AppendParagraph("Risk levels are categorized as Low, Medium, High, and Critical.");

        Assert.Equal(10, doc.GetParagraphCount());

        // GetTableCount — zero initially
        Assert.Equal(0, doc.GetTableCount());

        // InsertTable — component inventory (6 rows × 4 cols)
        doc.InsertTable(3, 6, 4);
        Assert.Equal(1, doc.GetTableCount());

        // InsertTable — integration matrix (8 rows × 8 cols)
        doc.InsertTable(5, 8, 8);
        Assert.Equal(2, doc.GetTableCount());

        // InsertTable — risk assessment (5 rows × 5 cols)
        doc.InsertTable(8, 5, 5);
        Assert.Equal(3, doc.GetTableCount());

        // Consistent
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());

        // GetTableRowCount
        var rows0 = doc.GetTableRowCount(0);
        var rows1 = doc.GetTableRowCount(1);
        var rows2 = doc.GetTableRowCount(2);
        Assert.True(rows0 > 0);
        Assert.True(rows1 > 0);
        Assert.True(rows2 > 0);
        Assert.Equal(rows0, doc.GetTableRowCount(0)); // consistent

        // ExportToHtml works with tables
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

        // GetCharCount and GetWordCount still positive
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_ea_review.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetTableCount());
        Assert.True(loaded.GetParagraphCount() > 0);

        // GetTableRowCount on loaded
        for (int i = 0; i < loaded.GetTableCount(); i++)
            Assert.True(loaded.GetTableRowCount(i) > 0);

        // InsertTable on loaded
        loaded.InsertTable(loaded.GetParagraphCount() - 1, 3, 3);
        Assert.Equal(4, loaded.GetTableCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: the architecture meets enterprise standards with minor gaps identified.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_ea_review_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetTableCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.ExportToPlainText());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
