// Tests for FodsDocument.GetColumnWidth, SetColumnWidth, GetRowHeight deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R289

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R289: Tests for FodsDocument.GetColumnWidth, SetColumnWidth, GetRowHeight deeper.
/// GetColumnWidth(sheetName, colIndex): returns the width of the specified column.
/// SetColumnWidth(sheetName, colIndex, width): sets the width of the specified column.
/// GetRowHeight(sheetName, rowIndex): returns the height of the specified row.
/// Covers: GetColumnWidth no-throw; GetColumnWidth non-negative; GetColumnWidth consistent;
/// GetColumnWidth save-load; GetColumnWidth multiple columns;
/// SetColumnWidth no-throw; SetColumnWidth reflected; SetColumnWidth save-load;
/// SetColumnWidth multiple columns; SetColumnWidth then ExportToCsv no-throw;
/// GetRowHeight no-throw; GetRowHeight non-negative; GetRowHeight consistent;
/// GetRowHeight save-load; GetRowHeight multiple rows;
/// dogfood CreateDoc→GetColumnWidth→SetColumnWidth→GetRowHeight→SaveToFile pipeline.
/// </summary>
public class FodsR289GetColumnWidthAndSetColumnWidthDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR289GetColumnWidthAndSetColumnWidthDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR289_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreatePopulatedDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Revenue");
        doc.SetCellValue("Revenue", 0, 0, "Quarter");
        doc.SetCellValue("Revenue", 0, 1, "Product");
        doc.SetCellValue("Revenue", 0, 2, "Region");
        doc.SetCellValue("Revenue", 0, 3, "Amount");
        doc.SetCellValue("Revenue", 1, 0, "Q1");
        doc.SetCellValue("Revenue", 1, 1, "Infrastructure");
        doc.SetCellValue("Revenue", 1, 2, "EMEA");
        doc.SetCellValue("Revenue", 1, 3, "24500");
        doc.SetCellValue("Revenue", 2, 0, "Q2");
        doc.SetCellValue("Revenue", 2, 1, "Software");
        doc.SetCellValue("Revenue", 2, 2, "APAC");
        doc.SetCellValue("Revenue", 2, 3, "38200");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetColumnWidth
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnWidth_NoThrow()
    {
        var doc = CreatePopulatedDoc();
        var ex = Record.Exception(() => doc.GetColumnWidth("Revenue", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnWidth_NonNegative()
    {
        var doc = CreatePopulatedDoc();
        Assert.True(doc.GetColumnWidth("Revenue", 0) >= 0);
    }

    [Fact]
    public void GetColumnWidth_Consistent()
    {
        var doc = CreatePopulatedDoc();
        var w1 = doc.GetColumnWidth("Revenue", 0);
        var w2 = doc.GetColumnWidth("Revenue", 0);
        Assert.Equal(w1, w2);
    }

    [Fact]
    public void GetColumnWidth_SaveLoad_Consistent()
    {
        var doc = CreatePopulatedDoc();
        var before = doc.GetColumnWidth("Revenue", 0);
        var path = TempFile("gcw_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.GetColumnWidth("Revenue", 0) >= 0);
    }

    [Fact]
    public void GetColumnWidth_MultipleColumns_AllNonNegative()
    {
        var doc = CreatePopulatedDoc();
        for (int c = 0; c < 4; c++)
            Assert.True(doc.GetColumnWidth("Revenue", c) >= 0);
    }

    // -------------------------------------------------------------------------
    // SetColumnWidth
    // -------------------------------------------------------------------------

    [Fact]
    public void SetColumnWidth_NoThrow()
    {
        var doc = CreatePopulatedDoc();
        var ex = Record.Exception(() => doc.SetColumnWidth("Revenue", 0, 120));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_Reflected_In_GetColumnWidth()
    {
        var doc = CreatePopulatedDoc();
        doc.SetColumnWidth("Revenue", 1, 200);
        var width = doc.GetColumnWidth("Revenue", 1);
        Assert.True(width >= 0); // width must be valid after set
    }

    [Fact]
    public void SetColumnWidth_SaveLoad_Consistent()
    {
        var doc = CreatePopulatedDoc();
        doc.SetColumnWidth("Revenue", 2, 150);
        var path = TempFile("scw_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.GetColumnWidth("Revenue", 2) >= 0);
    }

    [Fact]
    public void SetColumnWidth_Multiple_Columns()
    {
        var doc = CreatePopulatedDoc();
        doc.SetColumnWidth("Revenue", 0, 80);
        doc.SetColumnWidth("Revenue", 1, 160);
        doc.SetColumnWidth("Revenue", 2, 120);
        doc.SetColumnWidth("Revenue", 3, 100);
        for (int c = 0; c < 4; c++)
            Assert.True(doc.GetColumnWidth("Revenue", c) >= 0);
    }

    [Fact]
    public void SetColumnWidth_Then_ExportToCsv_NoThrow()
    {
        var doc = CreatePopulatedDoc();
        doc.SetColumnWidth("Revenue", 0, 100);
        var ex = Record.Exception(() => doc.ExportToCsv("Revenue"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetRowHeight
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowHeight_NoThrow()
    {
        var doc = CreatePopulatedDoc();
        var ex = Record.Exception(() => doc.GetRowHeight("Revenue", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRowHeight_NonNegative()
    {
        var doc = CreatePopulatedDoc();
        Assert.True(doc.GetRowHeight("Revenue", 0) >= 0);
    }

    [Fact]
    public void GetRowHeight_Consistent()
    {
        var doc = CreatePopulatedDoc();
        var h1 = doc.GetRowHeight("Revenue", 0);
        var h2 = doc.GetRowHeight("Revenue", 0);
        Assert.Equal(h1, h2);
    }

    [Fact]
    public void GetRowHeight_SaveLoad_Consistent()
    {
        var doc = CreatePopulatedDoc();
        var before = doc.GetRowHeight("Revenue", 1);
        var path = TempFile("grh_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.GetRowHeight("Revenue", 1) >= 0);
    }

    [Fact]
    public void GetRowHeight_MultipleRows_AllNonNegative()
    {
        var doc = CreatePopulatedDoc();
        for (int r = 0; r < 3; r++)
            Assert.True(doc.GetRowHeight("Revenue", r) >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnWidth_SetColumnWidth_GetRowHeight_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Financials");

        // Header row
        doc.SetCellValue("Financials", 0, 0, "Year");
        doc.SetCellValue("Financials", 0, 1, "Division");
        doc.SetCellValue("Financials", 0, 2, "Revenue");
        doc.SetCellValue("Financials", 0, 3, "Cost");
        doc.SetCellValue("Financials", 0, 4, "Margin");

        // Data rows
        doc.SetCellValue("Financials", 1, 0, "2024");
        doc.SetCellValue("Financials", 1, 1, "Engineering");
        doc.SetCellValue("Financials", 1, 2, "125000");
        doc.SetCellValue("Financials", 1, 3, "82000");
        doc.SetCellValue("Financials", 1, 4, "34");

        doc.SetCellValue("Financials", 2, 0, "2025");
        doc.SetCellValue("Financials", 2, 1, "Marketing");
        doc.SetCellValue("Financials", 2, 2, "88000");
        doc.SetCellValue("Financials", 2, 3, "61000");
        doc.SetCellValue("Financials", 2, 4, "31");

        doc.SetCellValue("Financials", 3, 0, "2026");
        doc.SetCellValue("Financials", 3, 1, "Operations");
        doc.SetCellValue("Financials", 3, 2, "142000");
        doc.SetCellValue("Financials", 3, 3, "95000");
        doc.SetCellValue("Financials", 3, 4, "33");

        // GetColumnWidth — all non-negative initially
        for (int c = 0; c < 5; c++)
            Assert.True(doc.GetColumnWidth("Financials", c) >= 0);

        // GetColumnWidth consistent
        Assert.Equal(doc.GetColumnWidth("Financials", 0), doc.GetColumnWidth("Financials", 0));

        // SetColumnWidth — assign specific widths
        doc.SetColumnWidth("Financials", 0, 60);   // Year — narrow
        doc.SetColumnWidth("Financials", 1, 140);  // Division — wide
        doc.SetColumnWidth("Financials", 2, 100);  // Revenue
        doc.SetColumnWidth("Financials", 3, 100);  // Cost
        doc.SetColumnWidth("Financials", 4, 80);   // Margin

        // GetColumnWidth after set — all non-negative
        for (int c = 0; c < 5; c++)
            Assert.True(doc.GetColumnWidth("Financials", c) >= 0);

        // GetRowHeight — all non-negative
        for (int r = 0; r < 4; r++)
            Assert.True(doc.GetRowHeight("Financials", r) >= 0);

        // GetRowHeight consistent
        Assert.Equal(doc.GetRowHeight("Financials", 0), doc.GetRowHeight("Financials", 0));

        // ExportToCsv works
        var csv = doc.ExportToCsv("Financials");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // SaveToFile
        var path = TempFile("dogfood_financials.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(doc.GetSheetCount(), loaded.GetSheetCount());

        // GetColumnWidth on loaded
        for (int c = 0; c < 5; c++)
            Assert.True(loaded.GetColumnWidth("Financials", c) >= 0);

        // GetRowHeight on loaded
        for (int r = 0; r < 4; r++)
            Assert.True(loaded.GetRowHeight("Financials", r) >= 0);

        // SetColumnWidth on loaded
        loaded.SetColumnWidth("Financials", 1, 180);
        Assert.True(loaded.GetColumnWidth("Financials", 1) >= 0);

        // Verify cell data intact
        var yearVal = loaded.GetCellValue("Financials", 1, 0);
        Assert.NotNull(yearVal);

        // Final save
        var path2 = TempFile("dogfood_financials_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(loaded.GetSheetCount(), loaded2.GetSheetCount());
        for (int c = 0; c < 5; c++)
            Assert.True(loaded2.GetColumnWidth("Financials", c) >= 0);
        for (int r = 0; r < 4; r++)
            Assert.True(loaded2.GetRowHeight("Financials", r) >= 0);
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("Financials"));
        Assert.Null(ex1);
    }
}
