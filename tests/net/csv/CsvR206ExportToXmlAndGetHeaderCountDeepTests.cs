// Tests for CsvDocument.ExportToXml, GetHeaderCount, Clone deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R206

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R206: Tests for CsvDocument.ExportToXml, GetHeaderCount, Clone deeper.
/// ExportToXml(): exports the document as an XML string.
/// GetHeaderCount(): returns the number of column headers in the document.
/// Clone(): returns an independent copy of the document.
/// Covers: ExportToXml non-null; ExportToXml non-empty; ExportToXml has root;
/// ExportToXml has header names; ExportToXml has data; ExportToXml after AddRow grows;
/// ExportToXml after Filter shrinks; ExportToXml consistent; ExportToXml save-load;
/// GetHeaderCount=4; GetHeaderCount consistent; GetHeaderCount no-throw;
/// GetHeaderCount after AddColumn increases; GetHeaderCount after RemoveColumn decreases;
/// GetHeaderCount after Filter unchanged; GetHeaderCount after SortRows unchanged;
/// Clone non-null; Clone same row count; Clone same headers; Clone independent;
/// Clone changes don't affect original; Clone persist; Clone then Filter;
/// Clone then SortRows; Clone then AddRow original unchanged; Clone then SetCell;
/// dogfood LoadFile→ExportToXml→GetHeaderCount→Clone→SaveToFile pipeline.
/// </summary>
public class CsvR206ExportToXmlAndGetHeaderCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR206ExportToXmlAndGetHeaderCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR206_" + Guid.NewGuid().ToString("N"));
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
    public void ExportToXml_HasRoot()
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
        doc.AddRow(new[] { "Frank", "Delta", "80", "Oslo" });
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

    [Fact]
    public void ExportToXml_SaveLoad()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var path = TempFile("xml_saveload.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var xml = loaded.ExportToXml();
        Assert.NotNull(xml);
        Assert.NotEmpty(xml);
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
    public void GetHeaderCount_AfterSortRows_Unchanged()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetHeaderCount();
        doc.SortRows("Name", ascending: true);
        Assert.Equal(before, doc.GetHeaderCount());
    }

    // -------------------------------------------------------------------------
    // Clone
    // -------------------------------------------------------------------------

    [Fact]
    public void Clone_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.Clone());
    }

    [Fact]
    public void Clone_SameRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetRowCount(), doc.Clone().GetRowCount());
    }

    [Fact]
    public void Clone_SameHeaders()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetHeaderCount(), doc.Clone().GetHeaderCount());
    }

    [Fact]
    public void Clone_Independent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var clone = doc.Clone();
        clone.SetCell(0, 0, "CLONE_MODIFIED");
        Assert.NotEqual("CLONE_MODIFIED", doc.GetCell(0, 0));
    }

    [Fact]
    public void Clone_ChangesDontAffectOriginal()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var origRow0 = doc.GetCell(0, 0);
        var clone = doc.Clone();
        clone.AddRow(new[] { "Extra", "Beta", "99", "Oslo" });
        Assert.Equal(5, doc.GetRowCount());
        Assert.Equal(origRow0, doc.GetCell(0, 0));
    }

    [Fact]
    public void Clone_Persist()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var clone = doc.Clone();
        var path = TempFile("clone_persist.csv");
        clone.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetRowCount());
    }

    [Fact]
    public void Clone_ThenFilter()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var clone = doc.Clone();
        var filtered = clone.Filter("Team", "Alpha");
        Assert.Equal(3, filtered.GetRowCount());
    }

    [Fact]
    public void Clone_ThenSortRows()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var clone = doc.Clone();
        clone.SortRows("Name", ascending: true);
        Assert.Equal("Alice", clone.GetCell(0, 0));
        Assert.Equal(5, doc.GetRowCount()); // original unchanged
    }

    [Fact]
    public void Clone_ThenAddRow_OriginalUnchanged()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var clone = doc.Clone();
        clone.AddRow(new[] { "Zara", "Delta", "77", "Vienna" });
        Assert.Equal(5, doc.GetRowCount());
        Assert.Equal(6, clone.GetRowCount());
    }

    [Fact]
    public void Clone_ThenSetCell_OriginalUnchanged()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var origVal = doc.GetCell(2, 1);
        var clone = doc.Clone();
        clone.SetCell(2, 1, "MODIFIED_TEAM");
        Assert.Equal(origVal, doc.GetCell(2, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ExportToXml_GetHeaderCount_Clone_SaveToFile_Pipeline()
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

        // Clone
        var clone = doc.Clone();
        Assert.Equal(6, clone.GetRowCount());
        Assert.Equal(hc, clone.GetHeaderCount());

        // Clone is independent
        clone.SetCell(0, 0, "ALICE_CLONE");
        Assert.Equal("Alice", doc.GetCell(0, 0));
        Assert.Equal("ALICE_CLONE", clone.GetCell(0, 0));

        // GetHeaderCount unchanged after clone modification
        Assert.Equal(hc, clone.GetHeaderCount());

        // ExportToXml on clone = same length (same data minus one char)
        var xmlClone = clone.ExportToXml();
        Assert.NotNull(xmlClone);
        Assert.NotEmpty(xmlClone);

        // AddRow to clone only
        clone.AddRow(new[] { "Grace", "HR", "Junior", "Madrid", "48000" });
        Assert.Equal(7, clone.GetRowCount());
        Assert.Equal(6, doc.GetRowCount());

        // ExportToXml grows on clone
        var xmlCloneGrown = clone.ExportToXml();
        Assert.True(xmlCloneGrown.Length > xml.Length);

        // GetHeaderCount on clone after AddRow
        Assert.Equal(hc, clone.GetHeaderCount());

        // Filter original
        var eng = doc.Filter("Department", "Engineering");
        Assert.Equal(3, eng.GetRowCount());
        Assert.Equal(hc, eng.GetHeaderCount());

        // ExportToXml on filtered shrinks
        var xmlEng = eng.ExportToXml();
        Assert.True(xmlEng.Length < xml.Length);

        // Clone of filtered
        var engClone = eng.Clone();
        Assert.Equal(eng.GetRowCount(), engClone.GetRowCount());
        Assert.Equal(hc, engClone.GetHeaderCount());

        // SortRows on clone
        clone.SortRows("Salary", ascending: false);
        Assert.Equal(7, clone.GetRowCount());

        // AddColumn to clone
        clone.AddColumn("Active", new[] { "Yes", "Yes", "Yes", "Yes", "Yes", "No", "Yes" });
        Assert.Equal(hc + 1, clone.GetHeaderCount());

        // ExportToXml after AddColumn grows
        var xmlCloneFull = clone.ExportToXml();
        Assert.True(xmlCloneFull.Length > xmlCloneGrown.Length);

        // GetHeaderCount original unchanged
        Assert.Equal(hc, doc.GetHeaderCount());

        // ExportToXml consistent
        var x1 = doc.ExportToXml();
        var x2 = doc.ExportToXml();
        Assert.Equal(x1.Length, x2.Length);

        // SaveToFile original
        var saveOrig = TempFile("dogfood_orig.csv");
        doc.SaveToFile(saveOrig);
        Assert.True(File.Exists(saveOrig));

        // SaveToFile clone
        var saveClone = TempFile("dogfood_clone.csv");
        clone.SaveToFile(saveClone);
        Assert.True(File.Exists(saveClone));

        // LoadFile verify original
        var loadedOrig = CsvDocument.LoadFile(saveOrig);
        Assert.Equal(6, loadedOrig.GetRowCount());
        Assert.Equal(hc, loadedOrig.GetHeaderCount());

        // ExportToXml on loaded
        var loadedXml = loadedOrig.ExportToXml();
        Assert.NotNull(loadedXml);
        Assert.NotEmpty(loadedXml);

        // LoadFile verify clone
        var loadedClone = CsvDocument.LoadFile(saveClone);
        Assert.Equal(7, loadedClone.GetRowCount());
        Assert.Equal(hc + 1, loadedClone.GetHeaderCount());

        // Clone of loaded
        var cloneOfLoaded = loadedOrig.Clone();
        Assert.Equal(loadedOrig.GetRowCount(), cloneOfLoaded.GetRowCount());
        Assert.Equal(hc, cloneOfLoaded.GetHeaderCount());
    }
}
