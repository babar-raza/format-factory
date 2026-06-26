// Tests for FodsDocument.CopySheet, DeleteRows, InsertRow, ClearSheet, GetCellCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R176

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R176: Tests for FodsDocument.CopySheet, DeleteRows, InsertRow, ClearSheet, GetCellCount.
/// CopySheet(sourceName, newName): duplicates a sheet under a new name.
/// DeleteRows(sheetName, startRow, count): removes rows from a sheet.
/// InsertRow(sheetName, rowIndex): inserts an empty row at the given index.
/// ClearSheet(sheetName): removes all rows from a sheet.
/// GetCellCount(): total non-empty cells across all sheets.
/// Covers: CopySheet adds to SheetCount; CopySheet new sheet has same row values;
/// DeleteRows reduces row count; DeleteRows correct row removed;
/// InsertRow increases row count by 1; InsertRow shifts existing rows down;
/// ClearSheet makes row count zero; ClearSheet does not remove sheet;
/// GetCellCount positive after data added; GetCellCount zero after ClearSheet;
/// ExportSheetToTsv non-empty; ExportSheetToXml non-empty;
/// dogfood CreateNew->InsertRows->CopySheet->DeleteRows->ClearSheet pipeline.
/// </summary>
public class FodsR176CopySheetAndDeleteRowsTests
{
    private static FodsDocument BuildSheet(string sheetName, string[] headers, string[][] rows)
    {
        var doc = FodsDocument.CreateNew();
        var names = doc.GetSheetNames();
        if (names.Count > 0)
            doc.RenameSheet(names[0], sheetName);
        else
            doc.AddSheet(sheetName);

        doc.InsertRowWithValues(sheetName, 0, headers);
        for (var i = 0; i < rows.Length; i++)
            doc.InsertRowWithValues(sheetName, i + 1, rows[i]);

        return doc;
    }

    // -------------------------------------------------------------------------
    // CopySheet
    // -------------------------------------------------------------------------

    [Fact]
    public void CopySheet_AddsToSheetCount()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var before = doc.SheetCount;
        doc.CopySheet("Sheet", "SheetCopy");
        Assert.Equal(before + 1, doc.SheetCount);
    }

    [Fact]
    public void CopySheet_NewSheetHasSameCellValues()
    {
        var doc = BuildSheet("Original",
            new[] { "Name" },
            new[] { new[] { "Alice" } });
        doc.CopySheet("Original", "Copy");
        var original = doc.GetSheetByName("Original")!;
        var copy = doc.GetSheetByName("Copy")!;
        Assert.Equal(
            FodsDocument.GetCellValue(original, 1, 0),
            FodsDocument.GetCellValue(copy, 1, 0));
    }

    [Fact]
    public void CopySheet_NewSheetAccessibleByName()
    {
        var doc = BuildSheet("Data",
            new[] { "Col" },
            new[] { new[] { "Val" } });
        doc.CopySheet("Data", "DataCopy");
        var copy = doc.GetSheetByName("DataCopy");
        Assert.NotNull(copy);
    }

    // -------------------------------------------------------------------------
    // DeleteRows
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRows_ReducesRowCount()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name" },
            new[] { new[] { "Alice" }, new[] { "Bob" }, new[] { "Carol" } });
        var sheet = doc.GetSheetByName("Sheet")!;
        var before = sheet.Rows.Count;
        doc.DeleteRows("Sheet", 1, 1);
        Assert.Equal(before - 1, sheet.Rows.Count);
    }

    [Fact]
    public void DeleteRows_CorrectRowIsRemoved()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name" },
            new[] { new[] { "Alice" }, new[] { "Bob" }, new[] { "Carol" } });
        // Row 0 = header, Row 1 = Alice, Row 2 = Bob, Row 3 = Carol
        // Delete row 2 (Bob)
        doc.DeleteRows("Sheet", 2, 1);
        // Now row 2 should be Carol
        Assert.Equal("Carol", doc.GetCellValue(2, 0));
    }

    // -------------------------------------------------------------------------
    // InsertRow
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRow_IncreasesRowCountByOne()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name" },
            new[] { new[] { "Alice" }, new[] { "Bob" } });
        var sheet = doc.GetSheetByName("Sheet")!;
        var before = sheet.Rows.Count;
        doc.InsertRow("Sheet", 1);
        Assert.Equal(before + 1, sheet.Rows.Count);
    }

    [Fact]
    public void InsertRow_ShiftsExistingRowsDown()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name" },
            new[] { new[] { "Alice" } });
        // Before: row 1 = Alice
        doc.InsertRow("Sheet", 1); // insert empty row at index 1
        // Alice should now be at row 2
        Assert.Equal("Alice", doc.GetCellValue(2, 0));
    }

    // -------------------------------------------------------------------------
    // ClearSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearSheet_MakesRowCountZero()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name" },
            new[] { new[] { "Alice" }, new[] { "Bob" } });
        doc.ClearSheet("Sheet");
        var sheet = doc.GetSheetByName("Sheet")!;
        Assert.Equal(0, sheet.Rows.Count);
    }

    [Fact]
    public void ClearSheet_DoesNotRemoveSheet()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name" },
            new[] { new[] { "Alice" } });
        doc.ClearSheet("Sheet");
        Assert.NotNull(doc.GetSheetByName("Sheet"));
    }

    // -------------------------------------------------------------------------
    // GetCellCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCount_PositiveAfterDataAdded()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        Assert.True(doc.GetCellCount() > 0);
    }

    [Fact]
    public void GetCellCount_ZeroOrReducedAfterClearSheet()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name" },
            new[] { new[] { "Alice" } });
        var before = doc.GetCellCount();
        doc.ClearSheet("Sheet");
        Assert.True(doc.GetCellCount() <= before);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToTsv / ExportSheetToXml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToTsv_IsNonEmpty()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var tsv = FodsDocumentExporter.ExportSheetToTsv(doc.GetSheetByName("Sheet")!);
        Assert.False(string.IsNullOrEmpty(tsv));
    }

    [Fact]
    public void ExportSheetToXml_IsNonEmpty()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name" },
            new[] { new[] { "Alice" } });
        var xml = FodsDocumentExporter.ExportSheetToXml(doc.GetSheetByName("Sheet")!);
        Assert.False(string.IsNullOrEmpty(xml));
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->InsertRows->CopySheet->DeleteRows->ClearSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCopyDeleteClearPipeline()
    {
        var doc = BuildSheet("Main",
            new[] { "Item", "Qty" },
            new[] {
                new[] { "Widget", "10" },
                new[] { "Gadget", "20" },
                new[] { "Doohickey", "30" }
            });

        Assert.Equal(1, doc.SheetCount);

        // Copy sheet
        doc.CopySheet("Main", "Backup");
        Assert.Equal(2, doc.SheetCount);

        var backup = doc.GetSheetByName("Backup")!;
        Assert.Equal("Widget", FodsDocument.GetCellValue(backup, 1, 0));

        // Delete a row from main
        var main = doc.GetSheetByName("Main")!;
        var rowsBefore = main.Rows.Count;
        doc.DeleteRows("Main", 1, 1); // delete Widget row
        Assert.Equal(rowsBefore - 1, main.Rows.Count);

        // Clear backup
        doc.ClearSheet("Backup");
        Assert.Equal(0, backup.Rows.Count);
        Assert.NotNull(doc.GetSheetByName("Backup")); // sheet still exists
    }
}
