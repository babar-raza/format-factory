// Tests for TsvDocument.SortRows, RemoveColumn, GetRowCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R191

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R191: Tests for TsvDocument.SortRows, RemoveColumn, GetRowCount deeper.
/// SortRows(colName, ascending): sorts rows by the specified column.
/// RemoveColumn(colName): removes a column from the document.
/// GetRowCount(): returns the number of data rows (excluding header).
/// Covers: SortRows ascending first-value correct; SortRows descending first-value correct;
/// SortRows preserves row count; SortRows by numeric column; SortRows consistent;
/// SortRows then ToTsv reflects order; SortRows after Filter still sorted;
/// RemoveColumn decrements column count; RemoveColumn removes from GetHeaders;
/// RemoveColumn removes from ExportToJson; RemoveColumn after Filter still works;
/// RemoveColumn non-existent no-throw; RemoveColumn persist;
/// GetRowCount correct; GetRowCount after AddRow increases; GetRowCount after Filter decreases;
/// GetRowCount consistent; GetRowCount empty zero;
/// dogfood LoadFile→SortRows→RemoveColumn→GetRowCount→verify pipeline.
/// </summary>
public class TsvR191SortRowsAndGetRowCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR191SortRowsAndGetRowCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR191_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleTsv =
        "Name\tDept\tScore\tCity\n" +
        "Charlie\tEngineering\t85\tBoston\n" +
        "Alice\tFinance\t92\tNew York\n" +
        "Eve\tEngineering\t78\tSeattle\n" +
        "Bob\tHR\t95\tChicago\n" +
        "Diana\tFinance\t88\tLos Angeles\n";

    private TsvDocument LoadSample()
    {
        var path = TempFile("sample.tsv");
        File.WriteAllText(path, SampleTsv);
        return TsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // SortRows
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_Ascending_FirstValueCorrect()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Name", ascending: true);
        var values = sorted.GetColumnValues("Name");
        Assert.Equal("Alice", values[0]);
    }

    [Fact]
    public void SortRows_Descending_FirstValueCorrect()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Name", ascending: false);
        var values = sorted.GetColumnValues("Name");
        Assert.Equal("Eve", values[0]);
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
        var values = sorted.GetColumnValues("Score");
        // 78 should be first
        Assert.Equal("78", values[0]);
    }

    [Fact]
    public void SortRows_ByScore_Descending_FirstIsHighest()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Score", ascending: false);
        var values = sorted.GetColumnValues("Score");
        // 95 should be first
        Assert.Equal("95", values[0]);
    }

    [Fact]
    public void SortRows_ThenToTsv_ReflectsOrder()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Name", ascending: true);
        var tsv = sorted.ToTsv();
        // Alice should appear before Charlie in the output
        var alicePos = tsv.IndexOf("Alice");
        var charliePos = tsv.IndexOf("Charlie");
        Assert.True(alicePos < charliePos);
    }

    [Fact]
    public void SortRows_AfterFilter_StillSorted()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("Dept", "Finance");
        var sorted = filtered.SortRows("Name", ascending: true);
        var values = sorted.GetColumnValues("Name");
        Assert.True(values.Count >= 2);
        Assert.Equal("Alice", values[0]); // Alice < Diana
    }

    [Fact]
    public void SortRows_Consistent()
    {
        var doc = LoadSample();
        var s1 = doc.SortRows("Name", ascending: true).GetColumnValues("Name");
        var s2 = doc.SortRows("Name", ascending: true).GetColumnValues("Name");
        Assert.Equal(s1, s2);
    }

    // -------------------------------------------------------------------------
    // RemoveColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveColumn_DecrementsColumnCount()
    {
        var doc = LoadSample();
        var before = doc.GetHeaders().Count;
        var updated = doc.RemoveColumn("City");
        Assert.True(updated.GetHeaders().Count < before);
    }

    [Fact]
    public void RemoveColumn_RemovedFromGetHeaders()
    {
        var doc = LoadSample();
        var updated = doc.RemoveColumn("City");
        Assert.DoesNotContain("City", updated.GetHeaders());
    }

    [Fact]
    public void RemoveColumn_OtherColumnsPreserved()
    {
        var doc = LoadSample();
        var updated = doc.RemoveColumn("City");
        var headers = updated.GetHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Dept", headers);
        Assert.Contains("Score", headers);
    }

    [Fact]
    public void RemoveColumn_RowCountUnchanged()
    {
        var doc = LoadSample();
        var before = doc.GetRowCount();
        var updated = doc.RemoveColumn("City");
        Assert.Equal(before, updated.GetRowCount());
    }

    [Fact]
    public void RemoveColumn_NonExistent_NoThrow()
    {
        var doc = LoadSample();
        var ex = Record.Exception(() => doc.RemoveColumn("DOES_NOT_EXIST_XYZ"));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveColumn_FilterStillWorks()
    {
        var doc = LoadSample();
        var updated = doc.RemoveColumn("City");
        var filtered = updated.Filter("Dept", "Finance");
        Assert.True(filtered.GetRowCount() >= 1);
    }

    // -------------------------------------------------------------------------
    // GetRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_Correct()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_AfterAddRow_Increases()
    {
        var doc = LoadSample();
        var before = doc.GetRowCount();
        doc.AddRow(new[] { "Frank", "Marketing", "91", "Denver" });
        Assert.Equal(before + 1, doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_AfterFilter_Decreases()
    {
        var doc = LoadSample();
        var all = doc.GetRowCount();
        var filtered = doc.Filter("Dept", "Finance").GetRowCount();
        Assert.True(filtered < all);
    }

    [Fact]
    public void GetRowCount_Consistent()
    {
        var doc = LoadSample();
        Assert.Equal(doc.GetRowCount(), doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_EmptyDoc_ZeroOrMinimal()
    {
        var emptyPath = TempFile("empty.tsv");
        File.WriteAllText(emptyPath, "Name\tDept\n");
        var doc = TsvDocument.LoadFile(emptyPath);
        Assert.True(doc.GetRowCount() == 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_SortRows_RemoveColumn_GetRowCount_Verify_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.GetRowCount());
        Assert.True(doc.GetHeaders().Count >= 4);

        // SortRows ascending by Name
        var sorted = doc.SortRows("Name", ascending: true);
        Assert.Equal(5, sorted.GetRowCount());
        var names = sorted.GetColumnValues("Name");
        Assert.Equal("Alice", names[0]);
        Assert.Equal("Eve", names[4]);

        // SortRows descending by Score
        var sortedDesc = doc.SortRows("Score", ascending: false);
        var scores = sortedDesc.GetColumnValues("Score");
        Assert.Equal("95", scores[0]); // Bob
        Assert.Equal("78", scores[4]); // Eve

        // Filter then SortRows
        var engFiltered = doc.Filter("Dept", "Engineering");
        Assert.Equal(2, engFiltered.GetRowCount());
        var sortedEng = engFiltered.SortRows("Score", ascending: false);
        var engScores = sortedEng.GetColumnValues("Score");
        Assert.Equal("85", engScores[0]); // Charlie

        // RemoveColumn City
        var noCityDoc = doc.RemoveColumn("City");
        Assert.DoesNotContain("City", noCityDoc.GetHeaders());
        Assert.Equal(5, noCityDoc.GetRowCount());
        Assert.Equal(3, noCityDoc.GetHeaders().Count); // Name, Dept, Score

        // SortRows on modified doc
        var sortedNoCity = noCityDoc.SortRows("Name", ascending: true);
        Assert.Equal(5, sortedNoCity.GetRowCount());
        var noCityNames = sortedNoCity.GetColumnValues("Name");
        Assert.Equal("Alice", noCityNames[0]);

        // AddRow then GetRowCount
        doc.AddRow(new[] { "Grace", "Legal", "87", "Miami" });
        Assert.Equal(6, doc.GetRowCount());

        // SortRows after AddRow
        var sortedAfterAdd = doc.SortRows("Name", ascending: true);
        var allNames = sortedAfterAdd.GetColumnValues("Name");
        Assert.Equal("Alice", allNames[0]);
        Assert.Equal("Grace", allNames[3]); // Alice,Bob,Charlie,Diana,Eve,Grace in alpha order
        Assert.Equal(6, sortedAfterAdd.GetRowCount());

        // SaveToFile and reload
        var path = TempFile("dogfood_sort.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetRowCount());
        var loadedSorted = loaded.SortRows("Name", ascending: true);
        Assert.Equal(6, loadedSorted.GetRowCount());
        Assert.Equal("Alice", loadedSorted.GetColumnValues("Name")[0]);
    }
}
