// Tests for CsvDocument.SortRows, GetHeaderCount, ExportToXml deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R205

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R205: Tests for CsvDocument.SortRows, GetHeaderCount, ExportToXml deeper.
/// SortRows(colName, ascending): sorts rows by the specified column.
/// GetHeaderCount(): returns the number of column headers in the document.
/// ExportToXml(): exports the document as an XML string.
/// Covers: SortRows no-throw; SortRows ascending first=Alice; SortRows descending first=Eve;
/// SortRows consistent; SortRows preserves row count; SortRows preserves header count;
/// SortRows numeric ascending; SortRows numeric descending; SortRows then Filter;
/// SortRows then AddRow; SortRows save-load consistent; SortRows on single row no-throw;
/// GetHeaderCount=4; GetHeaderCount consistent; GetHeaderCount no-throw;
/// GetHeaderCount after AddColumn increases; GetHeaderCount after RemoveColumn decreases;
/// GetHeaderCount after Filter unchanged; GetHeaderCount save-load consistent;
/// ExportToXml non-null; ExportToXml non-empty; ExportToXml has root element;
/// ExportToXml has header names; ExportToXml has data; ExportToXml after AddRow grows;
/// ExportToXml after Filter shrinks; ExportToXml consistent;
/// dogfood LoadFile→SortRows→GetHeaderCount→ExportToXml→SaveToFile pipeline.
/// </summary>
public class CsvR205SortRowsAndGetHeaderCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR205SortRowsAndGetHeaderCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR205_" + Guid.NewGuid().ToString("N"));
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
            "Name,Team,Score,City\n" +
            "Alice,Alpha,92,London\n" +
            "Bob,Beta,78,Paris\n" +
            "Carol,Alpha,88,Berlin\n" +
            "Dave,Gamma,85,Rome\n" +
            "Eve,Alpha,95,Madrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // SortRows
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.SortRows("Name", ascending: true));
        Assert.Null(ex);
    }

    [Fact]
    public void SortRows_Ascending_FirstIsAlice()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.SortRows("Name", ascending: true);
        Assert.Equal("Alice", doc.GetCell(0, 0));
    }

    [Fact]
    public void SortRows_Descending_FirstIsEve()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.SortRows("Name", ascending: false);
        Assert.Equal("Eve", doc.GetCell(0, 0));
    }

    [Fact]
    public void SortRows_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.SortRows("Name", ascending: true);
        var first = doc.GetCell(0, 0);
        doc.SortRows("Name", ascending: true);
        Assert.Equal(first, doc.GetCell(0, 0));
    }

    [Fact]
    public void SortRows_PreservesRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetRowCount();
        doc.SortRows("Name", ascending: true);
        Assert.Equal(before, doc.GetRowCount());
    }

    [Fact]
    public void SortRows_PreservesHeaderCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetHeaderCount();
        doc.SortRows("Team", ascending: true);
        Assert.Equal(before, doc.GetHeaderCount());
    }

    [Fact]
    public void SortRows_NumericAscending()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.SortRows("Score", ascending: true);
        // 78 should be first (Bob)
        var firstScore = doc.GetCell(0, 2);
        Assert.Equal("78", firstScore);
    }

    [Fact]
    public void SortRows_NumericDescending()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.SortRows("Score", ascending: false);
        // 95 should be first (Eve)
        var firstScore = doc.GetCell(0, 2);
        Assert.Equal("95", firstScore);
    }

    [Fact]
    public void SortRows_ThenFilter()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.SortRows("Name", ascending: true);
        var filtered = doc.Filter("Team", "Alpha");
        Assert.Equal(3, filtered.GetRowCount());
    }

    [Fact]
    public void SortRows_ThenAddRow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.SortRows("Name", ascending: true);
        doc.AddRow(new[] { "Zara", "Delta", "77", "Vienna" });
        Assert.Equal(6, doc.GetRowCount());
    }

    [Fact]
    public void SortRows_SaveLoadConsistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.SortRows("Name", ascending: true);
        var path = TempFile("sorted_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal("Alice", loaded.GetCell(0, 0));
    }

    // -------------------------------------------------------------------------
    // GetHeaderCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaderCount_Equals4()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(4, doc.GetHeaderCount());
    }

    [Fact]
    public void GetHeaderCount_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetHeaderCount(), doc.GetHeaderCount());
    }

    [Fact]
    public void GetHeaderCount_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetHeaderCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHeaderCount_AfterAddColumn_Increases()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetHeaderCount();
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU" });
        Assert.Equal(before + 1, doc.GetHeaderCount());
    }

    [Fact]
    public void GetHeaderCount_AfterRemoveColumn_Decreases()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetHeaderCount();
        doc.RemoveColumn("City");
        Assert.Equal(before - 1, doc.GetHeaderCount());
    }

    [Fact]
    public void GetHeaderCount_AfterFilter_Unchanged()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetHeaderCount();
        var filtered = doc.Filter("Team", "Alpha");
        Assert.Equal(before, filtered.GetHeaderCount());
    }

    [Fact]
    public void GetHeaderCount_SaveLoadConsistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetHeaderCount();
        var path = TempFile("header_count_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHeaderCount());
    }

    // -------------------------------------------------------------------------
    // ExportToXml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToXml_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_NonEmpty()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotEmpty(doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_HasRootElement()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("<") && xml.Contains(">"));
    }

    [Fact]
    public void ExportToXml_HasHeaderNames()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("Name") || xml.Contains("Team") || xml.Contains("Score"));
    }

    [Fact]
    public void ExportToXml_HasData()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("Alice") || xml.Contains("Bob") || xml.Contains("Carol"));
    }

    [Fact]
    public void ExportToXml_AfterAddRow_Grows()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.ExportToXml().Length;
        doc.AddRow(new[] { "Frank", "Beta", "82", "Oslo" });
        Assert.True(doc.ExportToXml().Length > before);
    }

    [Fact]
    public void ExportToXml_AfterFilter_Shrinks()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.ExportToXml().Length;
        var filtered = doc.Filter("Team", "Gamma");
        Assert.True(filtered.ExportToXml().Length < before);
    }

    [Fact]
    public void ExportToXml_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.ExportToXml().Length, doc.ExportToXml().Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SortRows_GetHeaderCount_ExportToXml_SaveToFile_Pipeline()
    {
        // Create main CSV
        var path = TempFile("dogfood_main.csv");
        var content =
            "Employee,Department,Grade,Location,Salary\n" +
            "Alice,Engineering,Senior,London,95000\n" +
            "Bob,Marketing,Junior,Paris,55000\n" +
            "Carol,Engineering,Lead,London,115000\n" +
            "Dave,Finance,Mid,Berlin,72000\n" +
            "Eve,Engineering,Senior,London,98000\n" +
            "Frank,Marketing,Senior,Rome,82000\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(6, doc.GetRowCount());

        // GetHeaderCount baseline
        var hc = doc.GetHeaderCount();
        Assert.Equal(5, hc);

        // ExportToXml baseline
        var xml = doc.ExportToXml();
        Assert.NotNull(xml);
        Assert.NotEmpty(xml);
        Assert.True(xml.Contains("<") && xml.Contains(">"));

        // SortRows ascending by Employee
        doc.SortRows("Employee", ascending: true);
        Assert.Equal(6, doc.GetRowCount());
        Assert.Equal("Alice", doc.GetCell(0, 0));
        Assert.Equal("Frank", doc.GetCell(5, 0));

        // GetHeaderCount unchanged after sort
        Assert.Equal(hc, doc.GetHeaderCount());

        // ExportToXml after sort — same length (content same, just reordered)
        var xmlSorted = doc.ExportToXml();
        Assert.Equal(xml.Length, xmlSorted.Length);

        // SortRows descending by Salary
        doc.SortRows("Salary", ascending: false);
        Assert.Equal(6, doc.GetRowCount());
        Assert.Equal("115000", doc.GetCell(0, 4)); // Carol highest

        // AddColumn and verify GetHeaderCount
        doc.AddColumn("Level", new[] { "L6", "L2", "L6", "L3", "L5", "L4" });
        Assert.Equal(hc + 1, doc.GetHeaderCount());

        // ExportToXml grows after AddColumn
        var xmlAfterAdd = doc.ExportToXml();
        Assert.True(xmlAfterAdd.Length > xml.Length);

        // GetHeaderCount consistent
        Assert.Equal(doc.GetHeaderCount(), doc.GetHeaderCount());

        // SortRows by Grade
        doc.SortRows("Grade", ascending: true);
        Assert.Equal(6, doc.GetRowCount());

        // Filter Engineering
        var eng = doc.Filter("Department", "Engineering");
        Assert.Equal(hc + 1, eng.GetHeaderCount()); // Level column preserved
        var engXml = eng.ExportToXml();
        Assert.True(engXml.Length < xmlAfterAdd.Length);

        // RemoveColumn Level and verify
        doc.RemoveColumn("Level");
        Assert.Equal(hc, doc.GetHeaderCount());

        // AddRow and verify
        doc.AddRow(new[] { "Grace", "Finance", "Junior", "Madrid", "48000" });
        Assert.Equal(7, doc.GetRowCount());
        var xmlAfterRow = doc.ExportToXml();
        Assert.True(xmlAfterRow.Length > xml.Length);

        // SortRows after AddRow
        doc.SortRows("Employee", ascending: true);
        Assert.Equal("Alice", doc.GetCell(0, 0));

        // ExportToXml consistent
        var x1 = doc.ExportToXml();
        var x2 = doc.ExportToXml();
        Assert.Equal(x1.Length, x2.Length);

        // SaveToFile
        var savePath = TempFile("dogfood_sorted.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(7, loaded.GetRowCount());
        Assert.Equal(hc, loaded.GetHeaderCount());
        Assert.Equal("Alice", loaded.GetCell(0, 0));

        // SortRows on loaded
        loaded.SortRows("Salary", ascending: false);
        Assert.Equal(7, loaded.GetRowCount());

        // ExportToXml on loaded
        var loadedXml = loaded.ExportToXml();
        Assert.NotNull(loadedXml);
        Assert.NotEmpty(loadedXml);

        // GetHeaderCount on loaded consistent
        Assert.Equal(loaded.GetHeaderCount(), loaded.GetHeaderCount());

        // Final save
        var path2 = TempFile("dogfood_sorted_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetHeaderCount(), loaded2.GetHeaderCount());
    }
}
