// FormatFactory.Csv.Tests -- Mutation API tests (TC-RECON-W5-001).
// Verifies CsvDocument.AddRow(), SetCell(), and RemoveRow().

using System;
using System.Collections.Generic;
using FormatFactory.Csv;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// Tests for CsvDocument mutation API: AddRow, SetCell, RemoveRow.
/// </summary>
public class CsvMutationApiTests
{
    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_AppendsRowToEmptyDocument()
    {
        var doc = CsvDocument.Load(string.Empty, hasHeaders: false);
        doc.AddRow(new[] { "a", "b", "c" });
        Assert.Equal(1, doc.RowCount);
        Assert.Equal(new[] { "a", "b", "c" }, doc.Rows[0]);
    }

    [Fact]
    public void AddRow_AppendsRowToExistingDocument()
    {
        var doc = CsvDocument.Load("x,y\n1,2", hasHeaders: false);
        Assert.Equal(2, doc.RowCount);
        doc.AddRow(new[] { "3", "4" });
        Assert.Equal(3, doc.RowCount);
        Assert.Equal(new[] { "3", "4" }, doc.Rows[2]);
    }

    [Fact]
    public void AddRow_WithHeaders_AppendsBelowHeaderRow()
    {
        var doc = CsvDocument.Load("Name,Age\nAlice,30", hasHeaders: true);
        Assert.Equal(1, doc.RowCount);
        doc.AddRow(new[] { "Bob", "25" });
        Assert.Equal(2, doc.RowCount);
        Assert.Equal("Bob", doc.Rows[1][0]);
        Assert.Equal("25", doc.Rows[1][1]);
    }

    [Fact]
    public void AddRow_NullInput_ThrowsArgumentNullException()
    {
        var doc = CsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.Throws<ArgumentNullException>(() => doc.AddRow(null!));
    }

    [Fact]
    public void AddRow_EmptyRow_AddsEmptyRowArray()
    {
        var doc = CsvDocument.Load(string.Empty, hasHeaders: false);
        doc.AddRow(Array.Empty<string>());
        Assert.Equal(1, doc.RowCount);
        Assert.Empty(doc.Rows[0]);
    }

    [Fact]
    public void AddRow_PreservesDocumentRoundtrip()
    {
        var doc = CsvDocument.Load("Name,Score\nAlice,90", hasHeaders: true);
        doc.AddRow(new[] { "Bob", "85" });
        var csv = doc.ToCsv();
        var reloaded = CsvDocument.Load(csv, hasHeaders: true);
        Assert.Equal(2, reloaded.RowCount);
        Assert.Equal("Bob", reloaded.GetCellValue(1, 0));
        Assert.Equal("85", reloaded.GetCellValue(1, 1));
    }

    // -------------------------------------------------------------------------
    // SetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_OverwritesExistingCell()
    {
        var doc = CsvDocument.Load("a,b,c", hasHeaders: false);
        doc.SetCell(0, 1, "NEW");
        Assert.Equal("NEW", doc.GetCellValue(0, 1));
    }

