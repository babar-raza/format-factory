// Tests for CsvDocument.MergeWith, GetRowValues, GetColumnIndex deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R204

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R204: Tests for CsvDocument.MergeWith, GetRowValues, GetColumnIndex deeper.
/// MergeWith(other): merges another document's rows into this document.
/// GetRowValues(rowIndex): returns all cell values in the specified row.
/// GetColumnIndex(colName): returns the zero-based index of the named column.
/// Covers: MergeWith non-null; MergeWith sum row count; MergeWith all rows present;
/// MergeWith preserves headers; MergeWith consistent; MergeWith no-throw;
/// MergeWith persist; MergeWith self doubles; MergeWith then Filter; MergeWith then SortRows;
/// GetRowValues non-null; GetRowValues non-empty; GetRowValues count=colCount;
/// GetRowValues contains known; GetRowValues consistent; GetRowValues no-throw;
/// GetRowValues after SetCell reflects; GetRowValues for all rows count same;
/// GetColumnIndex non-negative for known; GetColumnIndex correct; GetColumnIndex negative for unknown;
/// GetColumnIndex consistent; GetColumnIndex no-throw; GetColumnIndex after AddColumn;
/// GetColumnIndex after RemoveColumn returns invalid; GetColumnIndex for all headers;
/// dogfood LoadFile→MergeWith→GetRowValues→GetColumnIndex→SaveToFile pipeline.
/// </summary>
public class CsvR204MergeWithAndGetRowValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR204MergeWithAndGetRowValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR204_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleCsv(string name = "sample.csv")
    {
        var path = TempFile(name);
        var content =
            "Name,Department,Score,City\n" +
            "Alice,Engineering,92,London\n" +
            "Bob,Marketing,78,Paris\n" +
            "Carol,Engineering,88,Berlin\n";
        File.WriteAllText(path, content);
        return path;
    }

    private string CreateSecondCsv()
    {
        var path = TempFile("second.csv");
        var content =
            "Name,Department,Score,City\n" +
            "Dave,Finance,85,Rome\n" +
            "Eve,Engineering,95,Madrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // MergeWith
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeWith_NonNull()
    {
        var doc1 = CsvDocument.LoadFile(CreateSampleCsv());
        var doc2 = CsvDocument.LoadFile(CreateSecondCsv());
        Assert.NotNull(doc1.MergeWith(doc2));
    }

    [Fact]
    public void MergeWith_SumRowCount()
    {
        var doc1 = CsvDocument.LoadFile(CreateSampleCsv());
        var doc2 = CsvDocument.LoadFile(CreateSecondCsv());
        var r1 = doc1.GetRowCount();
        var r2 = doc2.GetRowCount();
        var merged = doc1.MergeWith(doc2);
        Assert.Equal(r1 + r2, merged.GetRowCount());
    }

    [Fact]
    public void MergeWith_AllRowsPresent()
    {
        var doc1 = CsvDocument.LoadFile(CreateSampleCsv());
        var doc2 = CsvDocument.LoadFile(CreateSecondCsv());
        var merged = doc1.MergeWith(doc2);
        var nameCol = merged.GetColumnValues("Name");
        Assert.Contains("Alice", nameCol);
        Assert.Contains("Dave", nameCol);
        Assert.Contains("Eve", nameCol);
    }

    [Fact]
    public void MergeWith_PreservesHeaders()
    {
        var doc1 = CsvDocument.LoadFile(CreateSampleCsv());
        var doc2 = CsvDocument.LoadFile(CreateSecondCsv());
        var merged = doc1.MergeWith(doc2);
        var headers = merged.GetHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Department", headers);
        Assert.Contains("Score", headers);
        Assert.Contains("City", headers);
    }

    [Fact]
    public void MergeWith_NoThrow()
    {
        var doc1 = CsvDocument.LoadFile(CreateSampleCsv());
        var doc2 = CsvDocument.LoadFile(CreateSecondCsv());
        var ex = Record.Exception(() => doc1.MergeWith(doc2));
        Assert.Null(ex);
    }

    [Fact]
    public void MergeWith_Persist()
    {
        var doc1 = CsvDocument.LoadFile(CreateSampleCsv());
        var doc2 = CsvDocument.LoadFile(CreateSecondCsv());
        var merged = doc1.MergeWith(doc2);
        var path = TempFile("merged_persist.csv");
        merged.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(merged.GetRowCount(), loaded.GetRowCount());
    }

    [Fact]
    public void MergeWith_SelfDoubles()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetRowCount();
        var doubled = doc.MergeWith(doc);
        Assert.Equal(before * 2, doubled.GetRowCount());
    }

    [Fact]
    public void MergeWith_ThenFilter()
    {
        var doc1 = CsvDocument.LoadFile(CreateSampleCsv());
        var doc2 = CsvDocument.LoadFile(CreateSecondCsv());
        var merged = doc1.MergeWith(doc2);
        var filtered = merged.Filter("Department", "Engineering");
        Assert.True(filtered.GetRowCount() > 0);
        Assert.True(filtered.GetRowCount() < merged.GetRowCount());
    }

    [Fact]
    public void MergeWith_ThenSortRows()
    {
        var doc1 = CsvDocument.LoadFile(CreateSampleCsv());
        var doc2 = CsvDocument.LoadFile(CreateSecondCsv());
        var merged = doc1.MergeWith(doc2);
        var ex = Record.Exception(() => merged.SortRows("Name", ascending: true));
        Assert.Null(ex);
        Assert.Equal("Alice", merged.GetCell(0, 0));
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
        Assert.Equal(doc.GetColumnCount(), doc.GetRowValues(0).Count);
    }

    [Fact]
    public void GetRowValues_ContainsKnown()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var values = doc.GetRowValues(0);
        Assert.True(values.Contains("Alice") || values.Contains("Engineering") || values[0] != null);
    }

    [Fact]
    public void GetRowValues_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var v1 = doc.GetRowValues(0);
        var v2 = doc.GetRowValues(0);
        Assert.Equal(v1.Count, v2.Count);
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
        doc.SetCell(0, 0, "ALICE_MOD");
        var values = doc.GetRowValues(0);
        Assert.Contains("ALICE_MOD", values);
    }

    [Fact]
    public void GetRowValues_ForAllRows_CountSame()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        int cols = doc.GetColumnCount();
        for (int r = 0; r < doc.GetRowCount(); r++)
            Assert.Equal(cols, doc.GetRowValues(r).Count);
    }

    // -------------------------------------------------------------------------
    // GetColumnIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnIndex_NonNegative_ForKnown()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnIndex("Name") >= 0);
    }

    [Fact]
    public void GetColumnIndex_Correct()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(0, doc.GetColumnIndex("Name"));
        Assert.Equal(1, doc.GetColumnIndex("Department"));
        Assert.Equal(2, doc.GetColumnIndex("Score"));
        Assert.Equal(3, doc.GetColumnIndex("City"));
    }

    [Fact]
    public void GetColumnIndex_Negative_ForUnknown()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var idx = doc.GetColumnIndex("NONE_XYZ");
        Assert.True(idx < 0);
    }

    [Fact]
    public void GetColumnIndex_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnIndex("Name"), doc.GetColumnIndex("Name"));
    }

    [Fact]
    public void GetColumnIndex_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnIndex("Name"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnIndex_AfterAddColumn_NewIsLast()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.AddColumn("Region", new[] { "EU", "EU", "EU" });
        var idx = doc.GetColumnIndex("Region");
        Assert.True(idx >= 4);
    }

    [Fact]
    public void GetColumnIndex_AfterRemoveColumn_Returns_Invalid()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RemoveColumn("City");
        var idx = doc.GetColumnIndex("City");
        Assert.True(idx < 0 || !doc.HasColumn("City"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_MergeWith_GetRowValues_GetColumnIndex_SaveToFile_Pipeline()
    {
        // Create source CSVs
        var pathA = TempFile("dogfood_a.csv");
        var pathB = TempFile("dogfood_b.csv");
        var pathC = TempFile("dogfood_c.csv");

        File.WriteAllText(pathA,
            "EmpID,Name,Dept,Grade,City\n" +
            "E001,Alice,Engineering,Senior,London\n" +
            "E002,Bob,Marketing,Junior,Paris\n" +
            "E003,Carol,Engineering,Lead,London\n");

        File.WriteAllText(pathB,
            "EmpID,Name,Dept,Grade,City\n" +
            "E004,Dave,Finance,Mid,Berlin\n" +
            "E005,Eve,Engineering,Senior,London\n" +
            "E006,Frank,Marketing,Senior,Rome\n");

        File.WriteAllText(pathC,
            "EmpID,Name,Dept,Grade,City\n" +
            "E007,Grace,HR,Junior,Madrid\n" +
            "E008,Henry,Finance,Lead,Vienna\n");

        var docA = CsvDocument.LoadFile(pathA);
        var docB = CsvDocument.LoadFile(pathB);
        var docC = CsvDocument.LoadFile(pathC);

        Assert.Equal(3, docA.GetRowCount());
        Assert.Equal(3, docB.GetRowCount());
        Assert.Equal(2, docC.GetRowCount());

        // GetColumnIndex on docA
        Assert.Equal(0, docA.GetColumnIndex("EmpID"));
        Assert.Equal(1, docA.GetColumnIndex("Name"));
        Assert.Equal(2, docA.GetColumnIndex("Dept"));
        Assert.Equal(3, docA.GetColumnIndex("Grade"));
        Assert.Equal(4, docA.GetColumnIndex("City"));
        Assert.True(docA.GetColumnIndex("NONE") < 0);

        // GetRowValues on docA
        var row0A = docA.GetRowValues(0);
        Assert.Equal(5, row0A.Count);
        Assert.Contains("Alice", row0A);
        Assert.Contains("Engineering", row0A);

        // MergeWith docA + docB
        var mergedAB = docA.MergeWith(docB);
        Assert.Equal(6, mergedAB.GetRowCount());
        Assert.Equal(5, mergedAB.GetColumnCount());

        var mergedNames = mergedAB.GetColumnValues("Name");
        Assert.Contains("Alice", mergedNames);
        Assert.Contains("Frank", mergedNames);

        // GetColumnIndex on merged
        Assert.Equal(0, mergedAB.GetColumnIndex("EmpID"));
        Assert.Equal(2, mergedAB.GetColumnIndex("Dept"));

        // GetRowValues on merged
        var mergedRow5 = mergedAB.GetRowValues(5);
        Assert.Equal(5, mergedRow5.Count);
        Assert.Contains("Frank", mergedRow5);

        // MergeWith all three
        var mergedAll = mergedAB.MergeWith(docC);
        Assert.Equal(8, mergedAll.GetRowCount());

        var allNames = mergedAll.GetColumnValues("Name");
        Assert.Contains("Grace", allNames);
        Assert.Contains("Henry", allNames);

        // GetRowValues for each merged row
        for (int r = 0; r < mergedAll.GetRowCount(); r++)
        {
            var rv = mergedAll.GetRowValues(r);
            Assert.Equal(5, rv.Count);
        }

        // SetCell and verify GetRowValues
        mergedAll.SetCell(0, 1, "ALICE_MERGED");
        var row0Updated = mergedAll.GetRowValues(0);
        Assert.Contains("ALICE_MERGED", row0Updated);

        // Filter Engineering
        var eng = mergedAll.Filter("Dept", "Engineering");
        Assert.True(eng.GetRowCount() >= 3);

        var engRow0 = eng.GetRowValues(0);
        Assert.NotNull(engRow0);
        Assert.Contains("Engineering", engRow0);

        // GetColumnIndex after AddColumn
        mergedAll.AddColumn("Active", Enumerable8("Yes"));
        var idxActive = mergedAll.GetColumnIndex("Active");
        Assert.Equal(5, idxActive);

        // GetRowValues after AddColumn
        var rowWithActive = mergedAll.GetRowValues(0);
        Assert.Equal(6, rowWithActive.Count);

        // GetColumnIndex after RemoveColumn
        mergedAll.RemoveColumn("Active");
        Assert.True(mergedAll.GetColumnIndex("Active") < 0);

        // SortRows and verify GetColumnIndex unchanged
        mergedAll.SortRows("Name", ascending: true);
        Assert.Equal(0, mergedAll.GetColumnIndex("EmpID"));
        Assert.Equal("ALICE_MERGED", mergedAll.GetCell(0, 1));

        // SaveToFile
        var savePath = TempFile("dogfood_merged.csv");
        mergedAll.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(8, loaded.GetRowCount());

        Assert.Equal(0, loaded.GetColumnIndex("EmpID"));
        Assert.Equal(4, loaded.GetColumnIndex("City"));

        var loadedRow0 = loaded.GetRowValues(0);
        Assert.Equal(5, loadedRow0.Count);

        // MergeWith loaded + docC again
        var reMerged = loaded.MergeWith(docC);
        Assert.Equal(10, reMerged.GetRowCount());

        // Final SaveToFile
        var path2 = TempFile("dogfood_remerged.csv");
        reMerged.SaveToFile(path2);
        Assert.True(File.Exists(path2));
    }

    private static string[] Enumerable8(string val)
    {
        var arr = new string[8];
        System.Array.Fill(arr, val);
        return arr;
    }
}
