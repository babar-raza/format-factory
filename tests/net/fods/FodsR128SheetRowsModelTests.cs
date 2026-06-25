// Tests for FodsSheet.Rows model hierarchy — FodsRow.Cells and FodsCell.Value.
// Sprint: FORMAT-FACTORY-FODS-SHEET-ROWS-MODEL-20260626
// Ledger: R128-GOVERNED-DOTNET-FODS-SHEET-ROWS-MODEL-001

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R128: FodsSheet.Rows model hierarchy — iterating sheet.Rows to access
/// FodsRow.Cells and FodsCell.Value directly. Verifies that the object model
/// faithfully reflects values set via SetCellValue and InsertRowWithValues.
/// </summary>
public class FodsR128SheetRowsModelTests
{
    // ---- Rows count matches SetCellValue-based row count ----

    [Fact]
    public void SheetRows_EmptySheet_HasZeroRows()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.GetSheetByName("Sheet1")!;
        Assert.Empty(sheet.Rows);
    }

    [Fact]
    public void SheetRows_AfterSetCellValue_HasRows()
    {
        var doc = FodsDocument.CreateNew();
        FodsDocument.SetCellValue(doc.GetSheetByName("Sheet1")!, 0, 0, "A");

        var sheet = doc.GetSheetByName("Sheet1")!;
        Assert.NotEmpty(sheet.Rows);
    }

    [Fact]
    public void SheetRows_CountMatchesGetRowCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "r1c1", "r1c2" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "r2c1", "r2c2" });
        doc.InsertRowWithValues("Sheet1", 2, new[] { "r3c1", "r3c2" });

        var sheet = doc.GetSheetByName("Sheet1")!;
        Assert.Equal(doc.GetRowCount("Sheet1"), sheet.Rows.Count);
    }

    // ---- Row.Cells count ----

    [Fact]
    public void RowCells_SingleValue_HasAtLeastOneCell()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Hello" });

        var sheet = doc.GetSheetByName("Sheet1")!;
        Assert.True(sheet.Rows[0].Cells.Count >= 1,
            "Row with one value should have at least one cell");
    }

    [Fact]
    public void RowCells_ThreeValues_HasThreeCells()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "A", "B", "C" });

        var sheet = doc.GetSheetByName("Sheet1")!;
        Assert.Equal(3, sheet.Rows[0].Cells.Count);
    }

    // ---- Cell.Value reflects SetCellValue ----

    [Fact]
    public void CellValue_MatchesSetCellValue()
    {
        var doc = FodsDocument.CreateNew();
        FodsDocument.SetCellValue(doc.GetSheetByName("Sheet1")!, 0, 0, "TestValue");

        var sheet = doc.GetSheetByName("Sheet1")!;
        var cell = sheet.Rows[0].Cells[0];
        Assert.Equal("TestValue", cell.Value);
    }

    [Fact]
    public void CellValue_MultipleColumns_AllCorrect()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Alpha", "Beta", "Gamma" });

        var sheet = doc.GetSheetByName("Sheet1")!;
        var row = sheet.Rows[0];
        Assert.Equal("Alpha", row.Cells[0].Value);
        Assert.Equal("Beta", row.Cells[1].Value);
        Assert.Equal("Gamma", row.Cells[2].Value);
    }

    // ---- Cell.IsCovered for normal cells ----

    [Fact]
    public void CellIsCovered_NormalCell_IsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Normal" });

        var sheet = doc.GetSheetByName("Sheet1")!;
        Assert.False(sheet.Rows[0].Cells[0].IsCovered);
    }

    // ---- Multi-row model iteration ----

    [Fact]
    public void MultiRowIteration_AllCellsAccessible()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "R0C0", "R0C1" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "R1C0", "R1C1" });

        var sheet = doc.GetSheetByName("Sheet1")!;
        Assert.Equal("R0C0", sheet.Rows[0].Cells[0].Value);
        Assert.Equal("R0C1", sheet.Rows[0].Cells[1].Value);
        Assert.Equal("R1C0", sheet.Rows[1].Cells[0].Value);
        Assert.Equal("R1C1", sheet.Rows[1].Cells[1].Value);
    }

    // ---- Dogfood: model values match GetCellValue ----

    [Fact]
    public void DogfoodPipeline_ModelValuesMatchGetCellValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Name", "Score" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "Alice", "95" });
        doc.InsertRowWithValues("Sheet1", 2, new[] { "Bob", "87" });

        var sheet = doc.GetSheetByName("Sheet1")!;

        // Compare model iteration with GetCellValue
        for (int r = 0; r < sheet.Rows.Count; r++)
        {
            var cells = sheet.Rows[r].Cells;
            for (int c = 0; c < cells.Count; c++)
            {
                var modelVal = cells[c].Value;
                var apiVal = FodsDocument.GetCellValue(sheet, r, c);
                Assert.Equal(apiVal, modelVal);
            }
        }
    }
}
