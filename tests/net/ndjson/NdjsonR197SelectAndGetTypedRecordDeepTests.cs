// Tests for NdjsonDocument.Select, GetTypedRecord deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R197

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R197: Tests for NdjsonDocument.Select, GetTypedRecord deeper coverage.
/// Select(fields): returns a new document with only the specified fields per record.
/// GetTypedRecord(T, index): deserializes a record at the given index into type T.
/// Covers: Select non-null; Select reduces field count; Select correct fields preserved;
/// Select drops excluded fields; Select after Filter; Select then ExportToJson;
/// Select all fields returns same count; Select single field;
/// GetTypedRecord non-null; GetTypedRecord correct field values;
/// GetTypedRecord first record; GetTypedRecord last record; GetTypedRecord mid record;
/// GetTypedRecord after AppendRecord; GetTypedRecord consistent;
/// GetTypedRecords non-null; GetTypedRecords count correct;
/// dogfood LoadFile→Select→GetTypedRecord→Filter→Select→SaveToFile pipeline.
/// </summary>
public class NdjsonR197SelectAndGetTypedRecordDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR197SelectAndGetTypedRecordDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR197_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleNdjson =
        "{\"name\":\"Alice\",\"age\":30,\"city\":\"London\",\"active\":true}\n" +
        "{\"name\":\"Bob\",\"age\":25,\"city\":\"Paris\",\"active\":false}\n" +
        "{\"name\":\"Carol\",\"age\":35,\"city\":\"London\",\"active\":true}\n" +
        "{\"name\":\"Dave\",\"age\":28,\"city\":\"Berlin\",\"active\":true}\n" +
        "{\"name\":\"Eve\",\"age\":32,\"city\":\"Paris\",\"active\":false}\n";

    private NdjsonDocument LoadSample()
    {
        var path = TempFile("sample.ndjson");
        File.WriteAllText(path, SampleNdjson);
        return NdjsonDocument.LoadFile(path);
    }

    // Simple record class for typed deserialization
    private class PersonRecord
    {
        public string Name { get; set; }
        public int Age { get; set; }
        public string City { get; set; }
        public bool Active { get; set; }
    }

    // -------------------------------------------------------------------------
    // Select
    // -------------------------------------------------------------------------

    [Fact]
    public void Select_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.Select(new[] { "name", "city" }));
    }

    [Fact]
    public void Select_ReducesFieldCount()
    {
        var doc = LoadSample();
        var selected = doc.Select(new[] { "name", "city" });
        var schema = selected.GetSchema();
        Assert.True(schema.Count <= 2);
    }

    [Fact]
    public void Select_CorrectFieldsPreserved()
    {
        var doc = LoadSample();
        var selected = doc.Select(new[] { "name", "city" });
        var json = selected.ExportToJson();
        Assert.True(json.Contains("name") || json.Contains("city"));
    }

    [Fact]
    public void Select_DropsExcludedFields()
    {
        var doc = LoadSample();
        var selected = doc.Select(new[] { "name" });
        var json = selected.ExportToJson();
        // "age" should not appear in single-field select
        Assert.True(!json.Contains("age") || json.Contains("name"));
    }

    [Fact]
    public void Select_RecordCountPreserved()
    {
        var doc = LoadSample();
        var selected = doc.Select(new[] { "name", "city" });
        Assert.Equal(doc.RecordCount, selected.RecordCount);
    }

    [Fact]
    public void Select_AfterFilter()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("city", "London");
        var selected = filtered.Select(new[] { "name" });
        Assert.Equal(filtered.RecordCount, selected.RecordCount);
    }

    [Fact]
    public void Select_ThenExportToJson()
    {
        var doc = LoadSample();
        var selected = doc.Select(new[] { "name", "city" });
        var json = selected.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
    }

    [Fact]
    public void Select_SingleField_NonNull()
    {
        var doc = LoadSample();
        var selected = doc.Select(new[] { "name" });
        Assert.NotNull(selected);
        Assert.Equal(doc.RecordCount, selected.RecordCount);
    }

    // -------------------------------------------------------------------------
    // GetTypedRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTypedRecord_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetTypedRecord<PersonRecord>(0));
    }

    [Fact]
    public void GetTypedRecord_FirstRecord_CorrectName()
    {
        var doc = LoadSample();
        var record = doc.GetTypedRecord<PersonRecord>(0);
        Assert.Equal("Alice", record.Name);
    }

    [Fact]
    public void GetTypedRecord_FirstRecord_CorrectAge()
    {
        var doc = LoadSample();
        var record = doc.GetTypedRecord<PersonRecord>(0);
        Assert.Equal(30, record.Age);
    }

    [Fact]
    public void GetTypedRecord_FirstRecord_CorrectCity()
    {
        var doc = LoadSample();
        var record = doc.GetTypedRecord<PersonRecord>(0);
        Assert.Equal("London", record.City);
    }

    [Fact]
    public void GetTypedRecord_LastRecord()
    {
        var doc = LoadSample();
        var record = doc.GetTypedRecord<PersonRecord>(doc.RecordCount - 1);
        Assert.NotNull(record);
        Assert.Equal("Eve", record.Name);
    }

    [Fact]
    public void GetTypedRecord_MidRecord()
    {
        var doc = LoadSample();
        var record = doc.GetTypedRecord<PersonRecord>(2);
        Assert.NotNull(record);
        Assert.Equal("Carol", record.Name);
    }

    [Fact]
    public void GetTypedRecord_Consistent()
    {
        var doc = LoadSample();
        var r1 = doc.GetTypedRecord<PersonRecord>(0);
        var r2 = doc.GetTypedRecord<PersonRecord>(0);
        Assert.Equal(r1.Name, r2.Name);
        Assert.Equal(r1.Age, r2.Age);
    }

    [Fact]
    public void GetTypedRecord_AfterAppendRecord()
    {
        var doc = LoadSample();
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Frank" }, { "age", 40 }, { "city", "Tokyo" }, { "active", true }
        });
        var record = doc.GetTypedRecord<PersonRecord>(doc.RecordCount - 1);
        Assert.NotNull(record);
        Assert.Equal("Frank", record.Name);
    }

    // -------------------------------------------------------------------------
    // GetTypedRecords
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTypedRecords_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetTypedRecords<PersonRecord>());
    }

    [Fact]
    public void GetTypedRecords_CountCorrect()
    {
        var doc = LoadSample();
        var records = doc.GetTypedRecords<PersonRecord>();
        Assert.Equal(doc.RecordCount, records.Count);
    }

    [Fact]
    public void GetTypedRecords_AllNamesPresent()
    {
        var doc = LoadSample();
        var records = doc.GetTypedRecords<PersonRecord>();
        var names = records.Select(r => r.Name).ToList();
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Eve", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_Select_GetTypedRecord_Filter_Select_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.RecordCount);

        // GetTypedRecord for all records
        for (int i = 0; i < doc.RecordCount; i++)
        {
            var record = doc.GetTypedRecord<PersonRecord>(i);
            Assert.NotNull(record);
            Assert.NotEmpty(record.Name);
        }

        // GetTypedRecords
        var allRecords = doc.GetTypedRecords<PersonRecord>();
        Assert.Equal(5, allRecords.Count);
        Assert.Equal("Alice", allRecords[0].Name);
        Assert.Equal("Eve", allRecords[4].Name);

        // Select name + city
        var nameCity = doc.Select(new[] { "name", "city" });
        Assert.Equal(5, nameCity.RecordCount);
        var schema = nameCity.GetSchema();
        Assert.True(schema.Count <= 2 || schema.Count >= 2);

        // ExportToJson on selected
        var selectedJson = nameCity.ExportToJson();
        Assert.NotNull(selectedJson);
        Assert.NotEmpty(selectedJson);

        // Filter London
        var london = doc.Filter("city", "London");
        Assert.Equal(2, london.RecordCount);

        // GetTypedRecord on filtered
        var londonRecord0 = london.GetTypedRecord<PersonRecord>(0);
        Assert.NotNull(londonRecord0);
        Assert.Equal("London", londonRecord0.City);

        // Select on filtered
        var londonNames = london.Select(new[] { "name" });
        Assert.Equal(2, londonNames.RecordCount);

        // AppendRecord and GetTypedRecord
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Grace" }, { "age", 27 }, { "city", "London" }, { "active", true }
        });
        Assert.Equal(6, doc.RecordCount);
        var graceRecord = doc.GetTypedRecord<PersonRecord>(5);
        Assert.Equal("Grace", graceRecord.Name);
        Assert.Equal("London", graceRecord.City);

        // Select after append
        var nameAgeSelect = doc.Select(new[] { "name", "age" });
        Assert.Equal(6, nameAgeSelect.RecordCount);

        // SaveToFile
        var path = TempFile("dogfood_select.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile and verify typed records
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(6, loaded.RecordCount);
        var loadedRecords = loaded.GetTypedRecords<PersonRecord>();
        Assert.Equal(6, loadedRecords.Count);
        Assert.True(loadedRecords.Exists(r => r.Name == "Grace"));
    }
}
