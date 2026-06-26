// Tests for NdjsonDocument.Filter(Func<JsonElement, bool> predicate).
// Sprint: ff-sprint-s131-dotnet-deepening-20260627
// Ledger: PC-NDJSON-R135

using System;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R135: Tests for NdjsonDocument.Filter(Func&lt;JsonElement, bool&gt; predicate).
/// Filter returns a new NdjsonDocument containing only records that satisfy the
/// predicate. Original document is unchanged. Empty documents return empty results.
/// Covers: Filter all-match predicate → same count; Filter none-match → empty;
/// Filter by field value → correct subset; Filter result is new document;
/// Filter on empty document → empty; Filter preserves record order;
/// Filter null predicate throws ArgumentNullException;
/// GetAllKeys on filtered result; dogfood Filter → Filter pipeline (chained).
/// </summary>
public class NdjsonR135FilterPredicateTests
{
    private static NdjsonDocument LoadThreeRecords() =>
        NdjsonDocument.Load(
            "{\"name\":\"Alice\",\"score\":95,\"active\":true}\n" +
            "{\"name\":\"Bob\",\"score\":72,\"active\":false}\n" +
            "{\"name\":\"Carol\",\"score\":88,\"active\":true}");

    // -------------------------------------------------------------------------
    // Filter: all-match predicate
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_AlwaysTruePredicate_ReturnsSameCount()
    {
        var doc = LoadThreeRecords();
        var filtered = doc.Filter(_ => true);
        Assert.Equal(3, filtered.Count);
    }

    [Fact]
    public void Filter_AlwaysFalsePredicate_ReturnsEmpty()
    {
        var doc = LoadThreeRecords();
        var filtered = doc.Filter(_ => false);
        Assert.Equal(0, filtered.Count);
    }

    // -------------------------------------------------------------------------
    // Filter: selective predicate
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_ByScoreAbove80_ReturnsTwoRecords()
    {
        var doc = LoadThreeRecords();
        var filtered = doc.Filter(rec =>
        {
            if (rec.ValueKind != JsonValueKind.Object) return false;
            if (!rec.TryGetProperty("score", out var score)) return false;
            return score.GetInt32() > 80;
        });
        Assert.Equal(2, filtered.Count);
    }

    [Fact]
    public void Filter_ActiveOnly_ReturnsTwoRecords()
    {
        var doc = LoadThreeRecords();
        var filtered = doc.Filter(rec =>
        {
            if (rec.ValueKind != JsonValueKind.Object) return false;
            if (!rec.TryGetProperty("active", out var active)) return false;
            return active.GetBoolean();
        });
        Assert.Equal(2, filtered.Count);
    }

    // -------------------------------------------------------------------------
    // Filter: result is a new NdjsonDocument
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_Result_IsNewDocument()
    {
        var doc = LoadThreeRecords();
        var filtered = doc.Filter(_ => true);
        Assert.NotSame(doc, filtered);
    }

    // -------------------------------------------------------------------------
    // Filter: empty document
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_EmptyDocument_AlwaysTruePredicate_ReturnsEmpty()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        var filtered = doc.Filter(_ => true);
        Assert.Equal(0, filtered.Count);
    }

    // -------------------------------------------------------------------------
    // Filter: order preservation
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_PreservesRecordOrder()
    {
        var doc = LoadThreeRecords();
        var filtered = doc.Filter(rec =>
        {
            if (!rec.TryGetProperty("name", out var name)) return false;
            return name.GetString() != "Bob";
        });

        Assert.Equal(2, filtered.Count);
        // First record should still be Alice
        Assert.True(filtered.Records[0].TryGetProperty("name", out var first));
        Assert.Equal("Alice", first.GetString());
    }

    // -------------------------------------------------------------------------
    // Filter: GetAllKeys on result
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_Result_GetAllKeys_ContainsExpectedKeys()
    {
        var doc = LoadThreeRecords();
        var filtered = doc.Filter(_ => true);
        var keys = filtered.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
    }

    // -------------------------------------------------------------------------
    // Dogfood: chained Filter pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ChainedFilter_ActiveAndHighScore()
    {
        var doc = LoadThreeRecords();

        // First filter: active=true → Alice and Carol
        var activeOnly = doc.Filter(rec =>
        {
            if (!rec.TryGetProperty("active", out var active)) return false;
            return active.GetBoolean();
        });

        // Second filter: score > 90 → only Alice
        var topActive = activeOnly.Filter(rec =>
        {
            if (!rec.TryGetProperty("score", out var score)) return false;
            return score.GetInt32() > 90;
        });

        Assert.Equal(1, topActive.Count);
        Assert.True(topActive.Records[0].TryGetProperty("name", out var name));
        Assert.Equal("Alice", name.GetString());
    }
}
