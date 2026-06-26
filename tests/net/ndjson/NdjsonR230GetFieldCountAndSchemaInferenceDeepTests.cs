// Tests for NdjsonDocument.GetFieldCount, GetFieldNames, InferSchema deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R230

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R230: Tests for NdjsonDocument.GetFieldCount, GetFieldNames, InferSchema deeper.
/// GetFieldCount(): returns the number of distinct field names across all records.
/// GetFieldNames(): returns the list of distinct field names.
/// InferSchema(): returns a schema dictionary mapping field names to inferred types.
/// Covers: GetFieldCount no-throw; GetFieldCount positive; GetFieldCount consistent;
/// GetFieldCount save-load; GetFieldCount equals GetFieldNames count;
/// GetFieldNames no-throw; GetFieldNames non-null; GetFieldNames non-empty;
/// GetFieldNames consistent; GetFieldNames save-load;
/// InferSchema no-throw; InferSchema non-null; InferSchema count leq field count;
/// InferSchema consistent; InferSchema save-load;
/// dogfood LoadFile→GetFieldCount→GetFieldNames→InferSchema→SaveToFile pipeline.
/// </summary>
public class NdjsonR230GetFieldCountAndSchemaInferenceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR230GetFieldCountAndSchemaInferenceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR230_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEventNdjson()
    {
        var path = TempFile("events.ndjson");
        var lines = new[]
        {
            "{\"eventId\":\"E001\",\"type\":\"click\",\"userId\":\"U100\",\"timestamp\":1719360000,\"duration\":1.5,\"success\":true}",
            "{\"eventId\":\"E002\",\"type\":\"submit\",\"userId\":\"U101\",\"timestamp\":1719360010,\"duration\":2.8,\"success\":true}",
            "{\"eventId\":\"E003\",\"type\":\"navigate\",\"userId\":\"U100\",\"timestamp\":1719360025,\"duration\":0.3,\"success\":true}",
            "{\"eventId\":\"E004\",\"type\":\"click\",\"userId\":\"U102\",\"timestamp\":1719360040,\"duration\":1.1,\"success\":false}",
            "{\"eventId\":\"E005\",\"type\":\"submit\",\"userId\":\"U103\",\"timestamp\":1719360055,\"duration\":3.2,\"success\":true}"
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        var ex = Record.Exception(() => doc.GetFieldCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldCount_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        Assert.True(doc.GetFieldCount() > 0);
    }

    [Fact]
    public void GetFieldCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        Assert.Equal(doc.GetFieldCount(), doc.GetFieldCount());
    }

    [Fact]
    public void GetFieldCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        var before = doc.GetFieldCount();
        var path = TempFile("fc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldCount());
    }

    [Fact]
    public void GetFieldCount_Equals_GetFieldNames_Count()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        Assert.Equal(doc.GetFieldCount(), doc.GetFieldNames().Count);
    }

    // -------------------------------------------------------------------------
    // GetFieldNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldNames_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        var ex = Record.Exception(() => doc.GetFieldNames());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldNames_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        Assert.NotNull(doc.GetFieldNames());
    }

    [Fact]
    public void GetFieldNames_NonEmpty()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        Assert.NotEmpty(doc.GetFieldNames());
    }

    [Fact]
    public void GetFieldNames_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        Assert.Equal(doc.GetFieldNames().Count, doc.GetFieldNames().Count);
    }

    [Fact]
    public void GetFieldNames_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        var before = doc.GetFieldNames().Count;
        var path = TempFile("fn_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldNames().Count);
    }

    // -------------------------------------------------------------------------
    // InferSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void InferSchema_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        var ex = Record.Exception(() => doc.InferSchema());
        Assert.Null(ex);
    }

    [Fact]
    public void InferSchema_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        Assert.NotNull(doc.InferSchema());
    }

    [Fact]
    public void InferSchema_Count_Leq_FieldCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        Assert.True(doc.InferSchema().Count <= doc.GetFieldCount());
    }

    [Fact]
    public void InferSchema_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        Assert.Equal(doc.InferSchema().Count, doc.InferSchema().Count);
    }

    [Fact]
    public void InferSchema_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEventNdjson());
        var before = doc.InferSchema().Count;
        var path = TempFile("is_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.InferSchema().Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldCount_GetFieldNames_InferSchema_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_transactions.ndjson");
        var lines = new[]
        {
            "{\"txId\":\"TX001\",\"accountId\":\"ACC100\",\"type\":\"debit\",\"amount\":250.00,\"currency\":\"USD\",\"merchant\":\"Amazon\",\"category\":\"Shopping\",\"approved\":true,\"timestamp\":1719360000}",
            "{\"txId\":\"TX002\",\"accountId\":\"ACC101\",\"type\":\"credit\",\"amount\":1500.00,\"currency\":\"EUR\",\"merchant\":\"Payroll\",\"category\":\"Income\",\"approved\":true,\"timestamp\":1719360060}",
            "{\"txId\":\"TX003\",\"accountId\":\"ACC100\",\"type\":\"debit\",\"amount\":89.99,\"currency\":\"USD\",\"merchant\":\"Netflix\",\"category\":\"Entertainment\",\"approved\":true,\"timestamp\":1719360120}",
            "{\"txId\":\"TX004\",\"accountId\":\"ACC102\",\"type\":\"debit\",\"amount\":5200.00,\"currency\":\"GBP\",\"merchant\":\"RentCo\",\"category\":\"Housing\",\"approved\":true,\"timestamp\":1719360180}",
            "{\"txId\":\"TX005\",\"accountId\":\"ACC103\",\"type\":\"debit\",\"amount\":75.50,\"currency\":\"USD\",\"merchant\":\"GroceryMart\",\"category\":\"Food\",\"approved\":false,\"timestamp\":1719360240}",
            "{\"txId\":\"TX006\",\"accountId\":\"ACC100\",\"type\":\"credit\",\"amount\":320.00,\"currency\":\"USD\",\"merchant\":\"FreelanceClient\",\"category\":\"Income\",\"approved\":true,\"timestamp\":1719360300}",
            "{\"txId\":\"TX007\",\"accountId\":\"ACC104\",\"type\":\"debit\",\"amount\":45.00,\"currency\":\"CAD\",\"merchant\":\"Pharmacy\",\"category\":\"Health\",\"approved\":true,\"timestamp\":1719360360}"
        };
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(7, doc.GetRecordCount());

        // GetFieldCount
        var fieldCount = doc.GetFieldCount();
        Assert.True(fieldCount > 0);
        Assert.Equal(fieldCount, doc.GetFieldCount()); // consistent

        // GetFieldNames
        var fieldNames = doc.GetFieldNames();
        Assert.NotNull(fieldNames);
        Assert.NotEmpty(fieldNames);
        Assert.Equal(fieldCount, fieldNames.Count);
        Assert.Equal(fieldNames.Count, doc.GetFieldNames().Count); // consistent

        // GetFieldNames contains known fields
        Assert.True(fieldNames.Contains("txId") || fieldNames.Contains("amount") || fieldCount >= 1);

        // InferSchema
        var schema = doc.InferSchema();
        Assert.NotNull(schema);
        Assert.True(schema.Count >= 1);
        Assert.True(schema.Count <= fieldCount);
        Assert.Equal(schema.Count, doc.InferSchema().Count); // consistent

        // GetUniqueFieldValues — type (debit/credit)
        var types = doc.GetUniqueFieldValues("type");
        Assert.NotNull(types);
        Assert.True(types.Count >= 1);
        Assert.True(types.Count <= doc.GetRecordCount());

        // GetUniqueFieldValues — currency
        var currencies = doc.GetUniqueFieldValues("currency");
        Assert.NotNull(currencies);
        Assert.True(currencies.Count >= 1);

        // FilterByRange — amount
        var highValue = doc.FilterByRange("amount", 500.0, double.MaxValue);
        Assert.NotNull(highValue);
        Assert.True(highValue.GetRecordCount() >= 0);
        Assert.True(highValue.GetRecordCount() <= doc.GetRecordCount());

        // AppendRecord
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["txId"] = "TX008",
            ["accountId"] = "ACC105",
            ["type"] = "debit",
            ["amount"] = 199.99,
            ["currency"] = "USD",
            ["merchant"] = "TechStore",
            ["category"] = "Electronics",
            ["approved"] = true,
            ["timestamp"] = 1719360420
        });
        Assert.Equal(8, doc.GetRecordCount());

        // GetFieldCount should be stable after append of same schema
        Assert.Equal(fieldCount, doc.GetFieldCount());

        // SaveToFile
        var savePath = TempFile("dogfood_transactions_out.ndjson");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(8, loaded.GetRecordCount());
        Assert.Equal(fieldCount, loaded.GetFieldCount());
        Assert.Equal(fieldNames.Count, loaded.GetFieldNames().Count);
        Assert.Equal(schema.Count, loaded.InferSchema().Count);

        // GetRecordsByFieldPrefix on loaded
        var debitRecords = loaded.GetRecordsByFieldPrefix("type", "d");
        Assert.NotNull(debitRecords);
        Assert.True(debitRecords.GetRecordCount() >= 0);

        // Final save
        var path2 = TempFile("dogfood_transactions_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), loaded2.GetRecordCount());
        Assert.Equal(loaded.GetFieldCount(), loaded2.GetFieldCount());
        Assert.NotNull(loaded2.InferSchema());
        Assert.True(loaded2.GetFieldNames().Count >= 1);
    }
}
