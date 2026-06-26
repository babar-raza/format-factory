// Tests for CsvDocument.AddRow and CsvDocument.SetCell.
// Sprint: ff-sprint-s143-dotnet-deepening-20260627
// Ledger: PC-CSV-R135

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R135: Tests for CsvDocument.AddRow and CsvDocument.SetCell.
/// AddRow appends a row of values to the document. SetCell updates the value at a given row/col.
/// Covers: AddRow null values throws ArgumentNullException; AddRow empty values adds empty row;
/// AddRow single value increases RowCount by 1; AddRow multiple values stored;
/// AddRow row count increments; SetCell negative row throws ArgumentOutOfRangeException;
/// SetCell negative col throws; SetCell row>=RowCount throws; SetCell valid updates value;
/// SetCell then GetCellValue returns updated value;
/// dogfood Load->AddRow->SetCell->ToCsv->Load round-trip pipeline.
/// </summary>
public class CsvR135AddRowAndSetCellTests
{
    private static CsvDocument ThreeColumnDoc()
    {
        const string content = "name,score,active\nAlice,95,true\nBob,80,false";
        return CsvDocument.Load(content, hasHeaders: true);
    }

    // -------------------------------------------------------------------------
    // AddRow tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_NullValues_ThrowsArgumentNullException()
    {
        var doc = ThreeColumnDoc();
        Assert.Throws<ArgumentNullException>(() => doc.AddRow(null!));
    }

    [Fact]
    public void AddRow_EmptyValues_AddsEmptyRow()
    {
        var doc = ThreeColumnDoc();
        int before = doc.RowCount;
        doc.AddRow(Array.Empty<string>());
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_SingleValue_IncrementsRowCount()
    {
        var doc = ThreeColumnDoc();
        int before = doc.RowCount;
        doc.AddRow(new[] { "Carol" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_MultipleValues_StoredInLastRow()
    {
        var doc = ThreeColumnDoc();
        doc.AddRow(new[] { "Carol", "92", "true" });
        var lastRow = doc.Rows[doc.RowCount - 1];
        Assert.Equal("Carol", lastRow[0]);
        Assert.Equal("92", lastRow[1]);
        Assert.Equal("true", lastRow[2]);
    }

    [Fact]
    public void AddRow_CalledTwice_RowCountIncreasesBy2()
    {
        var doc = ThreeColumnDoc();
        int before = doc.RowCount;
        doc.AddRow(new[] { "Carol", "92", "true" });
        doc.AddRow(new[] { "Dave", "88", "true" });
        Assert.Equal(before + 2, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // SetCell tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_NegativeRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = ThreeColumnDoc();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetCell(-1, 0, "X"));
    }

    [Fact]
    public void SetCell_NegativeCol_ThrowsArgumentOutOfRangeException()
    {
        var doc = ThreeColumnDoc();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetCell(0, -1, "X"));
    }

    [Fact]
    public void SetCell_RowBeyondCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = ThreeColumnDoc();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetCell(doc.RowCount, 0, "X"));
    }

    [Fact]
    public void SetCell_ValidRowAndCol_UpdatesValue()
    {
        var doc = ThreeColumnDoc();
        doc.SetCell(0, 1, "99");
        Assert.Equal("99", doc.GetCellValue(0, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load -> AddRow -> SetCell -> ToCsv -> Load round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddRow_SetCell_ToCsv_RoundTrip()
    {
        var doc = ThreeColumnDoc();
        doc.AddRow(new[] { "Carol", "75", "true" });

        // Update Carol's score
        int carolRow = doc.RowCount - 1;
        doc.SetCell(carolRow, 1, "92");

        // Round-trip via ToCsv
        var csv = doc.ToCsv();
        var reloaded = CsvDocument.Load(csv, hasHeaders: true);

        Assert.Equal(3, reloaded.RowCount);
        Assert.Equal("Carol", reloaded.GetCellValue(2, 0));
        Assert.Equal("92", reloaded.GetCellValue(2, 1));
    }
}
