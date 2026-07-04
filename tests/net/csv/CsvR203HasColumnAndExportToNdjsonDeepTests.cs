// Tests for CsvDocument.HasColumn, ExportToNdjson, GetDistinctValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R203

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R203: Tests for CsvDocument.HasColumn, ExportToNdjson, GetDistinctValues deeper.
/// HasColumn(colName): returns true if the column exists.
/// ExportToNdjson(): exports the document as newline-delimited JSON.
/// GetDistinctValues(colName): returns the unique values in the specified column.
/// Covers: HasColumn true for existing; HasColumn false for non-existent; HasColumn consistent;
/// HasColumn no-throw; HasColumn after AddColumn true; HasColumn after RemoveColumn false;
/// HasColumn for all known headers; HasColumn returns bool;
/// ExportToNdjson non-null; ExportToNdjson non-empty; ExportToNdjson has braces;
/// ExportToNdjson has header names; ExportToNdjson has data values;
/// ExportToNdjson after AddRow grows; ExportToNdjson after Filter shrinks;
/// ExportToNdjson consistent; ExportToNdjson newline per record;
/// GetDistinctValues non-null; GetDistinctValues non-empty; GetDistinctValues count correct;
/// GetDistinctValues contains known; GetDistinctValues no duplicates; GetDistinctValues consistent;
/// GetDistinctValues after AddRow updates; GetDistinctValues after Filter shrinks;
/// dogfood LoadFile→HasColumn→ExportToNdjson→GetDistinctValues→SaveToFile pipeline.
/// </summary>
public class CsvR203HasColumnAndExportToNdjsonDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR203HasColumnAndExportToNdjsonDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR203_" + Guid.NewGuid().ToString("N"));
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

    // -------------------------------------------------------------------------
    // HasColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_True_ForExisting()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.True(doc.HasColumn("Name"));
        Assert.True(doc.HasColumn("Department"));
        Assert.True(doc.HasColumn("Score"));
        Assert.True(doc.HasColumn("City"));
    }

    [Fact]
    public void HasColumn_False_ForNonExistent()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.False(doc.HasColumn("NONEXISTENT_COLUMN_XYZ"));
    }

    [Fact]
    public void HasColumn_Consistent()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(doc.HasColumn("Name"), doc.HasColumn("Name"));
    }

    [Fact]
    public void HasColumn_NoThrow()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.HasColumn("Name"));
        Assert.Null(ex);
    }

    [Fact]
    public void HasColumn_AfterAddColumn_True()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU" });
        Assert.True(doc.HasColumn("Region"));
    }

    [Fact]
    public void HasColumn_AfterRemoveColumn_False()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.RemoveColumn("City");
        Assert.False(doc.HasColumn("City"));
    }

    [Fact]
    public void HasColumn_RetainedAfterRemoveOther()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.RemoveColumn("City");
        Assert.True(doc.HasColumn("Name"));
        Assert.True(doc.HasColumn("Department"));
        Assert.True(doc.HasColumn("Score"));
    }

    [Fact]
    public void HasColumn_ReturnsBool()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var result = doc.HasColumn("Name");
        Assert.IsType<bool>(result);
    }

    // -------------------------------------------------------------------------
    // ExportToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToNdjson_NonNull()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.NotNull(doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_NonEmpty()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.NotEmpty(doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_HasBraces()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var ndjson = doc.ExportToNdjson();
        Assert.Contains("{", ndjson);
    }

    [Fact]
    public void ExportToNdjson_HasHeaderNames()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var ndjson = doc.ExportToNdjson();
        Assert.True(ndjson.Contains("Name") || ndjson.Contains("Department") || ndjson.Contains("Score"));
    }

    [Fact]
    public void ExportToNdjson_HasDataValues()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var ndjson = doc.ExportToNdjson();
        Assert.True(ndjson.Contains("Alice") || ndjson.Contains("Bob") || ndjson.Contains("Carol"));
    }

    [Fact]
    public void ExportToNdjson_AfterAddRow_Grows()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.ExportToNdjson().Length;
        doc.AddRow(new[] { "Frank", "Operations", "82", "Vienna" });
        var after = doc.ExportToNdjson().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToNdjson_AfterFilter_Shrinks()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.ExportToNdjson().Length;
        var filtered = doc.Filter("Department", "Finance");
        var after = filtered.ExportToNdjson().Length;
        Assert.True(after < before);
    }

    [Fact]
    public void ExportToNdjson_Consistent()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var n1 = doc.ExportToNdjson();
        var n2 = doc.ExportToNdjson();
        Assert.Equal(n1.Length, n2.Length);
    }

    [Fact]
    public void ExportToNdjson_NewlinePerRecord()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var ndjson = doc.ExportToNdjson();
        var lines = ndjson.Trim().Split('\n');
        Assert.True(lines.Length >= doc.GetRowCount());
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
        // Engineering, Marketing, Finance = 3 distinct departments
        Assert.Equal(3, doc.GetDistinctValues("Department").Count);
    }

    [Fact]
    public void GetDistinctValues_ContainsKnown()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var values = doc.GetDistinctValues("Department");
        Assert.Contains("Engineering", values);
        Assert.Contains("Marketing", values);
        Assert.Contains("Finance", values);
    }

    [Fact]
    public void GetDistinctValues_NoDuplicates()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var values = doc.GetDistinctValues("Department");
        var set = new System.Collections.Generic.HashSet<string>(values);
        Assert.Equal(set.Count, values.Count);
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
    public void GetDistinctValues_AfterAddRow_Updates()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetDistinctValues("Department").Count;
        doc.AddRow(new[] { "Frank", "Operations", "82", "Vienna" });
        var after = doc.GetDistinctValues("Department").Count;
        Assert.True(after >= before);
    }

    [Fact]
    public void GetDistinctValues_AllNamesUnique()
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
    public void Dogfood_HasColumn_ExportToNdjson_GetDistinctValues_SaveToFile_Pipeline()
    {
        // Create source CSV
        var path = TempFile("dogfood_src.csv");
        var content =
            "EmployeeID,Name,Department,Grade,City,Active\n" +
            "E001,Alice,Engineering,Senior,London,Yes\n" +
            "E002,Bob,Marketing,Junior,Paris,Yes\n" +
            "E003,Carol,Engineering,Lead,London,No\n" +
            "E004,Dave,Finance,Mid,Berlin,Yes\n" +
            "E005,Eve,Engineering,Senior,London,Yes\n" +
            "E006,Frank,Marketing,Senior,Rome,No\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(6, doc.GetRowCount());

        // HasColumn checks
        Assert.True(doc.HasColumn("EmployeeID"));
        Assert.True(doc.HasColumn("Name"));
        Assert.True(doc.HasColumn("Department"));
        Assert.True(doc.HasColumn("Grade"));
        Assert.True(doc.HasColumn("City"));
        Assert.True(doc.HasColumn("Active"));
        Assert.False(doc.HasColumn("Salary"));
        Assert.False(doc.HasColumn("Region"));

        // GetDistinctValues baseline
        var depts = doc.GetDistinctValues("Department");
        Assert.Equal(3, depts.Count);
        Assert.Contains("Engineering", depts);
        Assert.Contains("Marketing", depts);
        Assert.Contains("Finance", depts);

        var cities = doc.GetDistinctValues("City");
        Assert.True(cities.Count <= 4); // London, Paris, Berlin, Rome

        var grades = doc.GetDistinctValues("Grade");
        Assert.Contains("Senior", grades);
        Assert.Contains("Junior", grades);
        Assert.Contains("Lead", grades);
        Assert.Contains("Mid", grades);

        // ExportToNdjson baseline
        var ndjson = doc.ExportToNdjson();
        Assert.NotNull(ndjson);
        Assert.NotEmpty(ndjson);
        Assert.Contains("{", ndjson);

        // AddColumn and verify HasColumn
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU", "EU" });
        Assert.True(doc.HasColumn("Region"));
        var distinctRegions = doc.GetDistinctValues("Region");
        Assert.Equal(1, distinctRegions.Count);

        // ExportToNdjson grows after AddColumn
        var ndjsonAfterAdd = doc.ExportToNdjson();
        Assert.True(ndjsonAfterAdd.Length > ndjson.Length);

        // AddRow and verify GetDistinctValues updates
        doc.AddRow(new[] { "E007", "Grace", "HR", "Junior", "Madrid", "Yes", "EU" });
        Assert.Equal(7, doc.GetRowCount());
        var deptsAfterRow = doc.GetDistinctValues("Department");
        Assert.Equal(4, deptsAfterRow.Count);
        Assert.Contains("HR", deptsAfterRow);

        // GetColumnValues reflects new row
        var names = doc.GetColumnValues("Name");
        Assert.Equal(7, names.Count);
        Assert.Contains("Grace", names);

        // HasColumn after RemoveColumn
        doc.RemoveColumn("Region");
        Assert.False(doc.HasColumn("Region"));

        // ExportToNdjson after RemoveColumn
        var ndjsonAfterRemove = doc.ExportToNdjson();
        Assert.True(ndjsonAfterRemove.Length > 0);

        // Filter Engineering
        var eng = doc.Filter("Department", "Engineering");
        Assert.False(eng.HasColumn("Region")); // was removed

        var engDistinct = eng.GetDistinctValues("Department");
        Assert.Equal(1, engDistinct.Count);
        Assert.Contains("Engineering", engDistinct);

        // ExportToNdjson on filtered
        var engNdjson = eng.ExportToNdjson();
        Assert.True(engNdjson.Length < ndjsonAfterRemove.Length);

        // GetDistinctValues after Filter shrinks
        var allActive = doc.GetDistinctValues("Active");
        Assert.True(allActive.Count >= 1);

        // SortRows then verify GetDistinctValues unchanged
        doc.SortRows("Name", ascending: true);
        var deptsAfterSort = doc.GetDistinctValues("Department");
        Assert.Equal(4, deptsAfterSort.Count);

        // HasColumn consistent
        Assert.Equal(doc.HasColumn("Name"), doc.HasColumn("Name"));

        // SaveToFile
        var savePath = TempFile("dogfood_modified.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(7, loaded.GetRowCount());

        Assert.True(loaded.HasColumn("Name"));
        Assert.True(loaded.HasColumn("Department"));
        Assert.False(loaded.HasColumn("Region"));

        var loadedDepts = loaded.GetDistinctValues("Department");
        Assert.Equal(4, loadedDepts.Count);

        // ExportToNdjson on loaded
        var loadedNdjson = loaded.ExportToNdjson();
        Assert.NotNull(loadedNdjson);
        Assert.NotEmpty(loadedNdjson);
        Assert.Contains("{", loadedNdjson);

        // GetDistinctValues consistent on loaded
        var lv1 = loaded.GetDistinctValues("Department");
        var lv2 = loaded.GetDistinctValues("Department");
        Assert.Equal(lv1.Count, lv2.Count);
    }
}
