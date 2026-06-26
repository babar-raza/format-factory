// Tests for NdjsonDocument.ToList, GetRecord, WriteToStream deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R210

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R210: Tests for NdjsonDocument.ToList, GetRecord, WriteToStream deeper.
/// ToList(): returns all records as a list of dictionaries.
/// GetRecord(index): returns the record at the specified index.
/// WriteToStream(stream): writes the document to a stream.
/// Covers: ToList non-null; ToList non-empty; ToList count=recordCount; ToList consistent;
/// ToList contains known records; ToList no-throw; ToList after AppendRecord grows;
/// ToList after DeleteRecord shrinks; ToList after Filter shrinks; ToList each has fields;
/// GetRecord non-null; GetRecord has fields; GetRecord correct for index 0; GetRecord correct for last;
/// GetRecord consistent; GetRecord no-throw; GetRecord after AppendRecord; GetRecord after DeleteRecord shifts;
/// GetRecord after Filter correct; GetRecord returns dict;
/// WriteToStream no-throw; WriteToStream stream non-empty; WriteToStream produces parseable ndjson;
/// WriteToStream consistent; WriteToStream then LoadFile roundtrip;
/// dogfood CreateDoc→ToList→GetRecord→WriteToStream→LoadFile pipeline.
/// </summary>
public class NdjsonR210ToListAndGetRecordDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR210ToListAndGetRecordDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR210_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NdjsonDocument CreateBaseDoc()
    {
        var doc = NdjsonDocument.CreateNew();
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 1, ["name"] = "Alice", ["dept"] = "Engineering", ["score"] = 92 });
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 2, ["name"] = "Bob", ["dept"] = "Marketing", ["score"] = 78 });
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 3, ["name"] = "Carol", ["dept"] = "Engineering", ["score"] = 88 });
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 4, ["name"] = "Dave", ["dept"] = "Finance", ["score"] = 85 });
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 5, ["name"] = "Eve", ["dept"] = "Engineering", ["score"] = 95 });
        return doc;
    }

    // -------------------------------------------------------------------------
    // ToList
    // -------------------------------------------------------------------------

    [Fact]
    public void ToList_NonNull()
    {
        var doc = CreateBaseDoc();
        Assert.NotNull(doc.ToList());
    }

    [Fact]
    public void ToList_NonEmpty()
    {
        var doc = CreateBaseDoc();
        Assert.True(doc.ToList().Count > 0);
    }

    [Fact]
    public void ToList_CountEqualsRecordCount()
    {
        var doc = CreateBaseDoc();
        Assert.Equal(doc.GetRecordCount(), doc.ToList().Count);
    }

    [Fact]
    public void ToList_Consistent()
    {
        var doc = CreateBaseDoc();
        Assert.Equal(doc.ToList().Count, doc.ToList().Count);
    }

    [Fact]
    public void ToList_NoThrow()
    {
        var doc = CreateBaseDoc();
        var ex = Record.Exception(() => doc.ToList());
        Assert.Null(ex);
    }

    [Fact]
    public void ToList_AfterAppendRecord_Grows()
    {
        var doc = CreateBaseDoc();
        var before = doc.ToList().Count;
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 6, ["name"] = "Frank", ["dept"] = "HR", ["score"] = 80 });
        Assert.Equal(before + 1, doc.ToList().Count);
    }

    [Fact]
    public void ToList_AfterDeleteRecord_Shrinks()
    {
        var doc = CreateBaseDoc();
        var before = doc.ToList().Count;
        doc.DeleteRecord(0);
        Assert.Equal(before - 1, doc.ToList().Count);
    }

    [Fact]
    public void ToList_AfterFilter_Shrinks()
    {
        var doc = CreateBaseDoc();
        var before = doc.ToList().Count;
        var filtered = doc.Filter("dept", "Engineering");
        Assert.True(filtered.ToList().Count < before);
    }

    [Fact]
    public void ToList_EachRecord_HasFields()
    {
        var doc = CreateBaseDoc();
        foreach (var record in doc.ToList())
        {
            Assert.NotNull(record);
            Assert.True(record.Count > 0);
        }
    }

    [Fact]
    public void ToList_ContainsKnownData()
    {
        var doc = CreateBaseDoc();
        var list = doc.ToList();
        Assert.True(list.Exists(r => r.ContainsKey("name") && r["name"].ToString() == "Alice"));
    }

    // -------------------------------------------------------------------------
    // GetRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecord_NonNull()
    {
        var doc = CreateBaseDoc();
        Assert.NotNull(doc.GetRecord(0));
    }

    [Fact]
    public void GetRecord_HasFields()
    {
        var doc = CreateBaseDoc();
        var record = doc.GetRecord(0);
        Assert.True(record.Count > 0);
    }

    [Fact]
    public void GetRecord_CorrectForIndex0()
    {
        var doc = CreateBaseDoc();
        var record = doc.GetRecord(0);
        Assert.True(record.ContainsKey("name"));
        Assert.Equal("Alice", record["name"].ToString());
    }

    [Fact]
    public void GetRecord_CorrectForLast()
    {
        var doc = CreateBaseDoc();
        var last = doc.GetRecord(doc.GetRecordCount() - 1);
        Assert.True(last.ContainsKey("name"));
        Assert.Equal("Eve", last["name"].ToString());
    }

    [Fact]
    public void GetRecord_Consistent()
    {
        var doc = CreateBaseDoc();
        var r1 = doc.GetRecord(0);
        var r2 = doc.GetRecord(0);
        Assert.Equal(r1["name"].ToString(), r2["name"].ToString());
    }

    [Fact]
    public void GetRecord_NoThrow()
    {
        var doc = CreateBaseDoc();
        var ex = Record.Exception(() => doc.GetRecord(2));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecord_AfterAppendRecord_NewAccessible()
    {
        var doc = CreateBaseDoc();
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 6, ["name"] = "Frank", ["dept"] = "HR", ["score"] = 80 });
        var last = doc.GetRecord(doc.GetRecordCount() - 1);
        Assert.Equal("Frank", last["name"].ToString());
    }

    [Fact]
    public void GetRecord_AfterDeleteRecord_NewIndex0()
    {
        var doc = CreateBaseDoc();
        doc.DeleteRecord(0); // Remove Alice
        var newFirst = doc.GetRecord(0);
        Assert.Equal("Bob", newFirst["name"].ToString());
    }

    [Fact]
    public void GetRecord_AfterFilter_CorrectRecord()
    {
        var doc = CreateBaseDoc();
        var filtered = doc.Filter("dept", "Engineering");
        var first = filtered.GetRecord(0);
        Assert.Equal("Engineering", first["dept"].ToString());
    }

    [Fact]
    public void GetRecord_ReturnsDict()
    {
        var doc = CreateBaseDoc();
        var record = doc.GetRecord(0);
        Assert.IsAssignableFrom<Dictionary<string, object>>(record);
    }

    // -------------------------------------------------------------------------
    // WriteToStream
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToStream_NoThrow()
    {
        var doc = CreateBaseDoc();
        using var ms = new MemoryStream();
        var ex = Record.Exception(() => doc.WriteToStream(ms));
        Assert.Null(ex);
    }

    [Fact]
    public void WriteToStream_StreamNonEmpty()
    {
        var doc = CreateBaseDoc();
        using var ms = new MemoryStream();
        doc.WriteToStream(ms);
        Assert.True(ms.Length > 0);
    }

    [Fact]
    public void WriteToStream_ProducesNdjson()
    {
        var doc = CreateBaseDoc();
        using var ms = new MemoryStream();
        doc.WriteToStream(ms);
        ms.Position = 0;
        var content = new StreamReader(ms).ReadToEnd();
        Assert.Contains("{", content);
        Assert.Contains("Alice", content);
    }

    [Fact]
    public void WriteToStream_Consistent()
    {
        var doc = CreateBaseDoc();
        using var ms1 = new MemoryStream();
        using var ms2 = new MemoryStream();
        doc.WriteToStream(ms1);
        doc.WriteToStream(ms2);
        Assert.Equal(ms1.Length, ms2.Length);
    }

    [Fact]
    public void WriteToStream_ThenLoadFile_Roundtrip()
    {
        var doc = CreateBaseDoc();
        var path = TempFile("stream_roundtrip.ndjson");
        using (var fs = File.OpenWrite(path))
            doc.WriteToStream(fs);
        Assert.True(File.Exists(path));
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.GetRecordCount(), loaded.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ToList_GetRecord_WriteToStream_LoadFile_Pipeline()
    {
        // Build document
        var doc = NdjsonDocument.CreateNew();
        var data = new[]
        {
            new Dictionary<string, object> { ["id"] = 1, ["product"] = "Alpha", ["type"] = "Hardware", ["qty"] = 50, ["price"] = 12.99 },
            new Dictionary<string, object> { ["id"] = 2, ["product"] = "Beta", ["type"] = "Software", ["qty"] = 200, ["price"] = 49.99 },
            new Dictionary<string, object> { ["id"] = 3, ["product"] = "Gamma", ["type"] = "Hardware", ["qty"] = 75, ["price"] = 8.99 },
            new Dictionary<string, object> { ["id"] = 4, ["product"] = "Delta", ["type"] = "Service", ["qty"] = 1, ["price"] = 999.99 },
            new Dictionary<string, object> { ["id"] = 5, ["product"] = "Epsilon", ["type"] = "Software", ["qty"] = 100, ["price"] = 29.99 },
            new Dictionary<string, object> { ["id"] = 6, ["product"] = "Zeta", ["type"] = "Hardware", ["qty"] = 30, ["price"] = 15.99 },
        };
        foreach (var r in data) doc.AppendRecord(r);
        Assert.Equal(6, doc.GetRecordCount());

        // ToList baseline
        var list = doc.ToList();
        Assert.NotNull(list);
        Assert.Equal(6, list.Count);
        Assert.True(list.Exists(r => r["product"].ToString() == "Alpha"));
        Assert.True(list.Exists(r => r["product"].ToString() == "Zeta"));

        // GetRecord baseline
        var rec0 = doc.GetRecord(0);
        Assert.Equal("Alpha", rec0["product"].ToString());
        Assert.Equal("Hardware", rec0["type"].ToString());

        var rec5 = doc.GetRecord(5);
        Assert.Equal("Zeta", rec5["product"].ToString());

        // WriteToStream
        var path1 = TempFile("stream_output.ndjson");
        using (var fs = File.OpenWrite(path1))
            doc.WriteToStream(fs);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile from stream output
        var loadedFromStream = NdjsonDocument.LoadFile(path1);
        Assert.Equal(6, loadedFromStream.GetRecordCount());

        // ToList on loaded
        var loadedList = loadedFromStream.ToList();
        Assert.Equal(6, loadedList.Count);

        // GetRecord on loaded
        var loadedRec0 = loadedFromStream.GetRecord(0);
        Assert.Equal("Alpha", loadedRec0["product"].ToString());

        // AppendRecord and verify ToList grows
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 7, ["product"] = "Eta", ["type"] = "Service", ["qty"] = 2, ["price"] = 499.99 });
        Assert.Equal(7, doc.GetRecordCount());
        Assert.Equal(7, doc.ToList().Count);

        // GetRecord for new record
        var newRec = doc.GetRecord(6);
        Assert.Equal("Eta", newRec["product"].ToString());

        // DeleteRecord and verify ToList shrinks
        doc.DeleteRecord(0); // Remove Alpha
        Assert.Equal(6, doc.GetRecordCount());
        Assert.Equal(6, doc.ToList().Count);

        // GetRecord after delete
        var newRec0 = doc.GetRecord(0);
        Assert.Equal("Beta", newRec0["product"].ToString());

        // Filter Software
        var software = doc.Filter("type", "Software");
        var softList = software.ToList();
        Assert.NotNull(softList);
        Assert.True(softList.Count < doc.GetRecordCount());
        foreach (var r in softList)
            Assert.Equal("Software", r["type"].ToString());

        // GetRecord on filtered
        var softRec0 = software.GetRecord(0);
        Assert.Equal("Software", softRec0["type"].ToString());

        // WriteToStream on filtered
        using var filterMs = new MemoryStream();
        software.WriteToStream(filterMs);
        Assert.True(filterMs.Length > 0);

        // WriteToStream consistent
        using var ms1 = new MemoryStream();
        using var ms2 = new MemoryStream();
        doc.WriteToStream(ms1);
        doc.WriteToStream(ms2);
        Assert.Equal(ms1.Length, ms2.Length);

        // WriteToFile and verify matches WriteToStream
        var path2 = TempFile("write_to_file.ndjson");
        doc.WriteToFile(path2);
        var fileSize = new FileInfo(path2).Length;

        using var ms3 = new MemoryStream();
        doc.WriteToStream(ms3);
        // Stream and file should produce similar sizes
        Assert.True(Math.Abs(ms3.Length - fileSize) <= 10);

        // ToList consistent
        var tl1 = doc.ToList();
        var tl2 = doc.ToList();
        Assert.Equal(tl1.Count, tl2.Count);

        // Final WriteToStream
        var path3 = TempFile("final_stream.ndjson");
        using (var fs = File.OpenWrite(path3))
            doc.WriteToStream(fs);
        var final = NdjsonDocument.LoadFile(path3);
        Assert.Equal(doc.GetRecordCount(), final.GetRecordCount());
        Assert.Equal(6, final.ToList().Count);
    }
}
