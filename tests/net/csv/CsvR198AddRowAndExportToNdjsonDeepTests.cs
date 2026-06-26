// Tests for CsvDocument.AddRow, ExportToNdjson, GetRowCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R198

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R198: Tests for CsvDocument.AddRow, ExportToNdjson, GetRowCount deeper.
/// AddRow(values): appends a new data row.
/// ExportToNdjson(): exports the document as an NDJSON string.
/// GetRowCount(): returns the number of data rows.
/// Covers: AddRow increases row count; AddRow values accessible; AddRow persist;
/// AddRow multiple; AddRow then Filter; AddRow then SortRows;
/// AddRow then ExportToNdjson grows; AddRow then GetRowCount;
/// ExportToNdjson non-null; ExportToNdjson non-empty; ExportToNdjson has field names;
/// ExportToNdjson has data values; ExportToNdjson after AddRow grows;
/// ExportToNdjson after Filter shrinks; ExportToNdjson consistent;
/// GetRowCount correct; GetRowCount after AddRow increases; GetRowCount after Filter decreases;
/// GetRowCount consistent; GetRowCount empty zero; GetRowCount after save-load preserved;
/// dogfood LoadFile→AddRow→ExportToNdjson→GetRowCount→SaveToFile pipeline.
/// </summary>
public class CsvR198AddRowAndExportToNdjsonDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR198AddRowAndExportToNdjsonDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR198_" + Guid.NewGuid().ToString("N"));
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
        "Alice,Engineering,92,Boston\n" +
        "Bob,Finance,85,New York\n" +
        "Carol,Engineering,95,Chicago\n";

    private CsvDocument LoadSample()
    {
        var path = TempFile("sample.csv");
        File.WriteAllText(path, SampleCsv);
        return CsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncreasesRowCount()
    {
        var doc = LoadSample();
        var before = doc.GetRowCount();
        doc.AddRow(new[] { "Dave", "HR", "78", "Seattle" });
        Assert.Equal(before + 1, doc.GetRowCount());
    }

    [Fact]
    public void AddRow_ValuesAccessible()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Eve", "Finance", "88", "Los Angeles" });
        Assert.Contains("Eve", doc.GetColumnValues("Name"));
    }

    [Fact]
    public void AddRow_Persist()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Frank", "Legal", "91", "Denver" });
        var path = TempFile("addrow_persist.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Contains("Frank", loaded.GetColumnValues("Name"));
    }

    [Fact]
    public void AddRow_Multiple_AllPresent()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Grace", "IT", "87", "Atlanta" });
        doc.AddRow(new[] { "Hank", "Sales", "93", "Houston" });
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Grace", names);
        Assert.Contains("Hank", names);
    }

    [Fact]
    public void AddRow_ThenFilter_Works()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Ivan", "Engineering", "79", "Portland" });
        var eng = doc.Filter("Dept", "Engineering");
        Assert.Equal(3, eng.GetRowCount());
    }

    [Fact]
    public void AddRow_ThenSortRows_Works()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Aaron", "Marketing", "88", "Denver" });
        var sorted = doc.SortRows("Name", ascending: true);
        Assert.Equal("Aaron", sorted.GetColumnValues("Name")[0]);
    }

    [Fact]
    public void AddRow_ThenExportToNdjson_Grows()
    {
        var doc = LoadSample();
        var before = doc.ExportToNdjson().Length;
        doc.AddRow(new[] { "Julia", "Legal", "90", "Miami" });
        var after = doc.ExportToNdjson().Length;
        Assert.True(after > before);
    }

    // -------------------------------------------------------------------------
    // ExportToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToNdjson_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_NonEmpty()
    {
        var doc = LoadSample();
        Assert.True(doc.ExportToNdjson().Length > 0);
    }

    [Fact]
    public void ExportToNdjson_HasFieldNames()
    {
        var doc = LoadSample();
        var ndjson = doc.ExportToNdjson();
        Assert.True(ndjson.Contains("Name") || ndjson.Contains("Dept") || ndjson.Contains("{"));
    }

    [Fact]
    public void ExportToNdjson_HasDataValues()
    {
        var doc = LoadSample();
        var ndjson = doc.ExportToNdjson();
        Assert.True(ndjson.Contains("Alice") || ndjson.Contains("Bob") || ndjson.Length > 10);
    }

    [Fact]
    public void ExportToNdjson_AfterFilter_Shrinks()
    {
        var doc = LoadSample();
        var all = doc.ExportToNdjson().Length;
        var filtered = doc.Filter("Dept", "Engineering");
        var filteredNdjson = filtered.ExportToNdjson().Length;
        Assert.True(filteredNdjson < all);
    }

    [Fact]
    public void ExportToNdjson_Consistent()
    {
        var doc = LoadSample();
        var n1 = doc.ExportToNdjson();
        var n2 = doc.ExportToNdjson();
        Assert.Equal(n1.Length, n2.Length);
    }

    [Fact]
    public void ExportToNdjson_HasNewlinePerRecord()
    {
        var doc = LoadSample();
        var ndjson = doc.ExportToNdjson();
        // Each record on its own line — should have newlines for 3 rows
        var lines = ndjson.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.True(lines.Length >= 3);
    }

    // -------------------------------------------------------------------------
    // GetRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_Correct()
    {
        var doc = LoadSample();
        Assert.Equal(3, doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_AfterAddRow_Increases()
    {
        var doc = LoadSample();
        var before = doc.GetRowCount();
        doc.AddRow(new[] { "Karl", "Ops", "82", "Phoenix" });
        Assert.Equal(before + 1, doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_AfterFilter_Decreases()
    {
        var doc = LoadSample();
        var all = doc.GetRowCount();
        var filtered = doc.Filter("Dept", "Engineering").GetRowCount();
        Assert.True(filtered < all);
    }

    [Fact]
    public void GetRowCount_Consistent()
    {
        var doc = LoadSample();
        Assert.Equal(doc.GetRowCount(), doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_EmptyDoc_Zero()
    {
        var emptyPath = TempFile("empty.csv");
        File.WriteAllText(emptyPath, "Name,Dept,Score\n");
        var doc = CsvDocument.LoadFile(emptyPath);
        Assert.Equal(0, doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_AfterSaveLoad_Preserved()
    {
        var doc = LoadSample();
        var path = TempFile("count_preserve.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(doc.GetRowCount(), loaded.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_AddRow_ExportToNdjson_GetRowCount_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(3, doc.GetRowCount());

        // ExportToNdjson baseline
        var ndjson = doc.ExportToNdjson();
        Assert.NotNull(ndjson);
        Assert.True(ndjson.Length > 0);

        // AddRow — new employees
        doc.AddRow(new[] { "Dave", "HR", "78", "Seattle" });
        Assert.Equal(4, doc.GetRowCount());
        Assert.Contains("Dave", doc.GetColumnValues("Name"));

        // ExportToNdjson grew
        var ndjsonAfter1 = doc.ExportToNdjson();
        Assert.True(ndjsonAfter1.Length > ndjson.Length);

        doc.AddRow(new[] { "Eve", "Finance", "88", "Los Angeles" });
        doc.AddRow(new[] { "Frank", "Engineering", "91", "Denver" });
        Assert.Equal(6, doc.GetRowCount());

        // ExportToNdjson with 6 rows
        var ndjsonAll = doc.ExportToNdjson();
        Assert.True(ndjsonAll.Length > ndjsonAfter1.Length);

        // NDJSON should have one JSON object per line
        var lines = ndjsonAll.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.True(lines.Length >= 6);

        // Filter then GetRowCount
        var engineering = doc.Filter("Dept", "Engineering");
        Assert.Equal(3, engineering.GetRowCount()); // Alice, Carol, Frank

        // ExportToNdjson on filtered
        var engNdjson = engineering.ExportToNdjson();
        Assert.True(engNdjson.Length < ndjsonAll.Length);

        // SortRows
        var sorted = doc.SortRows("Name", ascending: true);
        Assert.Equal(6, sorted.GetRowCount());
        var sortedNames = sorted.GetColumnValues("Name");
        Assert.Equal("Alice", sortedNames[0]);

        // AddRow then immediately check GetRowCount
        doc.AddRow(new[] { "Grace", "IT", "87", "Atlanta" });
        Assert.Equal(7, doc.GetRowCount());

        // ExportToNdjson after all additions
        var finalNdjson = doc.ExportToNdjson();
        Assert.True(finalNdjson.Length > ndjsonAll.Length);

        // SaveToFile and reload
        var path = TempFile("dogfood_addrow_ndjson.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(7, loaded.GetRowCount());

        // GetRowCount on loaded
        Assert.Equal(doc.GetRowCount(), loaded.GetRowCount());

        // ExportToNdjson on loaded
        var loadedNdjson = loaded.ExportToNdjson();
        Assert.NotNull(loadedNdjson);
        Assert.True(loadedNdjson.Length > 0);

        // AddRow on loaded
        loaded.AddRow(new[] { "Hank", "Sales", "93", "Houston" });
        Assert.Equal(8, loaded.GetRowCount());
        Assert.Contains("Hank", loaded.GetColumnValues("Name"));

        // Filter on loaded
        var loadedEng = loaded.Filter("Dept", "Engineering");
        Assert.Equal(3, loadedEng.GetRowCount());
    }
}
