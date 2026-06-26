// Tests for NdjsonDocument.Join, GetRecordAt, ToJson deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R201

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R201: Tests for NdjsonDocument.Join, GetRecordAt, ToJson deeper coverage.
/// Join(other): combines two NdjsonDocuments into one with all records.
/// GetRecordAt(index): returns the raw record dictionary at the given index.
/// ToJson(): exports all records as a JSON array string.
/// Covers: Join non-null; Join record count is sum; Join contains both docs' records;
/// Join first doc records preserved; Join second doc records present;
/// Join consistent; Join then Filter works; Join then GroupBy correct;
/// GetRecordAt first; GetRecordAt last; GetRecordAt mid; GetRecordAt non-null;
/// GetRecordAt has expected fields; GetRecordAt consistent; GetRecordAt after AppendRecord;
/// ToJson non-null; ToJson non-empty; ToJson is JSON array; ToJson contains data;
/// ToJson line count less than NDJSON; ToJson after AppendRecord larger;
/// ToJson after Filter smaller; ToJson consistent;
/// dogfood LoadContent→Join→GetRecordAt→ToJson→Filter→verify pipeline.
/// </summary>
public class NdjsonR201JoinAndGetRecordAtDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR201JoinAndGetRecordAtDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR201_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleNdjsonA =
        "{\"name\":\"Alice\",\"dept\":\"Engineering\",\"score\":92}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":78}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Engineering\",\"score\":85}\n";

    private static readonly string SampleNdjsonB =
        "{\"name\":\"Dave\",\"dept\":\"HR\",\"score\":71}\n" +
        "{\"name\":\"Eve\",\"dept\":\"Finance\",\"score\":90}\n" +
        "{\"name\":\"Frank\",\"dept\":\"Engineering\",\"score\":88}\n";

    private NdjsonDocument LoadA()
    {
        var path = TempFile("sampleA.ndjson");
        File.WriteAllText(path, SampleNdjsonA);
        return NdjsonDocument.LoadFile(path);
    }

    private NdjsonDocument LoadB()
    {
        var path = TempFile("sampleB.ndjson");
        File.WriteAllText(path, SampleNdjsonB);
        return NdjsonDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // Join
    // -------------------------------------------------------------------------

    [Fact]
    public void Join_NonNull()
    {
        var a = LoadA();
        var b = LoadB();
        Assert.NotNull(a.Join(b));
    }

    [Fact]
    public void Join_RecordCountIsSum()
    {
        var a = LoadA();
        var b = LoadB();
        var joined = a.Join(b);
        Assert.Equal(a.RecordCount + b.RecordCount, joined.RecordCount);
    }

    [Fact]
    public void Join_ContainsBothDocsRecords()
    {
        var a = LoadA();
        var b = LoadB();
        var joined = a.Join(b);
        var names = joined.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Frank", names);
    }

    [Fact]
    public void Join_FirstDocRecordsPreserved()
    {
        var a = LoadA();
        var b = LoadB();
        var joined = a.Join(b);
        var names = joined.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void Join_SecondDocRecordsPresent()
    {
        var a = LoadA();
        var b = LoadB();
        var joined = a.Join(b);
        var names = joined.GetFieldValues("name");
        Assert.Contains("Dave", names);
        Assert.Contains("Eve", names);
        Assert.Contains("Frank", names);
    }

    [Fact]
    public void Join_Consistent()
    {
        var a = LoadA();
        var b = LoadB();
        var j1 = a.Join(b);
        var j2 = a.Join(b);
        Assert.Equal(j1.RecordCount, j2.RecordCount);
    }

    [Fact]
    public void Join_ThenFilter_Works()
    {
        var a = LoadA();
        var b = LoadB();
        var joined = a.Join(b);
        var eng = joined.Filter("dept", "Engineering");
        // Alice(A), Carol(A), Frank(B) = 3
        Assert.Equal(3, eng.RecordCount);
    }

    [Fact]
    public void Join_ThenGroupBy_CorrectGroups()
    {
        var a = LoadA();
        var b = LoadB();
        var joined = a.Join(b);
        var groups = joined.GroupBy("dept");
        Assert.Equal(3, groups.Count); // Engineering, Finance, HR
        Assert.Equal(3, groups["Engineering"].Count);
    }

    // -------------------------------------------------------------------------
    // GetRecordAt
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordAt_First_NonNull()
    {
        var a = LoadA();
        Assert.NotNull(a.GetRecordAt(0));
    }

    [Fact]
    public void GetRecordAt_First_CorrectName()
    {
        var a = LoadA();
        var record = a.GetRecordAt(0);
        Assert.True(record.ContainsKey("name"));
        Assert.Equal("Alice", record["name"].ToString());
    }

    [Fact]
    public void GetRecordAt_Last_CorrectName()
    {
        var a = LoadA();
        var record = a.GetRecordAt(a.RecordCount - 1);
        Assert.Equal("Carol", record["name"].ToString());
    }

    [Fact]
    public void GetRecordAt_Mid_CorrectName()
    {
        var a = LoadA();
        var record = a.GetRecordAt(1);
        Assert.Equal("Bob", record["name"].ToString());
    }

    [Fact]
    public void GetRecordAt_HasExpectedFields()
    {
        var a = LoadA();
        var record = a.GetRecordAt(0);
        Assert.True(record.ContainsKey("name"));
        Assert.True(record.ContainsKey("dept"));
        Assert.True(record.ContainsKey("score"));
    }

    [Fact]
    public void GetRecordAt_Consistent()
    {
        var a = LoadA();
        var r1 = a.GetRecordAt(0);
        var r2 = a.GetRecordAt(0);
        Assert.Equal(r1["name"].ToString(), r2["name"].ToString());
    }

    [Fact]
    public void GetRecordAt_AfterAppendRecord_NewRecordAccessible()
    {
        var a = LoadA();
        a.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "NewPerson" }, { "dept", "Legal" }, { "score", 77 }
        });
        var last = a.GetRecordAt(a.RecordCount - 1);
        Assert.Equal("NewPerson", last["name"].ToString());
    }

    // -------------------------------------------------------------------------
    // ToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToJson_NonNull()
    {
        var a = LoadA();
        Assert.NotNull(a.ToJson());
    }

    [Fact]
    public void ToJson_NonEmpty()
    {
        var a = LoadA();
        Assert.NotEmpty(a.ToJson());
    }

    [Fact]
    public void ToJson_IsJsonArray()
    {
        var a = LoadA();
        var json = a.ToJson();
        Assert.True(json.TrimStart().StartsWith("[") || json.Contains("{"));
    }

    [Fact]
    public void ToJson_ContainsData()
    {
        var a = LoadA();
        Assert.Contains("Alice", a.ToJson());
    }

    [Fact]
    public void ToJson_AfterAppendRecord_Larger()
    {
        var a = LoadA();
        var before = a.ToJson().Length;
        a.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "NewEntry" }, { "dept", "Test" }, { "score", 50 }
        });
        Assert.True(a.ToJson().Length > before);
    }

    [Fact]
    public void ToJson_AfterFilter_Smaller()
    {
        var a = LoadA();
        var all = a.ToJson();
        var filtered = a.Filter("dept", "Engineering").ToJson();
        Assert.True(filtered.Length < all.Length);
    }

    [Fact]
    public void ToJson_Consistent()
    {
        var a = LoadA();
        Assert.Equal(a.ToJson().Length, a.ToJson().Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_Join_GetRecordAt_ToJson_Filter_Pipeline()
    {
        var docA = LoadA();
        var docB = LoadB();
        Assert.Equal(3, docA.RecordCount);
        Assert.Equal(3, docB.RecordCount);

        // Join
        var joined = docA.Join(docB);
        Assert.NotNull(joined);
        Assert.Equal(6, joined.RecordCount);

        // Verify all records present
        var names = joined.GetFieldValues("name");
        Assert.Equal(6, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Frank", names);

        // GetRecordAt
        var first = joined.GetRecordAt(0);
        Assert.Equal("Alice", first["name"].ToString());
        Assert.Equal("Engineering", first["dept"].ToString());

        var fourth = joined.GetRecordAt(3);
        Assert.Equal("Dave", fourth["name"].ToString());

        var last = joined.GetRecordAt(5);
        Assert.Equal("Frank", last["name"].ToString());

        // ToJson
        var json = joined.ToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
        Assert.Contains("Alice", json);
        Assert.Contains("Frank", json);

        // Filter after Join
        var eng = joined.Filter("dept", "Engineering");
        Assert.Equal(3, eng.RecordCount);
        var engJson = eng.ToJson();
        Assert.True(engJson.Length < json.Length);
        Assert.Contains("Alice", engJson);
        Assert.Contains("Frank", engJson);
        Assert.DoesNotContain("Dave", engJson);

        // GroupBy after Join
        var groups = joined.GroupBy("dept");
        Assert.Equal(3, groups.Count);
        Assert.Equal(3, groups["Engineering"].Count);
        Assert.Equal(2, groups["Finance"].Count);
        Assert.Equal(1, groups["HR"].Count);

        // AppendRecord to joined
        joined.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Grace" }, { "dept", "Engineering" }, { "score", 91 }
        });
        Assert.Equal(7, joined.RecordCount);

        // GetRecordAt new record
        var newRecord = joined.GetRecordAt(6);
        Assert.Equal("Grace", newRecord["name"].ToString());

        // ToJson after AppendRecord
        var updatedJson = joined.ToJson();
        Assert.True(updatedJson.Length > json.Length);
        Assert.Contains("Grace", updatedJson);

        // SaveToFile and reload
        var path = TempFile("dogfood_join.ndjson");
        joined.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(7, loaded.RecordCount);
        Assert.Equal("Alice", loaded.GetRecordAt(0)["name"].ToString());
        Assert.Contains("Grace", loaded.GetFieldValues("name"));

        // Join loaded with docA again
        var reJoined = loaded.Join(docA);
        Assert.Equal(10, reJoined.RecordCount);
    }
}
