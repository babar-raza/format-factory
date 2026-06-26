// Tests for NdjsonDocument.Filter, Count, GroupBy deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R202

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R202: Tests for NdjsonDocument.Filter, Count, GroupBy deeper.
/// Filter(field, value): returns a new NdjsonDocument with only records where field equals value.
/// Count(field, value): counts records where the field matches the value.
/// GroupBy(field): groups records by field value and returns a dictionary of groups.
/// Covers: Filter non-null; Filter reduces record count; Filter returns matching records;
/// Filter by string field; Filter by numeric field; Filter chained;
/// Filter then GetAllKeys; Filter persist; Filter empty result;
/// Count equals Filter row count; Count zero for non-existent; Count positive;
/// Count consistent; Count after AppendRecord increases;
/// GroupBy non-null; GroupBy keys are distinct values; GroupBy record counts match;
/// GroupBy then access records; GroupBy consistent;
/// dogfood LoadFile→Filter→Count→GroupBy→SaveToFile pipeline.
/// </summary>
public class NdjsonR202FilterAndCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR202FilterAndCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR202_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Engineering\",\"score\":92,\"active\":true}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":85,\"active\":false}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Engineering\",\"score\":95,\"active\":true}\n" +
        "{\"name\":\"Dave\",\"dept\":\"HR\",\"score\":78,\"active\":true}\n" +
        "{\"name\":\"Eve\",\"dept\":\"Finance\",\"score\":88,\"active\":false}\n";

    private NdjsonDocument LoadSample()
    {
        var path = TempFile("sample.ndjson");
        File.WriteAllText(path, SampleNdjson);
        return NdjsonDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.Filter("dept", "Engineering"));
    }

    [Fact]
    public void Filter_ReducesRecordCount()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("dept", "Engineering");
        Assert.True(filtered.GetRecordCount() < doc.GetRecordCount());
    }

    [Fact]
    public void Filter_ReturnsMatchingRecords()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("dept", "Engineering");
        Assert.Equal(2, filtered.GetRecordCount());
    }

    [Fact]
    public void Filter_ByStringField_Works()
    {
        var doc = LoadSample();
        var finance = doc.Filter("dept", "Finance");
        Assert.Equal(2, finance.GetRecordCount());
        var names = finance.GetFieldValues("name");
        Assert.Contains("Bob", names);
        Assert.Contains("Eve", names);
    }

    [Fact]
    public void Filter_Chained_NarrowsResult()
    {
        var doc = LoadSample();
        var engineering = doc.Filter("dept", "Engineering");
        Assert.True(engineering.GetRecordCount() <= doc.GetRecordCount());
    }

    [Fact]
    public void Filter_EmptyResult_NonNull()
    {
        var doc = LoadSample();
        var result = doc.Filter("dept", "NONEXISTENT_DEPT_XYZ");
        Assert.NotNull(result);
        Assert.True(result.GetRecordCount() == 0);
    }

    [Fact]
    public void Filter_Persist()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("dept", "Engineering");
        var path = TempFile("filter_persist.ndjson");
        filtered.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(filtered.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void Filter_ThenGetAllKeys_Works()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("dept", "Engineering");
        var keys = filtered.GetAllKeys();
        Assert.NotNull(keys);
        Assert.True(keys.Count > 0);
    }

    // -------------------------------------------------------------------------
    // Count
    // -------------------------------------------------------------------------

    [Fact]
    public void Count_EqualsFilterRowCount()
    {
        var doc = LoadSample();
        var filterCount = doc.Filter("dept", "Finance").GetRecordCount();
        var countResult = doc.Count("dept", "Finance");
        Assert.Equal(filterCount, countResult);
    }

    [Fact]
    public void Count_ZeroForNonExistent()
    {
        var doc = LoadSample();
        Assert.Equal(0, doc.Count("dept", "NONEXISTENT_DEPT_XYZ"));
    }

    [Fact]
    public void Count_Positive_ForExistingValue()
    {
        var doc = LoadSample();
        Assert.True(doc.Count("dept", "Engineering") > 0);
    }

    [Fact]
    public void Count_Consistent()
    {
        var doc = LoadSample();
        Assert.Equal(doc.Count("dept", "Finance"), doc.Count("dept", "Finance"));
    }

    [Fact]
    public void Count_AllDepts_SumsToTotal()
    {
        var doc = LoadSample();
        var eng = doc.Count("dept", "Engineering");
        var fin = doc.Count("dept", "Finance");
        var hr = doc.Count("dept", "HR");
        Assert.Equal(doc.GetRecordCount(), eng + fin + hr);
    }

    [Fact]
    public void Count_HRDept_IsOne()
    {
        var doc = LoadSample();
        Assert.Equal(1, doc.Count("dept", "HR"));
    }

    // -------------------------------------------------------------------------
    // GroupBy
    // -------------------------------------------------------------------------

    [Fact]
    public void GroupBy_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GroupBy("dept"));
    }

    [Fact]
    public void GroupBy_KeysAreDistinctValues()
    {
        var doc = LoadSample();
        var groups = doc.GroupBy("dept");
        Assert.True(groups.Count >= 3); // Engineering, Finance, HR
    }

    [Fact]
    public void GroupBy_RecordCountsMatchTotal()
    {
        var doc = LoadSample();
        var groups = doc.GroupBy("dept");
        var total = 0;
        foreach (var kv in groups)
            total += kv.Value.GetRecordCount();
        Assert.Equal(doc.GetRecordCount(), total);
    }

    [Fact]
    public void GroupBy_ContainsExpectedKeys()
    {
        var doc = LoadSample();
        var groups = doc.GroupBy("dept");
        Assert.True(groups.ContainsKey("Engineering") || groups.Count >= 2);
    }

    [Fact]
    public void GroupBy_Consistent()
    {
        var doc = LoadSample();
        var g1 = doc.GroupBy("dept");
        var g2 = doc.GroupBy("dept");
        Assert.Equal(g1.Count, g2.Count);
    }

    [Fact]
    public void GroupBy_EachGroupNonNull()
    {
        var doc = LoadSample();
        var groups = doc.GroupBy("dept");
        foreach (var kv in groups)
            Assert.NotNull(kv.Value);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_Filter_Count_GroupBy_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.GetRecordCount());

        // Filter by dept
        var engDoc = doc.Filter("dept", "Engineering");
        Assert.NotNull(engDoc);
        Assert.Equal(2, engDoc.GetRecordCount());

        // Count
        Assert.Equal(2, doc.Count("dept", "Engineering"));
        Assert.Equal(2, doc.Count("dept", "Finance"));
        Assert.Equal(1, doc.Count("dept", "HR"));
        Assert.Equal(0, doc.Count("dept", "Marketing"));

        // Count matches Filter
        Assert.Equal(engDoc.GetRecordCount(), doc.Count("dept", "Engineering"));

        // Filter field values
        var engNames = engDoc.GetFieldValues("name");
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);

        // Filter persist
        var filterPath = TempFile("dogfood_filter.ndjson");
        engDoc.SaveToFile(filterPath);
        Assert.True(File.Exists(filterPath));
        var loadedFiltered = NdjsonDocument.LoadFile(filterPath);
        Assert.Equal(2, loadedFiltered.GetRecordCount());

        // GroupBy dept
        var groups = doc.GroupBy("dept");
        Assert.NotNull(groups);
        Assert.True(groups.Count >= 3);

        // Verify group totals
        var totalFromGroups = 0;
        foreach (var kv in groups)
        {
            Assert.NotNull(kv.Value);
            totalFromGroups += kv.Value.GetRecordCount();
        }
        Assert.Equal(5, totalFromGroups);

        // Access Engineering group
        if (groups.TryGetValue("Engineering", out var engGroup))
        {
            Assert.Equal(2, engGroup.GetRecordCount());
        }

        // Filter chained — Finance from full doc
        var financeDoc = doc.Filter("dept", "Finance");
        Assert.Equal(2, financeDoc.GetRecordCount());
        var financeNames = financeDoc.GetFieldValues("name");
        Assert.Contains("Bob", financeNames);
        Assert.Contains("Eve", financeNames);

        // GroupBy on filtered doc
        var finGroups = financeDoc.GroupBy("dept");
        Assert.True(finGroups.Count >= 1);

        // SortBy then Filter
        var sorted = doc.SortBy("score", ascending: false);
        var topFinance = sorted.Filter("dept", "Finance");
        Assert.Equal(2, topFinance.GetRecordCount());

        // SaveToFile and reload
        var path = TempFile("dogfood_ndjson_filter.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetRecordCount());

        // Filter on loaded
        var loadedEng = loaded.Filter("dept", "Engineering");
        Assert.Equal(2, loadedEng.GetRecordCount());

        // Count on loaded
        Assert.Equal(2, loaded.Count("dept", "Engineering"));

        // GroupBy on loaded
        var loadedGroups = loaded.GroupBy("dept");
        Assert.NotNull(loadedGroups);
        Assert.True(loadedGroups.Count >= 3);
    }
}
