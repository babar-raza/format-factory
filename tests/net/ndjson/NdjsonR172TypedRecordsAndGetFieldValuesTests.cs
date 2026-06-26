// Tests for NdjsonDocument.TypedRecords, GetFieldValues, GetAllKeys deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R172

using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R172: Tests for NdjsonDocument.TypedRecords, GetFieldValues, GetAllKeys deeper.
/// TypedRecords: list of NdjsonRecord providing typed access to fields.
/// GetFieldValues(fieldName): returns all values for a field across records.
/// GetAllKeys(): returns union of all field names across records.
/// NdjsonRecord.TryGetString(key, out value): typed string access.
/// NdjsonRecord.TryGetInt(key, out value): typed int access.
/// Covers: TypedRecords count matches Count; TypedRecords first record non-null;
/// TypedRecords TryGetString returns correct value; TypedRecords TryGetInt returns value;
/// TypedRecords TryGetString for missing key returns false;
/// GetFieldValues count matches record count; GetFieldValues contains all values;
/// GetFieldValues for missing field returns empty; GetAllKeys non-empty;
/// GetAllKeys contains known field names; GetAllKeys count matches schema;
/// TypedRecords after Filter count reduced; GetFieldValues after Filter filtered;
/// GetAllKeys on uniform schema stable;
/// dogfood Load->TypedRecords->GetFieldValues->GetAllKeys->Filter->TypedRecords verify.
/// </summary>
public class NdjsonR172TypedRecordsAndGetFieldValuesTests
{
    private const string ThreeRecordNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Eng\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Eng\",\"score\":88}";

    // -------------------------------------------------------------------------
    // TypedRecords
    // -------------------------------------------------------------------------

    [Fact]
    public void TypedRecords_CountMatchesDocCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(doc.Count, doc.TypedRecords.Count);
    }

    [Fact]
    public void TypedRecords_FirstRecord_NonNull()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.NotNull(doc.TypedRecords[0]);
    }

    [Fact]
    public void TypedRecords_TryGetString_Name_Correct()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.True(doc.TypedRecords[0].TryGetString("name", out var name));
        Assert.Equal("Alice", name);
    }

    [Fact]
    public void TypedRecords_TryGetString_Dept_Correct()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.True(doc.TypedRecords[1].TryGetString("dept", out var dept));
        Assert.Equal("Finance", dept);
    }

    [Fact]
    public void TypedRecords_TryGetInt_Score_Correct()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.True(doc.TypedRecords[0].TryGetInt("score", out var score));
        Assert.Equal(95, score);
    }

    [Fact]
    public void TypedRecords_TryGetString_MissingKey_ReturnsFalse()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.False(doc.TypedRecords[0].TryGetString("nonexistent", out _));
    }

    [Fact]
    public void TypedRecords_AllRecords_HaveNameField()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        foreach (var r in doc.TypedRecords)
            Assert.True(r.TryGetString("name", out _));
    }

    [Fact]
    public void TypedRecords_AfterFilter_CountReduced()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.TypedRecords.Count);
    }

    // -------------------------------------------------------------------------
    // GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValues_CountMatchesRecordCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var names = doc.GetFieldValues("name");
        Assert.Equal(3, names.Count);
    }

    [Fact]
    public void GetFieldValues_ContainsAllValues()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void GetFieldValues_ForMissingField_ReturnsEmpty()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var vals = doc.GetFieldValues("nonexistent");
        Assert.Empty(vals);
    }

    [Fact]
    public void GetFieldValues_AfterFilter_Reduced()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var names = eng.GetFieldValues("name");
        Assert.Equal(2, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }

    // -------------------------------------------------------------------------
    // GetAllKeys
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_NonEmpty()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var keys = doc.GetAllKeys();
        Assert.NotEmpty(keys);
    }

    [Fact]
    public void GetAllKeys_ContainsNameKey()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
    }

    [Fact]
    public void GetAllKeys_ContainsAllSchemaKeys()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.Contains("score", keys);
    }

    [Fact]
    public void GetAllKeys_OnUniformSchema_Stable()
    {
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        var keys1 = doc.GetAllKeys();
        var keys2 = doc.GetAllKeys();
        Assert.Equal(keys1.Count, keys2.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadTypedRecordsGetFieldValuesGetAllKeysFilterTypedVerify_Pipeline()
    {
        // Load
        var doc = NdjsonDocument.Load(ThreeRecordNdjson);
        Assert.Equal(3, doc.Count);

        // TypedRecords
        var typed = doc.TypedRecords;
        Assert.Equal(3, typed.Count);
        Assert.True(typed[0].TryGetString("name", out var firstName));
        Assert.Equal("Alice", firstName);
        Assert.True(typed[2].TryGetInt("score", out var lastScore));
        Assert.Equal(88, lastScore);

        // GetFieldValues
        var names = doc.GetFieldValues("name");
        Assert.Equal(3, names.Count);

        // GetAllKeys
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count); // name, dept, score
        Assert.Contains("dept", keys);

        // Filter
        var eng = doc.Filter(el => el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // TypedRecords after filter
        var engTyped = eng.TypedRecords;
        Assert.Equal(2, engTyped.Count);
        Assert.True(engTyped[0].TryGetString("name", out var engName));
        Assert.Equal("Alice", engName);

        // GetFieldValues after filter
        var engNames = eng.GetFieldValues("name");
        Assert.DoesNotContain("Bob", engNames);
    }
}
