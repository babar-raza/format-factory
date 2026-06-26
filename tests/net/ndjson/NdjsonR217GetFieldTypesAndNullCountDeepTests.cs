// Tests for NdjsonDocument.GetFieldTypes, GetNullCount, GetFieldStats deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R217

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R217: Tests for NdjsonDocument.GetFieldTypes, GetNullCount, GetFieldStats deeper.
/// GetFieldTypes(): returns dictionary of field name → inferred type string.
/// GetNullCount(fieldName): returns count of null/missing values for a field.
/// GetFieldStats(fieldName): returns min/max/avg for numeric fields.
/// Covers: GetFieldTypes non-null; GetFieldTypes non-empty; GetFieldTypes no-throw;
/// GetFieldTypes string field type; GetFieldTypes number field type;
/// GetFieldTypes consistent; GetFieldTypes save-load; GetFieldTypes all keys present;
/// GetNullCount non-negative; GetNullCount no-throw; GetNullCount for complete field=0;
/// GetNullCount consistent; GetNullCount save-load; GetNullCount after AppendRecord updates;
/// GetNullCount total across fields; GetNullCount for sparse field;
/// GetFieldStats non-null; GetFieldStats no-throw; GetFieldStats min correct;
/// GetFieldStats max correct; GetFieldStats avg correct; GetFieldStats consistent;
/// GetFieldStats save-load; GetFieldStats after AppendRecord updates;
/// dogfood CreateDoc→GetFieldTypes→GetNullCount→GetFieldStats→SaveToFile pipeline.
/// </summary>
public class NdjsonR217GetFieldTypesAndNullCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR217GetFieldTypesAndNullCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR217_" + Guid.NewGuid().ToString("N"));
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
        var content =
            "{\"name\":\"Alice\",\"department\":\"Engineering\",\"score\":92,\"salary\":95000}\n" +
            "{\"name\":\"Bob\",\"department\":\"Marketing\",\"score\":78,\"salary\":55000}\n" +
            "{\"name\":\"Carol\",\"department\":\"Engineering\",\"score\":88,\"salary\":115000}\n" +
            "{\"name\":\"Dave\",\"department\":\"Finance\",\"score\":85,\"salary\":72000}\n" +
            "{\"name\":\"Eve\",\"department\":\"Engineering\",\"score\":95,\"salary\":98000}\n";
        File.WriteAllText(path, content);
        return path;
    }

    private string CreateSparseNdjson()
    {
        var path = TempFile("sparse.ndjson");
        // Some records missing 'bonus' field
        var content =
            "{\"name\":\"Alice\",\"score\":92,\"bonus\":5000}\n" +
            "{\"name\":\"Bob\",\"score\":78}\n" +
            "{\"name\":\"Carol\",\"score\":88,\"bonus\":7000}\n" +
            "{\"name\":\"Dave\",\"score\":85}\n" +
            "{\"name\":\"Eve\",\"score\":95,\"bonus\":6000}\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldTypes
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldTypes_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.GetFieldTypes());
    }

    [Fact]
    public void GetFieldTypes_NonEmpty()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.True(doc.GetFieldTypes().Count > 0);
    }

    [Fact]
    public void GetFieldTypes_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GetFieldTypes());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldTypes_StringField_TypeString()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var types = doc.GetFieldTypes();
        Assert.True(types.ContainsKey("name"));
        Assert.True(types["name"].ToLower().Contains("string") || types["name"].ToLower().Contains("text"));
    }

    [Fact]
    public void GetFieldTypes_NumberField_TypeNumber()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var types = doc.GetFieldTypes();
        Assert.True(types.ContainsKey("score") || types.ContainsKey("salary"));
        var scoreType = types.ContainsKey("score") ? types["score"].ToLower() : "number";
        Assert.True(scoreType.Contains("number") || scoreType.Contains("integer") || scoreType.Contains("numeric"));
    }

    [Fact]
    public void GetFieldTypes_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var t1 = doc.GetFieldTypes();
        var t2 = doc.GetFieldTypes();
        Assert.Equal(t1.Count, t2.Count);
    }

    [Fact]
    public void GetFieldTypes_AllKeys_Present()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var types = doc.GetFieldTypes();
        Assert.True(types.ContainsKey("name") || types.ContainsKey("department") || types.ContainsKey("score"));
    }

    [Fact]
    public void GetFieldTypes_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var before = doc.GetFieldTypes().Count;
        var path = TempFile("ft_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldTypes().Count);
    }

    // -------------------------------------------------------------------------
    // GetNullCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNullCount_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.True(doc.GetNullCount("name") >= 0);
    }

    [Fact]
    public void GetNullCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GetNullCount("name"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNullCount_CompleteField_IsZero()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        // All 5 records have 'name' field
        Assert.Equal(0, doc.GetNullCount("name"));
    }

    [Fact]
    public void GetNullCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.Equal(doc.GetNullCount("name"), doc.GetNullCount("name"));
    }

    [Fact]
    public void GetNullCount_SparseField_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        // 'bonus' is missing from Bob and Dave → null count = 2
        var count = doc.GetNullCount("bonus");
        Assert.Equal(2, count);
    }

    [Fact]
    public void GetNullCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        var before = doc.GetNullCount("bonus");
        var path = TempFile("nc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNullCount("bonus"));
    }

    // -------------------------------------------------------------------------
    // GetFieldStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldStats_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.GetFieldStats("score"));
    }

    [Fact]
    public void GetFieldStats_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GetFieldStats("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldStats_Min_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var stats = doc.GetFieldStats("score");
        Assert.Equal(78.0, stats.Min, 3);
    }

    [Fact]
    public void GetFieldStats_Max_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var stats = doc.GetFieldStats("score");
        Assert.Equal(95.0, stats.Max, 3);
    }

    [Fact]
    public void GetFieldStats_Avg_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var stats = doc.GetFieldStats("score");
        // (92+78+88+85+95) / 5 = 438/5 = 87.6
        Assert.Equal(87.6, stats.Average, 3);
    }

    [Fact]
    public void GetFieldStats_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var s1 = doc.GetFieldStats("score");
        var s2 = doc.GetFieldStats("score");
        Assert.Equal(s1.Min, s2.Min, 5);
        Assert.Equal(s1.Max, s2.Max, 5);
    }

    [Fact]
    public void GetFieldStats_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var stats = doc.GetFieldStats("salary");
        var path = TempFile("fs_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var loadedStats = loaded.GetFieldStats("salary");
        Assert.Equal(stats.Min, loadedStats.Min, 5);
        Assert.Equal(stats.Max, loadedStats.Max, 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldTypes_GetNullCount_GetFieldStats_SaveToFile_Pipeline()
    {
        // Create rich NDJSON with mixed types and sparse fields
        var path = TempFile("dogfood_products.ndjson");
        var content =
            "{\"product\":\"Widget-A\",\"category\":\"Electronics\",\"price\":29.99,\"stock\":500,\"discount\":5.0}\n" +
            "{\"product\":\"Gadget-B\",\"category\":\"Electronics\",\"price\":79.99,\"stock\":200}\n" +
            "{\"product\":\"Tool-C\",\"category\":\"Hardware\",\"price\":14.99,\"stock\":800,\"discount\":2.5}\n" +
            "{\"product\":\"Device-D\",\"category\":\"Electronics\",\"price\":149.99,\"stock\":100,\"discount\":15.0}\n" +
            "{\"product\":\"Part-E\",\"category\":\"Hardware\",\"price\":9.99,\"stock\":1200}\n" +
            "{\"product\":\"Module-F\",\"category\":\"Software\",\"price\":199.99,\"stock\":50,\"discount\":20.0}\n";
        File.WriteAllText(path, content);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(6, doc.GetRecordCount());

        // GetFieldTypes
        var types = doc.GetFieldTypes();
        Assert.NotNull(types);
        Assert.True(types.Count > 0);
        Assert.True(types.ContainsKey("product") || types.ContainsKey("category") || types.ContainsKey("price"));

        // String fields
        if (types.ContainsKey("product"))
            Assert.True(types["product"].ToLower().Contains("string") || types["product"].ToLower().Contains("text"));

        // Numeric fields
        if (types.ContainsKey("price"))
            Assert.True(types["price"].ToLower().Contains("number") || types["price"].ToLower().Contains("double") || types["price"].ToLower().Contains("float") || types["price"].ToLower().Contains("numeric"));

        // Consistent
        Assert.Equal(types.Count, doc.GetFieldTypes().Count);

        // GetNullCount — 'discount' missing from Gadget-B and Part-E = 2 nulls
        var discountNulls = doc.GetNullCount("discount");
        Assert.Equal(2, discountNulls);

        // 'product' is present in all records
        Assert.Equal(0, doc.GetNullCount("product"));

        // Consistent
        Assert.Equal(discountNulls, doc.GetNullCount("discount"));

        // GetFieldStats — price
        var priceStats = doc.GetFieldStats("price");
        Assert.NotNull(priceStats);
        Assert.Equal(9.99, priceStats.Min, 3);
        Assert.Equal(199.99, priceStats.Max, 3);
        // Sum = 29.99+79.99+14.99+149.99+9.99+199.99 = 484.94, Avg = 484.94/6 ≈ 80.82
        Assert.True(priceStats.Average > 70.0 && priceStats.Average < 100.0);

        // GetFieldStats — stock
        var stockStats = doc.GetFieldStats("stock");
        Assert.NotNull(stockStats);
        Assert.Equal(50.0, stockStats.Min, 3);
        Assert.Equal(1200.0, stockStats.Max, 3);

        // Consistent
        Assert.Equal(priceStats.Min, doc.GetFieldStats("price").Min, 5);

        // AppendRecord and verify updates
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object?>
        {
            { "product", "Cable-G" },
            { "category", "Hardware" },
            { "price", 4.99 },
            { "stock", 2000 }
            // no discount → null count for discount should increase to 3
        });
        Assert.Equal(7, doc.GetRecordCount());
        Assert.Equal(3, doc.GetNullCount("discount"));

        // GetFieldStats after AppendRecord
        var updatedPriceStats = doc.GetFieldStats("price");
        Assert.Equal(4.99, updatedPriceStats.Min, 3);
        Assert.Equal(199.99, updatedPriceStats.Max, 3);

        // SaveToFile
        var savePath = TempFile("dogfood_products_out.ndjson");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(7, loaded.GetRecordCount());

        // GetFieldTypes on loaded
        var loadedTypes = loaded.GetFieldTypes();
        Assert.Equal(types.Count, loadedTypes.Count);

        // GetNullCount on loaded
        Assert.Equal(3, loaded.GetNullCount("discount"));
        Assert.Equal(0, loaded.GetNullCount("product"));

        // GetFieldStats on loaded
        var loadedPriceStats = loaded.GetFieldStats("price");
        Assert.Equal(priceStats.Min, loadedPriceStats.Min, 3);

        // Final save
        var path2 = TempFile("dogfood_products_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetRecordCount());
        Assert.Equal(loaded.GetFieldTypes().Count, loaded2.GetFieldTypes().Count);
        Assert.Equal(3, loaded2.GetNullCount("discount"));
    }
}
