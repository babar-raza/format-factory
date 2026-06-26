// Tests for NdjsonDocument.ToNdjson, Count, TypedRecords deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R166

using System;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R166: Tests for NdjsonDocument.ToNdjson, Count, TypedRecords deeper coverage.
/// ToNdjson(): serializes document to NDJSON string.
/// Count: total number of records.
/// TypedRecords: list of NdjsonRecord typed wrappers.
/// Covers: ToNdjson non-null for non-empty doc; ToNdjson non-empty for non-empty doc;
/// ToNdjson contains data values; ToNdjson->Load round-trip count matches;
/// ToNdjson->Load field values correct; Count zero for empty doc;
/// Count matches RowCount property; TypedRecords count matches Count;
/// TypedRecords first element TryGetString; TypedRecords last element field;
/// ToNdjson empty doc returns empty string or whitespace;
/// Filter->ToNdjson->Load preserves schema; Count after Filter;
/// TypedRecords after Filter;
/// dogfood Load->ToNdjson->Load->Filter->ToNdjson->Load chain.
/// </summary>
public class NdjsonR166ToNdjsonAndCountTests
{
    private const string ThreeRecordNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}";

    // -------------------------------------------------------------------------
    // ToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_NonNull()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.NotNull(doc.ToNdjson());
    }

    [Fact]
    public void ToNdjson_NonEmpty()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.False(string.IsNullOrWhiteSpace(doc.ToNdjson()));
    }

    [Fact]
    public void ToNdjson_ContainsDataValues()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var ndjson = doc.ToNdjson();
        Assert.Contains("Alice", ndjson);
        Assert.Contains("Bob", ndjson);
        Assert.Contains("Carol", ndjson);
    }

    [Fact]
    public void ToNdjson_Load_RoundTrip_CountMatches()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var ndjson = doc.ToNdjson();
        var loaded = NdjsonDocument.Load(ndjson);
        Assert.Equal(doc.Count, loaded.Count);
    }

    [Fact]
    public void ToNdjson_Load_RoundTrip_FieldValuesCorrect()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var ndjson = doc.ToNdjson();
        var loaded = NdjsonDocument.Load(ndjson);
        var names = loaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void ToNdjson_EmptyDoc_ReturnsEmptyOrWhitespace()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        var ndjson = doc.ToNdjson();
        // Empty doc should produce empty/whitespace string
        Assert.True(string.IsNullOrWhiteSpace(ndjson) || ndjson.Length == 0);
    }

    [Fact]
    public void Filter_ToNdjson_Load_PreservesSchema()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var ndjson = eng.ToNdjson();
        var loaded = NdjsonDocument.Load(ndjson);
        Assert.True(loaded.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // Count
    // -------------------------------------------------------------------------

    [Fact]
    public void Count_ZeroForEmptyDoc()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        Assert.Equal(0, doc.Count);
    }

    [Fact]
    public void Count_ThreeForThreeRecords()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void Count_AfterFilter_Decreases()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);
    }

    // -------------------------------------------------------------------------
    // TypedRecords
    // -------------------------------------------------------------------------

    [Fact]
    public void TypedRecords_CountMatchesCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(doc.Count, doc.TypedRecords.Count);
    }

    [Fact]
    public void TypedRecords_FirstElement_TryGetStringName()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var first = doc.TypedRecords[0];
        Assert.True(first.TryGetString("name", out var name));
        Assert.Equal("Alice", name);
    }

    [Fact]
    public void TypedRecords_LastElement_FieldAccessible()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var last = doc.TypedRecords[doc.Count - 1];
        Assert.True(last.TryGetString("name", out var name));
        Assert.Equal("Carol", name);
    }

    [Fact]
    public void TypedRecords_AfterFilter_CountMatches()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.TypedRecords.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->ToNdjson->Load->Filter->ToNdjson->Load chain
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadToNdjsonLoadFilterToNdjsonLoad_Chain()
    {
        // Load
        var doc1 = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(3, doc1.Count);

        // ToNdjson -> Load
        var ndjson1 = doc1.ToNdjson();
        var doc2 = NdjsonDocument.Load(ndjson1);
        Assert.Equal(3, doc2.Count);
        Assert.Equal(3, doc2.TypedRecords.Count);

        // Filter
        var eng = doc2.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // ToNdjson -> Load
        var ndjson2 = eng.ToNdjson();
        var doc3 = NdjsonDocument.Load(ndjson2);
        Assert.Equal(2, doc3.Count);
        Assert.True(doc3.IsUniformSchema());

        // TypedRecords
        var names = doc3.TypedRecords;
        Assert.Equal(2, names.Count);
        Assert.True(names[0].TryGetString("name", out var n0));
        Assert.Equal("Alice", n0);
    }
}
