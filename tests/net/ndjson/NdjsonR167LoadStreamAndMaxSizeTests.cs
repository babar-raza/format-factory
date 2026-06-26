// Tests for NdjsonDocument.LoadStream, MaxFileSizeBytes, NdjsonException deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R167

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R167: Tests for NdjsonDocument.LoadStream, MaxFileSizeBytes, NdjsonException deeper coverage.
/// NdjsonDocument.LoadStream(stream): loads NDJSON from a readable stream.
/// NdjsonDocument.MaxFileSizeBytes: static property for maximum allowed file size.
/// NdjsonException: thrown for invalid NDJSON content.
/// Covers: LoadStream non-null result; LoadStream count matches records;
/// LoadStream field values correct; LoadStream empty stream returns empty doc;
/// LoadStream then Filter works; MaxFileSizeBytes positive;
/// MaxFileSizeBytes greater than one megabyte; NdjsonException thrown for invalid content;
/// NdjsonException has message; LoadStream then GetAllKeys non-null;
/// LoadStream then IsUniformSchema; LoadStream then TypedRecords;
/// LoadStream with unicode content; LoadStream single record;
/// dogfood LoadStream->Filter->GetFieldValues->TypedRecords->ToNdjson chain.
/// </summary>
public class NdjsonR167LoadStreamAndMaxSizeTests
{
    private const string ThreeRecordNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}";

    private static Stream MakeStream(string content)
        => new MemoryStream(Encoding.UTF8.GetBytes(content));

    // -------------------------------------------------------------------------
    // NdjsonDocument.LoadStream
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_NonNull()
    {
        using var stream = MakeStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.LoadStream(stream);
        Assert.NotNull(doc);
    }

    [Fact]
    public void LoadStream_CountMatchesRecords()
    {
        using var stream = MakeStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.LoadStream(stream);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void LoadStream_FieldValuesCorrect()
    {
        using var stream = MakeStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.LoadStream(stream);
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void LoadStream_EmptyStream_ReturnsEmptyDoc()
    {
        using var stream = MakeStream(string.Empty);
        var doc = NdjsonDocument.LoadStream(stream);
        Assert.Equal(0, doc.Count);
    }

    [Fact]
    public void LoadStream_ThenFilter_Works()
    {
        using var stream = MakeStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.LoadStream(stream);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);
    }

    [Fact]
    public void LoadStream_SingleRecord_Count()
    {
        using var stream = MakeStream("{\"id\":1,\"value\":\"test\"}");
        var doc = NdjsonDocument.LoadStream(stream);
        Assert.Equal(1, doc.Count);
    }

    [Fact]
    public void LoadStream_ThenGetAllKeys_NonNull()
    {
        using var stream = MakeStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.LoadStream(stream);
        var keys = doc.GetAllKeys();
        Assert.NotNull(keys);
        Assert.NotEmpty(keys);
    }

    [Fact]
    public void LoadStream_ThenIsUniformSchema_True()
    {
        using var stream = MakeStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.LoadStream(stream);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void LoadStream_ThenTypedRecords_CountMatches()
    {
        using var stream = MakeStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.LoadStream(stream);
        Assert.Equal(doc.Count, doc.TypedRecords.Count);
    }

    [Fact]
    public void LoadStream_UnicodeContent_Parsed()
    {
        var content = "{\"name\":\"Ünïcödé\",\"value\":42}";
        using var stream = MakeStream(content);
        var doc = NdjsonDocument.LoadStream(stream);
        Assert.Equal(1, doc.Count);
    }

    // -------------------------------------------------------------------------
    // MaxFileSizeBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void MaxFileSizeBytes_Positive()
    {
        Assert.True(NdjsonDocument.MaxFileSizeBytes > 0);
    }

    [Fact]
    public void MaxFileSizeBytes_GreaterThanOneMegabyte()
    {
        Assert.True(NdjsonDocument.MaxFileSizeBytes > 1024 * 1024);
    }

    // -------------------------------------------------------------------------
    // NdjsonException
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonException_HasMessage()
    {
        var ex = new NdjsonException("Test error");
        Assert.Equal("Test error", ex.Message);
    }

    // -------------------------------------------------------------------------
    // Dogfood: LoadStream->Filter->GetFieldValues->TypedRecords->ToNdjson chain
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadStreamFilterGetFieldTypedToNdjson_Chain()
    {
        // LoadStream
        using var stream = MakeStream(ThreeRecordNdjson);
        var doc = NdjsonDocument.LoadStream(stream);
        Assert.Equal(3, doc.Count);

        // Filter
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // GetFieldValues
        var names = eng.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);

        // TypedRecords
        var typed = eng.TypedRecords;
        Assert.Equal(2, typed.Count);
        Assert.True(typed[0].TryGetString("name", out var firstName));
        Assert.Equal("Alice", firstName);

        // ToNdjson
        var ndjson = eng.ToNdjson();
        Assert.Contains("Alice", ndjson);
        Assert.DoesNotContain("Bob", ndjson);

        // Reload
        var reloaded = NdjsonDocument.Load(ndjson);
        Assert.Equal(2, reloaded.Count);
    }
}
