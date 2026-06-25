// Tests for CsvReader.ReadRows(string) and CsvWriter.WriteRows(rows) static APIs.
// Sprint: FORMAT-FACTORY-CSV-STATIC-READER-WRITER-20260626
// Ledger: R121-GOVERNED-DOTNET-CSV-STATIC-READER-WRITER-001

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R121: CsvReader.ReadRows(string content) parses CSV text into raw string arrays without
/// header processing. CsvWriter.WriteRows(IEnumerable{IEnumerable{string?}}) serializes
/// rows back to CSV text. Both are stateless static operations useful for streaming
/// or low-level CSV processing.
/// </summary>
public class CsvR121StaticReaderWriterTests
{
    // ---- CsvReader.ReadRows: basic parsing ----

    [Fact]
    public void ReadRows_SingleRow_ReturnsOneItem()
    {
        var rows = CsvReader.ReadRows("Alice,90,A\n");
        Assert.Single(rows);
    }

    [Fact]
    public void ReadRows_MultipleRows_CountMatches()
    {
        var csv = "Alice,90\nBob,70\nCarol,85\n";
        var rows = CsvReader.ReadRows(csv);
        Assert.Equal(3, rows.Count);
    }

    [Fact]
    public void ReadRows_ValuesCorrect()
    {
        var rows = CsvReader.ReadRows("Alice,90,A\n");
        Assert.Equal("Alice", rows[0][0]);
        Assert.Equal("90",    rows[0][1]);
        Assert.Equal("A",     rows[0][2]);
    }

    [Fact]
    public void ReadRows_TreatsHeaderAsDataRow()
    {
        // ReadRows does NOT skip headers — it treats all rows as data
        var csv = "Name,Score\nAlice,90\n";
        var rows = CsvReader.ReadRows(csv);
        Assert.Equal(2, rows.Count); // header row is included
        Assert.Equal("Name", rows[0][0]);
    }

    [Fact]
    public void ReadRows_EmptyContent_ReturnsEmptyList()
    {
        var rows = CsvReader.ReadRows(string.Empty);
        Assert.Empty(rows);
    }

    // ---- CsvWriter.WriteRows: basic serialization ----

    [Fact]
    public void WriteRows_ProducesNonEmptyString()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "Alice", "90" } };
        var csv = CsvWriter.WriteRows(rows);
        Assert.False(string.IsNullOrWhiteSpace(csv));
    }

    [Fact]
    public void WriteRows_ContainsCommaSeparators()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "A", "B", "C" } };
        var csv = CsvWriter.WriteRows(rows);
        Assert.Contains(",", csv);
    }

    [Fact]
    public void WriteRows_ContainsValues()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "Alice", "London" } };
        var csv = CsvWriter.WriteRows(rows);
        Assert.Contains("Alice", csv);
        Assert.Contains("London", csv);
    }

    [Fact]
    public void WriteRows_MultipleRows_AllValuesPresent()
    {
        var rows = new List<IEnumerable<string?>>
        {
            new[] { "Name", "Score" },
            new[] { "Alice", "90" },
            new[] { "Bob", "75" }
        };
        var csv = CsvWriter.WriteRows(rows);
        Assert.Contains("Name", csv);
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
    }

    // ---- Round-trip: ReadRows → WriteRows ----

    [Fact]
    public void RoundTrip_ReadThenWrite_DataPreserved()
    {
        var original = "Alice,90,A\nBob,75,B\n";
        var rows = CsvReader.ReadRows(original);
        var output = CsvWriter.WriteRows(rows);

        Assert.Contains("Alice", output);
        Assert.Contains("Bob", output);
        Assert.Contains("90", output);
        Assert.Contains("75", output);
    }

    // ---- Dogfood: static reader+writer pipeline ----

    [Fact]
    public void DogfoodPipeline_ReadFilterWrite_CorrectOutput()
    {
        var csv = "Alice,92\nBob,68\nCarol,85\n";

        // Read all rows
        var allRows = CsvReader.ReadRows(csv);
        Assert.Equal(3, allRows.Count);

        // Filter in-memory: keep rows with score >= 80
        var highScoreRows = new List<IEnumerable<string?>>();
        foreach (var row in allRows)
        {
            if (row.Length > 1 && int.TryParse(row[1], out int score) && score >= 80)
                highScoreRows.Add(row);
        }

        // Write filtered rows
        var output = CsvWriter.WriteRows(highScoreRows);
        Assert.Contains("Alice", output);
        Assert.Contains("Carol", output);
        Assert.DoesNotContain("Bob", output);
    }
}
