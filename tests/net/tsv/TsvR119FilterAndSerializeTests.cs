// Tests for TsvDocument.Filter, IsEmpty, ToTsv, GetCellValue mutation pipeline.
// Sprint: FORMAT-FACTORY-TSV-FILTER-SERIALIZE-20260626
// Ledger: R119-GOVERNED-DOTNET-TSV-FILTER-SERIALIZE-001

using System;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R119: TsvDocument.Filter(predicate) returns a filtered subset document. IsEmpty
/// reflects zero data rows. ToTsv() serializes back to TSV text with tab separators.
/// GetCellValue(row, col) accesses cell data by index. ColumnCount is correct for
/// multi-column documents.
/// </summary>
public class TsvR119FilterAndSerializeTests
{
    private static TsvDocument LoadTsv(string tsv) =>
        TsvDocument.Load(tsv, hasHeaders: true);

    // ---- IsEmpty ----

    [Fact]
    public void IsEmpty_NoDataRows_IsTrue()
    {
        var doc = LoadTsv("Name\tScore\n");
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_WithDataRow_IsFalse()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\n");
        Assert.False(doc.IsEmpty);
    }

    // ---- ColumnCount ----

    [Fact]
    public void ColumnCount_TwoColumns_IsTwo()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\n");
        Assert.Equal(2, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_ThreeColumns_IsThree()
    {
        var doc = LoadTsv("Name\tScore\tGrade\nAlice\t90\tA\n");
        Assert.Equal(3, doc.ColumnCount);
    }

    // ---- GetCellValue ----

    [Fact]
    public void GetCellValue_FirstRowFirstCol_ReturnsCorrectValue()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\nBob\t75\n");
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_SecondRowSecondCol_ReturnsCorrectValue()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\nBob\t75\n");
        Assert.Equal("75", doc.GetCellValue(1, 1));
    }

    // ---- Filter ----

    [Fact]
    public void Filter_MatchingRows_ReturnsSubset()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\nBob\t70\nCarol\t85\n");
        var filtered = doc.Filter(row => int.TryParse(row[1], out int v) && v >= 80);

        Assert.Equal(2, filtered.RowCount);
    }

    [Fact]
    public void Filter_NoMatchingRows_ReturnsEmpty()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\nBob\t70\n");
        var filtered = doc.Filter(row => false);

        Assert.True(filtered.IsEmpty);
    }

    [Fact]
    public void Filter_AllMatchingRows_FullCount()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\nBob\t70\n");
        var filtered = doc.Filter(row => true);

        Assert.Equal(doc.RowCount, filtered.RowCount);
    }

    // ---- ToTsv ----

    [Fact]
    public void ToTsv_ContainsTabSeparators()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\n");
        var tsv = doc.ToTsv();
        Assert.Contains("\t", tsv);
    }

    [Fact]
    public void ToTsv_ContainsHeaderNames()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\n");
        var tsv = doc.ToTsv();
        Assert.Contains("Name", tsv);
        Assert.Contains("Score", tsv);
    }

    [Fact]
    public void ToTsv_ContainsDataValues()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\n");
        var tsv = doc.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("90", tsv);
    }

    // ---- Dogfood: filter + ToTsv pipeline ----

    [Fact]
    public void DogfoodPipeline_FilterThenSerialize_ConsistentOutput()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t92\nBob\t68\nCarol\t85\nDave\t55\n");

        // Filter high scores
        var filtered = doc.Filter(row => int.TryParse(row[1], out int v) && v >= 80);
        Assert.Equal(2, filtered.RowCount);

        // Serialize
        var tsv = filtered.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Carol", tsv);
        Assert.DoesNotContain("Bob", tsv);
        Assert.DoesNotContain("Dave", tsv);

        // Tab separators present in output
        Assert.Contains("\t", tsv);
    }
}
