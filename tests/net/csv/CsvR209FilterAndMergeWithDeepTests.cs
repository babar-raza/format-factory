// Tests for CsvDocument.Filter, MergeWith, GetDistinctValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R209

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R209: Tests for CsvDocument.Filter, MergeWith, GetDistinctValues deeper.
/// Filter(colName, value): returns filtered rows as a new CsvDocument.
/// MergeWith(other): merges rows from another CsvDocument into this one.
/// GetDistinctValues(colName): returns unique values in the specified column.
/// Covers: Filter non-null; Filter no-throw; Filter Engineering=3; Filter Marketing=1;
/// Filter non-match=0; Filter preserves header count; Filter then SortRows;
/// Filter consistent; Filter save-load; Filter then ExportToXml;
/// MergeWith non-null; MergeWith no-throw; MergeWith sum rows;
/// MergeWith then Filter; MergeWith consistent; MergeWith self doubles;
/// MergeWith save-load; MergeWith then SortRows; MergeWith header count same;
/// GetDistinctValues non-null; GetDistinctValues no-throw; GetDistinctValues count correct;
/// GetDistinctValues no duplicates; GetDistinctValues consistent; GetDistinctValues after AddRow;
/// GetDistinctValues save-load; GetDistinctValues all unique column;
/// dogfood LoadFile→Filter→MergeWith→GetDistinctValues→SaveToFile pipeline.
/// </summary>
public class CsvR209FilterAndMergeWithDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR209FilterAndMergeWithDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR209_" + Guid.NewGuid().ToString("N"));
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
            "Name,Department,Score,City\n" +
            "Alice,Engineering,92,London\n" +
            "Bob,Marketing,78,Paris\n" +
            "Carol,Engineering,88,Berlin\n" +
            "Dave,Finance,85,Rome\n" +
            "Eve,Engineering,95,Madrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    private string CreateContractorCsv()
    {
        var path = TempFile("contractors.csv");
        var content =
            "Name,Department,Score,City\n" +
            "Frank,Marketing,80,Vienna\n" +
            "Grace,Finance,72,Oslo\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.Filter("Department", "Engineering"));
    }

    [Fact]
    public void Filter_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.Filter("Department", "Engineering"));
        Assert.Null(ex);
    }

    [Fact]
    public void Filter_Engineering_Count3()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(3, doc.Filter("Department", "Engineering").GetRowCount());
    }

    [Fact]
    public void Filter_Marketing_Count1()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(1, doc.Filter("Department", "Marketing").GetRowCount());
    }

    [Fact]
    public void Filter_NonMatch_Count0()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(0, doc.Filter("Department", "HR").GetRowCount());
    }

    [Fact]
    public void Filter_PreservesHeaderCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetHeaderCount();
        Assert.Equal(before, doc.Filter("Department", "Engineering").GetHeaderCount());
    }

    [Fact]
    public void Filter_ThenSortRows_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var filtered = doc.Filter("Department", "Engineering");
        var ex = Record.Exception(() => filtered.SortRows("Score", ascending: false));
        Assert.Null(ex);
    }

    [Fact]
    public void Filter_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.Filter("Department", "Engineering").GetRowCount(),
                     doc.Filter("Department", "Engineering").GetRowCount());
    }

    [Fact]
    public void Filter_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var filtered = doc.Filter("Department", "Engineering");
        var path = TempFile("filter_save.csv");
        filtered.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetRowCount());
    }

    [Fact]
    public void Filter_ThenExportToXml_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var filtered = doc.Filter("Department", "Engineering");
        Assert.NotNull(filtered.ExportToXml());
        Assert.NotEmpty(filtered.ExportToXml());
    }

    // -------------------------------------------------------------------------
    // MergeWith
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeWith_NonNull()
    {
        var docA = CsvDocument.LoadFile(CreateSampleCsv());
        var docB = CsvDocument.LoadFile(CreateContractorCsv());
        Assert.NotNull(docA.MergeWith(docB));
    }

    [Fact]
    public void MergeWith_NoThrow()
    {
        var docA = CsvDocument.LoadFile(CreateSampleCsv());
        var docB = CsvDocument.LoadFile(CreateContractorCsv());
        var ex = Record.Exception(() => docA.MergeWith(docB));
        Assert.Null(ex);
    }

    [Fact]
    public void MergeWith_SumOfRowCounts()
    {
        var docA = CsvDocument.LoadFile(CreateSampleCsv()); // 5
        var docB = CsvDocument.LoadFile(CreateContractorCsv()); // 2
        var merged = docA.MergeWith(docB);
        Assert.Equal(7, merged.GetRowCount());
    }

    [Fact]
    public void MergeWith_ThenFilter()
    {
        var docA = CsvDocument.LoadFile(CreateSampleCsv());
        var docB = CsvDocument.LoadFile(CreateContractorCsv());
        var merged = docA.MergeWith(docB);
        // Marketing: Bob + Frank = 2
        Assert.Equal(2, merged.Filter("Department", "Marketing").GetRowCount());
    }

    [Fact]
    public void MergeWith_Consistent()
    {
        var docA = CsvDocument.LoadFile(CreateSampleCsv());
        var docB = CsvDocument.LoadFile(CreateContractorCsv());
        var m1 = docA.MergeWith(docB);
        var m2 = docA.MergeWith(docB);
        Assert.Equal(m1.GetRowCount(), m2.GetRowCount());
    }

    [Fact]
    public void MergeWith_Self_Doubles()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv()); // 5
        var merged = doc.MergeWith(doc);
        Assert.Equal(10, merged.GetRowCount());
    }

    [Fact]
    public void MergeWith_SaveLoad_Consistent()
    {
        var docA = CsvDocument.LoadFile(CreateSampleCsv());
        var docB = CsvDocument.LoadFile(CreateContractorCsv());
        var merged = docA.MergeWith(docB);
        var path = TempFile("merged_save.csv");
        merged.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(7, loaded.GetRowCount());
    }

    [Fact]
    public void MergeWith_HeaderCount_Unchanged()
    {
        var docA = CsvDocument.LoadFile(CreateSampleCsv());
        var docB = CsvDocument.LoadFile(CreateContractorCsv());
        var before = docA.GetHeaderCount();
        var merged = docA.MergeWith(docB);
        Assert.Equal(before, merged.GetHeaderCount());
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.GetDistinctValues("Department"));
    }

    [Fact]
    public void GetDistinctValues_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetDistinctValues("Department"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDistinctValues_Count3_Departments()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(3, doc.GetDistinctValues("Department").Count);
    }

    [Fact]
    public void GetDistinctValues_NoDuplicates()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var vals = doc.GetDistinctValues("Department");
        var distinct = new System.Collections.Generic.HashSet<string>(vals);
        Assert.Equal(distinct.Count, vals.Count);
    }

    [Fact]
    public void GetDistinctValues_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetDistinctValues("Department").Count,
                     doc.GetDistinctValues("Department").Count);
    }

    [Fact]
    public void GetDistinctValues_AfterAddRow_Updates()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetDistinctValues("Department").Count;
        doc.AddRow(new[] { "Hector", "HR", "80", "Tokyo" });
        Assert.True(doc.GetDistinctValues("Department").Count >= before);
    }

    [Fact]
    public void GetDistinctValues_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetDistinctValues("Department").Count;
        var path = TempFile("distinct_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDistinctValues("Department").Count);
    }

    [Fact]
    public void GetDistinctValues_Name_AllUnique()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        // All 5 names are unique
        Assert.Equal(5, doc.GetDistinctValues("Name").Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Filter_MergeWith_GetDistinctValues_SaveToFile_Pipeline()
    {
        // Create main CSV with employees
        var pathA = TempFile("dogfood_employees.csv");
        var contentA =
            "Employee,Department,Grade,Location,Salary\n" +
            "Alice,Engineering,Senior,London,95000\n" +
            "Bob,Marketing,Junior,Paris,55000\n" +
            "Carol,Engineering,Lead,London,115000\n" +
            "Dave,Finance,Mid,Berlin,72000\n" +
            "Eve,Engineering,Senior,London,98000\n" +
            "Frank,Marketing,Senior,Rome,82000\n";
        File.WriteAllText(pathA, contentA);

        // Create secondary CSV with contractors
        var pathB = TempFile("dogfood_contractors.csv");
        var contentB =
            "Employee,Department,Grade,Location,Salary\n" +
            "Grace,Finance,Junior,Madrid,48000\n" +
            "Hector,Engineering,Mid,Tokyo,88000\n" +
            "Iris,Marketing,Senior,Sydney,92000\n";
        File.WriteAllText(pathB, contentB);

        var docA = CsvDocument.LoadFile(pathA);
        var docB = CsvDocument.LoadFile(pathB);

        Assert.Equal(6, docA.GetRowCount());
        Assert.Equal(3, docB.GetRowCount());

        // GetDistinctValues on docA
        var depts = docA.GetDistinctValues("Department");
        Assert.Equal(3, depts.Count); // Engineering, Marketing, Finance

        var grades = docA.GetDistinctValues("Grade");
        Assert.True(grades.Count >= 3); // Senior, Junior, Lead, Mid

        var locations = docA.GetDistinctValues("Location");
        Assert.True(locations.Count >= 3); // London, Paris, Berlin, Rome

        // Filter Engineering from docA — Alice, Carol, Eve = 3
        var eng = docA.Filter("Department", "Engineering");
        Assert.Equal(3, eng.GetRowCount());
        Assert.Equal(5, eng.GetHeaderCount());

        // Filter Marketing — Bob, Frank = 2
        var mkt = docA.Filter("Department", "Marketing");
        Assert.Equal(2, mkt.GetRowCount());

        // Filter London — Alice, Carol, Eve = 3
        var london = docA.Filter("Location", "London");
        Assert.Equal(3, london.GetRowCount());

        // Filter then ExportToXml
        var engXml = eng.ExportToXml();
        Assert.NotNull(engXml);
        Assert.NotEmpty(engXml);

        // MergeWith docB — 6 + 3 = 9
        var merged = docA.MergeWith(docB);
        Assert.Equal(9, merged.GetRowCount());
        Assert.Equal(5, merged.GetHeaderCount());

        // GetDistinctValues on merged
        var mergedDepts = merged.GetDistinctValues("Department");
        Assert.Equal(3, mergedDepts.Count); // Still 3 — Engineering, Marketing, Finance

        // Filter Engineering from merged — Alice, Carol, Eve, Hector = 4
        var mergedEng = merged.Filter("Department", "Engineering");
        Assert.Equal(4, mergedEng.GetRowCount());

        // Filter Marketing from merged — Bob, Frank, Iris = 3
        var mergedMkt = merged.Filter("Department", "Marketing");
        Assert.Equal(3, mergedMkt.GetRowCount());

        // MergeWith consistent
        var m2 = docA.MergeWith(docB);
        Assert.Equal(merged.GetRowCount(), m2.GetRowCount());

        // MergeWith self — doubles
        var selfMerge = merged.MergeWith(merged);
        Assert.Equal(18, selfMerge.GetRowCount());

        // GetDistinctValues no duplicates
        var noDup = new System.Collections.Generic.HashSet<string>(mergedDepts);
        Assert.Equal(noDup.Count, mergedDepts.Count);

        // SortRows on merged
        merged.SortRows("Employee", ascending: true);
        Assert.Equal(9, merged.GetRowCount());
        Assert.Equal("Alice", merged.GetCell(0, 0));

        // SaveToFile merged
        var savePath = TempFile("dogfood_merged.csv");
        merged.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRowCount());
        Assert.Equal(3, loaded.GetDistinctValues("Department").Count);

        // Filter on loaded
        var loadedEng = loaded.Filter("Department", "Engineering");
        Assert.Equal(4, loadedEng.GetRowCount());

        // GetDistinctValues on loaded consistent
        Assert.Equal(loaded.GetDistinctValues("Department").Count,
                     loaded.GetDistinctValues("Department").Count);

        // ExportToXml on loaded
        var loadedXml = loaded.ExportToXml();
        Assert.NotNull(loadedXml);
        Assert.NotEmpty(loadedXml);

        // Final save
        var path2 = TempFile("dogfood_merged_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetDistinctValues("Department").Count,
                     loaded2.GetDistinctValues("Department").Count);
    }
}
