// Tests for CsvDocument.ToCsv, IsEmpty, GetColumn(index), GetColumn(name), HasColumn.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R142

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R142: Tests for CsvDocument.ToCsv, IsEmpty, GetColumn(index), GetColumn(name), HasColumn.
/// ToCsv(): serializes document to CSV string with comma separators.
/// IsEmpty: true when Rows.Count == 0.
/// GetColumn(int): returns all cell values at column index.
/// GetColumn(string): returns all cell values for named column.
/// HasColumn(string): true if header exists with that name.
/// Covers: ToCsv contains comma characters; ToCsv includes all rows;
/// ToCsv round-trip via Load; IsEmpty for empty doc; IsEmpty false for non-empty;
/// GetColumn valid index returns values; GetColumn by name returns values;
/// GetColumn count equals row count; HasColumn existing header true;
/// HasColumn nonexistent header false; HasColumn no-headers doc false;
/// dogfood Load->GetColumn->Filter->ToCsv->Load pipeline.
/// </summary>
public class CsvR142ToCsvAndColumnTests
{
    private const string FourRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88\n" +
        "Dave,Finance,91";

    // -------------------------------------------------------------------------
    // ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_ContainsCommaCharacters()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains(",", csv);
    }

    [Fact]
    public void ToCsv_IncludesAllRows()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
        Assert.Contains("Carol", csv);
        Assert.Contains("Dave", csv);
    }

    [Fact]
    public void ToCsv_RoundTrip_PreservesRowCount()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var csv = doc.ToCsv();
        var reloaded = CsvDocument.Load(csv);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
    }

    [Fact]
    public void ToCsv_RoundTrip_PreservesCellValues()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var csv = doc.ToCsv();
        var reloaded = CsvDocument.Load(csv);
        Assert.Equal("Alice", reloaded.GetCellValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_EmptyDoc_IsTrue()
    {
        var doc = CsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_NonEmpty_IsFalse()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_HeaderOnly_NoRows_IsTrue()
    {
        // Header with no data rows
        var doc = CsvDocument.Load("Name,Score", hasHeaders: true);
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // GetColumn(int)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumn_ByIndex_ReturnsValues()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var names = doc.GetColumn(0);
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
    }

    [Fact]
    public void GetColumn_ByIndex_CountEqualsRowCount()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var col = doc.GetColumn(2); // Score column
        Assert.Equal(doc.RowCount, col.Count);
    }

    [Fact]
    public void GetColumn_ByIndex_LastColumn_ReturnsScores()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var scores = doc.GetColumn(2);
        Assert.Contains("95", scores);
        Assert.Contains("82", scores);
    }

    // -------------------------------------------------------------------------
    // GetColumn(string)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumn_ByName_ReturnsValues()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var names = doc.GetColumn("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void GetColumn_ByName_Score_ReturnsScores()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var scores = doc.GetColumn("Score");
        Assert.Contains("88", scores);
        Assert.Contains("91", scores);
    }

    // -------------------------------------------------------------------------
    // HasColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_ExistingHeader_IsTrue()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.True(doc.HasColumn("Name"));
        Assert.True(doc.HasColumn("Dept"));
        Assert.True(doc.HasColumn("Score"));
    }

    [Fact]
    public void HasColumn_NonexistentHeader_IsFalse()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.False(doc.HasColumn("Salary"));
    }

    [Fact]
    public void HasColumn_NoHeadersDoc_IsFalse()
    {
        var doc = CsvDocument.Load("Alice,Eng,95", hasHeaders: false);
        Assert.False(doc.HasColumn("Name"));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetColumn->Filter->ToCsv->Load
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnFilterToCsvLoad_Pipeline()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.False(doc.IsEmpty);
        Assert.True(doc.HasColumn("Dept"));

        // Get all department values
        var depts = doc.GetColumn("Dept");
        Assert.Contains("Eng", depts);
        Assert.Contains("Finance", depts);

        // Filter to Eng only
        var eng = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, eng.RowCount);
        Assert.False(eng.IsEmpty);

        // Serialize and reload
        var csv = eng.ToCsv();
        Assert.Contains(",", csv);
        var reloaded = CsvDocument.Load(csv);
        Assert.Equal(2, reloaded.RowCount);
        Assert.Contains("Alice", reloaded.GetColumn(0));
        Assert.Contains("Carol", reloaded.GetColumn(0));
    }
}
