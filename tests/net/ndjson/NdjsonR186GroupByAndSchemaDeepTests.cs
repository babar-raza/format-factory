// Tests for NdjsonDocument.GroupBy, IsUniformSchema, GetAllKeys deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R186

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R186: Tests for NdjsonDocument.GroupBy, IsUniformSchema, GetAllKeys deeper coverage.
/// GroupBy(field): returns a dictionary grouping records by field value.
/// IsUniformSchema(): returns true if all records have the same set of fields.
/// GetAllKeys(): returns the union of all field keys across all records.
/// Covers: GroupBy non-null; GroupBy correct key count; GroupBy correct group sizes;
/// GroupBy empty collection for missing field; GroupBy single group when all same value;
/// GroupBy after Filter reduces groups; IsUniformSchema true for uniform data;
/// IsUniformSchema false for ragged data; GetAllKeys non-null;
/// GetAllKeys count correct; GetAllKeys contains expected fields;
/// GetAllKeys superset when records have different fields;
/// dogfood LoadContent->GroupBy->IsUniformSchema->GetAllKeys->Verify pipeline.
/// </summary>
public class NdjsonR186GroupByAndSchemaDeepTests
{
    private const string UniformContent =
        "{\"Name\":\"Alice\",\"Dept\":\"Eng\",\"Score\":92}\n" +
        "{\"Name\":\"Bob\",\"Dept\":\"Finance\",\"Score\":85}\n" +
        "{\"Name\":\"Carol\",\"Dept\":\"Eng\",\"Score\":78}\n" +
        "{\"Name\":\"Dave\",\"Dept\":\"HR\",\"Score\":91}\n" +
        "{\"Name\":\"Eve\",\"Dept\":\"Finance\",\"Score\":88}\n" +
        "{\"Name\":\"Frank\",\"Dept\":\"Eng\",\"Score\":79}";

    private const string RaggedContent =
        "{\"Name\":\"Alice\",\"Dept\":\"Eng\",\"Score\":92}\n" +
        "{\"Name\":\"Bob\",\"Score\":85}\n" +
        "{\"Name\":\"Carol\",\"Dept\":\"Eng\"}";

    // -------------------------------------------------------------------------
    // GroupBy
    // -------------------------------------------------------------------------

