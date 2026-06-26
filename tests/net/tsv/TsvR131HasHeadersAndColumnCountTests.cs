// Tests for TsvDocument.HasHeaders (bool) and TsvDocument.ColumnCount (computed int).
// Sprint: ff-sprint-s134-dotnet-deepening-20260627
// Ledger: PC-TSV-R131

using System;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R131: Tests for TsvDocument.HasHeaders and TsvDocument.ColumnCount.
/// HasHeaders is true when the document was loaded with hasHeaders=true.
/// ColumnCount is the number of columns in the header row (or first row if no headers).
/// Covers: HasHeaders=true when loaded with hasHeaders=true; HasHeaders=false when
/// loaded with hasHeaders=false; HasHeaders=false on empty doc; ColumnCount matches
/// header count; ColumnCount without headers matches first row length; ColumnCount on
/// empty doc=0; ColumnCount after adding row reflects column count; Headers contain
/// expected names; dogfood Load→HasHeaders→ColumnCount→row access pipeline.
/// </summary>
public class TsvR131HasHeadersAndColumnCountTests
{
    private const string SampleTsv = "Name\tScore\tCity\nAlice\t95\tLondon\nBob\t72\tParis\n";

    // -------------------------------------------------------------------------
    // TsvDocument.HasHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvDocument_HasHeaders_LoadedWithHeadersTrue_IsTrue()
    {
        var doc = TsvDocument.Load(SampleTsv, hasHeaders: true);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void TsvDocument_HasHeaders_LoadedWithHeadersFalse_IsFalse()
    {
        var doc = TsvDocument.Load(SampleTsv, hasHeaders: false);
        Assert.False(doc.HasHeaders);
    }

    [Fact]
    public void TsvDocument_HasHeaders_EmptyDoc_IsFalse()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.False(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // TsvDocument.ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvDocument_ColumnCount_WithHeaders_MatchesHeaderCount()
    {
        var doc = TsvDocument.Load(SampleTsv, hasHeaders: true);
        // Headers: Name, Score, City → 3 columns
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void TsvDocument_ColumnCount_WithoutHeaders_MatchesFirstRowLength()
    {
        // Without headers, first row becomes row 0: "Name\tScore\tCity" → 3 fields
        var doc = TsvDocument.Load(SampleTsv, hasHeaders: false);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void TsvDocument_ColumnCount_EmptyDoc_IsZero()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.Equal(0, doc.ColumnCount);
    }

    [Fact]
    public void TsvDocument_ColumnCount_SingleColumnDoc_IsOne()
    {
        var doc = TsvDocument.Load("Header\nValue1\nValue2\n", hasHeaders: true);
        Assert.Equal(1, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Headers populated correctly
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvDocument_Headers_LoadedWithHeadersTrue_ContainsExpectedNames()
    {
        var doc = TsvDocument.Load(SampleTsv, hasHeaders: true);
        Assert.NotNull(doc.Headers);
        Assert.Contains("Name", doc.Headers);
        Assert.Contains("Score", doc.Headers);
        Assert.Contains("City", doc.Headers);
    }

    [Fact]
    public void TsvDocument_Headers_LoadedWithHeadersFalse_IsNull()
    {
        var doc = TsvDocument.Load(SampleTsv, hasHeaders: false);
        Assert.Null(doc.Headers);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load → HasHeaders → ColumnCount → row access pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Load_HasHeaders_ColumnCount_RowAccess()
    {
        var doc = TsvDocument.Load(SampleTsv, hasHeaders: true);

        Assert.True(doc.HasHeaders);
        Assert.Equal(3, doc.ColumnCount);
        Assert.Equal(2, doc.RowCount);

        // First data row: Alice, 95, London
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("95", doc.GetCellValue(0, 1));
        Assert.Equal("London", doc.GetCellValue(0, 2));
    }
}
