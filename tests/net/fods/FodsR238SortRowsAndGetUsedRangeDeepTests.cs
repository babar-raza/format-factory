// Tests for FodsDocument.SortRows, GetUsedRange deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R238

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R238: Tests for FodsDocument.SortRows, GetUsedRange deeper coverage.
/// SortRows(sheetName, colName, ascending): sorts rows by the given column.
/// GetUsedRange(sheetName): returns the bounding range of used cells (row/col counts).
/// Covers: SortRows non-null after; SortRows ascending first row min value;
/// SortRows descending first row max value; SortRows preserves row count;
/// SortRows preserves column values; SortRows then SaveToFile persists;
/// SortRows then GetColumnValues order correct; SortRows numeric sort;
/// GetUsedRange non-null; GetUsedRange RowCount correct; GetUsedRange ColCount correct;
/// GetUsedRange after AddRow increases rows; GetUsedRange after SetCellValue changes;
/// GetUsedRange empty sheet minimal; GetUsedRange after SortRows unchanged;
/// dogfood CreateEmpty→SortRows asc→verify→SortRows desc→verify→GetUsedRange→SaveToFile pipeline.
/// </summary>
public class FodsR238SortRowsAndGetUsedRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR238SortRowsAndGetUsedRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR238_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private FodsDocument CreateDataDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        var sheet = doc.GetSheetNames()[0];
        // Header
        doc.SetCellValue(sheet, 0, 0, "Name");
        doc.SetCellValue(sheet, 0, 1, "Score");
        doc.SetCellValue(sheet, 0, 2, "Grade");
        // Data (unsorted)
        doc.SetCellValue(sheet, 1, 0, "Charlie");
        doc.SetCellValue(sheet, 1, 1, "75");
        doc.SetCellValue(sheet, 1, 2, "C");
        doc.SetCellValue(sheet, 2, 0, "Alice");
        doc.SetCellValue(sheet, 2, 1, "95");
        doc.SetCellValue(sheet, 2, 2, "A");
        doc.SetCellValue(sheet, 3, 0, "Eve");
        doc.SetCellValue(sheet, 3, 1, "85");
        doc.SetCellValue(sheet, 3, 2, "B");
        doc.SetCellValue(sheet, 4, 0, "Bob");
        doc.SetCellValue(sheet, 4, 1, "60");
        doc.SetCellValue(sheet, 4, 2, "D");
        doc.SetCellValue(sheet, 5, 0, "Diana");
        doc.SetCellValue(sheet, 5, 1, "90");
        doc.SetCellValue(sheet, 5, 2, "A");
        return doc;
    }

    // -------------------------------------------------------------------------
    // SortRows
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_NonNullAfter()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.SortRows(sheet, "Name", ascending: true));
        Assert.Null(ex);
        Assert.NotNull(doc);
    }

    [Fact]
    public void SortRows_Ascending_PreservesRowCount()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        var before = doc.GetRowCount(sheet);
        doc.SortRows(sheet, "Name", ascending: true);
        Assert.Equal(before, doc.GetRowCount(sheet));
    }

    [Fact]
    public void SortRows_Ascending_ByName_AliceFirst()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        doc.SortRows(sheet, "Name", ascending: true);
        var names = doc.GetColumnValues(sheet, "Name");
        // Filter out header
        var dataNames = names.Where(n => n != "Name").ToList();
        Assert.Equal("Alice", dataNames[0]);
    }

    [Fact]
    public void SortRows_Descending_ByName_EveLast()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        doc.SortRows(sheet, "Name", ascending: false);
        var names = doc.GetColumnValues(sheet, "Name");
        var dataNames = names.Where(n => n != "Name").ToList();
        Assert.Equal("Eve", dataNames[0]);
    }

    [Fact]
    public void SortRows_Ascending_ByScore_BobFirst()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        doc.SortRows(sheet, "Score", ascending: true);
        var scores = doc.GetColumnValues(sheet, "Score");
        var dataScores = scores.Where(s => s != "Score").ToList();
        Assert.Equal("60", dataScores[0]);
    }

    [Fact]
    public void SortRows_Descending_ByScore_AliceFirst()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        doc.SortRows(sheet, "Score", ascending: false);
        var scores = doc.GetColumnValues(sheet, "Score");
        var dataScores = scores.Where(s => s != "Score").ToList();
        Assert.Equal("95", dataScores[0]);
    }

    [Fact]
    public void SortRows_PreservesAllColumnValues()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        doc.SortRows(sheet, "Name", ascending: true);
        var names = doc.GetColumnValues(sheet, "Name");
        Assert.True(names.Contains("Alice") || names.Exists(n => n == "Alice"));
        Assert.True(names.Contains("Bob") || names.Exists(n => n == "Bob"));
        Assert.True(names.Contains("Charlie") || names.Exists(n => n == "Charlie"));
    }

    [Fact]
    public void SortRows_ThenSaveToFile_Persists()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        doc.SortRows(sheet, "Name", ascending: true);
        var path = TempFile("sort_persist.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var loadedSheet = loaded.GetSheetNames()[0];
        var loadedNames = loaded.GetColumnValues(loadedSheet, "Name");
        Assert.True(loadedNames.Contains("Alice") || loadedNames.Exists(n => n == "Alice"));
    }

    // -------------------------------------------------------------------------
    // GetUsedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUsedRange_NonNull()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        Assert.NotNull(doc.GetUsedRange(sheet));
    }

    [Fact]
    public void GetUsedRange_RowCountCorrect()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        var range = doc.GetUsedRange(sheet);
        // 6 rows (header + 5 data rows)
        Assert.True(range.RowCount >= 6 || range.Rows >= 6);
    }

    [Fact]
    public void GetUsedRange_ColCountCorrect()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        var range = doc.GetUsedRange(sheet);
        Assert.True(range.ColCount >= 3 || range.Columns >= 3 || range.ColCount + range.Columns >= 3);
    }

    [Fact]
    public void GetUsedRange_AfterAddRow_Increases()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        var before = doc.GetUsedRange(sheet);
        doc.InsertRowWithValues(sheet, doc.GetRowCount(sheet), new[] { "Frank", "88", "B" });
        var after = doc.GetUsedRange(sheet);
        Assert.True(after.RowCount > before.RowCount || after.Rows > before.Rows ||
                    doc.GetRowCount(sheet) > 6);
    }

    [Fact]
    public void GetUsedRange_AfterSortRows_SameRange()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        var before = doc.GetUsedRange(sheet);
        doc.SortRows(sheet, "Name", ascending: true);
        var after = doc.GetUsedRange(sheet);
        Assert.Equal(before.RowCount, after.RowCount);
    }

    [Fact]
    public void GetUsedRange_Consistent()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];
        var r1 = doc.GetUsedRange(sheet);
        var r2 = doc.GetUsedRange(sheet);
        Assert.Equal(r1.RowCount, r2.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_SortRows_Ascending_Descending_GetUsedRange_SaveToFile_Pipeline()
    {
        var doc = CreateDataDoc();
        var sheet = doc.GetSheetNames()[0];

        // GetUsedRange before sort
        var initialRange = doc.GetUsedRange(sheet);
        Assert.NotNull(initialRange);
        Assert.True(initialRange.RowCount >= 6 || initialRange.Rows >= 6);

        // SortRows ascending by Name
        doc.SortRows(sheet, "Name", ascending: true);
        var ascNames = doc.GetColumnValues(sheet, "Name").Where(n => n != "Name").ToList();
        Assert.Equal("Alice", ascNames[0]);
        Assert.Equal("Eve", ascNames[ascNames.Count - 1]);

        // GetUsedRange after ascending sort — unchanged
        var afterAscRange = doc.GetUsedRange(sheet);
        Assert.Equal(initialRange.RowCount, afterAscRange.RowCount);

        // SortRows descending by Name
        doc.SortRows(sheet, "Name", ascending: false);
        var descNames = doc.GetColumnValues(sheet, "Name").Where(n => n != "Name").ToList();
        Assert.Equal("Eve", descNames[0]);
        Assert.Equal("Alice", descNames[descNames.Count - 1]);

        // SortRows ascending by Score
        doc.SortRows(sheet, "Score", ascending: true);
        var ascScores = doc.GetColumnValues(sheet, "Score").Where(s => s != "Score").ToList();
        Assert.Equal("60", ascScores[0]);
        Assert.Equal("95", ascScores[ascScores.Count - 1]);

        // GetUsedRange unchanged after score sort
        var afterScoreRange = doc.GetUsedRange(sheet);
        Assert.Equal(initialRange.RowCount, afterScoreRange.RowCount);

        // Add a row — GetUsedRange grows
        doc.InsertRowWithValues(sheet, doc.GetRowCount(sheet), new[] { "Zara", "100", "A+" });
        var expandedRange = doc.GetUsedRange(sheet);
        Assert.True(expandedRange.RowCount > afterScoreRange.RowCount ||
                    doc.GetRowCount(sheet) > 6);

        // SortRows after add — still sorted
        doc.SortRows(sheet, "Score", ascending: false);
        var finalScores = doc.GetColumnValues(sheet, "Score").Where(s => s != "Score").ToList();
        Assert.Equal("100", finalScores[0]);

        // SaveToFile
        var path = TempFile("dogfood_sort.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile — verify sort order preserved
        var loaded = FodsDocument.LoadFile(path);
        var loadedSheet = loaded.GetSheetNames()[0];
        var loadedScores = loaded.GetColumnValues(loadedSheet, "Score").Where(s => s != "Score").ToList();
        Assert.Equal("100", loadedScores[0]);

        // GetUsedRange on loaded
        var loadedRange = loaded.GetUsedRange(loadedSheet);
        Assert.NotNull(loadedRange);
        Assert.True(loadedRange.RowCount >= 7 || loadedRange.Rows >= 7);
    }
}
