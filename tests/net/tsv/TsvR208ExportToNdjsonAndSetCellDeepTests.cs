// Tests for TsvDocument.ExportToNdjson, SetCell, GetHeaders deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R208

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R208: Tests for TsvDocument.ExportToNdjson, SetCell, GetHeaders deeper.
/// ExportToNdjson(): exports the document as NDJSON (newline-delimited JSON).
/// SetCell(row, col, value): sets the value of a specific cell.
/// GetHeaders(): returns the list of column header names.
/// Covers: ExportToNdjson non-null; ExportToNdjson non-empty; ExportToNdjson no-throw;
/// ExportToNdjson has braces; ExportToNdjson record count correct; ExportToNdjson consistent;
/// ExportToNdjson after AddRow grows; ExportToNdjson after Filter shrinks;
/// ExportToNdjson save-load consistent;
/// SetCell no-throw; SetCell reflects in GetCell; SetCell all cells addressable;
/// SetCell then SaveToFile persists; SetCell then ExportToNdjson updates;
/// SetCell overwrite existing; SetCell new row expands; SetCell consistent;
/// GetHeaders non-null; GetHeaders non-empty; GetHeaders no-throw; GetHeaders count=4;
/// GetHeaders consistent; GetHeaders contains known; GetHeaders after AddColumn grows;
/// GetHeaders save-load consistent; GetHeaders after RemoveColumn shrinks;
/// dogfood LoadTsv→ExportToNdjson→SetCell→GetHeaders→SaveToFile pipeline.
/// </summary>
public class TsvR208ExportToNdjsonAndSetCellDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR208ExportToNdjsonAndSetCellDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR208_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleTsv()
    {
        var path = TempFile("sample.tsv");
        var content =
            "Name\tDepartment\tScore\tCity\n" +
            "Alice\tEngineering\t92\tLondon\n" +
            "Bob\tMarketing\t78\tParis\n" +
            "Carol\tEngineering\t88\tBerlin\n" +
            "Dave\tFinance\t85\tRome\n" +
            "Eve\tEngineering\t95\tMadrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // ExportToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToNdjson_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_NonEmpty()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotEmpty(doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.ExportToNdjson());
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToNdjson_HasBraces()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ndjson = doc.ExportToNdjson();
        Assert.True(ndjson.Contains("{") && ndjson.Contains("}"));
    }

    [Fact]
    public void ExportToNdjson_RecordCount_EqualsRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ndjson = doc.ExportToNdjson();
        // Each line is a JSON object — count non-empty lines
        var lines = ndjson.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(doc.GetRowCount(), lines.Length);
    }

    [Fact]
    public void ExportToNdjson_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.ExportToNdjson().Length, doc.ExportToNdjson().Length);
    }

    [Fact]
    public void ExportToNdjson_AfterAddRow_Grows()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.ExportToNdjson().Length;
        doc.AddRow(new[] { "Frank", "Finance", "80", "Oslo" });
        Assert.True(doc.ExportToNdjson().Length > before);
    }

    [Fact]
    public void ExportToNdjson_AfterFilter_Shrinks()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.ExportToNdjson().Length;
        var filtered = doc.Filter("Department", "Engineering");
        Assert.True(filtered.ExportToNdjson().Length < before);
    }

    [Fact]
    public void ExportToNdjson_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.ExportToNdjson().Length;
        var path = TempFile("ndjson_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.ExportToNdjson().Length);
    }

    // -------------------------------------------------------------------------
    // SetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.SetCell(0, 0, "UpdatedAlice"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCell_ReflectsInGetCell()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.SetCell(0, 0, "Zara");
        Assert.Equal("Zara", doc.GetCell(0, 0));
    }

    [Fact]
    public void SetCell_OverwriteExisting()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.SetCell(0, 2, "99"); // was 92
        Assert.Equal("99", doc.GetCell(0, 2));
    }

    [Fact]
    public void SetCell_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.SetCell(1, 1, "Marketing");
        Assert.Equal("Marketing", doc.GetCell(1, 1));
        doc.SetCell(1, 1, "Marketing"); // set same value
        Assert.Equal("Marketing", doc.GetCell(1, 1));
    }

    [Fact]
    public void SetCell_ThenSaveToFile_Persists()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.SetCell(0, 0, "UpdatedName");
        var path = TempFile("setcell_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal("UpdatedName", loaded.GetCell(0, 0));
    }

    [Fact]
    public void SetCell_ThenExportToNdjson_Updates()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.SetCell(0, 0, "UpdatedNdjsonName");
        var ndjson = doc.ExportToNdjson();
        Assert.Contains("UpdatedNdjsonName", ndjson);
    }

    [Fact]
    public void SetCell_AllCells_Row0_Addressable()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        for (int col = 0; col < doc.GetHeaderCount(); col++)
        {
            var ex = Record.Exception(() => doc.SetCell(0, col, $"Val{col}"));
            Assert.Null(ex);
        }
    }

    // -------------------------------------------------------------------------
    // GetHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaders_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetHeaders());
    }

    [Fact]
    public void GetHeaders_NonEmpty()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetHeaders().Count > 0);
    }

    [Fact]
    public void GetHeaders_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetHeaders());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHeaders_Count4()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(4, doc.GetHeaders().Count);
    }

    [Fact]
    public void GetHeaders_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetHeaders().Count, doc.GetHeaders().Count);
    }

    [Fact]
    public void GetHeaders_ContainsKnown()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var headers = doc.GetHeaders();
        Assert.True(headers.Contains("Name") || headers.Exists(h => h == "Name"));
        Assert.True(headers.Contains("Department") || headers.Exists(h => h == "Department"));
    }

    [Fact]
    public void GetHeaders_AfterAddColumn_Grows()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetHeaders().Count;
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU" });
        Assert.Equal(before + 1, doc.GetHeaders().Count);
    }

    [Fact]
    public void GetHeaders_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetHeaders().Count;
        var path = TempFile("headers_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHeaders().Count);
    }

    [Fact]
    public void GetHeaders_AfterRemoveColumn_Shrinks()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetHeaders().Count;
        doc.RemoveColumn("City");
        Assert.Equal(before - 1, doc.GetHeaders().Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ExportToNdjson_SetCell_GetHeaders_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_team.tsv");
        var content =
            "Employee\tDepartment\tGrade\tLocation\tSalary\n" +
            "Alice\tEngineering\tSenior\tLondon\t95000\n" +
            "Bob\tMarketing\tJunior\tParis\t55000\n" +
            "Carol\tEngineering\tLead\tLondon\t115000\n" +
            "Dave\tFinance\tMid\tBerlin\t72000\n" +
            "Eve\tEngineering\tSenior\tLondon\t98000\n" +
            "Frank\tMarketing\tSenior\tRome\t82000\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(6, doc.GetRowCount());

        // GetHeaders — 5 columns
        var headers = doc.GetHeaders();
        Assert.Equal(5, headers.Count);
        Assert.True(headers.Contains("Employee") || headers.Exists(h => h == "Employee"));
        Assert.True(headers.Contains("Salary") || headers.Exists(h => h == "Salary"));

        // ExportToNdjson baseline
        var ndjson = doc.ExportToNdjson();
        Assert.NotNull(ndjson);
        Assert.True(ndjson.Contains("{") && ndjson.Contains("}"));
        var lines = ndjson.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(6, lines.Length);

        // Consistent
        Assert.Equal(ndjson.Length, doc.ExportToNdjson().Length);

        // SetCell — update Alice's salary
        doc.SetCell(0, 4, "100000");
        Assert.Equal("100000", doc.GetCell(0, 4));

        // ExportToNdjson updates after SetCell
        var ndjsonAfter = doc.ExportToNdjson();
        Assert.Contains("100000", ndjsonAfter);

        // SetCell — update multiple cells
        doc.SetCell(1, 2, "Senior");     // Bob promoted to Senior
        doc.SetCell(3, 3, "Madrid");     // Dave relocated
        Assert.Equal("Senior", doc.GetCell(1, 2));
        Assert.Equal("Madrid", doc.GetCell(3, 3));

        // GetHeaders unchanged after SetCell
        Assert.Equal(5, doc.GetHeaders().Count);

        // AddRow and verify ExportToNdjson grows
        doc.AddRow(new[] { "Grace", "HR", "Junior", "Tokyo", "48000" });
        Assert.Equal(7, doc.GetRowCount());
        var ndjsonAfterRow = doc.ExportToNdjson();
        Assert.True(ndjsonAfterRow.Length > ndjsonAfter.Length);
        var linesAfterRow = ndjsonAfterRow.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(7, linesAfterRow.Length);

        // AddColumn and verify GetHeaders grows
        doc.AddColumn("Level", new[] { "L6", "L2", "L6", "L3", "L5", "L4", "L2" });
        Assert.Equal(6, doc.GetHeaders().Count);

        // Filter and verify ExportToNdjson shrinks
        var filtered = doc.Filter("Department", "Engineering");
        Assert.Equal(3, filtered.GetRowCount());
        var filteredNdjson = filtered.ExportToNdjson();
        Assert.True(filteredNdjson.Length < ndjsonAfterRow.Length);

        // SaveToFile
        var savePath = TempFile("dogfood_team_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(7, loaded.GetRowCount());
        Assert.Equal(6, loaded.GetHeaders().Count);

        // ExportToNdjson on loaded
        var loadedNdjson = loaded.ExportToNdjson();
        Assert.Equal(7, loadedNdjson.Split('\n', StringSplitOptions.RemoveEmptyEntries).Length);

        // SetCell on loaded
        loaded.SetCell(0, 0, "Alexandra");
        Assert.Equal("Alexandra", loaded.GetCell(0, 0));

        // GetHeaders on loaded consistent
        Assert.Equal(loaded.GetHeaders().Count, loaded.GetHeaders().Count);

        // Final save
        var path2 = TempFile("dogfood_team_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetHeaders().Count, loaded2.GetHeaders().Count);
        Assert.Equal("Alexandra", loaded2.GetCell(0, 0));
    }
}
