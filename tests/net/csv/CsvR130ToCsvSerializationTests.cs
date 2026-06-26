// Tests for CsvDocument.ToCsv() serialization and GetCellValue(row, col) cell access.
// Sprint: FORMAT-FACTORY-CSV-R130-20260627
// Ledger: R130-GOVERNED-DOTNET-CSV-TOCSV-SERIALIZATION-001

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R130: Tests for CsvDocument.ToCsv() round-trip serialization and
/// CsvDocument.GetCellValue(int row, int col) cell access with edge-case guards.
/// ToCsv() re-serializes the in-memory CSV state: headers appear on line 0
/// when HasHeaders=true; rows follow in order; values are comma-separated.
/// GetCellValue returns null for out-of-range indices.
/// Covers: ToCsv header line present; ToCsv row values correct; ToCsv after AddRow
/// reflects new data; ToCsv after SetCell reflects updated value; ToCsv no-header
/// document starts with first row; GetCellValue valid cell returns value;
/// GetCellValue out-of-range row returns null; GetCellValue out-of-range col returns null;
/// GetCellValue negative index returns null; dogfood ToCsv → Load roundtrip parity.
/// </summary>
public class CsvR130ToCsvSerializationTests
{
    private static CsvDocument LoadSample() =>
        CsvDocument.Load("Name,Score,City\nAlice,95,NYC\nBob,80,London\nCarol,88,Paris");

    private static CsvDocument LoadNoHeader() =>
        CsvDocument.Load("Alice,95,NYC\nBob,80,London", hasHeaders: false);

    // -------------------------------------------------------------------------
    // ToCsv() — header and row serialization
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_HeadersPresent_FirstLineIsHeaderRow()
    {
        var doc = LoadSample();
        var lines = doc.ToCsv().Split('\n', System.StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal("Name,Score,City", lines[0]);
    }

    [Fact]
    public void ToCsv_RowValues_CorrectOrder()
    {
        var doc = LoadSample();
        var lines = doc.ToCsv().Split('\n', System.StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal("Alice,95,NYC",  lines[1]);
        Assert.Equal("Bob,80,London", lines[2]);
    }

    [Fact]
    public void ToCsv_AfterAddRow_NewRowAppearsInOutput()
    {
        var doc = LoadSample();
        doc.AddRow(["Dave", "72", "Berlin"]);
        var csv = doc.ToCsv();
        Assert.Contains("Dave,72,Berlin", csv);
    }

    [Fact]
    public void ToCsv_AfterSetCell_UpdatedValueAppearsInOutput()
    {
        var doc = LoadSample();
        doc.SetCell(0, 1, "99");   // Alice's score → 99
        var csv = doc.ToCsv();
        Assert.Contains("Alice,99,NYC", csv);
    }

    [Fact]
    public void ToCsv_NoHeaderDocument_FirstLineIsFirstDataRow()
    {
        var doc = LoadNoHeader();
        var lines = doc.ToCsv().Split('\n', System.StringSplitOptions.RemoveEmptyEntries);
        // Without headers, first line should be the first data row
        Assert.Equal("Alice,95,NYC", lines[0]);
    }

    // -------------------------------------------------------------------------
    // GetCellValue(int row, int col)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_ValidCell_ReturnsValue()
    {
        var doc = LoadSample();
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("95",    doc.GetCellValue(0, 1));
    }

    [Fact]
    public void GetCellValue_OutOfRangeRow_ReturnsNull()
    {
        var doc = LoadSample();
        Assert.Null(doc.GetCellValue(99, 0));
    }

    [Fact]
    public void GetCellValue_OutOfRangeCol_ReturnsNull()
    {
        var doc = LoadSample();
        Assert.Null(doc.GetCellValue(0, 99));
    }

    [Fact]
    public void GetCellValue_NegativeRow_ReturnsNull()
    {
        var doc = LoadSample();
        Assert.Null(doc.GetCellValue(-1, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood: ToCsv() → CsvDocument.Load() round-trip parity
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ToCsv_ThenLoad_RoundtripParity()
    {
        var original = CsvDocument.Load(
            "Product,Region,Revenue\nWidget,West,1000\nGadget,East,800\nThingit,East,500");

        var csv = original.ToCsv();
        var restored = CsvDocument.Load(csv);

        Assert.Equal(original.RowCount,    restored.RowCount);
        Assert.Equal(original.ColumnCount, restored.ColumnCount);

        // All cell values match
        for (var r = 0; r < original.RowCount; r++)
        {
            for (var c = 0; c < original.ColumnCount; c++)
            {
                Assert.Equal(
                    original.GetCellValue(r, c),
                    restored.GetCellValue(r, c));
            }
        }
    }
}
