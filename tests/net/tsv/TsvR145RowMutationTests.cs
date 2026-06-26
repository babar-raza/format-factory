// Tests for TsvDocument row mutation: Rows.Add, Rows.RemoveAt, Rows[r][c] = value.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R145

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R145: Tests for TsvDocument row mutation via Rows collection.
/// Rows.Add(string[]): appends a row to the document.
/// Rows.RemoveAt(int): removes a row at the given index.
/// Rows[r][c] = value: sets a cell value in-place.
/// Covers: Add row increases RowCount; Add multiple rows increases correctly;
/// Added row values are retrievable; RemoveAt decreases RowCount;
/// RemoveAt correct row removed; Cell assignment changes value;
/// Cell assignment persists through ToTsv round-trip; RowCount after mutations;
/// Filter after mutation works correctly; IsEmpty after removing all rows;
/// GetColumnValues after add contains new value; GetCellValue after cell assignment;
/// dogfood Load->Add->RemoveAt->SetCell->ToTsv pipeline.
/// </summary>
public class TsvR145RowMutationTests
{
    private const string TwoRowTsv =
        "Name\tScore\n" +
        "Alice\t95\n" +
        "Bob\t82";

    // -------------------------------------------------------------------------
    // Rows.Add
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncreasesRowCount()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        var before = doc.RowCount;
        doc.Rows.Add(new[] { "Carol", "88" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddMultipleRows_IncreasesCorrectly()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        var before = doc.RowCount;
        doc.Rows.Add(new[] { "Carol", "88" });
        doc.Rows.Add(new[] { "Dave", "91" });
        Assert.Equal(before + 2, doc.RowCount);
    }

    [Fact]
    public void AddRow_ValuesRetrievable()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.Rows.Add(new[] { "Carol", "88" });
        var lastRow = doc.Rows[doc.RowCount - 1];
        Assert.Equal("Carol", lastRow[0]);
        Assert.Equal("88", lastRow[1]);
    }

    [Fact]
    public void AddRow_GetColumnValues_ContainsNewValue()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.Rows.Add(new[] { "Carol", "88" });
        var names = doc.GetColumnValues(0);
        Assert.Contains("Carol", names);
    }

    // -------------------------------------------------------------------------
    // Rows.RemoveAt
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveAt_DecreasesRowCount()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        var before = doc.RowCount;
        doc.Rows.RemoveAt(0);
        Assert.Equal(before - 1, doc.RowCount);
    }

    [Fact]
    public void RemoveAt_CorrectRowRemoved()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        // Remove first row (Name\tScore header row)
        doc.Rows.RemoveAt(0);
        // First row should now be Alice
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void RemoveAt_AllRows_IsEmpty()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        while (doc.RowCount > 0)
            doc.Rows.RemoveAt(0);
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void RemoveAt_LastRow_RowCountDecreases()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        var before = doc.RowCount;
        doc.Rows.RemoveAt(doc.RowCount - 1);
        Assert.Equal(before - 1, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // Cell assignment: Rows[r][c] = value
    // -------------------------------------------------------------------------

    [Fact]
    public void CellAssignment_ChangesValue()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.Rows[1][1] = "100"; // Change Alice's score
        Assert.Equal("100", doc.Rows[1][1]);
    }

    [Fact]
    public void CellAssignment_GetCellValueReturnsNewValue()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.Rows[1][0] = "ALICE";
        Assert.Equal("ALICE", doc.GetCellValue(1, 0));
    }

    [Fact]
    public void CellAssignment_PersistsThroughToTsv()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.Rows[1][1] = "999";
        var tsv = doc.ToTsv();
        Assert.Contains("999", tsv);
    }

    // -------------------------------------------------------------------------
    // Filter after mutation
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterAfterMutation_WorksCorrectly()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.Rows.Add(new[] { "Carol", "88" });
        var high = doc.Filter(row =>
            row.Length > 1 && int.TryParse(row[1], out var s) && s > 85);
        // Alice(95), Carol(88) pass; Bob(82) does not
        Assert.Equal(2, high.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Add->RemoveAt->SetCell->ToTsv pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddRemoveSetCellToTsvPipeline()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        Assert.Equal(3, doc.RowCount); // header + 2 rows

        // Add rows
        doc.Rows.Add(new[] { "Carol", "88" });
        doc.Rows.Add(new[] { "Dave", "91" });
        Assert.Equal(5, doc.RowCount);

        // Remove one
        doc.Rows.RemoveAt(2); // removes Bob
        Assert.Equal(4, doc.RowCount);

        // Set cell
        doc.Rows[1][1] = "97"; // Update Alice's score
        Assert.Equal("97", doc.GetCellValue(1, 1));

        // ToTsv preserves changes
        var tsv = doc.ToTsv();
        Assert.Contains("97", tsv);
        Assert.Contains("Carol", tsv);
        Assert.DoesNotContain("Bob", tsv);

        // Reload
        var reloaded = TsvDocument.Load(tsv, hasHeaders: false);
        Assert.Equal(4, reloaded.RowCount);
    }
}
