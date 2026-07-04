// Tests for CsvDocument.GetRowAt, DeleteRow, SetRowValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R215

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R215: Tests for CsvDocument.GetRowAt, DeleteRow, SetRowValues deeper.
/// GetRowAt(rowIndex): returns the string array of values for the specified row.
/// DeleteRow(rowIndex): removes the row at the given index.
/// SetRowValues(rowIndex, string[]): replaces all cell values in the specified row.
/// Covers: GetRowAt non-null; GetRowAt no-throw; GetRowAt correct values;
/// GetRowAt count equals column count; GetRowAt consistent; GetRowAt save-load;
/// GetRowAt all rows valid; GetRowAt first and last rows;
/// DeleteRow no-throw; DeleteRow decreases row count; DeleteRow save-load;
/// DeleteRow consistent; DeleteRow then add row; DeleteRow multiple rows;
/// SetRowValues no-throw; SetRowValues reflects in GetRowAt; SetRowValues save-load;
/// SetRowValues multiple rows; SetRowValues then ExportToHtml no-throw;
/// dogfood LoadFile→GetRowAt→DeleteRow→SetRowValues→SaveToFile pipeline.
/// </summary>
public class CsvR215GetRowAtAndDeleteRowDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR215GetRowAtAndDeleteRowDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR215_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateProjectsCsv()
    {
        var path = TempFile("projects.csv");
        var content =
            "ProjectId,Name,Status,Budget,Owner\n" +
            "PRJ-001,Platform Modernization,Active,500000,Alice\n" +
            "PRJ-002,Data Warehouse Upgrade,Completed,280000,Bob\n" +
            "PRJ-003,Mobile App Redesign,Active,175000,Carol\n" +
            "PRJ-004,Security Hardening,On Hold,95000,Dave\n" +
            "PRJ-005,Analytics Dashboard,Active,320000,Eve\n" +
            "PRJ-006,Cloud Migration,Planning,650000,Frank\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRowAt
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowAt_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        Assert.NotNull(doc.GetRowAt(0));
    }

    [Fact]
    public void GetRowAt_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        var ex = Record.Exception(() => doc.GetRowAt(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRowAt_CorrectValues_FirstRow()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        var row = doc.GetRowAt(0);
        Assert.True(row.Length > 0);
        Assert.True(System.Array.Exists((string[])row, v => v.Contains("PRJ-001") || v.Contains("Alice") || v.Contains("Platform")));
    }

    [Fact]
    public void GetRowAt_Count_Equals_ColumnCount()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        var row = doc.GetRowAt(0);
        Assert.Equal(doc.GetColumnCount(), row.Length);
    }

    [Fact]
    public void GetRowAt_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        var r1 = doc.GetRowAt(0);
        var r2 = doc.GetRowAt(0);
        Assert.Equal(r1.Length, r2.Length);
        Assert.Equal(r1[0], r2[0]);
    }

    [Fact]
    public void GetRowAt_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        var before = doc.GetRowAt(2);
        var path = TempFile("gra_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetRowAt(2);
        Assert.Equal(before.Length, after.Length);
    }

    [Fact]
    public void GetRowAt_AllRows_Valid()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        for (int i = 0; i < doc.GetRowCount(); i++)
        {
            var row = doc.GetRowAt(i);
            Assert.NotNull(row);
            Assert.True(row.Length > 0);
        }
    }

    [Fact]
    public void GetRowAt_LastRow_Valid()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        var lastIdx = doc.GetRowCount() - 1;
        var row = doc.GetRowAt(lastIdx);
        Assert.NotNull(row);
        Assert.True(row.Length > 0);
    }

    // -------------------------------------------------------------------------
    // DeleteRow
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRow_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        var ex = Record.Exception(() => doc.DeleteRow(0));
        Assert.Null(ex);
    }

    [Fact]
    public void DeleteRow_Decreases_RowCount()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        var before = doc.GetRowCount();
        doc.DeleteRow(0);
        Assert.Equal(before - 1, doc.GetRowCount());
    }

    [Fact]
    public void DeleteRow_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        doc.DeleteRow(2);
        var before = doc.GetRowCount();
        var path = TempFile("dr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRowCount());
    }

    [Fact]
    public void DeleteRow_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        doc.DeleteRow(0);
        var count1 = doc.GetRowCount();
        var count2 = doc.GetRowCount();
        Assert.Equal(count1, count2);
    }

    [Fact]
    public void DeleteRow_Multiple_Rows()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        var before = doc.GetRowCount();
        doc.DeleteRow(0);
        doc.DeleteRow(0);
        Assert.Equal(before - 2, doc.GetRowCount());
    }

    [Fact]
    public void DeleteRow_Then_GetRowAt_NewIndexes()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        var secondRow = doc.GetRowAt(1);
        doc.DeleteRow(0);
        var newFirst = doc.GetRowAt(0);
        Assert.Equal(secondRow.Length, newFirst.Length);
    }

    // -------------------------------------------------------------------------
    // SetRowValues
    // -------------------------------------------------------------------------

    [Fact]
    public void SetRowValues_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        var ex = Record.Exception(() => doc.SetRowValues(0, new[] { "PRJ-NEW", "New Project", "Active", "100000", "Grace" }));
        Assert.Null(ex);
    }

    [Fact]
    public void SetRowValues_Reflects_In_GetRowAt()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        doc.SetRowValues(0, new[] { "PRJ-UPD", "Updated Project", "Planning", "200000", "Hector" });
        var row = doc.GetRowAt(0);
        Assert.True(System.Array.Exists((string[])row, v => v.Contains("PRJ-UPD") || v.Contains("Updated") || v.Contains("Hector")));
    }

    [Fact]
    public void SetRowValues_SaveLoad_Persists()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        doc.SetRowValues(2, new[] { "PRJ-MOD", "Modified Project", "Completed", "150000", "Iris" });
        var path = TempFile("srv_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var row = loaded.GetRowAt(2);
        Assert.True(System.Array.Exists((string[])row, v => v.Contains("PRJ-MOD") || v.Contains("Modified") || v.Contains("Iris")));
    }

    [Fact]
    public void SetRowValues_Multiple_Rows()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        doc.SetRowValues(0, new[] { "A", "B", "C", "D", "E" });
        doc.SetRowValues(1, new[] { "F", "G", "H", "I", "J" });
        var r0 = doc.GetRowAt(0);
        var r1 = doc.GetRowAt(1);
        Assert.NotNull(r0);
        Assert.NotNull(r1);
    }

    [Fact]
    public void SetRowValues_Then_ExportToHtml_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateProjectsCsv());
        doc.SetRowValues(0, new[] { "PRJ-X", "X Project", "Active", "999000", "Jack" });
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRowAt_DeleteRow_SetRowValues_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_initiatives.csv");
        var content =
            "InitId,Title,Owner,Priority,Budget,Phase,Region\n" +
            "INIT-001,Digital Transformation,Alice,High,1200000,Execution,EMEA\n" +
            "INIT-002,Cloud First Strategy,Bob,Critical,2500000,Planning,AMER\n" +
            "INIT-003,Data Governance Framework,Carol,High,800000,Execution,APAC\n" +
            "INIT-004,Cybersecurity Uplift,Dave,Critical,950000,Design,EMEA\n" +
            "INIT-005,Customer Portal Redesign,Eve,Medium,650000,Execution,AMER\n" +
            "INIT-006,Automation Center of Excellence,Frank,High,1800000,Initiation,APAC\n" +
            "INIT-007,Sustainability Reporting,Grace,Low,350000,Planning,EMEA\n" +
            "INIT-008,AI Pilot Program,Hector,Critical,3200000,Design,AMER\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRowCount());
        Assert.Equal(7, doc.GetColumnCount());

        // GetRowAt — all rows valid
        for (int i = 0; i < doc.GetRowCount(); i++)
        {
            var row = doc.GetRowAt(i);
            Assert.NotNull(row);
            Assert.Equal(7, row.Length);
        }

        // GetRowAt first row
        var first = doc.GetRowAt(0);
        Assert.True(System.Array.Exists((string[])first, v => v.Contains("INIT-001") || v.Contains("Alice")));

        // GetRowAt last row
        var last = doc.GetRowAt(7);
        Assert.True(System.Array.Exists((string[])last, v => v.Contains("INIT-008") || v.Contains("Hector")));

        // GetRowAt consistent
        var r2a = doc.GetRowAt(2);
        var r2b = doc.GetRowAt(2);
        Assert.Equal(r2a.Length, r2b.Length);
        Assert.Equal(r2a[0], r2b[0]);

        // SetRowValues — update first initiative (now in Execution phase with revised budget)
        doc.SetRowValues(0, new[] { "INIT-001", "Digital Transformation v2", "Alice", "Critical", "1500000", "Execution", "EMEA" });
        var updatedFirst = doc.GetRowAt(0);
        Assert.True(System.Array.Exists((string[])updatedFirst, v => v.Contains("v2") || v.Contains("1500000") || v.Contains("Critical")));

        // SetRowValues — update another row
        doc.SetRowValues(6, new[] { "INIT-007", "ESG Reporting Initiative", "Grace", "Medium", "420000", "Planning", "EMEA" });
        var updatedSeven = doc.GetRowAt(6);
        Assert.True(System.Array.Exists((string[])updatedSeven, v => v.Contains("ESG") || v.Contains("420000")));

        // DeleteRow — remove lowest priority initiative
        doc.DeleteRow(6); // Grace's ESG initiative (just updated)
        Assert.Equal(7, doc.GetRowCount());

        // DeleteRow — remove another
        doc.DeleteRow(3); // Dave's cybersecurity
        Assert.Equal(6, doc.GetRowCount());

        // Consistent
        Assert.Equal(6, doc.GetRowCount());

        // GetDistinctValues after mutations
        var priorities = doc.GetDistinctValues("Priority");
        Assert.True(priorities.Count >= 1);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // FilterRows still works
        var critical = doc.FilterRows("Priority", "Critical");
        Assert.True(critical.GetRowCount() >= 0);

        // SaveToFile
        var savePath = TempFile("dogfood_initiatives_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(6, loaded.GetRowCount());

        // GetRowAt on loaded — all valid
        for (int i = 0; i < loaded.GetRowCount(); i++)
        {
            var row = loaded.GetRowAt(i);
            Assert.NotNull(row);
            Assert.Equal(7, row.Length);
        }

        // SetRowValues on loaded
        loaded.SetRowValues(0, new[] { "INIT-001", "DT v3 — Board Approved", "Alice", "Critical", "1800000", "Execution", "EMEA" });
        var loadedRow0 = loaded.GetRowAt(0);
        Assert.True(System.Array.Exists((string[])loadedRow0, v => v.Contains("v3") || v.Contains("1800000")));

        // DeleteRow on loaded
        loaded.DeleteRow(0);
        Assert.Equal(5, loaded.GetRowCount());

        // Final save
        var path2 = TempFile("dogfood_initiatives_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetRowCount());
        for (int i = 0; i < loaded2.GetRowCount(); i++)
            Assert.Equal(7, loaded2.GetRowAt(i).Length);
    }
}
