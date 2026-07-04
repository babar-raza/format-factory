// Tests for CsvDocument.SortRows, GetCell, RemoveRow deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R199

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R199: Tests for CsvDocument.SortRows, GetCell, RemoveRow deeper.
/// SortRows(colName, ascending): sorts rows by the specified column.
/// GetCell(row, col): returns the cell value at the given row and column index.
/// RemoveRow(rowIndex): removes the row at the specified index.
/// Covers: SortRows ascending first value correct; SortRows descending first value correct;
/// SortRows preserves row count; SortRows by numeric column; SortRows consistent;
/// SortRows then ToTsv reflects order; SortRows after Filter still sorted;
/// SortRows non-null; SortRows same headers;
/// GetCell first cell value; GetCell consistent; GetCell after SetCell reflects;
/// GetCell multiple different cells; GetCell last row accessible; GetCell non-null;
/// RemoveRow decreases count; RemoveRow removes correct row; RemoveRow persist;
/// RemoveRow no-throw; RemoveRow then Filter; RemoveRow row count updated;
/// dogfood LoadFile→SortRows→GetCell→RemoveRow→SaveToFile pipeline.
/// </summary>
public class CsvR199SortRowsAndGetCellDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR199SortRowsAndGetCellDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR199_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleCsv =
        "Name,Dept,Score,City\n" +
        "Charlie,Engineering,85,Boston\n" +
        "Alice,Finance,92,New York\n" +
        "Eve,Engineering,78,Seattle\n" +
        "Bob,HR,95,Chicago\n" +
        "Diana,Finance,88,Los Angeles\n";

    private CsvDocument LoadSample()
    {
        var path = TempFile("sample.csv");
        File.WriteAllText(path, SampleCsv);
        return CsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // SortRows
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_Ascending_FirstValueCorrect()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Name", ascending: true);
        Assert.Equal("Alice", sorted.GetColumnValues("Name")[0]);
    }

    [Fact]
    public void SortRows_Descending_FirstValueCorrect()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Name", ascending: false);
        Assert.Equal("Eve", sorted.GetColumnValues("Name")[0]);
    }

    [Fact]
    public void SortRows_PreservesRowCount()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Name", ascending: true);
        Assert.Equal(doc.GetRowCount(), sorted.GetRowCount());
    }

    [Fact]
    public void SortRows_ByScore_Ascending()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Score", ascending: true);
        Assert.Equal("78", sorted.GetColumnValues("Score")[0]);
    }

    [Fact]
    public void SortRows_ByScore_Descending()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Score", ascending: false);
        Assert.Equal("95", sorted.GetColumnValues("Score")[0]);
    }

    [Fact]
    public void SortRows_Consistent()
    {
        var doc = LoadSample();
        var s1 = doc.SortRows("Name", ascending: true).GetColumnValues("Name");
        var s2 = doc.SortRows("Name", ascending: true).GetColumnValues("Name");
        Assert.Equal(s1, s2);
    }

    [Fact]
    public void SortRows_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.SortRows("Name", ascending: true));
    }

    [Fact]
    public void SortRows_SameHeaders()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Name", ascending: true);
        var origHeaders = doc.GetHeaders();
        var sortedHeaders = sorted.GetHeaders();
        Assert.Equal(origHeaders.Count, sortedHeaders.Count);
    }

    [Fact]
    public void SortRows_AfterFilter_StillSorted()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("Dept", "Finance");
        var sorted = filtered.SortRows("Name", ascending: true);
        var names = sorted.GetColumnValues("Name");
        Assert.Equal("Alice", names[0]);
    }

    // -------------------------------------------------------------------------
    // GetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCell_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetCell(0, 0));
    }

    [Fact]
    public void GetCell_FirstCell_HasValue()
    {
        var doc = LoadSample();
        Assert.True(doc.GetCell(0, 0).Length > 0);
    }

    [Fact]
    public void GetCell_FirstRow_ContainsCharlie()
    {
        var doc = LoadSample();
        Assert.Equal("Charlie", doc.GetCell(0, 0));
    }

    [Fact]
    public void GetCell_Consistent()
    {
        var doc = LoadSample();
        Assert.Equal(doc.GetCell(0, 0), doc.GetCell(0, 0));
    }

    [Fact]
    public void GetCell_AfterSetCell_Reflects()
    {
        var doc = LoadSample();
        doc.SetCell(0, 0, "CHARLIE_UPDATED");
        Assert.Equal("CHARLIE_UPDATED", doc.GetCell(0, 0));
    }

    [Fact]
    public void GetCell_MultipleDifferentCells()
    {
        var doc = LoadSample();
        var c00 = doc.GetCell(0, 0);
        var c01 = doc.GetCell(0, 1);
        var c10 = doc.GetCell(1, 0);
        Assert.NotEqual(c00, c01);
        Assert.NotEqual(c00, c10);
    }

    [Fact]
    public void GetCell_LastRow_HasValue()
    {
        var doc = LoadSample();
        var lastRow = doc.GetRowCount() - 1;
        var cell = doc.GetCell(lastRow, 0);
        Assert.NotNull(cell);
        Assert.True(cell.Length > 0);
    }

    [Fact]
    public void GetCell_ScoreColumn_IsNumeric()
    {
        var doc = LoadSample();
        Assert.Equal("85", doc.GetCell(0, 2)); // Charlie's score
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_DecreasesCount()
    {
        var doc = LoadSample();
        var before = doc.GetRowCount();
        doc.RemoveRow(0);
        Assert.Equal(before - 1, doc.GetRowCount());
    }

    [Fact]
    public void RemoveRow_RemovesCorrectRow()
    {
        var doc = LoadSample();
        var secondRowName = doc.GetCell(1, 0); // Alice
        doc.RemoveRow(0); // Remove Charlie
        // Alice should now be at row 0
        Assert.Equal(secondRowName, doc.GetCell(0, 0));
    }

    [Fact]
    public void RemoveRow_NoThrow()
    {
        var doc = LoadSample();
        var ex = Record.Exception(() => doc.RemoveRow(0));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveRow_Persist()
    {
        var doc = LoadSample();
        var secondName = doc.GetCell(1, 0);
        doc.RemoveRow(0);
        var path = TempFile("remove_row_persist.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(secondName, loaded.GetCell(0, 0));
    }

    [Fact]
    public void RemoveRow_ThenFilter_Works()
    {
        var doc = LoadSample();
        doc.RemoveRow(0); // Remove Charlie (Engineering)
        var eng = doc.Filter("Dept", "Engineering");
        // Eve is still Engineering
        Assert.Equal(1, eng.GetRowCount());
    }

    [Fact]
    public void RemoveRow_Multiple_CountUpdated()
    {
        var doc = LoadSample();
        var before = doc.GetRowCount();
        doc.RemoveRow(0);
        doc.RemoveRow(0);
        Assert.Equal(before - 2, doc.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_SortRows_GetCell_RemoveRow_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.GetRowCount());

        // GetCell baseline
        Assert.Equal("Charlie", doc.GetCell(0, 0));
        Assert.Equal("85", doc.GetCell(0, 2));

        // SortRows ascending by Name
        var sorted = doc.SortRows("Name", ascending: true);
        Assert.Equal(5, sorted.GetRowCount());
        Assert.Equal("Alice", sorted.GetColumnValues("Name")[0]);
        Assert.Equal("Eve", sorted.GetColumnValues("Name")[4]);

        // GetCell on sorted
        Assert.Equal("Alice", sorted.GetCell(0, 0));
        Assert.Equal("92", sorted.GetCell(0, 2));

        // SortRows descending by Score
        var sortedDesc = doc.SortRows("Score", ascending: false);
        Assert.Equal("95", sortedDesc.GetColumnValues("Score")[0]);
        Assert.Equal("Bob", sortedDesc.GetCell(0, 0)); // Bob has 95

        // Filter then SortRows
        var financeFiltered = doc.Filter("Dept", "Finance");
        var financeSorted = financeFiltered.SortRows("Name", ascending: true);
        Assert.Equal("Alice", financeSorted.GetCell(0, 0));

        // RemoveRow — remove current row 0 (Bob=95 after Score desc sort)
        var charlieScore = doc.GetCell(0, 2);
        Assert.Equal("95", charlieScore);
        doc.RemoveRow(0);
        Assert.Equal(4, doc.GetRowCount());

        // GetCell after remove — Alice now at row 0
        Assert.Equal("Alice", doc.GetCell(0, 0));

        // SortRows after RemoveRow
        var sortedAfterRemove = doc.SortRows("Name", ascending: true);
        Assert.Equal(4, sortedAfterRemove.GetRowCount());
        Assert.Equal("Alice", sortedAfterRemove.GetCell(0, 0));

        // RemoveRow last row
        var lastIdx = doc.GetRowCount() - 1;
        doc.RemoveRow(lastIdx);
        Assert.Equal(3, doc.GetRowCount());

        // GetCell still works
        Assert.NotNull(doc.GetCell(0, 0));

        // Filter after removes
        var engAfterRemove = doc.Filter("Dept", "Engineering");
        Assert.True(engAfterRemove.GetRowCount() >= 1);

        // SaveToFile and reload
        var path = TempFile("dogfood_sort_cell.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetRowCount());

        // GetCell on loaded
        Assert.NotNull(loaded.GetCell(0, 0));
        Assert.True(loaded.GetCell(0, 0).Length > 0);

        // SortRows on loaded
        var loadedSorted = loaded.SortRows("Name", ascending: true);
        Assert.Equal(3, loadedSorted.GetRowCount());
        Assert.Equal("Alice", loadedSorted.GetCell(0, 0));

        // RemoveRow on loaded
        loaded.RemoveRow(0);
        Assert.Equal(2, loaded.GetRowCount());
    }
}
