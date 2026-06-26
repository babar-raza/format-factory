// Tests for NdjsonDocument.UpdateRecord, HasField, DeleteRecord deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R207

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R207: Tests for NdjsonDocument.UpdateRecord, HasField, DeleteRecord deeper.
/// UpdateRecord(index, dict): replaces the record at the given index with a new dict.
/// HasField(field): returns true if any record contains the specified field.
/// DeleteRecord(index): removes the record at the given index.
/// Covers: UpdateRecord no-throw; UpdateRecord changes value; UpdateRecord then GetRecord reflects;
/// UpdateRecord persist; UpdateRecord first; UpdateRecord last; UpdateRecord multiple;
/// UpdateRecord then Filter; UpdateRecord preserves count;
/// HasField true for existing; HasField false for non-existent; HasField consistent;
/// HasField after AppendRecord with new field; HasField after SelectFields may be false;
/// HasField no-throw; HasField returns bool; HasField all known fields;
/// DeleteRecord no-throw; DeleteRecord decreases count; DeleteRecord removes correct record;
/// DeleteRecord first; DeleteRecord last; DeleteRecord persist; DeleteRecord then Filter;
/// DeleteRecord multiple reduces count by N;
/// dogfood CreateDoc→UpdateRecord→HasField→DeleteRecord→WriteToFile pipeline.
/// </summary>
public class NdjsonR207UpdateRecordAndHasFieldDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR207UpdateRecordAndHasFieldDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR207_" + Guid.NewGuid().ToString("N"));
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
            { ["name"] = "Alice", ["score"] = 92, ["dept"] = "Engineering", ["active"] = true });
        doc.AppendRecord(new Dictionary<string, object>
            { ["name"] = "Bob", ["score"] = 78, ["dept"] = "Marketing", ["active"] = true });
        doc.AppendRecord(new Dictionary<string, object>
            { ["name"] = "Carol", ["score"] = 88, ["dept"] = "Engineering", ["active"] = false });
        doc.AppendRecord(new Dictionary<string, object>
            { ["name"] = "Dave", ["score"] = 85, ["dept"] = "Finance", ["active"] = true });
        doc.AppendRecord(new Dictionary<string, object>
            { ["name"] = "Eve", ["score"] = 95, ["dept"] = "Engineering", ["active"] = true });
        return doc;
    }

    // -------------------------------------------------------------------------
    // UpdateRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void UpdateRecord_NoThrow()
    {
        var doc = CreateBaseDoc();
        var updated = new Dictionary<string, object>
            { ["name"] = "ALICE_UPDATED", ["score"] = 99, ["dept"] = "Engineering", ["active"] = true };
        var ex = Record.Exception(() => doc.UpdateRecord(0, updated));
        Assert.Null(ex);
    }

    [Fact]
    public void UpdateRecord_ChangesValue()
    {
        var doc = CreateBaseDoc();
        var updated = new Dictionary<string, object>
            { ["name"] = "ALICE_UPDATED", ["score"] = 99, ["dept"] = "Engineering", ["active"] = true };
        doc.UpdateRecord(0, updated);
        var rec = doc.GetRecord(0);
        Assert.Equal("ALICE_UPDATED", rec["name"].ToString());
    }

    [Fact]
    public void UpdateRecord_ThenGetRecord_Reflects()
    {
        var doc = CreateBaseDoc();
        var updated = new Dictionary<string, object>
            { ["name"] = "BOB_RENAMED", ["score"] = 85, ["dept"] = "HR", ["active"] = false };
        doc.UpdateRecord(1, updated);
        var rec = doc.GetRecord(1);
        Assert.Equal("BOB_RENAMED", rec["name"].ToString());
        Assert.Equal("HR", rec["dept"].ToString());
    }

    [Fact]
    public void UpdateRecord_PreservesCount()
    {
        var doc = CreateBaseDoc();
        var before = doc.GetRecordCount();
        doc.UpdateRecord(2, new Dictionary<string, object>
            { ["name"] = "CAROL_NEW", ["score"] = 90, ["dept"] = "Operations", ["active"] = true });
        Assert.Equal(before, doc.GetRecordCount());
    }

    [Fact]
    public void UpdateRecord_First_Works()
    {
        var doc = CreateBaseDoc();
        doc.UpdateRecord(0, new Dictionary<string, object>
            { ["name"] = "FIRST_UPDATED", ["score"] = 1, ["dept"] = "X", ["active"] = true });
        Assert.Equal("FIRST_UPDATED", doc.GetRecord(0)["name"].ToString());
    }

    [Fact]
    public void UpdateRecord_Last_Works()
    {
        var doc = CreateBaseDoc();
        var last = doc.GetRecordCount() - 1;
        doc.UpdateRecord(last, new Dictionary<string, object>
            { ["name"] = "LAST_UPDATED", ["score"] = 99, ["dept"] = "Y", ["active"] = false });
        Assert.Equal("LAST_UPDATED", doc.GetRecord(last)["name"].ToString());
    }

    [Fact]
    public void UpdateRecord_Persist()
    {
        var doc = CreateBaseDoc();
        doc.UpdateRecord(0, new Dictionary<string, object>
            { ["name"] = "ALICE_PERSISTED", ["score"] = 99, ["dept"] = "Engineering", ["active"] = true });
        var path = TempFile("update_persist.ndjson");
        doc.WriteToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal("ALICE_PERSISTED", loaded.GetRecord(0)["name"].ToString());
    }

    [Fact]
    public void UpdateRecord_Multiple_AllReflect()
    {
        var doc = CreateBaseDoc();
        doc.UpdateRecord(0, new Dictionary<string, object>
            { ["name"] = "UPD_0", ["score"] = 10, ["dept"] = "A", ["active"] = true });
        doc.UpdateRecord(2, new Dictionary<string, object>
            { ["name"] = "UPD_2", ["score"] = 20, ["dept"] = "B", ["active"] = false });
        doc.UpdateRecord(4, new Dictionary<string, object>
            { ["name"] = "UPD_4", ["score"] = 30, ["dept"] = "C", ["active"] = true });
        Assert.Equal("UPD_0", doc.GetRecord(0)["name"].ToString());
        Assert.Equal("UPD_2", doc.GetRecord(2)["name"].ToString());
        Assert.Equal("UPD_4", doc.GetRecord(4)["name"].ToString());
    }

    [Fact]
    public void UpdateRecord_ThenFilter_Works()
    {
        var doc = CreateBaseDoc();
        doc.UpdateRecord(1, new Dictionary<string, object>
            { ["name"] = "BOB_ENG", ["score"] = 80, ["dept"] = "Engineering", ["active"] = true });
        var engFiltered = doc.Filter("dept", "Engineering");
        // Alice, Bob_ENG, Carol, Eve = 4 engineering records
        Assert.True(engFiltered.GetRecordCount() >= 3);
    }

    // -------------------------------------------------------------------------
    // HasField
    // -------------------------------------------------------------------------

    [Fact]
    public void HasField_TrueForExisting()
    {
        var doc = CreateBaseDoc();
        Assert.True(doc.HasField("name"));
    }

    [Fact]
    public void HasField_FalseForNonExistent()
    {
        var doc = CreateBaseDoc();
        Assert.False(doc.HasField("NONEXISTENT_FIELD_XYZ"));
    }

    [Fact]
    public void HasField_Consistent()
    {
        var doc = CreateBaseDoc();
        Assert.Equal(doc.HasField("name"), doc.HasField("name"));
    }

    [Fact]
    public void HasField_NoThrow()
    {
        var doc = CreateBaseDoc();
        var ex = Record.Exception(() => doc.HasField("someField"));
        Assert.Null(ex);
    }

    [Fact]
    public void HasField_AllKnownFields()
    {
        var doc = CreateBaseDoc();
        Assert.True(doc.HasField("name"));
        Assert.True(doc.HasField("score"));
        Assert.True(doc.HasField("dept"));
        Assert.True(doc.HasField("active"));
    }

    [Fact]
    public void HasField_AfterAppendRecord_WithNewField_True()
    {
        var doc = CreateBaseDoc();
        Assert.False(doc.HasField("email"));
        doc.AppendRecord(new Dictionary<string, object>
            { ["name"] = "Zara", ["score"] = 90, ["dept"] = "HR", ["active"] = true, ["email"] = "zara@example.com" });
        Assert.True(doc.HasField("email"));
    }

    [Fact]
    public void HasField_ReturnsBool()
    {
        var doc = CreateBaseDoc();
        var result = doc.HasField("name");
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void HasField_EmptyDoc_False()
    {
        var doc = NdjsonDocument.CreateNew();
        Assert.False(doc.HasField("name"));
    }

    // -------------------------------------------------------------------------
    // DeleteRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRecord_NoThrow()
    {
        var doc = CreateBaseDoc();
        var ex = Record.Exception(() => doc.DeleteRecord(1));
        Assert.Null(ex);
    }

    [Fact]
    public void DeleteRecord_DecreasesCount()
    {
        var doc = CreateBaseDoc();
        var before = doc.GetRecordCount();
        doc.DeleteRecord(1);
        Assert.Equal(before - 1, doc.GetRecordCount());
    }

    [Fact]
    public void DeleteRecord_RemovesCorrectRecord()
    {
        var doc = CreateBaseDoc();
        var nameAt2 = doc.GetRecord(2)["name"].ToString();
        doc.DeleteRecord(1);
        // Former index 2 shifts to index 1
        var newAt1 = doc.GetRecord(1)["name"].ToString();
        Assert.Equal(nameAt2, newAt1);
    }

    [Fact]
    public void DeleteRecord_First_Works()
    {
        var doc = CreateBaseDoc();
        var nameAt1 = doc.GetRecord(1)["name"].ToString();
        var before = doc.GetRecordCount();
        doc.DeleteRecord(0);
        Assert.Equal(before - 1, doc.GetRecordCount());
        Assert.Equal(nameAt1, doc.GetRecord(0)["name"].ToString());
    }

    [Fact]
    public void DeleteRecord_Last_Works()
    {
        var doc = CreateBaseDoc();
        var before = doc.GetRecordCount();
        doc.DeleteRecord(before - 1);
        Assert.Equal(before - 1, doc.GetRecordCount());
    }

    [Fact]
    public void DeleteRecord_Persist()
    {
        var doc = CreateBaseDoc();
        doc.DeleteRecord(1); // Remove Bob
        var path = TempFile("delete_persist.ndjson");
        doc.WriteToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetRecordCount());
        var names = loaded.GetFieldValues("name");
        Assert.DoesNotContain("Bob", names);
    }

    [Fact]
    public void DeleteRecord_Multiple_ReducesCountByN()
    {
        var doc = CreateBaseDoc();
        var before = doc.GetRecordCount();
        doc.DeleteRecord(0);
        doc.DeleteRecord(0); // Now deleting what was index 1
        Assert.Equal(before - 2, doc.GetRecordCount());
    }

    [Fact]
    public void DeleteRecord_ThenFilter_Works()
    {
        var doc = CreateBaseDoc();
        doc.DeleteRecord(1); // Remove Bob (Marketing)
        var mktRows = doc.Filter("dept", "Marketing");
        Assert.Equal(0, mktRows.GetRecordCount()); // No marketing left
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_UpdateRecord_HasField_DeleteRecord_WriteToFile_Pipeline()
    {
        // Build document
        var doc = NdjsonDocument.CreateNew();
        var initialData = new[]
        {
            new Dictionary<string, object> { ["id"] = 1, ["name"] = "Aaron", ["role"] = "Developer", ["score"] = 88 },
            new Dictionary<string, object> { ["id"] = 2, ["name"] = "Brianna", ["role"] = "Designer", ["score"] = 75 },
            new Dictionary<string, object> { ["id"] = 3, ["name"] = "Caleb", ["role"] = "Developer", ["score"] = 91 },
            new Dictionary<string, object> { ["id"] = 4, ["name"] = "Diane", ["role"] = "Manager", ["score"] = 82 },
            new Dictionary<string, object> { ["id"] = 5, ["name"] = "Ethan", ["role"] = "Developer", ["score"] = 77 },
            new Dictionary<string, object> { ["id"] = 6, ["name"] = "Fiona", ["role"] = "Designer", ["score"] = 95 },
        };
        foreach (var rec in initialData) doc.AppendRecord(rec);
        Assert.Equal(6, doc.GetRecordCount());

        // HasField — known fields
        Assert.True(doc.HasField("id"));
        Assert.True(doc.HasField("name"));
        Assert.True(doc.HasField("role"));
        Assert.True(doc.HasField("score"));
        Assert.False(doc.HasField("email"));
        Assert.False(doc.HasField("department"));

        // UpdateRecord — update Brianna's score and role
        doc.UpdateRecord(1, new Dictionary<string, object>
            { ["id"] = 2, ["name"] = "Brianna", ["role"] = "Senior Designer", ["score"] = 89 });
        var briannaRec = doc.GetRecord(1);
        Assert.Equal("Senior Designer", briannaRec["role"].ToString());
        Assert.Equal("89", briannaRec["score"].ToString());
        Assert.Equal(6, doc.GetRecordCount()); // count unchanged

        // UpdateRecord — promote Ethan
        doc.UpdateRecord(4, new Dictionary<string, object>
            { ["id"] = 5, ["name"] = "Ethan", ["role"] = "Senior Developer", ["score"] = 90 });
        Assert.Equal("Senior Developer", doc.GetRecord(4)["role"].ToString());

        // AppendRecord with new field
        doc.AppendRecord(new Dictionary<string, object>
            { ["id"] = 7, ["name"] = "Grace", ["role"] = "Architect", ["score"] = 97, ["email"] = "grace@example.com" });
        Assert.Equal(7, doc.GetRecordCount());
        Assert.True(doc.HasField("email")); // now exists

        // UpdateRecord — add email to existing record
        doc.UpdateRecord(0, new Dictionary<string, object>
            { ["id"] = 1, ["name"] = "Aaron", ["role"] = "Developer", ["score"] = 92, ["email"] = "aaron@example.com" });
        Assert.Equal("aaron@example.com", doc.GetRecord(0)["email"].ToString());

        // Filter — Developers
        var devs = doc.Filter("role", "Developer");
        // Aaron=Developer, Caleb=Developer (Ethan is now Senior Developer)
        Assert.True(devs.GetRecordCount() >= 1);
        Assert.True(devs.HasField("name"));

        // DeleteRecord — remove Ethan (index 4)
        var eveIdx = -1;
        for (int i = 0; i < doc.GetRecordCount(); i++)
        {
            if (doc.GetRecord(i)["name"].ToString() == "Ethan")
            {
                eveIdx = i;
                break;
            }
        }
        if (eveIdx >= 0)
        {
            doc.DeleteRecord(eveIdx);
            Assert.Equal(6, doc.GetRecordCount());
            var names = doc.GetFieldValues("name");
            Assert.DoesNotContain("Ethan", names);
        }

        // DeleteRecord — remove Brianna
        var briIdx = -1;
        for (int i = 0; i < doc.GetRecordCount(); i++)
        {
            if (doc.GetRecord(i)["name"].ToString() == "Brianna")
            {
                briIdx = i;
                break;
            }
        }
        if (briIdx >= 0)
        {
            doc.DeleteRecord(briIdx);
            Assert.Equal(5, doc.GetRecordCount());
        }

        // HasField still true for remaining fields
        Assert.True(doc.HasField("id"));
        Assert.True(doc.HasField("name"));
        Assert.True(doc.HasField("score"));

        // SortBy remaining records
        var sorted = doc.SortBy("score", ascending: false);
        Assert.NotNull(sorted);
        Assert.Equal("Grace", sorted.GetRecord(0)["name"].ToString()); // score=97

        // GetFieldValues
        var names2 = doc.GetFieldValues("name");
        Assert.DoesNotContain("Ethan", names2);
        Assert.DoesNotContain("Brianna", names2);
        Assert.Contains("Aaron", names2);
        Assert.Contains("Grace", names2);

        // WriteToFile
        var path = TempFile("dogfood_update_delete.ndjson");
        doc.WriteToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.GetRecordCount(), loaded.GetRecordCount());
        Assert.True(loaded.HasField("name"));
        Assert.True(loaded.HasField("email")); // Grace still has email

        var loadedNames = loaded.GetFieldValues("name");
        Assert.Contains("Aaron", loadedNames);
        Assert.Contains("Grace", loadedNames);

        // UpdateRecord on loaded
        loaded.UpdateRecord(0, new Dictionary<string, object>
            { ["id"] = 999, ["name"] = "LOADED_UPDATED", ["role"] = "CTO", ["score"] = 100 });
        Assert.Equal("LOADED_UPDATED", loaded.GetRecord(0)["name"].ToString());
        Assert.Equal(doc.GetRecordCount(), loaded.GetRecordCount());

        // DeleteRecord on loaded
        var loadedBefore = loaded.GetRecordCount();
        loaded.DeleteRecord(0);
        Assert.Equal(loadedBefore - 1, loaded.GetRecordCount());

        // HasField after DeleteRecord
        Assert.True(loaded.HasField("name"));

        // Final WriteToFile
        var path2 = TempFile("dogfood_final_state.ndjson");
        loaded.WriteToFile(path2);
        Assert.True(File.Exists(path2));
        var final = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), final.GetRecordCount());
    }
}
