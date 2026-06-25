// Tests for CsvDocument inspection APIs: IsEmpty, GetCellValue, Filter, HasColumn
// Sprint: FORMAT-FACTORY-CSV-DOCUMENT-QUERY-20260624

using System;
using Xunit;

namespace FormatFactory.Csv.Tests;

public class CsvR117DocumentQueryTests
{
    private const string _sample = "Name,Age,City\nAlice,30,Boston\nBob,25,Denver\nCarol,35,Boston";

    private static CsvDocument Load(string content) => CsvDocument.Load(content, hasHeaders: true);

    // ---- IsEmpty ----

    [Fact]
    public void IsEmpty_NewDocumentWithNoRows_ReturnsTrue()
    {
        var doc = CsvDocument.Load("Name,Age", hasHeaders: true);
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_DocumentWithRows_ReturnsFalse()
    {
        var doc = Load(_sample);
        Assert.False(doc.IsEmpty);
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

    // ---- HasColumn ----

    [Fact]
    public void HasColumn_ExistingHeader_ReturnsTrue()
    {
        var doc = Load(_sample);
        Assert.True(doc.HasColumn("Name"));
        Assert.True(doc.HasColumn("Age"));
        Assert.True(doc.HasColumn("City"));
    }

    [Fact]
    public void HasColumn_MissingHeader_ReturnsFalse()
    {
        var doc = Load(_sample);
        Assert.False(doc.HasColumn("Zipcode"));
    }

    [Fact]
    public void HasColumn_CaseSensitive_ReturnsFalse()
    {
        var doc = Load(_sample);
        Assert.False(doc.HasColumn("name")); // lower case
    }

    [Fact]
    public void HasColumn_NoHeaders_ReturnsFalse()
    {
        var doc = CsvDocument.Load("Alice,30\nBob,25", hasHeaders: false);
        Assert.False(doc.HasColumn("Name"));
    }
}
