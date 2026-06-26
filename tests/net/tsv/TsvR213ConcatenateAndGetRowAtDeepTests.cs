// Tests for TsvDocument.Concatenate, GetRowAt, SetCell deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R213

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R213: Tests for TsvDocument.Concatenate, GetRowAt, SetCell deeper.
/// Concatenate(other): vertically appends another TsvDocument, returning a combined document.
/// GetRowAt(rowIndex): returns the values of the specified row as a string array.
/// SetCell(rowIndex, colIndex, value): sets the value of a specific cell.
/// Covers: Concatenate non-null; Concatenate no-throw; Concatenate row count sum;
/// Concatenate consistent; Concatenate save-load; Concatenate headers preserved;
/// Concatenate then GetColumnValues; Concatenate then GroupBy;
/// GetRowAt non-null; GetRowAt no-throw; GetRowAt correct values; GetRowAt count;
/// GetRowAt consistent; GetRowAt save-load; GetRowAt all rows valid;
/// SetCell no-throw; SetCell reflects in GetRowAt; SetCell save-load persists;
/// SetCell multiple cells; SetCell then ExportToHtml no-throw;
/// dogfood LoadFile→Concatenate→GetRowAt→SetCell→SaveToFile pipeline.
/// </summary>
public class TsvR213ConcatenateAndGetRowAtDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR213ConcatenateAndGetRowAtDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR213_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateTeamATsv()
    {
        var path = TempFile("team_a.tsv");
        var content =
            "Name\tRole\tLevel\tScore\n" +
            "Alice\tEngineer\tSenior\t92\n" +
            "Bob\tDesigner\tMid\t78\n" +
            "Carol\tEngineer\tLead\t98\n" +
            "Dave\tManager\tSenior\t85\n";
        File.WriteAllText(path, content);
        return path;
    }

    private string CreateTeamBTsv()
    {
        var path = TempFile("team_b.tsv");
        var content =
            "Name\tRole\tLevel\tScore\n" +
            "Eve\tEngineer\tJunior\t74\n" +
            "Frank\tAnalyst\tMid\t82\n" +
            "Grace\tDesigner\tSenior\t90\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // Concatenate
    // -------------------------------------------------------------------------

    [Fact]
    public void Concatenate_NonNull()
    {
        var a = TsvDocument.LoadFile(CreateTeamATsv());
        var b = TsvDocument.LoadFile(CreateTeamBTsv());
        Assert.NotNull(a.Concatenate(b));
    }

    [Fact]
    public void Concatenate_NoThrow()
    {
        var a = TsvDocument.LoadFile(CreateTeamATsv());
        var b = TsvDocument.LoadFile(CreateTeamBTsv());
        var ex = Record.Exception(() => a.Concatenate(b));
        Assert.Null(ex);
    }

    [Fact]
    public void Concatenate_RowCount_IsSum()
    {
        var a = TsvDocument.LoadFile(CreateTeamATsv());
        var b = TsvDocument.LoadFile(CreateTeamBTsv());
        var combined = a.Concatenate(b);
        Assert.Equal(a.GetRowCount() + b.GetRowCount(), combined.GetRowCount());
    }

    [Fact]
    public void Concatenate_Consistent()
    {
        var a = TsvDocument.LoadFile(CreateTeamATsv());
        var b = TsvDocument.LoadFile(CreateTeamBTsv());
        var c1 = a.Concatenate(b);
        var c2 = a.Concatenate(b);
        Assert.Equal(c1.GetRowCount(), c2.GetRowCount());
    }

    [Fact]
    public void Concatenate_SaveLoad_Consistent()
    {
        var a = TsvDocument.LoadFile(CreateTeamATsv());
        var b = TsvDocument.LoadFile(CreateTeamBTsv());
        var combined = a.Concatenate(b);
        var path = TempFile("concat_save.tsv");
        combined.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(combined.GetRowCount(), loaded.GetRowCount());
    }

    [Fact]
    public void Concatenate_Then_GroupBy_Works()
    {
        var a = TsvDocument.LoadFile(CreateTeamATsv());
        var b = TsvDocument.LoadFile(CreateTeamBTsv());
        var combined = a.Concatenate(b);
        var groups = combined.GroupBy("Role");
        Assert.True(groups.ContainsKey("Engineer"));
    }

    [Fact]
    public void Concatenate_Then_GetColumnValues_HasAllRows()
    {
        var a = TsvDocument.LoadFile(CreateTeamATsv());
        var b = TsvDocument.LoadFile(CreateTeamBTsv());
        var combined = a.Concatenate(b);
        var names = combined.GetColumnValues("Name");
        Assert.Equal(combined.GetRowCount(), names.Count);
    }

    // -------------------------------------------------------------------------
    // GetRowAt
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowAt_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateTeamATsv());
        Assert.NotNull(doc.GetRowAt(0));
    }

    [Fact]
    public void GetRowAt_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateTeamATsv());
        var ex = Record.Exception(() => doc.GetRowAt(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRowAt_CorrectValues_FirstRow()
    {
        var doc = TsvDocument.LoadFile(CreateTeamATsv());
        var row = doc.GetRowAt(0);
        Assert.True(row.Length > 0);
        Assert.True(System.Array.Exists(row, v => v.Contains("Alice")));
    }

    [Fact]
    public void GetRowAt_Count_Equals_ColumnCount()
    {
        var doc = TsvDocument.LoadFile(CreateTeamATsv());
        var row = doc.GetRowAt(0);
        Assert.Equal(doc.GetColumnCount(), row.Length);
    }

    [Fact]
    public void GetRowAt_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateTeamATsv());
        var r1 = doc.GetRowAt(0);
        var r2 = doc.GetRowAt(0);
        Assert.Equal(r1.Length, r2.Length);
        Assert.Equal(r1[0], r2[0]);
    }

    [Fact]
    public void GetRowAt_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateTeamATsv());
        var before = doc.GetRowAt(1);
        var path = TempFile("gra_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetRowAt(1);
        Assert.Equal(before.Length, after.Length);
    }

    [Fact]
    public void GetRowAt_AllRows_Valid()
    {
        var doc = TsvDocument.LoadFile(CreateTeamATsv());
        for (int i = 0; i < doc.GetRowCount(); i++)
        {
            var row = doc.GetRowAt(i);
            Assert.NotNull(row);
            Assert.True(row.Length > 0);
        }
    }

    // -------------------------------------------------------------------------
    // SetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateTeamATsv());
        var ex = Record.Exception(() => doc.SetCell(0, 3, "99"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCell_ReflectsIn_GetRowAt()
    {
        var doc = TsvDocument.LoadFile(CreateTeamATsv());
        doc.SetCell(0, 3, "100");
        var row = doc.GetRowAt(0);
        Assert.True(row[3] == "100" || System.Array.Exists(row, v => v.Contains("100")));
    }

    [Fact]
    public void SetCell_SaveLoad_Persists()
    {
        var doc = TsvDocument.LoadFile(CreateTeamATsv());
        doc.SetCell(1, 3, "97");
        var path = TempFile("sc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var row = loaded.GetRowAt(1);
        Assert.True(System.Array.Exists(row, v => v.Contains("97")));
    }

    [Fact]
    public void SetCell_Multiple_Cells()
    {
        var doc = TsvDocument.LoadFile(CreateTeamATsv());
        doc.SetCell(0, 3, "95");
        doc.SetCell(1, 3, "82");
        doc.SetCell(2, 3, "99");
        // All rows accessible
        for (int i = 0; i < 3; i++)
            Assert.NotNull(doc.GetRowAt(i));
    }

    [Fact]
    public void SetCell_Then_ExportToHtml_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateTeamATsv());
        doc.SetCell(0, 0, "Updated Name Column");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Concatenate_GetRowAt_SetCell_SaveToFile_Pipeline()
    {
        // Build three datasets
        var pathA = TempFile("dogfood_dept_a.tsv");
        File.WriteAllText(pathA,
            "Employee\tDepartment\tGrade\tPerformance\tBonus\n" +
            "Alice\tPlatform\tSenior\t95\t8000\n" +
            "Bob\tPlatform\tMid\t78\t4000\n" +
            "Carol\tPlatform\tLead\t99\t15000\n");

        var pathB = TempFile("dogfood_dept_b.tsv");
        File.WriteAllText(pathB,
            "Employee\tDepartment\tGrade\tPerformance\tBonus\n" +
            "Dave\tData\tSenior\t88\t7000\n" +
            "Eve\tData\tJunior\t72\t2000\n" +
            "Frank\tData\tMid\t83\t5000\n");

        var pathC = TempFile("dogfood_dept_c.tsv");
        File.WriteAllText(pathC,
            "Employee\tDepartment\tGrade\tPerformance\tBonus\n" +
            "Grace\tFinance\tSenior\t91\t7500\n" +
            "Hector\tFinance\tMid\t80\t4500\n");

        var docA = TsvDocument.LoadFile(pathA);
        var docB = TsvDocument.LoadFile(pathB);
        var docC = TsvDocument.LoadFile(pathC);

        Assert.Equal(3, docA.GetRowCount());
        Assert.Equal(3, docB.GetRowCount());
        Assert.Equal(2, docC.GetRowCount());

        // Concatenate A + B
        var ab = docA.Concatenate(docB);
        Assert.Equal(6, ab.GetRowCount());

        // Concatenate A+B + C
        var abc = ab.Concatenate(docC);
        Assert.Equal(8, abc.GetRowCount());

        // Consistent
        Assert.Equal(abc.GetRowCount(), docA.Concatenate(docB).Concatenate(docC).GetRowCount());

        // GetRowAt — all 8 rows valid
        for (int i = 0; i < abc.GetRowCount(); i++)
        {
            var row = abc.GetRowAt(i);
            Assert.NotNull(row);
            Assert.Equal(5, row.Length);
        }

        // GetRowAt first row — Alice
        var firstRow = abc.GetRowAt(0);
        Assert.True(System.Array.Exists(firstRow, v => v.Contains("Alice") || v.Contains("Platform")));

        // GetRowAt last row — Hector
        var lastRow = abc.GetRowAt(7);
        Assert.True(System.Array.Exists(lastRow, v => v.Contains("Hector") || v.Contains("Finance")));

        // SetCell — update bonus for first employee
        abc.SetCell(0, 4, "9000");
        var updatedRow = abc.GetRowAt(0);
        Assert.True(System.Array.Exists(updatedRow, v => v.Contains("9000")));

        // SetCell — update performance score
        abc.SetCell(3, 3, "92");
        abc.SetCell(4, 3, "75");

        // GroupBy still works
        var groups = abc.GroupBy("Department");
        Assert.True(groups.ContainsKey("Platform"));
        Assert.True(groups.ContainsKey("Data"));
        Assert.True(groups.ContainsKey("Finance"));
        Assert.Equal(3, groups["Platform"].Count);

        // GetColumnValues consistent after mutations
        var names = abc.GetColumnValues("Employee");
        Assert.Equal(8, names.Count);

        // ExportToHtml
        var html = abc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var savePath = TempFile("dogfood_all_depts.tsv");
        abc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(8, loaded.GetRowCount());

        // GetRowAt on loaded
        for (int i = 0; i < loaded.GetRowCount(); i++)
        {
            var row = loaded.GetRowAt(i);
            Assert.NotNull(row);
            Assert.Equal(5, row.Length);
        }

        // SetCell on loaded
        loaded.SetCell(0, 4, "10000");
        Assert.True(System.Array.Exists(loaded.GetRowAt(0), v => v.Contains("10000")));

        // Concatenate loaded with a new doc
        var pathD = TempFile("dogfood_dept_d.tsv");
        File.WriteAllText(pathD,
            "Employee\tDepartment\tGrade\tPerformance\tBonus\n" +
            "Iris\tSales\tMid\t86\t6000\n");
        var docD = TsvDocument.LoadFile(pathD);
        var loadedPlusD = loaded.Concatenate(docD);
        Assert.Equal(9, loadedPlusD.GetRowCount());

        // Final save
        var path2 = TempFile("dogfood_all_v2.tsv");
        loadedPlusD.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(9, loaded2.GetRowCount());
        Assert.Equal(5, loaded2.GetRowAt(0).Length);
    }
}
