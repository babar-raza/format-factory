// Tests for TsvDocument.GetRowCount, RemoveRow, GetHeaders deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R205

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R205: Tests for TsvDocument.GetRowCount, RemoveRow, GetHeaders deeper.
/// GetRowCount(): returns the number of data rows (excluding header).
/// RemoveRow(index): removes the row at the specified zero-based index.
/// GetHeaders(): returns the list of column header names.
/// Covers: GetRowCount=5; GetRowCount consistent; GetRowCount no-throw;
/// GetRowCount after AddRow increases; GetRowCount after RemoveRow decreases;
/// GetRowCount after Filter correct; GetRowCount save-load consistent;
/// GetRowCount after Clone same; GetRowCount after MergeWith sums;
/// RemoveRow no-throw; RemoveRow decreases count; RemoveRow first row;
/// RemoveRow last row; RemoveRow middle row; RemoveRow persist;
/// RemoveRow correct row removed; RemoveRow then Filter; RemoveRow multiple;
/// GetHeaders non-null; GetHeaders non-empty; GetHeaders count=4; GetHeaders consistent;
/// GetHeaders no-throw; GetHeaders contains known; GetHeaders after AddColumn grows;
/// GetHeaders after RemoveColumn shrinks; GetHeaders save-load consistent;
/// GetHeaders after Filter unchanged; GetHeaders after SortRows unchanged;
/// dogfood LoadFile→GetRowCount→RemoveRow→GetHeaders→SaveToFile pipeline.
/// </summary>
public class TsvR205GetRowCountAndRemoveRowDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR205GetRowCountAndRemoveRowDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR205_" + Guid.NewGuid().ToString("N"));
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
            "Alice\tAlpha\t92\tLondon\n" +
            "Bob\tBeta\t78\tParis\n" +
            "Carol\tAlpha\t88\tBerlin\n" +
            "Dave\tGamma\t85\tRome\n" +
            "Eve\tAlpha\t95\tMadrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_Equals5()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(5, doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetRowCount(), doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetRowCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetRowCount_AfterAddRow_Increases()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetRowCount();
        doc.AddRow(new[] { "Frank", "Delta", "80", "Oslo" });
        Assert.Equal(before + 1, doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_AfterRemoveRow_Decreases()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetRowCount();
        doc.RemoveRow(0);
        Assert.Equal(before - 1, doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_AfterFilter_Correct()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var filtered = doc.Filter("Team", "Alpha");
        Assert.Equal(3, filtered.GetRowCount());
    }

    [Fact]
    public void GetRowCount_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetRowCount();
        var path = TempFile("rowcount_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRowCount());
    }

    [Fact]
    public void GetRowCount_AfterClone_Same()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var clone = doc.Clone();
        Assert.Equal(doc.GetRowCount(), clone.GetRowCount());
    }

    [Fact]
    public void GetRowCount_AfterMergeWith_Sums()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var path2 = TempFile("second.tsv");
        File.WriteAllText(path2, "Name\tTeam\tScore\tCity\nFrank\tDelta\t80\tOslo\nGrace\tBeta\t91\tVienna\n");
        var doc2 = TsvDocument.LoadFile(path2);
        var merged = doc.MergeWith(doc2);
        Assert.Equal(doc.GetRowCount() + doc2.GetRowCount(), merged.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.RemoveRow(0));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveRow_DecreasesCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetRowCount();
        doc.RemoveRow(2);
        Assert.Equal(before - 1, doc.GetRowCount());
    }

    [Fact]
    public void RemoveRow_FirstRow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.RemoveRow(0);
        Assert.Equal(4, doc.GetRowCount());
        // Bob should now be first
        Assert.Equal("Bob", doc.GetCell(0, 0));
    }

    [Fact]
    public void RemoveRow_LastRow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.RemoveRow(4); // Eve
        Assert.Equal(4, doc.GetRowCount());
        Assert.Equal("Dave", doc.GetCell(3, 0)); // Dave still last
    }

    [Fact]
    public void RemoveRow_MiddleRow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.RemoveRow(2); // Carol
        Assert.Equal(4, doc.GetRowCount());
        // Dave should now be at index 2
        Assert.Equal("Dave", doc.GetCell(2, 0));
    }

    [Fact]
    public void RemoveRow_Persist()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.RemoveRow(0);
        var path = TempFile("removerow_persist.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetRowCount());
        Assert.Equal("Bob", loaded.GetCell(0, 0));
    }

    [Fact]
    public void RemoveRow_CorrectRowRemoved()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        // Remove Carol (index 2)
        doc.RemoveRow(2);
        var names = doc.GetColumnValues("Name");
        Assert.DoesNotContain("Carol", names);
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void RemoveRow_ThenFilter()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.RemoveRow(0); // Remove Alice (Alpha)
        var filtered = doc.Filter("Team", "Alpha");
        Assert.Equal(2, filtered.GetRowCount()); // Carol and Eve remain
    }

    [Fact]
    public void RemoveRow_Multiple()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.RemoveRow(0); // Alice
        doc.RemoveRow(0); // Bob (now index 0)
        Assert.Equal(3, doc.GetRowCount());
        Assert.Equal("Carol", doc.GetCell(0, 0));
    }

    // -------------------------------------------------------------------------
    // GetHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaders_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetHeaders());
    }

    [Fact]
    public void GetHeaders_NonEmpty()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetHeaders().Count > 0);
    }

    [Fact]
    public void GetHeaders_Count_Is4()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(4, doc.GetHeaders().Count);
    }

    [Fact]
    public void GetHeaders_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetHeaders().Count, doc.GetHeaders().Count);
    }

    [Fact]
    public void GetHeaders_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetHeaders());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHeaders_ContainsKnown()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var headers = doc.GetHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Team", headers);
        Assert.Contains("Score", headers);
        Assert.Contains("City", headers);
    }

    [Fact]
    public void GetHeaders_AfterAddColumn_Grows()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetHeaders().Count;
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU" });
        Assert.Equal(before + 1, doc.GetHeaders().Count);
        Assert.Contains("Region", doc.GetHeaders());
    }

    [Fact]
    public void GetHeaders_AfterRemoveColumn_Shrinks()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetHeaders().Count;
        doc.RemoveColumn("City");
        Assert.Equal(before - 1, doc.GetHeaders().Count);
        Assert.DoesNotContain("City", doc.GetHeaders());
    }

    [Fact]
    public void GetHeaders_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetHeaders();
        var path = TempFile("headers_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before.Count, loaded.GetHeaders().Count);
    }

    [Fact]
    public void GetHeaders_AfterFilter_Unchanged()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetHeaders().Count;
        var filtered = doc.Filter("Team", "Alpha");
        Assert.Equal(before, filtered.GetHeaders().Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRowCount_RemoveRow_GetHeaders_SaveToFile_Pipeline()
    {
        // Create comprehensive TSV
        var path = TempFile("dogfood_src.tsv");
        var content =
            "Employee\tDepartment\tGrade\tLocation\tSalary\n" +
            "Alice\tEngineering\tSenior\tLondon\t95000\n" +
            "Bob\tMarketing\tJunior\tParis\t55000\n" +
            "Carol\tEngineering\tLead\tLondon\t115000\n" +
            "Dave\tFinance\tMid\tBerlin\t72000\n" +
            "Eve\tEngineering\tSenior\tLondon\t98000\n" +
            "Frank\tMarketing\tSenior\tRome\t82000\n" +
            "Grace\tFinance\tJunior\tMadrid\t48000\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);

        // GetRowCount baseline
        Assert.Equal(7, doc.GetRowCount());

        // GetHeaders baseline
        var headers = doc.GetHeaders();
        Assert.NotNull(headers);
        Assert.Equal(5, headers.Count);
        Assert.Contains("Employee", headers);
        Assert.Contains("Department", headers);
        Assert.Contains("Salary", headers);

        // GetRowCount consistent
        Assert.Equal(doc.GetRowCount(), doc.GetRowCount());

        // GetHeaders consistent
        Assert.Equal(headers.Count, doc.GetHeaders().Count);

        // RemoveRow — Grace (index 6)
        doc.RemoveRow(6);
        Assert.Equal(6, doc.GetRowCount());
        Assert.DoesNotContain("Grace", doc.GetColumnValues("Employee"));

        // GetHeaders unchanged after RemoveRow
        Assert.Equal(5, doc.GetHeaders().Count);

        // RemoveRow — Bob (now at index 1)
        doc.RemoveRow(1);
        Assert.Equal(5, doc.GetRowCount());
        Assert.DoesNotContain("Bob", doc.GetColumnValues("Employee"));

        // GetRowCount after multiple removes
        Assert.Equal(5, doc.GetRowCount());

        // Filter Engineering
        var eng = doc.Filter("Department", "Engineering");
        Assert.Equal(3, eng.GetRowCount()); // Alice, Carol, Eve
        Assert.Equal(5, eng.GetHeaders().Count); // headers unchanged

        // RemoveRow from filtered context (original unchanged)
        var engClone = eng.Clone();
        engClone.RemoveRow(0); // Remove Alice from clone
        Assert.Equal(2, engClone.GetRowCount());
        Assert.Equal(3, eng.GetRowCount()); // original filtered doc unchanged

        // AddColumn and verify GetHeaders
        doc.AddColumn("Level", new[] { "L5", "L6", "L3", "L5", "L4" });
        Assert.Equal(6, doc.GetHeaders().Count);
        Assert.Contains("Level", doc.GetHeaders());

        // RemoveColumn and verify
        doc.RemoveColumn("Level");
        Assert.Equal(5, doc.GetHeaders().Count);

        // SortRows and verify GetHeaders unchanged
        doc.SortRows("Salary", ascending: false);
        Assert.Equal(5, doc.GetRowCount());
        Assert.Equal(5, doc.GetHeaders().Count);
        Assert.Equal("115000", doc.GetCell(0, 4)); // Carol highest

        // AddRow and verify
        doc.AddRow(new[] { "Hank", "Finance", "Mid", "Vienna", "68000" });
        Assert.Equal(6, doc.GetRowCount());

        // RemoveRow the newly added row (index 5 after sort)
        // Find Hank's index
        var empVals = doc.GetColumnValues("Employee");
        var hankIdx = empVals.IndexOf("Hank");
        if (hankIdx >= 0)
        {
            doc.RemoveRow(hankIdx);
            Assert.Equal(5, doc.GetRowCount());
        }

        // GetHeaders after all operations
        Assert.Equal(5, doc.GetHeaders().Count);
        Assert.Contains("Employee", doc.GetHeaders());

        // ExportToXml and ExportToNdjson
        var xml = doc.ExportToXml();
        Assert.NotNull(xml);
        var ndjson = doc.ExportToNdjson();
        Assert.NotNull(ndjson);

        // SaveToFile
        var savePath = TempFile("dogfood_result.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(doc.GetRowCount(), loaded.GetRowCount());
        Assert.Equal(5, loaded.GetHeaders().Count);
        Assert.Contains("Employee", loaded.GetHeaders());

        // RemoveRow on loaded
        loaded.RemoveRow(0);
        Assert.Equal(doc.GetRowCount() - 1, loaded.GetRowCount());

        // GetHeaders on loaded after RemoveRow unchanged
        Assert.Equal(5, loaded.GetHeaders().Count);

        // Final SaveToFile
        var path2 = TempFile("dogfood_result_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(5, loaded2.GetHeaders().Count);
    }
}
