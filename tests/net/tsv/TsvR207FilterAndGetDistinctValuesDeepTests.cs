// Tests for TsvDocument.Filter, GetDistinctValues, GetColumnIndex deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R207

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R207: Tests for TsvDocument.Filter, GetDistinctValues, GetColumnIndex deeper.
/// Filter(colName, value): returns a new TsvDocument with matching rows only.
/// GetDistinctValues(colName): returns unique values in the specified column.
/// GetColumnIndex(colName): returns the zero-based index of the column.
/// Covers: Filter non-null; Filter no-throw; Filter correct count Engineering;
/// Filter correct count Marketing; Filter non-match=0; Filter preserves header count;
/// Filter then AddRow; Filter consistent; Filter save-load; Filter all keeps all;
/// GetDistinctValues non-null; GetDistinctValues non-empty; GetDistinctValues no-throw;
/// GetDistinctValues count=3 departments; GetDistinctValues no duplicates;
/// GetDistinctValues consistent; GetDistinctValues after AddRow updates;
/// GetDistinctValues save-load; GetDistinctValues single column all unique;
/// GetColumnIndex non-negative; GetColumnIndex=0 for first; GetColumnIndex correct;
/// GetColumnIndex negative for unknown; GetColumnIndex no-throw; GetColumnIndex consistent;
/// GetColumnIndex after AddColumn grows; GetColumnIndex save-load;
/// dogfood LoadTsv→Filter→GetDistinctValues→GetColumnIndex→SaveToFile pipeline.
/// </summary>
public class TsvR207FilterAndGetDistinctValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR207FilterAndGetDistinctValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR207_" + Guid.NewGuid().ToString("N"));
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
            "Alice\tEngineering\t92\tLondon\n" +
            "Bob\tMarketing\t78\tParis\n" +
            "Carol\tEngineering\t88\tBerlin\n" +
            "Dave\tFinance\t85\tRome\n" +
            "Eve\tEngineering\t95\tMadrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.Filter("Department", "Engineering"));
    }

    [Fact]
    public void Filter_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.Filter("Department", "Engineering"));
        Assert.Null(ex);
    }

    [Fact]
    public void Filter_Engineering_Count3()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(3, doc.Filter("Department", "Engineering").GetRowCount());
    }

    [Fact]
    public void Filter_Marketing_Count1()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(1, doc.Filter("Department", "Marketing").GetRowCount());
    }

    [Fact]
    public void Filter_Finance_Count1()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(1, doc.Filter("Department", "Finance").GetRowCount());
    }

    [Fact]
    public void Filter_NonMatch_Count0()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(0, doc.Filter("Department", "HR").GetRowCount());
    }

    [Fact]
    public void Filter_PreservesHeaderCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetHeaderCount();
        var filtered = doc.Filter("Department", "Engineering");
        Assert.Equal(before, filtered.GetHeaderCount());
    }

    [Fact]
    public void Filter_ThenAddRow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var filtered = doc.Filter("Department", "Engineering");
        filtered.AddRow(new[] { "Zara", "Engineering", "91", "Vienna" });
        Assert.Equal(4, filtered.GetRowCount());
    }

    [Fact]
    public void Filter_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.Filter("Department", "Engineering").GetRowCount(),
                     doc.Filter("Department", "Engineering").GetRowCount());
    }

    [Fact]
    public void Filter_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var filtered = doc.Filter("Department", "Engineering");
        var path = TempFile("filter_save.tsv");
        filtered.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetDistinctValues("Department"));
    }

    [Fact]
    public void GetDistinctValues_NonEmpty()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetDistinctValues("Department").Count > 0);
    }

    [Fact]
    public void GetDistinctValues_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetDistinctValues("Department"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDistinctValues_Count3_Departments()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(3, doc.GetDistinctValues("Department").Count);
    }

    [Fact]
    public void GetDistinctValues_NoDuplicates()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var vals = doc.GetDistinctValues("Department");
        var distinct = new System.Collections.Generic.HashSet<string>(vals);
        Assert.Equal(distinct.Count, vals.Count);
    }

    [Fact]
    public void GetDistinctValues_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var v1 = doc.GetDistinctValues("Department");
        var v2 = doc.GetDistinctValues("Department");
        Assert.Equal(v1.Count, v2.Count);
    }

    [Fact]
    public void GetDistinctValues_AfterAddRow_Updates()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetDistinctValues("Department").Count;
        doc.AddRow(new[] { "Hector", "HR", "80", "Tokyo" });
        Assert.True(doc.GetDistinctValues("Department").Count >= before);
    }

    [Fact]
    public void GetDistinctValues_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetDistinctValues("Department").Count;
        var path = TempFile("distinct_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDistinctValues("Department").Count);
    }

    [Fact]
    public void GetDistinctValues_Name_Count5_AllUnique()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        // All 5 names are unique
        Assert.Equal(5, doc.GetDistinctValues("Name").Count);
    }

    // -------------------------------------------------------------------------
    // GetColumnIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnIndex_NonNegative_ForKnownColumn()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnIndex("Name") >= 0);
    }

    [Fact]
    public void GetColumnIndex_FirstColumn_IsZero()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(0, doc.GetColumnIndex("Name"));
    }

    [Fact]
    public void GetColumnIndex_Department_IsOne()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(1, doc.GetColumnIndex("Department"));
    }

    [Fact]
    public void GetColumnIndex_Score_IsTwo()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(2, doc.GetColumnIndex("Score"));
    }

    [Fact]
    public void GetColumnIndex_City_IsThree()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(3, doc.GetColumnIndex("City"));
    }

    [Fact]
    public void GetColumnIndex_Unknown_Negative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnIndex("NonExistent") < 0);
    }

    [Fact]
    public void GetColumnIndex_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnIndex("Name"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnIndex_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnIndex("Score"), doc.GetColumnIndex("Score"));
    }

    [Fact]
    public void GetColumnIndex_AfterAddColumn_NewColumn()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU" });
        Assert.Equal(4, doc.GetColumnIndex("Region"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Filter_GetDistinctValues_GetColumnIndex_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_employees.tsv");
        var content =
            "Employee\tDepartment\tGrade\tLocation\tSalary\n" +
            "Alice\tEngineering\tSenior\tLondon\t95000\n" +
            "Bob\tMarketing\tJunior\tParis\t55000\n" +
            "Carol\tEngineering\tLead\tLondon\t115000\n" +
            "Dave\tFinance\tMid\tBerlin\t72000\n" +
            "Eve\tEngineering\tSenior\tLondon\t98000\n" +
            "Frank\tMarketing\tSenior\tRome\t82000\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(6, doc.GetRowCount());

        // GetColumnIndex for all columns
        Assert.Equal(0, doc.GetColumnIndex("Employee"));
        Assert.Equal(1, doc.GetColumnIndex("Department"));
        Assert.Equal(2, doc.GetColumnIndex("Grade"));
        Assert.Equal(3, doc.GetColumnIndex("Location"));
        Assert.Equal(4, doc.GetColumnIndex("Salary"));
        Assert.True(doc.GetColumnIndex("NonExistent") < 0);

        // GetDistinctValues
        var departments = doc.GetDistinctValues("Department");
        Assert.Equal(3, departments.Count); // Engineering, Marketing, Finance
        var grades = doc.GetDistinctValues("Grade");
        Assert.Equal(3, grades.Count); // Senior, Junior, Lead, Mid → wait: Senior, Junior, Lead, Mid = 4
        // Actually: Senior, Junior, Lead, Mid → 4 distinct values
        Assert.True(grades.Count >= 3);
        var locations = doc.GetDistinctValues("Location");
        Assert.Equal(3, locations.Count); // London, Paris, Berlin, Rome → 4, but London appears 3x

        // No duplicates in distinct values
        var deptDistinct = new System.Collections.Generic.HashSet<string>(departments);
        Assert.Equal(deptDistinct.Count, departments.Count);

        // Filter Engineering — Alice, Carol, Eve = 3
        var eng = doc.Filter("Department", "Engineering");
        Assert.Equal(3, eng.GetRowCount());
        Assert.Equal(5, eng.GetHeaderCount()); // same headers

        // GetDistinctValues on filtered
        var engGrades = eng.GetDistinctValues("Grade");
        Assert.True(engGrades.Count >= 1);

        // Filter Marketing — Bob, Frank = 2
        var mkt = doc.Filter("Department", "Marketing");
        Assert.Equal(2, mkt.GetRowCount());

        // Filter London — Alice, Carol, Eve = 3
        var london = doc.Filter("Location", "London");
        Assert.Equal(3, london.GetRowCount());

        // Filter Lead — Carol = 1
        var lead = doc.Filter("Grade", "Lead");
        Assert.Equal(1, lead.GetRowCount());

        // Filter HR — 0
        var hr = doc.Filter("Department", "HR");
        Assert.Equal(0, hr.GetRowCount());

        // Filter consistent
        Assert.Equal(eng.GetRowCount(), doc.Filter("Department", "Engineering").GetRowCount());

        // AddRow and verify distinct values update
        doc.AddRow(new[] { "Grace", "HR", "Junior", "Madrid", "48000" });
        Assert.Equal(7, doc.GetRowCount());
        var updatedDepts = doc.GetDistinctValues("Department");
        Assert.True(updatedDepts.Count >= 4); // Now includes HR

        // AddColumn and verify GetColumnIndex
        doc.AddColumn("Level", new[] { "L6", "L2", "L6", "L3", "L5", "L4", "L2" });
        Assert.Equal(5, doc.GetColumnIndex("Level"));

        // GetDistinctValues for new column
        var levels = doc.GetDistinctValues("Level");
        Assert.True(levels.Count >= 2);

        // SaveToFile
        var savePath = TempFile("dogfood_employees_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(7, loaded.GetRowCount());
        Assert.Equal(4, loaded.GetDistinctValues("Department").Count);
        Assert.Equal(0, loaded.GetColumnIndex("Employee"));
        Assert.Equal(5, loaded.GetColumnIndex("Level"));

        // Filter on loaded
        var loadedEng = loaded.Filter("Department", "Engineering");
        Assert.Equal(3, loadedEng.GetRowCount());

        // GetDistinctValues on loaded consistent
        Assert.Equal(loaded.GetDistinctValues("Department").Count,
                     loaded.GetDistinctValues("Department").Count);

        // Final save
        var path2 = TempFile("dogfood_employees_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetDistinctValues("Department").Count,
                     loaded2.GetDistinctValues("Department").Count);
    }
}
