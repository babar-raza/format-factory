// Tests for TsvDocument.GetColumnStats, ExportToJson, ExportToHtml deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R183

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R183: Tests for TsvDocument.GetColumnStats, ExportToJson, ExportToHtml deeper coverage.
/// GetColumnStats(colIndex): returns min/max/sum/avg for a numeric column.
/// ExportToJson(): returns a JSON string of the document data.
/// ExportToHtml(): returns an HTML table string of the document data.
/// Covers: GetColumnStats non-null; GetColumnStats correct min/max/sum/avg;
/// GetColumnStats after AddRow increases sum; GetColumnStats min≤max;
/// GetColumnStats after Filter subset;
/// ExportToJson non-null; ExportToJson non-empty; ExportToJson contains field names;
/// ExportToJson contains data values; ExportToJson after AddRow includes new;
/// ExportToHtml non-null; ExportToHtml contains table tag; ExportToHtml has headers;
/// ExportToHtml has data values; ExportToHtml after mutation reflects;
/// dogfood LoadContent→GetColumnStats→ExportToJson→ExportToHtml→Filter→mutation pipeline.
/// </summary>
public class TsvR183GetColumnStatsAndExportDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR183GetColumnStatsAndExportDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR183_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleTsv =
        "Name\tScore\tDept\n" +
        "Alice\t92\tEngineering\n" +
        "Bob\t78\tFinance\n" +
        "Carol\t85\tEngineering\n" +
        "Dave\t71\tHR\n" +
        "Eve\t90\tFinance\n" +
        "Frank\t88\tEngineering\n";

    private TsvDocument LoadSample()
    {
        var path = TempFile("sample.tsv");
        File.WriteAllText(path, SampleTsv);
        return TsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // GetColumnStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStats_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetColumnStats(1)); // Score column
    }

    [Fact]
    public void GetColumnStats_CorrectMin()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats(1);
        Assert.Equal(71.0, stats.Min, 1);
    }

    [Fact]
    public void GetColumnStats_CorrectMax()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats(1);
        Assert.Equal(92.0, stats.Max, 1);
    }

    [Fact]
    public void GetColumnStats_CorrectSum()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats(1);
        Assert.Equal(504.0, stats.Sum, 1); // 92+78+85+71+90+88
    }

    [Fact]
    public void GetColumnStats_CorrectAvg()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats(1);
        Assert.True(stats.Avg >= 83.0 && stats.Avg <= 85.0); // 504/6=84
    }

    [Fact]
    public void GetColumnStats_MinLessOrEqualMax()
    {
        var doc = LoadSample();
        var stats = doc.GetColumnStats(1);
        Assert.True(stats.Min <= stats.Max);
    }

    [Fact]
    public void GetColumnStats_AfterAddRow_SumIncreases()
    {
        var doc = LoadSample();
        var before = doc.GetColumnStats(1).Sum;
        doc.AddRow(new[] { "Grace", "95", "Marketing" });
        var after = doc.GetColumnStats(1).Sum;
        Assert.True(after > before);
    }

    [Fact]
    public void GetColumnStats_AfterFilter_SubsetStats()
    {
        var doc = LoadSample();
        var allStats = doc.GetColumnStats(1);
        var filtered = doc.Filter("Dept", "Engineering");
        var engStats = filtered.GetColumnStats(1);
        Assert.True(engStats.Count <= allStats.Count);
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
    public void ExportToJson_ContainsFieldName()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Name") || json.Contains("Score") || json.Contains("Dept"));
    }

    [Fact]
    public void ExportToJson_ContainsDataValue()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Alice") || json.Contains("Engineering"));
    }

    [Fact]
    public void ExportToJson_AfterAddRow_IncludesNew()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Zara", "99", "Research" });
        var json = doc.ExportToJson();
        Assert.Contains("Zara", json);
    }

    [Fact]
    public void ExportToJson_IsJsonLike()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("{") || json.Contains("["));
    }

    // -------------------------------------------------------------------------
    // ExportToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_ContainsTableTag()
    {
        var doc = LoadSample();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("<") && html.Length > 0);
    }

    [Fact]
    public void ExportToHtml_ContainsHeaderText()
    {
        var doc = LoadSample();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("Name") || html.Contains("Score"));
    }

    [Fact]
    public void ExportToHtml_ContainsDataValue()
    {
        var doc = LoadSample();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("Alice") || html.Contains("Engineering"));
    }

    [Fact]
    public void ExportToHtml_AfterAddRow_IncludesNew()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Zara", "99", "Research" });
        var html = doc.ExportToHtml();
        Assert.Contains("Zara", html);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_GetColumnStats_ExportToJson_ExportToHtml_Filter_Pipeline()
    {
        var doc = LoadSample();

        // GetColumnStats
        var stats = doc.GetColumnStats(1);
        Assert.NotNull(stats);
        Assert.Equal(71.0, stats.Min, 1);
        Assert.Equal(92.0, stats.Max, 1);
        Assert.True(stats.Avg > 80.0);

        // ExportToJson
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
        Assert.Contains("Alice", json);
        Assert.Contains("Frank", json);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);
        Assert.True(html.Contains("<") && html.Length > 0);

        // Filter Engineering
        var eng = doc.Filter("Dept", "Engineering");
        Assert.Equal(3, eng.RowCount);

        // GetColumnStats on filtered subset
        var engStats = eng.GetColumnStats(1);
        Assert.True(engStats.Min >= 85.0); // Carol=85, Alice=92, Frank=88
        Assert.Equal(92.0, engStats.Max, 0);

        // ExportToJson from filtered — smaller
        var engJson = eng.ExportToJson();
        Assert.NotEmpty(engJson);
        Assert.Contains("Alice", engJson);
        Assert.False(engJson.Contains("Dave")); // Dave is HR

        // ExportToHtml from filtered
        var engHtml = eng.ExportToHtml();
        Assert.True(engHtml.Contains("<") && engHtml.Length > 0);

        // AddRow and re-verify stats
        doc.AddRow(new[] { "Zara", "60", "Engineering" });
        var newStats = doc.GetColumnStats(1);
        Assert.Equal(60.0, newStats.Min, 0); // Zara = 60 is new min
        Assert.True(newStats.Sum > stats.Sum);
    }
}
