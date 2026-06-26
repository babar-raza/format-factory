// Tests for TsvDocument.ExportToJson, Merge, GetDistinctValues deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R187

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R187: Tests for TsvDocument.ExportToJson, Merge, GetDistinctValues deeper coverage.
/// ExportToJson(): returns the document as a JSON string.
/// Merge(other): combines rows from two TsvDocuments.
/// GetDistinctValues(colName): returns distinct values in a named column.
/// Covers: ExportToJson non-null; ExportToJson non-empty; ExportToJson is JSON-like;
/// ExportToJson contains field names; ExportToJson contains data; ExportToJson after AddRow;
/// ExportToJson after Filter smaller; Merge non-null; Merge count = sum;
/// Merge contains rows from both; Merge GetColumnValues all; Merge with empty same count;
/// Merge headers from first; GetDistinctValues non-null; GetDistinctValues three depts;
/// GetDistinctValues all-same one; GetDistinctValues all-unique count;
/// GetDistinctValues after AddRow includes new; GetDistinctValues after Filter;
/// dogfood LoadContent×2→Merge→GetDistinctValues→ExportToJson→Filter pipeline.
/// </summary>
public class TsvR187ExportToJsonAndMergeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR187ExportToJsonAndMergeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR187_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string Doc1Tsv =
        "Name\tScore\tDept\n" +
        "Alice\t92\tEngineering\n" +
        "Bob\t78\tFinance\n" +
        "Carol\t85\tEngineering\n";

    private static readonly string Doc2Tsv =
        "Name\tScore\tDept\n" +
        "Dave\t71\tHR\n" +
        "Eve\t90\tFinance\n" +
        "Frank\t88\tEngineering\n";

    private TsvDocument LoadDoc1()
    {
        var path = TempFile("doc1.tsv");
        File.WriteAllText(path, Doc1Tsv);
        return TsvDocument.LoadFile(path);
    }

    private TsvDocument LoadDoc2()
    {
        var path = TempFile("doc2.tsv");
        File.WriteAllText(path, Doc2Tsv);
        return TsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // ExportToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_NonNull()
    {
        var doc = LoadDoc1();
        Assert.NotNull(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_NonEmpty()
    {
        var doc = LoadDoc1();
        Assert.NotEmpty(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_IsJsonLike()
    {
        var doc = LoadDoc1();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("{") || json.Contains("["));
    }

    [Fact]
    public void ExportToJson_ContainsFieldName()
    {
        var doc = LoadDoc1();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Name") || json.Contains("Score"));
    }

    [Fact]
    public void ExportToJson_ContainsDataValue()
    {
        var doc = LoadDoc1();
        Assert.Contains("Alice", doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_AfterAddRow_Larger()
    {
        var doc = LoadDoc1();
        var before = doc.ExportToJson().Length;
        doc.AddRow(new[] { "Zara", "99", "Research" });
        Assert.True(doc.ExportToJson().Length > before);
    }

    [Fact]
    public void ExportToJson_AfterFilter_Smaller()
    {
        var doc = LoadDoc1();
        var all = doc.ExportToJson();
        var filtered = doc.Filter("Dept", "Finance").ExportToJson();
        Assert.True(filtered.Length < all.Length);
    }

    // -------------------------------------------------------------------------
    // Merge
    // -------------------------------------------------------------------------

    [Fact]
    public void Merge_NonNull()
    {
        var doc1 = LoadDoc1();
        var doc2 = LoadDoc2();
        Assert.NotNull(doc1.Merge(doc2));
    }

    [Fact]
    public void Merge_CountEqualsSumOfBoth()
    {
        var doc1 = LoadDoc1();
        var doc2 = LoadDoc2();
        var merged = doc1.Merge(doc2);
        Assert.Equal(doc1.RowCount + doc2.RowCount, merged.RowCount);
    }

    [Fact]
    public void Merge_ContainsRowsFromBoth()
    {
        var doc1 = LoadDoc1();
        var doc2 = LoadDoc2();
        var merged = doc1.Merge(doc2);
        var names = merged.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Frank", names);
    }

    [Fact]
    public void Merge_GetColumnValues_AllSixNames()
    {
        var doc1 = LoadDoc1();
        var doc2 = LoadDoc2();
        var names = doc1.Merge(doc2).GetColumnValues("Name");
        Assert.Equal(6, names.Count);
    }

    [Fact]
    public void Merge_WithEmpty_SameCount()
    {
        var doc1 = LoadDoc1();
        var emptyPath = TempFile("empty.tsv");
        File.WriteAllText(emptyPath, "Name\tScore\tDept\n");
        var empty = TsvDocument.LoadFile(emptyPath);
        var merged = doc1.Merge(empty);
        Assert.Equal(doc1.RowCount, merged.RowCount);
    }

    [Fact]
    public void Merge_HeadersFromFirstDoc()
    {
        var doc1 = LoadDoc1();
        var doc2 = LoadDoc2();
        var headers = doc1.Merge(doc2).GetHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Dept", headers);
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = LoadDoc1();
        Assert.NotNull(doc.GetDistinctValues("Dept"));
    }

    [Fact]
    public void GetDistinctValues_TwoDepts()
    {
        var doc = LoadDoc1();
        Assert.Equal(2, doc.GetDistinctValues("Dept").Count); // Eng + Finance
    }

    [Fact]
    public void GetDistinctValues_AllSame_ReturnsOne()
    {
        var path = TempFile("allsame.tsv");
        File.WriteAllText(path, "Dept\nEng\nEng\nEng\n");
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(1, doc.GetDistinctValues("Dept").Count);
    }

    [Fact]
    public void GetDistinctValues_AllUnique_EqualRowCount()
    {
        var doc = LoadDoc1();
        Assert.Equal(doc.RowCount, doc.GetDistinctValues("Name").Count);
    }

    [Fact]
    public void GetDistinctValues_AfterAddRow_IncludesNew()
    {
        var doc = LoadDoc1();
        doc.AddRow(new[] { "Zara", "99", "Research" });
        var depts = doc.GetDistinctValues("Dept");
        Assert.Contains("Research", depts);
    }

    [Fact]
    public void GetDistinctValues_AfterMerge_IncludesAllDepts()
    {
        var doc1 = LoadDoc1();
        var doc2 = LoadDoc2();
        var merged = doc1.Merge(doc2);
        var depts = merged.GetDistinctValues("Dept");
        Assert.Contains("Engineering", depts);
        Assert.Contains("Finance", depts);
        Assert.Contains("HR", depts);
        Assert.Equal(3, depts.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_Merge_GetDistinctValues_ExportToJson_Filter_Pipeline()
    {
        var doc1 = LoadDoc1();
        var doc2 = LoadDoc2();

        // Merge
        var merged = doc1.Merge(doc2);
        Assert.Equal(6, merged.RowCount);

        // GetDistinctValues on merged
        var depts = merged.GetDistinctValues("Dept");
        Assert.Equal(3, depts.Count);
        Assert.Contains("Engineering", depts);
        Assert.Contains("Finance", depts);
        Assert.Contains("HR", depts);

        // ExportToJson
        var json = merged.ExportToJson();
        Assert.NotNull(json);
        Assert.True(json.Contains("{") || json.Contains("["));
        Assert.Contains("Alice", json);
        Assert.Contains("Frank", json);

        // Filter Engineering (3 records)
        var eng = merged.Filter("Dept", "Engineering");
        Assert.Equal(3, eng.RowCount);

        // ExportToJson from filtered — smaller
        var engJson = eng.ExportToJson();
        Assert.True(engJson.Length < json.Length);
        Assert.Contains("Alice", engJson);
        Assert.False(engJson.Contains("Dave")); // HR

        // GetDistinctValues on filtered — only Engineering
        var engDepts = eng.GetDistinctValues("Dept");
        Assert.Equal(1, engDepts.Count);
        Assert.Contains("Engineering", engDepts);

        // AddRow to merged and verify distinct updates
        merged.AddRow(new[] { "Zara", "99", "Research" });
        var updatedDepts = merged.GetDistinctValues("Dept");
        Assert.Equal(4, updatedDepts.Count);
        Assert.Contains("Research", updatedDepts);

        // ExportToJson after AddRow — includes Zara
        var updatedJson = merged.ExportToJson();
        Assert.Contains("Zara", updatedJson);
    }
}
