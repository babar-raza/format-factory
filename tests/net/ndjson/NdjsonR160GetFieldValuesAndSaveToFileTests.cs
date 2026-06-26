// Tests for NdjsonDocument.GetFieldValues, SaveToFile, LoadContent, ToNdjson.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R160

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R160: Tests for NdjsonDocument.GetFieldValues, SaveToFile, LoadContent round-trips.
/// GetFieldValues(key): extracts all values for a given key as string list.
/// SaveToFile(path): writes NDJSON to disk.
/// LoadContent/LoadFile: reads NDJSON from disk or string.
/// Covers: GetFieldValues count equals record count; GetFieldValues contains expected values;
/// GetFieldValues for numeric field; GetFieldValues missing key returns empty;
/// SaveToFile creates file; SaveToFile->LoadFile count matches;
/// SaveToFile->LoadFile->GetFieldValues matches original;
/// Filter->SaveToFile->LoadFile->GetFieldValues subset;
/// LoadContent returns same count; ToNdjson is non-empty string;
/// ToNdjson->Load->Count matches; GetFieldValues on filtered doc;
/// Filter->GetFieldValues count matches filter count;
/// dogfood Load->GetFieldValues->Filter->SaveToFile->LoadFile->GetFieldValues.
/// </summary>
public class NdjsonR160GetFieldValuesAndSaveToFileTests : IDisposable
{
    private readonly string _tempDir;

    private const string FourRecordNdjson =
        "{\"name\":\"Alice\",\"score\":95,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Bob\",\"score\":82,\"dept\":\"Finance\"}\n" +
        "{\"name\":\"Carol\",\"score\":88,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Dave\",\"score\":91,\"dept\":\"Finance\"}";

    public NdjsonR160GetFieldValuesAndSaveToFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR160_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValues_Name_CountEqualsRecordCount()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var names = doc.GetFieldValues("name");
        Assert.Equal(4, names.Count);
    }

    [Fact]
    public void GetFieldValues_Name_ContainsExpectedValues()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void GetFieldValues_NumericField_ReturnsStringValues()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var scores = doc.GetFieldValues("score");
        Assert.Equal(4, scores.Count);
        Assert.Contains("95", scores);
    }

    [Fact]
    public void GetFieldValues_MissingKey_ReturnsEmpty()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var vals = doc.GetFieldValues("nonexistent_field_xyz");
        Assert.Empty(vals);
    }

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var path = TempFile("out.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_LoadFile_CountMatches()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var path = TempFile("rt.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.Count, loaded.Count);
    }

    [Fact]
    public void SaveToFile_LoadFile_GetFieldValues_Matches()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var path = TempFile("gfv.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var names = loaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void Filter_SaveToFile_LoadFile_GetFieldValues_Subset()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var path = TempFile("eng.ndjson");
        eng.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var names = loaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
        Assert.DoesNotContain("Dave", names);
    }

    // -------------------------------------------------------------------------
    // ToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_IsNonEmptyString()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var s = doc.ToNdjson();
        Assert.False(string.IsNullOrEmpty(s));
    }

    [Fact]
    public void ToNdjson_Load_CountMatches()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var s = doc.ToNdjson();
        var loaded = NdjsonDocument.Load(s);
        Assert.Equal(4, loaded.Count);
    }

    // -------------------------------------------------------------------------
    // GetFieldValues on filtered
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValues_OnFilteredDoc_CountMatchesFilter()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var finance = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Finance");
        var names = finance.GetFieldValues("name");
        Assert.Equal(2, names.Count);
    }

    [Fact]
    public void Filter_GetFieldValues_CountMatchesFilterCount()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var depts = eng.GetFieldValues("dept");
        Assert.Equal(eng.Count, depts.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetFieldValues->Filter->SaveToFile->LoadFile->GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldValuesFilterSaveLoadGetFieldValues_Pipeline()
    {
        var doc = NdjsonDocument.Load(FourRecordNdjson);
        Assert.Equal(4, doc.Count);

        // GetFieldValues all names
        var allNames = doc.GetFieldValues("name");
        Assert.Equal(4, allNames.Count);

        // Filter Finance
        var finance = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Finance");
        Assert.Equal(2, finance.Count);

        // SaveToFile
        var path = TempFile("dogfood.ndjson");
        finance.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, loaded.Count);

        // GetFieldValues on loaded
        var financeNames = loaded.GetFieldValues("name");
        Assert.Contains("Bob", financeNames);
        Assert.Contains("Dave", financeNames);
        Assert.DoesNotContain("Alice", financeNames);

        // Scores of finance members
        var scores = loaded.GetFieldValues("score");
        Assert.Equal(2, scores.Count);
        Assert.Contains("82", scores);
        Assert.Contains("91", scores);
    }
}
