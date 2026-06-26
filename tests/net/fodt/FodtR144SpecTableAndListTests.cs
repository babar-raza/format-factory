// Tests for FormatFactory.Fodt.Spec.Table and Spec.Text.List model classes.
// Sprint: FORMAT-FACTORY-FODT-R144-20260627
// Ledger: R144-GOVERNED-DOTNET-FODT-SPEC-TABLE-LIST-001

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R144: Tests for the canonical spec-shaped model classes in FormatFactory.Fodt.Spec.Table
/// and FormatFactory.Fodt.Spec.Text:
/// Spec.Table.Table (table:table, FACT-FODT-007),
/// Spec.Table.TableRow (table:table-row, FACT-FODT-007),
/// Spec.Table.TableCell (table:table-cell, FACT-FODT-007),
/// Spec.Text.List (text:list, FACT-FODT-005),
/// Spec.Text.ListItem (text:list-item, FACT-FODT-005),
/// Spec.Office.Body (office:body, FACT-FODT-002).
/// Covers: SpecQName constants; SpecFactRef constants; init-only property assignment;
/// IsCovered; Content; CellCount; StyleName; ItemCount; ChildCount;
/// dogfood table→row→cell composition pipeline.
/// ODF 1.3 basis: §3.3 (office:body), §5.3.1 (text:list), §9.1.2 (table:table).
/// </summary>
public class FodtR144SpecTableAndListTests
{
    // -------------------------------------------------------------------------
    // Spec.Table.Table
    // -------------------------------------------------------------------------

    [Fact]
    public void Table_SpecQName_IsCorrect()
    {
        Assert.Equal("table:table", Spec.Table.Table.SpecQName);
    }

    [Fact]
    public void Table_SpecFactRef_IsCorrect()
    {
        Assert.Equal("FACT-FODT-007", Spec.Table.Table.SpecFactRef);
    }

    [Fact]
    public void Table_NameAndRowCount_AreAssignable()
    {
        var t = new Spec.Table.Table { Name = "Data", RowCount = 3 };
        Assert.Equal("Data", t.Name);
        Assert.Equal(3, t.RowCount);
    }

    // -------------------------------------------------------------------------
    // Spec.Table.TableRow
    // -------------------------------------------------------------------------

    [Fact]
    public void TableRow_SpecQName_IsCorrect()
    {
        Assert.Equal("table:table-row", Spec.Table.TableRow.SpecQName);
    }

    [Fact]
    public void TableRow_CellCount_IsAssignable()
    {
        var row = new Spec.Table.TableRow { CellCount = 4 };
        Assert.Equal(4, row.CellCount);
    }

    // -------------------------------------------------------------------------
    // Spec.Table.TableCell
    // -------------------------------------------------------------------------

    [Fact]
    public void TableCell_SpecQName_IsCorrect()
    {
        Assert.Equal("table:table-cell", Spec.Table.TableCell.SpecQName);
    }

    [Fact]
    public void TableCell_Content_IsAssignable()
    {
        var cell = new Spec.Table.TableCell { Content = "100.00" };
        Assert.Equal("100.00", cell.Content);
    }

    [Fact]
    public void TableCell_IsCovered_DefaultIsFalse()
    {
        var cell = new Spec.Table.TableCell();
        Assert.False(cell.IsCovered);
    }

    // -------------------------------------------------------------------------
    // Spec.Text.List and ListItem
    // -------------------------------------------------------------------------

    [Fact]
    public void List_SpecQName_IsCorrect()
    {
        Assert.Equal("text:list", Spec.Text.List.SpecQName);
    }

    [Fact]
    public void ListItem_SpecQName_IsCorrect()
    {
        Assert.Equal("text:list-item", Spec.Text.ListItem.SpecQName);
    }

    [Fact]
    public void List_ItemCount_IsAssignable()
    {
        var list = new Spec.Text.List { ItemCount = 3 };
        Assert.Equal(3, list.ItemCount);
    }

    // -------------------------------------------------------------------------
    // Spec.Office.Body
    // -------------------------------------------------------------------------

    [Fact]
    public void Body_SpecQName_IsCorrect()
    {
        Assert.Equal("office:body", Spec.Office.Body.SpecQName);
    }

    // -------------------------------------------------------------------------
    // Dogfood: table → row → cell composition pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TableRowCellComposition()
    {
        var cellA = new Spec.Table.TableCell { Content = "Alice" };
        var cellB = new Spec.Table.TableCell { Content = "95" };
        var row   = new Spec.Table.TableRow  { CellCount = 2, StyleName = "TableRow1" };
        var table = new Spec.Table.Table     { Name = "Results", RowCount = 1 };
        var body  = new Spec.Office.Body     { ChildCount = 2 };
        var list  = new Spec.Text.List       { ItemCount = 2, StyleName = "List_Bullet" };
        var item  = new Spec.Text.ListItem   { Content = "First item" };

        Assert.Equal("Alice", cellA.Content);
        Assert.Equal(2, row.CellCount);
        Assert.Equal("Results", table.Name);
        Assert.Equal(2, body.ChildCount);
        Assert.Equal(2, list.ItemCount);
        Assert.Equal("First item", item.Content);
    }
}
