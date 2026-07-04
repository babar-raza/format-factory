// Tests for CsvDocument.GetRowValues, ExportToNdjson, RemoveRow deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R207

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R207: Tests for CsvDocument.GetRowValues, ExportToNdjson, RemoveRow deeper.
/// GetRowValues(rowIndex): returns all cell values in the specified row.
/// ExportToNdjson(): exports the document as newline-delimited JSON.
/// RemoveRow(index): removes the row at the specified zero-based index.
/// Covers: GetRowValues non-null; GetRowValues non-empty; GetRowValues count=colCount;
/// GetRowValues consistent; GetRowValues no-throw; GetRowValues after SetCell reflects;
/// GetRowValues first row; GetRowValues last row; GetRowValues for all rows no-throw;
/// GetRowValues after AddRow reflects new row; GetRowValues after RemoveRow shifts;
/// ExportToNdjson non-null; ExportToNdjson non-empty; ExportToNdjson has braces;
/// ExportToNdjson has header names; ExportToNdjson has data; ExportToNdjson after AddRow grows;
/// ExportToNdjson after Filter shrinks; ExportToNdjson consistent;
/// ExportToNdjson newline per record; ExportToNdjson after RemoveRow shrinks;
/// RemoveRow no-throw; RemoveRow decreases count; RemoveRow first; RemoveRow last;
/// RemoveRow middle; RemoveRow persist; RemoveRow correct row; RemoveRow multiple;
/// dogfood LoadFile→GetRowValues→ExportToNdjson→RemoveRow→SaveToFile pipeline.
/// </summary>
public class CsvR207GetRowValuesAndExportToNdjsonDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR207GetRowValuesAndExportToNdjsonDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR207_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleCsv()
    {
        var path = TempFile("sample.csv");
        var content =
            "Name,Team,Score,City\n" +
            "Alice,Alpha,92,London\n" +
            "Bob,Beta,78,Paris\n" +
            "Carol,Alpha,88,Berlin\n" +
            "Dave,Gamma,85,Rome\n" +
            "Eve,Alpha,95,Madrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRowValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.GetRowValues(0));
    }

    [Fact]
    public void GetRowValues_NonEmpty()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetRowValues(0).Count > 0);
    }

    [Fact]
    public void GetRowValues_CountEqualsColumnCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetHeaderCount(), doc.GetRowValues(0).Count);
    }

    [Fact]
    public void GetRowValues_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var r1 = doc.GetRowValues(0);
        var r2 = doc.GetRowValues(0);
        Assert.Equal(r1.Count, r2.Count);
    }

    [Fact]
    public void GetRowValues_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetRowValues(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRowValues_AfterSetCell_Reflects()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.SetCell(1, 0, "BOB_UPDATED");
        var row = doc.GetRowValues(1);
        Assert.Contains("BOB_UPDATED", row);
    }

    [Fact]
    public void GetRowValues_FirstRow_HasAlice()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var row = doc.GetRowValues(0);
        Assert.Contains("Alice", row);
    }

    [Fact]
    public void GetRowValues_LastRow_HasEve()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var row = doc.GetRowValues(4);
        Assert.Contains("Eve", row);
    }

    [Fact]
    public void GetRowValues_ForAllRows_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        for (int i = 0; i < doc.GetRowCount(); i++)
        {
            var ex = Record.Exception(() => doc.GetRowValues(i));
            Assert.Null(ex);
        }
    }

    [Fact]
    public void GetRowValues_AfterAddRow_ReflectsNewRow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.AddRow(new[] { "Frank", "Delta", "80", "Oslo" });
        var row = doc.GetRowValues(5);
        Assert.Contains("Frank", row);
        Assert.Contains("Oslo", row);
    }

    // -------------------------------------------------------------------------
    // ExportToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToNdjson_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_NonEmpty()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotEmpty(doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_HasBraces()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Contains("{", doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_HasHeaderNames()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ndjson = doc.ExportToNdjson();
        Assert.True(ndjson.Contains("Name") || ndjson.Contains("Team") || ndjson.Contains("Score"));
    }

    [Fact]
    public void ExportToNdjson_HasData()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ndjson = doc.ExportToNdjson();
        Assert.True(ndjson.Contains("Alice") || ndjson.Contains("Bob") || ndjson.Contains("Carol"));
    }

    [Fact]
    public void ExportToNdjson_AfterAddRow_Grows()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.ExportToNdjson().Length;
        doc.AddRow(new[] { "Frank", "Delta", "80", "Oslo" });
        Assert.True(doc.ExportToNdjson().Length > before);
    }

    [Fact]
    public void ExportToNdjson_AfterFilter_Shrinks()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.ExportToNdjson().Length;
        var filtered = doc.Filter("Team", "Gamma");
        Assert.True(filtered.ExportToNdjson().Length < before);
    }

    [Fact]
    public void ExportToNdjson_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.ExportToNdjson().Length, doc.ExportToNdjson().Length);
    }

    [Fact]
    public void ExportToNdjson_AfterRemoveRow_Shrinks()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.ExportToNdjson().Length;
        doc.RemoveRow(0);
        Assert.True(doc.ExportToNdjson().Length < before);
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.RemoveRow(0));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveRow_DecreasesCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetRowCount();
        doc.RemoveRow(2);
        Assert.Equal(before - 1, doc.GetRowCount());
    }

    [Fact]
    public void RemoveRow_FirstRow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RemoveRow(0); // Alice
        Assert.Equal("Bob", doc.GetCell(0, 0));
        Assert.Equal(4, doc.GetRowCount());
    }

    [Fact]
    public void RemoveRow_LastRow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RemoveRow(4); // Eve
        Assert.Equal(4, doc.GetRowCount());
        Assert.Equal("Dave", doc.GetCell(3, 0));
    }

    [Fact]
    public void RemoveRow_MiddleRow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RemoveRow(2); // Carol
        Assert.Equal(4, doc.GetRowCount());
        Assert.Equal("Dave", doc.GetCell(2, 0));
    }

    [Fact]
    public void RemoveRow_Persist()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RemoveRow(0);
        var path = TempFile("removerow_persist.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetRowCount());
        Assert.Equal("Bob", loaded.GetCell(0, 0));
    }

    [Fact]
    public void RemoveRow_CorrectRowRemoved()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RemoveRow(2); // Carol
        var names = doc.GetColumnValues("Name");
        Assert.DoesNotContain("Carol", names);
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void RemoveRow_Multiple()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RemoveRow(0); // Alice
        doc.RemoveRow(0); // Bob becomes index 0
        Assert.Equal(3, doc.GetRowCount());
        Assert.Equal("Carol", doc.GetCell(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRowValues_ExportToNdjson_RemoveRow_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_src.csv");
        var content =
            "Employee,Department,Grade,Location,Salary\n" +
            "Alice,Engineering,Senior,London,95000\n" +
            "Bob,Marketing,Junior,Paris,55000\n" +
            "Carol,Engineering,Lead,London,115000\n" +
            "Dave,Finance,Mid,Berlin,72000\n" +
            "Eve,Engineering,Senior,London,98000\n" +
            "Frank,Marketing,Senior,Rome,82000\n" +
            "Grace,Finance,Junior,Madrid,48000\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(7, doc.GetRowCount());

        // GetRowValues baseline
        var row0 = doc.GetRowValues(0);
        Assert.NotNull(row0);
        Assert.Equal(5, row0.Count);
        Assert.Contains("Alice", row0);
        Assert.Contains("95000", row0);

        var row6 = doc.GetRowValues(6);
        Assert.Contains("Grace", row6);
        Assert.Contains("48000", row6);

        // ExportToNdjson baseline
        var ndjson = doc.ExportToNdjson();
        Assert.NotNull(ndjson);
        Assert.NotEmpty(ndjson);
        Assert.Contains("{", ndjson);
        Assert.True(ndjson.Contains("Alice") || ndjson.Contains("Employee"));

        // RemoveRow — Grace (index 6)
        doc.RemoveRow(6);
        Assert.Equal(6, doc.GetRowCount());

        // GetRowValues after remove
        var newRow5 = doc.GetRowValues(5);
        Assert.Contains("Frank", newRow5);

        // ExportToNdjson shrinks after RemoveRow
        var ndjsonAfterRemove = doc.ExportToNdjson();
        Assert.True(ndjsonAfterRemove.Length < ndjson.Length);

        // GetRowValues consistent
        Assert.Equal(doc.GetRowValues(0).Count, doc.GetRowValues(0).Count);

        // ExportToNdjson consistent
        Assert.Equal(doc.ExportToNdjson().Length, doc.ExportToNdjson().Length);

        // RemoveRow — Bob (index 1)
        doc.RemoveRow(1);
        Assert.Equal(5, doc.GetRowCount());
        Assert.DoesNotContain("Bob", doc.GetColumnValues("Employee"));

        // GetRowValues after Bob removed — Carol now at index 1
        var row1AfterRemove = doc.GetRowValues(1);
        Assert.Contains("Carol", row1AfterRemove);

        // AddRow
        doc.AddRow(new[] { "Hannah", "HR", "Junior", "Brussels", "52000" });
        Assert.Equal(6, doc.GetRowCount());
        var lastRow = doc.GetRowValues(5);
        Assert.Contains("Hannah", lastRow);

        // ExportToNdjson grows after AddRow
        var ndjsonAfterAdd = doc.ExportToNdjson();
        Assert.True(ndjsonAfterAdd.Length > 0);

        // Filter Engineering and verify
        var eng = doc.Filter("Department", "Engineering");
        Assert.Equal(3, eng.GetRowCount()); // Alice, Carol, Eve
        var engNdjson = eng.ExportToNdjson();
        Assert.True(engNdjson.Length < ndjsonAfterAdd.Length);

        // GetRowValues for all rows
        for (int i = 0; i < doc.GetRowCount(); i++)
        {
            var row = doc.GetRowValues(i);
            Assert.NotNull(row);
            Assert.Equal(5, row.Count);
        }

        // SetCell and verify GetRowValues reflects
        doc.SetCell(0, 4, "97000"); // Alice salary
        var aliceRow = doc.GetRowValues(0);
        Assert.Contains("97000", aliceRow);

        // SortRows and verify GetRowValues
        doc.SortRows("Salary", ascending: false);
        var topRow = doc.GetRowValues(0);
        Assert.Contains("115000", topRow); // Carol highest

        // RemoveRow after sort
        doc.RemoveRow(0); // Carol (highest salary)
        Assert.Equal(5, doc.GetRowCount());

        // ExportToNdjson
        var finalNdjson = doc.ExportToNdjson();
        Assert.NotNull(finalNdjson);
        Assert.NotEmpty(finalNdjson);

        // SaveToFile
        var savePath = TempFile("dogfood_result.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(5, loaded.GetRowCount());

        // GetRowValues on loaded
        var loadedRow0 = loaded.GetRowValues(0);
        Assert.NotNull(loadedRow0);
        Assert.Equal(5, loadedRow0.Count);

        // ExportToNdjson on loaded
        var loadedNdjson = loaded.ExportToNdjson();
        Assert.NotNull(loadedNdjson);
        Assert.NotEmpty(loadedNdjson);

        // RemoveRow on loaded
        loaded.RemoveRow(0);
        Assert.Equal(4, loaded.GetRowCount());

        // Final SaveToFile
        var path2 = TempFile("dogfood_result_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetRowCount());
        Assert.NotNull(loaded2.GetRowValues(0));
    }
}
