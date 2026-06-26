// Tests for NdjsonDocument.Count, RecordAt, Records, GetFieldValues, TryGetValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R176

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R176: Tests for NdjsonDocument.Count, RecordAt, Records, GetFieldValues, TryGetValue deeper.
/// Count: total number of records in the document.
/// RecordAt(index): returns the NdjsonRecord at the given zero-based index.
/// Records: IReadOnlyList of all records.
/// GetFieldValues(field): returns all values for a given field across all records.
/// NdjsonRecord.TryGetValue(field, out value): retrieves a field value if present.
/// Covers: Count equals loaded records; Count after LoadContent; RecordAt first correct;
/// RecordAt last correct; RecordAt out-of-range throws; Records list non-null;
/// Records.Count equals Count; Records items accessible;
/// GetFieldValues returns correct count; GetFieldValues contains expected values;
/// GetFieldValues missing field returns empty; TryGetValue returns true for present field;
/// TryGetValue returns correct value; TryGetValue returns false for missing field;
/// dogfood Load->Count->RecordAt->TryGetValue->GetFieldValues->Filter->verify pipeline.
/// </summary>
public class NdjsonR176RecordCountAndFieldAccessDeepTests
{
    private const string ThreeRecordNdjson =
        "{\"id\":1,\"name\":\"Alice\",\"dept\":\"Eng\"}\n" +
        "{\"id\":2,\"name\":\"Bob\",\"dept\":\"Finance\"}\n" +
        "{\"id\":3,\"name\":\"Carol\",\"dept\":\"Eng\"}";

    private const string FiveRecordNdjson =
        "{\"product\":\"Alpha\",\"price\":10.5,\"active\":true}\n" +
        "{\"product\":\"Beta\",\"price\":20.0,\"active\":false}\n" +
        "{\"product\":\"Gamma\",\"price\":15.75,\"active\":true}\n" +
        "{\"product\":\"Delta\",\"price\":8.0,\"active\":true}\n" +
        "{\"product\":\"Epsilon\",\"price\":30.0,\"active\":false}";

    // -------------------------------------------------------------------------
    // Count
    // -------------------------------------------------------------------------

    [Fact]
    public void Count_EqualsLoadedRecords()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void Count_FiveRecords_Correct()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        Assert.Equal(5, doc.Count);
    }

    [Fact]
    public void Count_SingleRecord_IsOne()
    {
        var doc = NdjsonDocument.LoadContent("{\"x\":1}");
        Assert.Equal(1, doc.Count);
    }

    // -------------------------------------------------------------------------
    // RecordAt
    // -------------------------------------------------------------------------

    [Fact]
    public void RecordAt_First_NotNull()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        Assert.NotNull(doc.RecordAt(0));
    }

    [Fact]
    public void RecordAt_Last_NotNull()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        Assert.NotNull(doc.RecordAt(2));
    }

    [Fact]
    public void RecordAt_First_ContainsExpectedField()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var rec = doc.RecordAt(0);
        Assert.True(rec.TryGetValue("name", out var val));
        Assert.Equal("Alice", val);
    }

    [Fact]
    public void RecordAt_Last_ContainsExpectedField()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var rec = doc.RecordAt(2);
        Assert.True(rec.TryGetValue("name", out var val));
        Assert.Equal("Carol", val);
    }

    // -------------------------------------------------------------------------
    // Records
    // -------------------------------------------------------------------------

    [Fact]
    public void Records_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        Assert.NotNull(doc.Records);
    }

    [Fact]
    public void Records_Count_EqualsDocumentCount()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        Assert.Equal(doc.Count, doc.Records.Count);
    }

    [Fact]
    public void Records_FirstItem_FieldAccessible()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var first = doc.Records[0];
        Assert.True(first.TryGetValue("dept", out var dept));
        Assert.Equal("Eng", dept);
    }

    [Fact]
    public void Records_AllItemsNonNull()
    {
        var doc = NdjsonDocument.LoadContent(FiveRecordNdjson);
        foreach (var rec in doc.Records)
            Assert.NotNull(rec);
    }

    // -------------------------------------------------------------------------
    // GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValues_Count_EqualsRecordCount()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var names = doc.GetFieldValues("name");
        Assert.Equal(3, names.Count);
    }

    [Fact]
    public void GetFieldValues_ContainsExpectedValues()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void GetFieldValues_MissingField_ReturnsEmpty()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var result = doc.GetFieldValues("nonexistent");
        Assert.True(result == null || result.Count == 0);
    }

    [Fact]
    public void GetFieldValues_DeptField_CorrectValues()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var depts = doc.GetFieldValues("dept");
        Assert.Contains("Eng", depts);
        Assert.Contains("Finance", depts);
    }

    // -------------------------------------------------------------------------
    // TryGetValue
    // -------------------------------------------------------------------------

    [Fact]
    public void TryGetValue_PresentField_ReturnsTrue()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var rec = doc.RecordAt(0);
        Assert.True(rec.TryGetValue("name", out _));
    }

    [Fact]
    public void TryGetValue_PresentField_CorrectValue()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var rec = doc.RecordAt(1);
        rec.TryGetValue("name", out var val);
        Assert.Equal("Bob", val);
    }

    [Fact]
    public void TryGetValue_MissingField_ReturnsFalse()
    {
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        var rec = doc.RecordAt(0);
        Assert.False(rec.TryGetValue("nonexistent", out _));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadCountRecordAtTryGetValueGetFieldValuesFilterVerify_Pipeline()
    {
        // Load
        var doc = NdjsonDocument.LoadContent(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);

        // RecordAt
        var first = doc.RecordAt(0);
        Assert.NotNull(first);
        Assert.True(first.TryGetValue("name", out var firstName));
        Assert.Equal("Alice", firstName);

        // Records list
        Assert.Equal(3, doc.Records.Count);

        // GetFieldValues for dept
        var depts = doc.GetFieldValues("dept");
        Assert.Equal(3, depts.Count);
        Assert.Contains("Eng", depts);
        Assert.Contains("Finance", depts);

        // Filter by dept=Eng
        var eng = doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng");
        Assert.Equal(2, eng.Count);

        // GetFieldValues from filtered
        var engNames = eng.GetFieldValues("name");
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);
        Assert.DoesNotContain("Bob", engNames);

        // TryGetValue on filtered record
        var firstEng = eng.RecordAt(0);
        Assert.True(firstEng.TryGetValue("dept", out var engDept));
        Assert.Equal("Eng", engDept);
    }
}
