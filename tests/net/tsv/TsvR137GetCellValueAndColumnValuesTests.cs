// Tests for TsvDocument.GetCellValue and GetColumnValues.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R137

using System;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R137: Tests for TsvDocument.GetCellValue and GetColumnValues.
/// GetCellValue(row, col): returns the cell string at data row/col; null for OOB.
/// GetColumnValues(colIndex): returns all values in that column across all data rows.
/// Covers: GetCellValue valid row/col returns correct string;
/// GetCellValue OOB row returns null; GetCellValue OOB col returns null;
/// GetCellValue negative row returns null; GetCellValue negative col returns null;
/// GetCellValue empty doc returns null; GetColumnValues returns all values in column;
/// GetColumnValues count matches RowCount; GetColumnValues first column correct;
/// GetColumnValues OOB colIndex returns empty; GetColumnValues after Filter;
/// dogfood Load->GetCellValue->GetColumnValues->Filter pipeline.
/// </summary>
public class TsvR137GetCellValueAndColumnValuesTests
{
    private const string ThreeRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88";

    // -------------------------------------------------------------------------
    // GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_ValidRowCol_ReturnsCorrectValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_LastRow_ReturnsCorrectValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("Carol", doc.GetCellValue(2, 0));
    }

    [Fact]
    public void GetCellValue_ThirdColumn_ReturnsScore()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("95", doc.GetCellValue(0, 2));
    }

    [Fact]
    public void GetCellValue_OobRow_ReturnsNull()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Null(doc.GetCellValue(doc.RowCount, 0));
    }

    [Fact]
    public void GetCellValue_OobCol_ReturnsNull()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Null(doc.GetCellValue(0, doc.ColumnCount));
    }

    [Fact]
    public void GetCellValue_NegativeRow_ReturnsNull()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Null(doc.GetCellValue(-1, 0));
    }

    [Fact]
    public void GetCellValue_NegativeCol_ReturnsNull()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Null(doc.GetCellValue(0, -1));
    }

    [Fact]
    public void GetCellValue_EmptyDoc_ReturnsNull()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.Null(doc.GetCellValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_FirstColumn_AllNames()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var values = doc.GetColumnValues(0);
        Assert.Contains("Alice", values);
        Assert.Contains("Bob", values);
        Assert.Contains("Carol", values);
    }

    [Fact]
    public void GetColumnValues_CountMatchesRowCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var values = doc.GetColumnValues(0);
        Assert.Equal(doc.RowCount, values.Count);
    }

    [Fact]
    public void GetColumnValues_ScoreColumn_AllScores()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var values = doc.GetColumnValues(2);
        Assert.Contains("95", values);
        Assert.Contains("82", values);
        Assert.Contains("88", values);
    }

    [Fact]
    public void GetColumnValues_OobColIndex_ReturnsEmpty()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var values = doc.GetColumnValues(doc.ColumnCount + 5);
        Assert.Empty(values);
    }

    [Fact]
    public void GetColumnValues_AfterFilter_SubsetValues()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var engOnly = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        var names = engOnly.GetColumnValues(0);
        Assert.Equal(2, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetCellValue->GetColumnValues->Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadGetCellGetColumnFilter_Pipeline()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);

        // Verify individual cells
        Assert.Equal("Bob", doc.GetCellValue(1, 0));
        Assert.Equal("Finance", doc.GetCellValue(1, 1));

        // Get all dept values
        var depts = doc.GetColumnValues(1);
        Assert.Equal(3, depts.Count);

        // Filter to Finance only
        var finance = doc.Filter(row => row.Length > 1 && row[1] == "Finance");
        Assert.Equal(1, finance.RowCount);
        Assert.Equal("Bob", finance.GetCellValue(0, 0));

        // GetColumnValues on filtered doc
        var filteredNames = finance.GetColumnValues(0);
        Assert.Single(filteredNames);
        Assert.Equal("Bob", filteredNames[0]);
    }
}
