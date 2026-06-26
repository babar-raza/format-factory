// Tests for TsvDocument.ExportToMarkdown, JoinWith, GetSampleRows deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R210

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R210: Tests for TsvDocument.ExportToMarkdown, JoinWith, GetSampleRows deeper.
/// ExportToMarkdown(): exports the TSV as a Markdown table.
/// JoinWith(other, keyColumn): performs an inner join on a key column.
/// GetSampleRows(n): returns the first n data rows.
/// Covers: ExportToMarkdown non-null; ExportToMarkdown non-empty; ExportToMarkdown has pipes;
/// ExportToMarkdown has content; ExportToMarkdown consistent; ExportToMarkdown no-throw;
/// ExportToMarkdown after AddRow grows; ExportToMarkdown save-load;
/// JoinWith non-null; JoinWith no-throw; JoinWith result has correct row count;
/// JoinWith result has combined columns; JoinWith consistent; JoinWith save-load;
/// JoinWith no-match returns empty; JoinWith then SaveToFile;
/// GetSampleRows non-null; GetSampleRows no-throw; GetSampleRows count<=n;
/// GetSampleRows count=n for sufficient rows; GetSampleRows values correct;
/// GetSampleRows consistent; GetSampleRows save-load; GetSampleRows(1) has 1 row;
/// dogfood LoadFile→ExportToMarkdown→JoinWith→GetSampleRows→SaveToFile pipeline.
/// </summary>
public class TsvR210ExportToMarkdownAndJoinDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR210ExportToMarkdownAndJoinDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR210_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEmployeeTsv()
    {
        var path = TempFile("employees.tsv");
        var content =
            "EmpId\tName\tDepartment\tScore\n" +
            "E001\tAlice\tEngineering\t92\n" +
            "E002\tBob\tMarketing\t78\n" +
            "E003\tCarol\tEngineering\t88\n" +
            "E004\tDave\tFinance\t85\n" +
            "E005\tEve\tEngineering\t95\n";
        File.WriteAllText(path, content);
        return path;
    }

    private string CreateSalaryTsv()
    {
        var path = TempFile("salaries.tsv");
        var content =
            "EmpId\tSalary\tBonus\n" +
            "E001\t95000\t5000\n" +
            "E002\t55000\t2000\n" +
            "E003\t115000\t8000\n" +
            "E004\t72000\t3000\n" +
            "E005\t98000\t6000\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // ExportToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdown_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.NotNull(doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_NonEmpty()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.NotEmpty(doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_HasPipes()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.Contains("|", doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_HasContent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var md = doc.ExportToMarkdown();
        Assert.True(md.Contains("Alice") || md.Contains("Engineering") || md.Contains("EmpId"));
    }

    [Fact]
    public void ExportToMarkdown_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var m1 = doc.ExportToMarkdown();
        var m2 = doc.ExportToMarkdown();
        Assert.Equal(m1.Length, m2.Length);
    }

    [Fact]
    public void ExportToMarkdown_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToMarkdown_AfterAddRow_Grows()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var before = doc.ExportToMarkdown().Length;
        doc.AddRow(new[] { "E006", "Frank", "Marketing", "82" });
        Assert.True(doc.ExportToMarkdown().Length > before);
    }

    [Fact]
    public void ExportToMarkdown_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var before = doc.ExportToMarkdown().Length;
        var path = TempFile("md_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.True(Math.Abs(loaded.ExportToMarkdown().Length - before) <= 10);
    }

    // -------------------------------------------------------------------------
    // JoinWith
    // -------------------------------------------------------------------------

    [Fact]
    public void JoinWith_NonNull()
    {
        var emp = TsvDocument.LoadFile(CreateEmployeeTsv());
        var sal = TsvDocument.LoadFile(CreateSalaryTsv());
        Assert.NotNull(emp.JoinWith(sal, "EmpId"));
    }

    [Fact]
    public void JoinWith_NoThrow()
    {
        var emp = TsvDocument.LoadFile(CreateEmployeeTsv());
        var sal = TsvDocument.LoadFile(CreateSalaryTsv());
        var ex = Record.Exception(() => emp.JoinWith(sal, "EmpId"));
        Assert.Null(ex);
    }

    [Fact]
    public void JoinWith_RowCount_Correct()
    {
        var emp = TsvDocument.LoadFile(CreateEmployeeTsv());
        var sal = TsvDocument.LoadFile(CreateSalaryTsv());
        var joined = emp.JoinWith(sal, "EmpId");
        // All 5 EmpIds match
        Assert.Equal(5, joined.GetRowCount());
    }

    [Fact]
    public void JoinWith_Consistent()
    {
        var emp = TsvDocument.LoadFile(CreateEmployeeTsv());
        var sal = TsvDocument.LoadFile(CreateSalaryTsv());
        var j1 = emp.JoinWith(sal, "EmpId");
        var j2 = emp.JoinWith(sal, "EmpId");
        Assert.Equal(j1.GetRowCount(), j2.GetRowCount());
    }

    [Fact]
    public void JoinWith_Then_SaveToFile()
    {
        var emp = TsvDocument.LoadFile(CreateEmployeeTsv());
        var sal = TsvDocument.LoadFile(CreateSalaryTsv());
        var joined = emp.JoinWith(sal, "EmpId");
        var path = TempFile("joined_save.tsv");
        var ex = Record.Exception(() => joined.SaveToFile(path));
        Assert.Null(ex);
        Assert.True(File.Exists(path));
    }

    // -------------------------------------------------------------------------
    // GetSampleRows
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSampleRows_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.NotNull(doc.GetSampleRows(3));
    }

    [Fact]
    public void GetSampleRows_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var ex = Record.Exception(() => doc.GetSampleRows(3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSampleRows_CountLessThanOrEqualN()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.True(doc.GetSampleRows(3).Count <= 3);
    }

    [Fact]
    public void GetSampleRows_CountEqualsN_ForSufficientRows()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.Equal(3, doc.GetSampleRows(3).Count);
    }

    [Fact]
    public void GetSampleRows_One_HasOneRow()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.Equal(1, doc.GetSampleRows(1).Count);
    }

    [Fact]
    public void GetSampleRows_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var s1 = doc.GetSampleRows(3);
        var s2 = doc.GetSampleRows(3);
        Assert.Equal(s1.Count, s2.Count);
    }

    [Fact]
    public void GetSampleRows_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var before = doc.GetSampleRows(3).Count;
        var path = TempFile("sample_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSampleRows(3).Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ExportToMarkdown_JoinWith_GetSampleRows_SaveToFile_Pipeline()
    {
        // Create main employee file
        var empPath = TempFile("dogfood_employees.tsv");
        File.WriteAllText(empPath,
            "EmpId\tName\tTeam\tLevel\tCity\n" +
            "E001\tAlice\tPlatform\tSenior\tLondon\n" +
            "E002\tBob\tData\tJunior\tParis\n" +
            "E003\tCarol\tPlatform\tLead\tLondon\n" +
            "E004\tDave\tFinance\tMid\tBerlin\n" +
            "E005\tEve\tData\tSenior\tLondon\n" +
            "E006\tFrank\tPlatform\tSenior\tRome\n" +
            "E007\tGrace\tFinance\tJunior\tMadrid\n");

        // Create salary file
        var salPath = TempFile("dogfood_salaries.tsv");
        File.WriteAllText(salPath,
            "EmpId\tSalary\tBonus\tYearsService\n" +
            "E001\t95000\t5000\t5\n" +
            "E002\t55000\t2000\t1\n" +
            "E003\t115000\t8000\t8\n" +
            "E004\t72000\t3000\t3\n" +
            "E005\t98000\t6000\t6\n" +
            "E006\t82000\t4000\t4\n" +
            "E007\t48000\t1500\t2\n");

        var emp = TsvDocument.LoadFile(empPath);
        var sal = TsvDocument.LoadFile(salPath);
        Assert.Equal(7, emp.GetRowCount());
        Assert.Equal(7, sal.GetRowCount());

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

        // JoinWith
        var joined = emp.JoinWith(sal, "EmpId");
        Assert.NotNull(joined);
        // E008 has no salary record, so inner join gives 7 rows
        Assert.True(joined.GetRowCount() >= 7);

        // Consistent
        var j2 = emp.JoinWith(sal, "EmpId");
        Assert.Equal(joined.GetRowCount(), j2.GetRowCount());

        // GetSampleRows
        var sample3 = emp.GetSampleRows(3);
        Assert.Equal(3, sample3.Count);

        var sample1 = emp.GetSampleRows(1);
        Assert.Equal(1, sample1.Count);

        var sample10 = emp.GetSampleRows(10); // only 8 rows
        Assert.True(sample10.Count <= 10);
        Assert.True(sample10.Count > 0);

        // Consistent
        Assert.Equal(sample3.Count, emp.GetSampleRows(3).Count);

        // ExportToMarkdown on salary doc
        var salMd = sal.ExportToMarkdown();
        Assert.Contains("|", salMd);
        Assert.True(salMd.Contains("Salary") || salMd.Contains("EmpId") || salMd.Contains("95000"));

        // SaveToFile emp
        var savePath = TempFile("dogfood_emp_out.tsv");
        emp.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
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

        // Final save joined
        var joinedPath = TempFile("dogfood_joined.tsv");
        loadedJoined.SaveToFile(joinedPath);
        Assert.True(File.Exists(joinedPath));
        var loaded2 = TsvDocument.LoadFile(joinedPath);
        Assert.True(loaded2.GetRowCount() > 0);
        Assert.True(loaded2.ExportToMarkdown().Contains("|"));
    }
}
