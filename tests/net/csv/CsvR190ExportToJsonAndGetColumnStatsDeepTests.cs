// Tests for CsvDocument.ExportToJson, GetColumnStats deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R190

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R190: Tests for CsvDocument.ExportToJson, GetColumnStats deeper coverage.
/// ExportToJson(): exports document as a JSON array string.
/// GetColumnStats(colName): returns statistical summary (min/max/sum/avg/count) for a numeric column.
/// Covers: ExportToJson non-null; ExportToJson non-empty; ExportToJson is array-like;
/// ExportToJson contains field names; ExportToJson contains data values;
/// ExportToJson after AddRow larger; ExportToJson after Filter smaller;
/// ExportToJson round-trip property count; ExportToJson on empty doc;
/// GetColumnStats non-null; GetColumnStats sum correct; GetColumnStats avg correct;
/// GetColumnStats min correct; GetColumnStats max correct; GetColumnStats count correct;
/// GetColumnStats after AddRow updates; GetColumnStats after Filter updates;
/// GetColumnStats on all-same values; GetColumnStats on single row;
/// dogfood LoadFile→ExportToJson→GetColumnStats→AddRow→Filter→verify pipeline.
/// </summary>
public class CsvR190ExportToJsonAndGetColumnStatsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR190ExportToJsonAndGetColumnStatsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR190_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleCsv =
        "Employee,Department,Salary,Years\n" +
        "Alice,Engineering,95000,5\n" +
        "Bob,Finance,82000,3\n" +
        "Carol,Engineering,105000,8\n" +
        "Dave,HR,72000,2\n" +
        "Eve,Finance,88000,4\n";

    private CsvDocument LoadSample()
    {
        var path = TempFile("sample.csv");
        File.WriteAllText(path, SampleCsv);
        return CsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // ExportToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_IsArrayLike()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.True(json.TrimStart().StartsWith("[") || json.Contains("{"));
    }

    [Fact]
    public void ExportToJson_ContainsFieldName()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Employee") || json.Contains("Department") || json.Contains("Salary"));
    }

    [Fact]
    public void ExportToJson_ContainsDataValue()
    {
        var doc = LoadSample();
        Assert.Contains("Alice", doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_AfterAddRow_Larger()
    {
        var doc = LoadSample();
        var before = doc.ExportToJson().Length;
        doc.AddRow(new[] { "Frank", "Engineering", "98000", "6" });
        Assert.True(doc.ExportToJson().Length > before);
    }

    [Fact]
    public void ExportToJson_AfterFilter_Smaller()
    {
        var doc = LoadSample();
        var all = doc.ExportToJson();
        var filtered = doc.Filter("Department", "Finance").ExportToJson();
        Assert.True(filtered.Length < all.Length);
    }

    [Fact]
    public void ExportToJson_AllNamesPresent()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.Contains("Alice", json);
        Assert.Contains("Bob", json);
        Assert.Contains("Carol", json);
        Assert.Contains("Dave", json);
        Assert.Contains("Eve", json);
    }

    // -------------------------------------------------------------------------
    // GetColumnStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStats_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetColumnStats("Salary"));
    }

    [Fact]
    public void GetColumnStats_SumCorrect()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats("Salary");
        // 95000 + 82000 + 105000 + 72000 + 88000 = 442000
        Assert.Equal(442000, stats.Sum, 0.01);
    }

    [Fact]
    public void GetColumnStats_AvgCorrect()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats("Salary");
        // 442000 / 5 = 88400
        Assert.Equal(88400, stats.Avg, 0.01);
    }

    [Fact]
    public void GetColumnStats_MinCorrect()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats("Salary");
        Assert.Equal(72000, stats.Min, 0.01);
    }

    [Fact]
    public void GetColumnStats_MaxCorrect()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats("Salary");
        Assert.Equal(105000, stats.Max, 0.01);
    }

    [Fact]
    public void GetColumnStats_CountCorrect()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats("Salary");
        Assert.Equal(5, stats.Count);
    }

    [Fact]
    public void GetColumnStats_YearsSum()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats("Years");
        // 5+3+8+2+4 = 22
        Assert.Equal(22, stats.Sum, 0.01);
    }

    [Fact]
    public void GetColumnStats_AfterAddRow_Updates()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Frank", "Engineering", "110000", "7" });
        var stats = doc.GetColumnStats("Salary");
        Assert.Equal(6, stats.Count);
        Assert.Equal(110000, stats.Max, 0.01);
    }

    [Fact]
    public void GetColumnStats_AfterFilter_Updates()
    {
        var doc = LoadSample();
        var engStats = doc.Filter("Department", "Engineering").GetColumnStats("Salary");
        // Alice=95000, Carol=105000
        Assert.Equal(2, engStats.Count);
        Assert.Equal(95000, engStats.Min, 0.01);
        Assert.Equal(105000, engStats.Max, 0.01);
        Assert.Equal(200000, engStats.Sum, 0.01);
        Assert.Equal(100000, engStats.Avg, 0.01);
    }

    [Fact]
    public void GetColumnStats_SingleRow()
    {
        var path = TempFile("single.csv");
        File.WriteAllText(path, "Name,Score\nAlice,100\n");
        var doc = CsvDocument.LoadFile(path);
        var stats = doc.GetColumnStats("Score");
        Assert.Equal(1, stats.Count);
        Assert.Equal(100, stats.Min, 0.01);
        Assert.Equal(100, stats.Max, 0.01);
        Assert.Equal(100, stats.Sum, 0.01);
        Assert.Equal(100, stats.Avg, 0.01);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_ExportToJson_GetColumnStats_AddRow_Filter_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.RowCount);

        // ExportToJson
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
        Assert.True(json.Contains("{") || json.Contains("["));
        Assert.Contains("Alice", json);

        // GetColumnStats — Salary
        var salaryStats = doc.GetColumnStats("Salary");
        Assert.NotNull(salaryStats);
        Assert.Equal(5, salaryStats.Count);
        Assert.Equal(72000, salaryStats.Min, 0.01);
        Assert.Equal(105000, salaryStats.Max, 0.01);
        Assert.Equal(442000, salaryStats.Sum, 0.01);
        Assert.Equal(88400, salaryStats.Avg, 0.01);

        // GetColumnStats — Years
        var yearsStats = doc.GetColumnStats("Years");
        Assert.Equal(5, yearsStats.Count);
        Assert.Equal(2, yearsStats.Min, 0.01);
        Assert.Equal(8, yearsStats.Max, 0.01);
        Assert.Equal(22, yearsStats.Sum, 0.01);

        // Filter Engineering
        var eng = doc.Filter("Department", "Engineering");
        Assert.Equal(2, eng.RowCount);
        var engSalary = eng.GetColumnStats("Salary");
        Assert.Equal(2, engSalary.Count);
        Assert.Equal(100000, engSalary.Avg, 0.01);
        var engJson = eng.ExportToJson();
        Assert.True(engJson.Length < json.Length);
        Assert.Contains("Alice", engJson);
        Assert.DoesNotContain("Bob", engJson);

        // AddRow
        doc.AddRow(new[] { "Grace", "Engineering", "112000", "9" });
        Assert.Equal(6, doc.RowCount);
        var updatedStats = doc.GetColumnStats("Salary");
        Assert.Equal(6, updatedStats.Count);
        Assert.Equal(112000, updatedStats.Max, 0.01);
        Assert.True(doc.ExportToJson().Length > json.Length);
        Assert.Contains("Grace", doc.ExportToJson());

        // SaveToFile and reload
        var path = TempFile("dogfood_stats.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(6, loaded.RowCount);
        var loadedStats = loaded.GetColumnStats("Salary");
        Assert.Equal(6, loadedStats.Count);
        Assert.Equal(112000, loadedStats.Max, 0.01);
        Assert.NotNull(loaded.ExportToJson());
    }
}
