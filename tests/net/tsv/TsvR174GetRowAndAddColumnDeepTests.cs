// Tests for TsvDocument.GetRow, AddColumn, RemoveColumn, GetCell deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R174

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R174: Tests for TsvDocument.GetRow, AddColumn, RemoveColumn, GetCell deeper.
/// GetRow(index): returns a list of cell values for the given row.
/// AddColumn(header, values): appends a new column with given header and values.
/// RemoveColumn(name): removes the column with the given header name.
/// GetCell(row, col): returns the cell value at the given row and column indices.
/// Covers: GetRow first row non-null; GetRow count equals ColumnCount; GetRow last row correct;
/// AddColumn increases ColumnCount; AddColumn header appears in Headers; AddColumn values accessible;
/// RemoveColumn decreases ColumnCount; RemoveColumn header no longer in Headers;
/// GetCell by index returns correct value; GetCell by column name correct;
/// dogfood CreateEmpty->AddRows->AddColumn->GetRow->GetCell->RemoveColumn->Verify pipeline.
/// </summary>
public class TsvR174GetRowAndAddColumnDeepTests
{
    private static TsvDocument CreateWithThreeRows()
    {
        var doc = TsvDocument.CreateEmpty(new List<string> { "Name", "Dept", "Score" });
        doc.AddRow(new List<string> { "Alice", "Engineering", "92" });
        doc.AddRow(new List<string> { "Bob", "Finance", "85" });
        doc.AddRow(new List<string> { "Carol", "Engineering", "78" });
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetRow
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRow_First_NonNull()
    {
        var doc = CreateWithThreeRows();
        Assert.NotNull(doc.GetRow(0));
    }

    [Fact]
    public void GetRow_First_CountEqualsColumnCount()
    {
        var doc = CreateWithThreeRows();
        Assert.Equal(doc.ColumnCount, doc.GetRow(0).Count);
    }

    [Fact]
    public void GetRow_First_ContainsExpectedValues()
    {
        var doc = CreateWithThreeRows();
        var row = doc.GetRow(0);
        Assert.Contains("Alice", row);
    }

    [Fact]
    public void GetRow_Last_ContainsExpectedValues()
    {
        var doc = CreateWithThreeRows();
        var row = doc.GetRow(2);
        Assert.Contains("Carol", row);
    }

    [Fact]
    public void GetRow_Middle_ContainsExpectedValues()
    {
        var doc = CreateWithThreeRows();
        var row = doc.GetRow(1);
        Assert.Contains("Bob", row);
    }

    // -------------------------------------------------------------------------
    // AddColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_IncreasesColumnCount()
    {
        var doc = CreateWithThreeRows();
        var before = doc.ColumnCount;
        doc.AddColumn("Salary", new List<string> { "60000", "55000", "58000" });
        Assert.Equal(before + 1, doc.ColumnCount);
    }

    [Fact]
    public void AddColumn_HeaderAppearsInHeaders()
    {
        var doc = CreateWithThreeRows();
        doc.AddColumn("Level", new List<string> { "Senior", "Junior", "Mid" });
        Assert.Contains("Level", doc.Headers);
    }

    [Fact]
    public void AddColumn_ValuesAccessibleByGetCell()
    {
        var doc = CreateWithThreeRows();
        doc.AddColumn("Grade", new List<string> { "A", "B", "C" });
        var cell = doc.GetCell(0, doc.ColumnCount - 1);
        Assert.Equal("A", cell);
    }

    [Fact]
    public void AddColumn_MultipleCols_AllAccessible()
    {
        var doc = CreateWithThreeRows();
        doc.AddColumn("Col1", new List<string> { "X", "Y", "Z" });
        doc.AddColumn("Col2", new List<string> { "1", "2", "3" });
        Assert.True(doc.ColumnCount >= 5);
    }

    // -------------------------------------------------------------------------
    // RemoveColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveColumn_DecreasesColumnCount()
    {
        var doc = CreateWithThreeRows();
        var before = doc.ColumnCount;
        doc.RemoveColumn("Dept");
        Assert.Equal(before - 1, doc.ColumnCount);
    }

    [Fact]
    public void RemoveColumn_HeaderNoLongerInHeaders()
    {
        var doc = CreateWithThreeRows();
        doc.RemoveColumn("Score");
        Assert.DoesNotContain("Score", doc.Headers);
    }

    [Fact]
    public void RemoveColumn_OtherColumnsPreserved()
    {
        var doc = CreateWithThreeRows();
        doc.RemoveColumn("Dept");
        Assert.Contains("Name", doc.Headers);
        Assert.Contains("Score", doc.Headers);
    }

    // -------------------------------------------------------------------------
    // GetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCell_ByIndex_ReturnsCorrectValue()
    {
        var doc = CreateWithThreeRows();
        // Row 0, col 0 = "Alice"
        Assert.Equal("Alice", doc.GetCell(0, 0));
    }

    [Fact]
    public void GetCell_ByColumnName_ReturnsCorrectValue()
    {
        var doc = CreateWithThreeRows();
        Assert.Equal("Engineering", doc.GetCell(0, "Dept"));
    }

    [Fact]
    public void GetCell_LastRow_LastColumn_Correct()
    {
        var doc = CreateWithThreeRows();
        Assert.Equal("78", doc.GetCell(2, "Score"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_AddRows_AddColumn_GetRow_GetCell_RemoveColumn_Verify_Pipeline()
    {
        // CreateEmpty
        var doc = TsvDocument.CreateEmpty(new List<string> { "ID", "Product", "Price" });
        Assert.Equal(3, doc.ColumnCount);

        // AddRow
        doc.AddRow(new List<string> { "1", "Widget", "9.99" });
        doc.AddRow(new List<string> { "2", "Gadget", "24.99" });
        doc.AddRow(new List<string> { "3", "Gizmo", "14.99" });
        Assert.Equal(3, doc.RowCount);

        // GetRow
        var firstRow = doc.GetRow(0);
        Assert.NotNull(firstRow);
        Assert.Equal(3, firstRow.Count);
        Assert.Contains("Widget", firstRow);

        // GetCell
        Assert.Equal("Gadget", doc.GetCell(1, "Product"));
        Assert.Equal("14.99", doc.GetCell(2, 2));

        // AddColumn
        doc.AddColumn("InStock", new List<string> { "true", "true", "false" });
        Assert.Equal(4, doc.ColumnCount);
        Assert.Contains("InStock", doc.Headers);
        Assert.Equal("true", doc.GetCell(0, "InStock"));
        Assert.Equal("false", doc.GetCell(2, "InStock"));

        // RemoveColumn
        doc.RemoveColumn("ID");
        Assert.Equal(3, doc.ColumnCount);
        Assert.DoesNotContain("ID", doc.Headers);
        Assert.Contains("Product", doc.Headers);

        // GetRow still works after removal
        var rowAfter = doc.GetRow(0);
        Assert.Equal(3, rowAfter.Count);
    }
}
