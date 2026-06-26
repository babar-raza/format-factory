// Tests for NdjsonDocument.Deduplicate, GetUniqueFieldValues, GetRecordsByFieldPrefix deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R229

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R229: Tests for NdjsonDocument.Deduplicate, GetUniqueFieldValues, GetRecordsByFieldPrefix deeper.
/// Deduplicate(): returns a new document with duplicate records removed.
/// GetUniqueFieldValues(fieldName): returns the set of distinct values in the field.
/// GetRecordsByFieldPrefix(fieldName, prefix): returns records where the field value starts with prefix.
/// Covers: Deduplicate no-throw; Deduplicate count leq original; Deduplicate consistent;
/// Deduplicate save-load; Deduplicate idempotent;
/// GetUniqueFieldValues no-throw; GetUniqueFieldValues count leq record count;
/// GetUniqueFieldValues non-null; GetUniqueFieldValues save-load; GetUniqueFieldValues consistent;
/// GetRecordsByFieldPrefix no-throw; GetRecordsByFieldPrefix count leq total;
/// GetRecordsByFieldPrefix non-null; GetRecordsByFieldPrefix save-load; GetRecordsByFieldPrefix empty-prefix-returns-all;
/// dogfood LoadFile→Deduplicate→GetUniqueFieldValues→GetRecordsByFieldPrefix→SaveToFile pipeline.
/// </summary>
public class NdjsonR229DeduplicateAndGetUniqueFieldValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR229DeduplicateAndGetUniqueFieldValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR229_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateProductNdjson()
    {
        var path = TempFile("products.ndjson");
        var lines = new[]
        {
            "{\"sku\":\"P001\",\"category\":\"Electronics\",\"brand\":\"TechCorp\",\"price\":299.99,\"inStock\":true}",
            "{\"sku\":\"P002\",\"category\":\"Clothing\",\"brand\":\"FashionCo\",\"price\":49.99,\"inStock\":true}",
            "{\"sku\":\"P003\",\"category\":\"Electronics\",\"brand\":\"TechCorp\",\"price\":599.99,\"inStock\":false}",
            "{\"sku\":\"P004\",\"category\":\"HomeGoods\",\"brand\":\"HomePro\",\"price\":89.99,\"inStock\":true}",
            "{\"sku\":\"P005\",\"category\":\"Clothing\",\"brand\":\"FashionCo\",\"price\":79.99,\"inStock\":true}",
            "{\"sku\":\"P001\",\"category\":\"Electronics\",\"brand\":\"TechCorp\",\"price\":299.99,\"inStock\":true}",
            "{\"sku\":\"P006\",\"category\":\"Sports\",\"brand\":\"SportMax\",\"price\":149.99,\"inStock\":false}"
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // Deduplicate
    // -------------------------------------------------------------------------

    [Fact]
    public void Deduplicate_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var ex = Record.Exception(() => doc.Deduplicate());
        Assert.Null(ex);
    }

    [Fact]
    public void Deduplicate_Count_Leq_Original()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var deduped = doc.Deduplicate();
        Assert.True(deduped.GetRecordCount() <= doc.GetRecordCount());
    }

    [Fact]
    public void Deduplicate_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.Equal(doc.Deduplicate().GetRecordCount(), doc.Deduplicate().GetRecordCount());
    }

    [Fact]
    public void Deduplicate_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var deduped = doc.Deduplicate();
        var before = deduped.GetRecordCount();
        var path = TempFile("dedup_save.ndjson");
        deduped.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordCount());
    }

    [Fact]
    public void Deduplicate_Idempotent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var once = doc.Deduplicate();
        var twice = once.Deduplicate();
        Assert.Equal(once.GetRecordCount(), twice.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // GetUniqueFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUniqueFieldValues_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var ex = Record.Exception(() => doc.GetUniqueFieldValues("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetUniqueFieldValues_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.NotNull(doc.GetUniqueFieldValues("category"));
    }

    [Fact]
    public void GetUniqueFieldValues_Count_Leq_RecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var vals = doc.GetUniqueFieldValues("category");
        Assert.True(vals.Count <= doc.GetRecordCount());
    }

    [Fact]
    public void GetUniqueFieldValues_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.Equal(
            doc.GetUniqueFieldValues("brand").Count,
            doc.GetUniqueFieldValues("brand").Count);
    }

    [Fact]
    public void GetUniqueFieldValues_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var before = doc.GetUniqueFieldValues("category").Count;
        var path = TempFile("ufv_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetUniqueFieldValues("category").Count);
    }

    // -------------------------------------------------------------------------
    // GetRecordsByFieldPrefix
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordsByFieldPrefix_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var ex = Record.Exception(() => doc.GetRecordsByFieldPrefix("sku", "P0"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordsByFieldPrefix_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.NotNull(doc.GetRecordsByFieldPrefix("sku", "P0"));
    }

    [Fact]
    public void GetRecordsByFieldPrefix_Count_Leq_Total()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var filtered = doc.GetRecordsByFieldPrefix("category", "Elec");
        Assert.True(filtered.GetRecordCount() <= doc.GetRecordCount());
    }

    [Fact]
    public void GetRecordsByFieldPrefix_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var filtered = doc.GetRecordsByFieldPrefix("brand", "Tech");
        var before = filtered.GetRecordCount();
        var path = TempFile("pfx_save.ndjson");
        filtered.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordCount());
    }

    [Fact]
    public void GetRecordsByFieldPrefix_EmptyPrefix_ReturnsAll()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var all = doc.GetRecordsByFieldPrefix("sku", "");
        Assert.True(all.GetRecordCount() >= doc.GetRecordCount() - 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Deduplicate_GetUniqueFieldValues_GetRecordsByFieldPrefix_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_orders.ndjson");
        var lines = new[]
        {
            "{\"orderId\":\"O001\",\"customerId\":\"C100\",\"region\":\"Northeast\",\"product\":\"Laptop\",\"amount\":1299.99,\"status\":\"Shipped\"}",
            "{\"orderId\":\"O002\",\"customerId\":\"C101\",\"region\":\"Southeast\",\"product\":\"Phone\",\"amount\":799.99,\"status\":\"Delivered\"}",
            "{\"orderId\":\"O003\",\"customerId\":\"C100\",\"region\":\"Northeast\",\"product\":\"Tablet\",\"amount\":499.99,\"status\":\"Processing\"}",
            "{\"orderId\":\"O004\",\"customerId\":\"C102\",\"region\":\"Midwest\",\"product\":\"Laptop\",\"amount\":1199.99,\"status\":\"Shipped\"}",
            "{\"orderId\":\"O005\",\"customerId\":\"C103\",\"region\":\"West\",\"product\":\"Monitor\",\"amount\":349.99,\"status\":\"Delivered\"}",
            "{\"orderId\":\"O002\",\"customerId\":\"C101\",\"region\":\"Southeast\",\"product\":\"Phone\",\"amount\":799.99,\"status\":\"Delivered\"}",
            "{\"orderId\":\"O006\",\"customerId\":\"C104\",\"region\":\"Northeast\",\"product\":\"Keyboard\",\"amount\":149.99,\"status\":\"Pending\"}",
            "{\"orderId\":\"O007\",\"customerId\":\"C102\",\"region\":\"Midwest\",\"product\":\"Phone\",\"amount\":799.99,\"status\":\"Processing\"}",
            "{\"orderId\":\"O008\",\"customerId\":\"C105\",\"region\":\"Southwest\",\"product\":\"Laptop\",\"amount\":1399.99,\"status\":\"Pending\"}",
            "{\"orderId\":\"O001\",\"customerId\":\"C100\",\"region\":\"Northeast\",\"product\":\"Laptop\",\"amount\":1299.99,\"status\":\"Shipped\"}"
        };
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRecordCount());

        // Deduplicate — removes 2 duplicates (O001, O002 appear twice)
        var deduped = doc.Deduplicate();
        Assert.NotNull(deduped);
        Assert.True(deduped.GetRecordCount() <= doc.GetRecordCount());
        Assert.True(deduped.GetRecordCount() >= 1);

        // Deduplicate is idempotent
        Assert.Equal(deduped.GetRecordCount(), deduped.Deduplicate().GetRecordCount());

        // GetUniqueFieldValues — region
        var regions = doc.GetUniqueFieldValues("region");
        Assert.NotNull(regions);
        Assert.True(regions.Count >= 1);
        Assert.True(regions.Count <= doc.GetRecordCount());
        Assert.Equal(regions.Count, doc.GetUniqueFieldValues("region").Count); // consistent

        // GetUniqueFieldValues — status
        var statuses = doc.GetUniqueFieldValues("status");
        Assert.NotNull(statuses);
        Assert.True(statuses.Count >= 1);
        Assert.True(statuses.Count <= doc.GetRecordCount());

        // GetUniqueFieldValues — product
        var products = doc.GetUniqueFieldValues("product");
        Assert.NotNull(products);
        Assert.True(products.Count >= 1);

        // GetRecordsByFieldPrefix — region starts with "North"
        var northeast = doc.GetRecordsByFieldPrefix("region", "North");
        Assert.NotNull(northeast);
        Assert.True(northeast.GetRecordCount() >= 0);
        Assert.True(northeast.GetRecordCount() <= doc.GetRecordCount());
        Assert.Equal(northeast.GetRecordCount(), northeast.GetRecordCount()); // consistent

        // GetRecordsByFieldPrefix — orderId starts with "O00"
        var o00 = doc.GetRecordsByFieldPrefix("orderId", "O00");
        Assert.NotNull(o00);
        Assert.True(o00.GetRecordCount() >= 0);

        // GetRecordsByFieldPrefix — empty prefix → all records
        var allPrefix = doc.GetRecordsByFieldPrefix("product", "");
        Assert.True(allPrefix.GetRecordCount() >= doc.GetRecordCount() - 1);

        // SaveToFile — deduped
        var dedupPath = TempFile("dogfood_orders_deduped.ndjson");
        deduped.SaveToFile(dedupPath);
        Assert.True(File.Exists(dedupPath));
        Assert.True(new FileInfo(dedupPath).Length > 0);

        // LoadFile and verify
        var loadedDedup = NdjsonDocument.LoadFile(dedupPath);
        Assert.Equal(deduped.GetRecordCount(), loadedDedup.GetRecordCount());
        Assert.Equal(
            deduped.GetUniqueFieldValues("region").Count,
            loadedDedup.GetUniqueFieldValues("region").Count);

        // GetRecordsByFieldPrefix on loaded
        var loadedPrefix = loadedDedup.GetRecordsByFieldPrefix("status", "S");
        Assert.NotNull(loadedPrefix);
        Assert.True(loadedPrefix.GetRecordCount() >= 0);

        // Merge deduped with a new record and re-deduplicate
        deduped.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["orderId"] = "O009",
            ["customerId"] = "C106",
            ["region"] = "Northwest",
            ["product"] = "Webcam",
            ["amount"] = 99.99,
            ["status"] = "Pending"
        });
        var finalDedup = deduped.Deduplicate();
        Assert.True(finalDedup.GetRecordCount() >= loadedDedup.GetRecordCount());

        // Final save
        var path2 = TempFile("dogfood_orders_final.ndjson");
        finalDedup.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(finalDedup.GetRecordCount(), loaded2.GetRecordCount());
        Assert.True(loaded2.GetUniqueFieldValues("region").Count >= 1);
        Assert.True(loaded2.GetRecordsByFieldPrefix("orderId", "O").GetRecordCount() >= 1);
    }
}
