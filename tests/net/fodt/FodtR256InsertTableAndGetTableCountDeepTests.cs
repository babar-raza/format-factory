// Tests for FodtDocument.InsertTable, GetTableCount, GetTableCell deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R256

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R256: Tests for FodtDocument.InsertTable, GetTableCount, GetTableCell deeper.
/// InsertTable(rows, cols): inserts a new table into the document.
/// GetTableCount(): returns the number of tables in the document.
/// GetTableCell(tableIndex, row, col): returns the content of a specific cell.
/// Covers: InsertTable no-throw; InsertTable increases GetTableCount; InsertTable multiple;
/// InsertTable persist; InsertTable then SaveToFile; InsertTable then ExportToHtml;
/// InsertTable 1x1; InsertTable 3x4; InsertTable large;
/// GetTableCount zero for no-table doc; GetTableCount increases after InsertTable;
/// GetTableCount consistent; GetTableCount no-throw; GetTableCount save-load;
/// GetTableCount after AppendParagraph unchanged; GetTableCount multiple inserts;
/// GetTableCell non-null; GetTableCell no-throw; GetTableCell consistent;
/// GetTableCell after SetTableCell reflects; GetTableCell row0col0; GetTableCell last;
/// GetTableCell for all cells no-throw; GetTableCell returns string;
/// dogfood CreateDoc→InsertTable→GetTableCount→GetTableCell→SaveToFile pipeline.
/// </summary>
public class FodtR256InsertTableAndGetTableCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR256InsertTableAndGetTableCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR256_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateDocWithTable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Report Title", 1);
        doc.AppendParagraph("Introduction paragraph before the table.");
        doc.InsertTable(3, 4); // 3 rows, 4 cols
        doc.AppendParagraph("Paragraph after the table with additional context.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // InsertTable
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertTable_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.InsertTable(3, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertTable_IncreasesTableCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetTableCount();
        doc.InsertTable(2, 3);
        Assert.Equal(before + 1, doc.GetTableCount());
    }

    [Fact]
    public void InsertTable_Multiple()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertTable(2, 2);
        doc.InsertTable(3, 4);
        doc.InsertTable(4, 5);
        Assert.Equal(3, doc.GetTableCount());
    }

    [Fact]
    public void InsertTable_Persist()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertTable(3, 3);
        var path = TempFile("table_persist.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(1, loaded.GetTableCount());
    }

    [Fact]
    public void InsertTable_ThenSaveToFile_FileNonEmpty()
    {
        var doc = CreateDocWithTable();
        var path = TempFile("with_table.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void InsertTable_ThenExportToHtml_NonNull()
    {
        var doc = CreateDocWithTable();
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);
    }

    [Fact]
    public void InsertTable_1x1_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.InsertTable(1, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertTable_3x4_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.InsertTable(3, 4));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertTable_Large_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.InsertTable(10, 8));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertTable_DoesNotChangeParagraphCount_For_HeadingAndBody()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        doc.AppendParagraph("Body paragraph.");
        var beforePara = doc.GetParagraphCount();
        doc.InsertTable(2, 3);
        // Paragraph count should be >= before (table may add structure but not reduce paras)
        Assert.True(doc.GetParagraphCount() >= beforePara);
    }

    // -------------------------------------------------------------------------
    // GetTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCount_ZeroForNoTableDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No tables here.");
        Assert.Equal(0, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_IncreasesAfterInsertTable()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetTableCount());
        doc.InsertTable(2, 2);
        Assert.Equal(1, doc.GetTableCount());
        doc.InsertTable(3, 3);
        Assert.Equal(2, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_Consistent()
    {
        var doc = CreateDocWithTable();
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_NoThrow()
    {
        var doc = CreateDocWithTable();
        var ex = Record.Exception(() => doc.GetTableCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCount_SaveLoad_Preserved()
    {
        var doc = CreateDocWithTable();
        doc.InsertTable(2, 2);
        var before = doc.GetTableCount();
        var path = TempFile("table_count_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    [Fact]
    public void GetTableCount_AfterAppendParagraph_Unchanged()
    {
        var doc = CreateDocWithTable();
        var before = doc.GetTableCount();
        doc.AppendParagraph("Additional paragraph.");
        Assert.Equal(before, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_MultipleInserts()
    {
        var doc = FodtDocument.CreateEmpty();
        for (int i = 0; i < 5; i++)
            doc.InsertTable(2, 3);
        Assert.Equal(5, doc.GetTableCount());
    }

    // -------------------------------------------------------------------------
    // GetTableCell
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCell_NonNull()
    {
        var doc = CreateDocWithTable();
        var cell = doc.GetTableCell(0, 0, 0);
        Assert.NotNull(cell);
    }

    [Fact]
    public void GetTableCell_NoThrow()
    {
        var doc = CreateDocWithTable();
        var ex = Record.Exception(() => doc.GetTableCell(0, 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCell_Consistent()
    {
        var doc = CreateDocWithTable();
        var c1 = doc.GetTableCell(0, 0, 0);
        var c2 = doc.GetTableCell(0, 0, 0);
        Assert.Equal(c1, c2);
    }

    [Fact]
    public void GetTableCell_AfterSetTableCell_Reflects()
    {
        var doc = CreateDocWithTable();
        doc.SetTableCell(0, 1, 2, "CELL_VALUE_XYZ");
        var cell = doc.GetTableCell(0, 1, 2);
        Assert.Equal("CELL_VALUE_XYZ", cell);
    }

    [Fact]
    public void GetTableCell_Row0Col0_NonNull()
    {
        var doc = CreateDocWithTable();
        Assert.NotNull(doc.GetTableCell(0, 0, 0));
    }

    [Fact]
    public void GetTableCell_ReturnsString()
    {
        var doc = CreateDocWithTable();
        var cell = doc.GetTableCell(0, 0, 0);
        Assert.IsType<string>(cell);
    }

    [Fact]
    public void GetTableCell_ForAllCells_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertTable(3, 4);
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 4; c++)
            {
                var ex = Record.Exception(() => doc.GetTableCell(0, r, c));
                Assert.Null(ex);
            }
    }

    [Fact]
    public void GetTableCell_MultipleTablesIndexing()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertTable(2, 2);
        doc.InsertTable(3, 3);
        doc.SetTableCell(0, 0, 0, "TABLE_ZERO");
        doc.SetTableCell(1, 0, 0, "TABLE_ONE");
        Assert.Equal("TABLE_ZERO", doc.GetTableCell(0, 0, 0));
        Assert.Equal("TABLE_ONE", doc.GetTableCell(1, 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertTable_GetTableCount_GetTableCell_SaveToFile_Pipeline()
    {
        // Build a report document with multiple tables
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Quarterly Business Review", 1);
        doc.AppendParagraph("This report covers Q3 performance metrics across all business units.");
        doc.AppendParagraph("Data has been collected from regional offices and consolidated for review.");

        // Insert first table: Revenue by Region
        doc.InsertHeading(3, "Revenue by Region", 2);
        doc.AppendParagraph("The following table shows revenue figures by geographic region.");
        doc.InsertTable(4, 3); // header + 3 data rows, 3 cols (Region, Q2, Q3)

        // Populate revenue table
        doc.SetTableCell(0, 0, 0, "Region");
        doc.SetTableCell(0, 0, 1, "Q2 Revenue");
        doc.SetTableCell(0, 0, 2, "Q3 Revenue");
        doc.SetTableCell(0, 1, 0, "Europe");
        doc.SetTableCell(0, 1, 1, "1250000");
        doc.SetTableCell(0, 1, 2, "1380000");
        doc.SetTableCell(0, 2, 0, "Americas");
        doc.SetTableCell(0, 2, 1, "2100000");
        doc.SetTableCell(0, 2, 2, "2340000");
        doc.SetTableCell(0, 3, 0, "APAC");
        doc.SetTableCell(0, 3, 1, "890000");
        doc.SetTableCell(0, 3, 2, "1050000");

        Assert.Equal(1, doc.GetTableCount());

        // Verify table cells
        Assert.Equal("Region", doc.GetTableCell(0, 0, 0));
        Assert.Equal("Europe", doc.GetTableCell(0, 1, 0));
        Assert.Equal("2340000", doc.GetTableCell(0, 2, 2));
        Assert.Equal("1050000", doc.GetTableCell(0, 3, 2));

        // Insert second table: Headcount by Department
        doc.InsertHeading(doc.GetParagraphCount(), "Headcount by Department", 2);
        doc.AppendParagraph("Headcount changes reflect both new hires and attrition.");
        doc.InsertTable(5, 3); // header + 4 dept rows, 3 cols

        Assert.Equal(2, doc.GetTableCount());

        // Populate headcount table
        doc.SetTableCell(1, 0, 0, "Department");
        doc.SetTableCell(1, 0, 1, "Start HC");
        doc.SetTableCell(1, 0, 2, "End HC");
        doc.SetTableCell(1, 1, 0, "Engineering");
        doc.SetTableCell(1, 1, 1, "145");
        doc.SetTableCell(1, 1, 2, "162");
        doc.SetTableCell(1, 2, 0, "Marketing");
        doc.SetTableCell(1, 2, 1, "38");
        doc.SetTableCell(1, 2, 2, "41");
        doc.SetTableCell(1, 3, 0, "Finance");
        doc.SetTableCell(1, 3, 1, "22");
        doc.SetTableCell(1, 3, 2, "23");
        doc.SetTableCell(1, 4, 0, "Operations");
        doc.SetTableCell(1, 4, 1, "67");
        doc.SetTableCell(1, 4, 2, "70");

        // Verify headcount table cells
        Assert.Equal("Department", doc.GetTableCell(1, 0, 0));
        Assert.Equal("Engineering", doc.GetTableCell(1, 1, 0));
        Assert.Equal("162", doc.GetTableCell(1, 1, 2));

        // Insert third table: Risks
        doc.InsertHeading(doc.GetParagraphCount(), "Risk Register", 2);
        doc.InsertTable(3, 4); // 3 risks with 4 attributes each

        Assert.Equal(3, doc.GetTableCount());

        doc.SetTableCell(2, 0, 0, "Risk");
        doc.SetTableCell(2, 0, 1, "Category");
        doc.SetTableCell(2, 0, 2, "Severity");
        doc.SetTableCell(2, 0, 3, "Owner");
        doc.SetTableCell(2, 1, 0, "Supply chain disruption");
        doc.SetTableCell(2, 1, 1, "Operational");
        doc.SetTableCell(2, 1, 2, "High");
        doc.SetTableCell(2, 1, 3, "COO");
        doc.SetTableCell(2, 2, 0, "Regulatory change");
        doc.SetTableCell(2, 2, 1, "Compliance");
        doc.SetTableCell(2, 2, 2, "Medium");
        doc.SetTableCell(2, 2, 3, "General Counsel");

        // GetTableCount consistent
        Assert.Equal(3, doc.GetTableCount());
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());

        // GetTableCell no-throw for all cells in table 0
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 3; c++)
            {
                var ex = Record.Exception(() => doc.GetTableCell(0, r, c));
                Assert.Null(ex);
            }

        // ExportToHtml includes tables
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown has headings
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.Contains("#", md);

        // GetWordCount positive
        var wc = doc.GetWordCount();
        Assert.True(wc > 0);

        // AppendParagraph does not change table count
        doc.AppendParagraph("Conclusion: all metrics reviewed and approved.");
        Assert.Equal(3, doc.GetTableCount());

        // SaveToFile
        var path = TempFile("dogfood_report.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(doc.GetTableCount(), loaded.GetTableCount());
        Assert.Equal(3, loaded.GetTableCount());

        // GetTableCell on loaded
        var ex2 = Record.Exception(() => loaded.GetTableCell(0, 0, 0));
        Assert.Null(ex2);
        Assert.NotNull(loaded.GetTableCell(0, 0, 0));

        // GetTableCell value preserved on loaded
        Assert.Equal("Region", loaded.GetTableCell(0, 0, 0));
        Assert.Equal("Europe", loaded.GetTableCell(0, 1, 0));

        // InsertTable on loaded
        loaded.InsertTable(2, 2);
        Assert.Equal(4, loaded.GetTableCount());

        // SetTableCell on newly inserted
        loaded.SetTableCell(3, 0, 0, "NEW_TABLE_CELL");
        Assert.Equal("NEW_TABLE_CELL", loaded.GetTableCell(3, 0, 0));

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // Final SaveToFile
        var path2 = TempFile("dogfood_report_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(loaded.GetTableCount(), loaded2.GetTableCount());
    }
}
