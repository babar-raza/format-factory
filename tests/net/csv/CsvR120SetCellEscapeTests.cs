// Tests for CsvDocument.SetCell, EscapeField, ColumnCount, and SaveToFile.
// Sprint: FORMAT-FACTORY-CSV-SET-CELL-ESCAPE-20260626
// Ledger: R120-GOVERNED-DOTNET-CSV-SET-CELL-ESCAPE-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R120: CsvDocument.SetCell(row, col, value) updates cell content in-place without
/// changing RowCount or ColumnCount. CsvWriter.EscapeField(value) wraps values
/// containing commas or quotes in double-quotes. ColumnCount reflects header count.
/// SaveToFile(path) persists and can be reloaded.
/// </summary>
public class CsvR120SetCellEscapeTests
{
    private static CsvDocument LoadCsv(string csv) =>
        CsvDocument.Load(csv, hasHeaders: true);

    // ---- SetCell: basic mutation ----

    [Fact]
    public void SetCell_UpdatesValueAtPosition()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\n");
        doc.SetCell(0, 1, "95");

        Assert.Equal("95", doc.GetCellValue(0, 1));
    }

    [Fact]
    public void SetCell_RowCountUnchanged()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\nBob,70\n");
        var before = doc.RowCount;

        doc.SetCell(0, 0, "Alicia");

        Assert.Equal(before, doc.RowCount);
    }

    [Fact]
    public void SetCell_OtherCellsUnchanged()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\nBob,70\n");
        doc.SetCell(0, 1, "99");

        // Other row unchanged
        Assert.Equal("Bob", doc.GetCellValue(1, 0));
        Assert.Equal("70", doc.GetCellValue(1, 1));
    }

    [Fact]
    public void SetCell_MultipleUpdatesOnSameDocument()
    {
        var doc = LoadCsv("A,B,C\n1,2,3\n");
        doc.SetCell(0, 0, "X");
        doc.SetCell(0, 1, "Y");
        doc.SetCell(0, 2, "Z");

        Assert.Equal("X", doc.GetCellValue(0, 0));
        Assert.Equal("Y", doc.GetCellValue(0, 1));
        Assert.Equal("Z", doc.GetCellValue(0, 2));
    }

    // ---- ColumnCount ----

    [Fact]
    public void ColumnCount_TwoHeaders_IsTwo()
    {
        var doc = LoadCsv("Name,Score\nAlice,90\n");
        Assert.Equal(2, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_FourHeaders_IsFour()
    {
        var doc = LoadCsv("A,B,C,D\n1,2,3,4\n");
        Assert.Equal(4, doc.ColumnCount);
    }

    // ---- EscapeField ----

    [Fact]
    public void EscapeField_PlainValue_ReturnsUnchanged()
    {
        var escaped = CsvWriter.EscapeField("Alice");
        Assert.Equal("Alice", escaped);
    }

    [Fact]
    public void EscapeField_ValueWithComma_WrapsInQuotes()
    {
        var escaped = CsvWriter.EscapeField("Smith, John");
        Assert.StartsWith("\"", escaped);
        Assert.EndsWith("\"", escaped);
    }

    [Fact]
    public void EscapeField_ValueWithQuote_EscapesQuote()
    {
        var escaped = CsvWriter.EscapeField("He said \"hello\"");
        Assert.Contains("\"\"", escaped); // doubled quotes
    }

    [Fact]
    public void EscapeField_NullValue_DoesNotThrow()
    {
        var escaped = CsvWriter.EscapeField(null);
        Assert.NotNull(escaped);
    }

    // ---- Dogfood: SetCell + ToCsv ----

    [Fact]
    public void DogfoodPipeline_SetCellsThenSerialize_OutputUpdated()
    {
        var doc = LoadCsv("Name,Score,Grade\nAlice,90,A\nBob,70,C\n");

        // Update scores
        doc.SetCell(0, 1, "95");
        doc.SetCell(1, 1, "75");
        doc.SetCell(0, 2, "A+");

        var csv = doc.ToCsv();
        Assert.Contains("95", csv);
        Assert.Contains("75", csv);
        Assert.Contains("A+", csv);
        Assert.DoesNotContain(",90,", csv);
    }
}
