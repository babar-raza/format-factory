// Tests for TsvDocument.ExportToNdjson, RemoveRow, GetColumnCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R200

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R200: Tests for TsvDocument.ExportToNdjson, RemoveRow, GetColumnCount deeper.
/// ExportToNdjson(): exports the document as newline-delimited JSON records.
/// RemoveRow(rowIndex): removes the row at the specified index.
/// GetColumnCount(): returns the number of columns (headers).
/// Covers: ExportToNdjson non-null; ExportToNdjson non-empty; ExportToNdjson has field names;
/// ExportToNdjson has data values; ExportToNdjson newline per record; ExportToNdjson after AddRow grows;
/// ExportToNdjson after Filter shrinks; ExportToNdjson consistent; ExportToNdjson has curly braces;
/// RemoveRow decreases count; RemoveRow removes correct row; RemoveRow no-throw;
/// RemoveRow first; RemoveRow last; RemoveRow persist; RemoveRow then Filter; RemoveRow multiple;
/// GetColumnCount correct; GetColumnCount after AddColumn increases; GetColumnCount after RenameColumn unchanged;
/// GetColumnCount consistent; GetColumnCount save-load preserved; GetColumnCount matches headers count;
/// dogfood LoadFile→ExportToNdjson→RemoveRow→GetColumnCount→SaveToFile pipeline.
/// </summary>
public class TsvR200ExportToNdjsonAndRemoveRowDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR200ExportToNdjsonAndRemoveRowDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR200_" + Guid.NewGuid().ToString("N"));
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
            "Name\tTeam\tScore\tCity\n" +
            "Alice\tEngineering\t92\tLondon\n" +
            "Bob\tMarketing\t78\tParis\n" +
            "Carol\tEngineering\t88\tBerlin\n" +
            "Dave\tFinance\t85\tRome\n" +
            "Eve\tEngineering\t95\tMadrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // ExportToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToNdjson_NonNull()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.NotNull(doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_NonEmpty()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.NotEmpty(doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_HasFieldNames()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var ndjson = doc.ExportToNdjson();
        Assert.True(ndjson.Contains("Name") || ndjson.Contains("Team") || ndjson.Contains("Score"));
    }

    [Fact]
    public void ExportToNdjson_HasDataValues()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var ndjson = doc.ExportToNdjson();
        Assert.True(ndjson.Contains("Alice") || ndjson.Contains("Bob") || ndjson.Contains("Carol"));
    }

    [Fact]
    public void ExportToNdjson_HasCurlyBraces()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var ndjson = doc.ExportToNdjson();
        Assert.Contains("{", ndjson);
        Assert.Contains("}", ndjson);
    }

    [Fact]
    public void ExportToNdjson_AfterAddRow_Grows()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.ExportToNdjson().Length;
        doc.AddRow(new[] { "Frank", "HR", "77", "Oslo" });
        var after = doc.ExportToNdjson().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToNdjson_AfterFilter_Shrinks()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.ExportToNdjson().Length;
        var filtered = doc.Filter("Team", "Engineering");
        var after = filtered.ExportToNdjson().Length;
        Assert.True(after < before);
    }

    [Fact]
    public void ExportToNdjson_Consistent()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var n1 = doc.ExportToNdjson();
        var n2 = doc.ExportToNdjson();
        Assert.Equal(n1.Length, n2.Length);
    }

    [Fact]
    public void ExportToNdjson_NewlinePerRecord()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var ndjson = doc.ExportToNdjson();
        var lineCount = ndjson.Split('\n').Length;
        // Should have at least as many lines as rows (each row = 1 JSON object)
        Assert.True(lineCount >= doc.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_DecreasesCount()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.GetRowCount();
        doc.RemoveRow(1);
        Assert.Equal(before - 1, doc.GetRowCount());
    }

    [Fact]
    public void RemoveRow_RemovesCorrectRow()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var nameAt2 = doc.GetCell(2, 0);
        doc.RemoveRow(1);
        Assert.Equal(nameAt2, doc.GetCell(1, 0));
    }

    [Fact]
    public void RemoveRow_NoThrow()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.RemoveRow(1));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveRow_First_Works()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var nameAt1 = doc.GetCell(1, 0);
        var before = doc.GetRowCount();
        doc.RemoveRow(0);
        Assert.Equal(before - 1, doc.GetRowCount());
        Assert.Equal(nameAt1, doc.GetCell(0, 0));
    }

    [Fact]
    public void RemoveRow_Last_Works()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.GetRowCount();
        doc.RemoveRow(before - 1);
        Assert.Equal(before - 1, doc.GetRowCount());
    }

    [Fact]
    public void RemoveRow_Persist()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.RemoveRow(1); // Remove Bob
        var savePath = TempFile("remove_persist.tsv");
        doc.SaveToFile(savePath);
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(4, loaded.GetRowCount());
    }

    [Fact]
    public void RemoveRow_Multiple_ReducesCountByN()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.GetRowCount();
        doc.RemoveRow(0);
        doc.RemoveRow(0); // remove what was index 1
        Assert.Equal(before - 2, doc.GetRowCount());
    }

    [Fact]
    public void RemoveRow_ThenFilter_Works()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.RemoveRow(1); // Remove Bob (Marketing)
        var mktRows = doc.Filter("Team", "Marketing");
        Assert.Equal(0, mktRows.GetRowCount()); // No Marketing left
    }

    // -------------------------------------------------------------------------
    // GetColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_Correct()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(4, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_AfterAddColumn_Increases()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.GetColumnCount();
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU" });
        Assert.Equal(before + 1, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_AfterRenameColumn_Unchanged()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.GetColumnCount();
        doc.RenameColumn("Name", "FullName");
        Assert.Equal(before, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_Consistent()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(doc.GetColumnCount(), doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_MatchesHeadersCount()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(doc.GetHeaders().Count, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_SaveLoadPreserved()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.AddColumn("Extra", new[] { "A", "B", "C", "D", "E" });
        var count = doc.GetColumnCount();
        var savePath = TempFile("colcount_persist.tsv");
        doc.SaveToFile(savePath);
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(count, loaded.GetColumnCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ExportToNdjson_RemoveRow_GetColumnCount_SaveToFile_Pipeline()
    {
        // Create dataset
        var path = TempFile("dogfood_src.tsv");
        var content =
            "ID\tEmployee\tDept\tSalary\tYears\n" +
            "001\tAaron\tEngineering\t95000\t5\n" +
            "002\tBrianna\tDesign\t72000\t3\n" +
            "003\tCaleb\tEngineering\t88000\t7\n" +
            "004\tDiane\tHR\t68000\t2\n" +
            "005\tEthan\tEngineering\t102000\t9\n" +
            "006\tFiona\tDesign\t85000\t6\n" +
            "007\tGeorge\tHR\t71000\t4\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(7, doc.GetRowCount());

        // GetColumnCount
        Assert.Equal(5, doc.GetColumnCount());
        Assert.Equal(doc.GetHeaders().Count, doc.GetColumnCount());

        // ExportToNdjson baseline
        var ndjson = doc.ExportToNdjson();
        Assert.NotNull(ndjson);
        Assert.NotEmpty(ndjson);
        Assert.Contains("{", ndjson);
        Assert.Contains("Aaron", ndjson);
        Assert.Contains("Employee", ndjson);

        // RemoveRow — remove Diane (HR, index 3)
        var nameAtIdx4 = doc.GetCell(4, 1); // Ethan
        doc.RemoveRow(3);
        Assert.Equal(6, doc.GetRowCount());
        Assert.Equal(nameAtIdx4, doc.GetCell(3, 1)); // Ethan shifted

        // ExportToNdjson after RemoveRow shrinks
        var ndjsonAfterRemove = doc.ExportToNdjson();
        Assert.True(ndjsonAfterRemove.Length < ndjson.Length);
        Assert.False(ndjsonAfterRemove.Contains("Diane"));

        // RemoveRow — remove last row
        doc.RemoveRow(doc.GetRowCount() - 1); // Remove George
        Assert.Equal(5, doc.GetRowCount());

        // GetColumnCount unchanged after RemoveRow
        Assert.Equal(5, doc.GetColumnCount());

        // AddColumn — Location
        doc.AddColumn("Location", new[] { "Berlin", "Paris", "London", "Rome", "Madrid" });
        Assert.Equal(6, doc.GetColumnCount());
        var ndjsonAfterCol = doc.ExportToNdjson();
        Assert.True(ndjsonAfterCol.Length > ndjsonAfterRemove.Length);
        Assert.Contains("Location", ndjsonAfterCol);

        // RenameColumn
        doc.RenameColumn("Dept", "Department");
        Assert.Equal(6, doc.GetColumnCount()); // unchanged
        var ndjsonAfterRename = doc.ExportToNdjson();
        Assert.Contains("Department", ndjsonAfterRename);

        // AddRow
        doc.AddRow(new[] { "008", "Hannah", "Design", "78000", "4", "Stockholm" });
        Assert.Equal(6, doc.GetRowCount());
        var ndjsonAfterAddRow = doc.ExportToNdjson();
        Assert.True(ndjsonAfterAddRow.Length > ndjsonAfterRename.Length);
        Assert.Contains("Hannah", ndjsonAfterAddRow);

        // Filter Engineering
        var engRows = doc.Filter("Department", "Engineering");
        Assert.Equal(2, engRows.GetRowCount()); // Aaron and Caleb (Ethan removed)
        var engNdjson = engRows.ExportToNdjson();
        Assert.Contains("Engineering", engNdjson);

        // SortRows
        doc.SortRows("Employee", ascending: true);
        Assert.Equal("Aaron", doc.GetCell(0, 1));
        Assert.Equal(6, doc.GetColumnCount());

        // GetColumnCount matches headers
        Assert.Equal(doc.GetHeaders().Count, doc.GetColumnCount());

        // SaveToFile
        var savePath = TempFile("dogfood_modified.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(6, loaded.GetRowCount());
        Assert.Equal(6, loaded.GetColumnCount());

        // ExportToNdjson on loaded
        var loadedNdjson = loaded.ExportToNdjson();
        Assert.NotNull(loadedNdjson);
        Assert.Contains("{", loadedNdjson);
        Assert.Contains("Hannah", loadedNdjson);

        // RemoveRow on loaded
        var loadedBefore = loaded.GetRowCount();
        loaded.RemoveRow(0);
        Assert.Equal(loadedBefore - 1, loaded.GetRowCount());

        // GetColumnCount on loaded
        Assert.Equal(6, loaded.GetColumnCount());

        // Final SaveToFile
        var finalPath = TempFile("dogfood_final.tsv");
        loaded.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = TsvDocument.LoadFile(finalPath);
        Assert.Equal(loaded.GetRowCount(), final.GetRowCount());
    }
}
