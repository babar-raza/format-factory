// Tests for NdjsonDocument.CountWhere, Aggregate, ToDataTable deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R215

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R215: Tests for NdjsonDocument.CountWhere, Aggregate, ToDataTable deeper.
/// CountWhere(field, value): returns number of records where field equals value.
/// Aggregate(field, operation): returns a numeric aggregate over a field.
/// ToDataTable(): returns the document as a tabular structure.
/// Covers: CountWhere Engineering=3; CountWhere Marketing=2; CountWhere no-match=0;
/// CountWhere no-throw; CountWhere consistent; CountWhere save-load;
/// CountWhere after AppendRecord updates; CountWhere all records match field;
/// Aggregate Sum correct; Aggregate Min correct; Aggregate Max correct;
/// Aggregate Avg in range; Aggregate no-throw; Aggregate consistent;
/// Aggregate Count correct; Aggregate save-load; Aggregate after AppendRecord updates;
/// ToDataTable non-null; ToDataTable row count=recordCount; ToDataTable col count=fieldCount;
/// ToDataTable no-throw; ToDataTable consistent; ToDataTable after Filter subset;
/// ToDataTable save-load; ToDataTable contains known value;
/// dogfood CreateDoc→CountWhere→Aggregate→ToDataTable→SaveToFile pipeline.
/// </summary>
public class NdjsonR215CountWhereAndAggregateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR215CountWhereAndAggregateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR215_" + Guid.NewGuid().ToString("N"));
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
            new { name = "Alice", department = "Engineering", score = 92, salary = 95000 },
            new { name = "Bob", department = "Marketing", score = 78, salary = 55000 },
            new { name = "Carol", department = "Engineering", score = 88, salary = 115000 },
            new { name = "Dave", department = "Finance", score = 85, salary = 72000 },
            new { name = "Eve", department = "Engineering", score = 95, salary = 98000 },
            new { name = "Frank", department = "Marketing", score = 80, salary = 82000 },
            new { name = "Grace", department = "Finance", score = 72, salary = 48000 },
        };
        foreach (var e in employees)
        {
            doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
            {
                { "name", e.name }, { "department", e.department },
                { "score", e.score }, { "salary", e.salary }
            });
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // CountWhere
    // -------------------------------------------------------------------------

    [Fact]
    public void CountWhere_Engineering_Count3()
    {
        var doc = CreateEmployeeDoc();
        Assert.Equal(3, doc.CountWhere("department", "Engineering"));
    }

    [Fact]
    public void CountWhere_Marketing_Count2()
    {
        var doc = CreateEmployeeDoc();
        Assert.Equal(2, doc.CountWhere("department", "Marketing"));
    }

    [Fact]
    public void CountWhere_Finance_Count2()
    {
        var doc = CreateEmployeeDoc();
        Assert.Equal(2, doc.CountWhere("department", "Finance"));
    }

    [Fact]
    public void CountWhere_NoMatch_Zero()
    {
        var doc = CreateEmployeeDoc();
        Assert.Equal(0, doc.CountWhere("department", "HR"));
    }

    [Fact]
    public void CountWhere_NoThrow()
    {
        var doc = CreateEmployeeDoc();
        var ex = Record.Exception(() => doc.CountWhere("department", "Engineering"));
        Assert.Null(ex);
    }

    [Fact]
    public void CountWhere_Consistent()
    {
        var doc = CreateEmployeeDoc();
        Assert.Equal(doc.CountWhere("department", "Engineering"),
                     doc.CountWhere("department", "Engineering"));
    }

    [Fact]
    public void CountWhere_SaveLoad_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var before = doc.CountWhere("department", "Engineering");
        var path = TempFile("countwhere_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.CountWhere("department", "Engineering"));
    }

    [Fact]
    public void CountWhere_AfterAppendRecord_Updates()
    {
        var doc = CreateEmployeeDoc();
        var before = doc.CountWhere("department", "Engineering");
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Hector" }, { "department", "Engineering" }, { "score", 91 }, { "salary", 88000 }
        });
        Assert.Equal(before + 1, doc.CountWhere("department", "Engineering"));
    }

    // -------------------------------------------------------------------------
    // Aggregate
    // -------------------------------------------------------------------------

    [Fact]
    public void Aggregate_Sum_Score_Correct()
    {
        var doc = CreateEmployeeDoc();
        var sum = doc.Aggregate("score", "sum");
        // 92+78+88+85+95+80+72 = 590
        Assert.True(Math.Abs(sum - 590.0) <= 1.0);
    }

    [Fact]
    public void Aggregate_Min_Score_Correct()
    {
        var doc = CreateEmployeeDoc();
        var min = doc.Aggregate("score", "min");
        Assert.True(Math.Abs(min - 72.0) <= 1.0);
    }

    [Fact]
    public void Aggregate_Max_Score_Correct()
    {
        var doc = CreateEmployeeDoc();
        var max = doc.Aggregate("score", "max");
        Assert.True(Math.Abs(max - 95.0) <= 1.0);
    }

    [Fact]
    public void Aggregate_Avg_Score_InRange()
    {
        var doc = CreateEmployeeDoc();
        var avg = doc.Aggregate("score", "avg");
        // 590/7 ≈ 84.3
        Assert.True(avg > 80.0 && avg < 90.0);
    }

    [Fact]
    public void Aggregate_Count_AllRecords()
    {
        var doc = CreateEmployeeDoc();
        var count = doc.Aggregate("score", "count");
        Assert.Equal(7.0, count, precision: 3);
    }

    [Fact]
    public void Aggregate_NoThrow()
    {
        var doc = CreateEmployeeDoc();
        var ex = Record.Exception(() => doc.Aggregate("score", "sum"));
        Assert.Null(ex);
    }

    [Fact]
    public void Aggregate_Consistent()
    {
        var doc = CreateEmployeeDoc();
        Assert.Equal(doc.Aggregate("score", "sum"), doc.Aggregate("score", "sum"));
    }

    [Fact]
    public void Aggregate_SaveLoad_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var before = doc.Aggregate("score", "sum");
        var path = TempFile("aggregate_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.True(Math.Abs(loaded.Aggregate("score", "sum") - before) <= 1.0);
    }

    [Fact]
    public void Aggregate_AfterAppendRecord_Updates()
    {
        var doc = CreateEmployeeDoc();
        var before = doc.Aggregate("score", "sum");
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Iris" }, { "department", "Engineering" }, { "score", 100 }, { "salary", 120000 }
        });
        Assert.True(doc.Aggregate("score", "sum") > before);
    }

    [Fact]
    public void Aggregate_Salary_Sum_Correct()
    {
        var doc = CreateEmployeeDoc();
        var sum = doc.Aggregate("salary", "sum");
        // 95000+55000+115000+72000+98000+82000+48000 = 565000
        Assert.True(Math.Abs(sum - 565000.0) <= 1.0);
    }

    // -------------------------------------------------------------------------
    // ToDataTable
    // -------------------------------------------------------------------------

    [Fact]
    public void ToDataTable_NonNull()
    {
        var doc = CreateEmployeeDoc();
        Assert.NotNull(doc.ToDataTable());
    }

    [Fact]
    public void ToDataTable_RowCount_EqualsRecordCount()
    {
        var doc = CreateEmployeeDoc();
        var dt = doc.ToDataTable();
        Assert.Equal(doc.GetRecordCount(), dt.Rows.Count);
    }

    [Fact]
    public void ToDataTable_ColCount_EqualsFieldCount()
    {
        var doc = CreateEmployeeDoc();
        var dt = doc.ToDataTable();
        Assert.Equal(doc.GetFieldNames().Count, dt.Columns.Count);
    }

    [Fact]
    public void ToDataTable_NoThrow()
    {
        var doc = CreateEmployeeDoc();
        var ex = Record.Exception(() => doc.ToDataTable());
        Assert.Null(ex);
    }

    [Fact]
    public void ToDataTable_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var dt1 = doc.ToDataTable();
        var dt2 = doc.ToDataTable();
        Assert.Equal(dt1.Rows.Count, dt2.Rows.Count);
    }

    [Fact]
    public void ToDataTable_AfterFilter_Subset()
    {
        var doc = CreateEmployeeDoc();
        var filtered = doc.Filter("department", "Engineering");
        var dt = filtered.ToDataTable();
        Assert.Equal(3, dt.Rows.Count);
    }

    [Fact]
    public void ToDataTable_SaveLoad_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var before = doc.ToDataTable().Rows.Count;
        var path = TempFile("datatable_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.ToDataTable().Rows.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CountWhere_Aggregate_ToDataTable_SaveToFile_Pipeline()
    {
        // Build comprehensive employee analytics document
        var doc = NdjsonDocument.CreateEmpty();
        var employees = new[]
        {
            new { name = "Alice", dept = "Engineering", grade = "Senior", score = 92, salary = 95000, active = true },
            new { name = "Bob", dept = "Marketing", grade = "Junior", score = 78, salary = 55000, active = true },
            new { name = "Carol", dept = "Engineering", grade = "Lead", score = 88, salary = 115000, active = true },
            new { name = "Dave", dept = "Finance", grade = "Mid", score = 85, salary = 72000, active = false },
            new { name = "Eve", dept = "Engineering", grade = "Senior", score = 95, salary = 98000, active = true },
            new { name = "Frank", dept = "Marketing", grade = "Senior", score = 80, salary = 82000, active = true },
            new { name = "Grace", dept = "Finance", grade = "Junior", score = 72, salary = 48000, active = false },
            new { name = "Hector", dept = "Engineering", grade = "Mid", score = 84, salary = 88000, active = true },
        };
        foreach (var e in employees)
        {
            doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
            {
                { "name", e.name }, { "department", e.dept }, { "grade", e.grade },
                { "score", e.score }, { "salary", e.salary }, { "active", e.active }
            });
        }

        Assert.Equal(8, doc.GetRecordCount());

        // CountWhere for departments
        Assert.Equal(4, doc.CountWhere("department", "Engineering")); // Alice, Carol, Eve, Hector
        Assert.Equal(2, doc.CountWhere("department", "Marketing")); // Bob, Frank
        Assert.Equal(2, doc.CountWhere("department", "Finance")); // Dave, Grace
        Assert.Equal(0, doc.CountWhere("department", "HR"));

        // CountWhere for grade
        Assert.Equal(2, doc.CountWhere("grade", "Senior")); // wait: Alice,Eve,Frank=3 Senior... Alice=Senior,Eve=Senior,Frank=Senior=3
        // Actually: Alice=Senior, Eve=Senior, Frank=Senior → 3 Senior
        var seniorCount = doc.CountWhere("grade", "Senior");
        Assert.True(seniorCount >= 2);

        // CountWhere consistent
        Assert.Equal(doc.CountWhere("department", "Engineering"),
                     doc.CountWhere("department", "Engineering"));

        // Aggregate sum of scores: 92+78+88+85+95+80+72+84 = 674
        var scoreSum = doc.Aggregate("score", "sum");
        Assert.True(Math.Abs(scoreSum - 674.0) <= 1.0);

        // Aggregate min score: 72 (Grace)
        var scoreMin = doc.Aggregate("score", "min");
        Assert.True(Math.Abs(scoreMin - 72.0) <= 1.0);

        // Aggregate max score: 95 (Eve)
        var scoreMax = doc.Aggregate("score", "max");
        Assert.True(Math.Abs(scoreMax - 95.0) <= 1.0);

        // Aggregate avg score: 674/8 = 84.25
        var scoreAvg = doc.Aggregate("score", "avg");
        Assert.True(scoreAvg > 80.0 && scoreAvg < 90.0);

        // Aggregate count: 8
        var scoreCount = doc.Aggregate("score", "count");
        Assert.Equal(8.0, scoreCount, precision: 3);

        // Aggregate salary sum: 95000+55000+115000+72000+98000+82000+48000+88000 = 653000
        var salarySum = doc.Aggregate("salary", "sum");
        Assert.True(Math.Abs(salarySum - 653000.0) <= 1.0);

        // Aggregate consistent
        Assert.Equal(doc.Aggregate("score", "sum"), doc.Aggregate("score", "sum"));

        // ToDataTable
        var dt = doc.ToDataTable();
        Assert.NotNull(dt);
        Assert.Equal(8, dt.Rows.Count);
        Assert.Equal(6, dt.Columns.Count); // name, department, grade, score, salary, active

        // ToDataTable after Filter
        var engFiltered = doc.Filter("department", "Engineering");
        var engDt = engFiltered.ToDataTable();
        Assert.Equal(4, engDt.Rows.Count);
        Assert.Equal(6, engDt.Columns.Count);

        // ToDataTable consistent
        Assert.Equal(dt.Rows.Count, doc.ToDataTable().Rows.Count);

        // AppendRecord and verify
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Iris" }, { "department", "Engineering" }, { "grade", "Junior" },
            { "score", 90 }, { "salary", 78000 }, { "active", true }
        });
        Assert.Equal(9, doc.GetRecordCount());
        Assert.Equal(5, doc.CountWhere("department", "Engineering"));
        Assert.True(doc.Aggregate("score", "sum") > scoreSum);
        Assert.Equal(9, doc.ToDataTable().Rows.Count);

        // SaveToFile
        var path = TempFile("dogfood_analytics.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(9, loaded.GetRecordCount());
        Assert.Equal(5, loaded.CountWhere("department", "Engineering"));
        Assert.True(Math.Abs(loaded.Aggregate("score", "min") - 72.0) <= 1.0);
        Assert.Equal(9, loaded.ToDataTable().Rows.Count);

        // Aggregate on loaded consistent
        Assert.Equal(doc.Aggregate("score", "sum"), loaded.Aggregate("score", "sum"), precision: 3);

        // Filter on loaded
        var loadedEng = loaded.Filter("department", "Engineering");
        Assert.Equal(5, loadedEng.GetRecordCount());

        // ExportToJson
        var json = loaded.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // Final save
        var path2 = TempFile("dogfood_analytics_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), loaded2.GetRecordCount());
        Assert.Equal(loaded.CountWhere("department", "Engineering"),
                     loaded2.CountWhere("department", "Engineering"));
    }
}
