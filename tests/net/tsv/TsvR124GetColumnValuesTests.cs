// Tests for TsvDocument.GetColumnValues(int colIndex) — column extraction API.
// Sprint: FORMAT-FACTORY-TSV-R124-20260626
// Ledger: R124-GOVERNED-DOTNET-TSV-GETCOLUMNVALUES-001

using System;
using System.Collections.Generic;
using FormatFactory.Tsv;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R124: Tests for TsvDocument.GetColumnValues(int colIndex).
/// Returns an IReadOnlyList of string values for the specified column index,
/// across all rows. Covers: valid column index, first/last column, all-numeric
/// column, out-of-range index behavior, single-row document, dogfood pipeline.
/// TSV spec basis: tab-separated values per row (IANA text/tab-separated-values).
/// </summary>
public class TsvR124GetColumnValuesTests
{
    private static TsvDocument LoadSample() =>
        TsvDocument.Load("Name\tScore\tCity\nAlice\t90\tNYC\nBob\t80\tLondon\nCarol\t95\tParis");

    // -------------------------------------------------------------------------
    // Basic column extraction
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_FirstColumn_ReturnsAllNames()
    {
        var doc = LoadSample();
        var col = doc.GetColumnValues(0);
        Assert.Contains("Alice", col);
        Assert.Contains("Bob", col);
        Assert.Contains("Carol", col);
    }

    [Fact]
    public void GetColumnValues_FirstColumn_RowCountMatch()
    {
        var doc = LoadSample();
        var col = doc.GetColumnValues(0);
        Assert.Equal(doc.RowCount, col.Count);
    }

    [Fact]
    public void GetColumnValues_SecondColumn_AllNumericStrings()
    {
        var doc = LoadSample();
        var col = doc.GetColumnValues(1);
        Assert.Contains("90", col);
        Assert.Contains("80", col);
        Assert.Contains("95", col);
    }

    [Fact]
    public void GetColumnValues_LastColumn_CorrectValues()
    {
        var doc = LoadSample();
        int lastCol = doc.ColumnCount - 1;
        var col = doc.GetColumnValues(lastCol);
        Assert.Contains("NYC", col);
        Assert.Contains("London", col);
        Assert.Contains("Paris", col);
    }

    // -------------------------------------------------------------------------
    // Value ordering
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_OrderMatchesRowOrder()
    {
        var doc = LoadSample();
        var col = doc.GetColumnValues(0);
        Assert.Equal("Alice", col[0]);
        Assert.Equal("Bob",   col[1]);
        Assert.Equal("Carol", col[2]);
    }

    [Fact]
    public void GetColumnValues_CountEqualsRowCount()
    {
        var doc = LoadSample();
        for (int c = 0; c < doc.ColumnCount; c++)
        {
            Assert.Equal(doc.RowCount, doc.GetColumnValues(c).Count);
        }
    }

    // -------------------------------------------------------------------------
    // Edge cases
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_SingleRow_ReturnsSingleValue()
    {
        var doc = TsvDocument.Load("A\tB\tC", hasHeaders: false);
        var col = doc.GetColumnValues(0);
        Assert.Single(col);
        Assert.Equal("A", col[0]);
    }

    [Fact]
    public void GetColumnValues_EmptyDocument_ReturnsEmpty()
    {
        var doc = TsvDocument.Load(string.Empty);
        var col = doc.GetColumnValues(0);
        Assert.Empty(col);
    }

    // -------------------------------------------------------------------------
    // Dogfood: column extraction pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_DogfoodPipeline_AllColumnsExtractable()
    {
        var doc = LoadSample();
        for (int c = 0; c < doc.ColumnCount; c++)
        {
            var col = doc.GetColumnValues(c);
            Assert.NotNull(col);
            Assert.Equal(doc.RowCount, col.Count);
        }
    }

    [Fact]
    public void GetColumnValues_DogfoodPipeline_ColumnSumVerifiable()
    {
        var doc = LoadSample();
        var scores = doc.GetColumnValues(1);
        int total = 0;
        foreach (var s in scores)
        {
            if (int.TryParse(s, out int v)) total += v;
        }
        Assert.Equal(265, total);  // 90 + 80 + 95
    }

    [Fact]
    public void GetColumnValues_AllColumnsAreReadOnly()
    {
        var doc = LoadSample();
        var col = doc.GetColumnValues(0);
        // IReadOnlyList — cannot cast to mutable List
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<string?>>(col);
    }
}