    [Fact]
    public void SetCell_FirstCellInFirstRow()
    {
        var doc = CsvDocument.Load("x,y\n1,2", hasHeaders: false);
        doc.SetCell(0, 0, "Z");
        Assert.Equal("Z", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCell_LastCellInLastRow()
    {
        var doc = CsvDocument.Load("a,b\n1,2\n3,4", hasHeaders: false);
        doc.SetCell(2, 1, "99");
        Assert.Equal("99", doc.GetCellValue(2, 1));
    }

    [Fact]
    public void SetCell_NullValue_StoresEmptyString()
    {
        var doc = CsvDocument.Load("a,b", hasHeaders: false);
        doc.SetCell(0, 0, null!);
        Assert.Equal(string.Empty, doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCell_WidensRowWhenColExceedsLength()
    {
        var doc = CsvDocument.Load("a", hasHeaders: false);
        // Row[0] currently has 1 cell; set col=3 to widen
        doc.SetCell(0, 3, "X");
        Assert.Equal("X", doc.GetCellValue(0, 3));
        // Original cell still intact
        Assert.Equal("a", doc.GetCellValue(0, 0));
        // Intermediate cells are empty string
        Assert.Equal(string.Empty, doc.GetCellValue(0, 1));
        Assert.Equal(string.Empty, doc.GetCellValue(0, 2));
    }

    [Fact]
    public void SetCell_NegativeRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = CsvDocument.Load("a,b", hasHeaders: false);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetCell(-1, 0, "x"));
    }

    [Fact]
    public void SetCell_RowTooLarge_ThrowsArgumentOutOfRangeException()
    {
        var doc = CsvDocument.Load("a,b", hasHeaders: false);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetCell(999, 0, "x"));
    }

    [Fact]
    public void SetCell_NegativeCol_ThrowsArgumentOutOfRangeException()
    {
        var doc = CsvDocument.Load("a,b", hasHeaders: false);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetCell(0, -1, "x"));
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_RemovesFirstRow()
    {
        var doc = CsvDocument.Load("a\nb\nc", hasHeaders: false);
        doc.RemoveRow(0);
        Assert.Equal(2, doc.RowCount);
        Assert.Equal("b", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void RemoveRow_RemovesLastRow()
    {
        var doc = CsvDocument.Load("a\nb\nc", hasHeaders: false);
        doc.RemoveRow(2);
        Assert.Equal(2, doc.RowCount);
        Assert.Equal("b", doc.GetCellValue(1, 0));
    }

    [Fact]
    public void RemoveRow_RemovesMiddleRow()
    {
        var doc = CsvDocument.Load("a\nb\nc", hasHeaders: false);
        doc.RemoveRow(1);
        Assert.Equal(2, doc.RowCount);
        Assert.Equal("a", doc.GetCellValue(0, 0));
        Assert.Equal("c", doc.GetCellValue(1, 0));
    }

    [Fact]
    public void RemoveRow_SingleRow_LeavesEmptyDocument()
    {
        var doc = CsvDocument.Load("only", hasHeaders: false);
        doc.RemoveRow(0);
        Assert.True(doc.IsEmpty);
        Assert.Equal(0, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = CsvDocument.Load("a,b", hasHeaders: false);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveRow(-1));
    }

    [Fact]
    public void RemoveRow_IndexTooLarge_ThrowsArgumentOutOfRangeException()
    {
        var doc = CsvDocument.Load("a,b", hasHeaders: false);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveRow(999));
    }

    [Fact]
    public void RemoveRow_AfterRemoval_RowCountDecremented()
    {
        var doc = CsvDocument.Load("1\n2\n3\n4\n5", hasHeaders: false);
        Assert.Equal(5, doc.RowCount);
        doc.RemoveRow(2);
        Assert.Equal(4, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // Combined mutation workflow
    // -------------------------------------------------------------------------

    [Fact]
    public void MutationWorkflow_AddThenSetThenRemove_CorrectFinalState()
    {
        var doc = CsvDocument.Load("Name,Score\nAlice,90\nBob,80", hasHeaders: true);

        // Add a row
        doc.AddRow(new[] { "Charlie", "70" });
        Assert.Equal(3, doc.RowCount);

        // Mutate a cell
        doc.SetCell(2, 1, "75");
        Assert.Equal("75", doc.GetCellValue(2, 1));

        // Remove first data row
        doc.RemoveRow(0);
        Assert.Equal(2, doc.RowCount);
        Assert.Equal("Bob", doc.GetCellValue(0, 0));
        Assert.Equal("Charlie", doc.GetCellValue(1, 0));
        Assert.Equal("75", doc.GetCellValue(1, 1));
    }

    [Fact]
    public void MutationWorkflow_ModifiedDocumentRoundtripsViaFile()
    {
        var doc = CsvDocument.Load("A,B\n1,2", hasHeaders: true);
        doc.AddRow(new[] { "3", "4" });
        doc.SetCell(0, 0, "10");
        doc.RemoveRow(1);

        var csv = doc.ToCsv();
        var reloaded = CsvDocument.Load(csv, hasHeaders: true);
        Assert.Equal(1, reloaded.RowCount);
        Assert.Equal("10", reloaded.GetCellValue(0, 0));
        Assert.Equal("2", reloaded.GetCellValue(0, 1));
    }
}
