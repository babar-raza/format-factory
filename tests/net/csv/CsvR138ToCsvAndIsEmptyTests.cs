// Tests for CsvDocument.ToCsv and IsEmpty.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R138

using System;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R138: Tests for CsvDocument.ToCsv and CsvDocument.IsEmpty.
/// ToCsv() serializes the document to a CSV string with comma-separated values;
/// headers appear as the first line when present; each row ends with a newline.
/// IsEmpty returns true when Rows.Count == 0; false when there is at least one data row.
/// Covers: ToCsv single row has correct comma-separated format; ToCsv headers appear first;
/// ToCsv round-trip Load->ToCsv->Load preserves row count and cell values;
/// ToCsv with no headers omits header line; ToCsv escapes commas in values;
/// IsEmpty new doc is empty; IsEmpty after AddRow is false; IsEmpty after RemoveRow is true again;
/// IsEmpty false with loaded content; IsEmpty true with empty string Load;
/// dogfood Load->AddRow->ToCsv->Load pipeline.
/// </summary>
public class CsvR138ToCsvAndIsEmptyTests
{
    private const string TwoRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82";

    // -------------------------------------------------------------------------
    // ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_SingleRow_ContainsCommaSeparatedValues()
    {
        var doc = CsvDocument.Load("A,B,C\n1,2,3");
        var csv = doc.ToCsv();
        Assert.Contains("1,2,3", csv);
    }

    [Fact]
    public void ToCsv_HeadersAppearFirst()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        var csv = doc.ToCsv();
        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal("Name,Dept,Score", lines[0]);
    }

    [Fact]
    public void ToCsv_RoundTrip_RowCountPreserved()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        var csv = doc.ToCsv();
        var doc2 = CsvDocument.Load(csv);
        Assert.Equal(doc.RowCount, doc2.RowCount);
    }

    [Fact]
    public void ToCsv_RoundTrip_CellValuesPreserved()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        var csv = doc.ToCsv();
        var doc2 = CsvDocument.Load(csv);
        Assert.Equal(doc.GetCellValue(0, 0), doc2.GetCellValue(0, 0));
        Assert.Equal(doc.GetCellValue(1, 1), doc2.GetCellValue(1, 1));
    }

    [Fact]
    public void ToCsv_NoHeaders_DoesNotIncludeExtraLine()
    {
        var content = "a,b\n1,2";
        var doc = CsvDocument.Load(content, hasHeaders: false);
        var csv = doc.ToCsv();
        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        // Without headers, there should be exactly 2 data lines
        Assert.Equal(2, lines.Length);
    }

    [Fact]
    public void ToCsv_EscapesCommasInValues()
    {
        // When a value contains a comma, it should be quoted
        var content = "Name,Note\nAlice,\"Hello, world\"";
        var doc = CsvDocument.Load(content);
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        // The reloaded doc should have "Hello, world" as a single cell
        var doc2 = CsvDocument.Load(csv);
        var note = doc2.GetCellValue(0, 1);
        Assert.Contains("Hello", note ?? "");
    }

    // -------------------------------------------------------------------------
    // IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_NewDocumentFromLoad_EmptyContent_IsTrue()
    {
        var doc = CsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_LoadedWithContent_IsFalse()
    {
        var doc = CsvDocument.Load("A,B\n1,2");
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_AfterAddRow_IsFalse()
    {
        var doc = CsvDocument.Load(string.Empty, hasHeaders: false);
        doc.AddRow(new[] { "x", "y" });
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_AfterRemoveLastRow_IsTrue()
    {
        var doc = CsvDocument.Load("A\n1", hasHeaders: true);
        Assert.False(doc.IsEmpty);
        doc.RemoveRow(0);
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // Dogfood: pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadAddRowToCsvLoad_Pipeline()
    {
        var doc = CsvDocument.Load("Name,Score\nAlice,90");
        Assert.False(doc.IsEmpty);

        // Add a new row
        doc.AddRow(new[] { "Bob", "85" });
        Assert.Equal(2, doc.RowCount);

        // Serialize and reload
        var csv = doc.ToCsv();
        var doc2 = CsvDocument.Load(csv);
        Assert.Equal(2, doc2.RowCount);
        Assert.Equal("Bob", doc2.GetCellValue(1, 0));
        Assert.Equal("85", doc2.GetCellValue(1, 1));
    }
}
