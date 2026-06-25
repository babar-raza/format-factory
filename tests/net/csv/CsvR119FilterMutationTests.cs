// Tests for CsvDocument.Filter, HasColumn, IsEmpty, AddRow, RemoveRow, ToCsv.
// Sprint: FORMAT-FACTORY-CSV-FILTER-MUTATION-20260626
// Ledger: R119-GOVERNED-DOTNET-CSV-FILTER-MUTATION-001

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R119: CsvDocument.Filter(predicate) returns a filtered document with matching rows.
/// HasColumn(name) checks header existence. IsEmpty reflects zero rows. AddRow appends
/// a new data row. RemoveRow deletes by index. ToCsv serializes back to CSV text.
/// </summary>
public class CsvR119FilterMutationTests
{
    private static CsvDocument LoadCsv(string csv) =>
        CsvDocument.Load(csv, hasHeaders: true);

    // ---- IsEmpty ----

    [Fact]
    public void IsEmpty_NoDataRows_IsTrue()
    {
        var doc = LoadCsv("Name,Score\n");
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_WithDataRow_IsFalse()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\n");
        Assert.False(doc.IsEmpty);
    }

    // ---- HasColumn ----

    [Fact]
    public void HasColumn_ExistingHeader_IsTrue()
    {
        var doc = LoadCsv("Name,Score,Grade\nAlice,90,A\n");
        Assert.True(doc.HasColumn("Score"));
    }

    [Fact]
    public void HasColumn_MissingHeader_IsFalse()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\n");
        Assert.False(doc.HasColumn("Department"));
    }

    // ---- Filter ----

    [Fact]
    public void Filter_MatchingRows_ReturnsSubset()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\nBob,70\nCarol,85\n");
        var filtered = doc.Filter(row => int.TryParse(row[1], out int v) && v >= 80);

        Assert.Equal(2, filtered.RowCount);
    }

    [Fact]
    public void Filter_NoMatchingRows_ReturnsEmptyDocument()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\nBob,70\n");
        var filtered = doc.Filter(row => false);

        Assert.True(filtered.IsEmpty);
    }

    [Fact]
    public void Filter_AllMatchingRows_SameCount()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\nBob,70\n");
        var filtered = doc.Filter(row => true);

        Assert.Equal(doc.RowCount, filtered.RowCount);
    }

    // ---- AddRow ----

    [Fact]
    public void AddRow_IncreasesRowCount()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\n");
        var before = doc.RowCount;

        doc.AddRow(new[] { "Dave", "88" });

        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_NewRowDataAccessible()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\n");
        doc.AddRow(new[] { "Eve", "95" });

        Assert.Equal("Eve", doc.GetCellValue(1, 0));
        Assert.Equal("95", doc.GetCellValue(1, 1));
    }

    // ---- RemoveRow ----

    [Fact]
    public void RemoveRow_DecreasesRowCount()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\nBob,70\n");
        var before = doc.RowCount;

        doc.RemoveRow(0);

        Assert.Equal(before - 1, doc.RowCount);
    }

    // ---- ToCsv ----

    [Fact]
    public void ToCsv_ContainsHeaderRow()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\n");
        var csv = doc.ToCsv();
        Assert.Contains("Name", csv);
        Assert.Contains("Score", csv);
    }

    [Fact]
    public void ToCsv_ContainsDataValues()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\n");
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("90", csv);
    }

    // ---- Dogfood: filter + mutate + serialize ----

    [Fact]
    public void DogfoodPipeline_FilterAddToCsv_ConsistentResult()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\nBob,70\nCarol,85\n");

        // Filter to high scores
        var filtered = doc.Filter(row => int.TryParse(row[1], out int v) && v >= 80);
        Assert.Equal(2, filtered.RowCount);

        // Add a new row to filtered
        filtered.AddRow(new[] { "Dana", "92" });
        Assert.Equal(3, filtered.RowCount);

        // Serialize and verify content
        var csv = filtered.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Carol", csv);
        Assert.Contains("Dana", csv);
        Assert.DoesNotContain("Bob", csv);
    }
}
