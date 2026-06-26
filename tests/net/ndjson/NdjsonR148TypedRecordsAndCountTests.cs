// Tests for NdjsonDocument.TypedRecords, GetTypedRecord, Count, ToNdjson.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R148

using System;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R148: Tests for NdjsonDocument.TypedRecords, GetTypedRecord, Count, ToNdjson.
/// TypedRecords: IReadOnlyList of NdjsonRecord wrapping each JsonElement.
/// GetTypedRecord(index): returns NdjsonRecord at given index; throws OOB.
/// Count: number of records in the document.
/// ToNdjson(): serializes all records to NDJSON string.
/// Covers: TypedRecords count matches Count; TypedRecords accessible by index;
/// TypedRecords field access via TryGetValue; GetTypedRecord valid index;
/// GetTypedRecord OOB throws; Count empty doc is 0; Count matches record count;
/// ToNdjson contains curly braces; ToNdjson round-trip preserves count;
/// ToNdjson includes field values; dogfood Load->TypedRecords->Filter->ToNdjson pipeline.
/// </summary>
public class NdjsonR148TypedRecordsAndCountTests
{
    private const string ThreeRecordNdjson =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"score\":88}";

    // -------------------------------------------------------------------------
    // TypedRecords
    // -------------------------------------------------------------------------

    [Fact]
    public void TypedRecords_CountMatchesDocumentCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(doc.Count, doc.TypedRecords.Count);
    }

    [Fact]
    public void TypedRecords_AccessibleByIndex()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var record = doc.TypedRecords[0];
        Assert.NotNull(record);
    }

    [Fact]
    public void TypedRecords_FieldAccessViaTryGetValue()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var record = doc.TypedRecords[0];
        var found = record.TryGetValue("name", out var val);
        Assert.True(found);
        Assert.Equal("Alice", val.GetString());
    }

    [Fact]
    public void TypedRecords_AllHaveRawElement()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        foreach (var record in doc.TypedRecords)
        {
            Assert.Equal(JsonValueKind.Object, record.RawElement.ValueKind);
        }
    }

    // -------------------------------------------------------------------------
    // GetTypedRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTypedRecord_ValidIndex_ReturnsRecord()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var record = doc.GetTypedRecord(1);
        Assert.NotNull(record);
        var found = record.TryGetValue("name", out var val);
        Assert.True(found);
        Assert.Equal("Bob", val.GetString());
    }

    [Fact]
    public void GetTypedRecord_OobIndex_Throws()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.ThrowsAny<Exception>(() => doc.GetTypedRecord(doc.Count));
    }

    [Fact]
    public void GetTypedRecord_NegativeIndex_Throws()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.ThrowsAny<Exception>(() => doc.GetTypedRecord(-1));
    }

    // -------------------------------------------------------------------------
    // Count
    // -------------------------------------------------------------------------

    [Fact]
    public void Count_EmptyDoc_IsZero()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        Assert.Equal(0, doc.Count);
    }

    [Fact]
    public void Count_ThreeRecords_IsThree()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void Count_SingleRecord_IsOne()
    {
        var doc = NdjsonDocument.Load("{\"x\":1}");
        Assert.Equal(1, doc.Count);
    }

    // -------------------------------------------------------------------------
    // ToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_ContainsBraces()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var ndjson = doc.ToNdjson();
        Assert.Contains("{", ndjson);
        Assert.Contains("}", ndjson);
    }

    [Fact]
    public void ToNdjson_ContainsFieldValues()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var ndjson = doc.ToNdjson();
        Assert.Contains("Alice", ndjson);
        Assert.Contains("Bob", ndjson);
    }

    [Fact]
    public void ToNdjson_RoundTrip_PreservesCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var ndjson = doc.ToNdjson();
        var reloaded = NdjsonDocument.Load(ndjson);
        Assert.Equal(doc.Count, reloaded.Count);
    }

    [Fact]
    public void ToNdjson_EmptyDoc_ReturnsEmptyOrNewline()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        var ndjson = doc.ToNdjson();
        Assert.True(string.IsNullOrWhiteSpace(ndjson));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->TypedRecords->Filter->ToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_TypedRecordsFilterToNdjson_Pipeline()
    {
        var ndjson =
            "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
            "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":72}\n" +
            "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}";

        var doc = NdjsonDocument.Load(ndjson);
        Assert.Equal(3, doc.Count);

        // Access TypedRecords
        var first = doc.TypedRecords[0];
        first.TryGetValue("name", out var firstName);
        Assert.Equal("Alice", firstName.GetString());

        // Filter via Eng dept
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // GetTypedRecord on filtered
        var engFirst = eng.GetTypedRecord(0);
        Assert.NotNull(engFirst);

        // Serialize filtered
        var filteredNdjson = eng.ToNdjson();
        Assert.Contains("Alice", filteredNdjson);
        Assert.Contains("Carol", filteredNdjson);

        // Round-trip
        var reloaded = NdjsonDocument.Load(filteredNdjson);
        Assert.Equal(2, reloaded.Count);
    }
}
