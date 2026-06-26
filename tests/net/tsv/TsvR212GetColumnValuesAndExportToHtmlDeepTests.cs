// Tests for TsvDocument.GetColumnValues, ExportToHtml, GetNullCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R212

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R212: Tests for TsvDocument.GetColumnValues, ExportToHtml, GetNullCount deeper.
/// GetColumnValues(colName): returns all values in a named column as a list.
/// ExportToHtml(): returns the document as an HTML table string.
/// GetNullCount(colName): returns the number of empty/null cells in the column.
/// Covers: GetColumnValues non-null; GetColumnValues no-throw; GetColumnValues count;
/// GetColumnValues all non-null; GetColumnValues correct values; GetColumnValues consistent;
/// GetColumnValues save-load; GetColumnValues after AddRow;
/// ExportToHtml non-null; ExportToHtml no-throw; ExportToHtml non-empty;
/// ExportToHtml has table tags; ExportToHtml has header; ExportToHtml consistent;
/// ExportToHtml save-load; ExportToHtml after AddRow grows;
/// GetNullCount no-throw; GetNullCount non-negative; GetNullCount consistent;
/// GetNullCount sparse column; GetNullCount save-load;
/// dogfood LoadFile→GetColumnValues→ExportToHtml→GetNullCount→SaveToFile pipeline.
/// </summary>
public class TsvR212GetColumnValuesAndExportToHtmlDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR212GetColumnValuesAndExportToHtmlDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR212_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateStaffTsv()
    {
        var path = TempFile("staff.tsv");
        var content =
            "Name\tDepartment\tLevel\tSalary\tCity\n" +
            "Alice\tEngineering\tSenior\t95000\tLondon\n" +
            "Bob\tMarketing\tMid\t72000\tParis\n" +
            "Carol\tEngineering\tLead\t115000\tLondon\n" +
            "Dave\tFinance\tJunior\t58000\tBerlin\n" +
            "Eve\tEngineering\tSenior\t99000\tLondon\n" +
            "Frank\tMarketing\tSenior\t81000\tRome\n" +
            "Grace\tFinance\tMid\t76000\tMadrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    private string CreateSparseNullTsv()
    {
        var path = TempFile("sparse.tsv");
        var content =
            "Name\tDepartment\tBonus\n" +
            "Alice\tEngineering\t5000\n" +
            "Bob\tMarketing\t\n" +
            "Carol\tEngineering\t3000\n" +
            "Dave\tFinance\t\n" +
            "Eve\tEngineering\t4500\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        Assert.NotNull(doc.GetColumnValues("Department"));
    }

    [Fact]
    public void GetColumnValues_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        var ex = Record.Exception(() => doc.GetColumnValues("Name"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnValues_Count_Equals_RowCount()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        var values = doc.GetColumnValues("Name");
        Assert.Equal(doc.GetRowCount(), values.Count);
    }

    [Fact]
    public void GetColumnValues_AllNonNull()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        var values = doc.GetColumnValues("Department");
        foreach (var v in values)
            Assert.NotNull(v);
    }

    [Fact]
    public void GetColumnValues_CorrectValues()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        var values = doc.GetColumnValues("Name");
        Assert.True(values.Contains("Alice") || values.Exists(v => v.Contains("Alice")));
        Assert.True(values.Contains("Carol") || values.Exists(v => v.Contains("Carol")));
    }

    [Fact]
    public void GetColumnValues_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        var v1 = doc.GetColumnValues("Level");
        var v2 = doc.GetColumnValues("Level");
        Assert.Equal(v1.Count, v2.Count);
    }

    [Fact]
    public void GetColumnValues_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        var before = doc.GetColumnValues("City").Count;
        var path = TempFile("gcv_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnValues("City").Count);
    }

    [Fact]
    public void GetColumnValues_AfterAddRow_Grows()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        var before = doc.GetColumnValues("Name").Count;
        doc.AddRow(new[] { "Hector", "Engineering", "Senior", "105000", "Tokyo" });
        Assert.Equal(before + 1, doc.GetColumnValues("Name").Count);
    }

    // -------------------------------------------------------------------------
    // ExportToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        Assert.NotNull(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToHtml_NonEmpty()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        Assert.NotEmpty(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_HasTableTags()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("<table") || html.Contains("<TABLE") || html.Contains("<tr") || html.Contains("<td"));
    }

    [Fact]
    public void ExportToHtml_HasHeaderColumns()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("Name") || html.Contains("Department"));
    }

    [Fact]
    public void ExportToHtml_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        var h1 = doc.ExportToHtml();
        var h2 = doc.ExportToHtml();
        Assert.Equal(h1.Length, h2.Length);
    }

    [Fact]
    public void ExportToHtml_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        var before = doc.ExportToHtml().Length;
        var path = TempFile("html_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.True(Math.Abs(loaded.ExportToHtml().Length - before) <= 20);
    }

    [Fact]
    public void ExportToHtml_AfterAddRow_Grows()
    {
        var doc = TsvDocument.LoadFile(CreateStaffTsv());
        var before = doc.ExportToHtml().Length;
        doc.AddRow(new[] { "Iris", "Finance", "Lead", "88000", "Sydney" });
        Assert.True(doc.ExportToHtml().Length > before);
    }

    // -------------------------------------------------------------------------
    // GetNullCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNullCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSparseNullTsv());
        var ex = Record.Exception(() => doc.GetNullCount("Bonus"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNullCount_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSparseNullTsv());
        Assert.True(doc.GetNullCount("Bonus") >= 0);
    }

    [Fact]
    public void GetNullCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSparseNullTsv());
        Assert.Equal(doc.GetNullCount("Bonus"), doc.GetNullCount("Bonus"));
    }

    [Fact]
    public void GetNullCount_SparseColumn_NonZero()
    {
        var doc = TsvDocument.LoadFile(CreateSparseNullTsv());
        // Bob and Dave have empty Bonus — 2 nulls out of 5
        Assert.True(doc.GetNullCount("Bonus") > 0);
    }

    [Fact]
    public void GetNullCount_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSparseNullTsv());
        var before = doc.GetNullCount("Bonus");
        var path = TempFile("nc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNullCount("Bonus"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnValues_ExportToHtml_GetNullCount_SaveToFile_Pipeline()
    {
        // Build comprehensive TSV
        var path = TempFile("dogfood_staff.tsv");
        var content =
            "Employee\tTeam\tGrade\tLocation\tBonus\tYearsExp\n" +
            "Alice\tPlatform\tSenior\tLondon\t8000\t7\n" +
            "Bob\tData\tJunior\tParis\t\t2\n" +
            "Carol\tPlatform\tLead\tLondon\t15000\t12\n" +
            "Dave\tFinance\tMid\tBerlin\t4000\t5\n" +
            "Eve\tData\tSenior\tLondon\t9000\t8\n" +
            "Frank\tPlatform\tSenior\tRome\t7500\t6\n" +
            "Grace\tFinance\tJunior\tMadrid\t\t1\n" +
            "Hector\tData\tMid\tTokyo\t5000\t4\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRowCount());

        // GetColumnValues — Employee
        var names = doc.GetColumnValues("Employee");
        Assert.NotNull(names);
        Assert.Equal(8, names.Count);
        Assert.True(names.Contains("Alice") || names.Exists(n => n.Contains("Alice")));
        Assert.True(names.Contains("Carol") || names.Exists(n => n.Contains("Carol")));
        foreach (var n in names) Assert.NotNull(n);

        // GetColumnValues — Team
        var teams = doc.GetColumnValues("Team");
        Assert.Equal(8, teams.Count);
        Assert.True(teams.Exists(t => t.Contains("Platform")));
        Assert.True(teams.Exists(t => t.Contains("Data")));

        // Consistent
        Assert.Equal(names.Count, doc.GetColumnValues("Employee").Count);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);
        Assert.True(html.Contains("<table") || html.Contains("<tr") || html.Contains("<td") || html.Contains("Employee"));

        // Consistent
        Assert.Equal(html.Length, doc.ExportToHtml().Length);

        // GetNullCount — Bonus (Bob and Grace have empty bonus)
        var nullCount = doc.GetNullCount("Bonus");
        Assert.True(nullCount >= 0);
        Assert.True(nullCount > 0); // Bob and Grace
        Assert.Equal(nullCount, doc.GetNullCount("Bonus")); // consistent

        // GetNullCount — non-sparse column
        var nameNulls = doc.GetNullCount("Employee");
        Assert.Equal(0, nameNulls);

        // AddRow and recheck
        doc.AddRow(new[] { "Iris", "Platform", "Mid", "Sydney", "", "3" });
        Assert.Equal(9, doc.GetRowCount());
        Assert.Equal(9, doc.GetColumnValues("Employee").Count);
        // Null count for Bonus should increase by 1
        Assert.Equal(nullCount + 1, doc.GetNullCount("Bonus"));

        // ExportToHtml grows after AddRow
        Assert.True(doc.ExportToHtml().Length > html.Length);

        // SaveToFile
        var savePath = TempFile("dogfood_staff_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRowCount());
        Assert.Equal(9, loaded.GetColumnValues("Employee").Count);
        Assert.Equal(nullCount + 1, loaded.GetNullCount("Bonus"));
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // SortByColumn still works after all operations
        var sorted = loaded.SortByColumn("YearsExp", ascending: true);
        Assert.Equal(9, sorted.GetRowCount());

        // Final save
        var path2 = TempFile("dogfood_staff_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetNullCount("Bonus"), loaded2.GetNullCount("Bonus"));
    }
}
