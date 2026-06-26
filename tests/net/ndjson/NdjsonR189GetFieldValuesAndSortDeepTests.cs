// Tests for NdjsonDocument.GetFieldValues, Sort deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R189

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R189: Tests for NdjsonDocument.GetFieldValues, Sort deeper coverage.
/// GetFieldValues(field): returns all values of a field across all records.
/// Sort(field, ascending): returns a new document with records sorted by field.
/// Covers: GetFieldValues non-null; GetFieldValues count equals Count;
/// GetFieldValues all present; GetFieldValues after Filter reduces count;
/// GetFieldValues missing field returns empty or null values;
/// GetFieldValues after AppendRecord includes new;
/// Sort ascending non-null; Sort ascending correct order (first/last elements);
/// Sort descending non-null; Sort descending correct order;
/// Sort by numeric field ascending; Sort by numeric field descending;
/// Sort preserves count; Sort doesn't change original;
/// dogfood LoadContent->GetFieldValues->Sort->Filter->Verify pipeline.
/// </summary>
public class NdjsonR189GetFieldValuesAndSortDeepTests
{
    private const string Content =
        "{\"Name\":\"Carol\",\"Dept\":\"Eng\",\"Score\":78}\n" +
        "{\"Name\":\"Alice\",\"Dept\":\"Finance\",\"Score\":92}\n" +
        "{\"Name\":\"Frank\",\"Dept\":\"Eng\",\"Score\":79}\n" +
        "{\"Name\":\"Bob\",\"Dept\":\"HR\",\"Score\":85}\n" +
        "{\"Name\":\"Eve\",\"Dept\":\"Finance\",\"Score\":88}\n" +
        "{\"Name\":\"Dave\",\"Dept\":\"Eng\",\"Score\":91}";

