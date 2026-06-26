// Tests for CsvDocument.Headers, ColumnCount, HasHeaders deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R145

using System;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R145: Tests for CsvDocument.Headers, ColumnCount, HasHeaders deeper coverage.
/// Headers: the header row as string array, or null when no headers.
/// ColumnCount: inferred from headers or first row.
/// HasHeaders: true when Headers != null.
/// Covers: Headers contains expected names; Headers null without hasHeaders;
/// ColumnCount from headers; ColumnCount from first row; ColumnCount empty doc is 0;
/// HasHeaders true with headers param; HasHeaders false without headers param;
/// HasHeaders false empty doc; Load with hasHeaders=false has null Headers;
/// Load single-row (header-only) has 0 rows; GetColumn names match headers;
/// dogfood Load->Headers->ColumnCount->GetColumn->IsEmpty pipeline.
/// </summary>
public class CsvR145HeaderAndColumnCountTests
{
    private const string FourColCsv =
        "ID,Name,Dept,Score\n" +
        "1,Alice,Eng,95\n" +
        "2,Bob,Finance,82";

    // -------------------------------------------------------------------------
    // Headers
    // -------------------------------------------------------------------------

    [Fact]
    public void Headers_WithHeaders_ContainsExpectedNames()
    {
        var doc = CsvDocument.Load(FourColCsv);
        Assert.Contains("ID", doc.Headers!);
        Assert.Contains("Name", doc.Headers!);
        Assert.Contains("Dept", doc.Headers!);
        Assert.Contains("Score", doc.Headers!);
    }

    [Fact]
    public void Headers_WithoutHeaders_IsNull()
    {
        var doc = CsvDocument.Load("Alice,Eng,95", hasHeaders: false);
        Assert.Null(doc.Headers);
    }

    [Fact]
    public void Headers_HeaderRowNotInRows()
    {
        var doc = CsvDocument.Load(FourColCsv);
        // Headers should NOT appear in Rows (they're separate)
        Assert.Equal(2, doc.RowCount);
        Assert.DoesNotContain(doc.Headers!, h => doc.Rows.Exists(r => r.Length > 0 && r[0] == "ID"));
    }

    [Fact]
    public void Headers_LengthMatchesColumnCount()
    {
        var doc = CsvDocument.Load(FourColCsv);
        Assert.Equal(doc.ColumnCount, doc.Headers!.Length);
    }

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_WithHeaders_FromHeaderLength()
    {
        var doc = CsvDocument.Load(FourColCsv);
        Assert.Equal(4, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_WithoutHeaders_FromFirstRow()
    {
        var doc = CsvDocument.Load("A,B,C\n1,2,3", hasHeaders: false);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_EmptyDoc_IsZero()
    {
        var doc = CsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.Equal(0, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_SingleColumn_IsOne()
    {
        var doc = CsvDocument.Load("Value\nA\nB\nC");
        Assert.Equal(1, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // HasHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void HasHeaders_WithHeaders_IsTrue()
    {
        var doc = CsvDocument.Load(FourColCsv, hasHeaders: true);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void HasHeaders_WithoutHeaders_IsFalse()
    {
        var doc = CsvDocument.Load("A,B\n1,2", hasHeaders: false);
        Assert.False(doc.HasHeaders);
    }

    [Fact]
    public void HasHeaders_EmptyDoc_IsFalse()
    {
        var doc = CsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.False(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // Load edge cases
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_HeaderOnly_ZeroRows()
    {
        var doc = CsvDocument.Load("Name,Score", hasHeaders: true);
        Assert.Equal(0, doc.RowCount);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void Load_SingleDataRow_OneRow()
    {
        var doc = CsvDocument.Load("Name,Score\nAlice,95");
        Assert.Equal(1, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Headers->ColumnCount->GetColumn->IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_HeadersColumnCountGetColumnIsEmpty_Pipeline()
    {
        var doc = CsvDocument.Load(FourColCsv);

        // IsEmpty
        Assert.False(doc.IsEmpty);

        // Headers
        Assert.True(doc.HasHeaders);
        Assert.Equal(4, doc.Headers!.Length);

        // ColumnCount
        Assert.Equal(4, doc.ColumnCount);

        // GetColumn by name
        var names = doc.GetColumn("Name");
        Assert.Equal(2, names.Count);
        Assert.Contains("Alice", names);

        // GetColumn by index
        var ids = doc.GetColumn(0);
        Assert.Contains("1", ids);
        Assert.Contains("2", ids);

        // HasColumn
        Assert.True(doc.HasColumn("ID"));
        Assert.True(doc.HasColumn("Score"));
        Assert.False(doc.HasColumn("Salary"));
    }
}
