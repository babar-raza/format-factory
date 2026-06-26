// Tests for NdjsonDocument.ToNdjson, Count, Load chain deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R173

using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R173: Tests for NdjsonDocument.ToNdjson, Count, Load chain.
/// ToNdjson(): serializes document back to NDJSON string.
/// Count: number of records in document.
/// Covers: ToNdjson non-null; ToNdjson non-empty; ToNdjson contains record data;
/// ToNdjson->Load round-trip count matches; ToNdjson->Load values correct;
/// Count non-zero for non-empty doc; Count zero for empty doc;
/// Count matches TypedRecords count; ToNdjson after Filter only filtered records;
/// ToNdjson->Load->Filter chain; Load->ToNdjson->Load->ToNdjson idempotent count;
/// ToNdjson preserves all field values; Count after Filter is reduced;
/// Multiple Filter->ToNdjson->Load chain;
/// dogfood Load->Count->ToNdjson->Load->Filter->ToNdjson->Load->Count verify.
/// </summary>
public class NdjsonR173ToNdjsonAndLoadChainTests
{
    private const string FiveRecordNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}\n" +
        "{\"name\":\"Dave\",\"dept\":\"HR\",\"score\":76}\n" +
        "{\"name\":\"Eve\",\"dept\":\"Eng\",\"score\":91}";

    // -------------------------------------------------------------------------
    // ToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_NonNull()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        Assert.NotNull(doc.ToNdjson());
    }

    [Fact]
    public void ToNdjson_NonEmpty()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        Assert.False(string.IsNullOrWhiteSpace(doc.ToNdjson()));
    }

    [Fact]
    public void ToNdjson_ContainsFirstRecordData()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        Assert.Contains("Alice", doc.ToNdjson());
    }

    [Fact]
    public void ToNdjson_ContainsAllNames()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var ndjson = doc.ToNdjson();
        Assert.Contains("Alice", ndjson);
        Assert.Contains("Bob", ndjson);
        Assert.Contains("Carol", ndjson);
        Assert.Contains("Dave", ndjson);
        Assert.Contains("Eve", ndjson);
    }

    [Fact]
    public void ToNdjson_Load_RoundTrip_CountMatches()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var loaded = NdjsonDocument.Load(doc.ToNdjson());
        Assert.Equal(5, loaded.Count);
    }

    [Fact]
    public void ToNdjson_Load_RoundTrip_ValuesCorrect()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var loaded = NdjsonDocument.Load(doc.ToNdjson());
        var names = loaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);
    }

    [Fact]
    public void ToNdjson_AfterFilter_OnlyFilteredRecords()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var ndjson = eng.ToNdjson();
        Assert.Contains("Alice", ndjson);
        Assert.Contains("Carol", ndjson);
        Assert.Contains("Eve", ndjson);
        Assert.DoesNotContain("Bob", ndjson);
        Assert.DoesNotContain("Dave", ndjson);
    }

    [Fact]
    public void ToNdjson_Idempotent_DoubleSerialization()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var first = NdjsonDocument.Load(doc.ToNdjson());
        var second = NdjsonDocument.Load(first.ToNdjson());
        Assert.Equal(first.Count, second.Count);
    }

    // -------------------------------------------------------------------------
    // Count
    // -------------------------------------------------------------------------

    [Fact]
    public void Count_NonZero_ForNonEmptyDoc()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        Assert.True(doc.Count > 0);
    }

    [Fact]
    public void Count_IsFive()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        Assert.Equal(5, doc.Count);
    }

    [Fact]
    public void Count_Zero_ForEmptyDoc()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        Assert.Equal(0, doc.Count);
    }

    [Fact]
    public void Count_MatchesTypedRecordsCount()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        Assert.Equal(doc.Count, doc.TypedRecords.Count);
    }

    [Fact]
    public void Count_AfterFilter_Reduced()
    {
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(3, eng.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadCountToNdjsonLoadFilterToNdjsonLoadCountVerify_Pipeline()
    {
        // Load
        var doc = NdjsonDocument.Load(FiveRecordNdjson);
        Assert.Equal(5, doc.Count);

        // ToNdjson
        var ndjson1 = doc.ToNdjson();
        Assert.Contains("Eve", ndjson1);

        // Load from ToNdjson
        var loaded1 = NdjsonDocument.Load(ndjson1);
        Assert.Equal(5, loaded1.Count);

        // Filter Eng dept
        var eng = loaded1.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(3, eng.Count);

        // ToNdjson filtered
        var ndjson2 = eng.ToNdjson();
        Assert.DoesNotContain("Bob", ndjson2);

        // Load filtered
        var loaded2 = NdjsonDocument.Load(ndjson2);
        Assert.Equal(3, loaded2.Count);

        // Filter again by score > 90
        var highScore = loaded2.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetInt32() > 90);
        Assert.Equal(2, highScore.Count); // Alice(95) and Eve(91)

        var finalNames = highScore.GetFieldValues("name");
        Assert.Contains("Alice", finalNames);
        Assert.Contains("Eve", finalNames);
        Assert.DoesNotContain("Carol", finalNames);
    }
}
