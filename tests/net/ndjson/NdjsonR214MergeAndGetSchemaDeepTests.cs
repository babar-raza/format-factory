// Tests for NdjsonDocument.Merge, GetSchema, GetFieldNames deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R214

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R214: Tests for NdjsonDocument.Merge, GetSchema, GetFieldNames deeper.
/// Merge(other): merges records from another NdjsonDocument into this one.
/// GetSchema(): returns a schema describing field names and inferred types.
/// GetFieldNames(): returns all distinct field names found in the records.
/// Covers: Merge non-null; Merge no-throw; Merge sum of record counts;
/// Merge preserves all records; Merge then Filter; Merge then SortBy;
/// Merge consistent; Merge save-load; Merge self doubles;
/// GetSchema non-null; GetSchema no-throw; GetSchema has fields;
/// GetSchema field count correct; GetSchema consistent; GetSchema save-load;
/// GetSchema type string for text field; GetSchema type number for numeric;
/// GetFieldNames non-null; GetFieldNames non-empty; GetFieldNames count correct;
/// GetFieldNames contains known; GetFieldNames no-throw; GetFieldNames consistent;
/// GetFieldNames no duplicates; GetFieldNames save-load consistent;
/// dogfood CreateDoc→Merge→GetSchema→GetFieldNames→SaveToFile pipeline.
/// </summary>
public class NdjsonR214MergeAndGetSchemaDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR214MergeAndGetSchemaDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR214_" + Guid.NewGuid().ToString("N"));
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
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Alice" }, { "department", "Engineering" }, { "level", "Senior" }, { "salary", 95000 }
        });
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Bob" }, { "department", "Marketing" }, { "level", "Junior" }, { "salary", 55000 }
        });
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Carol" }, { "department", "Engineering" }, { "level", "Lead" }, { "salary", 115000 }
        });
        return doc;
    }

    private NdjsonDocument CreateContractorDoc()
    {
        var doc = NdjsonDocument.CreateEmpty();
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Dave" }, { "department", "Finance" }, { "level", "Mid" }, { "salary", 72000 }
        });
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Eve" }, { "department", "Engineering" }, { "level", "Senior" }, { "salary", 98000 }
        });
        return doc;
    }

    // -------------------------------------------------------------------------
    // Merge
    // -------------------------------------------------------------------------

    [Fact]
    public void Merge_NonNull()
    {
        var docA = CreateEmployeeDoc();
        var docB = CreateContractorDoc();
        Assert.NotNull(docA.Merge(docB));
    }

    [Fact]
    public void Merge_NoThrow()
    {
        var docA = CreateEmployeeDoc();
        var docB = CreateContractorDoc();
        var ex = Record.Exception(() => docA.Merge(docB));
        Assert.Null(ex);
    }

    [Fact]
    public void Merge_SumOfRecordCounts()
    {
        var docA = CreateEmployeeDoc(); // 3 records
        var docB = CreateContractorDoc(); // 2 records
        var merged = docA.Merge(docB);
        Assert.Equal(5, merged.GetRecordCount());
    }

    [Fact]
    public void Merge_PreservesAllRecords()
    {
        var docA = CreateEmployeeDoc();
        var docB = CreateContractorDoc();
        var merged = docA.Merge(docB);
        Assert.Equal(docA.GetRecordCount() + docB.GetRecordCount(), merged.GetRecordCount());
    }

    [Fact]
    public void Merge_ThenFilter_Engineering()
    {
        var docA = CreateEmployeeDoc();
        var docB = CreateContractorDoc();
        var merged = docA.Merge(docB);
        var filtered = merged.Filter("department", "Engineering");
        // Alice, Carol, Eve = 3
        Assert.Equal(3, filtered.GetRecordCount());
    }

    [Fact]
    public void Merge_Consistent()
    {
        var docA = CreateEmployeeDoc();
        var docB = CreateContractorDoc();
        var m1 = docA.Merge(docB);
        var m2 = docA.Merge(docB);
        Assert.Equal(m1.GetRecordCount(), m2.GetRecordCount());
    }

    [Fact]
    public void Merge_SaveLoad_Consistent()
    {
        var docA = CreateEmployeeDoc();
        var docB = CreateContractorDoc();
        var merged = docA.Merge(docB);
        var path = TempFile("merged_save.ndjson");
        merged.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(merged.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void Merge_Self_Doubles()
    {
        var doc = CreateEmployeeDoc(); // 3 records
        var merged = doc.Merge(doc);
        Assert.Equal(6, merged.GetRecordCount());
    }

    [Fact]
    public void Merge_ThenSortBy_NoThrow()
    {
        var docA = CreateEmployeeDoc();
        var docB = CreateContractorDoc();
        var merged = docA.Merge(docB);
        var ex = Record.Exception(() => merged.SortBy("name", ascending: true));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetSchema
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSchema_NonNull()
    {
        var doc = CreateEmployeeDoc();
        Assert.NotNull(doc.GetSchema());
    }

    [Fact]
    public void GetSchema_NoThrow()
    {
        var doc = CreateEmployeeDoc();
        var ex = Record.Exception(() => doc.GetSchema());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSchema_HasFields()
    {
        var doc = CreateEmployeeDoc();
        var schema = doc.GetSchema();
        Assert.True(schema.Fields.Count > 0);
    }

    [Fact]
    public void GetSchema_FieldCount_Correct()
    {
        var doc = CreateEmployeeDoc();
        var schema = doc.GetSchema();
        // 4 fields: name, department, level, salary
        Assert.Equal(4, schema.Fields.Count);
    }

    [Fact]
    public void GetSchema_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var s1 = doc.GetSchema();
        var s2 = doc.GetSchema();
        Assert.Equal(s1.Fields.Count, s2.Fields.Count);
    }

    [Fact]
    public void GetSchema_TypeString_ForTextField()
    {
        var doc = CreateEmployeeDoc();
        var schema = doc.GetSchema();
        // "name" field should be inferred as string
        Assert.True(schema.Fields.ContainsKey("name"));
        Assert.True(schema.Fields["name"].Contains("string") || schema.Fields["name"].Contains("String"));
    }

    [Fact]
    public void GetSchema_TypeNumber_ForNumericField()
    {
        var doc = CreateEmployeeDoc();
        var schema = doc.GetSchema();
        // "salary" field should be inferred as number/integer
        Assert.True(schema.Fields.ContainsKey("salary"));
        var salaryType = schema.Fields["salary"].ToLower();
        Assert.True(salaryType.Contains("number") || salaryType.Contains("integer") || salaryType.Contains("int") || salaryType.Contains("long"));
    }

    [Fact]
    public void GetSchema_SaveLoad_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var before = doc.GetSchema().Fields.Count;
        var path = TempFile("schema_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSchema().Fields.Count);
    }

    // -------------------------------------------------------------------------
    // GetFieldNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldNames_NonNull()
    {
        var doc = CreateEmployeeDoc();
        Assert.NotNull(doc.GetFieldNames());
    }

    [Fact]
    public void GetFieldNames_NonEmpty()
    {
        var doc = CreateEmployeeDoc();
        Assert.True(doc.GetFieldNames().Count > 0);
    }

    [Fact]
    public void GetFieldNames_CountCorrect()
    {
        var doc = CreateEmployeeDoc();
        var names = doc.GetFieldNames();
        // 4 fields: name, department, level, salary
        Assert.Equal(4, names.Count);
    }

    [Fact]
    public void GetFieldNames_ContainsKnown()
    {
        var doc = CreateEmployeeDoc();
        var names = doc.GetFieldNames();
        Assert.True(names.Contains("name") || names.Exists(n => n == "name"));
        Assert.True(names.Contains("department") || names.Exists(n => n == "department"));
    }

    [Fact]
    public void GetFieldNames_NoThrow()
    {
        var doc = CreateEmployeeDoc();
        var ex = Record.Exception(() => doc.GetFieldNames());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldNames_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var n1 = doc.GetFieldNames();
        var n2 = doc.GetFieldNames();
        Assert.Equal(n1.Count, n2.Count);
    }

    [Fact]
    public void GetFieldNames_NoDuplicates()
    {
        var doc = CreateEmployeeDoc();
        var names = doc.GetFieldNames();
        var distinct = new System.Collections.Generic.HashSet<string>(names);
        Assert.Equal(distinct.Count, names.Count);
    }

    [Fact]
    public void GetFieldNames_SaveLoad_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var before = doc.GetFieldNames().Count;
        var path = TempFile("fieldnames_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldNames().Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Merge_GetSchema_GetFieldNames_SaveToFile_Pipeline()
    {
        // Build two NDJSON documents to merge
        var docEmployees = NdjsonDocument.CreateEmpty();
        foreach (var emp in new[]
        {
            new { name = "Alice", dept = "Engineering", grade = "Senior", salary = 95000, active = true },
            new { name = "Bob", dept = "Marketing", grade = "Junior", salary = 55000, active = true },
            new { name = "Carol", dept = "Engineering", grade = "Lead", salary = 115000, active = true },
            new { name = "Dave", dept = "Finance", grade = "Mid", salary = 72000, active = false },
        })
        {
            docEmployees.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
            {
                { "name", emp.name }, { "department", emp.dept }, { "grade", emp.grade },
                { "salary", emp.salary }, { "active", emp.active }
            });
        }

        var docContractors = NdjsonDocument.CreateEmpty();
        foreach (var c in new[]
        {
            new { name = "Eve", dept = "Engineering", grade = "Senior", salary = 98000, active = true },
            new { name = "Frank", dept = "Marketing", grade = "Senior", salary = 82000, active = true },
            new { name = "Grace", dept = "Finance", grade = "Junior", salary = 48000, active = false },
        })
        {
            docContractors.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
            {
                { "name", c.name }, { "department", c.dept }, { "grade", c.grade },
                { "salary", c.salary }, { "active", c.active }
            });
        }

        Assert.Equal(4, docEmployees.GetRecordCount());
        Assert.Equal(3, docContractors.GetRecordCount());

        // GetFieldNames on employees
        var empFields = docEmployees.GetFieldNames();
        Assert.Equal(5, empFields.Count);
        Assert.True(empFields.Contains("name") || empFields.Exists(f => f == "name"));
        Assert.True(empFields.Contains("salary") || empFields.Exists(f => f == "salary"));

        // GetSchema on employees
        var empSchema = docEmployees.GetSchema();
        Assert.Equal(5, empSchema.Fields.Count);

        // Merge
        var merged = docEmployees.Merge(docContractors);
        Assert.Equal(7, merged.GetRecordCount());

        // GetFieldNames on merged — still 5 fields
        var mergedFields = merged.GetFieldNames();
        Assert.Equal(5, mergedFields.Count);

        // GetSchema on merged
        var mergedSchema = merged.GetSchema();
        Assert.Equal(5, mergedSchema.Fields.Count);

        // Filter Engineering from merged — Alice, Carol, Eve = 3
        var engineering = merged.Filter("department", "Engineering");
        Assert.Equal(3, engineering.GetRecordCount());

        // Filter Finance from merged — Dave, Grace = 2
        var finance = merged.Filter("department", "Finance");
        Assert.Equal(2, finance.GetRecordCount());

        // GetDistinctValues for department
        var departments = merged.GetDistinctValues("department");
        Assert.True(departments.Count >= 3); // Engineering, Marketing, Finance

        // SortBy name ascending
        var sorted = merged.SortBy("name", ascending: true);
        Assert.Equal(7, sorted.GetRecordCount());

        // GetFieldNames on sorted consistent
        Assert.Equal(mergedFields.Count, sorted.GetFieldNames().Count);

        // Merge with self — doubles to 14
        var doubled = merged.Merge(merged);
        Assert.Equal(14, doubled.GetRecordCount());

        // GetSchema consistent
        Assert.Equal(mergedSchema.Fields.Count, merged.GetSchema().Fields.Count);

        // GetFieldNames no duplicates
        var noDups = new System.Collections.Generic.HashSet<string>(mergedFields);
        Assert.Equal(noDups.Count, mergedFields.Count);

        // SaveToFile merged
        var path = TempFile("dogfood_merged.ndjson");
        merged.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(7, loaded.GetRecordCount());
        Assert.Equal(5, loaded.GetFieldNames().Count);
        Assert.Equal(5, loaded.GetSchema().Fields.Count);

        // Filter on loaded
        var loadedEng = loaded.Filter("department", "Engineering");
        Assert.Equal(3, loadedEng.GetRecordCount());

        // Merge loaded with contractors again
        var mergedLoaded = loaded.Merge(docContractors);
        Assert.Equal(10, mergedLoaded.GetRecordCount());

        // GetFieldNames on mergedLoaded
        var mergedLoadedFields = mergedLoaded.GetFieldNames();
        Assert.Equal(5, mergedLoadedFields.Count);

        // ExportToJson
        var json = merged.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // Final save
        var path2 = TempFile("dogfood_merged_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), loaded2.GetRecordCount());
        Assert.Equal(loaded.GetFieldNames().Count, loaded2.GetFieldNames().Count);
    }
}
