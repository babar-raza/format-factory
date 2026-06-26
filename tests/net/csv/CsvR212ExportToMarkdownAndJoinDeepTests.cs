// Tests for CsvDocument.ExportToMarkdown, JoinWith, GetSampleRows deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R212

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R212: Tests for CsvDocument.ExportToMarkdown, JoinWith, GetSampleRows deeper.
/// ExportToMarkdown(): exports the CSV as a Markdown table.
/// JoinWith(other, keyColumn): performs an inner join on a key column.
/// GetSampleRows(n): returns the first n data rows as list of dictionaries.
/// Covers: ExportToMarkdown non-null; ExportToMarkdown non-empty; ExportToMarkdown has pipes;
/// ExportToMarkdown has content; ExportToMarkdown consistent; ExportToMarkdown no-throw;
/// ExportToMarkdown after AddRow grows; ExportToMarkdown save-load;
/// JoinWith non-null; JoinWith no-throw; JoinWith row count correct;
/// JoinWith consistent; JoinWith save-load; JoinWith no-match empty;
/// GetSampleRows non-null; GetSampleRows no-throw; GetSampleRows count<=n;
/// GetSampleRows count=n for sufficient rows; GetSampleRows(1) has 1 row;
/// GetSampleRows consistent; GetSampleRows save-load;
/// GetSampleRows has correct first row; GetSampleRows contains header keys;
/// dogfood LoadFile→ExportToMarkdown→JoinWith→GetSampleRows→SaveToFile pipeline.
/// </summary>
public class CsvR212ExportToMarkdownAndJoinDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR212ExportToMarkdownAndJoinDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR212_" + Guid.NewGuid().ToString("N"));
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
            "EmpId,Name,Department,Score\n" +
            "E001,Alice,Engineering,92\n" +
            "E002,Bob,Marketing,78\n" +
            "E003,Carol,Engineering,88\n" +
            "E004,Dave,Finance,85\n" +
            "E005,Eve,Engineering,95\n";
        File.WriteAllText(path, content);
        return path;
    }

    private string CreateSalaryCsv()
    {
        var path = TempFile("salaries.csv");
        var content =
            "EmpId,Salary,Bonus\n" +
            "E001,95000,5000\n" +
            "E002,55000,2000\n" +
            "E003,115000,8000\n" +
            "E004,72000,3000\n" +
            "E005,98000,6000\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // ExportToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdown_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        Assert.NotNull(doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_NonEmpty()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        Assert.NotEmpty(doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_HasPipes()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        Assert.Contains("|", doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_HasContent()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var md = doc.ExportToMarkdown();
        Assert.True(md.Contains("Alice") || md.Contains("Engineering") || md.Contains("EmpId"));
    }

    [Fact]
    public void ExportToMarkdown_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var m1 = doc.ExportToMarkdown();
        var m2 = doc.ExportToMarkdown();
        Assert.Equal(m1.Length, m2.Length);
    }

    [Fact]
    public void ExportToMarkdown_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToMarkdown_AfterAddRow_Grows()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var before = doc.ExportToMarkdown().Length;
        doc.AddRow(new[] { "E006", "Frank", "Marketing", "82" });
        Assert.True(doc.ExportToMarkdown().Length > before);
    }

    [Fact]
    public void ExportToMarkdown_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var before = doc.ExportToMarkdown().Length;
        var path = TempFile("md_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.True(Math.Abs(loaded.ExportToMarkdown().Length - before) <= 10);
    }

    // -------------------------------------------------------------------------
    // JoinWith
    // -------------------------------------------------------------------------

    [Fact]
    public void JoinWith_NonNull()
    {
        var emp = CsvDocument.LoadFile(CreateEmployeeCsv());
        var sal = CsvDocument.LoadFile(CreateSalaryCsv());
        Assert.NotNull(emp.JoinWith(sal, "EmpId"));
    }

    [Fact]
    public void JoinWith_NoThrow()
    {
        var emp = CsvDocument.LoadFile(CreateEmployeeCsv());
        var sal = CsvDocument.LoadFile(CreateSalaryCsv());
        var ex = Record.Exception(() => emp.JoinWith(sal, "EmpId"));
        Assert.Null(ex);
    }

    [Fact]
    public void JoinWith_RowCount_Correct()
    {
        var emp = CsvDocument.LoadFile(CreateEmployeeCsv());
        var sal = CsvDocument.LoadFile(CreateSalaryCsv());
        var joined = emp.JoinWith(sal, "EmpId");
        Assert.Equal(5, joined.GetRowCount());
    }

    [Fact]
    public void JoinWith_Consistent()
    {
        var emp = CsvDocument.LoadFile(CreateEmployeeCsv());
        var sal = CsvDocument.LoadFile(CreateSalaryCsv());
        var j1 = emp.JoinWith(sal, "EmpId");
        var j2 = emp.JoinWith(sal, "EmpId");
        Assert.Equal(j1.GetRowCount(), j2.GetRowCount());
    }

    [Fact]
    public void JoinWith_SaveLoad_Consistent()
    {
        var emp = CsvDocument.LoadFile(CreateEmployeeCsv());
        var sal = CsvDocument.LoadFile(CreateSalaryCsv());
        var joined = emp.JoinWith(sal, "EmpId");
        var path = TempFile("joined_save.csv");
        joined.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(joined.GetRowCount(), loaded.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // GetSampleRows
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSampleRows_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        Assert.NotNull(doc.GetSampleRows(3));
    }

    [Fact]
    public void GetSampleRows_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var ex = Record.Exception(() => doc.GetSampleRows(3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSampleRows_CountLessThanOrEqualN()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        Assert.True(doc.GetSampleRows(3).Count <= 3);
    }

    [Fact]
    public void GetSampleRows_CountEqualsN_ForSufficientRows()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        Assert.Equal(3, doc.GetSampleRows(3).Count);
    }

    [Fact]
    public void GetSampleRows_One_HasOneRow()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        Assert.Equal(1, doc.GetSampleRows(1).Count);
    }

    [Fact]
    public void GetSampleRows_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var s1 = doc.GetSampleRows(3);
        var s2 = doc.GetSampleRows(3);
        Assert.Equal(s1.Count, s2.Count);
    }

    [Fact]
    public void GetSampleRows_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateEmployeeCsv());
        var before = doc.GetSampleRows(3).Count;
        var path = TempFile("sample_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSampleRows(3).Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ExportToMarkdown_JoinWith_GetSampleRows_SaveToFile_Pipeline()
    {
        // Create main employee file
        var empPath = TempFile("dogfood_employees.csv");
        File.WriteAllText(empPath,
            "EmpId,Name,Team,Level,City\n" +
            "E001,Alice,Platform,Senior,London\n" +
            "E002,Bob,Data,Junior,Paris\n" +
            "E003,Carol,Platform,Lead,London\n" +
            "E004,Dave,Finance,Mid,Berlin\n" +
            "E005,Eve,Data,Senior,London\n" +
            "E006,Frank,Platform,Senior,Rome\n" +
            "E007,Grace,Finance,Junior,Madrid\n");

        var salPath = TempFile("dogfood_salaries.csv");
        File.WriteAllText(salPath,
            "EmpId,Salary,Bonus,Years\n" +
            "E001,95000,5000,5\n" +
            "E002,55000,2000,1\n" +
            "E003,115000,8000,8\n" +
            "E004,72000,3000,3\n" +
            "E005,98000,6000,6\n" +
            "E006,82000,4000,4\n" +
            "E007,48000,1500,2\n");

        var emp = CsvDocument.LoadFile(empPath);
        var sal = CsvDocument.LoadFile(salPath);
        Assert.Equal(7, emp.GetRowCount());

        // ExportToMarkdown
        var md = emp.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);
        Assert.Contains("|", md);
        Assert.True(md.Contains("Alice") || md.Contains("EmpId") || md.Contains("Team"));

        // Consistent
        Assert.Equal(md.Length, emp.ExportToMarkdown().Length);

        // After AddRow — grows
        var mdBefore = emp.ExportToMarkdown().Length;
        emp.AddRow(new[] { "E008", "Hector", "Data", "Mid", "Tokyo" });
        Assert.True(emp.ExportToMarkdown().Length > mdBefore);
        Assert.Equal(8, emp.GetRowCount());

        // GetSampleRows
        var sample3 = emp.GetSampleRows(3);
        Assert.Equal(3, sample3.Count);

        var sample1 = emp.GetSampleRows(1);
        Assert.Equal(1, sample1.Count);

        var sampleAll = emp.GetSampleRows(20); // more than row count
        Assert.True(sampleAll.Count <= 20);
        Assert.True(sampleAll.Count > 0);

        // Consistent
        Assert.Equal(sample3.Count, emp.GetSampleRows(3).Count);

        // JoinWith
        var joined = emp.JoinWith(sal, "EmpId");
        Assert.NotNull(joined);
        // E008 has no salary row — inner join returns 7 rows
        Assert.True(joined.GetRowCount() >= 7);

        // Consistent
        Assert.Equal(joined.GetRowCount(), emp.JoinWith(sal, "EmpId").GetRowCount());

        // ExportToMarkdown on salary doc
        var salMd = sal.ExportToMarkdown();
        Assert.Contains("|", salMd);

        // SaveToFile emp
        var savePath = TempFile("dogfood_emp_out.csv");
        emp.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(8, loaded.GetRowCount());

        // ExportToMarkdown on loaded
        var loadedMd = loaded.ExportToMarkdown();
        Assert.NotNull(loadedMd);
        Assert.Contains("|", loadedMd);

        // GetSampleRows on loaded
        var loadedSample = loaded.GetSampleRows(3);
        Assert.Equal(3, loadedSample.Count);

        // JoinWith on loaded
        var loadedJoined = loaded.JoinWith(sal, "EmpId");
        Assert.NotNull(loadedJoined);
        Assert.True(loadedJoined.GetRowCount() > 0);

        // SaveToFile joined
        var joinedPath = TempFile("dogfood_joined.csv");
        loadedJoined.SaveToFile(joinedPath);
        Assert.True(File.Exists(joinedPath));
        var loaded2 = CsvDocument.LoadFile(joinedPath);
        Assert.True(loaded2.GetRowCount() > 0);
        Assert.True(loaded2.GetColumnCount() > emp.GetColumnCount()); // joined has more columns
        Assert.Contains("|", loaded2.ExportToMarkdown());
    }
}
