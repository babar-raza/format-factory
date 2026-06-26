// Tests for NdjsonDocument.SelectFields, Flatten, ToDataTable deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R213

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R213: Tests for NdjsonDocument.SelectFields, Flatten, ToDataTable deeper.
/// SelectFields(fields): returns a new document with only the specified fields.
/// Flatten(): flattens nested records into top-level key-value pairs.
/// ToDataTable(): converts the document into a tabular representation.
/// Covers: SelectFields non-null; SelectFields record count same; SelectFields field count correct;
/// SelectFields contains only specified fields; SelectFields consistent; SelectFields no-throw;
/// SelectFields single field; SelectFields all fields; SelectFields after Filter;
/// SelectFields then ExportToJson; SelectFields then SaveToFile;
/// Flatten non-null; Flatten record count same; Flatten no-throw; Flatten consistent;
/// Flatten non-empty; Flatten after AppendRecord; Flatten then SelectFields;
/// Flatten then ExportToJson; Flatten save-load;
/// ToDataTable non-null; ToDataTable has rows; ToDataTable has columns; ToDataTable consistent;
/// ToDataTable no-throw; ToDataTable row count = record count; ToDataTable col count = field count;
/// ToDataTable after Filter subset; ToDataTable after AppendRecord grows;
/// ToDataTable save-load consistent; ToDataTable then ExportToJson;
/// dogfood LoadFile→SelectFields→Flatten→ToDataTable→SaveToFile pipeline.
/// </summary>
public class NdjsonR213SelectFieldsAndFlattenDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR213SelectFieldsAndFlattenDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR213_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleNdjson()
    {
        var path = TempFile("sample.ndjson");
        var content =
            "{\"Name\":\"Alice\",\"Dept\":\"Engineering\",\"Score\":95,\"Salary\":95000}\n" +
            "{\"Name\":\"Bob\",\"Dept\":\"Marketing\",\"Score\":72,\"Salary\":55000}\n" +
            "{\"Name\":\"Carol\",\"Dept\":\"Engineering\",\"Score\":88,\"Salary\":115000}\n" +
            "{\"Name\":\"Dave\",\"Dept\":\"Finance\",\"Score\":80,\"Salary\":72000}\n" +
            "{\"Name\":\"Eve\",\"Dept\":\"Engineering\",\"Score\":91,\"Salary\":98000}\n" +
            "{\"Name\":\"Frank\",\"Dept\":\"Marketing\",\"Score\":83,\"Salary\":82000}\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // SelectFields
    // -------------------------------------------------------------------------

    [Fact]
    public void SelectFields_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.NotNull(doc.SelectFields(new[] { "Name", "Dept" }));
    }

    [Fact]
    public void SelectFields_RecordCountSame()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var selected = doc.SelectFields(new[] { "Name", "Dept" });
        Assert.Equal(doc.GetRecordCount(), selected.GetRecordCount());
    }

    [Fact]
    public void SelectFields_FieldCountCorrect()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var selected = doc.SelectFields(new[] { "Name", "Score" });
        var fieldNames = selected.GetFieldNames();
        Assert.Equal(2, fieldNames.Count);
    }

    [Fact]
    public void SelectFields_ContainsOnlySpecifiedFields()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var selected = doc.SelectFields(new[] { "Name", "Dept" });
        var fieldNames = selected.GetFieldNames();
        Assert.Contains("Name", fieldNames);
        Assert.Contains("Dept", fieldNames);
        Assert.DoesNotContain("Score", fieldNames);
        Assert.DoesNotContain("Salary", fieldNames);
    }

    [Fact]
    public void SelectFields_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var s1 = doc.SelectFields(new[] { "Name" });
        var s2 = doc.SelectFields(new[] { "Name" });
        Assert.Equal(s1.GetRecordCount(), s2.GetRecordCount());
    }

    [Fact]
    public void SelectFields_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.SelectFields(new[] { "Name", "Dept" }));
        Assert.Null(ex);
    }

    [Fact]
    public void SelectFields_SingleField()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var selected = doc.SelectFields(new[] { "Name" });
        Assert.Equal(6, selected.GetRecordCount());
        Assert.Equal(1, selected.GetFieldNames().Count);
    }

    [Fact]
    public void SelectFields_AfterFilter()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var filtered = doc.Filter("Dept", "Engineering");
        var selected = filtered.SelectFields(new[] { "Name", "Score" });
        Assert.Equal(3, selected.GetRecordCount());
        Assert.Equal(2, selected.GetFieldNames().Count);
    }

    [Fact]
    public void SelectFields_ThenExportToJson_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var selected = doc.SelectFields(new[] { "Name", "Dept" });
        var json = selected.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
    }

    [Fact]
    public void SelectFields_ThenSaveToFile()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var selected = doc.SelectFields(new[] { "Name", "Score" });
        var path = TempFile("selected.ndjson");
        selected.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetRecordCount());
    }

    [Fact]
    public void SelectFields_DataPreserved()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var selected = doc.SelectFields(new[] { "Name" });
        var record = selected.GetRecord(0);
        Assert.True(record.ContainsKey("Name"));
        Assert.Equal("Alice", record["Name"].ToString());
    }

    // -------------------------------------------------------------------------
    // Flatten
    // -------------------------------------------------------------------------

    [Fact]
    public void Flatten_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.NotNull(doc.Flatten());
    }

    [Fact]
    public void Flatten_RecordCountSame()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var flattened = doc.Flatten();
        Assert.Equal(doc.GetRecordCount(), flattened.GetRecordCount());
    }

    [Fact]
    public void Flatten_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.Flatten());
        Assert.Null(ex);
    }

    [Fact]
    public void Flatten_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var f1 = doc.Flatten();
        var f2 = doc.Flatten();
        Assert.Equal(f1.GetRecordCount(), f2.GetRecordCount());
    }

    [Fact]
    public void Flatten_NonEmpty()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var flattened = doc.Flatten();
        Assert.True(flattened.GetRecordCount() > 0);
    }

    [Fact]
    public void Flatten_ThenExportToJson_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var flattened = doc.Flatten();
        var json = flattened.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
    }

    [Fact]
    public void Flatten_ThenSelectFields()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var flattened = doc.Flatten();
        var selected = flattened.SelectFields(new[] { "Name", "Dept" });
        Assert.Equal(6, selected.GetRecordCount());
    }

    [Fact]
    public void Flatten_SaveLoad()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var flattened = doc.Flatten();
        var path = TempFile("flattened.ndjson");
        flattened.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(flattened.GetRecordCount(), loaded.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // ToDataTable
    // -------------------------------------------------------------------------

    [Fact]
    public void ToDataTable_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.NotNull(doc.ToDataTable());
    }

    [Fact]
    public void ToDataTable_HasRows()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var dt = doc.ToDataTable();
        Assert.True(dt.Rows.Count > 0);
    }

    [Fact]
    public void ToDataTable_HasColumns()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var dt = doc.ToDataTable();
        Assert.True(dt.Columns.Count > 0);
    }

    [Fact]
    public void ToDataTable_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var dt1 = doc.ToDataTable();
        var dt2 = doc.ToDataTable();
        Assert.Equal(dt1.Rows.Count, dt2.Rows.Count);
        Assert.Equal(dt1.Columns.Count, dt2.Columns.Count);
    }

    [Fact]
    public void ToDataTable_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.ToDataTable());
        Assert.Null(ex);
    }

    [Fact]
    public void ToDataTable_RowCountEqualsRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var dt = doc.ToDataTable();
        Assert.Equal(doc.GetRecordCount(), dt.Rows.Count);
    }

    [Fact]
    public void ToDataTable_ColCountEqualsFieldCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var dt = doc.ToDataTable();
        Assert.Equal(doc.GetFieldNames().Count, dt.Columns.Count);
    }

    [Fact]
    public void ToDataTable_AfterFilter_Subset()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var filtered = doc.Filter("Dept", "Engineering");
        var dt = filtered.ToDataTable();
        Assert.Equal(3, dt.Rows.Count);
    }

    [Fact]
    public void ToDataTable_AfterAppendRecord_Grows()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.ToDataTable().Rows.Count;
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Name"] = "Grace",
            ["Dept"] = "HR",
            ["Score"] = 78,
            ["Salary"] = 61000
        });
        var after = doc.ToDataTable().Rows.Count;
        Assert.Equal(before + 1, after);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SelectFields_Flatten_ToDataTable_SaveToFile_Pipeline()
    {
        // Create comprehensive NDJSON
        var path = TempFile("dogfood_main.ndjson");
        var content =
            "{\"Employee\":\"Alice\",\"Dept\":\"Engineering\",\"Grade\":\"Senior\",\"Score\":95,\"Salary\":95000,\"Years\":8}\n" +
            "{\"Employee\":\"Bob\",\"Dept\":\"Marketing\",\"Grade\":\"Junior\",\"Score\":72,\"Salary\":55000,\"Years\":2}\n" +
            "{\"Employee\":\"Carol\",\"Dept\":\"Engineering\",\"Grade\":\"Lead\",\"Score\":88,\"Salary\":115000,\"Years\":12}\n" +
            "{\"Employee\":\"Dave\",\"Dept\":\"Finance\",\"Grade\":\"Mid\",\"Score\":80,\"Salary\":72000,\"Years\":5}\n" +
            "{\"Employee\":\"Eve\",\"Dept\":\"Engineering\",\"Grade\":\"Senior\",\"Score\":91,\"Salary\":98000,\"Years\":9}\n" +
            "{\"Employee\":\"Frank\",\"Dept\":\"Marketing\",\"Grade\":\"Senior\",\"Score\":83,\"Salary\":82000,\"Years\":6}\n";
        File.WriteAllText(path, content);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(6, doc.GetRecordCount());
        Assert.Equal(6, doc.GetFieldNames().Count);

        // SelectFields — subset
        var summary = doc.SelectFields(new[] { "Employee", "Dept", "Score" });
        Assert.Equal(6, summary.GetRecordCount());
        Assert.Equal(3, summary.GetFieldNames().Count);
        Assert.Contains("Employee", summary.GetFieldNames());
        Assert.DoesNotContain("Salary", summary.GetFieldNames());

        // SelectFields data preserved
        var aliceRecord = summary.GetRecord(0);
        Assert.Equal("Alice", aliceRecord["Employee"].ToString());
        Assert.Equal("95", aliceRecord["Score"].ToString());

        // SelectFields after Filter
        var engSummary = doc.Filter("Dept", "Engineering").SelectFields(new[] { "Employee", "Salary" });
        Assert.Equal(3, engSummary.GetRecordCount());
        Assert.Equal(2, engSummary.GetFieldNames().Count);

        // ExportToJson on selected
        var summaryJson = summary.ExportToJson();
        Assert.NotNull(summaryJson);
        Assert.True(summaryJson.Length < doc.ExportToJson().Length); // fewer fields

        // Flatten baseline (flat document stays flat)
        var flattened = doc.Flatten();
        Assert.Equal(6, flattened.GetRecordCount());
        Assert.True(flattened.GetFieldNames().Count >= 1);

        // Flatten then SelectFields
        var flatSelected = flattened.SelectFields(new[] { "Employee", "Dept" });
        Assert.Equal(6, flatSelected.GetRecordCount());

        // ToDataTable on original
        var dt = doc.ToDataTable();
        Assert.NotNull(dt);
        Assert.Equal(6, dt.Rows.Count);
        Assert.Equal(6, dt.Columns.Count);

        // ToDataTable on selected
        var summaryDt = summary.ToDataTable();
        Assert.Equal(6, summaryDt.Rows.Count);
        Assert.Equal(3, summaryDt.Columns.Count);

        // ToDataTable after Filter
        var engDt = doc.Filter("Dept", "Engineering").ToDataTable();
        Assert.Equal(3, engDt.Rows.Count);

        // AppendRecord and verify ToDataTable grows
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Employee"] = "Grace",
            ["Dept"] = "HR",
            ["Grade"] = "Junior",
            ["Score"] = 78,
            ["Salary"] = 61000,
            ["Years"] = 1
        });
        var dtAfterAppend = doc.ToDataTable();
        Assert.Equal(7, dtAfterAppend.Rows.Count);

        // SelectFields after AppendRecord
        var summaryAfter = doc.SelectFields(new[] { "Employee", "Dept" });
        Assert.Equal(7, summaryAfter.GetRecordCount());
        Assert.Equal(2, summaryAfter.GetFieldNames().Count);

        // Flatten after AppendRecord
        var flattenedAfter = doc.Flatten();
        Assert.Equal(7, flattenedAfter.GetRecordCount());

        // ToDataTable consistent
        var dt1 = doc.ToDataTable();
        var dt2 = doc.ToDataTable();
        Assert.Equal(dt1.Rows.Count, dt2.Rows.Count);

        // SelectFields consistent
        var sf1 = doc.SelectFields(new[] { "Employee" });
        var sf2 = doc.SelectFields(new[] { "Employee" });
        Assert.Equal(sf1.GetRecordCount(), sf2.GetRecordCount());

        // SaveToFile original
        var savePath = TempFile("dogfood_result.ndjson");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // SaveToFile selected
        var saveSummary = TempFile("dogfood_summary.ndjson");
        summaryAfter.SaveToFile(saveSummary);
        Assert.True(File.Exists(saveSummary));

        // LoadFile verify original
        var loadedOrig = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(7, loadedOrig.GetRecordCount());

        var loadedDt = loadedOrig.ToDataTable();
        Assert.Equal(7, loadedDt.Rows.Count);

        // SelectFields on loaded
        var loadedSelected = loadedOrig.SelectFields(new[] { "Employee", "Dept", "Score" });
        Assert.Equal(7, loadedSelected.GetRecordCount());

        // Flatten on loaded
        var loadedFlat = loadedOrig.Flatten();
        Assert.Equal(7, loadedFlat.GetRecordCount());

        // Final SaveToFile
        var path2 = TempFile("dogfood_final.ndjson");
        loadedSelected.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetRecordCount());
        var loaded2Dt = loaded2.ToDataTable();
        Assert.Equal(7, loaded2Dt.Rows.Count);
        Assert.Equal(3, loaded2Dt.Columns.Count);
    }
}
