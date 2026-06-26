// Tests for NdjsonDocument.WriteToFile, LoadFile, Distinct deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R205

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R205: Tests for NdjsonDocument.WriteToFile, LoadFile, Distinct deeper.
/// WriteToFile(path): writes the document to a file in NDJSON format.
/// LoadFile(path): loads an NDJSON file into a NdjsonDocument.
/// Distinct(field): returns distinct values for a field across all records.
/// Covers: WriteToFile creates file; WriteToFile writes non-empty content;
/// WriteToFile then LoadFile round-trip; WriteToFile overwrites existing;
/// WriteToFile and LoadFile preserve record count; WriteToFile persist;
/// LoadFile non-null; LoadFile correct record count; LoadFile has expected fields;
/// LoadFile then Filter works; LoadFile then SortBy works;
/// Distinct non-null; Distinct non-empty; Distinct count correct;
/// Distinct contains known values; Distinct no duplicates; Distinct consistent;
/// Distinct after AppendRecord updates; Distinct for single-value field;
/// dogfood WriteToFile→LoadFile→Distinct→Filter→SaveToFile pipeline.
/// </summary>
public class NdjsonR205WriteToFileAndLoadFileDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR205WriteToFileAndLoadFileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR205_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Engineering\",\"score\":92}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":85}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Engineering\",\"score\":95}\n" +
        "{\"name\":\"Dave\",\"dept\":\"HR\",\"score\":78}\n" +
        "{\"name\":\"Eve\",\"dept\":\"Finance\",\"score\":88}\n";

    private NdjsonDocument LoadSample()
    {
        var path = TempFile("sample.ndjson");
        File.WriteAllText(path, SampleNdjson);
        return NdjsonDocument.LoadFile(path);
    }

    private static Dictionary<string, object> MakeRecord(string name, string dept, int score)
        => new Dictionary<string, object> { { "name", name }, { "dept", dept }, { "score", score } };

    // -------------------------------------------------------------------------
    // WriteToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_CreatesFile()
    {
        var doc = LoadSample();
        var path = TempFile("write_test.ndjson");
        doc.WriteToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_WritesNonEmptyContent()
    {
        var doc = LoadSample();
        var path = TempFile("write_content.ndjson");
        doc.WriteToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void WriteToFile_ThenLoadFile_RoundTrip()
    {
        var doc = LoadSample();
        var path = TempFile("write_rt.ndjson");
        doc.WriteToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void WriteToFile_OverwritesExisting()
    {
        var doc = LoadSample();
        var path = TempFile("write_overwrite.ndjson");
        doc.WriteToFile(path);
        doc.AppendRecord(MakeRecord("Frank", "IT", 90));
        doc.WriteToFile(path); // overwrite
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetRecordCount());
    }

    [Fact]
    public void WriteToFile_PreservesRecordCount()
    {
        var doc = LoadSample();
        var path = TempFile("write_count.ndjson");
        doc.WriteToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetRecordCount());
    }

    [Fact]
    public void WriteToFile_PreservesFieldValues()
    {
        var doc = LoadSample();
        var path = TempFile("write_values.ndjson");
        doc.WriteToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Contains("Alice", loaded.GetFieldValues("name"));
        Assert.Contains("Eve", loaded.GetFieldValues("name"));
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_NonNull()
    {
        var path = TempFile("load_test.ndjson");
        File.WriteAllText(path, SampleNdjson);
        Assert.NotNull(NdjsonDocument.LoadFile(path));
    }

    [Fact]
    public void LoadFile_CorrectRecordCount()
    {
        var path = TempFile("load_count.ndjson");
        File.WriteAllText(path, SampleNdjson);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(5, doc.GetRecordCount());
    }

    [Fact]
    public void LoadFile_HasExpectedFields()
    {
        var path = TempFile("load_fields.ndjson");
        File.WriteAllText(path, SampleNdjson);
        var doc = NdjsonDocument.LoadFile(path);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.Contains("score", keys);
    }

    [Fact]
    public void LoadFile_ThenFilter_Works()
    {
        var path = TempFile("load_filter.ndjson");
        File.WriteAllText(path, SampleNdjson);
        var doc = NdjsonDocument.LoadFile(path);
        var eng = doc.Filter("dept", "Engineering");
        Assert.Equal(2, eng.GetRecordCount());
    }

    [Fact]
    public void LoadFile_ThenSortBy_Works()
    {
        var path = TempFile("load_sort.ndjson");
        File.WriteAllText(path, SampleNdjson);
        var doc = NdjsonDocument.LoadFile(path);
        var sorted = doc.SortBy("name", ascending: true);
        Assert.Equal("Alice", sorted.GetFieldValues("name")[0]);
    }

    [Fact]
    public void LoadFile_Consistent()
    {
        var path = TempFile("load_consistent.ndjson");
        File.WriteAllText(path, SampleNdjson);
        var doc1 = NdjsonDocument.LoadFile(path);
        var doc2 = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc1.GetRecordCount(), doc2.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // Distinct
    // -------------------------------------------------------------------------

    [Fact]
    public void Distinct_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.Distinct("dept"));
    }

    [Fact]
    public void Distinct_NonEmpty()
    {
        var doc = LoadSample();
        Assert.True(doc.Distinct("dept").Count > 0);
    }

    [Fact]
    public void Distinct_CountCorrect()
    {
        var doc = LoadSample();
        // Engineering, Finance, HR = 3
        Assert.Equal(3, doc.Distinct("dept").Count);
    }

    [Fact]
    public void Distinct_ContainsKnownValues()
    {
        var doc = LoadSample();
        var distinct = doc.Distinct("dept");
        Assert.Contains("Engineering", distinct);
        Assert.Contains("Finance", distinct);
        Assert.Contains("HR", distinct);
    }

    [Fact]
    public void Distinct_NoDuplicates()
    {
        var doc = LoadSample();
        var distinct = doc.Distinct("dept");
        var set = new HashSet<string>(distinct);
        Assert.Equal(set.Count, distinct.Count);
    }

    [Fact]
    public void Distinct_Consistent()
    {
        var doc = LoadSample();
        var d1 = doc.Distinct("dept");
        var d2 = doc.Distinct("dept");
        Assert.Equal(d1.Count, d2.Count);
    }

    [Fact]
    public void Distinct_AfterAppendRecord_Updates()
    {
        var doc = LoadSample();
        var before = doc.Distinct("dept").Count;
        doc.AppendRecord(MakeRecord("Frank", "Legal", 91));
        var after = doc.Distinct("dept").Count;
        Assert.True(after > before);
    }

    [Fact]
    public void Distinct_ForAllUniqueNames_FiveValues()
    {
        var doc = LoadSample();
        // All 5 names are unique
        Assert.Equal(5, doc.Distinct("name").Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToFile_LoadFile_Distinct_Filter_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.GetRecordCount());

        // Distinct baseline
        var deptDistinct = doc.Distinct("dept");
        Assert.NotNull(deptDistinct);
        Assert.Equal(3, deptDistinct.Count);
        Assert.Contains("Engineering", deptDistinct);

        // WriteToFile
        var writePath = TempFile("dogfood_write.ndjson");
        doc.WriteToFile(writePath);
        Assert.True(File.Exists(writePath));

        // LoadFile
        var loaded = NdjsonDocument.LoadFile(writePath);
        Assert.NotNull(loaded);
        Assert.Equal(5, loaded.GetRecordCount());

        // Distinct on loaded
        var loadedDistinct = loaded.Distinct("dept");
        Assert.Equal(3, loadedDistinct.Count);

        // Filter on loaded
        var eng = loaded.Filter("dept", "Engineering");
        Assert.Equal(2, eng.GetRecordCount());

        // AppendRecord then WriteToFile
        doc.AppendRecord(MakeRecord("Frank", "Legal", 91));
        doc.AppendRecord(MakeRecord("Grace", "Engineering", 90));
        Assert.Equal(7, doc.GetRecordCount());

        // Distinct after append
        var deptAfter = doc.Distinct("dept");
        Assert.True(deptAfter.Count > deptDistinct.Count);
        Assert.Contains("Legal", deptAfter);

        // WriteToFile with new records
        doc.WriteToFile(writePath); // overwrite
        var loaded2 = NdjsonDocument.LoadFile(writePath);
        Assert.Equal(7, loaded2.GetRecordCount());

        // Distinct on loaded2
        var loadedDistinct2 = loaded2.Distinct("dept");
        Assert.Equal(deptAfter.Count, loadedDistinct2.Count);

        // SortBy then Distinct
        var sorted = doc.SortBy("name", ascending: true);
        var sortedDistinct = sorted.Distinct("dept");
        Assert.Equal(deptAfter.Count, sortedDistinct.Count);

        // Filter by new dept
        var legal = doc.Filter("dept", "Legal");
        Assert.Equal(1, legal.GetRecordCount());
        var legalDistinct = legal.Distinct("dept");
        Assert.Equal(1, legalDistinct.Count);

        // GroupBy and Distinct consistency
        var groups = doc.GroupBy("dept");
        Assert.Equal(deptAfter.Count, groups.Count);

        // SaveToFile
        var savePath = TempFile("dogfood_final.ndjson");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        var finalLoaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(7, finalLoaded.GetRecordCount());

        // WriteToFile and LoadFile on filtered
        var engPath = TempFile("engineering_only.ndjson");
        var engFiltered = finalLoaded.Filter("dept", "Engineering");
        engFiltered.WriteToFile(engPath);
        var loadedEng = NdjsonDocument.LoadFile(engPath);
        Assert.Equal(3, loadedEng.GetRecordCount()); // Alice, Carol, Grace
        Assert.Equal(1, loadedEng.Distinct("dept").Count);
    }
}
