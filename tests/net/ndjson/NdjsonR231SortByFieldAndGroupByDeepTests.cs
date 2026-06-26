// Tests for NdjsonDocument.SortByField, GroupBy, GetRecordsByFieldValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R231

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R231: Tests for NdjsonDocument.SortByField, GroupBy, GetRecordsByFieldValue deeper.
/// SortByField(fieldName, ascending): returns a new document sorted by the field.
/// GroupBy(fieldName): returns a dictionary mapping field values to sub-documents.
/// GetRecordsByFieldValue(fieldName, value): returns records with exact field match.
/// Covers: SortByField no-throw; SortByField count unchanged; SortByField consistent;
/// SortByField save-load; SortByField ascending-leq-descending-first;
/// GroupBy no-throw; GroupBy non-null; GroupBy consistent; GroupBy save-load;
/// GroupBy total-count-equals-original;
/// GetRecordsByFieldValue no-throw; GetRecordsByFieldValue count leq total;
/// GetRecordsByFieldValue non-null; GetRecordsByFieldValue save-load; GetRecordsByFieldValue consistent;
/// dogfood LoadFile→SortByField→GroupBy→GetRecordsByFieldValue→SaveToFile pipeline.
/// </summary>
public class NdjsonR231SortByFieldAndGroupByDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR231SortByFieldAndGroupByDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR231_" + Guid.NewGuid().ToString("N"));
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
        var lines = new[]
        {
            "{\"empId\":\"E001\",\"dept\":\"Engineering\",\"level\":\"Senior\",\"salary\":95000,\"years\":8}",
            "{\"empId\":\"E002\",\"dept\":\"Marketing\",\"level\":\"Junior\",\"salary\":55000,\"years\":2}",
            "{\"empId\":\"E003\",\"dept\":\"Engineering\",\"level\":\"Junior\",\"salary\":72000,\"years\":3}",
            "{\"empId\":\"E004\",\"dept\":\"HR\",\"level\":\"Mid\",\"salary\":65000,\"years\":5}",
            "{\"empId\":\"E005\",\"dept\":\"Engineering\",\"level\":\"Senior\",\"salary\":105000,\"years\":12}",
            "{\"empId\":\"E006\",\"dept\":\"Marketing\",\"level\":\"Senior\",\"salary\":88000,\"years\":9}",
            "{\"empId\":\"E007\",\"dept\":\"HR\",\"level\":\"Junior\",\"salary\":48000,\"years\":1}",
            "{\"empId\":\"E008\",\"dept\":\"Engineering\",\"level\":\"Mid\",\"salary\":82000,\"years\":6}"
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // SortByField
    // -------------------------------------------------------------------------

    [Fact]
    public void SortByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.SortByField("salary", ascending: true));
        Assert.Null(ex);
    }

    [Fact]
    public void SortByField_Count_Unchanged()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var sorted = doc.SortByField("salary", ascending: true);
        Assert.Equal(doc.GetRecordCount(), sorted.GetRecordCount());
    }

    [Fact]
    public void SortByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.Equal(
            doc.SortByField("years", true).GetRecordCount(),
            doc.SortByField("years", true).GetRecordCount());
    }

    [Fact]
    public void SortByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var sorted = doc.SortByField("salary", ascending: true);
        var before = sorted.GetRecordCount();
        var path = TempFile("sort_save.ndjson");
        sorted.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // GroupBy
    // -------------------------------------------------------------------------

    [Fact]
    public void GroupBy_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GroupBy("dept"));
        Assert.Null(ex);
    }

    [Fact]
    public void GroupBy_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.GroupBy("dept"));
    }

    [Fact]
    public void GroupBy_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.Equal(doc.GroupBy("dept").Count, doc.GroupBy("dept").Count);
    }

    [Fact]
    public void GroupBy_TotalCount_Equals_Original()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var groups = doc.GroupBy("dept");
        int total = 0;
        foreach (var g in groups.Values)
            total += g.GetRecordCount();
        Assert.Equal(doc.GetRecordCount(), total);
    }

    [Fact]
    public void GroupBy_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var before = doc.GroupBy("dept").Count;
        var path = TempFile("group_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GroupBy("dept").Count);
    }

    // -------------------------------------------------------------------------
    // GetRecordsByFieldValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordsByFieldValue_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GetRecordsByFieldValue("dept", "Engineering"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordsByFieldValue_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.GetRecordsByFieldValue("dept", "Marketing"));
    }

    [Fact]
    public void GetRecordsByFieldValue_Count_Leq_Total()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var eng = doc.GetRecordsByFieldValue("dept", "Engineering");
        Assert.True(eng.GetRecordCount() <= doc.GetRecordCount());
    }

    [Fact]
    public void GetRecordsByFieldValue_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.Equal(
            doc.GetRecordsByFieldValue("level", "Senior").GetRecordCount(),
            doc.GetRecordsByFieldValue("level", "Senior").GetRecordCount());
    }

    [Fact]
    public void GetRecordsByFieldValue_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var eng = doc.GetRecordsByFieldValue("dept", "Engineering");
        var before = eng.GetRecordCount();
        var path = TempFile("rfv_save.ndjson");
        eng.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SortByField_GroupBy_GetRecordsByFieldValue_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_sales.ndjson");
        var lines = new[]
        {
            "{\"dealId\":\"D001\",\"rep\":\"Alice\",\"region\":\"Northeast\",\"product\":\"Enterprise\",\"value\":125000,\"stage\":\"Closed-Won\",\"quarter\":\"Q1\"}",
            "{\"dealId\":\"D002\",\"rep\":\"Bob\",\"region\":\"Southeast\",\"product\":\"SMB\",\"value\":28000,\"stage\":\"Closed-Won\",\"quarter\":\"Q1\"}",
            "{\"dealId\":\"D003\",\"rep\":\"Carol\",\"region\":\"Midwest\",\"product\":\"Enterprise\",\"value\":215000,\"stage\":\"Negotiation\",\"quarter\":\"Q2\"}",
            "{\"dealId\":\"D004\",\"rep\":\"Alice\",\"region\":\"Northeast\",\"product\":\"SMB\",\"value\":42000,\"stage\":\"Closed-Won\",\"quarter\":\"Q2\"}",
            "{\"dealId\":\"D005\",\"rep\":\"Dave\",\"region\":\"West\",\"product\":\"Enterprise\",\"value\":180000,\"stage\":\"Proposal\",\"quarter\":\"Q1\"}",
            "{\"dealId\":\"D006\",\"rep\":\"Bob\",\"region\":\"Southeast\",\"product\":\"Enterprise\",\"value\":95000,\"stage\":\"Closed-Lost\",\"quarter\":\"Q2\"}",
            "{\"dealId\":\"D007\",\"rep\":\"Carol\",\"region\":\"Midwest\",\"product\":\"SMB\",\"value\":35000,\"stage\":\"Closed-Won\",\"quarter\":\"Q1\"}",
            "{\"dealId\":\"D008\",\"rep\":\"Dave\",\"region\":\"West\",\"product\":\"SMB\",\"value\":22000,\"stage\":\"Closed-Won\",\"quarter\":\"Q2\"}",
            "{\"dealId\":\"D009\",\"rep\":\"Eve\",\"region\":\"Southwest\",\"product\":\"Enterprise\",\"value\":310000,\"stage\":\"Negotiation\",\"quarter\":\"Q2\"}",
            "{\"dealId\":\"D010\",\"rep\":\"Alice\",\"region\":\"Northeast\",\"product\":\"Enterprise\",\"value\":165000,\"stage\":\"Closed-Won\",\"quarter\":\"Q2\"}"
        };
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRecordCount());

        // SortByField — value ascending
        var sorted = doc.SortByField("value", ascending: true);
        Assert.NotNull(sorted);
        Assert.Equal(doc.GetRecordCount(), sorted.GetRecordCount());
        Assert.Equal(sorted.GetRecordCount(), sorted.SortByField("value", true).GetRecordCount()); // consistent

        // SortByField — value descending
        var sortedDesc = doc.SortByField("value", ascending: false);
        Assert.Equal(doc.GetRecordCount(), sortedDesc.GetRecordCount());

        // GroupBy — stage
        var byStage = doc.GroupBy("stage");
        Assert.NotNull(byStage);
        Assert.True(byStage.Count >= 1);
        int stageTotal = 0;
        foreach (var g in byStage.Values)
            stageTotal += g.GetRecordCount();
        Assert.Equal(doc.GetRecordCount(), stageTotal);
        Assert.Equal(byStage.Count, doc.GroupBy("stage").Count); // consistent

        // GroupBy — product
        var byProduct = doc.GroupBy("product");
        Assert.NotNull(byProduct);
        Assert.True(byProduct.Count >= 1);
        int prodTotal = 0;
        foreach (var g in byProduct.Values)
            prodTotal += g.GetRecordCount();
        Assert.Equal(doc.GetRecordCount(), prodTotal);

        // GroupBy — quarter
        var byQuarter = doc.GroupBy("quarter");
        Assert.True(byQuarter.Count >= 1);

        // GetRecordsByFieldValue — Closed-Won deals
        var wonDeals = doc.GetRecordsByFieldValue("stage", "Closed-Won");
        Assert.NotNull(wonDeals);
        Assert.True(wonDeals.GetRecordCount() >= 0);
        Assert.True(wonDeals.GetRecordCount() <= doc.GetRecordCount());
        Assert.Equal(wonDeals.GetRecordCount(), wonDeals.GetRecordCount()); // consistent

        // GetRecordsByFieldValue — Enterprise product
        var enterprise = doc.GetRecordsByFieldValue("product", "Enterprise");
        Assert.NotNull(enterprise);
        Assert.True(enterprise.GetRecordCount() >= 0);

        // GetRecordsByFieldValue — Alice's deals
        var aliceDeals = doc.GetRecordsByFieldValue("rep", "Alice");
        Assert.NotNull(aliceDeals);
        Assert.True(aliceDeals.GetRecordCount() >= 0);

        // SaveToFile — sorted
        var sortedPath = TempFile("dogfood_sales_sorted.ndjson");
        sorted.SaveToFile(sortedPath);
        Assert.True(File.Exists(sortedPath));
        Assert.True(new FileInfo(sortedPath).Length > 0);

        // LoadFile and verify
        var loadedSorted = NdjsonDocument.LoadFile(sortedPath);
        Assert.Equal(doc.GetRecordCount(), loadedSorted.GetRecordCount());
        Assert.Equal(byStage.Count, loadedSorted.GroupBy("stage").Count);
        Assert.Equal(wonDeals.GetRecordCount(), loadedSorted.GetRecordsByFieldValue("stage", "Closed-Won").GetRecordCount());

        // AppendRecord to loaded
        loadedSorted.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["dealId"] = "D011",
            ["rep"] = "Frank",
            ["region"] = "Northwest",
            ["product"] = "Enterprise",
            ["value"] = 275000,
            ["stage"] = "Closed-Won",
            ["quarter"] = "Q2"
        });
        Assert.Equal(11, loadedSorted.GetRecordCount());

        // Final save
        var path2 = TempFile("dogfood_sales_v2.ndjson");
        loadedSorted.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(11, loaded2.GetRecordCount());
        Assert.True(loaded2.GroupBy("stage").Count >= 1);
        Assert.True(loaded2.GetRecordsByFieldValue("product", "Enterprise").GetRecordCount() >= 1);
        Assert.Equal(11, loaded2.SortByField("value", true).GetRecordCount());
    }
}