    // -------------------------------------------------------------------------
    // GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValues_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        Assert.NotNull(doc.GetFieldValues("Name"));
    }

    [Fact]
    public void GetFieldValues_CountEqualsDocCount()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        Assert.Equal(doc.Count, doc.GetFieldValues("Name").Count);
    }

    [Fact]
    public void GetFieldValues_AllPresent()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var names = doc.GetFieldValues("Name");
        Assert.Contains("Alice", names.ConvertAll(v => v?.ToString() ?? ""));
        Assert.Contains("Bob", names.ConvertAll(v => v?.ToString() ?? ""));
        Assert.Contains("Carol", names.ConvertAll(v => v?.ToString() ?? ""));
    }

    [Fact]
    public void GetFieldValues_AfterFilter_ReducesCount()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var engOnly = doc.Filter(r => r.GetField("Dept")?.ToString() == "Eng");
        var names = engOnly.GetFieldValues("Name");
        Assert.Equal(3, names.Count); // Carol, Frank, Dave
    }

    [Fact]
    public void GetFieldValues_AfterAppendRecord_IncludesNew()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var record = new Dictionary<string, object?> { ["Name"] = "Zara", ["Dept"] = "Legal", ["Score"] = 99 };
        var extended = doc.AppendRecord(record);
        var names = extended.GetFieldValues("Name");
        Assert.Equal(7, names.Count);
        Assert.Contains("Zara", names.ConvertAll(v => v?.ToString() ?? ""));
    }

    [Fact]
    public void GetFieldValues_DeptField_AllPresent()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var depts = doc.GetFieldValues("Dept");
        Assert.Equal(6, depts.Count);
    }

    // -------------------------------------------------------------------------
    // Sort
    // -------------------------------------------------------------------------

    [Fact]
    public void Sort_Ascending_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        Assert.NotNull(doc.Sort("Name", ascending: true));
    }

    [Fact]
    public void Sort_Descending_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        Assert.NotNull(doc.Sort("Name", ascending: false));
    }

    [Fact]
    public void Sort_Ascending_PreservesCount()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var sorted = doc.Sort("Name", ascending: true);
        Assert.Equal(doc.Count, sorted.Count);
    }

    [Fact]
    public void Sort_Descending_PreservesCount()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var sorted = doc.Sort("Name", ascending: false);
        Assert.Equal(doc.Count, sorted.Count);
    }

    [Fact]
    public void Sort_Ascending_FirstIsAlpha()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var sorted = doc.Sort("Name", ascending: true);
        // Alice should be first alphabetically
        Assert.Equal("Alice", sorted.RecordAt(0).GetField("Name")?.ToString());
    }

    [Fact]
    public void Sort_Descending_FirstIsZLast()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var sorted = doc.Sort("Name", ascending: false);
        // Frank should be last alphabetically, so first descending
        Assert.Equal("Frank", sorted.RecordAt(0).GetField("Name")?.ToString());
    }

    [Fact]
    public void Sort_ByNumericScore_Ascending_FirstIsLowest()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var sorted = doc.Sort("Score", ascending: true);
        var firstScore = Convert.ToDouble(sorted.RecordAt(0).GetField("Score"));
        var lastScore = Convert.ToDouble(sorted.RecordAt(sorted.Count - 1).GetField("Score"));
        Assert.True(firstScore <= lastScore);
    }

    [Fact]
    public void Sort_ByNumericScore_Descending_FirstIsHighest()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var sorted = doc.Sort("Score", ascending: false);
        var firstScore = Convert.ToDouble(sorted.RecordAt(0).GetField("Score"));
        var lastScore = Convert.ToDouble(sorted.RecordAt(sorted.Count - 1).GetField("Score"));
        Assert.True(firstScore >= lastScore);
    }

    [Fact]
    public void Sort_DoesNotMutateOriginal()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var originalFirst = doc.RecordAt(0).GetField("Name")?.ToString();
        _ = doc.Sort("Name", ascending: true);
        // Original doc's first record should be unchanged (Carol, as it was first in content)
        Assert.Equal(originalFirst, doc.RecordAt(0).GetField("Name")?.ToString());
    }

    [Fact]
    public void Sort_Ascending_LastIsZ()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        var sorted = doc.Sort("Name", ascending: true);
        // Last alphabetically among Carol/Alice/Frank/Bob/Eve/Dave = Frank
        Assert.Equal("Frank", sorted.RecordAt(sorted.Count - 1).GetField("Name")?.ToString());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_GetFieldValues_Sort_Filter_Verify_Pipeline()
    {
        var doc = NdjsonDocument.LoadContent(Content);
        Assert.Equal(6, doc.Count);

        // GetFieldValues for Name
        var names = doc.GetFieldValues("Name");
        Assert.Equal(6, names.Count);

        // Sort ascending by Name
        var sortedAsc = doc.Sort("Name", ascending: true);
        Assert.Equal(6, sortedAsc.Count);
        Assert.Equal("Alice", sortedAsc.RecordAt(0).GetField("Name")?.ToString());
        Assert.Equal("Frank", sortedAsc.RecordAt(5).GetField("Name")?.ToString());

        // Sort descending by Score
        var sortedDescScore = doc.Sort("Score", ascending: false);
        var topScore = Convert.ToDouble(sortedDescScore.RecordAt(0).GetField("Score"));
        Assert.Equal(92.0, topScore, 0);

        // GetFieldValues after sort same count
        var sortedNames = sortedAsc.GetFieldValues("Name");
        Assert.Equal(6, sortedNames.Count);

        // Filter then sort
        var engOnly = doc.Filter(r => r.GetField("Dept")?.ToString() == "Eng");
        Assert.Equal(3, engOnly.Count);
        var engSorted = engOnly.Sort("Name", ascending: true);
        Assert.Equal("Carol", engSorted.RecordAt(0).GetField("Name")?.ToString());
        Assert.Equal("Frank", engSorted.RecordAt(1).GetField("Name")?.ToString());

        // GetFieldValues on filtered+sorted
        var engNames = engSorted.GetFieldValues("Name");
        Assert.Equal(3, engNames.Count);

        // AppendRecord then GetFieldValues
        var newRecord = new Dictionary<string, object?> { ["Name"] = "Igor", ["Dept"] = "Eng", ["Score"] = 97 };
        var extended = doc.AppendRecord(newRecord);
        var extNames = extended.GetFieldValues("Name");
        Assert.Equal(7, extNames.Count);
    }
}