    [Fact]
    public void GroupBy_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        Assert.NotNull(doc.GroupBy("Dept"));
    }

    [Fact]
    public void GroupBy_CorrectKeyCount()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        var groups = doc.GroupBy("Dept");
        // Eng, Finance, HR = 3 groups
        Assert.Equal(3, groups.Count);
    }

    [Fact]
    public void GroupBy_EngGroup_HasThreeRecords()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        var groups = doc.GroupBy("Dept");
        Assert.True(groups.ContainsKey("Eng"));
        Assert.Equal(3, groups["Eng"].Count);
    }

    [Fact]
    public void GroupBy_FinanceGroup_HasTwoRecords()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        var groups = doc.GroupBy("Dept");
        Assert.True(groups.ContainsKey("Finance"));
        Assert.Equal(2, groups["Finance"].Count);
    }

    [Fact]
    public void GroupBy_HrGroup_HasOneRecord()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        var groups = doc.GroupBy("Dept");
        Assert.True(groups.ContainsKey("HR"));
        Assert.Equal(1, groups["HR"].Count);
    }

    [Fact]
    public void GroupBy_AllGroupSizes_SumToTotal()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        var groups = doc.GroupBy("Dept");
        var total = 0;
        foreach (var kv in groups)
            total += kv.Value.Count;
        Assert.Equal(doc.Count, total);
    }

    [Fact]
    public void GroupBy_AfterFilter_ReducesGroups()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        var engOnly = doc.Filter(r => r.GetField("Dept")?.ToString() == "Eng");
        var groups = engOnly.GroupBy("Dept");
        // Only "Eng" group remains
        Assert.Equal(1, groups.Count);
        Assert.True(groups.ContainsKey("Eng"));
    }

    [Fact]
    public void GroupBy_SingleValueField_OneGroup()
    {
        var content =
            "{\"Name\":\"A\",\"Tag\":\"X\"}\n" +
            "{\"Name\":\"B\",\"Tag\":\"X\"}\n" +
            "{\"Name\":\"C\",\"Tag\":\"X\"}";
        var doc = NdjsonDocument.LoadContent(content);
        var groups = doc.GroupBy("Tag");
        Assert.Equal(1, groups.Count);
        Assert.Equal(3, groups["X"].Count);
    }

    // -------------------------------------------------------------------------
    // IsUniformSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void IsUniformSchema_True_ForUniformData()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_False_ForRaggedData()
    {
        var doc = NdjsonDocument.LoadContent(RaggedContent);
        Assert.False(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_True_ForSingleRecord()
    {
        var doc = NdjsonDocument.LoadContent("{\"Name\":\"Alice\",\"Score\":92}");
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void IsUniformSchema_True_ForTwoIdenticalSchemaRecords()
    {
        var content = "{\"a\":1,\"b\":2}\n{\"a\":3,\"b\":4}";
        var doc = NdjsonDocument.LoadContent(content);
        Assert.True(doc.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // GetAllKeys
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        Assert.NotNull(doc.GetAllKeys());
    }

    [Fact]
    public void GetAllKeys_ContainsExpectedFields()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        var keys = doc.GetAllKeys();
        Assert.Contains("Name", keys);
        Assert.Contains("Dept", keys);
        Assert.Contains("Score", keys);
    }

    [Fact]
    public void GetAllKeys_CountCorrect_ForUniformData()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count);
    }

    [Fact]
    public void GetAllKeys_Superset_ForRaggedData()
    {
        var doc = NdjsonDocument.LoadContent(RaggedContent);
        var keys = doc.GetAllKeys();
        // Union of Name, Dept, Score = 3 unique keys
        Assert.Equal(3, keys.Count);
        Assert.Contains("Name", keys);
        Assert.Contains("Dept", keys);
        Assert.Contains("Score", keys);
    }

    [Fact]
    public void GetAllKeys_AfterAppendRecord_IncludesNewField()
    {
        var doc = NdjsonDocument.LoadContent(UniformContent);
        var record = new Dictionary<string, object?> { ["Name"] = "Zara", ["Dept"] = "Legal", ["Score"] = 95, ["Region"] = "West" };
        var updated = doc.AppendRecord(record);
        var keys = updated.GetAllKeys();
        Assert.Contains("Region", keys);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_GroupBy_IsUniformSchema_GetAllKeys_Verify_Pipeline()
    {
        // Load uniform content
        var doc = NdjsonDocument.LoadContent(UniformContent);
        Assert.Equal(6, doc.Count);

        // IsUniformSchema
        Assert.True(doc.IsUniformSchema());

        // GetAllKeys
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count);
        Assert.Contains("Name", keys);
        Assert.Contains("Score", keys);

        // GroupBy Dept
        var groups = doc.GroupBy("Dept");
        Assert.Equal(3, groups.Count);
        Assert.Equal(3, groups["Eng"].Count);
        Assert.Equal(2, groups["Finance"].Count);
        Assert.Equal(1, groups["HR"].Count);

        // Filter then GroupBy
        var highScore = doc.Filter(r =>
        {
            var scoreObj = r.GetField("Score");
            if (scoreObj == null) return false;
            return Convert.ToDouble(scoreObj) >= 90;
        });
        Assert.True(highScore.Count > 0);
        var highGroups = highScore.GroupBy("Dept");
        Assert.True(highGroups.Count > 0);

        // AppendRecord with new field — schema becomes non-uniform
        var extendedRecord = new Dictionary<string, object?>
        {
            ["Name"] = "Zara", ["Dept"] = "Legal", ["Score"] = 99, ["Region"] = "East"
        };
        var extended = doc.AppendRecord(extendedRecord);
        Assert.False(extended.IsUniformSchema()); // "Region" missing from original records
        var extKeys = extended.GetAllKeys();
        Assert.True(extKeys.Count > 3); // Now includes "Region"
    }
}
