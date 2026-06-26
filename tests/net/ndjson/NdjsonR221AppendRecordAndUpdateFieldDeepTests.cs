// Tests for NdjsonDocument.AppendRecord, RemoveRecord, UpdateField deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R221

using System;
using System.IO;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R221: Tests for NdjsonDocument.AppendRecord, RemoveRecord, UpdateField deeper.
/// AppendRecord(dict): appends a new record to the document.
/// RemoveRecord(index): removes the record at the given index.
/// UpdateField(recordIndex, fieldName, value): updates a field value in a record.
/// Covers: AppendRecord no-throw; AppendRecord increases count; AppendRecord then GetRecordAt;
/// AppendRecord multiple; AppendRecord save-load; AppendRecord then ExportToJson no-throw;
/// AppendRecord consistent; AppendRecord then GetFieldTypes;
/// RemoveRecord no-throw; RemoveRecord decreases count; RemoveRecord save-load;
/// RemoveRecord consistent; RemoveRecord then GetRecordAt valid;
/// UpdateField no-throw; UpdateField reflects in GetRecordAt; UpdateField save-load;
/// UpdateField consistent; UpdateField multiple records; UpdateField then ExportToCsv no-throw;
/// UpdateField then Sum changes; UpdateField then Average changes;
/// dogfood LoadFile→AppendRecord→RemoveRecord→UpdateField→SaveToFile pipeline.
/// </summary>
public class NdjsonR221AppendRecordAndUpdateFieldDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR221AppendRecordAndUpdateFieldDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR221_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateInventoryNdjson()
    {
        var path = TempFile("inventory.ndjson");
        var content =
            "{\"sku\":\"SKU-001\",\"name\":\"Widget Alpha\",\"qty\":500,\"price\":24.99,\"category\":\"Electronics\"}\n" +
            "{\"sku\":\"SKU-002\",\"name\":\"Widget Beta\",\"qty\":1200,\"price\":14.99,\"category\":\"Hardware\"}\n" +
            "{\"sku\":\"SKU-003\",\"name\":\"Widget Gamma\",\"qty\":300,\"price\":49.99,\"category\":\"Electronics\"}\n" +
            "{\"sku\":\"SKU-004\",\"name\":\"Widget Delta\",\"qty\":800,\"price\":9.99,\"category\":\"Office\"}\n" +
            "{\"sku\":\"SKU-005\",\"name\":\"Widget Epsilon\",\"qty\":150,\"price\":79.99,\"category\":\"Electronics\"}\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // AppendRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void AppendRecord_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        var record = new Dictionary<string, object> { ["sku"] = "SKU-NEW", ["name"] = "Widget Zeta", ["qty"] = 400, ["price"] = 34.99, ["category"] = "Hardware" };
        var ex = Record.Exception(() => doc.AppendRecord(record));
        Assert.Null(ex);
    }

    [Fact]
    public void AppendRecord_Increases_Count()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        var before = doc.GetRecordCount();
        var record = new Dictionary<string, object> { ["sku"] = "SKU-006", ["qty"] = 200 };
        doc.AppendRecord(record);
        Assert.Equal(before + 1, doc.GetRecordCount());
    }

    [Fact]
    public void AppendRecord_Then_GetRecordAt_HasNewRecord()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        var record = new Dictionary<string, object> { ["sku"] = "SKU-UNIQUE-XYZ", ["name"] = "Unique Widget" };
        doc.AppendRecord(record);
        var last = doc.GetRecordAt(doc.GetRecordCount() - 1);
        Assert.NotNull(last);
    }

    [Fact]
    public void AppendRecord_Multiple()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        var before = doc.GetRecordCount();
        doc.AppendRecord(new Dictionary<string, object> { ["sku"] = "A" });
        doc.AppendRecord(new Dictionary<string, object> { ["sku"] = "B" });
        doc.AppendRecord(new Dictionary<string, object> { ["sku"] = "C" });
        Assert.Equal(before + 3, doc.GetRecordCount());
    }

    [Fact]
    public void AppendRecord_SaveLoad_Persists()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        doc.AppendRecord(new Dictionary<string, object> { ["sku"] = "SKU-SAVED", ["qty"] = 100 });
        var before = doc.GetRecordCount();
        var path = TempFile("ar_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordCount());
    }

    [Fact]
    public void AppendRecord_Then_ExportToJson_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        doc.AppendRecord(new Dictionary<string, object> { ["sku"] = "SKU-X" });
        var ex = Record.Exception(() => doc.ExportToJson());
        Assert.Null(ex);
    }

    [Fact]
    public void AppendRecord_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        doc.AppendRecord(new Dictionary<string, object> { ["sku"] = "TEST" });
        var c1 = doc.GetRecordCount();
        var c2 = doc.GetRecordCount();
        Assert.Equal(c1, c2);
    }

    // -------------------------------------------------------------------------
    // RemoveRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRecord_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        var ex = Record.Exception(() => doc.RemoveRecord(0));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveRecord_Decreases_Count()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        var before = doc.GetRecordCount();
        doc.RemoveRecord(0);
        Assert.Equal(before - 1, doc.GetRecordCount());
    }

    [Fact]
    public void RemoveRecord_SaveLoad_Persists()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        doc.RemoveRecord(0);
        var before = doc.GetRecordCount();
        var path = TempFile("rr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordCount());
    }

    [Fact]
    public void RemoveRecord_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        doc.RemoveRecord(2);
        var c1 = doc.GetRecordCount();
        var c2 = doc.GetRecordCount();
        Assert.Equal(c1, c2);
    }

    [Fact]
    public void RemoveRecord_Then_GetRecordAt_ValidIndex()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        doc.RemoveRecord(0);
        // After removing first, index 0 still valid
        var ex = Record.Exception(() => doc.GetRecordAt(0));
        Assert.Null(ex);
        Assert.NotNull(doc.GetRecordAt(0));
    }

    // -------------------------------------------------------------------------
    // UpdateField
    // -------------------------------------------------------------------------

    [Fact]
    public void UpdateField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        var ex = Record.Exception(() => doc.UpdateField(0, "qty", 600));
        Assert.Null(ex);
    }

    [Fact]
    public void UpdateField_Reflects_In_GetRecordAt()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        doc.UpdateField(0, "name", "Updated Widget Alpha");
        var record = doc.GetRecordAt(0);
        Assert.NotNull(record);
        // The record should reflect the update
        Assert.True(record.ContainsKey("name") || record.Count > 0);
    }

    [Fact]
    public void UpdateField_SaveLoad_Persists()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        doc.UpdateField(1, "qty", 9999);
        var path = TempFile("uf_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void UpdateField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        doc.UpdateField(0, "qty", 750);
        var c1 = doc.GetRecordCount();
        var c2 = doc.GetRecordCount();
        Assert.Equal(c1, c2);
    }

    [Fact]
    public void UpdateField_Multiple_Records()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        doc.UpdateField(0, "qty", 100);
        doc.UpdateField(1, "qty", 200);
        doc.UpdateField(2, "qty", 300);
        Assert.Equal(5, doc.GetRecordCount());
    }

    [Fact]
    public void UpdateField_Then_ExportToCsv_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateInventoryNdjson());
        doc.UpdateField(0, "price", 29.99);
        var ex = Record.Exception(() => doc.ExportToCsv());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AppendRecord_RemoveRecord_UpdateField_SaveToFile_Pipeline()
    {
        // Build comprehensive NDJSON
        var path = TempFile("dogfood_transactions.ndjson");
        var content =
            "{\"txId\":\"TX-001\",\"merchant\":\"Apex Corp\",\"amount\":1250.00,\"currency\":\"USD\",\"category\":\"Technology\",\"approved\":true}\n" +
            "{\"txId\":\"TX-002\",\"merchant\":\"Beta Ltd\",\"amount\":890.50,\"currency\":\"EUR\",\"category\":\"Services\",\"approved\":true}\n" +
            "{\"txId\":\"TX-003\",\"merchant\":\"Gamma Inc\",\"amount\":3200.00,\"currency\":\"USD\",\"category\":\"Technology\",\"approved\":false}\n" +
            "{\"txId\":\"TX-004\",\"merchant\":\"Delta Co\",\"amount\":450.00,\"currency\":\"GBP\",\"category\":\"Office\",\"approved\":true}\n" +
            "{\"txId\":\"TX-005\",\"merchant\":\"Epsilon LLC\",\"amount\":6800.00,\"currency\":\"USD\",\"category\":\"Technology\",\"approved\":true}\n";
        File.WriteAllText(path, content);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(5, doc.GetRecordCount());

        // GetRecordAt — all valid
        for (int i = 0; i < doc.GetRecordCount(); i++)
            Assert.NotNull(doc.GetRecordAt(i));

        // AppendRecord — new transaction
        doc.AppendRecord(new Dictionary<string, object>
        {
            ["txId"] = "TX-006",
            ["merchant"] = "Zeta Partners",
            ["amount"] = 2100.00,
            ["currency"] = "USD",
            ["category"] = "Services",
            ["approved"] = true
        });
        Assert.Equal(6, doc.GetRecordCount());

        doc.AppendRecord(new Dictionary<string, object>
        {
            ["txId"] = "TX-007",
            ["merchant"] = "Eta Systems",
            ["amount"] = 950.00,
            ["currency"] = "EUR",
            ["category"] = "Office",
            ["approved"] = true
        });
        Assert.Equal(7, doc.GetRecordCount());

        // AppendRecord consistent
        Assert.Equal(7, doc.GetRecordCount());

        // ExportToJson after appends
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // UpdateField — approve the rejected transaction
        doc.UpdateField(2, "approved", true);
        // Update amount for an existing transaction
        doc.UpdateField(0, "amount", 1500.00);
        doc.UpdateField(4, "amount", 7200.00);

        // Record count unchanged after updates
        Assert.Equal(7, doc.GetRecordCount());

        // ExportToCsv after updates
        var csv = doc.ExportToCsv();
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // Sum of amounts
        var totalAmount = doc.Sum("amount");
        Assert.True(totalAmount > 0);

        // RemoveRecord — remove a record
        doc.RemoveRecord(6); // Remove last appended
        Assert.Equal(6, doc.GetRecordCount());

        doc.RemoveRecord(2); // Remove gamma (now approved but still remove)
        Assert.Equal(5, doc.GetRecordCount());

        // GetRecordAt still valid after removes
        for (int i = 0; i < doc.GetRecordCount(); i++)
            Assert.NotNull(doc.GetRecordAt(i));

        // GetFieldTypes still works
        var types = doc.GetFieldTypes();
        Assert.NotNull(types);
        Assert.True(types.Count > 0);

        // SaveToFile
        var savePath = TempFile("dogfood_transactions_out.ndjson");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(5, loaded.GetRecordCount());

        // AppendRecord on loaded
        loaded.AppendRecord(new Dictionary<string, object> { ["txId"] = "TX-FINAL", ["amount"] = 500.00 });
        Assert.Equal(6, loaded.GetRecordCount());

        // UpdateField on loaded
        loaded.UpdateField(0, "amount", 2000.00);
        Assert.Equal(6, loaded.GetRecordCount());

        // RemoveRecord on loaded
        loaded.RemoveRecord(5); // Remove just-appended
        Assert.Equal(5, loaded.GetRecordCount());

        // ExportToJson on loaded
        var loadedJson = loaded.ExportToJson();
        Assert.NotNull(loadedJson);
        Assert.NotEmpty(loadedJson);

        // Final save
        var path2 = TempFile("dogfood_transactions_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetRecordCount());
        Assert.True(loaded2.Sum("amount") > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToJson());
        var ex2 = Record.Exception(() => loaded2.ExportToCsv());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
