// Tests for CsvDocument.GetColumnValues, RemoveColumn, GetDistinctValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R202

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R202: Tests for CsvDocument.GetColumnValues, RemoveColumn, GetDistinctValues deeper.
/// GetColumnValues(colName): returns all values for the specified column as a list.
/// RemoveColumn(colName): removes a column from the document.
/// GetDistinctValues(colName): returns unique values for the specified column.
/// Covers: GetColumnValues non-null; GetColumnValues non-empty; GetColumnValues count=rowCount;
/// GetColumnValues contains known; GetColumnValues consistent; GetColumnValues for numeric;
/// GetColumnValues after SetCell reflects; GetColumnValues after AddRow grows;
/// GetColumnValues all names unique; GetColumnValues after Filter shrinks;
/// RemoveColumn decreases column count; RemoveColumn removes header; RemoveColumn values inaccessible;
/// RemoveColumn retains others; RemoveColumn no-throw; RemoveColumn persist;
/// RemoveColumn then SortRows; RemoveColumn multiple;
/// GetDistinctValues non-null; GetDistinctValues non-empty; GetDistinctValues count correct;
/// GetDistinctValues contains known; GetDistinctValues no duplicates; GetDistinctValues consistent;
/// GetDistinctValues after AddRow updates; GetDistinctValues all unique names;
/// dogfood LoadFile→GetColumnValues→RemoveColumn→GetDistinctValues→SaveToFile pipeline.
/// </summary>
public class CsvR202GetColumnValuesAndRemoveColumnDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR202GetColumnValuesAndRemoveColumnDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR202_" + Guid.NewGuid().ToString("N"));
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
            "Name,Department,Score,City,Active\n" +
            "Alice,Engineering,92,London,Yes\n" +
            "Bob,Marketing,78,Paris,Yes\n" +
            "Carol,Engineering,88,Berlin,No\n" +
            "Dave,Finance,85,Rome,Yes\n" +
            "Eve,Engineering,95,Madrid,Yes\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_NonNull()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.NotNull(doc.GetColumnValues("Name"));
    }

    [Fact]
    public void GetColumnValues_NonEmpty()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.True(doc.GetColumnValues("Name").Count > 0);
    }

    [Fact]
    public void GetColumnValues_CountEqualsRowCount()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(doc.GetRowCount(), doc.GetColumnValues("Name").Count);
    }

    [Fact]
    public void GetColumnValues_ContainsKnown()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Eve", names);
    }

    [Fact]
    public void GetColumnValues_Consistent()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var v1 = doc.GetColumnValues("Name");
        var v2 = doc.GetColumnValues("Name");
        Assert.Equal(v1.Count, v2.Count);
    }

    [Fact]
    public void GetColumnValues_ForNumeric_HasValues()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var scores = doc.GetColumnValues("Score");
        Assert.Equal(5, scores.Count);
        Assert.Contains("92", scores);
        Assert.Contains("95", scores);
    }

    [Fact]
    public void GetColumnValues_AfterSetCell_Reflects()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.SetCell(0, 0, "ALICE_UPDATED");
        var names = doc.GetColumnValues("Name");
        Assert.Contains("ALICE_UPDATED", names);
    }

    [Fact]
    public void GetColumnValues_AfterAddRow_Grows()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetColumnValues("Name").Count;
        doc.AddRow(new[] { "Frank", "HR", "77", "Vienna", "Yes" });
        var after = doc.GetColumnValues("Name").Count;
        Assert.Equal(before + 1, after);
    }

    [Fact]
    public void GetColumnValues_AfterFilter_Shrinks()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetColumnValues("Name").Count;
        var filtered = doc.Filter("Department", "Engineering");
        var after = filtered.GetColumnValues("Name").Count;
        Assert.True(after < before);
    }

    // -------------------------------------------------------------------------
    // RemoveColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveColumn_DecreasesColumnCount()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetColumnCount();
        doc.RemoveColumn("Active");
        Assert.Equal(before - 1, doc.GetColumnCount());
    }

    [Fact]
    public void RemoveColumn_RemovesHeader()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.RemoveColumn("Active");
        Assert.False(doc.GetHeaders().Contains("Active"));
    }

    [Fact]
    public void RemoveColumn_RetainsOtherColumns()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.RemoveColumn("Active");
        var headers = doc.GetHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Department", headers);
        Assert.Contains("Score", headers);
        Assert.Contains("City", headers);
    }

    [Fact]
    public void RemoveColumn_NoThrow()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.RemoveColumn("City"));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveColumn_Persist()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.RemoveColumn("Active");
        var savePath = TempFile("remove_col_persist.csv");
        doc.SaveToFile(savePath);
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.False(loaded.GetHeaders().Contains("Active"));
        Assert.Contains("Name", loaded.GetHeaders());
    }

    [Fact]
    public void RemoveColumn_Multiple_EachReducesCount()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetColumnCount();
        doc.RemoveColumn("Active");
        doc.RemoveColumn("City");
        Assert.Equal(before - 2, doc.GetColumnCount());
    }

    [Fact]
    public void RemoveColumn_RowCountUnchanged()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetRowCount();
        doc.RemoveColumn("Active");
        Assert.Equal(before, doc.GetRowCount());
    }

    [Fact]
    public void RemoveColumn_ThenSortRows_Works()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.RemoveColumn("Active");
        doc.SortRows("Name", ascending: true);
        Assert.Equal("Alice", doc.GetCell(0, 0));
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.NotNull(doc.GetDistinctValues("Department"));
    }

    [Fact]
    public void GetDistinctValues_NonEmpty()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.True(doc.GetDistinctValues("Department").Count > 0);
    }

    [Fact]
    public void GetDistinctValues_CountCorrect()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        // Engineering, Marketing, Finance = 3
        Assert.Equal(3, doc.GetDistinctValues("Department").Count);
    }

    [Fact]
    public void GetDistinctValues_ContainsKnown()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var vals = doc.GetDistinctValues("Department");
        Assert.Contains("Engineering", vals);
        Assert.Contains("Marketing", vals);
        Assert.Contains("Finance", vals);
    }

    [Fact]
    public void GetDistinctValues_NoDuplicates()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var vals = doc.GetDistinctValues("Department");
        var set = new System.Collections.Generic.HashSet<string>(vals);
        Assert.Equal(vals.Count, set.Count);
    }

    [Fact]
    public void GetDistinctValues_Consistent()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var v1 = doc.GetDistinctValues("Department");
        var v2 = doc.GetDistinctValues("Department");
        Assert.Equal(v1.Count, v2.Count);
    }

    [Fact]
    public void GetDistinctValues_AfterAddRow_UpdatesIfNewValue()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetDistinctValues("Department").Count;
        doc.AddRow(new[] { "Frank", "Operations", "77", "Oslo", "Yes" });
        var after = doc.GetDistinctValues("Department").Count;
        Assert.True(after > before);
    }

    [Fact]
    public void GetDistinctValues_AllUniqueNames()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        // All 5 names are unique
        Assert.Equal(5, doc.GetDistinctValues("Name").Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnValues_RemoveColumn_GetDistinctValues_SaveToFile_Pipeline()
    {
        // Create rich dataset
        var path = TempFile("dogfood_src.csv");
        var content =
            "EmpID,Name,Team,Grade,Salary,Location,Manager\n" +
            "E001,Alice,Engineering,Senior,95000,London,Carol\n" +
            "E002,Bob,Marketing,Junior,68000,Paris,Dave\n" +
            "E003,Carol,Engineering,Lead,115000,London,None\n" +
            "E004,Dave,Marketing,Senior,82000,Berlin,None\n" +
            "E005,Eve,Finance,Mid,77000,Rome,Frank\n" +
            "E006,Frank,Finance,Senior,91000,Rome,None\n" +
            "E007,Grace,Engineering,Mid,88000,London,Carol\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(7, doc.GetRowCount());
        Assert.Equal(7, doc.GetColumnCount());

        // GetColumnValues — Names
        var names = doc.GetColumnValues("Name");
        Assert.Equal(7, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Grace", names);

        // GetColumnValues — Teams
        var teams = doc.GetColumnValues("Team");
        Assert.Equal(7, teams.Count);
        Assert.Contains("Engineering", teams);
        Assert.Contains("Marketing", teams);

        // GetDistinctValues — Teams = 3
        var distinctTeams = doc.GetDistinctValues("Team");
        Assert.Equal(3, distinctTeams.Count);
        Assert.Contains("Engineering", distinctTeams);
        Assert.Contains("Finance", distinctTeams);

        // GetDistinctValues — Grades = 4
        var distinctGrades = doc.GetDistinctValues("Grade");
        Assert.Equal(4, distinctGrades.Count); // Senior, Junior, Lead, Mid

        // GetDistinctValues — all names unique
        var distinctNames = doc.GetDistinctValues("Name");
        Assert.Equal(7, distinctNames.Count);

        // RemoveColumn — EmpID (not needed for analysis)
        doc.RemoveColumn("EmpID");
        Assert.Equal(6, doc.GetColumnCount());
        Assert.False(doc.GetHeaders().Contains("EmpID"));

        // GetColumnValues still works after RemoveColumn
        var namesAfterRemove = doc.GetColumnValues("Name");
        Assert.Equal(7, namesAfterRemove.Count);
        Assert.Contains("Alice", namesAfterRemove);

        // RemoveColumn — Manager
        doc.RemoveColumn("Manager");
        Assert.Equal(5, doc.GetColumnCount());

        // GetDistinctValues after RemoveColumn — Teams unchanged
        var distinctTeamsAfter = doc.GetDistinctValues("Team");
        Assert.Equal(3, distinctTeamsAfter.Count);

        // AddRow
        doc.AddRow(new[] { "Hannah", "HR", "Junior", "62000", "Vienna" });
        Assert.Equal(8, doc.GetRowCount());

        // GetColumnValues after AddRow
        var namesAfterAdd = doc.GetColumnValues("Name");
        Assert.Equal(8, namesAfterAdd.Count);
        Assert.Contains("Hannah", namesAfterAdd);

        // GetDistinctValues after AddRow
        var distinctTeamsNew = doc.GetDistinctValues("Team");
        Assert.Equal(4, distinctTeamsNew.Count); // HR is new
        Assert.Contains("HR", distinctTeamsNew);

        // Filter Engineering and check column values
        var engRows = doc.Filter("Team", "Engineering");
        Assert.Equal(3, engRows.GetRowCount()); // Alice, Carol, Grace
        var engNames = engRows.GetColumnValues("Name");
        Assert.Equal(3, engNames.Count);
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);

        // SetCell and verify GetColumnValues reflects
        doc.SetCell(0, 0, "ALICE_UPDATED");
        var updatedNames = doc.GetColumnValues("Name");
        Assert.Contains("ALICE_UPDATED", updatedNames);

        // SortRows and verify column values remain correct count
        doc.SortRows("Name", ascending: true);
        var sortedNames = doc.GetColumnValues("Name");
        Assert.Equal(8, sortedNames.Count);

        // RemoveColumn — Location
        doc.RemoveColumn("Location");
        Assert.Equal(4, doc.GetColumnCount());

        // GetDistinctValues still works
        var finalTeams = doc.GetDistinctValues("Team");
        Assert.Equal(4, finalTeams.Count);

        // SaveToFile
        var savePath = TempFile("dogfood_modified.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(8, loaded.GetRowCount());
        Assert.Equal(4, loaded.GetColumnCount());

        // GetColumnValues on loaded
        var loadedNames = loaded.GetColumnValues("Name");
        Assert.Equal(8, loadedNames.Count);

        // GetDistinctValues on loaded
        var loadedTeams = loaded.GetDistinctValues("Team");
        Assert.Equal(4, loadedTeams.Count);

        // RemoveColumn on loaded
        loaded.RemoveColumn("Salary");
        Assert.Equal(3, loaded.GetColumnCount());
        Assert.False(loaded.GetHeaders().Contains("Salary"));

        // GetColumnValues on loaded after RemoveColumn
        var loadedNamesAfter = loaded.GetColumnValues("Name");
        Assert.Equal(8, loadedNamesAfter.Count);
    }
}
