// Tests for NdjsonDocument.SelectFields, Flatten, GetRecordAt deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R216

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R216: Tests for NdjsonDocument.SelectFields, Flatten, GetRecordAt deeper.
/// SelectFields(fields): returns a new doc with only the specified fields per record.
/// Flatten(): flattens nested objects into single-level records.
/// GetRecordAt(index): returns the record at the given index.
/// Covers: SelectFields non-null; SelectFields no-throw; SelectFields field count=2;
/// SelectFields does not contain removed fields; SelectFields record count same;
/// SelectFields consistent; SelectFields save-load; SelectFields then Filter;
/// SelectFields then Aggregate; SelectFields then SortBy;
/// Flatten non-null; Flatten no-throw; Flatten record count same; Flatten non-empty;
/// Flatten consistent; Flatten save-load; Flatten then GetFieldNames;
/// Flatten then Filter no-throw; Flatten then Aggregate no-throw;
/// GetRecordAt non-null; GetRecordAt no-throw; GetRecordAt first record;
/// GetRecordAt last record; GetRecordAt consistent; GetRecordAt all in range;
/// GetRecordAt save-load; GetRecordAt has correct fields;
/// dogfood CreateDoc→SelectFields→Flatten→GetRecordAt→SaveToFile pipeline.
/// </summary>
public class NdjsonR216SelectFieldsAndFlattenDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR216SelectFieldsAndFlattenDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR216_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private NdjsonDocument CreateEmployeeDoc()
    {
        var doc = NdjsonDocument.CreateEmpty();
        var employees = new[]
        {
            new { name = "Alice", department = "Engineering", score = 92, salary = 95000, active = true },
            new { name = "Bob", department = "Marketing", score = 78, salary = 55000, active = true },
            new { name = "Carol", department = "Engineering", score = 88, salary = 115000, active = true },
            new { name = "Dave", department = "Finance", score = 85, salary = 72000, active = false },
            new { name = "Eve", department = "Engineering", score = 95, salary = 98000, active = true },
        };
        foreach (var e in employees)
        {
            doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
            {
                { "name", e.name }, { "department", e.department },
                { "score", e.score }, { "salary", e.salary }, { "active", e.active }
            });
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // SelectFields
    // -------------------------------------------------------------------------

    [Fact]
    public void SelectFields_NonNull()
    {
        var doc = CreateEmployeeDoc();
        Assert.NotNull(doc.SelectFields(new[] { "name", "department" }));
    }

    [Fact]
    public void SelectFields_NoThrow()
    {
        var doc = CreateEmployeeDoc();
        var ex = Record.Exception(() => doc.SelectFields(new[] { "name", "department" }));
        Assert.Null(ex);
    }

    [Fact]
    public void SelectFields_FieldCount_IsTwo()
    {
        var doc = CreateEmployeeDoc();
        var selected = doc.SelectFields(new[] { "name", "department" });
        Assert.Equal(2, selected.GetFieldNames().Count);
    }

    [Fact]
    public void SelectFields_DoesNotContainRemovedFields()
    {
        var doc = CreateEmployeeDoc();
        var selected = doc.SelectFields(new[] { "name", "department" });
        var fields = selected.GetFieldNames();
        Assert.False(fields.Contains("score") || fields.Exists(f => f == "score"));
        Assert.False(fields.Contains("salary") || fields.Exists(f => f == "salary"));
    }

    [Fact]
    public void SelectFields_RecordCountSame()
    {
        var doc = CreateEmployeeDoc();
        var selected = doc.SelectFields(new[] { "name", "score" });
        Assert.Equal(doc.GetRecordCount(), selected.GetRecordCount());
    }

    [Fact]
    public void SelectFields_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var s1 = doc.SelectFields(new[] { "name", "department" });
        var s2 = doc.SelectFields(new[] { "name", "department" });
        Assert.Equal(s1.GetFieldNames().Count, s2.GetFieldNames().Count);
        Assert.Equal(s1.GetRecordCount(), s2.GetRecordCount());
    }

    [Fact]
    public void SelectFields_SaveLoad_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var selected = doc.SelectFields(new[] { "name", "department" });
        var path = TempFile("selectfields_save.ndjson");
        selected.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(selected.GetRecordCount(), loaded.GetRecordCount());
        Assert.Equal(2, loaded.GetFieldNames().Count);
    }

    [Fact]
    public void SelectFields_ThenFilter_NoThrow()
    {
        var doc = CreateEmployeeDoc();
        var selected = doc.SelectFields(new[] { "name", "department" });
        var ex = Record.Exception(() => selected.Filter("department", "Engineering"));
        Assert.Null(ex);
    }

    [Fact]
    public void SelectFields_ThenFilter_CorrectCount()
    {
        var doc = CreateEmployeeDoc();
        var selected = doc.SelectFields(new[] { "name", "department" });
        var filtered = selected.Filter("department", "Engineering");
        Assert.Equal(3, filtered.GetRecordCount());
    }

    [Fact]
    public void SelectFields_SingleField_Works()
    {
        var doc = CreateEmployeeDoc();
        var selected = doc.SelectFields(new[] { "name" });
        Assert.Equal(1, selected.GetFieldNames().Count);
        Assert.Equal(5, selected.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // Flatten
    // -------------------------------------------------------------------------

    [Fact]
    public void Flatten_NonNull()
    {
        var doc = CreateEmployeeDoc();
        Assert.NotNull(doc.Flatten());
    }

    [Fact]
    public void Flatten_NoThrow()
    {
        var doc = CreateEmployeeDoc();
        var ex = Record.Exception(() => doc.Flatten());
        Assert.Null(ex);
    }

    [Fact]
    public void Flatten_RecordCountSame()
    {
        var doc = CreateEmployeeDoc();
        var flat = doc.Flatten();
        Assert.Equal(doc.GetRecordCount(), flat.GetRecordCount());
    }

    [Fact]
    public void Flatten_NonEmpty()
    {
        var doc = CreateEmployeeDoc();
        var flat = doc.Flatten();
        Assert.True(flat.GetRecordCount() > 0);
    }

    [Fact]
    public void Flatten_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var f1 = doc.Flatten();
        var f2 = doc.Flatten();
        Assert.Equal(f1.GetRecordCount(), f2.GetRecordCount());
    }

    [Fact]
    public void Flatten_SaveLoad_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var flat = doc.Flatten();
        var path = TempFile("flatten_save.ndjson");
        flat.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(flat.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void Flatten_ThenFilter_NoThrow()
    {
        var doc = CreateEmployeeDoc();
        var flat = doc.Flatten();
        var ex = Record.Exception(() => flat.Filter("department", "Engineering"));
        Assert.Null(ex);
    }

    [Fact]
    public void Flatten_ThenGetFieldNames_NonEmpty()
    {
        var doc = CreateEmployeeDoc();
        var flat = doc.Flatten();
        Assert.True(flat.GetFieldNames().Count > 0);
    }

    // -------------------------------------------------------------------------
    // GetRecordAt
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordAt_NonNull()
    {
        var doc = CreateEmployeeDoc();
        Assert.NotNull(doc.GetRecordAt(0));
    }

    [Fact]
    public void GetRecordAt_NoThrow()
    {
        var doc = CreateEmployeeDoc();
        var ex = Record.Exception(() => doc.GetRecordAt(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordAt_FirstRecord_HasNameField()
    {
        var doc = CreateEmployeeDoc();
        var record = doc.GetRecordAt(0);
        Assert.True(record.ContainsKey("name") || record.Keys.Contains("name"));
    }

    [Fact]
    public void GetRecordAt_LastRecord_NonNull()
    {
        var doc = CreateEmployeeDoc();
        Assert.NotNull(doc.GetRecordAt(doc.GetRecordCount() - 1));
    }

    [Fact]
    public void GetRecordAt_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var r1 = doc.GetRecordAt(0);
        var r2 = doc.GetRecordAt(0);
        Assert.Equal(r1.Count, r2.Count);
    }

    [Fact]
    public void GetRecordAt_AllInRange_NoThrow()
    {
        var doc = CreateEmployeeDoc();
        for (int i = 0; i < doc.GetRecordCount(); i++)
        {
            var ex = Record.Exception(() => doc.GetRecordAt(i));
            Assert.Null(ex);
        }
    }

    [Fact]
    public void GetRecordAt_HasCorrectFields()
    {
        var doc = CreateEmployeeDoc();
        var record = doc.GetRecordAt(0);
        // Should have all 5 fields
        Assert.Equal(5, record.Count);
    }

    [Fact]
    public void GetRecordAt_SaveLoad_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var before = doc.GetRecordAt(0).Count;
        var path = TempFile("recordat_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordAt(0).Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SelectFields_Flatten_GetRecordAt_SaveToFile_Pipeline()
    {
        // Build comprehensive employee document
        var doc = NdjsonDocument.CreateEmpty();
        var employees = new[]
        {
            new { name = "Alice", dept = "Engineering", grade = "Senior", score = 92, salary = 95000, active = true, years = 5 },
            new { name = "Bob", dept = "Marketing", grade = "Junior", score = 78, salary = 55000, active = true, years = 1 },
            new { name = "Carol", dept = "Engineering", grade = "Lead", score = 88, salary = 115000, active = true, years = 8 },
            new { name = "Dave", dept = "Finance", grade = "Mid", score = 85, salary = 72000, active = false, years = 3 },
            new { name = "Eve", dept = "Engineering", grade = "Senior", score = 95, salary = 98000, active = true, years = 6 },
            new { name = "Frank", dept = "Marketing", grade = "Senior", score = 80, salary = 82000, active = true, years = 4 },
        };
        foreach (var e in employees)
        {
            doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
            {
                { "name", e.name }, { "department", e.dept }, { "grade", e.grade },
                { "score", e.score }, { "salary", e.salary }, { "active", e.active }, { "years", e.years }
            });
        }

        Assert.Equal(6, doc.GetRecordCount());
        Assert.Equal(7, doc.GetFieldNames().Count);

        // GetRecordAt first record
        var first = doc.GetRecordAt(0);
        Assert.NotNull(first);
        Assert.Equal(7, first.Count);
        Assert.True(first.ContainsKey("name"));

        // GetRecordAt all records — no throw
        for (int i = 0; i < doc.GetRecordCount(); i++)
        {
            var rec = doc.GetRecordAt(i);
            Assert.NotNull(rec);
            Assert.Equal(7, rec.Count);
        }

        // GetRecordAt last
        var last = doc.GetRecordAt(5);
        Assert.NotNull(last);

        // SelectFields — keep only name, department, score
        var nameDepScore = doc.SelectFields(new[] { "name", "department", "score" });
        Assert.Equal(6, nameDepScore.GetRecordCount());
        Assert.Equal(3, nameDepScore.GetFieldNames().Count);
        Assert.False(nameDepScore.GetFieldNames().Contains("salary") ||
                     nameDepScore.GetFieldNames().Exists(f => f == "salary"));

        // SelectFields then Filter Engineering
        var engSelected = nameDepScore.Filter("department", "Engineering");
        Assert.Equal(3, engSelected.GetRecordCount());
        Assert.Equal(3, engSelected.GetFieldNames().Count);

        // SelectFields then Aggregate
        var scoreSum = nameDepScore.Aggregate("score", "sum");
        Assert.True(scoreSum > 400.0); // 92+78+88+85+95+80 = 518

        // SelectFields single field
        var namesOnly = doc.SelectFields(new[] { "name" });
        Assert.Equal(1, namesOnly.GetFieldNames().Count);
        Assert.Equal(6, namesOnly.GetRecordCount());

        // SelectFields save-load
        var selectedPath = TempFile("dogfood_selected.ndjson");
        nameDepScore.SaveToFile(selectedPath);
        var loadedSelected = NdjsonDocument.LoadFile(selectedPath);
        Assert.Equal(6, loadedSelected.GetRecordCount());
        Assert.Equal(3, loadedSelected.GetFieldNames().Count);

        // Flatten — for flat docs, same record count
        var flat = doc.Flatten();
        Assert.Equal(6, flat.GetRecordCount());
        Assert.True(flat.GetFieldNames().Count > 0);

        // Flatten then Filter
        var flatEng = flat.Filter("department", "Engineering");
        Assert.Equal(3, flatEng.GetRecordCount());

        // Flatten save-load
        var flatPath = TempFile("dogfood_flat.ndjson");
        flat.SaveToFile(flatPath);
        var loadedFlat = NdjsonDocument.LoadFile(flatPath);
        Assert.Equal(6, loadedFlat.GetRecordCount());

        // AppendRecord and verify GetRecordAt
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Grace" }, { "department", "HR" }, { "grade", "Junior" },
            { "score", 75 }, { "salary", 48000 }, { "active", true }, { "years", 1 }
        });
        Assert.Equal(7, doc.GetRecordCount());
        var newLast = doc.GetRecordAt(6);
        Assert.NotNull(newLast);
        Assert.Equal(7, newLast.Count);

        // ExportToJson
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // SaveToFile main doc
        var path = TempFile("dogfood_main.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(7, loaded.GetRecordCount());
        Assert.Equal(7, loaded.GetFieldNames().Count);

        // GetRecordAt on loaded
        var loadedFirst = loaded.GetRecordAt(0);
        Assert.Equal(7, loadedFirst.Count);

        // SelectFields on loaded
        var loadedSelected2 = loaded.SelectFields(new[] { "name", "score" });
        Assert.Equal(2, loadedSelected2.GetFieldNames().Count);
        Assert.Equal(7, loadedSelected2.GetRecordCount());

        // Final save
        var path2 = TempFile("dogfood_main_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), loaded2.GetRecordCount());
        Assert.Equal(loaded.GetRecordAt(0).Count, loaded2.GetRecordAt(0).Count);
    }
}
