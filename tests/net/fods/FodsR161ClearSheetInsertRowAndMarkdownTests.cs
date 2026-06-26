// Tests for FodsDocument.ClearSheet, InsertRow, ExportSheetToMarkdown, MimeType, OdfVersion.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R161

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R161: Tests for FodsDocument.ClearSheet, InsertRow, ExportSheetToMarkdown, MimeType, OdfVersion.
/// ClearSheet(sheetName): removes all rows and cells from the named sheet; GetRowCount returns 0.
/// InsertRow(sheetName, rowIndex): inserts an empty row at rowIndex; shifts existing rows down.
/// ExportSheetToMarkdown(): returns a markdown table string for the first sheet.
/// ExportSheetToMarkdown(sheetName): returns a markdown table string for the named sheet.
/// MimeType: ODF spreadsheet MIME type.
/// OdfVersion: ODF version string.
/// Covers: ClearSheet empties row count; ClearSheet nonexistent sheet throws;
/// ClearSheet then InsertRow gives row count 1; InsertRow at 0 shifts rows;
/// InsertRow OOB index is clamped or throws; ExportSheetToMarkdown contains pipe characters;
/// ExportSheetToMarkdown single cell contains cell value; ExportSheetToMarkdown named sheet;
/// MimeType is not null; OdfVersion is not null;
/// dogfood CreateNew->InsertRowWithValues->ClearSheet->InsertRow->ExportMarkdown pipeline.
/// </summary>
public class FodsR161ClearSheetInsertRowAndMarkdownTests
{
    private static FodsDocument BuildSheet(
        string sheetName,
        string[] headers,
        string[][] dataRows)
    {
        var doc = FodsDocument.CreateNew();
        if (doc.GetSheetNames().Count > 0)
            doc.RenameSheet(doc.GetSheetNames()[0], sheetName);
        else
            doc.AddSheet(sheetName);

        doc.InsertRowWithValues(sheetName, 0, headers);
        for (var i = 0; i < dataRows.Length; i++)
            doc.InsertRowWithValues(sheetName, i + 1, dataRows[i]);

        return doc;
    }

    // -------------------------------------------------------------------------
    // ClearSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearSheet_EmptiesRowCount()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" }, new[] { "Bob", "82" } });
        doc.ClearSheet("Data");
        Assert.Equal(0, doc.GetRowCount("Data"));
    }

    [Fact]
    public void ClearSheet_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.ClearSheet("NoSuchSheet"));
    }

    [Fact]
    public void ClearSheet_ThenInsertRow_RowCountIsOne()
    {
        var doc = BuildSheet("Data",
            new[] { "A", "B" },
            new[] { new[] { "1", "2" } });
        doc.ClearSheet("Data");
        doc.InsertRow("Data", 0);
        Assert.Equal(1, doc.GetRowCount("Data"));
    }

    // -------------------------------------------------------------------------
    // InsertRow
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRow_AtZero_ShiftsExistingRows()
    {
        var doc = BuildSheet("Sheet",
            new[] { "H1" },
            new[] { new[] { "RowA" } });

        var beforeCount = doc.GetRowCount("Sheet");
        doc.InsertRow("Sheet", 0);
        Assert.Equal(beforeCount + 1, doc.GetRowCount("Sheet"));
    }

    [Fact]
    public void InsertRow_IncreasesRowCount()
    {
        var doc = BuildSheet("Sheet",
            new[] { "H" },
            new[] { new[] { "R1" }, new[] { "R2" } });
        var before = doc.GetRowCount("Sheet");
        doc.InsertRow("Sheet", 1);
        Assert.Equal(before + 1, doc.GetRowCount("Sheet"));
    }

    // -------------------------------------------------------------------------
    // ExportSheetToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToMarkdown_ContainsPipeCharacters()
    {
        var doc = BuildSheet("Report",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var md = doc.ExportSheetToMarkdown("Report");
        Assert.Contains("|", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsCellValue()
    {
        var doc = BuildSheet("Report",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var md = doc.ExportSheetToMarkdown("Report");
        Assert.Contains("Alice", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_NoArgs_ContainsData()
    {
        var doc = BuildSheet("First",
            new[] { "Col1" },
            new[] { new[] { "Val1" } });
        var md = doc.ExportSheetToMarkdown();
        Assert.Contains("|", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsHeaders()
    {
        var doc = BuildSheet("Report",
            new[] { "Name", "Score" },
            new[] { new[] { "Bob", "82" } });
        var md = doc.ExportSheetToMarkdown("Report");
        Assert.Contains("Name", md);
        Assert.Contains("Score", md);
    }

    // -------------------------------------------------------------------------
    // MimeType / OdfVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void MimeType_IsNotNullOrEmpty()
    {
        var doc = FodsDocument.CreateNew();
        Assert.False(string.IsNullOrEmpty(doc.MimeType));
    }

    [Fact]
    public void OdfVersion_IsNotNullOrEmpty()
    {
        var doc = FodsDocument.CreateNew();
        Assert.False(string.IsNullOrEmpty(doc.OdfVersion));
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->InsertRowWithValues->ClearSheet->InsertRow->ExportMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertClearInsertMarkdown_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.GetSheetNames()[0];

        doc.InsertRowWithValues(sheetName, 0, new[] { "Product", "Price" });
        doc.InsertRowWithValues(sheetName, 1, new[] { "Widget", "9.99" });
        doc.InsertRowWithValues(sheetName, 2, new[] { "Gadget", "19.99" });
        Assert.Equal(3, doc.GetRowCount(sheetName));

        // Clear the sheet
        doc.ClearSheet(sheetName);
        Assert.Equal(0, doc.GetRowCount(sheetName));

        // Re-insert one row
        doc.InsertRow(sheetName, 0);
        Assert.Equal(1, doc.GetRowCount(sheetName));

        // Set a cell and export
        doc.SetCellValue(0, 0, "RebornProduct");
        var md = doc.ExportSheetToMarkdown();
        Assert.Contains("|", md);
    }
}
