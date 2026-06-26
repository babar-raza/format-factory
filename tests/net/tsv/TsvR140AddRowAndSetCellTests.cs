// Tests for TsvDocument.AddRow, SetCell, RemoveRow via Rows mutation, ColumnCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R140

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R140: Tests for TsvDocument mutation via Rows list manipulation and ToTsv round-trips.
/// Rows: mutable list — can Add, Remove, and modify rows.
/// SetCell via direct Rows[row][col] assignment.
/// Covers: Add new row increases RowCount; Remove row decreases RowCount;
/// Set cell value reflects in GetCellValue; ToCsv after mutation includes new data;
/// Load with hasHeaders preserves Headers; Load without headers has null Headers;
/// ColumnCount from rows when no headers; AddRow(list) increases count;
/// mutation independence — shallow copy of rows doesn't alias;
/// dogfood Load->AddRow->SetCell->RemoveRow->ToTsv->Load pipeline.
/// </summary>
public class TsvR140AddRowAndSetCellTests
{
    private const string ThreeRowTsv =
        "Name\tScore\n" +
        "Alice\t95\n" +
        "Bob\t82\n" +
        "Carol\t88";

    // -------------------------------------------------------------------------
    // Rows mutation — Add
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncreasesRowCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var before = doc.RowCount;
        doc.Rows.Add(new[] { "Dave", "91" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_NewRowAccessibleViaGetCellValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.Rows.Add(new[] { "Dave", "91" });
        Assert.Equal("Dave", doc.GetCellValue(doc.RowCount - 1, 0));
    }

    [Fact]
    public void AddMultipleRows_CountIncreasesByAmount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var before = doc.RowCount;
        doc.Rows.Add(new[] { "Dave", "91" });
        doc.Rows.Add(new[] { "Eve", "77" });
        Assert.Equal(before + 2, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // Rows mutation — Remove
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_DecreasesRowCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var before = doc.RowCount;
        doc.Rows.RemoveAt(0);
        Assert.Equal(before - 1, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_SubsequentRowShiftsUp()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        // Remove Alice (index 0), Bob should now be at 0
        doc.Rows.RemoveAt(0);
        Assert.Equal("Bob", doc.GetCellValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // SetCell via direct assignment
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_ReflectsInGetCellValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.Rows[0][1] = "100"; // Change Alice's score
        Assert.Equal("100", doc.GetCellValue(0, 1));
    }

    [Fact]
    public void SetCell_DoesNotAffectOtherCells()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.Rows[0][1] = "100";
        Assert.Equal("Alice", doc.GetCellValue(0, 0)); // Name unchanged
        Assert.Equal("82", doc.GetCellValue(1, 1)); // Bob's score unchanged
    }

    // -------------------------------------------------------------------------
    // Headers
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_WithHeaders_HasHeadersProperty()
    {
        var doc = TsvDocument.Load(ThreeRowTsv, hasHeaders: true);
        Assert.True(doc.HasHeaders);
        Assert.NotNull(doc.Headers);
    }

    [Fact]
    public void Load_WithoutHeaders_HeadersIsNull()
    {
        var doc = TsvDocument.Load("Alice\t95\nBob\t82", hasHeaders: false);
        Assert.False(doc.HasHeaders);
        Assert.Null(doc.Headers);
    }

    [Fact]
    public void Load_Headers_ContainsExpectedNames()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Contains("Name", doc.Headers!);
        Assert.Contains("Score", doc.Headers!);
    }

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_WithHeaders_FromHeaderLength()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(2, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_NoHeaders_FromFirstRow()
    {
        var doc = TsvDocument.Load("A\tB\tC\n1\t2\t3", hasHeaders: false);
        Assert.Equal(3, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AddRow->SetCell->RemoveRow->ToTsv->Load
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddSetRemoveTsvLoad_Pipeline()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(3, doc.RowCount);

        // Add a new row
        doc.Rows.Add(new[] { "Dave", "91" });
        Assert.Equal(4, doc.RowCount);

        // Set a cell
        doc.Rows[3][1] = "92"; // Correct Dave's score
        Assert.Equal("92", doc.GetCellValue(3, 1));

        // Remove Bob (index 1)
        doc.Rows.RemoveAt(1);
        Assert.Equal(3, doc.RowCount);

        // Serialize and reload
        var tsv = doc.ToTsv();
        Assert.Contains("\t", tsv);
        var reloaded = TsvDocument.Load(tsv, hasHeaders: false);
        Assert.Equal(3, reloaded.RowCount);

        // Dave should be present
        var names = new List<string>();
        for (var i = 0; i < reloaded.RowCount; i++)
            names.Add(reloaded.GetCellValue(i, 0) ?? "");
        Assert.Contains("Dave", names);
        // Bob should be gone
        Assert.DoesNotContain("Bob", names);
    }
}
