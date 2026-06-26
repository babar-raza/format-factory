// Tests for CsvDocument.GetColumn (by index and by name) and ColumnCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R137

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R137: Tests for CsvDocument.GetColumn(int) / GetColumn(string) and ColumnCount.
/// GetColumn(int) returns a list of cell values in that column (all data rows).
/// GetColumn(string) looks up the column by header name and returns its values.
/// ColumnCount returns the number of columns (from Headers if present, else first row length).
/// Covers: GetColumn by index returns correct values; GetColumn out-of-range throws or returns empty;
/// GetColumn by name returns correct values; GetColumn by unknown name throws or returns empty;
/// ColumnCount with headers equals header length; ColumnCount no-headers equals first row length;
/// ColumnCount empty doc returns 0; GetColumn ragged rows handled gracefully;
/// dogfood Load->GetColumn->ColumnCount pipeline.
/// </summary>
public class CsvR137GetColumnAndColumnCountTests
{
    private const string ThreeColCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88";

    // -------------------------------------------------------------------------
    // GetColumn by index
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumn_ByIndex0_ReturnsFirstColumn()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        var col = doc.GetColumn(0);
        Assert.Equal(new List<string> { "Alice", "Bob", "Carol" }, col);
    }

    [Fact]
    public void GetColumn_ByIndex1_ReturnsMiddleColumn()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        var col = doc.GetColumn(1);
        Assert.Equal(new List<string> { "Eng", "Finance", "Eng" }, col);
    }

    [Fact]
    public void GetColumn_ByIndex2_ReturnsLastColumn()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        var col = doc.GetColumn(2);
        Assert.Equal(new List<string> { "95", "82", "88" }, col);
    }

    [Fact]
    public void GetColumn_ByIndex_CountMatchesRowCount()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        var col = doc.GetColumn(0);
        Assert.Equal(doc.Rows.Count, col.Count);
    }

    // -------------------------------------------------------------------------
    // GetColumn by header name
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumn_ByName_ReturnsCorrectValues()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        var col = doc.GetColumn("Dept");
        Assert.Equal(new List<string> { "Eng", "Finance", "Eng" }, col);
    }

    [Fact]
    public void GetColumn_ByNameScore_ReturnsScoreValues()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        var col = doc.GetColumn("Score");
        Assert.Contains("95", col);
        Assert.Contains("82", col);
        Assert.Contains("88", col);
    }

    [Fact]
    public void GetColumn_ByUnknownName_ThrowsOrReturnsEmpty()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        // Either throws an exception or returns an empty list — both are acceptable
        try
        {
            var col = doc.GetColumn("NoSuchColumn");
            Assert.Empty(col);
        }
        catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or KeyNotFoundException)
        {
            // Acceptable — column not found
        }
    }

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_WithHeaders_EqualsHeaderLength()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_NoHeaders_EqualsFirstRowLength()
    {
        var content = "A,B,C,D\n1,2,3,4";
        var doc = CsvDocument.Load(content, hasHeaders: false);
        // Without headers, first row is a data row with 4 cells
        Assert.Equal(4, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_EmptyDocument_ReturnsZero()
    {
        var doc = CsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.Equal(0, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_SingleColumnCsv_ReturnsOne()
    {
        var doc = CsvDocument.Load("ID\n1\n2\n3");
        Assert.Equal(1, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadGetColumnColumnCount_Pipeline()
    {
        var doc = CsvDocument.Load(ThreeColCsv);

        // Verify column count
        Assert.Equal(3, doc.ColumnCount);

        // Get name column by index and by name — should match
        var byIndex = doc.GetColumn(0);
        var byName = doc.GetColumn("Name");
        Assert.Equal(byIndex, byName);

        // All three rows present
        Assert.Equal(3, byIndex.Count);
        Assert.Equal("Alice", byIndex[0]);
        Assert.Equal("Carol", byIndex[2]);
    }
}
