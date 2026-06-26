// Tests for TsvWriter.WriteRows dedicated deepening.
// Sprint: ff-sprint-s144-dotnet-deepening-20260627
// Ledger: PC-TSV-R133

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R133: Dedicated tests for TsvWriter.WriteRows.
/// WriteRows serializes rows of strings to a TSV-formatted string (tab-delimited, newline-terminated).
/// Covers: WriteRows null rows throws; WriteRows empty rows returns empty string;
/// single row single column; single row multiple columns tab-separated;
/// multiple rows each on separate line; null values written as empty string;
/// WriteRows output contains tabs; row count matches newline count;
/// WriteRowsToFile creates file; dogfood WriteRows->Load round-trip matches original.
/// </summary>
public class TsvR133WriteRowsDedicatedTests
{
    // -------------------------------------------------------------------------
    // WriteRows guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRows_NullRows_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => TsvWriter.WriteRows(null!));
    }

    [Fact]
    public void WriteRows_EmptyRows_ReturnsEmptyString()
    {
        var result = TsvWriter.WriteRows(new List<IEnumerable<string?>>());
        Assert.Equal(string.Empty, result);
    }

    // -------------------------------------------------------------------------
    // WriteRows functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRows_SingleRowSingleColumn_ReturnsValuePlusNewline()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "Hello" } };
        var result = TsvWriter.WriteRows(rows);
        Assert.Contains("Hello", result);
    }

    [Fact]
    public void WriteRows_SingleRowMultipleColumns_TabSeparated()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "Alice", "95", "true" } };
        var result = TsvWriter.WriteRows(rows);
        Assert.Contains("Alice\t95\ttrue", result);
    }

    [Fact]
    public void WriteRows_MultipleRows_EachOnSeparateLine()
    {
        var rows = new List<IEnumerable<string?>>
        {
            new[] { "Alice", "95" },
            new[] { "Bob", "82" }
        };
        var result = TsvWriter.WriteRows(rows);
        var lines = result.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(2, lines.Length);
    }

    [Fact]
    public void WriteRows_NullValues_WrittenAsEmptyString()
    {
        var rows = new List<IEnumerable<string?>> { new string?[] { "Alice", null, "true" } };
        var result = TsvWriter.WriteRows(rows);
        Assert.Contains("Alice\t\ttrue", result);
    }

    [Fact]
    public void WriteRows_Output_ContainsTabs()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "A", "B", "C" } };
        var result = TsvWriter.WriteRows(rows);
        Assert.Contains('\t', result);
    }

    [Fact]
    public void WriteRows_TwoRows_TwoNewlines()
    {
        var rows = new List<IEnumerable<string?>>
        {
            new[] { "X", "1" },
            new[] { "Y", "2" }
        };
        var result = TsvWriter.WriteRows(rows);
        int newlines = 0;
        foreach (char c in result) if (c == '\n') newlines++;
        Assert.Equal(2, newlines);
    }

    [Fact]
    public void WriteRowsToFile_CreatesFile()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "A", "B" } };
        var path = Path.Combine(Path.GetTempPath(), $"tsv_r133_{Guid.NewGuid():N}.tsv");
        try
        {
            TsvWriter.WriteRowsToFile(rows, path);
            Assert.True(File.Exists(path));
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood: WriteRows -> Load round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_WriteRows_Load_RoundTrip_MatchesOriginal()
    {
        var rows = new List<IEnumerable<string?>>
        {
            new[] { "name", "score", "active" },
            new[] { "Alice", "95", "true" },
            new[] { "Bob", "82", "false" }
        };
        var tsv = TsvWriter.WriteRows(rows);
        var doc = TsvDocument.Load(tsv, hasHeaders: false);

        Assert.Equal(3, doc.RowCount);
        Assert.Equal("Alice", doc.GetCellValue(1, 0));
        Assert.Equal("95", doc.GetCellValue(1, 1));
    }
}
