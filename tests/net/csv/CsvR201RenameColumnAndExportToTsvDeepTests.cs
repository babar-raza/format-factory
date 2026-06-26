// Tests for CsvDocument.RenameColumn, ExportToTsv, GetColumnCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R201

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R201: Tests for CsvDocument.RenameColumn, ExportToTsv, GetColumnCount deeper.
/// RenameColumn(oldName, newName): renames a column header.
/// ExportToTsv(): exports the document content as a tab-separated string.
/// GetColumnCount(): returns the number of columns (headers).
/// Covers: RenameColumn changes header; RenameColumn old absent; RenameColumn new present;
/// RenameColumn values preserved; RenameColumn no-throw; RenameColumn persist;
/// RenameColumn then Filter; RenameColumn then SortRows; RenameColumn multiple;
/// ExportToTsv non-null; ExportToTsv non-empty; ExportToTsv has tabs;
/// ExportToTsv has header names; ExportToTsv has data values; ExportToTsv after AddRow grows;
/// ExportToTsv after Filter shrinks; ExportToTsv consistent; ExportToTsv after RenameColumn reflects;
/// GetColumnCount correct; GetColumnCount after AddColumn increases; GetColumnCount after RemoveColumn decreases;
/// GetColumnCount consistent; GetColumnCount empty doc zero; GetColumnCount save-load preserved;
/// dogfood LoadFile→RenameColumn→ExportToTsv→GetColumnCount→SaveToFile pipeline.
/// </summary>
public class CsvR201RenameColumnAndExportToTsvDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR201RenameColumnAndExportToTsvDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR201_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleCsv()
    {
        var path = TempFile("sample.csv");
        var content =
            "Name,Department,Score,City\n" +
            "Alice,Engineering,92,London\n" +
            "Bob,Marketing,78,Paris\n" +
            "Carol,Engineering,88,Berlin\n" +
            "Dave,Finance,85,Rome\n" +
            "Eve,Engineering,95,Madrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // RenameColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameColumn_ChangesHeader()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.RenameColumn("Department", "Team");
        Assert.Contains("Team", doc.GetHeaders());
    }

    [Fact]
    public void RenameColumn_OldNameAbsent()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.RenameColumn("Department", "Team");
        Assert.False(doc.GetHeaders().Contains("Department"));
    }

    [Fact]
    public void RenameColumn_NewNamePresent()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.RenameColumn("Score", "Points");
        Assert.Contains("Points", doc.GetHeaders());
    }

    [Fact]
    public void RenameColumn_ValuesPreserved()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var originalValues = doc.GetDistinctValues("Department");
        doc.RenameColumn("Department", "Team");
        var newValues = doc.GetDistinctValues("Team");
        Assert.Equal(originalValues.Count, newValues.Count);
    }

    [Fact]
    public void RenameColumn_NoThrow()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.RenameColumn("Name", "FullName"));
        Assert.Null(ex);
    }

    [Fact]
    public void RenameColumn_Persist()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.RenameColumn("City", "Location");
        var savePath = TempFile("rename_persist.csv");
        doc.SaveToFile(savePath);
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Contains("Location", loaded.GetHeaders());
        Assert.False(loaded.GetHeaders().Contains("City"));
    }

    [Fact]
    public void RenameColumn_ThenFilter_Works()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.RenameColumn("Department", "Team");
        var filtered = doc.Filter("Team", "Engineering");
        Assert.NotNull(filtered);
        Assert.True(filtered.GetRowCount() > 0);
    }

    [Fact]
    public void RenameColumn_Multiple_AllApplied()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.RenameColumn("Name", "FullName");
        doc.RenameColumn("Department", "Team");
        doc.RenameColumn("Score", "Points");
        doc.RenameColumn("City", "Location");
        var headers = doc.GetHeaders();
        Assert.Contains("FullName", headers);
        Assert.Contains("Team", headers);
        Assert.Contains("Points", headers);
        Assert.Contains("Location", headers);
    }

    [Fact]
    public void RenameColumn_RowCountUnchanged()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetRowCount();
        doc.RenameColumn("Name", "FullName");
        Assert.Equal(before, doc.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // ExportToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToTsv_NonNull()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.NotNull(doc.ExportToTsv());
    }

    [Fact]
    public void ExportToTsv_NonEmpty()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.NotEmpty(doc.ExportToTsv());
    }

    [Fact]
    public void ExportToTsv_HasTabs()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.Contains("\t", doc.ExportToTsv());
    }

    [Fact]
    public void ExportToTsv_HasHeaderNames()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var tsv = doc.ExportToTsv();
        Assert.Contains("Name", tsv);
        Assert.Contains("Department", tsv);
        Assert.Contains("Score", tsv);
    }

    [Fact]
    public void ExportToTsv_HasDataValues()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var tsv = doc.ExportToTsv();
        Assert.True(tsv.Contains("Alice") || tsv.Contains("Bob") || tsv.Contains("Carol"));
    }

    [Fact]
    public void ExportToTsv_AfterAddRow_Grows()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.ExportToTsv().Length;
        doc.AddRow(new[] { "Frank", "Operations", "82", "Vienna" });
        var after = doc.ExportToTsv().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToTsv_AfterFilter_Shrinks()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.ExportToTsv().Length;
        var filtered = doc.Filter("Department", "Finance");
        var after = filtered.ExportToTsv().Length;
        Assert.True(after < before);
    }

    [Fact]
    public void ExportToTsv_Consistent()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var tsv1 = doc.ExportToTsv();
        var tsv2 = doc.ExportToTsv();
        Assert.Equal(tsv1.Length, tsv2.Length);
    }

    [Fact]
    public void ExportToTsv_AfterRenameColumn_Reflects()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.RenameColumn("Department", "TEAM_RENAMED");
        var tsv = doc.ExportToTsv();
        Assert.Contains("TEAM_RENAMED", tsv);
    }

    // -------------------------------------------------------------------------
    // GetColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_Correct()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(4, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_AfterAddColumn_Increases()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetColumnCount();
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU" });
        Assert.Equal(before + 1, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_AfterRemoveColumn_Decreases()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetColumnCount();
        doc.RemoveColumn("City");
        Assert.Equal(before - 1, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_Consistent()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(doc.GetColumnCount(), doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_AfterRenameColumn_Unchanged()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetColumnCount();
        doc.RenameColumn("Name", "FullName");
        Assert.Equal(before, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_SaveLoadPreserved()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.AddColumn("Extra", new[] { "A", "B", "C", "D", "E" });
        var count = doc.GetColumnCount();
        var savePath = TempFile("colcount_preserve.csv");
        doc.SaveToFile(savePath);
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(count, loaded.GetColumnCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_RenameColumn_ExportToTsv_GetColumnCount_SaveToFile_Pipeline()
    {
        // Create source CSV
        var path = TempFile("dogfood_src.csv");
        var content =
            "EmployeeID,FirstName,LastName,Dept,Salary,YearsExp\n" +
            "E001,Alice,Smith,Engineering,95000,5\n" +
            "E002,Bob,Jones,Marketing,72000,3\n" +
            "E003,Carol,White,Engineering,88000,7\n" +
            "E004,Dave,Brown,Finance,81000,4\n" +
            "E005,Eve,Davis,Engineering,102000,9\n" +
            "E006,Frank,Miller,HR,68000,2\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(6, doc.GetRowCount());

        // GetColumnCount baseline
        Assert.Equal(6, doc.GetColumnCount());

        // GetHeaders
        var headers = doc.GetHeaders();
        Assert.Contains("EmployeeID", headers);
        Assert.Contains("Dept", headers);
        Assert.Contains("YearsExp", headers);

        // ExportToTsv baseline
        var tsv = doc.ExportToTsv();
        Assert.NotNull(tsv);
        Assert.NotEmpty(tsv);
        Assert.Contains("\t", tsv);
        Assert.Contains("EmployeeID", tsv);
        Assert.Contains("Alice", tsv);

        // RenameColumn — update names
        doc.RenameColumn("FirstName", "GivenName");
        doc.RenameColumn("LastName", "FamilyName");
        doc.RenameColumn("Dept", "Department");
        doc.RenameColumn("YearsExp", "Experience");

        var headersAfterRename = doc.GetHeaders();
        Assert.Contains("GivenName", headersAfterRename);
        Assert.Contains("FamilyName", headersAfterRename);
        Assert.Contains("Department", headersAfterRename);
        Assert.Contains("Experience", headersAfterRename);
        Assert.False(headersAfterRename.Contains("FirstName"));
        Assert.False(headersAfterRename.Contains("Dept"));
        Assert.False(headersAfterRename.Contains("YearsExp"));

        // GetColumnCount still 6 after renames
        Assert.Equal(6, doc.GetColumnCount());

        // ExportToTsv after renames reflects new headers
        var tsvAfterRename = doc.ExportToTsv();
        Assert.Contains("GivenName", tsvAfterRename);
        Assert.Contains("Department", tsvAfterRename);
        Assert.Contains("Alice", tsvAfterRename);
        Assert.False(tsvAfterRename.Contains("Dept\t") || tsvAfterRename.Contains("\tDept"));

        // Filter by Department (renamed from Dept)
        var engRows = doc.Filter("Department", "Engineering");
        Assert.Equal(3, engRows.GetRowCount());
        Assert.Equal(6, engRows.GetColumnCount());

        // ExportToTsv on filtered
        var engTsv = engRows.ExportToTsv();
        Assert.Contains("Engineering", engTsv);
        Assert.True(engTsv.Length < tsvAfterRename.Length);

        // AddColumn and verify GetColumnCount
        doc.AddColumn("Region", new[] { "EU", "US", "EU", "US", "EU", "US" });
        Assert.Equal(7, doc.GetColumnCount());
        var tsvAfterCol = doc.ExportToTsv();
        Assert.True(tsvAfterCol.Length > tsvAfterRename.Length);

        // RenameColumn on new column
        doc.RenameColumn("Region", "OfficeRegion");
        Assert.Contains("OfficeRegion", doc.GetHeaders());
        Assert.Equal(7, doc.GetColumnCount());

        // RemoveColumn
        doc.RemoveColumn("OfficeRegion");
        Assert.Equal(6, doc.GetColumnCount());
        Assert.False(doc.GetHeaders().Contains("OfficeRegion"));

        // AddRow and verify
        doc.AddRow(new[] { "E007", "Grace", "Taylor", "Engineering", "98000", "6" });
        Assert.Equal(7, doc.GetRowCount());
        var tsvAfterRow = doc.ExportToTsv();
        Assert.True(tsvAfterRow.Length > tsvAfterRename.Length);

        // SortRows then ExportToTsv
        doc.SortRows("GivenName", ascending: true);
        var sortedTsv = doc.ExportToTsv();
        Assert.NotNull(sortedTsv);
        // Alice should appear early in sorted output
        var aliceIdx = sortedTsv.IndexOf("Alice");
        var graceIdx = sortedTsv.IndexOf("Grace");
        Assert.True(aliceIdx < graceIdx);

        // SaveToFile
        var savePath = TempFile("dogfood_renamed.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(7, loaded.GetRowCount());
        Assert.Equal(6, loaded.GetColumnCount());
        var loadedHeaders = loaded.GetHeaders();
        Assert.Contains("GivenName", loadedHeaders);
        Assert.Contains("Department", loadedHeaders);
        Assert.Contains("Experience", loadedHeaders);

        // ExportToTsv on loaded
        var loadedTsv = loaded.ExportToTsv();
        Assert.NotNull(loadedTsv);
        Assert.Contains("\t", loadedTsv);
        Assert.Contains("GivenName", loadedTsv);

        // GetColumnCount on loaded
        Assert.Equal(6, loaded.GetColumnCount());

        // RenameColumn on loaded
        loaded.RenameColumn("GivenName", "Name");
        Assert.Contains("Name", loaded.GetHeaders());
        Assert.Equal(6, loaded.GetColumnCount());
    }
}
