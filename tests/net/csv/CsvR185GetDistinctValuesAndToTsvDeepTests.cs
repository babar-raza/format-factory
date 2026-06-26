// Tests for CsvDocument.GetDistinctValues, ToTsv, ExportToJson deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R185

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R185: Tests for CsvDocument.GetDistinctValues, ToTsv, ExportToJson deeper coverage.
/// GetDistinctValues(colName): returns distinct values in a column.
/// ToTsv(): converts the CSV document to a TSV string.
/// ExportToJson(): exports the document as a JSON string.
/// Covers: GetDistinctValues non-null; GetDistinctValues count≤RowCount;
/// GetDistinctValues contains all depts; GetDistinctValues all-same=1;
/// GetDistinctValues after AddRow includes new; GetDistinctValues all-unique=RowCount;
/// ToTsv non-null; ToTsv non-empty; ToTsv contains tab char; ToTsv has headers;
/// ToTsv has data values; ToTsv after AddRow includes new;
/// ExportToJson non-null; ExportToJson non-empty; ExportToJson is JSON-like;
/// ExportToJson contains field/data; ExportToJson after Filter smaller;
/// dogfood LoadContent→GetDistinctValues→ToTsv→ExportToJson→Filter→mutation pipeline.
/// </summary>
public class CsvR185GetDistinctValuesAndToTsvDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR185GetDistinctValuesAndToTsvDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR185_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleCsv =
        "Name,Score,Dept\n" +
        "Alice,92,Engineering\n" +
        "Bob,78,Finance\n" +
        "Carol,85,Engineering\n" +
        "Dave,71,HR\n" +
        "Eve,90,Finance\n" +
        "Frank,88,Engineering\n";

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
    public void GetDistinctValues_CountLessOrEqualRowCount()
    {
        var doc = LoadSample();
        Assert.True(doc.GetDistinctValues("Dept").Count <= doc.RowCount);
    }

    [Fact]
    public void GetDistinctValues_ThreeDepts()
    {
        var doc = LoadSample();
        Assert.Equal(3, doc.GetDistinctValues("Dept").Count);
    }

    [Fact]
    public void GetDistinctValues_ContainsAllDepts()
    {
        var doc = LoadSample();
        var depts = doc.GetDistinctValues("Dept");
        Assert.Contains("Engineering", depts);
        Assert.Contains("Finance", depts);
        Assert.Contains("HR", depts);
    }

    [Fact]
    public void GetDistinctValues_AllSame_ReturnsOne()
    {
        var path = TempFile("allsame.csv");
        File.WriteAllText(path, "Dept\nEng\nEng\nEng\n");
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(1, doc.GetDistinctValues("Dept").Count);
    }

    [Fact]
    public void GetDistinctValues_AfterAddRow_IncludesNew()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Grace", "88", "Research" });
        var depts = doc.GetDistinctValues("Dept");
        Assert.Contains("Research", depts);
        Assert.Equal(4, depts.Count);
    }

    [Fact]
    public void GetDistinctValues_AllUnique_EqualRowCount()
    {
        var doc = LoadSample();
        var names = doc.GetDistinctValues("Name");
        Assert.Equal(doc.RowCount, names.Count);
    }

    // -------------------------------------------------------------------------
    // ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToTsv_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ToTsv());
    }

    [Fact]
    public void ToTsv_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(doc.ToTsv());
    }

    [Fact]
    public void ToTsv_ContainsTabChar()
    {
        var doc = LoadSample();
        Assert.Contains("\t", doc.ToTsv());
    }

    [Fact]
    public void ToTsv_ContainsHeaderText()
    {
        var doc = LoadSample();
        var tsv = doc.ToTsv();
        Assert.True(tsv.Contains("Name") || tsv.Contains("Score"));
    }

    [Fact]
    public void ToTsv_ContainsDataValue()
    {
        var doc = LoadSample();
        var tsv = doc.ToTsv();
        Assert.Contains("Alice", tsv);
    }

    [Fact]
    public void ToTsv_AfterAddRow_IncludesNew()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Zara", "99", "Research" });
        var tsv = doc.ToTsv();
        Assert.Contains("Zara", tsv);
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
    public void ExportToJson_IsJsonLike()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("{") || json.Contains("["));
    }

    [Fact]
    public void ExportToJson_ContainsFieldName()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Name") || json.Contains("Score"));
    }

    [Fact]
    public void ExportToJson_ContainsDataValue()
    {
        var doc = LoadSample();
        var json = doc.ExportToJson();
        Assert.Contains("Alice", json);
    }

    [Fact]
    public void ExportToJson_AfterFilter_Smaller()
    {
        var doc = LoadSample();
        var all = doc.ExportToJson();
        var filtered = doc.Filter("Dept", "HR").ExportToJson();
        Assert.True(filtered.Length < all.Length);
    }

    [Fact]
    public void ExportToJson_AfterSetCellValue_Reflects()
    {
        var doc = LoadSample();
        doc.SetCellValue(0, "Name", "ALICE_MODIFIED");
        var json = doc.ExportToJson();
        Assert.Contains("ALICE_MODIFIED", json);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_GetDistinctValues_ToTsv_ExportToJson_Filter_Pipeline()
    {
        var doc = LoadSample();

        // GetDistinctValues
        var depts = doc.GetDistinctValues("Dept");
        Assert.Equal(3, depts.Count);
        Assert.Contains("Engineering", depts);
        Assert.Contains("Finance", depts);
        Assert.Contains("HR", depts);

        // ToTsv
        var tsv = doc.ToTsv();
        Assert.NotNull(tsv);
        Assert.Contains("\t", tsv);
        Assert.Contains("Alice", tsv);
        Assert.Contains("Frank", tsv);

        // ExportToJson
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.True(json.Contains("{") || json.Contains("["));
        Assert.Contains("Alice", json);
        Assert.Contains("Engineering", json);

        // Filter Engineering
        var eng = doc.Filter("Dept", "Engineering");
        Assert.Equal(3, eng.RowCount);

        // GetDistinctValues on filtered — only one dept
        var engDepts = eng.GetDistinctValues("Dept");
        Assert.Equal(1, engDepts.Count);

        // ToTsv from filtered
        var engTsv = eng.ToTsv();
        Assert.Contains("Alice", engTsv);
        Assert.False(engTsv.Contains("Dave")); // Dave is HR

        // ExportToJson from filtered
        var engJson = eng.ExportToJson();
        Assert.Contains("Alice", engJson);
        Assert.True(engJson.Length < json.Length);

        // AddRow with new dept — distinct values increases
        doc.AddRow(new[] { "Grace", "88", "Research" });
        var newDepts = doc.GetDistinctValues("Dept");
        Assert.Equal(4, newDepts.Count);
        Assert.Contains("Research", newDepts);

        // SetCellValue and verify ToTsv reflects change
        doc.SetCellValue(0, "Name", "ALICE_UPDATED");
        var updatedTsv = doc.ToTsv();
        Assert.Contains("ALICE_UPDATED", updatedTsv);
    }
}
