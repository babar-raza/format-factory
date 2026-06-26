// Tests for NdjsonDocument.Filter, Sort, GroupBy deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R183

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R183: Tests for NdjsonDocument.Filter, Sort, GroupBy deeper coverage.
/// Filter(predicate): returns a new NdjsonDocument with records matching the predicate.
/// Sort(field, ascending): returns a new NdjsonDocument sorted by the given field.
/// GroupBy(field): returns a dictionary grouping records by the given field value.
/// Covers: Filter non-null; Filter count correct; Filter chain reduces count;
/// Filter then GetFieldValues correct; Sort non-null; Sort ascending order correct;
/// Sort descending order correct; Sort preserves count; GroupBy non-null;
/// GroupBy key count correct; GroupBy group sizes correct; GroupBy all records preserved;
/// dogfood LoadContent->Filter->Sort->GroupBy->GetFieldValues->verify pipeline.
/// </summary>
public class NdjsonR183FilterAndSortDeepTests
{
    private const string SampleNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":92}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":85}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":78}\n" +
        "{\"name\":\"Dave\",\"dept\":\"HR\",\"score\":91}\n" +
        "{\"name\":\"Eve\",\"dept\":\"Finance\",\"score\":88}\n" +
        "{\"name\":\"Frank\",\"dept\":\"Eng\",\"score\":95}";

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        Assert.NotNull(doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng"));
    }

    [Fact]
    public void Filter_ByDept_CorrectCount()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var eng = doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng");
        Assert.Equal(3, eng.Count);
    }

    [Fact]
    public void Filter_EmptyResult_ZeroCount()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var none = doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Marketing");
        Assert.Equal(0, none.Count);
    }

    [Fact]
    public void Filter_AllMatch_SameCount()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var all = doc.Filter(r => true);
        Assert.Equal(doc.Count, all.Count);
    }

    [Fact]
    public void Filter_Chain_TwoConditions_CorrectCount()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var engHighScore = doc
            .Filter(r => r.TryGetValue("dept", out var d) && d == "Eng")
            .Filter(r => r.TryGetValue("score", out var s) && int.Parse(s) >= 90);
        // Alice(92) and Frank(95) — Carol is 78
        Assert.Equal(2, engHighScore.Count);
    }

    [Fact]
    public void Filter_ThenGetFieldValues_CorrectValues()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var finance = doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Finance");
        var names = finance.GetFieldValues("name");
        Assert.Contains("Bob", names);
        Assert.Contains("Eve", names);
        Assert.DoesNotContain("Alice", names);
    }

    // -------------------------------------------------------------------------
    // Sort
    // -------------------------------------------------------------------------

    [Fact]
    public void Sort_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        Assert.NotNull(doc.Sort("name", ascending: true));
    }

    [Fact]
    public void Sort_PreservesCount()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var sorted = doc.Sort("name", ascending: true);
        Assert.Equal(doc.Count, sorted.Count);
    }

    [Fact]
    public void Sort_Ascending_FirstRecordAlphabetical()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var sorted = doc.Sort("name", ascending: true);
        sorted.RecordAt(0).TryGetValue("name", out var first);
        Assert.Equal("Alice", first);
    }

    [Fact]
    public void Sort_Descending_FirstRecordLastAlphabetical()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var sorted = doc.Sort("name", ascending: false);
        sorted.RecordAt(0).TryGetValue("name", out var first);
        Assert.Equal("Frank", first);
    }

    [Fact]
    public void Sort_Numeric_Ascending_LowestFirst()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var sorted = doc.Sort("score", ascending: true);
        sorted.RecordAt(0).TryGetValue("name", out var lowest);
        // Carol has score 78 (lowest)
        Assert.Equal("Carol", lowest);
    }

    // -------------------------------------------------------------------------
    // GroupBy
    // -------------------------------------------------------------------------

    [Fact]
    public void GroupBy_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        Assert.NotNull(doc.GroupBy("dept"));
    }

    [Fact]
    public void GroupBy_KeyCount_CorrectNumberOfGroups()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var groups = doc.GroupBy("dept");
        Assert.Equal(3, groups.Count); // Eng, Finance, HR
    }

    [Fact]
    public void GroupBy_EngGroup_HasThreeRecords()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var groups = doc.GroupBy("dept");
        Assert.True(groups.ContainsKey("Eng"));
        Assert.Equal(3, groups["Eng"].Count);
    }

    [Fact]
    public void GroupBy_FinanceGroup_HasTwoRecords()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var groups = doc.GroupBy("dept");
        Assert.True(groups.ContainsKey("Finance"));
        Assert.Equal(2, groups["Finance"].Count);
    }

    [Fact]
    public void GroupBy_AllRecordsPreserved()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var groups = doc.GroupBy("dept");
        var total = 0;
        foreach (var grp in groups.Values)
            total += grp.Count;
        Assert.Equal(doc.Count, total);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_Filter_Sort_GroupBy_GetFieldValues_Verify_Pipeline()
    {
        // Load
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        Assert.Equal(6, doc.Count);

        // Filter Engineering
        var eng = doc.Filter(r => r.TryGetValue("dept", out var d) && d == "Eng");
        Assert.Equal(3, eng.Count);

        // Sort by score ascending within Eng
        var sorted = eng.Sort("score", ascending: true);
        sorted.RecordAt(0).TryGetValue("name", out var lowestEng);
        Assert.Equal("Carol", lowestEng); // score 78

        // GetFieldValues from sorted
        var names = sorted.GetFieldValues("name");
        Assert.Equal(3, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Frank", names);

        // GroupBy dept on full doc
        var groups = doc.GroupBy("dept");
        Assert.Equal(3, groups.Count);
        Assert.Equal(3, groups["Eng"].Count);
        Assert.Equal(2, groups["Finance"].Count);
        Assert.Equal(1, groups["HR"].Count);

        // Filter chain: Finance with score > 86
        var financeHigh = doc
            .Filter(r => r.TryGetValue("dept", out var d) && d == "Finance")
            .Filter(r => r.TryGetValue("score", out var s) && int.Parse(s) > 86);
        Assert.Equal(1, financeHigh.Count);
        financeHigh.RecordAt(0).TryGetValue("name", out var topFinance);
        Assert.Equal("Eve", topFinance); // score 88
    }
}
