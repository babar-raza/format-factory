// Tests for TsvDocument.SortRows, SetCell, ExportToCsv deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R198

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R198: Tests for TsvDocument.SortRows, SetCell, ExportToCsv deeper.
/// SortRows(colName, ascending): sorts document rows by the specified column.
/// SetCell(row, col, value): sets the value of a specific cell.
/// ExportToCsv(): exports the document to a CSV-formatted string.
/// Covers: SortRows ascending first row correct; SortRows descending first row correct;
/// SortRows preserves row count; SortRows preserves headers; SortRows by numeric column;
/// SortRows consistent; SortRows then Filter; SortRows no-throw;
/// SetCell changes value; SetCell then GetCell reflects; SetCell persist;
/// SetCell multiple cells; SetCell preserves other cells; SetCell first row;
/// SetCell last column; SetCell no-throw;
/// ExportToCsv non-null; ExportToCsv non-empty; ExportToCsv has commas;
/// ExportToCsv has header names; ExportToCsv has data values; ExportToCsv after AddRow grows;
/// ExportToCsv after Filter shrinks; ExportToCsv consistent;
/// dogfood LoadFile→SortRows→SetCell→ExportToCsv→SaveToFile pipeline.
/// </summary>
public class TsvR198SortRowsAndSetCellDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR198SortRowsAndSetCellDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR198_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleTsv()
    {
        var path = TempFile("sample.tsv");
        var content =
            "Name\tDepartment\tScore\tCity\n" +
            "Charlie\tFinance\t78\tLondon\n" +
            "Alice\tEngineering\t92\tParis\n" +
            "Eve\tMarketing\t85\tBerlin\n" +
            "Bob\tEngineering\t88\tLondon\n" +
            "Diana\tFinance\t91\tRome\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // SortRows
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_Ascending_FirstRowCorrect()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.SortRows("Name", ascending: true);
        var first = doc.GetCell(0, 0);
        Assert.Equal("Alice", first);
    }

    [Fact]
    public void SortRows_Descending_FirstRowCorrect()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.SortRows("Name", ascending: false);
        var first = doc.GetCell(0, 0);
        Assert.Equal("Eve", first);
    }

    [Fact]
    public void SortRows_PreservesRowCount()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.GetRowCount();
        doc.SortRows("Name", ascending: true);
        Assert.Equal(before, doc.GetRowCount());
    }

    [Fact]
    public void SortRows_PreservesHeaders()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.SortRows("Name", ascending: true);
        var headers = doc.GetHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Department", headers);
        Assert.Contains("Score", headers);
        Assert.Contains("City", headers);
    }

    [Fact]
    public void SortRows_ByScore_Ascending_FirstIsLowest()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.SortRows("Score", ascending: true);
        var first = doc.GetCell(0, 2);
        // 78 is lowest
        Assert.Equal("78", first);
    }

    [Fact]
    public void SortRows_ByScore_Descending_FirstIsHighest()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.SortRows("Score", ascending: false);
        var first = doc.GetCell(0, 2);
        // 92 is highest
        Assert.Equal("92", first);
    }

    [Fact]
    public void SortRows_NoThrow()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.SortRows("Name", ascending: true));
        Assert.Null(ex);
    }

    [Fact]
    public void SortRows_Consistent()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.SortRows("Name", ascending: true);
        var first = doc.GetCell(0, 0);
        doc.SortRows("Name", ascending: true);
        var firstAgain = doc.GetCell(0, 0);
        Assert.Equal(first, firstAgain);
    }

    // -------------------------------------------------------------------------
    // SetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_ChangesValue()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.SetCell(0, 2, "99");
        var val = doc.GetCell(0, 2);
        Assert.Equal("99", val);
    }

    [Fact]
    public void SetCell_ThenGetCell_Reflects()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.SetCell(1, 1, "UPDATED_DEPT");
        Assert.Equal("UPDATED_DEPT", doc.GetCell(1, 1));
    }

    [Fact]
    public void SetCell_NoThrow()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.SetCell(0, 0, "NewValue"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCell_Persist()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.SetCell(0, 3, "UPDATED_CITY");
        var savePath = TempFile("setcell_persist.tsv");
        doc.SaveToFile(savePath);
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal("UPDATED_CITY", loaded.GetCell(0, 3));
    }

    [Fact]
    public void SetCell_Multiple_AllReflect()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.SetCell(0, 0, "CHARLIE_RENAMED");
        doc.SetCell(1, 0, "ALICE_RENAMED");
        doc.SetCell(2, 0, "EVE_RENAMED");
        Assert.Equal("CHARLIE_RENAMED", doc.GetCell(0, 0));
        Assert.Equal("ALICE_RENAMED", doc.GetCell(1, 0));
        Assert.Equal("EVE_RENAMED", doc.GetCell(2, 0));
    }

    [Fact]
    public void SetCell_PreservesOtherCells()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var original_row1_col1 = doc.GetCell(1, 1);
        doc.SetCell(0, 0, "MODIFIED");
        Assert.Equal(original_row1_col1, doc.GetCell(1, 1));
    }

    [Fact]
    public void SetCell_FirstRow_Works()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.SetCell(0, 0, "FIRST_CELL_UPDATED");
        Assert.Equal("FIRST_CELL_UPDATED", doc.GetCell(0, 0));
    }

    [Fact]
    public void SetCell_RowCountUnchanged()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.GetRowCount();
        doc.SetCell(2, 1, "UpdatedDept");
        Assert.Equal(before, doc.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // ExportToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToCsv_NonNull()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.NotNull(doc.ExportToCsv());
    }

    [Fact]
    public void ExportToCsv_NonEmpty()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.NotEmpty(doc.ExportToCsv());
    }

    [Fact]
    public void ExportToCsv_HasCommas()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var csv = doc.ExportToCsv();
        Assert.Contains(",", csv);
    }

    [Fact]
    public void ExportToCsv_HasHeaderNames()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var csv = doc.ExportToCsv();
        Assert.Contains("Name", csv);
        Assert.Contains("Department", csv);
        Assert.Contains("Score", csv);
    }

    [Fact]
    public void ExportToCsv_HasDataValues()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var csv = doc.ExportToCsv();
        Assert.True(csv.Contains("Alice") || csv.Contains("Charlie") || csv.Contains("Eve"));
    }

    [Fact]
    public void ExportToCsv_AfterAddRow_Grows()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.ExportToCsv().Length;
        doc.AddRow(new[] { "Zara", "HR", "88", "Madrid" });
        var after = doc.ExportToCsv().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToCsv_AfterFilter_Shrinks()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.ExportToCsv().Length;
        var filtered = doc.Filter("Department", "Engineering");
        var after = filtered.ExportToCsv().Length;
        Assert.True(after < before);
    }

    [Fact]
    public void ExportToCsv_Consistent()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var csv1 = doc.ExportToCsv();
        var csv2 = doc.ExportToCsv();
        Assert.Equal(csv1.Length, csv2.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SortRows_SetCell_ExportToCsv_SaveToFile_Pipeline()
    {
        // Create sample TSV
        var path = TempFile("dogfood_src.tsv");
        var content =
            "Employee\tTeam\tScore\tLocation\n" +
            "Zara\tProduct\t77\tMadrid\n" +
            "Aaron\tEngineering\t95\tBerlin\n" +
            "Mia\tMarketing\t83\tParis\n" +
            "Owen\tProduct\t89\tLondon\n" +
            "Lily\tEngineering\t91\tRome\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(5, doc.GetRowCount());

        // GetHeaders
        var headers = doc.GetHeaders();
        Assert.Contains("Employee", headers);
        Assert.Contains("Team", headers);
        Assert.Contains("Score", headers);
        Assert.Contains("Location", headers);

        // SortRows ascending by Employee
        doc.SortRows("Employee", ascending: true);
        Assert.Equal("Aaron", doc.GetCell(0, 0));
        Assert.Equal(5, doc.GetRowCount());

        // SortRows descending by Score
        doc.SortRows("Score", ascending: false);
        Assert.Equal("95", doc.GetCell(0, 2)); // Aaron=95 is highest
        Assert.Equal(5, doc.GetRowCount());

        // SetCell — update some values
        doc.SetCell(4, 2, "80"); // Update lowest score
        var updated = doc.GetCell(4, 2);
        Assert.Equal("80", updated);

        doc.SetCell(0, 3, "UPDATED_LOCATION");
        Assert.Equal("UPDATED_LOCATION", doc.GetCell(0, 3));

        // ExportToCsv baseline
        var csv = doc.ExportToCsv();
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);
        Assert.Contains("Employee", csv);
        Assert.Contains("Aaron", csv);
        Assert.Contains(",", csv);

        // AddRow and verify ExportToCsv grows
        doc.AddRow(new[] { "Finn", "Marketing", "88", "Oslo" });
        var csvAfterAdd = doc.ExportToCsv();
        Assert.True(csvAfterAdd.Length > csv.Length);
        Assert.Contains("Finn", csvAfterAdd);
        Assert.Equal(6, doc.GetRowCount());

        // SortRows again after AddRow
        doc.SortRows("Employee", ascending: true);
        Assert.Equal("Aaron", doc.GetCell(0, 0));
        // Finn should appear sorted
        Assert.Equal(6, doc.GetRowCount());

        // Filter Engineering
        var engFiltered = doc.Filter("Team", "Engineering");
        var engCsv = engFiltered.ExportToCsv();
        Assert.True(engCsv.Length < csvAfterAdd.Length);
        Assert.Contains("Aaron", engCsv);
        Assert.Contains("Lily", engCsv);

        // SetCell on filtered result
        engFiltered.SetCell(0, 2, "100");
        Assert.Equal("100", engFiltered.GetCell(0, 2));

        // SaveToFile
        var savePath = TempFile("dogfood_sorted.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(6, loaded.GetRowCount());
        var loadedHeaders = loaded.GetHeaders();
        Assert.Contains("Employee", loadedHeaders);
        Assert.Contains("Score", loadedHeaders);

        // ExportToCsv on loaded
        var loadedCsv = loaded.ExportToCsv();
        Assert.NotNull(loadedCsv);
        Assert.NotEmpty(loadedCsv);
        Assert.Contains(",", loadedCsv);

        // SortRows on loaded
        loaded.SortRows("Score", ascending: false);
        var loadedFirst = loaded.GetCell(0, 2);
        Assert.True(int.TryParse(loadedFirst, out _));

        // SetCell on loaded
        loaded.SetCell(0, 0, "SORTED_FIRST");
        Assert.Equal("SORTED_FIRST", loaded.GetCell(0, 0));

        // Final ExportToCsv
        var finalCsv = loaded.ExportToCsv();
        Assert.Contains("SORTED_FIRST", finalCsv);
    }
}
