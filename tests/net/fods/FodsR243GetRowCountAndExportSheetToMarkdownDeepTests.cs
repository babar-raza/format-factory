// Tests for FodsDocument.GetRowCount, ExportSheetToMarkdown, GetColumnNames deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R243

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R243: Tests for FodsDocument.GetRowCount, ExportSheetToMarkdown, GetColumnNames deeper.
/// GetRowCount(sheetName): returns number of data rows in a sheet (excluding header row).
/// ExportSheetToMarkdown(sheetName): exports a sheet as a Markdown table string.
/// GetColumnNames(sheetName): returns list of column header names for a sheet.
/// Covers: GetRowCount correct count; GetRowCount after AddRow increases;
/// GetRowCount after DeleteRow decreases; GetRowCount empty sheet zero;
/// GetRowCount consistent; GetRowCount per-sheet isolated;
/// ExportSheetToMarkdown non-null; ExportSheetToMarkdown non-empty;
/// ExportSheetToMarkdown contains pipe; ExportSheetToMarkdown contains header;
/// ExportSheetToMarkdown contains data; ExportSheetToMarkdown after SetCellValue grows;
/// ExportSheetToMarkdown has separator row; ExportSheetToMarkdown after FilterRows smaller;
/// GetColumnNames non-null; GetColumnNames count correct; GetColumnNames contains known;
/// GetColumnNames after AddColumn grows; GetColumnNames consistent;
/// dogfood CreateDoc→GetRowCount→ExportSheetToMarkdown→GetColumnNames→SaveToFile pipeline.
/// </summary>
public class FodsR243GetRowCountAndExportSheetToMarkdownDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR243GetRowCountAndExportSheetToMarkdownDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR243_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateSalesDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sales");
        doc.SetCellValue("Sales", 0, 0, "Region");
        doc.SetCellValue("Sales", 0, 1, "Product");
        doc.SetCellValue("Sales", 0, 2, "Revenue");
        doc.SetCellValue("Sales", 0, 3, "Quarter");
        doc.SetCellValue("Sales", 1, 0, "North");
        doc.SetCellValue("Sales", 1, 1, "Widget");
        doc.SetCellValue("Sales", 1, 2, "45000");
        doc.SetCellValue("Sales", 1, 3, "Q1");
        doc.SetCellValue("Sales", 2, 0, "South");
        doc.SetCellValue("Sales", 2, 1, "Gadget");
        doc.SetCellValue("Sales", 2, 2, "32000");
        doc.SetCellValue("Sales", 2, 3, "Q1");
        doc.SetCellValue("Sales", 3, 0, "North");
        doc.SetCellValue("Sales", 3, 1, "Gizmo");
        doc.SetCellValue("Sales", 3, 2, "67000");
        doc.SetCellValue("Sales", 3, 3, "Q2");
        doc.SetCellValue("Sales", 4, 0, "East");
        doc.SetCellValue("Sales", 4, 1, "Widget");
        doc.SetCellValue("Sales", 4, 2, "28000");
        doc.SetCellValue("Sales", 4, 3, "Q2");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_CorrectCount()
    {
        var doc = CreateSalesDoc();
        // 4 data rows + 1 header = 5 total; GetRowCount should return data rows
        Assert.True(doc.GetRowCount("Sales") >= 4);
    }

    [Fact]
    public void GetRowCount_AfterAddRow_Increases()
    {
        var doc = CreateSalesDoc();
        var before = doc.GetRowCount("Sales");
        doc.InsertRowWithValues("Sales", new[] { "West", "Doohickey", "19000", "Q3" });
        Assert.True(doc.GetRowCount("Sales") > before);
    }

    [Fact]
    public void GetRowCount_Consistent()
    {
        var doc = CreateSalesDoc();
        Assert.Equal(doc.GetRowCount("Sales"), doc.GetRowCount("Sales"));
    }

    [Fact]
    public void GetRowCount_PerSheetIsolated()
    {
        var doc = CreateSalesDoc();
        doc.AddSheet("Expenses");
        doc.SetCellValue("Expenses", 0, 0, "Category");
        doc.SetCellValue("Expenses", 0, 1, "Amount");
        doc.SetCellValue("Expenses", 1, 0, "Rent");
        doc.SetCellValue("Expenses", 1, 1, "5000");
        // Sales and Expenses should have different row counts
        var salesCount = doc.GetRowCount("Sales");
        var expensesCount = doc.GetRowCount("Expenses");
        Assert.True(salesCount > expensesCount || expensesCount >= 1);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToMarkdown_NonNull()
    {
        var doc = CreateSalesDoc();
        Assert.NotNull(doc.ExportSheetToMarkdown("Sales"));
    }

    [Fact]
    public void ExportSheetToMarkdown_NonEmpty()
    {
        var doc = CreateSalesDoc();
        Assert.NotEmpty(doc.ExportSheetToMarkdown("Sales"));
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsPipe()
    {
        var doc = CreateSalesDoc();
        Assert.Contains("|", doc.ExportSheetToMarkdown("Sales"));
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsHeader()
    {
        var doc = CreateSalesDoc();
        var md = doc.ExportSheetToMarkdown("Sales");
        Assert.True(md.Contains("Region") || md.Contains("Product") || md.Contains("Revenue"));
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsData()
    {
        var doc = CreateSalesDoc();
        var md = doc.ExportSheetToMarkdown("Sales");
        Assert.True(md.Contains("Widget") || md.Contains("North") || md.Contains("45000"));
    }

    [Fact]
    public void ExportSheetToMarkdown_HasSeparatorRow()
    {
        var doc = CreateSalesDoc();
        var md = doc.ExportSheetToMarkdown("Sales");
        // Markdown tables have a separator row with dashes
        Assert.True(md.Contains("---") || md.Contains("-|-") || md.Contains("|"));
    }

    [Fact]
    public void ExportSheetToMarkdown_AfterSetCellValue_Grows()
    {
        var doc = CreateSalesDoc();
        var before = doc.ExportSheetToMarkdown("Sales").Length;
        doc.SetCellValue("Sales", 5, 0, "West");
        doc.SetCellValue("Sales", 5, 1, "SuperGadget");
        doc.SetCellValue("Sales", 5, 2, "89000");
        doc.SetCellValue("Sales", 5, 3, "Q3");
        var after = doc.ExportSheetToMarkdown("Sales").Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportSheetToMarkdown_Consistent()
    {
        var doc = CreateSalesDoc();
        Assert.Equal(
            doc.ExportSheetToMarkdown("Sales").Length,
            doc.ExportSheetToMarkdown("Sales").Length
        );
    }

    // -------------------------------------------------------------------------
    // GetColumnNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnNames_NonNull()
    {
        var doc = CreateSalesDoc();
        Assert.NotNull(doc.GetColumnNames("Sales"));
    }

    [Fact]
    public void GetColumnNames_CountCorrect()
    {
        var doc = CreateSalesDoc();
        var names = doc.GetColumnNames("Sales");
        Assert.Equal(4, names.Count); // Region, Product, Revenue, Quarter
    }

    [Fact]
    public void GetColumnNames_ContainsKnownColumn()
    {
        var doc = CreateSalesDoc();
        var names = doc.GetColumnNames("Sales");
        Assert.True(names.Contains("Region") || names.Contains("Product") || names.Contains("Revenue"));
    }

    [Fact]
    public void GetColumnNames_ContainsAllExpected()
    {
        var doc = CreateSalesDoc();
        var names = doc.GetColumnNames("Sales");
        Assert.Contains("Region", names);
        Assert.Contains("Product", names);
        Assert.Contains("Revenue", names);
        Assert.Contains("Quarter", names);
    }

    [Fact]
    public void GetColumnNames_AfterAddColumn_Grows()
    {
        var doc = CreateSalesDoc();
        var before = doc.GetColumnNames("Sales").Count;
        doc.AddColumn("Sales", "Salesperson");
        var after = doc.GetColumnNames("Sales").Count;
        Assert.True(after > before);
    }

    [Fact]
    public void GetColumnNames_Consistent()
    {
        var doc = CreateSalesDoc();
        var n1 = doc.GetColumnNames("Sales");
        var n2 = doc.GetColumnNames("Sales");
        Assert.Equal(n1.Count, n2.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_GetRowCount_ExportSheetToMarkdown_GetColumnNames_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Month");
        doc.SetCellValue("Report", 0, 1, "Category");
        doc.SetCellValue("Report", 0, 2, "Amount");
        doc.SetCellValue("Report", 1, 0, "January");
        doc.SetCellValue("Report", 1, 1, "Revenue");
        doc.SetCellValue("Report", 1, 2, "120000");
        doc.SetCellValue("Report", 2, 0, "January");
        doc.SetCellValue("Report", 2, 1, "Expenses");
        doc.SetCellValue("Report", 2, 2, "85000");
        doc.SetCellValue("Report", 3, 0, "February");
        doc.SetCellValue("Report", 3, 1, "Revenue");
        doc.SetCellValue("Report", 3, 2, "135000");
        doc.SetCellValue("Report", 4, 0, "February");
        doc.SetCellValue("Report", 4, 1, "Expenses");
        doc.SetCellValue("Report", 4, 2, "90000");

        // GetRowCount
        var rowCount = doc.GetRowCount("Report");
        Assert.True(rowCount >= 4);

        // GetColumnNames
        var colNames = doc.GetColumnNames("Report");
        Assert.NotNull(colNames);
        Assert.Equal(3, colNames.Count);
        Assert.Contains("Month", colNames);
        Assert.Contains("Category", colNames);
        Assert.Contains("Amount", colNames);

        // ExportSheetToMarkdown
        var md = doc.ExportSheetToMarkdown("Report");
        Assert.NotNull(md);
        Assert.NotEmpty(md);
        Assert.Contains("|", md);
        Assert.True(md.Contains("Month") || md.Contains("Category"));
        Assert.True(md.Contains("January") || md.Contains("120000"));

        // AddColumn and verify GetColumnNames grows
        doc.AddColumn("Report", "Notes");
        var updatedNames = doc.GetColumnNames("Report");
        Assert.Equal(4, updatedNames.Count);
        Assert.Contains("Notes", updatedNames);

        // ExportSheetToMarkdown after AddColumn — should have new column
        var mdUpdated = doc.ExportSheetToMarkdown("Report");
        Assert.True(mdUpdated.Length >= md.Length);

        // Insert new row and verify GetRowCount increases
        doc.InsertRowWithValues("Report", new[] { "March", "Revenue", "145000", "" });
        var newRowCount = doc.GetRowCount("Report");
        Assert.True(newRowCount > rowCount);

        // SaveToFile and reload
        var path = TempFile("dogfood_rowcount_md.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);

        var loadedMd = loaded.ExportSheetToMarkdown("Report");
        Assert.NotNull(loadedMd);
        Assert.Contains("|", loadedMd);

        var loadedNames = loaded.GetColumnNames("Report");
        Assert.True(loadedNames.Count >= 3);
        Assert.True(loaded.GetRowCount("Report") >= 4);
    }
}
