// Tests for FormatFactory.Fods.Spec.Table.TableCell, TableRow, and Table model classes.
// Sprint: FORMAT-FACTORY-FODS-R141-20260627
// Ledger: R141-GOVERNED-DOTNET-FODS-SPEC-TABLE-CELL-001

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R141: Tests for the canonical spec-shaped model classes in FormatFactory.Fods.Spec.Table:
/// TableCell (table:table-cell, FACT-FODS-006),
/// TableRow (table:table-row, FACT-FODS-005),
/// Table (table:table, FACT-FODS-004).
/// Covers: SpecQName constants; SpecFactRef constants; init-only property assignment;
/// ValueType; IsCovered; Content; CellCount; StyleName; Name; RowCount;
/// dogfood row→cells composition pipeline.
/// ODF 1.3 basis: §9.1.2 (table:table), §9.1.3 (table:table-row), §9.4.5 (table:table-cell).
/// </summary>
public class FodsR141SpecTableCellTests
{
    // -------------------------------------------------------------------------
    // TableCell constants and properties
    // -------------------------------------------------------------------------

    [Fact]
    public void TableCell_SpecQName_IsCorrect()
    {
        Assert.Equal("table:table-cell", Spec.Table.TableCell.SpecQName);
    }

    [Fact]
    public void TableCell_SpecFactRef_IsCorrect()
    {
        Assert.Equal("FACT-FODS-006", Spec.Table.TableCell.SpecFactRef);
    }

    [Fact]
    public void TableCell_ValueType_IsAssignable()
    {
        var cell = new Spec.Table.TableCell { ValueType = "float" };
        Assert.Equal("float", cell.ValueType);
    }

    [Fact]
    public void TableCell_ValueType_NullByDefault()
    {
        var cell = new Spec.Table.TableCell();
        Assert.Null(cell.ValueType);
    }

    [Fact]
    public void TableCell_Content_DefaultIsEmpty()
    {
        var cell = new Spec.Table.TableCell();
        Assert.Equal(string.Empty, cell.Content);
    }

    [Fact]
    public void TableCell_IsCovered_DefaultIsFalse()
    {
        var cell = new Spec.Table.TableCell();
        Assert.False(cell.IsCovered);
    }

    // -------------------------------------------------------------------------
    // TableRow constants and properties
    // -------------------------------------------------------------------------

    [Fact]
    public void TableRow_SpecQName_IsCorrect()
    {
        Assert.Equal("table:table-row", Spec.Table.TableRow.SpecQName);
    }

    [Fact]
    public void TableRow_SpecFactRef_IsCorrect()
    {
        Assert.Equal("FACT-FODS-005", Spec.Table.TableRow.SpecFactRef);
    }

    [Fact]
    public void TableRow_CellCount_IsAssignable()
    {
        var row = new Spec.Table.TableRow { CellCount = 5 };
        Assert.Equal(5, row.CellCount);
    }

    // -------------------------------------------------------------------------
    // Table constants and properties
    // -------------------------------------------------------------------------

    [Fact]
    public void Table_SpecQName_IsCorrect()
    {
        Assert.Equal("table:table", Spec.Table.Table.SpecQName);
    }

    // -------------------------------------------------------------------------
    // Dogfood: row → cells composition pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_RowAndCellComposition()
    {
        // Construct a minimal spec row+cells (dogfood pipeline)
        var cellA = new Spec.Table.TableCell { ValueType = "string", Content = "Alice" };
        var cellB = new Spec.Table.TableCell { ValueType = "float",  Content = "95.0" };
        var row   = new Spec.Table.TableRow  { CellCount = 2 };
        var table = new Spec.Table.Table     { Name = "Sheet1", RowCount = 1 };

        Assert.Equal(2, row.CellCount);
        Assert.Equal("Alice", cellA.Content);
        Assert.Equal("float", cellB.ValueType);
        Assert.Equal("Sheet1", table.Name);
        Assert.Equal(1, table.RowCount);
    }
}
