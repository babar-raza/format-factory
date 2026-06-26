// Tests for CsvDocument.AddRow, RemoveRow, SetCellValue deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R160

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R160: Tests for CsvDocument.AddRow, RemoveRow, SetCellValue deeper coverage.
/// AddRow(values): appends a new row with given values.
/// RemoveRow(index): removes the row at the given index.
/// SetCellValue(row, col, value): sets a specific cell value.
/// Covers: AddRow increases RowCount; AddRow values accessible via GetColumn;
/// AddRow multiple times increases count; RemoveRow decreases count;
/// RemoveRow first row shifts remaining; RemoveRow last row leaves others intact;
/// SetCellValue updates existing cell; SetCellValue at new row index;
/// AddRow then RemoveRow restores count; GetCellValue after SetCellValue;
/// AddRow preserves existing rows; IsEmpty after RemoveRow all;
/// AddRow->ToCsv->Load round-trip;
/// dogfood CreateEmpty->AddRows->SetCellValue->RemoveRow->ToCsv->Load.
/// </summary>
public class CsvR160AddRowAndRemoveRowTests
{
    private static CsvDocument CreateWithHeaders()
    {
        var doc = CsvDocument.Load("name,dept,score\nAlice,Eng,95\nBob,Finance,82");
        return doc;
    }

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncreasesRowCount()
    {
        var doc = CreateWithHeaders();
        var before = doc.RowCount;
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_ValuesAccessibleViaGetColumn()
    {
        var doc = CreateWithHeaders();
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        var names = doc.GetColumn("name");
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void AddRow_MultipleTimes_CountIncreases()
    {
        var doc = CsvDocument.Load("name,dept\n");
        doc.AddRow(new[] { "Alice", "Eng" });
        doc.AddRow(new[] { "Bob", "Finance" });
        doc.AddRow(new[] { "Carol", "Eng" });
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void AddRow_PreservesExistingRows()
    {
        var doc = CreateWithHeaders();
        doc.AddRow(new[] { "Dave", "HR", "77" });
        var names = doc.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void AddRow_ToCsv_Load_RoundTrip()
    {
        var doc = CreateWithHeaders();
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        var csv = doc.ToCsv();
        var loaded = CsvDocument.Load(csv);
        Assert.Equal(3, loaded.RowCount);
        Assert.Contains("Carol", loaded.GetColumn("name"));
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_DecreasesCount()
    {
        var doc = CreateWithHeaders();
        var before = doc.RowCount;
        doc.RemoveRow(0);
        Assert.Equal(before - 1, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_FirstRow_ShiftsRemaining()
    {
        var doc = CreateWithHeaders();
        // Before: Alice(0), Bob(1)
        doc.RemoveRow(0);
        // After: Bob(0)
        var names = doc.GetColumn("name");
        Assert.DoesNotContain("Alice", names);
        Assert.Contains("Bob", names);
    }

    [Fact]
    public void RemoveRow_LastRow_OthersIntact()
    {
        var doc = CreateWithHeaders();
        doc.RemoveRow(doc.RowCount - 1);
        var names = doc.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.DoesNotContain("Bob", names);
    }

    [Fact]
    public void RemoveRow_AllRows_IsEmpty()
    {
        var doc = CsvDocument.Load("name,dept\nAlice,Eng");
        doc.RemoveRow(0);
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // SetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_UpdatesExistingCell()
    {
        var doc = CreateWithHeaders();
        doc.SetCellValue(0, 0, "UpdatedAlice");
        var val = doc.GetCellValue(0, 0);
        Assert.Equal("UpdatedAlice", val);
    }

    [Fact]
    public void SetCellValue_AfterAddRow_NewRowCellAccessible()
    {
        var doc = CreateWithHeaders();
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        doc.SetCellValue(doc.RowCount - 1, 0, "Carol_Updated");
        var names = doc.GetColumn("name");
        Assert.Contains("Carol_Updated", names);
    }

    [Fact]
    public void AddRow_Then_RemoveRow_RestoresCount()
    {
        var doc = CreateWithHeaders();
        var original = doc.RowCount;
        doc.AddRow(new[] { "Extra", "IT", "70" });
        Assert.Equal(original + 1, doc.RowCount);
        doc.RemoveRow(doc.RowCount - 1);
        Assert.Equal(original, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->AddRows->SetCellValue->RemoveRow->ToCsv->Load
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAddSetRemoveToCsvLoad_Pipeline()
    {
        var doc = CsvDocument.Load("name,dept,score\n");
        Assert.Equal(0, doc.RowCount);

        // AddRow
        doc.AddRow(new[] { "Alice", "Eng", "95" });
        doc.AddRow(new[] { "Bob", "Finance", "82" });
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        Assert.Equal(3, doc.RowCount);

        // SetCellValue — update Bob's score
        doc.SetCellValue(1, 2, "90");
        Assert.Equal("90", doc.GetCellValue(1, 2));

        // RemoveRow — remove Carol
        doc.RemoveRow(2);
        Assert.Equal(2, doc.RowCount);
        Assert.DoesNotContain("Carol", doc.GetColumn("name"));

        // ToCsv
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
        Assert.DoesNotContain("Carol", csv);

        // Load
        var loaded = CsvDocument.Load(csv);
        Assert.Equal(2, loaded.RowCount);
        Assert.Equal("90", loaded.GetCellValue(1, 2));
    }
}
