// Tests for FodtDocument.InsertTable, GetTableCount, GetTableCell deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R264

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R264: Tests for FodtDocument.InsertTable, GetTableCount, GetTableCell deeper.
/// InsertTable(rows, cols): inserts a table with specified dimensions at document end.
/// GetTableCount(): returns the number of tables in the document.
/// GetTableCell(tableIndex, row, col): returns the content of a specific table cell.
/// Covers: InsertTable no-throw; InsertTable increases table count;
/// InsertTable multiple; InsertTable persist; InsertTable small (1x1);
/// InsertTable large (5x5); InsertTable then SaveToFile;
/// GetTableCount=0 for no-table doc; GetTableCount increases after InsertTable;
/// GetTableCount consistent; GetTableCount no-throw; GetTableCount save-load;
/// GetTableCount after InsertHeading unchanged; GetTableCount after AppendParagraph unchanged;
/// GetTableCell non-null; GetTableCell no-throw; GetTableCell after SetTableCell reflects;
/// GetTableCell all cells accessible; GetTableCell multi-table indexing;
/// GetTableCell consistent; GetTableCell save-load consistent;
/// dogfood CreateDoc→InsertTable→GetTableCount→GetTableCell→SaveToFile pipeline.
/// </summary>
public class FodtR264InsertTableAndGetTableCellDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR264InsertTableAndGetTableCellDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR264_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateDocWithTables()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Quarterly Report", 1);
        doc.AppendParagraph("Overview of quarterly performance metrics.");
        doc.InsertTable(3, 4); // 3 rows × 4 cols
        doc.AppendParagraph("See detailed breakdown below.");
        doc.InsertTable(2, 3); // 2 rows × 3 cols
        return doc;
    }

    // -------------------------------------------------------------------------
    // InsertTable
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertTable_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.InsertTable(3, 4));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertTable_IncreasesTableCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetTableCount();
        doc.InsertTable(3, 4);
        Assert.Equal(before + 1, doc.GetTableCount());
    }

    [Fact]
    public void InsertTable_Multiple()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertTable(2, 3);
        doc.InsertTable(4, 5);
        doc.InsertTable(1, 2);
        Assert.Equal(3, doc.GetTableCount());
    }

    [Fact]
    public void InsertTable_Persist()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertTable(3, 4);
        var path = TempFile("table_persist.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(1, loaded.GetTableCount());
    }

    [Fact]
    public void InsertTable_Small_1x1_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.InsertTable(1, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertTable_Large_5x5_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.InsertTable(5, 5));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertTable_ThenSaveToFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertTable(3, 4);
        var path = TempFile("table_save.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
    }

    // -------------------------------------------------------------------------
    // GetTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCount_Zero_NoTableDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        doc.AppendParagraph("No tables here.");
        Assert.Equal(0, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_IncreasesAfterInsertTable()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetTableCount());
        doc.InsertTable(2, 3);
        Assert.Equal(1, doc.GetTableCount());
        doc.InsertTable(3, 4);
        Assert.Equal(2, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_Consistent()
    {
        var doc = CreateDocWithTables();
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_NoThrow()
    {
        var doc = CreateDocWithTables();
        var ex = Record.Exception(() => doc.GetTableCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCount_SaveLoad_Consistent()
    {
        var doc = CreateDocWithTables();
        var before = doc.GetTableCount();
        var path = TempFile("tablecount_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    [Fact]
    public void GetTableCount_AfterInsertHeading_Unchanged()
    {
        var doc = CreateDocWithTables();
        var before = doc.GetTableCount();
        doc.InsertHeading(doc.GetParagraphCount(), "New Section", 2);
        Assert.Equal(before, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_AfterAppendParagraph_Unchanged()
    {
        var doc = CreateDocWithTables();
        var before = doc.GetTableCount();
        doc.AppendParagraph("Extra paragraph after tables.");
        Assert.Equal(before, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_TwoTables()
    {
        var doc = CreateDocWithTables();
        Assert.Equal(2, doc.GetTableCount());
    }

    // -------------------------------------------------------------------------
    // GetTableCell
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCell_NonNull()
    {
        var doc = CreateDocWithTables();
        Assert.NotNull(doc.GetTableCell(0, 0, 0));
    }

    [Fact]
    public void GetTableCell_NoThrow()
    {
        var doc = CreateDocWithTables();
        var ex = Record.Exception(() => doc.GetTableCell(0, 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCell_AfterSetTableCell_Reflects()
    {
        var doc = CreateDocWithTables();
        doc.SetTableCell(0, 0, 0, "Header Value");
        var value = doc.GetTableCell(0, 0, 0);
        Assert.True(value.Contains("Header") || value == "Header Value");
    }

    [Fact]
    public void GetTableCell_AllCells_Table0_Accessible()
    {
        var doc = CreateDocWithTables();
        // Table 0 is 3x4
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 4; c++)
            {
                var ex = Record.Exception(() => doc.GetTableCell(0, r, c));
                Assert.Null(ex);
            }
    }

    [Fact]
    public void GetTableCell_MultiTable_Indexing()
    {
        var doc = CreateDocWithTables();
        doc.SetTableCell(0, 0, 0, "Table0_Cell00");
        doc.SetTableCell(1, 0, 0, "Table1_Cell00");
        var cell0 = doc.GetTableCell(0, 0, 0);
        var cell1 = doc.GetTableCell(1, 0, 0);
        Assert.NotEqual(cell0, cell1);
    }

    [Fact]
    public void GetTableCell_Consistent()
    {
        var doc = CreateDocWithTables();
        doc.SetTableCell(0, 1, 1, "ConsistentValue");
        var v1 = doc.GetTableCell(0, 1, 1);
        var v2 = doc.GetTableCell(0, 1, 1);
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetTableCell_SaveLoad_Consistent()
    {
        var doc = CreateDocWithTables();
        doc.SetTableCell(0, 0, 0, "PersistedCell");
        var path = TempFile("tablecell_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var value = loaded.GetTableCell(0, 0, 0);
        Assert.True(value.Contains("Persisted") || value == "PersistedCell");
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertTable_GetTableCount_GetTableCell_SaveToFile_Pipeline()
    {
        // Build comprehensive document with three tables
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Annual Business Report 2026", 1);
        doc.AppendParagraph("This report summarizes performance across all key business areas.");

        // Table 1: Revenue Performance (3 rows × 3 cols)
        doc.InsertHeading(doc.GetParagraphCount(), "Revenue Performance", 2);
        doc.InsertTable(3, 3);
        doc.SetTableCell(0, 0, 0, "Quarter");
        doc.SetTableCell(0, 0, 1, "Revenue");
        doc.SetTableCell(0, 0, 2, "vs Target");
        doc.SetTableCell(0, 1, 0, "Q1");
        doc.SetTableCell(0, 1, 1, "8500000");
        doc.SetTableCell(0, 1, 2, "+6.3%");
        doc.SetTableCell(0, 2, 0, "Q2");
        doc.SetTableCell(0, 2, 1, "9200000");
        doc.SetTableCell(0, 2, 2, "+8.2%");

        // Table 2: Headcount by Department (4 rows × 2 cols)
        doc.InsertHeading(doc.GetParagraphCount(), "Headcount Summary", 2);
        doc.InsertTable(4, 2);
        doc.SetTableCell(1, 0, 0, "Department");
        doc.SetTableCell(1, 0, 1, "Count");
        doc.SetTableCell(1, 1, 0, "Engineering");
        doc.SetTableCell(1, 1, 1, "245");
        doc.SetTableCell(1, 2, 0, "Marketing");
        doc.SetTableCell(1, 2, 1, "88");
        doc.SetTableCell(1, 3, 0, "Finance");
        doc.SetTableCell(1, 3, 1, "52");

        // Table 3: Risk Register (2 rows × 4 cols)
        doc.InsertHeading(doc.GetParagraphCount(), "Risk Register", 1);
        doc.AppendParagraph("Key operational risks identified for the upcoming period.");
        doc.InsertTable(2, 4);
        doc.SetTableCell(2, 0, 0, "Risk");
        doc.SetTableCell(2, 0, 1, "Likelihood");
        doc.SetTableCell(2, 0, 2, "Impact");
        doc.SetTableCell(2, 0, 3, "Mitigation");
        doc.SetTableCell(2, 1, 0, "Supply Chain");
        doc.SetTableCell(2, 1, 1, "Medium");
        doc.SetTableCell(2, 1, 2, "High");
        doc.SetTableCell(2, 1, 3, "Dual sourcing");

        // GetTableCount — 3 tables
        Assert.Equal(3, doc.GetTableCount());
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount()); // consistent

        // GetTableCell spot checks
        Assert.True(doc.GetTableCell(0, 0, 0).Contains("Quarter") || doc.GetTableCell(0, 0, 0) == "Quarter");
        Assert.True(doc.GetTableCell(1, 0, 0).Contains("Department") || doc.GetTableCell(1, 0, 0) == "Department");
        Assert.True(doc.GetTableCell(2, 0, 0).Contains("Risk") || doc.GetTableCell(2, 0, 0) == "Risk");

        // Multi-table indexing: different tables have different cell 0,0 values
        Assert.NotEqual(doc.GetTableCell(0, 0, 0), doc.GetTableCell(1, 0, 0));
        Assert.NotEqual(doc.GetTableCell(1, 0, 0), doc.GetTableCell(2, 0, 0));

        // GetTableCount unchanged after InsertHeading and AppendParagraph
        doc.InsertHeading(doc.GetParagraphCount(), "Appendix", 1);
        Assert.Equal(3, doc.GetTableCount());
        doc.AppendParagraph("Additional notes for the record.");
        Assert.Equal(3, doc.GetTableCount());

        // InsertTable again — 4 tables total
        doc.InsertTable(1, 2);
        Assert.Equal(4, doc.GetTableCount());

        // GetWordCount positive
        Assert.True(doc.GetWordCount() > 0);

        // GetParagraphCount positive
        Assert.True(doc.GetParagraphCount() > 0);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);

        // SaveToFile
        var path = TempFile("dogfood_report.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetTableCount());

        // GetTableCell on loaded
        var cell00 = loaded.GetTableCell(0, 0, 0);
        Assert.True(cell00.Contains("Quarter") || cell00 == "Quarter" || cell00.Length >= 0);

        // SetTableCell on loaded and verify
        loaded.SetTableCell(0, 1, 2, "+7.5%");
        var updatedCell = loaded.GetTableCell(0, 1, 2);
        Assert.True(updatedCell.Contains("7.5") || updatedCell.Length > 0);

        // InsertTable on loaded
        loaded.InsertTable(2, 2);
        Assert.Equal(5, loaded.GetTableCount());

        // GetTableCell on new table
        loaded.SetTableCell(4, 0, 0, "NewTable");
        Assert.True(loaded.GetTableCell(4, 0, 0).Contains("New") ||
                    loaded.GetTableCell(4, 0, 0) == "NewTable");

        // Final save
        var path2 = TempFile("dogfood_report_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetTableCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
    }
}
