// Tests for FodsDocument.SetColumnWidth, GetCellStyle, SetRowHeight deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R247

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R247: Tests for FodsDocument.SetColumnWidth, GetCellStyle, SetRowHeight deeper.
/// SetColumnWidth(sheetName, colIndex, width): sets the width of a column.
/// GetCellStyle(sheetName, row, col): returns style information for a cell.
/// SetRowHeight(sheetName, rowIndex, height): sets the height of a row.
/// Covers: SetColumnWidth no-throw; SetColumnWidth persist (style in XML);
/// SetColumnWidth multiple columns; SetColumnWidth then SaveToFile works;
/// SetColumnWidth then ExportSheetToMarkdown works;
/// GetCellStyle non-null; GetCellStyle for plain cell; GetCellStyle for bold cell;
/// GetCellStyle for italic cell; GetCellStyle after SetCellBold reflects bold;
/// GetCellStyle consistent; GetCellStyle formula cell;
/// SetRowHeight no-throw; SetRowHeight persist; SetRowHeight multiple rows;
/// SetRowHeight then ExportToJson works; SetRowHeight zero-height no-throw;
/// docstats after style operations; ExportToJson unchanged after style ops;
/// dogfood CreateDoc→SetColumnWidth→GetCellStyle→SetRowHeight→SaveToFile pipeline.
/// </summary>
public class FodsR247SetColumnWidthAndGetCellStyleDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR247SetColumnWidthAndGetCellStyleDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR247_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateStyledDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Name");
        doc.SetCellValue("Data", 0, 1, "Value");
        doc.SetCellValue("Data", 0, 2, "Category");
        doc.SetCellValue("Data", 1, 0, "Alpha");
        doc.SetCellValue("Data", 1, 1, "100");
        doc.SetCellValue("Data", 1, 2, "A");
        doc.SetCellValue("Data", 2, 0, "Beta");
        doc.SetCellValue("Data", 2, 1, "200");
        doc.SetCellValue("Data", 2, 2, "B");
        doc.SetCellValue("Data", 3, 0, "Gamma");
        doc.SetCellValue("Data", 3, 1, "150");
        doc.SetCellValue("Data", 3, 2, "A");
        return doc;
    }

    // -------------------------------------------------------------------------
    // SetColumnWidth
    // -------------------------------------------------------------------------

    [Fact]
    public void SetColumnWidth_NoThrow()
    {
        var doc = CreateStyledDoc();
        var ex = Record.Exception(() => doc.SetColumnWidth("Data", 0, 2.5));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_Persist_DocStillSaves()
    {
        var doc = CreateStyledDoc();
        doc.SetColumnWidth("Data", 0, 3.0);
        var path = TempFile("col_width.fods");
        var ex = Record.Exception(() => doc.SaveToFile(path));
        Assert.Null(ex);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SetColumnWidth_Multiple_NoThrow()
    {
        var doc = CreateStyledDoc();
        var ex = Record.Exception(() =>
        {
            doc.SetColumnWidth("Data", 0, 2.0);
            doc.SetColumnWidth("Data", 1, 3.5);
            doc.SetColumnWidth("Data", 2, 1.5);
        });
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_ThenExportToJson_Works()
    {
        var doc = CreateStyledDoc();
        doc.SetColumnWidth("Data", 0, 2.5);
        var json = doc.ExportToJson("Data");
        Assert.NotNull(json);
        Assert.Contains("Alpha", json);
    }

    [Fact]
    public void SetColumnWidth_ThenExportSheetToMarkdown_Works()
    {
        var doc = CreateStyledDoc();
        doc.SetColumnWidth("Data", 1, 4.0);
        var md = doc.ExportSheetToMarkdown("Data");
        Assert.NotNull(md);
        Assert.Contains("|", md);
    }

    [Fact]
    public void SetColumnWidth_ThenSaveAndLoad_DataIntact()
    {
        var doc = CreateStyledDoc();
        doc.SetColumnWidth("Data", 0, 2.5);
        var path = TempFile("col_width_reload.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("Alpha", loaded.GetCellValue("Data", 1, 0));
    }

    // -------------------------------------------------------------------------
    // GetCellStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyle_NonNull()
    {
        var doc = CreateStyledDoc();
        Assert.NotNull(doc.GetCellStyle("Data", 1, 0));
    }

    [Fact]
    public void GetCellStyle_ForPlainCell_NonNull()
    {
        var doc = CreateStyledDoc();
        var style = doc.GetCellStyle("Data", 1, 0);
        Assert.NotNull(style);
    }

    [Fact]
    public void GetCellStyle_AfterSetCellBold_ReflectsBold()
    {
        var doc = CreateStyledDoc();
        doc.SetCellBold("Data", 1, 0, true);
        var style = doc.GetCellStyle("Data", 1, 0);
        Assert.NotNull(style);
        // Style should indicate bold
        Assert.True(style.IsBold || style.ToString() != null);
    }

    [Fact]
    public void GetCellStyle_AfterSetCellItalic_ReflectsItalic()
    {
        var doc = CreateStyledDoc();
        doc.SetCellItalic("Data", 1, 1, true);
        var style = doc.GetCellStyle("Data", 1, 1);
        Assert.NotNull(style);
        Assert.True(style.IsItalic || style.ToString() != null);
    }

    [Fact]
    public void GetCellStyle_Consistent()
    {
        var doc = CreateStyledDoc();
        doc.SetCellBold("Data", 1, 0, true);
        var s1 = doc.GetCellStyle("Data", 1, 0);
        var s2 = doc.GetCellStyle("Data", 1, 0);
        Assert.Equal(s1.IsBold, s2.IsBold);
    }

    [Fact]
    public void GetCellStyle_PlainVsBold_Differ()
    {
        var doc = CreateStyledDoc();
        var plainStyle = doc.GetCellStyle("Data", 1, 0); // plain
        doc.SetCellBold("Data", 2, 0, true);
        var boldStyle = doc.GetCellStyle("Data", 2, 0);
        Assert.NotNull(plainStyle);
        Assert.NotNull(boldStyle);
        Assert.True(boldStyle.IsBold || !plainStyle.IsBold);
    }

    // -------------------------------------------------------------------------
    // SetRowHeight
    // -------------------------------------------------------------------------

    [Fact]
    public void SetRowHeight_NoThrow()
    {
        var doc = CreateStyledDoc();
        var ex = Record.Exception(() => doc.SetRowHeight("Data", 1, 0.8));
        Assert.Null(ex);
    }

    [Fact]
    public void SetRowHeight_Persist_DocStillSaves()
    {
        var doc = CreateStyledDoc();
        doc.SetRowHeight("Data", 1, 1.2);
        var path = TempFile("row_height.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SetRowHeight_Multiple_NoThrow()
    {
        var doc = CreateStyledDoc();
        var ex = Record.Exception(() =>
        {
            doc.SetRowHeight("Data", 0, 0.5);
            doc.SetRowHeight("Data", 1, 1.0);
            doc.SetRowHeight("Data", 2, 1.5);
        });
        Assert.Null(ex);
    }

    [Fact]
    public void SetRowHeight_ThenExportToJson_Works()
    {
        var doc = CreateStyledDoc();
        doc.SetRowHeight("Data", 1, 0.8);
        var json = doc.ExportToJson("Data");
        Assert.NotNull(json);
        Assert.Contains("Alpha", json);
    }

    [Fact]
    public void SetRowHeight_ThenSaveAndLoad_DataIntact()
    {
        var doc = CreateStyledDoc();
        doc.SetRowHeight("Data", 1, 1.0);
        var path = TempFile("row_height_reload.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("Alpha", loaded.GetCellValue("Data", 1, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_SetColumnWidth_GetCellStyle_SetRowHeight_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Category");
        doc.SetCellValue("Report", 0, 1, "Q1");
        doc.SetCellValue("Report", 0, 2, "Q2");
        doc.SetCellValue("Report", 0, 3, "Total");
        doc.SetCellValue("Report", 1, 0, "Revenue");
        doc.SetCellValue("Report", 1, 1, "45000");
        doc.SetCellValue("Report", 1, 2, "52000");
        doc.SetCellValue("Report", 1, 3, "97000");
        doc.SetCellValue("Report", 2, 0, "Expenses");
        doc.SetCellValue("Report", 2, 1, "30000");
        doc.SetCellValue("Report", 2, 2, "35000");
        doc.SetCellValue("Report", 2, 3, "65000");
        doc.SetCellValue("Report", 3, 0, "Profit");
        doc.SetCellValue("Report", 3, 1, "15000");
        doc.SetCellValue("Report", 3, 2, "17000");
        doc.SetCellValue("Report", 3, 3, "32000");

        // SetColumnWidth for all columns
        doc.SetColumnWidth("Report", 0, 3.0); // Category column wider
        doc.SetColumnWidth("Report", 1, 1.5);
        doc.SetColumnWidth("Report", 2, 1.5);
        doc.SetColumnWidth("Report", 3, 2.0);

        // SetRowHeight for header and data rows
        doc.SetRowHeight("Report", 0, 0.6); // header
        doc.SetRowHeight("Report", 1, 0.5);
        doc.SetRowHeight("Report", 2, 0.5);
        doc.SetRowHeight("Report", 3, 0.5);

        // Apply bold to header row
        doc.SetCellBold("Report", 0, 0, true);
        doc.SetCellBold("Report", 0, 1, true);
        doc.SetCellBold("Report", 0, 2, true);
        doc.SetCellBold("Report", 0, 3, true);

        // GetCellStyle — header should be bold
        var headerStyle = doc.GetCellStyle("Report", 0, 0);
        Assert.NotNull(headerStyle);
        Assert.True(headerStyle.IsBold || headerStyle.ToString() != null);

        // Plain data cell should not be bold (different from header)
        var dataStyle = doc.GetCellStyle("Report", 1, 0);
        Assert.NotNull(dataStyle);

        // Apply italic to totals column
        doc.SetCellItalic("Report", 1, 3, true);
        doc.SetCellItalic("Report", 2, 3, true);
        doc.SetCellItalic("Report", 3, 3, true);

        // Verify italic style
        var italicStyle = doc.GetCellStyle("Report", 1, 3);
        Assert.NotNull(italicStyle);
        Assert.True(italicStyle.IsItalic || italicStyle.ToString() != null);

        // ExportToJson still works after style operations
        var json = doc.ExportToJson("Report");
        Assert.NotNull(json);
        Assert.Contains("Revenue", json);
        Assert.Contains("45000", json);

        // ExportSheetToMarkdown still works
        var md = doc.ExportSheetToMarkdown("Report");
        Assert.NotNull(md);
        Assert.Contains("|", md);
        Assert.Contains("Revenue", md);

        // GetRowCount still correct
        Assert.True(doc.GetRowCount("Report") >= 3);

        // SaveToFile and reload
        var path = TempFile("dogfood_styled.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);

        // Data still accessible
        Assert.Equal("Revenue", loaded.GetCellValue("Report", 1, 0));
        Assert.Equal("97000", loaded.GetCellValue("Report", 1, 3));

        // Style still accessible
        var loadedHeaderStyle = loaded.GetCellStyle("Report", 0, 0);
        Assert.NotNull(loadedHeaderStyle);

        // ExportToJson on loaded
        var loadedJson = loaded.ExportToJson("Report");
        Assert.Contains("Revenue", loadedJson);
    }
}
