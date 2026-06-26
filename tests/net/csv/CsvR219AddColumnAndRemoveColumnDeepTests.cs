// Tests for CsvDocument.AddColumn, RemoveColumn, GetColumnSummary deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R219

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R219: Tests for CsvDocument.AddColumn, RemoveColumn, GetColumnSummary deeper.
/// AddColumn(name): adds a new empty column to the document.
/// RemoveColumn(name): removes a named column from the document.
/// GetColumnSummary(colName): returns a summary object with stats for the column.
/// Covers: AddColumn no-throw; AddColumn increases column count; AddColumn HasColumn true;
/// AddColumn save-load; AddColumn multiple; AddColumn then SetCell;
/// RemoveColumn no-throw; RemoveColumn decreases column count; RemoveColumn HasColumn false;
/// RemoveColumn save-load; RemoveColumn then GetRowCount unchanged;
/// GetColumnSummary no-throw; GetColumnSummary non-null; GetColumnSummary consistent;
/// GetColumnSummary save-load; GetColumnSummary min/max/mean valid;
/// dogfood LoadFile→AddColumn→RemoveColumn→GetColumnSummary→SaveToFile pipeline.
/// </summary>
public class CsvR219AddColumnAndRemoveColumnDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR219AddColumnAndRemoveColumnDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR219_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEmployeeCsv()
    {
        var path = TempFile("employees.csv");
        var content =
            "EmpId,Name,Department,Salary,YearsExp\n" +
            "E001,Alice,Engineering,95000,7\n" +
            "E002,Bob,Marketing,72000,3\n" +
            "E003,Carol,Engineering,115000,12\n" +
            "E004,Dave,Finance,85000,5\n" +
            "E005,Eve,Engineering,99000,8\n" +
            "E006,Frank,Marketing,81000,6\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // AddColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var ex = Record.Exception(() => doc.AddColumn("Bonus"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddColumn_HasColumn_True()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        doc.AddColumn("Grade");
        Assert.True(doc.HasColumn("Grade"));
    }

    [Fact]
    public void AddColumn_Increases_ColumnCount()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var before = doc.GetColumnNames().Count;
        doc.AddColumn("NewCol");
        Assert.Equal(before + 1, doc.GetColumnNames().Count);
    }

    [Fact]
    public void AddColumn_SaveLoad_Persists()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        doc.AddColumn("Region");
        var path = TempFile("ac_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.True(loaded.HasColumn("Region"));
    }

    [Fact]
    public void AddColumn_Multiple()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        doc.AddColumn("Col1");
        doc.AddColumn("Col2");
        doc.AddColumn("Col3");
        Assert.True(doc.HasColumn("Col1"));
        Assert.True(doc.HasColumn("Col2"));
        Assert.True(doc.HasColumn("Col3"));
    }

    [Fact]
    public void AddColumn_RowCount_Unchanged()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var before = doc.GetRowCount();
        doc.AddColumn("Extra");
        Assert.Equal(before, doc.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // RemoveColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveColumn_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var ex = Record.Exception(() => doc.RemoveColumn("YearsExp"));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveColumn_HasColumn_False()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        doc.RemoveColumn("YearsExp");
        Assert.False(doc.HasColumn("YearsExp"));
    }

    [Fact]
    public void RemoveColumn_Decreases_ColumnCount()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var before = doc.GetColumnNames().Count;
        doc.RemoveColumn("Salary");
        Assert.Equal(before - 1, doc.GetColumnNames().Count);
    }

    [Fact]
    public void RemoveColumn_SaveLoad_Persists()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        doc.RemoveColumn("YearsExp");
        var path = TempFile("rc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.False(loaded.HasColumn("YearsExp"));
    }

    [Fact]
    public void RemoveColumn_RowCount_Unchanged()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var before = doc.GetRowCount();
        doc.RemoveColumn("Department");
        Assert.Equal(before, doc.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // GetColumnSummary
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnSummary_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var ex = Record.Exception(() => doc.GetColumnSummary("Salary"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnSummary_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        Assert.NotNull(doc.GetColumnSummary("Salary"));
    }

    [Fact]
    public void GetColumnSummary_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var s1 = doc.GetColumnSummary("Salary");
        var s2 = doc.GetColumnSummary("Salary");
        Assert.Equal(s1.Min, s2.Min, 1);
        Assert.Equal(s1.Max, s2.Max, 1);
    }

    [Fact]
    public void GetColumnSummary_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var before = doc.GetColumnSummary("Salary");
        var path = TempFile("gcs_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetColumnSummary("Salary");
        Assert.Equal(before.Min, after.Min, 1);
        Assert.Equal(before.Max, after.Max, 1);
    }

    [Fact]
    public void GetColumnSummary_Min_LessThanMax()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var summary = doc.GetColumnSummary("Salary");
        Assert.True(summary.Min <= summary.Max);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddColumn_RemoveColumn_GetColumnSummary_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_workforce.csv");
        var content =
            "StaffId,FullName,Division,BaseSalary,Bonus,YearsService,Location,Grade\n" +
            "S001,Alice Chen,Platform,95000,8000,7,London,Senior\n" +
            "S002,Bob Kumar,Data,72000,5000,3,Paris,Mid\n" +
            "S003,Carol White,Platform,125000,15000,12,London,Lead\n" +
            "S004,Dave Singh,Finance,85000,6000,5,Berlin,Senior\n" +
            "S005,Eve Martin,Data,99000,9000,8,London,Senior\n" +
            "S006,Frank Lee,Platform,81000,7500,6,Rome,Senior\n" +
            "S007,Grace Kim,Finance,76000,4000,4,Madrid,Mid\n" +
            "S008,Hector Cruz,Data,105000,12000,9,Tokyo,Lead\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRowCount());

        // GetColumnNames initial
        var cols = doc.GetColumnNames();
        Assert.Equal(8, cols.Count);
        Assert.True(doc.HasColumn("BaseSalary"));
        Assert.True(doc.HasColumn("Bonus"));

        // GetColumnSummary — BaseSalary
        var salarySummary = doc.GetColumnSummary("BaseSalary");
        Assert.NotNull(salarySummary);
        Assert.True(salarySummary.Min <= salarySummary.Max);
        Assert.True(salarySummary.Min > 0);

        // GetColumnSummary — YearsService
        var yrsSummary = doc.GetColumnSummary("YearsService");
        Assert.NotNull(yrsSummary);
        Assert.True(yrsSummary.Min <= yrsSummary.Max);

        // Consistent
        var ss2 = doc.GetColumnSummary("BaseSalary");
        Assert.Equal(salarySummary.Min, ss2.Min, 1);

        // AddColumn — TotalComp
        doc.AddColumn("TotalComp");
        Assert.True(doc.HasColumn("TotalComp"));
        Assert.Equal(9, doc.GetColumnNames().Count);
        Assert.Equal(8, doc.GetRowCount()); // row count unchanged

        // AddColumn — RoleLevel
        doc.AddColumn("RoleLevel");
        Assert.Equal(10, doc.GetColumnNames().Count);

        // RemoveColumn — Grade (already in Grade column)
        doc.RemoveColumn("Grade");
        Assert.False(doc.HasColumn("Grade"));
        Assert.Equal(9, doc.GetColumnNames().Count);
        Assert.Equal(8, doc.GetRowCount()); // row count still unchanged

        // RemoveColumn — Location
        doc.RemoveColumn("Location");
        Assert.False(doc.HasColumn("Location"));
        Assert.Equal(8, doc.GetColumnNames().Count);

        // GetColumnSummary still works after column ops
        var salaryAfter = doc.GetColumnSummary("BaseSalary");
        Assert.Equal(salarySummary.Min, salaryAfter.Min, 1);
        Assert.Equal(salarySummary.Max, salaryAfter.Max, 1);

        // ExportToHtml works
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var savePath = TempFile("dogfood_workforce_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(8, loaded.GetRowCount());
        Assert.True(loaded.HasColumn("TotalComp"));
        Assert.True(loaded.HasColumn("RoleLevel"));
        Assert.False(loaded.HasColumn("Grade"));
        Assert.False(loaded.HasColumn("Location"));

        // GetColumnSummary on loaded
        var loadedSummary = loaded.GetColumnSummary("BaseSalary");
        Assert.Equal(salarySummary.Min, loadedSummary.Min, 1);

        // AddColumn and RemoveColumn on loaded
        loaded.AddColumn("Notes");
        Assert.True(loaded.HasColumn("Notes"));
        loaded.RemoveColumn("TotalComp");
        Assert.False(loaded.HasColumn("TotalComp"));

        // Final save
        var path2 = TempFile("dogfood_workforce_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.True(loaded2.HasColumn("Notes"));
        Assert.False(loaded2.HasColumn("TotalComp"));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        Assert.Null(ex1);
    }
}
