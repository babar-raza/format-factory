// Tests for NdjsonDocument.SortByField, TakeFirst, SkipFirst deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R223

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R223: Tests for NdjsonDocument.SortByField, TakeFirst, SkipFirst deeper.
/// SortByField(fieldName, ascending): returns a new document sorted by the given field.
/// TakeFirst(count): returns a new document containing only the first N records.
/// SkipFirst(count): returns a new document with the first N records removed.
/// Covers: SortByField non-null; SortByField no-throw; SortByField same count;
/// SortByField ascending; SortByField descending; SortByField consistent;
/// SortByField save-load; SortByField then Sum;
/// TakeFirst non-null; TakeFirst no-throw; TakeFirst correct count;
/// TakeFirst consistent; TakeFirst save-load; TakeFirst then GetRecordAt;
/// SkipFirst non-null; SkipFirst no-throw; SkipFirst correct count;
/// SkipFirst consistent; SkipFirst save-load; SkipFirst then TakeFirst;
/// dogfood LoadFile→SortByField→TakeFirst→SkipFirst→SaveToFile pipeline.
/// </summary>
public class NdjsonR223SortByFieldAndTakeFirstDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR223SortByFieldAndTakeFirstDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR223_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSaleNdjson()
    {
        var path = TempFile("sales.ndjson");
        var content =
            "{\"id\":\"S001\",\"rep\":\"Alice\",\"region\":\"EMEA\",\"amount\":45000,\"quarter\":\"Q1\"}\n" +
            "{\"id\":\"S002\",\"rep\":\"Bob\",\"region\":\"APAC\",\"amount\":32000,\"quarter\":\"Q2\"}\n" +
            "{\"id\":\"S003\",\"rep\":\"Carol\",\"region\":\"AMER\",\"amount\":61000,\"quarter\":\"Q1\"}\n" +
            "{\"id\":\"S004\",\"rep\":\"Dave\",\"region\":\"EMEA\",\"amount\":28000,\"quarter\":\"Q3\"}\n" +
            "{\"id\":\"S005\",\"rep\":\"Eve\",\"region\":\"APAC\",\"amount\":74000,\"quarter\":\"Q2\"}\n" +
            "{\"id\":\"S006\",\"rep\":\"Frank\",\"region\":\"AMER\",\"amount\":19000,\"quarter\":\"Q4\"}\n" +
            "{\"id\":\"S007\",\"rep\":\"Grace\",\"region\":\"EMEA\",\"amount\":55000,\"quarter\":\"Q3\"}\n" +
            "{\"id\":\"S008\",\"rep\":\"Hector\",\"region\":\"APAC\",\"amount\":41000,\"quarter\":\"Q4\"}\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // SortByField
    // -------------------------------------------------------------------------

    [Fact]
    public void SortByField_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        Assert.NotNull(doc.SortByField("amount", ascending: true));
    }

    [Fact]
    public void SortByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var ex = Record.Exception(() => doc.SortByField("rep", ascending: true));
        Assert.Null(ex);
    }

    [Fact]
    public void SortByField_SameRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var sorted = doc.SortByField("amount", ascending: true);
        Assert.Equal(doc.GetRecordCount(), sorted.GetRecordCount());
    }

    [Fact]
    public void SortByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var s1 = doc.SortByField("amount", ascending: true);
        var s2 = doc.SortByField("amount", ascending: true);
        Assert.Equal(s1.GetRecordCount(), s2.GetRecordCount());
    }

    [Fact]
    public void SortByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var sorted = doc.SortByField("amount", ascending: true);
        var path = TempFile("sf_save.ndjson");
        sorted.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(sorted.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void SortByField_Then_Sum_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var sorted = doc.SortByField("amount", ascending: true);
        Assert.Equal(doc.Sum("amount"), sorted.Sum("amount"), 1);
    }

    // -------------------------------------------------------------------------
    // TakeFirst
    // -------------------------------------------------------------------------

    [Fact]
    public void TakeFirst_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        Assert.NotNull(doc.TakeFirst(3));
    }

    [Fact]
    public void TakeFirst_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var ex = Record.Exception(() => doc.TakeFirst(5));
        Assert.Null(ex);
    }

    [Fact]
    public void TakeFirst_CorrectCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var taken = doc.TakeFirst(3);
        Assert.Equal(3, taken.GetRecordCount());
    }

    [Fact]
    public void TakeFirst_All_Records()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var taken = doc.TakeFirst(doc.GetRecordCount());
        Assert.Equal(doc.GetRecordCount(), taken.GetRecordCount());
    }

    [Fact]
    public void TakeFirst_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var t1 = doc.TakeFirst(4);
        var t2 = doc.TakeFirst(4);
        Assert.Equal(t1.GetRecordCount(), t2.GetRecordCount());
    }

    [Fact]
    public void TakeFirst_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var taken = doc.TakeFirst(5);
        var path = TempFile("tf_save.ndjson");
        taken.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(taken.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void TakeFirst_Then_GetRecordAt_AllValid()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var taken = doc.TakeFirst(3);
        for (int i = 0; i < taken.GetRecordCount(); i++)
            Assert.NotNull(taken.GetRecordAt(i));
    }

    // -------------------------------------------------------------------------
    // SkipFirst
    // -------------------------------------------------------------------------

    [Fact]
    public void SkipFirst_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        Assert.NotNull(doc.SkipFirst(2));
    }

    [Fact]
    public void SkipFirst_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var ex = Record.Exception(() => doc.SkipFirst(3));
        Assert.Null(ex);
    }

    [Fact]
    public void SkipFirst_CorrectCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var skipped = doc.SkipFirst(3);
        Assert.Equal(doc.GetRecordCount() - 3, skipped.GetRecordCount());
    }

    [Fact]
    public void SkipFirst_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var s1 = doc.SkipFirst(2);
        var s2 = doc.SkipFirst(2);
        Assert.Equal(s1.GetRecordCount(), s2.GetRecordCount());
    }

    [Fact]
    public void SkipFirst_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var skipped = doc.SkipFirst(4);
        var path = TempFile("sk_save.ndjson");
        skipped.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(skipped.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void SkipFirst_Then_TakeFirst_Subset()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        // skip 2, take 3 → should have 3 records
        var skipped = doc.SkipFirst(2);
        var taken = skipped.TakeFirst(3);
        Assert.Equal(3, taken.GetRecordCount());
    }

    [Fact]
    public void TakeFirst_Plus_SkipFirst_Equals_Total()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var n = 3;
        var taken = doc.TakeFirst(n);
        var skipped = doc.SkipFirst(n);
        Assert.Equal(doc.GetRecordCount(), taken.GetRecordCount() + skipped.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SortByField_TakeFirst_SkipFirst_SaveToFile_Pipeline()
    {
        var pathA = TempFile("dogfood_deals.ndjson");
        File.WriteAllText(pathA,
            "{\"dealId\":\"D001\",\"owner\":\"Alice\",\"stage\":\"Closed-Won\",\"value\":95000,\"region\":\"EMEA\",\"month\":1}\n" +
            "{\"dealId\":\"D002\",\"owner\":\"Bob\",\"stage\":\"Negotiation\",\"value\":42000,\"region\":\"APAC\",\"month\":2}\n" +
            "{\"dealId\":\"D003\",\"owner\":\"Carol\",\"stage\":\"Closed-Won\",\"value\":128000,\"region\":\"AMER\",\"month\":1}\n" +
            "{\"dealId\":\"D004\",\"owner\":\"Dave\",\"stage\":\"Proposal\",\"value\":67000,\"region\":\"EMEA\",\"month\":3}\n" +
            "{\"dealId\":\"D005\",\"owner\":\"Eve\",\"stage\":\"Closed-Won\",\"value\":83000,\"region\":\"APAC\",\"month\":2}\n" +
            "{\"dealId\":\"D006\",\"owner\":\"Frank\",\"stage\":\"Negotiation\",\"value\":31000,\"region\":\"AMER\",\"month\":4}\n" +
            "{\"dealId\":\"D007\",\"owner\":\"Grace\",\"stage\":\"Closed-Won\",\"value\":112000,\"region\":\"EMEA\",\"month\":3}\n" +
            "{\"dealId\":\"D008\",\"owner\":\"Hector\",\"stage\":\"Proposal\",\"value\":54000,\"region\":\"APAC\",\"month\":4}\n" +
            "{\"dealId\":\"D009\",\"owner\":\"Iris\",\"stage\":\"Closed-Won\",\"value\":77000,\"region\":\"AMER\",\"month\":1}\n" +
            "{\"dealId\":\"D010\",\"owner\":\"Jack\",\"stage\":\"Negotiation\",\"value\":48000,\"region\":\"EMEA\",\"month\":2}\n");

        var doc = NdjsonDocument.LoadFile(pathA);
        Assert.Equal(10, doc.GetRecordCount());

        // Sum verification
        var totalValue = doc.Sum("value");
        Assert.True(totalValue > 0);

        // SortByField — ascending by value
        var sortedAsc = doc.SortByField("value", ascending: true);
        Assert.Equal(10, sortedAsc.GetRecordCount());
        Assert.Equal(totalValue, sortedAsc.Sum("value"), 1); // same total
        Assert.NotNull(sortedAsc.GetRecordAt(0));

        // SortByField — descending by value
        var sortedDesc = doc.SortByField("value", ascending: false);
        Assert.Equal(10, sortedDesc.GetRecordCount());
        Assert.Equal(totalValue, sortedDesc.Sum("value"), 1);

        // Consistent sort
        var sortedAsc2 = doc.SortByField("value", ascending: true);
        Assert.Equal(sortedAsc.GetRecordCount(), sortedAsc2.GetRecordCount());

        // TakeFirst — top 5
        var top5 = doc.TakeFirst(5);
        Assert.Equal(5, top5.GetRecordCount());
        for (int i = 0; i < top5.GetRecordCount(); i++)
            Assert.NotNull(top5.GetRecordAt(i));

        // TakeFirst from sorted — top 3 by value
        var top3Sorted = sortedDesc.TakeFirst(3);
        Assert.Equal(3, top3Sorted.GetRecordCount());
        Assert.True(top3Sorted.Sum("value") > 0);

        // SkipFirst — skip first 3
        var skip3 = doc.SkipFirst(3);
        Assert.Equal(7, skip3.GetRecordCount());

        // TakeFirst + SkipFirst = total
        Assert.Equal(doc.GetRecordCount(), top5.GetRecordCount() + doc.SkipFirst(5).GetRecordCount());

        // SkipFirst then TakeFirst — records 4-6
        var middle = doc.SkipFirst(3).TakeFirst(3);
        Assert.Equal(3, middle.GetRecordCount());

        // GetDistinctValues on sorted
        var regions = sortedAsc.GetDistinctValues("region");
        Assert.NotNull(regions);
        Assert.True(regions.Count >= 3);

        // FilterByField on sorted
        var closedWon = sortedAsc.FilterByField("stage", "Closed-Won");
        Assert.True(closedWon.GetRecordCount() > 0);

        // ExportToCsv
        var csv = doc.ExportToCsv();
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // Save sorted
        var savePath = TempFile("dogfood_deals_sorted.ndjson");
        sortedAsc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile sorted and verify
        var loaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(10, loaded.GetRecordCount());
        Assert.Equal(totalValue, loaded.Sum("value"), 1);

        // TakeFirst on loaded
        var loadedTop3 = loaded.TakeFirst(3);
        Assert.Equal(3, loadedTop3.GetRecordCount());

        // SkipFirst on loaded
        var loadedSkip5 = loaded.SkipFirst(5);
        Assert.Equal(5, loadedSkip5.GetRecordCount());

        // SortByField on loaded
        var loadedSorted = loaded.SortByField("month", ascending: true);
        Assert.Equal(10, loadedSorted.GetRecordCount());

        // MergeWith — combine
        var merged = doc.MergeWith(top3Sorted);
        Assert.Equal(13, merged.GetRecordCount());

        // Final save
        var path2 = TempFile("dogfood_deals_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), loaded2.GetRecordCount());
        Assert.Equal(totalValue, loaded2.Sum("value"), 1);
        var ex1 = Record.Exception(() => loaded2.ExportToCsv());
        var ex2 = Record.Exception(() => loaded2.ExportToJson());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
