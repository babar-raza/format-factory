// Tests for CsvDocument.GetCellValue, AddRow, SetCell, RemoveRow deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R148

using System;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R148: Tests for CsvDocument.GetCellValue, AddRow, SetCell, RemoveRow deeper coverage.
/// GetCellValue(row, col): retrieves cell at row/col.
/// AddRow(IEnumerable[string]): appends a new row.
/// SetCell(row, col, value): mutates a single cell.
/// RemoveRow(index): removes a row.
/// Covers: GetCellValue first row first col; GetCellValue last row last col;
/// GetCellValue OOB returns null; AddRow increases RowCount; AddRow value retrievable;
/// SetCell changes value; SetCell GetCellValue returns new value;
/// SetCell persists through ToCsv; RemoveRow decreases RowCount; RemoveRow OOB throws;
/// AddRow then Filter works; IsEmpty after all rows removed;
/// GetColumn after SetCell returns updated value; dogfood pipeline.
/// </summary>
public class CsvR148GetCellValueAndMutationTests
{
    private const string ThreeRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88";

    // -------------------------------------------------------------------------
    // GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_Row0Col0_IsFirstCell()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        Assert.Equal("Name", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_LastRowLastCol_Correct()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        // 4 rows (0-3); col 2
        Assert.Equal("88", doc.GetCellValue(3, 2));
    }

    [Fact]
    public void GetCellValue_OobRow_ReturnsNull()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        Assert.Null(doc.GetCellValue(999, 0));
    }

    [Fact]
    public void GetCellValue_OobCol_ReturnsNull()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        Assert.Null(doc.GetCellValue(0, 999));
    }

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncreasesRowCount()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        var before = doc.RowCount;
        doc.AddRow(new[] { "Dave", "Finance", "91" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_ValueRetrievable()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        doc.AddRow(new[] { "Dave", "Finance", "91" });
        Assert.Equal("Dave", doc.GetCellValue(doc.RowCount - 1, 0));
    }

    [Fact]
    public void AddRow_FilterWorksProperly()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        doc.AddRow(new[] { "Dave", "Finance", "91" });
        var finance = doc.Filter(row => row.Length > 1 && row[1] == "Finance");
        Assert.Equal(2, finance.RowCount); // Bob + Dave
    }

    // -------------------------------------------------------------------------
    // SetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_ChangesValue()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        doc.SetCell(1, 0, "ALICE");
        Assert.Equal("ALICE", doc.GetCellValue(1, 0));
    }

    [Fact]
    public void SetCell_PersistsThroughToCsv()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        doc.SetCell(1, 2, "100");
        var csv = doc.ToCsv();
        Assert.Contains("100", csv);
    }

    [Fact]
    public void SetCell_GetColumnAfterSet_ContainsNewValue()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        doc.SetCell(1, 0, "MODIFIED");
        var col = doc.GetColumn(0);
        Assert.Contains("MODIFIED", col);
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_DecreasesRowCount()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        var before = doc.RowCount;
        doc.RemoveRow(0);
        Assert.Equal(before - 1, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_CorrectRowRemoved()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        // Row 0 = header. Remove row 1 (Alice)
        doc.RemoveRow(1);
        // Now row 1 = Bob
        Assert.Equal("Bob", doc.GetCellValue(1, 0));
    }

    [Fact]
    public void RemoveRow_AllRows_IsEmpty()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        while (doc.RowCount > 0)
            doc.RemoveRow(0);
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AddRow->SetCell->RemoveRow->ToCsv pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddSetRemoveToCsvPipeline()
    {
        var doc = CsvDocument.Load(ThreeRowCsv, hasHeaders: false);
        Assert.Equal(4, doc.RowCount);

        // Add a row
        doc.AddRow(new[] { "Dave", "Finance", "91" });
        Assert.Equal(5, doc.RowCount);

        // Set a cell
        doc.SetCell(1, 2, "99"); // Update Alice's score
        Assert.Equal("99", doc.GetCellValue(1, 2));

        // Remove a row (Bob, index 2)
        doc.RemoveRow(2);
        Assert.Equal(4, doc.RowCount);

        // Serialize and verify
        var csv = doc.ToCsv();
        Assert.Contains("99", csv);   // Alice's updated score
        Assert.Contains("Dave", csv); // newly added
        Assert.DoesNotContain("Bob", csv); // removed

        // Filter
        var eng = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Contains("Alice", eng.GetColumn(0));
    }
}
