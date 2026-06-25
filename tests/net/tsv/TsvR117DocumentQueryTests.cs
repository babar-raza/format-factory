// Tests for TsvDocument inspection APIs: IsEmpty, GetCellValue, GetColumnValues, Filter
// Sprint: FORMAT-FACTORY-TSV-DOCUMENT-QUERY-20260624

using System;
using Xunit;

namespace FormatFactory.Tsv.Tests;

public class TsvR117DocumentQueryTests
{
    private const string _sample = "Name\tAge\tCity\nAlice\t30\tBoston\nBob\t25\tDenver\nCarol\t35\tBoston";

    private static TsvDocument Load(string content) => TsvDocument.Load(content, hasHeaders: true);

    // ---- IsEmpty ----

    [Fact]
    public void IsEmpty_EmptyDocument_ReturnsTrue()
    {
        var doc = new TsvDocument();
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_NonEmptyDocument_ReturnsFalse()
    {
        var doc = Load(_sample);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_DocumentWithOnlyHeaders_ReturnsTrue()
    {
        var doc = TsvDocument.Load("Name\tAge", hasHeaders: true);
        Assert.True(doc.IsEmpty);
    }

    // ---- GetCellValue ----

    [Fact]
    public void GetCellValue_ValidCoords_ReturnsValue()
    {
        var doc = Load(_sample);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("25", doc.GetCellValue(1, 1));
        Assert.Equal("Boston", doc.GetCellValue(2, 2));
    }

    [Fact]
    public void GetCellValue_OutOfBoundsRow_ReturnsNull()
    {
        var doc = Load(_sample);
        Assert.Null(doc.GetCellValue(99, 0));
    }

    [Fact]
    public void GetCellValue_OutOfBoundsCol_ReturnsNull()
    {
        var doc = Load(_sample);
        Assert.Null(doc.GetCellValue(0, 99));
    }

    [Fact]
    public void GetCellValue_NegativeRow_ReturnsNull()
    {
        var doc = Load(_sample);
        Assert.Null(doc.GetCellValue(-1, 0));
    }

    // ---- GetColumnValues ----

    [Fact]
    public void GetColumnValues_FirstColumn_ReturnsAllNames()
    {
        var doc = Load(_sample);
        var names = doc.GetColumnValues(0);
        Assert.Equal(3, names.Count);
        Assert.Equal("Alice", names[0]);
        Assert.Equal("Bob", names[1]);
        Assert.Equal("Carol", names[2]);
    }

    [Fact]
    public void GetColumnValues_ShortRowYieldsNull()
    {
        var doc = TsvDocument.Load("A\tB\n1\t2\n3", hasHeaders: true);
        // Row 2 has only 1 column; col 1 should be null
        var vals = doc.GetColumnValues(1);
        Assert.Equal(2, vals.Count);
        Assert.Equal("2", vals[0]);
        Assert.Null(vals[1]);
    }

    [Fact]
    public void GetColumnValues_NegativeIndexThrows()
    {
        var doc = Load(_sample);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetColumnValues(-1));
    }

    // ---- Filter ----

    [Fact]
    public void Filter_ByColumnValue_ReturnsMatchingRows()
    {
        var doc = Load(_sample);
        var filtered = doc.Filter(r => r.Length > 2 && r[2] == "Boston");
        Assert.Equal(2, filtered.RowCount);
    }

    [Fact]
    public void Filter_NoMatchReturnsEmptyDocument()
    {
        var doc = Load(_sample);
        var filtered = doc.Filter(r => r.Length > 0 && r[0] == "Zara");
        Assert.True(filtered.IsEmpty);
    }

    [Fact]
    public void Filter_PreservesHeaders()
    {
        var doc = Load(_sample);
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.Headers, filtered.Headers);
    }

    [Fact]
    public void Filter_AllMatchReturnsSameCount()
    {
        var doc = Load(_sample);
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.RowCount, filtered.RowCount);
    }

    [Fact]
    public void Filter_NullPredicateThrows()
    {
        var doc = Load(_sample);
        Assert.Throws<ArgumentNullException>(() => doc.Filter(null!));
    }
}
