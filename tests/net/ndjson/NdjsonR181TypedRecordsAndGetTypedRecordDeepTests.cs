// Tests for NdjsonDocument.TypedRecords<T>, GetTypedRecord<T> deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R181

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R181: Tests for NdjsonDocument.TypedRecords&lt;T&gt;, GetTypedRecord&lt;T&gt; deeper coverage.
/// TypedRecords&lt;T&gt;(): deserializes all records to a list of typed T instances.
/// GetTypedRecord&lt;T&gt;(index): deserializes a single record at the given index to T.
/// Covers: TypedRecords non-null; TypedRecords count matches Count;
/// TypedRecords first item non-null; TypedRecords property values correct;
/// TypedRecords all items non-null; GetTypedRecord first non-null;
/// GetTypedRecord last non-null; GetTypedRecord property value correct;
/// GetTypedRecord at different indices; TypedRecords string fields correct;
/// TypedRecords after Filter count matches; GetTypedRecord after Filter correct;
/// dogfood Load->TypedRecords->GetTypedRecord->Filter->TypedRecords->verify pipeline.
/// </summary>
public class NdjsonR181TypedRecordsAndGetTypedRecordDeepTests
{
    private sealed class EmployeeRecord
    {
        public string Name { get; set; } = "";
        public string Dept { get; set; } = "";
        public int Score { get; set; }
    }

    private const string EmployeeNdjson =
        "{\"Name\":\"Alice\",\"Dept\":\"Eng\",\"Score\":95}\n" +
        "{\"Name\":\"Bob\",\"Dept\":\"Finance\",\"Score\":82}\n" +
        "{\"Name\":\"Carol\",\"Dept\":\"Eng\",\"Score\":91}\n" +
        "{\"Name\":\"Dave\",\"Dept\":\"HR\",\"Score\":77}";

    // -------------------------------------------------------------------------
    // TypedRecords<T>
    // -------------------------------------------------------------------------

    [Fact]
    public void TypedRecords_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        Assert.NotNull(doc.TypedRecords<EmployeeRecord>());
    }

    [Fact]
    public void TypedRecords_Count_MatchesDocumentCount()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        var typed = doc.TypedRecords<EmployeeRecord>();
        Assert.Equal(doc.Count, typed.Count);
    }

    [Fact]
    public void TypedRecords_FirstItem_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        var typed = doc.TypedRecords<EmployeeRecord>();
        Assert.NotNull(typed[0]);
    }

    [Fact]
    public void TypedRecords_FirstItem_NameCorrect()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        var typed = doc.TypedRecords<EmployeeRecord>();
        Assert.Equal("Alice", typed[0].Name);
    }

    [Fact]
    public void TypedRecords_FirstItem_DeptCorrect()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        var typed = doc.TypedRecords<EmployeeRecord>();
        Assert.Equal("Eng", typed[0].Dept);
    }

    [Fact]
    public void TypedRecords_AllItems_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        var typed = doc.TypedRecords<EmployeeRecord>();
        Assert.All(typed, item => Assert.NotNull(item));
    }

    [Fact]
    public void TypedRecords_LastItem_NameCorrect()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        var typed = doc.TypedRecords<EmployeeRecord>();
        Assert.Equal("Dave", typed[3].Name);
    }

    [Fact]
    public void TypedRecords_AfterFilter_CountMatches()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        var eng = doc.Filter(r => r.TryGetValue("Dept", out var d) && d == "Eng");
        var typed = eng.TypedRecords<EmployeeRecord>();
        Assert.Equal(2, typed.Count); // Alice and Carol
    }

    // -------------------------------------------------------------------------
    // GetTypedRecord<T>
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTypedRecord_First_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        Assert.NotNull(doc.GetTypedRecord<EmployeeRecord>(0));
    }

    [Fact]
    public void GetTypedRecord_First_NameCorrect()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        var rec = doc.GetTypedRecord<EmployeeRecord>(0);
        Assert.Equal("Alice", rec.Name);
    }

    [Fact]
    public void GetTypedRecord_Second_DeptCorrect()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        var rec = doc.GetTypedRecord<EmployeeRecord>(1);
        Assert.Equal("Finance", rec.Dept);
    }

    [Fact]
    public void GetTypedRecord_Last_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        Assert.NotNull(doc.GetTypedRecord<EmployeeRecord>(3));
    }

    [Fact]
    public void GetTypedRecord_Last_NameCorrect()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        var rec = doc.GetTypedRecord<EmployeeRecord>(3);
        Assert.Equal("Dave", rec.Name);
    }

    [Fact]
    public void GetTypedRecord_AfterFilter_CorrectValue()
    {
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        var eng = doc.Filter(r => r.TryGetValue("Dept", out var d) && d == "Eng");
        var first = eng.GetTypedRecord<EmployeeRecord>(0);
        Assert.Equal("Eng", first.Dept);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadTypedRecordsGetTypedRecordFilterTypedRecordsVerify_Pipeline()
    {
        // Load
        var doc = NdjsonDocument.LoadContent(EmployeeNdjson);
        Assert.Equal(4, doc.Count);

        // TypedRecords
        var all = doc.TypedRecords<EmployeeRecord>();
        Assert.Equal(4, all.Count);
        Assert.Equal("Alice", all[0].Name);
        Assert.Equal("Eng", all[0].Dept);
        Assert.Equal("Dave", all[3].Name);

        // GetTypedRecord
        var second = doc.GetTypedRecord<EmployeeRecord>(1);
        Assert.Equal("Bob", second.Name);
        Assert.Equal("Finance", second.Dept);

        // Filter Eng
        var eng = doc.Filter(r => r.TryGetValue("Dept", out var d) && d == "Eng");
        Assert.Equal(2, eng.Count);

        // TypedRecords from filtered
        var engTyped = eng.TypedRecords<EmployeeRecord>();
        Assert.Equal(2, engTyped.Count);
        Assert.All(engTyped, r => Assert.Equal("Eng", r.Dept));

        // GetTypedRecord from filtered
        var firstEng = eng.GetTypedRecord<EmployeeRecord>(0);
        Assert.Equal("Alice", firstEng.Name);
        Assert.Equal("Eng", firstEng.Dept);
    }
}
