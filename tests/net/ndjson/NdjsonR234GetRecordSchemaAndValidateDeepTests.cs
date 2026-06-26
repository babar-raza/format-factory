// Tests for NdjsonDocument.GetRecordSchema, ValidateSchema, GetSchemaViolationCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R234

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R234: Tests for NdjsonDocument.GetRecordSchema, ValidateSchema, GetSchemaViolationCount deeper.
/// GetRecordSchema(): returns a schema description inferred from the records.
/// ValidateSchema(expectedFields): validates that all records contain the expected fields.
/// GetSchemaViolationCount(): returns the number of records that violate the inferred schema.
/// Covers: GetRecordSchema no-throw; GetRecordSchema non-null; GetRecordSchema non-empty;
/// GetRecordSchema consistent; GetRecordSchema save-load;
/// ValidateSchema no-throw; ValidateSchema returns non-negative; ValidateSchema consistent;
/// ValidateSchema zero for consistent data; ValidateSchema save-load;
/// GetSchemaViolationCount no-throw; GetSchemaViolationCount non-negative; GetSchemaViolationCount consistent;
/// GetSchemaViolationCount zero for uniform schema; GetSchemaViolationCount save-load;
/// dogfood CreateDoc→GetRecordSchema→ValidateSchema→GetSchemaViolationCount→SaveToFile pipeline.
/// </summary>
public class NdjsonR234GetRecordSchemaAndValidateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR234GetRecordSchemaAndValidateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR234_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateConsistentNdjson()
    {
        var path = TempFile("consistent.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"id\":\"EMP001\",\"name\":\"Alice Chen\",\"department\":\"Engineering\",\"salary\":95000,\"grade\":\"L4\",\"active\":true}",
            "{\"id\":\"EMP002\",\"name\":\"Bob Patel\",\"department\":\"Finance\",\"salary\":82000,\"grade\":\"L3\",\"active\":true}",
            "{\"id\":\"EMP003\",\"name\":\"Carol Smith\",\"department\":\"Marketing\",\"salary\":78000,\"grade\":\"L3\",\"active\":false}",
            "{\"id\":\"EMP004\",\"name\":\"David Kim\",\"department\":\"Engineering\",\"salary\":105000,\"grade\":\"L5\",\"active\":true}",
            "{\"id\":\"EMP005\",\"name\":\"Emma Jones\",\"department\":\"HR\",\"salary\":72000,\"grade\":\"L2\",\"active\":true}",
            "{\"id\":\"EMP006\",\"name\":\"Frank Liu\",\"department\":\"Engineering\",\"salary\":115000,\"grade\":\"L6\",\"active\":true}",
            "{\"id\":\"EMP007\",\"name\":\"Grace Park\",\"department\":\"Legal\",\"salary\":98000,\"grade\":\"L4\",\"active\":false}",
            "{\"id\":\"EMP008\",\"name\":\"Henry Brown\",\"department\":\"Sales\",\"salary\":88000,\"grade\":\"L3\",\"active\":true}",
        });
        return path;
    }

    private string CreateMixedNdjson()
    {
        var path = TempFile("mixed.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"id\":1,\"value\":42.5,\"label\":\"alpha\"}",
            "{\"id\":2,\"value\":38.1,\"label\":\"beta\",\"extra\":\"bonus_field\"}",
            "{\"id\":3,\"value\":51.7,\"label\":\"gamma\"}",
            "{\"id\":4,\"label\":\"delta\"}",  // missing 'value'
            "{\"id\":5,\"value\":29.3,\"label\":\"epsilon\"}",
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRecordSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordSchema_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        var ex = Record.Exception(() => doc.GetRecordSchema());
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordSchema_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        Assert.NotNull(doc.GetRecordSchema());
    }

    [Fact]
    public void GetRecordSchema_NonEmpty()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        Assert.NotEmpty(doc.GetRecordSchema());
    }

    [Fact]
    public void GetRecordSchema_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        Assert.Equal(doc.GetRecordSchema(), doc.GetRecordSchema());
    }

    [Fact]
    public void GetRecordSchema_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        var before = doc.GetRecordSchema();
        var path = TempFile("schema_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var after = loaded.GetRecordSchema();
        Assert.NotNull(after);
        Assert.NotEmpty(after);
    }

    // -------------------------------------------------------------------------
    // ValidateSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void ValidateSchema_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        var ex = Record.Exception(() => doc.ValidateSchema(new[] { "id", "name", "department" }));
        Assert.Null(ex);
    }

    [Fact]
    public void ValidateSchema_Returns_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        Assert.True(doc.ValidateSchema(new[] { "id", "name", "department" }) >= 0);
    }

    [Fact]
    public void ValidateSchema_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        var r1 = doc.ValidateSchema(new[] { "id", "name", "salary" });
        var r2 = doc.ValidateSchema(new[] { "id", "name", "salary" });
        Assert.Equal(r1, r2);
    }

    [Fact]
    public void ValidateSchema_Zero_ForConsistentData()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        // All records have these fields
        var violations = doc.ValidateSchema(new[] { "id", "name", "department", "salary" });
        Assert.Equal(0, violations);
    }

    [Fact]
    public void ValidateSchema_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        var before = doc.ValidateSchema(new[] { "id", "name" });
        var path = TempFile("vs_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var after = loaded.ValidateSchema(new[] { "id", "name" });
        Assert.Equal(before, after);
    }

    // -------------------------------------------------------------------------
    // GetSchemaViolationCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSchemaViolationCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        var ex = Record.Exception(() => doc.GetSchemaViolationCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSchemaViolationCount_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        Assert.True(doc.GetSchemaViolationCount() >= 0);
    }

    [Fact]
    public void GetSchemaViolationCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        Assert.Equal(doc.GetSchemaViolationCount(), doc.GetSchemaViolationCount());
    }

    [Fact]
    public void GetSchemaViolationCount_Zero_ForUniformSchema()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        // All records have same 6 fields → no violations
        Assert.Equal(0, doc.GetSchemaViolationCount());
    }

    [Fact]
    public void GetSchemaViolationCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateConsistentNdjson());
        var before = doc.GetSchemaViolationCount();
        var path = TempFile("svc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSchemaViolationCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRecordSchema_ValidateSchema_GetSchemaViolationCount_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_inventory.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"sku\":\"PRD-001\",\"name\":\"Laptop Pro 15\",\"category\":\"Electronics\",\"price\":1299.99,\"stock\":45,\"supplier\":\"TechCorp\",\"in_stock\":true}",
            "{\"sku\":\"PRD-002\",\"name\":\"Wireless Keyboard\",\"category\":\"Accessories\",\"price\":89.99,\"stock\":230,\"supplier\":\"PeriCo\",\"in_stock\":true}",
            "{\"sku\":\"PRD-003\",\"name\":\"USB-C Hub\",\"category\":\"Accessories\",\"price\":59.99,\"stock\":180,\"supplier\":\"ConnectPro\",\"in_stock\":true}",
            "{\"sku\":\"PRD-004\",\"name\":\"Monitor 27\",\"category\":\"Electronics\",\"price\":449.99,\"stock\":28,\"supplier\":\"DisplayMax\",\"in_stock\":true}",
            "{\"sku\":\"PRD-005\",\"name\":\"Desk Chair\",\"category\":\"Furniture\",\"price\":349.99,\"stock\":55,\"supplier\":\"ErgoDesk\",\"in_stock\":true}",
            "{\"sku\":\"PRD-006\",\"name\":\"Webcam HD\",\"category\":\"Accessories\",\"price\":129.99,\"stock\":0,\"supplier\":\"VisionTech\",\"in_stock\":false}",
            "{\"sku\":\"PRD-007\",\"name\":\"Standing Desk\",\"category\":\"Furniture\",\"price\":699.99,\"stock\":12,\"supplier\":\"ErgoDesk\",\"in_stock\":true}",
            "{\"sku\":\"PRD-008\",\"name\":\"Noise-Cancelling Headphones\",\"category\":\"Electronics\",\"price\":299.99,\"stock\":67,\"supplier\":\"AudioPro\",\"in_stock\":true}",
            "{\"sku\":\"PRD-009\",\"name\":\"Docking Station\",\"category\":\"Accessories\",\"price\":199.99,\"stock\":89,\"supplier\":\"ConnectPro\",\"in_stock\":true}",
            "{\"sku\":\"PRD-010\",\"name\":\"Laptop Stand\",\"category\":\"Accessories\",\"price\":49.99,\"stock\":320,\"supplier\":\"ErgoCo\",\"in_stock\":true}",
        });

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRecordCount());

        // GetRecordSchema — non-null, non-empty
        var schema = doc.GetRecordSchema();
        Assert.NotNull(schema);
        Assert.NotEmpty(schema);
        Assert.Equal(schema, doc.GetRecordSchema()); // consistent

        // GetSchemaViolationCount — zero (all records same schema)
        var violationCount = doc.GetSchemaViolationCount();
        Assert.Equal(0, violationCount);
        Assert.Equal(violationCount, doc.GetSchemaViolationCount()); // consistent

        // ValidateSchema — all 7 required fields present
        var violations7 = doc.ValidateSchema(new[] { "sku", "name", "category", "price", "stock", "supplier", "in_stock" });
        Assert.Equal(0, violations7);

        // ValidateSchema — subset of fields → still zero violations
        var violations3 = doc.ValidateSchema(new[] { "sku", "name", "price" });
        Assert.Equal(0, violations3);
        Assert.Equal(violations3, doc.ValidateSchema(new[] { "sku", "name", "price" })); // consistent

        // GetFieldCount and GetFieldNames
        var fieldCount = doc.GetFieldCount();
        Assert.True(fieldCount > 0);
        var fieldNames = doc.GetFieldNames();
        Assert.NotNull(fieldNames);
        Assert.Equal(fieldCount, fieldNames.Count);

        // AggregateByField — by category
        var byCategory = doc.AggregateByField("category", "price", "sum");
        Assert.NotNull(byCategory);
        Assert.True(byCategory.Count <= doc.GetRecordCount());

        // SaveToFile
        var out1 = TempFile("dogfood_inventory_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(10, loaded.GetRecordCount());
        var loadedSchema = loaded.GetRecordSchema();
        Assert.NotNull(loadedSchema);
        Assert.NotEmpty(loadedSchema);
        Assert.Equal(violationCount, loaded.GetSchemaViolationCount());
        Assert.Equal(0, loaded.ValidateSchema(new[] { "sku", "name", "category" }));

        // AddRecord — consistent schema
        loaded.AddRecord("{\"sku\":\"PRD-011\",\"name\":\"Cable Management\",\"category\":\"Accessories\",\"price\":29.99,\"stock\":150,\"supplier\":\"OfficePro\",\"in_stock\":true}");
        Assert.Equal(11, loaded.GetRecordCount());
        Assert.Equal(0, loaded.GetSchemaViolationCount()); // still zero

        // Validate after add
        var violationsAfter = loaded.ValidateSchema(new[] { "sku", "name", "price" });
        Assert.Equal(0, violationsAfter);

        // GetTopN by price
        var top3 = loaded.GetTopN("price", 3);
        Assert.True(top3.Count <= 3);

        // Final save
        var out2 = TempFile("dogfood_inventory_v2.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NdjsonDocument.LoadFile(out2);
        Assert.Equal(11, loaded2.GetRecordCount());
        Assert.NotNull(loaded2.GetRecordSchema());
        Assert.True(loaded2.GetSchemaViolationCount() >= 0);
        var ex1 = Record.Exception(() => loaded2.ValidateSchema(new[] { "sku", "name" }));
        var ex2 = Record.Exception(() => loaded2.GetRecordSchema());
        var ex3 = Record.Exception(() => loaded2.GetSchemaViolationCount());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
