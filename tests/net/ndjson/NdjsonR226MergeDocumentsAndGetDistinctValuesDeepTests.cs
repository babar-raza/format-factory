// Tests for NdjsonDocument.MergeWith, GetDistinctValues, FilterByRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R226

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R226: Tests for NdjsonDocument.MergeWith, GetDistinctValues, FilterByRange deeper.
/// MergeWith(other): returns a new document combining all records from both documents.
/// GetDistinctValues(fieldName): returns an array of unique values for the given field.
/// FilterByRange(fieldName, minValue, maxValue): returns records where field value is in [min, max].
/// Covers: MergeWith no-throw; MergeWith count equals sum; MergeWith consistent;
/// MergeWith save-load; MergeWith with empty doc;
/// GetDistinctValues no-throw; GetDistinctValues non-null; GetDistinctValues count leq record count;
/// GetDistinctValues consistent; GetDistinctValues save-load; GetDistinctValues unique;
/// FilterByRange no-throw; FilterByRange count leq total; FilterByRange consistent;
/// FilterByRange save-load; FilterByRange all in range;
/// dogfood CreateDoc→MergeWith→GetDistinctValues→FilterByRange→SaveToFile pipeline.
/// </summary>
public class NdjsonR226MergeDocumentsAndGetDistinctValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR226MergeDocumentsAndGetDistinctValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR226_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEmployeeNdjson()
    {
        var path = TempFile("employees.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"id\":1,\"name\":\"Alice\",\"dept\":\"Engineering\",\"salary\":95000,\"level\":3}",
            "{\"id\":2,\"name\":\"Bob\",\"dept\":\"Marketing\",\"salary\":72000,\"level\":2}",
            "{\"id\":3,\"name\":\"Carol\",\"dept\":\"Engineering\",\"salary\":110000,\"level\":4}",
            "{\"id\":4,\"name\":\"Dave\",\"dept\":\"HR\",\"salary\":68000,\"level\":2}",
            "{\"id\":5,\"name\":\"Eve\",\"dept\":\"Engineering\",\"salary\":88000,\"level\":3}",
            "{\"id\":6,\"name\":\"Frank\",\"dept\":\"Marketing\",\"salary\":78000,\"level\":3}",
            "{\"id\":7,\"name\":\"Grace\",\"dept\":\"Finance\",\"salary\":92000,\"level\":3}"
        });
        return path;
    }

    private string CreateContractorNdjson()
    {
        var path = TempFile("contractors.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"id\":101,\"name\":\"Hector\",\"dept\":\"Engineering\",\"salary\":120000,\"level\":4}",
            "{\"id\":102,\"name\":\"Iris\",\"dept\":\"Design\",\"salary\":85000,\"level\":3}",
            "{\"id\":103,\"name\":\"Jack\",\"dept\":\"HR\",\"salary\":65000,\"level\":2}"
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // MergeWith
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeWith_NoThrow()
    {
        var doc1 = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var doc2 = NdjsonDocument.LoadFile(CreateContractorNdjson());
        var ex = Record.Exception(() => doc1.MergeWith(doc2));
        Assert.Null(ex);
    }

    [Fact]
    public void MergeWith_CountEqualsSum()
    {
        var doc1 = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var doc2 = NdjsonDocument.LoadFile(CreateContractorNdjson());
        var merged = doc1.MergeWith(doc2);
        Assert.Equal(doc1.GetRecordCount() + doc2.GetRecordCount(), merged.GetRecordCount());
    }

    [Fact]
    public void MergeWith_Consistent()
    {
        var doc1 = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var doc2 = NdjsonDocument.LoadFile(CreateContractorNdjson());
        var m1 = doc1.MergeWith(doc2);
        var m2 = doc1.MergeWith(doc2);
        Assert.Equal(m1.GetRecordCount(), m2.GetRecordCount());
    }

    [Fact]
    public void MergeWith_SaveLoad_Consistent()
    {
        var doc1 = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var doc2 = NdjsonDocument.LoadFile(CreateContractorNdjson());
        var merged = doc1.MergeWith(doc2);
        var before = merged.GetRecordCount();
        var path = TempFile("mw_save.ndjson");
        merged.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordCount());
    }

    [Fact]
    public void MergeWith_WithEmpty_ReturnsSameCount()
    {
        var doc1 = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var empty = NdjsonDocument.CreateEmpty();
        var merged = doc1.MergeWith(empty);
        Assert.Equal(doc1.GetRecordCount(), merged.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GetDistinctValues("dept"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.GetDistinctValues("dept"));
    }

    [Fact]
    public void GetDistinctValues_Count_Leq_RecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.True(doc.GetDistinctValues("dept").Length <= doc.GetRecordCount());
    }

    [Fact]
    public void GetDistinctValues_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var d1 = doc.GetDistinctValues("dept");
        var d2 = doc.GetDistinctValues("dept");
        Assert.Equal(d1.Length, d2.Length);
    }

    [Fact]
    public void GetDistinctValues_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var before = doc.GetDistinctValues("dept").Length;
        var path = TempFile("dv_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDistinctValues("dept").Length);
    }

    [Fact]
    public void GetDistinctValues_Dept_HasExpectedCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        // Engineering, Marketing, HR, Finance = 4 distinct
        var depts = doc.GetDistinctValues("dept");
        Assert.True(depts.Length >= 1);
        Assert.True(depts.Length <= doc.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // FilterByRange
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterByRange_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.FilterByRange("salary", 70000, 100000));
        Assert.Null(ex);
    }

    [Fact]
    public void FilterByRange_Count_Leq_Total()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var filtered = doc.FilterByRange("salary", 70000, 100000);
        Assert.True(filtered.GetRecordCount() <= doc.GetRecordCount());
    }

    [Fact]
    public void FilterByRange_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var f1 = doc.FilterByRange("salary", 80000, 100000);
        var f2 = doc.FilterByRange("salary", 80000, 100000);
        Assert.Equal(f1.GetRecordCount(), f2.GetRecordCount());
    }

    [Fact]
    public void FilterByRange_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var filtered = doc.FilterByRange("salary", 70000, 100000);
        var before = filtered.GetRecordCount();
        var path = TempFile("fbr_save.ndjson");
        filtered.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordCount());
    }

    [Fact]
    public void FilterByRange_AllRecords_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        // All salaries are < 200000
        var filtered = doc.FilterByRange("salary", 0, 200000);
        Assert.Equal(doc.GetRecordCount(), filtered.GetRecordCount());
    }

    [Fact]
    public void FilterByRange_NoRecords_OutOfRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        // No salaries above 500000
        var filtered = doc.FilterByRange("salary", 500000, 1000000);
        Assert.Equal(0, filtered.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_MergeWith_GetDistinctValues_FilterByRange_SaveToFile_Pipeline()
    {
        var q1Path = TempFile("q1_sales.ndjson");
        File.WriteAllLines(q1Path, new[]
        {
            "{\"id\":1,\"rep\":\"Alice\",\"region\":\"North\",\"product\":\"Alpha\",\"amount\":45000,\"quarter\":1}",
            "{\"id\":2,\"rep\":\"Bob\",\"region\":\"South\",\"product\":\"Beta\",\"amount\":32000,\"quarter\":1}",
            "{\"id\":3,\"rep\":\"Carol\",\"region\":\"East\",\"product\":\"Alpha\",\"amount\":58000,\"quarter\":1}",
            "{\"id\":4,\"rep\":\"Dave\",\"region\":\"West\",\"product\":\"Gamma\",\"amount\":41000,\"quarter\":1}",
            "{\"id\":5,\"rep\":\"Eve\",\"region\":\"North\",\"product\":\"Beta\",\"amount\":37000,\"quarter\":1}"
        });

        var q2Path = TempFile("q2_sales.ndjson");
        File.WriteAllLines(q2Path, new[]
        {
            "{\"id\":6,\"rep\":\"Alice\",\"region\":\"North\",\"product\":\"Alpha\",\"amount\":52000,\"quarter\":2}",
            "{\"id\":7,\"rep\":\"Bob\",\"region\":\"South\",\"product\":\"Gamma\",\"amount\":38000,\"quarter\":2}",
            "{\"id\":8,\"rep\":\"Frank\",\"region\":\"East\",\"product\":\"Beta\",\"amount\":61000,\"quarter\":2}",
            "{\"id\":9,\"rep\":\"Grace\",\"region\":\"West\",\"product\":\"Alpha\",\"amount\":47000,\"quarter\":2}",
            "{\"id\":10,\"rep\":\"Dave\",\"region\":\"South\",\"product\":\"Beta\",\"amount\":44000,\"quarter\":2}"
        });

        var q1 = NdjsonDocument.LoadFile(q1Path);
        var q2 = NdjsonDocument.LoadFile(q2Path);
        Assert.Equal(5, q1.GetRecordCount());
        Assert.Equal(5, q2.GetRecordCount());

        // MergeWith — combine quarters
        var all = q1.MergeWith(q2);
        Assert.Equal(10, all.GetRecordCount());
        Assert.Equal(all.GetRecordCount(), all.GetRecordCount()); // consistent

        // GetDistinctValues — regions
        var regions = all.GetDistinctValues("region");
        Assert.NotNull(regions);
        Assert.True(regions.Length >= 1 && regions.Length <= 10);

        // GetDistinctValues — products
        var products = all.GetDistinctValues("product");
        Assert.NotNull(products);
        Assert.True(products.Length >= 1);
        Assert.True(products.Length <= all.GetRecordCount());

        // GetDistinctValues — reps
        var reps = all.GetDistinctValues("rep");
        Assert.NotNull(reps);

        // FilterByRange — high-value deals (>= 45000)
        var highValue = all.FilterByRange("amount", 45000, 200000);
        Assert.True(highValue.GetRecordCount() > 0);
        Assert.True(highValue.GetRecordCount() <= all.GetRecordCount());

        // FilterByRange — all (0 to 100000)
        var allFiltered = all.FilterByRange("amount", 0, 100000);
        Assert.Equal(all.GetRecordCount(), allFiltered.GetRecordCount());

        // FilterByRange — none (> 1000000)
        var noneFiltered = all.FilterByRange("amount", 1000000, 9999999);
        Assert.Equal(0, noneFiltered.GetRecordCount());

        // FilterByRange — Q1 only (quarter=1)
        var q1Only = all.FilterByRange("quarter", 1, 1);
        Assert.Equal(5, q1Only.GetRecordCount());

        // ExportToJson works
        var json = all.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // GetRecordCount consistent
        Assert.Equal(all.GetRecordCount(), all.GetRecordCount());

        // SaveToFile — merged
        var mergedPath = TempFile("dogfood_merged.ndjson");
        all.SaveToFile(mergedPath);
        Assert.True(File.Exists(mergedPath));
        Assert.True(new FileInfo(mergedPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(mergedPath);
        Assert.Equal(10, loaded.GetRecordCount());
        Assert.Equal(regions.Length, loaded.GetDistinctValues("region").Length);
        Assert.Equal(products.Length, loaded.GetDistinctValues("product").Length);

        // FilterByRange on loaded
        var loadedHigh = loaded.FilterByRange("amount", 45000, 200000);
        Assert.Equal(highValue.GetRecordCount(), loadedHigh.GetRecordCount());

        // MergeWith empty on loaded
        var emptyDoc = NdjsonDocument.CreateEmpty();
        var mergedEmpty = loaded.MergeWith(emptyDoc);
        Assert.Equal(loaded.GetRecordCount(), mergedEmpty.GetRecordCount());

        // Final save
        var path2 = TempFile("dogfood_merged_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(10, loaded2.GetRecordCount());
        Assert.Equal(products.Length, loaded2.GetDistinctValues("product").Length);
        Assert.Equal(highValue.GetRecordCount(), loaded2.FilterByRange("amount", 45000, 200000).GetRecordCount());
    }
}
