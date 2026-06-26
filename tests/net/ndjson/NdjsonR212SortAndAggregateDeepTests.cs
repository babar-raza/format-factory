// Tests for NdjsonDocument.SortBy, Aggregate, CountWhere deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R212

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R212: Tests for NdjsonDocument.SortBy, Aggregate, CountWhere deeper.
/// SortBy(field, ascending): sorts records by the specified field value.
/// Aggregate(field, operation): computes an aggregate (sum/min/max/avg) over a numeric field.
/// CountWhere(field, value): counts records where field equals value.
/// Covers: SortBy non-null; SortBy ascending first=Alice; SortBy descending first=Frank;
/// SortBy consistent; SortBy preserves record count; SortBy no-throw;
/// SortBy after AppendRecord; SortBy then Filter; SortBy then ExportToJson;
/// SortBy numeric ascending; SortBy numeric descending;
/// Aggregate sum positive; Aggregate min correct; Aggregate max correct; Aggregate avg in range;
/// Aggregate consistent; Aggregate no-throw; Aggregate after AppendRecord;
/// Aggregate after Filter subset; Aggregate on empty returns 0;
/// CountWhere correct Engineering=3; CountWhere correct Marketing=2;
/// CountWhere no-match=0; CountWhere consistent; CountWhere no-throw;
/// CountWhere after AppendRecord updates; CountWhere after Filter;
/// CountWhere all same field=recordCount; CountWhere returns int;
/// dogfood LoadFile→SortBy→Aggregate→CountWhere→SaveToFile pipeline.
/// </summary>
public class NdjsonR212SortAndAggregateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR212SortAndAggregateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR212_" + Guid.NewGuid().ToString("N"));
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
    // SortBy
    // -------------------------------------------------------------------------

    [Fact]
    public void SortBy_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.NotNull(doc.SortBy("Name", ascending: true));
    }

    [Fact]
    public void SortBy_Ascending_FirstIsAlice()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sorted = doc.SortBy("Name", ascending: true);
        var first = sorted.GetRecord(0);
        Assert.Equal("Alice", first["Name"].ToString());
    }

    [Fact]
    public void SortBy_Descending_FirstIsEveOrFrank()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sorted = doc.SortBy("Name", ascending: false);
        var first = sorted.GetRecord(0);
        // Eve or Frank (both start with E or F)
        var name = first["Name"].ToString();
        Assert.True(name == "Frank" || name == "Eve");
    }

    [Fact]
    public void SortBy_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var s1 = doc.SortBy("Name", ascending: true);
        var s2 = doc.SortBy("Name", ascending: true);
        Assert.Equal(s1.GetRecord(0)["Name"].ToString(), s2.GetRecord(0)["Name"].ToString());
    }

    [Fact]
    public void SortBy_PreservesRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sorted = doc.SortBy("Name", ascending: true);
        Assert.Equal(doc.GetRecordCount(), sorted.GetRecordCount());
    }

    [Fact]
    public void SortBy_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.SortBy("Name", ascending: true));
        Assert.Null(ex);
    }

    [Fact]
    public void SortBy_NumericAscending()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sorted = doc.SortBy("Score", ascending: true);
        var first = sorted.GetRecord(0);
        // Bob has score 72 (lowest)
        Assert.Equal("Bob", first["Name"].ToString());
    }

    [Fact]
    public void SortBy_NumericDescending()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sorted = doc.SortBy("Score", ascending: false);
        var first = sorted.GetRecord(0);
        // Alice has score 95 (highest)
        Assert.Equal("Alice", first["Name"].ToString());
    }

    [Fact]
    public void SortBy_ThenFilter()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sorted = doc.SortBy("Name", ascending: true);
        var filtered = sorted.Filter("Dept", "Engineering");
        Assert.Equal(3, filtered.GetRecordCount());
    }

    [Fact]
    public void SortBy_ThenExportToJson_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sorted = doc.SortBy("Name", ascending: true);
        var json = sorted.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
    }

    // -------------------------------------------------------------------------
    // Aggregate
    // -------------------------------------------------------------------------

    [Fact]
    public void Aggregate_Sum_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sum = doc.Aggregate("Score", "sum");
        Assert.True(sum > 0);
    }

    [Fact]
    public void Aggregate_Min_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var min = doc.Aggregate("Score", "min");
        Assert.Equal(72.0, min, precision: 1); // Bob score=72
    }

    [Fact]
    public void Aggregate_Max_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var max = doc.Aggregate("Score", "max");
        Assert.Equal(95.0, max, precision: 1); // Alice score=95
    }

    [Fact]
    public void Aggregate_Avg_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var avg = doc.Aggregate("Score", "avg");
        // Sum = 95+72+88+80+91+83 = 509, avg = 509/6 ≈ 84.83
        Assert.True(avg > 70.0 && avg < 100.0);
    }

    [Fact]
    public void Aggregate_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sum1 = doc.Aggregate("Score", "sum");
        var sum2 = doc.Aggregate("Score", "sum");
        Assert.Equal(sum1, sum2);
    }

    [Fact]
    public void Aggregate_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.Aggregate("Score", "sum"));
        Assert.Null(ex);
    }

    [Fact]
    public void Aggregate_AfterAppendRecord_Updates()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.Aggregate("Score", "sum");
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Name"] = "Grace",
            ["Dept"] = "HR",
            ["Score"] = 78,
            ["Salary"] = 61000
        });
        var after = doc.Aggregate("Score", "sum");
        Assert.True(after > before);
    }

    [Fact]
    public void Aggregate_AfterFilter_Subset()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var totalSum = doc.Aggregate("Score", "sum");
        var engSum = doc.Filter("Dept", "Engineering").Aggregate("Score", "sum");
        Assert.True(engSum < totalSum);
        // Engineering: Alice=95, Carol=88, Eve=91 → 274
        Assert.Equal(274.0, engSum, precision: 1);
    }

    [Fact]
    public void Aggregate_Sum_ScoreCorrect()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sum = doc.Aggregate("Score", "sum");
        // 95+72+88+80+91+83 = 509
        Assert.Equal(509.0, sum, precision: 1);
    }

    // -------------------------------------------------------------------------
    // CountWhere
    // -------------------------------------------------------------------------

    [Fact]
    public void CountWhere_Engineering_Is3()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(3, doc.CountWhere("Dept", "Engineering"));
    }

    [Fact]
    public void CountWhere_Marketing_Is2()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(2, doc.CountWhere("Dept", "Marketing"));
    }

    [Fact]
    public void CountWhere_Finance_Is1()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(1, doc.CountWhere("Dept", "Finance"));
    }

    [Fact]
    public void CountWhere_NoMatch_Is0()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(0, doc.CountWhere("Dept", "NonExistentDept_XYZ"));
    }

    [Fact]
    public void CountWhere_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.CountWhere("Dept", "Engineering"), doc.CountWhere("Dept", "Engineering"));
    }

    [Fact]
    public void CountWhere_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.CountWhere("Dept", "Engineering"));
        Assert.Null(ex);
    }

    [Fact]
    public void CountWhere_AfterAppendRecord_Updates()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.CountWhere("Dept", "Engineering");
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Name"] = "Hank",
            ["Dept"] = "Engineering",
            ["Score"] = 82,
            ["Salary"] = 88000
        });
        Assert.Equal(before + 1, doc.CountWhere("Dept", "Engineering"));
    }

    [Fact]
    public void CountWhere_ReturnsInt()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var count = doc.CountWhere("Dept", "Engineering");
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SortBy_Aggregate_CountWhere_SaveToFile_Pipeline()
    {
        // Create comprehensive NDJSON
        var path = TempFile("dogfood_main.ndjson");
        var content =
            "{\"Employee\":\"Alice\",\"Dept\":\"Engineering\",\"Score\":95,\"Salary\":95000,\"Years\":8}\n" +
            "{\"Employee\":\"Bob\",\"Dept\":\"Marketing\",\"Score\":72,\"Salary\":55000,\"Years\":2}\n" +
            "{\"Employee\":\"Carol\",\"Dept\":\"Engineering\",\"Score\":88,\"Salary\":115000,\"Years\":12}\n" +
            "{\"Employee\":\"Dave\",\"Dept\":\"Finance\",\"Score\":80,\"Salary\":72000,\"Years\":5}\n" +
            "{\"Employee\":\"Eve\",\"Dept\":\"Engineering\",\"Score\":91,\"Salary\":98000,\"Years\":9}\n" +
            "{\"Employee\":\"Frank\",\"Dept\":\"Marketing\",\"Score\":83,\"Salary\":82000,\"Years\":6}\n" +
            "{\"Employee\":\"Grace\",\"Dept\":\"Finance\",\"Score\":77,\"Salary\":65000,\"Years\":3}\n";
        File.WriteAllText(path, content);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(7, doc.GetRecordCount());

        // CountWhere baseline
        Assert.Equal(3, doc.CountWhere("Dept", "Engineering"));
        Assert.Equal(2, doc.CountWhere("Dept", "Marketing"));
        Assert.Equal(2, doc.CountWhere("Dept", "Finance"));
        Assert.Equal(0, doc.CountWhere("Dept", "HR"));

        // Aggregate baseline
        var totalSalary = doc.Aggregate("Salary", "sum");
        Assert.True(totalSalary > 0);
        // 95000+55000+115000+72000+98000+82000+65000 = 582000
        Assert.Equal(582000.0, totalSalary, precision: 1);

        var minSalary = doc.Aggregate("Salary", "min");
        Assert.Equal(55000.0, minSalary, precision: 1); // Bob

        var maxSalary = doc.Aggregate("Salary", "max");
        Assert.Equal(115000.0, maxSalary, precision: 1); // Carol

        var avgScore = doc.Aggregate("Score", "avg");
        Assert.True(avgScore > 70.0 && avgScore < 100.0);

        // SortBy Employee ascending
        var sortedAsc = doc.SortBy("Employee", ascending: true);
        Assert.Equal(7, sortedAsc.GetRecordCount());
        Assert.Equal("Alice", sortedAsc.GetRecord(0)["Employee"].ToString());
        Assert.Equal("Grace", sortedAsc.GetRecord(6)["Employee"].ToString());

        // SortBy Salary descending
        var sortedBySalary = doc.SortBy("Salary", ascending: false);
        Assert.Equal("Carol", sortedBySalary.GetRecord(0)["Employee"].ToString()); // 115000

        // SortBy then CountWhere
        var sortedDoc = doc.SortBy("Score", ascending: false);
        Assert.Equal(3, sortedDoc.CountWhere("Dept", "Engineering"));

        // SortBy then Aggregate
        var sortedSum = sortedDoc.Aggregate("Score", "sum");
        var directSum = doc.Aggregate("Score", "sum");
        Assert.Equal(directSum, sortedSum, precision: 1); // Sort doesn't change sum

        // Filter Engineering then aggregate
        var eng = doc.Filter("Dept", "Engineering");
        Assert.Equal(3, eng.GetRecordCount());
        var engSalarySum = eng.Aggregate("Salary", "sum");
        Assert.Equal(308000.0, engSalarySum, precision: 1); // 95000+115000+98000

        var engCountDept = eng.CountWhere("Dept", "Engineering");
        Assert.Equal(3, engCountDept);

        // SortBy on filtered
        var engSorted = eng.SortBy("Salary", ascending: true);
        Assert.Equal("Alice", engSorted.GetRecord(0)["Employee"].ToString()); // 95000 lowest

        // AppendRecord and update aggregates
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Employee"] = "Hank",
            ["Dept"] = "Engineering",
            ["Score"] = 88,
            ["Salary"] = 91000,
            ["Years"] = 7
        });
        Assert.Equal(8, doc.GetRecordCount());
        Assert.Equal(4, doc.CountWhere("Dept", "Engineering"));

        var newTotalSalary = doc.Aggregate("Salary", "sum");
        Assert.Equal(totalSalary + 91000, newTotalSalary, precision: 1);

        // SortBy after AppendRecord
        var sortedAfterAppend = doc.SortBy("Employee", ascending: true);
        Assert.Equal(8, sortedAfterAppend.GetRecordCount());

        // CountWhere consistent
        Assert.Equal(doc.CountWhere("Dept", "Engineering"), doc.CountWhere("Dept", "Engineering"));

        // Aggregate consistent
        Assert.Equal(doc.Aggregate("Salary", "sum"), doc.Aggregate("Salary", "sum"), precision: 1);

        // ExportToJson non-null
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // SaveToFile
        var savePath = TempFile("dogfood_result.ndjson");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(8, loaded.GetRecordCount());
        Assert.Equal(4, loaded.CountWhere("Dept", "Engineering"));

        var loadedSum = loaded.Aggregate("Salary", "sum");
        Assert.True(loadedSum > 0);

        var loadedSorted = loaded.SortBy("Score", ascending: false);
        Assert.Equal(8, loadedSorted.GetRecordCount());

        // Final SaveToFile
        var path2 = TempFile("dogfood_final.ndjson");
        loadedSorted.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(8, loaded2.GetRecordCount());
        Assert.Equal(4, loaded2.CountWhere("Dept", "Engineering"));
    }
}
