// Tests for NdjsonDocument TypedRecords+GetTypedRecord deep pipeline coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R162

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R162: Tests for NdjsonDocument TypedRecords/GetTypedRecord deeper pipeline.
/// TypedRecords: IReadOnlyList of NdjsonRecord.
/// GetTypedRecord(index): returns NdjsonRecord by index.
/// NdjsonRecord.Keys: field names; TryGetValue: typed field access.
/// Covers: TypedRecords[0].Keys count; TypedRecords all records same key count;
/// GetTypedRecord 0 name is Alice; GetTypedRecord last index;
/// TryGetValue dept found; TryGetValue score value; TryGetValue not found;
/// TypedRecords count after Filter; GetTypedRecord after Filter index 0;
/// TypedRecords on single record; TryGetValue on second record;
/// NdjsonRecord.Keys contains all fields; TypedRecords on empty doc count;
/// dogfood Load->Filter->TypedRecords->TryGetValue->GetFieldValues chain.
/// </summary>
public class NdjsonR162TypedRecordsPipelineTests
{
    private const string FourRecordNdjson =
        "{\"name\":\"Alice\",\"score\":95,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Bob\",\"score\":82,\"dept\":\"Finance\"}\n" +
        "{\"name\":\"Carol\",\"score\":88,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Dave\",\"score\":91,\"dept\":\"Finance\"}";

    // -------------------------------------------------------------------------
    // TypedRecords deep coverage
    // -------------------------------------------------------------------------

    [Fact]
    public void TypedRecords_FirstRecord_KeysCount_IsThree()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        Assert.Equal(3, doc.TypedRecords[0].Keys.Count);
    }

    [Fact]
    public void TypedRecords_AllRecords_SameKeyCount()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        foreach (var rec in doc.TypedRecords)
            Assert.Equal(3, rec.Keys.Count);
    }

    [Fact]
    public void TypedRecords_Keys_ContainAllFields()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var keys = doc.TypedRecords[0].Keys;
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("dept", keys);
    }

    [Fact]
    public void TypedRecords_SingleRecord_CountIsOne()
    {
        var doc = NdjsonDocument.Load("{\"x\":1}");
        Assert.Single(doc.TypedRecords);
    }

    [Fact]
    public void TypedRecords_OnEmptyDoc_CountIsZero()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        Assert.Equal(0, doc.TypedRecords.Count);
    }

    // -------------------------------------------------------------------------
    // GetTypedRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTypedRecord_Index0_NameIsAlice()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var rec = doc.GetTypedRecord(0);
        rec.TryGetValue("name", out var name);
        Assert.Equal("Alice", name);
    }

    [Fact]
    public void GetTypedRecord_LastIndex_NameIsDave()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var rec = doc.GetTypedRecord(3);
        rec.TryGetValue("name", out var name);
        Assert.Equal("Dave", name);
    }

    [Fact]
    public void GetTypedRecord_Index1_NameIsBob()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var rec = doc.GetTypedRecord(1);
        rec.TryGetValue("name", out var name);
        Assert.Equal("Bob", name);
    }

    // -------------------------------------------------------------------------
    // TryGetValue
    // -------------------------------------------------------------------------

    [Fact]
    public void TryGetValue_Dept_Found()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var rec = doc.GetTypedRecord(0);
        Assert.True(rec.TryGetValue("dept", out var dept));
        Assert.Equal("Eng", dept);
    }

    [Fact]
    public void TryGetValue_Score_HasValue()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var rec = doc.GetTypedRecord(0);
        var found = rec.TryGetValue("score", out var val);
        Assert.True(found);
        Assert.Contains("95", val);
    }

    [Fact]
    public void TryGetValue_NotFound_ReturnsFalse()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var rec = doc.GetTypedRecord(0);
        Assert.False(rec.TryGetValue("nonexistent_xyz", out _));
    }

    [Fact]
    public void TryGetValue_SecondRecord_DeptIsFinance()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var rec = doc.GetTypedRecord(1);
        rec.TryGetValue("dept", out var dept);
        Assert.Equal("Finance", dept);
    }

    // -------------------------------------------------------------------------
    // TypedRecords after Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void TypedRecords_CountAfterFilter()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.TypedRecords.Count);
    }

    [Fact]
    public void GetTypedRecord_AfterFilter_Index0_IsAlice()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var rec = eng.GetTypedRecord(0);
        rec.TryGetValue("name", out var name);
        Assert.Equal("Alice", name);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->TypedRecords->TryGetValue->GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterTypedRecordsTryGetValueGetFieldValues_Pipeline()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        Assert.Equal(4, doc.Count);
        Assert.Equal(4, doc.TypedRecords.Count);

        // TypedRecords all have name field
        foreach (var rec in doc.TypedRecords)
            Assert.True(rec.TryGetValue("name", out _));

        // Filter Finance
        var finance = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Finance");
        Assert.Equal(2, finance.Count);
        Assert.Equal(2, finance.TypedRecords.Count);

        // GetTypedRecord on filtered
        var firstFinance = finance.GetTypedRecord(0);
        firstFinance.TryGetValue("name", out var firstName);
        Assert.Equal("Bob", firstName);

        // TryGetValue for all finance records
        foreach (var rec in finance.TypedRecords)
        {
            rec.TryGetValue("dept", out var dept);
            Assert.Equal("Finance", dept);
        }

        // GetFieldValues on filtered
        var names = finance.GetFieldValues("name");
        Assert.Contains("Bob", names);
        Assert.Contains("Dave", names);
    }
}
