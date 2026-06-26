// Tests for CsvDocument.GetDistinctValues, GetColumnStats, ToHtml, ExportToJson deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R176

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R176: Tests for CsvDocument.GetDistinctValues, GetColumnStats, ToHtml, ExportToJson deeper.
/// GetDistinctValues(colName): returns distinct values in a column.
/// GetColumnStats(colName): returns statistics (min/max/avg/count) for a numeric column.
/// ToHtml(): returns an HTML string representation of the document.
/// ExportToJson(): returns a JSON string representation of the document.
/// Covers: GetDistinctValues non-null; GetDistinctValues count correct (no duplicates);
/// GetDistinctValues contains expected; GetDistinctValues mixed dept column;
/// GetColumnStats non-null for numeric; GetColumnStats count matches row count;
/// ToHtml non-null and non-empty; ToHtml contains table tag; ToHtml contains header values;
/// ExportToJson non-null and non-empty; ExportToJson contains field names;
/// dogfood Load->GetDistinctValues->GetColumnStats->ToHtml->ExportToJson->Verify pipeline.
/// </summary>
public class CsvR176GetDistinctValuesAndStatsDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string SampleCsv =
        "Name,Dept,Score\n" +
        "Alice,Engineering,92\n" +
        "Bob,Finance,85\n" +
        "Carol,Engineering,78\n" +
        "Dave,HR,91\n" +
        "Eve,Finance,88";

    public CsvR176GetDistinctValuesAndStatsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR176_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private CsvDocument LoadSample()
    {
        var path = TempFile("sample.csv");
        File.WriteAllText(path, SampleCsv);
        return CsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetDistinctValues("Dept"));
    }

    [Fact]
    public void GetDistinctValues_Count_CorrectNoDuplicates()
    {
        var doc = LoadSample();
        var distinct = doc.GetDistinctValues("Dept");
        // Engineering, Finance, HR = 3 distinct
        Assert.Equal(3, distinct.Count);
    }

    [Fact]
    public void GetDistinctValues_ContainsExpectedValues()
    {
        var doc = LoadSample();
        var distinct = doc.GetDistinctValues("Dept");
        Assert.Contains("Engineering", distinct);
        Assert.Contains("Finance", distinct);
        Assert.Contains("HR", distinct);
    }

    [Fact]
    public void GetDistinctValues_AllSameValue_ReturnsOne()
    {
        var path = TempFile("same.csv");
        File.WriteAllText(path, "Col\nA\nA\nA\nA");
        var doc = CsvDocument.LoadFile(path);
        var distinct = doc.GetDistinctValues("Col");
        Assert.Equal(1, distinct.Count);
    }

    [Fact]
    public void GetDistinctValues_NameColumn_AllUnique()
    {
        var doc = LoadSample();
        var distinct = doc.GetDistinctValues("Name");
        Assert.Equal(5, distinct.Count);
    }

    // -------------------------------------------------------------------------
    // GetColumnStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStats_NonNull_ForNumericColumn()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats("Score");
        Assert.NotNull(stats);
    }

    [Fact]
    public void GetColumnStats_Count_MatchesRowCount()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats("Score");
        Assert.Equal(doc.RowCount, stats.Count);
    }

    [Fact]
    public void GetColumnStats_MinLessThanMax()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats("Score");
        Assert.True(stats.Min <= stats.Max);
    }

    [Fact]
    public void GetColumnStats_AvgBetweenMinAndMax()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats("Score");
        Assert.True(stats.Average >= stats.Min);
        Assert.True(stats.Average <= stats.Max);
    }

    // -------------------------------------------------------------------------
    // ToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void ToHtml_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ToHtml());
    }

    [Fact]
    public void ToHtml_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(doc.ToHtml());
    }

    [Fact]
    public void ToHtml_ContainsTableTag()
    {
        var doc = LoadSample();
        var html = doc.ToHtml();
        Assert.Contains("<table", html.ToLower());
    }

    [Fact]
    public void ToHtml_ContainsHeaderValues()
    {
        var doc = LoadSample();
        var html = doc.ToHtml();
        Assert.Contains("Name", html);
        Assert.Contains("Dept", html);
        Assert.Contains("Score", html);
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
    public void ExportToJson_ContainsFieldNames()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.Contains("Name", json);
    }

    [Fact]
    public void ExportToJson_ContainsDataValues()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.Contains("Alice", json);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Load_GetDistinctValues_GetColumnStats_ToHtml_ExportToJson_Verify_Pipeline()
    {
        // Load
        var doc = LoadSample();
        Assert.Equal(5, doc.RowCount);

        // GetDistinctValues
        var depts = doc.GetDistinctValues("Dept");
        Assert.Equal(3, depts.Count);
        Assert.Contains("Engineering", depts);

        // GetColumnStats
        var stats = doc.GetColumnStats("Score");
        Assert.NotNull(stats);
        Assert.Equal(5, stats.Count);
        Assert.True(stats.Min >= 0);
        Assert.True(stats.Max <= 100);

        // ToHtml
        var html = doc.ToHtml();
        Assert.NotNull(html);
        Assert.Contains("Alice", html);

        // ExportToJson
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.Contains("Engineering", json);

        // Filter and verify distinct
        var engOnly = doc.Filter(r => r.GetCellValue("Dept") == "Engineering");
        var engDepts = engOnly.GetDistinctValues("Dept");
        Assert.Equal(1, engDepts.Count);
        Assert.Contains("Engineering", engDepts);
    }
}
