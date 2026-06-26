// Tests for CsvWriter.WriteRows and CsvDocument.ToCsv.
// Sprint: ff-sprint-s137-dotnet-deepening-20260627
// Ledger: PC-CSV-R133

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R133: Tests for CsvWriter.WriteRows (static) and CsvDocument.ToCsv (instance).
/// CsvWriter.WriteRows serializes row collections to CSV with LF line endings.
/// Null rows argument throws ArgumentNullException.
/// CsvDocument.ToCsv round-trips the document content including headers when present.
/// Covers: WriteRows null throws; empty rows=empty string; single row one field;
/// single row multiple fields; fields with comma are quoted; null field=empty;
/// CsvDocument.ToCsv empty=empty; with headers row-counts match;
/// with data values appear in output;
/// dogfood CsvDocument.Load->Filter->ToCsv->Load round-trip.
/// </summary>
public class CsvR133WriterRowsAndToCsvTests
{
    // -------------------------------------------------------------------------
    // CsvWriter.WriteRows null guard
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRows_NullRows_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => CsvWriter.WriteRows(null!));
    }

    // -------------------------------------------------------------------------
    // CsvWriter.WriteRows basic behavior
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRows_EmptyRows_ReturnsEmptyString()
    {
        var result = CsvWriter.WriteRows(new List<IEnumerable<string?>>());
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void WriteRows_SingleRowOneField_ReturnsSingleLine()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "hello" } };
        var result = CsvWriter.WriteRows(rows);
        Assert.Contains("hello", result);
    }

    [Fact]
    public void WriteRows_SingleRowMultipleFields_FieldsSeparatedByComma()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "Alice", "95", "true" } };
        var result = CsvWriter.WriteRows(rows);
        Assert.Equal("Alice,95,true\n", result);
    }

    [Fact]
    public void WriteRows_FieldContainsComma_FieldIsQuoted()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "Smith, John", "42" } };
        var result = CsvWriter.WriteRows(rows);
        Assert.Contains("\"Smith, John\"", result);
    }

    [Fact]
    public void WriteRows_NullField_TreatedAsEmpty()
    {
        var rows = new List<IEnumerable<string?>> { new string?[] { "Alice", null, "95" } };
        var result = CsvWriter.WriteRows(rows);
        Assert.Equal("Alice,,95\n", result);
    }

    // -------------------------------------------------------------------------
    // CsvDocument.ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_EmptyDocument_ReturnsOnlyHeaders()
    {
        var doc = CsvDocument.Load("Name,Score", hasHeaders: true);
        var csv = doc.ToCsv();
        Assert.Contains("Name", csv);
        Assert.Contains("Score", csv);
    }

    [Fact]
    public void ToCsv_WithDataRows_ContainsAllValues()
    {
        const string input = "Name,Score\nAlice,95\nBob,72";
        var doc = CsvDocument.Load(input, hasHeaders: true);
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
        Assert.Contains("95", csv);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load -> Filter -> ToCsv -> Load round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_LoadFilterToCsvLoad_RoundTripRowCount()
    {
        const string input = "Name,Score\nAlice,95\nBob,72\nCarol,88";
        var doc = CsvDocument.Load(input, hasHeaders: true);

        // Filter to score > 80 (Alice=95, Carol=88)
        var filtered = doc.Filter(row => row.Length > 1 &&
            int.TryParse(row[1], out var s) && s > 80);

        var csv = filtered.ToCsv();
        var reloaded = CsvDocument.Load(csv, hasHeaders: true);

        Assert.Equal(2, reloaded.RowCount);
        Assert.Equal("Alice", reloaded.GetCellValue(0, 0));
        Assert.Equal("Carol", reloaded.GetCellValue(1, 0));
    }
}
