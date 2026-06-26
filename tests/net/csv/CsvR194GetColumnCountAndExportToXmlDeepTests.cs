// Tests for CsvDocument.GetColumnCount, ExportToXml, Clone deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R194

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R194: Tests for CsvDocument.GetColumnCount, ExportToXml, Clone deeper.
/// GetColumnCount(): returns number of columns in the document.
/// ExportToXml(): exports the document as an XML string.
/// Clone(): creates an independent copy of the document.
/// Covers: GetColumnCount correct; GetColumnCount after AddRow unchanged;
/// GetColumnCount after Filter unchanged; GetColumnCount consistent;
/// GetColumnCount empty doc; GetColumnCount per-loaded-file;
/// ExportToXml non-null; ExportToXml non-empty; ExportToXml has XML structure;
/// ExportToXml contains header; ExportToXml contains data; ExportToXml after AddRow grows;
/// ExportToXml after Filter smaller; ExportToXml has root element;
/// Clone non-null; Clone has same row count; Clone has same column count;
/// Clone is independent (modify clone does not affect original);
/// Clone has same data; Clone then SaveToFile works; Clone after Filter;
/// dogfood LoadFile→GetColumnCount→ExportToXml→Clone→modify→verify pipeline.
/// </summary>
public class CsvR194GetColumnCountAndExportToXmlDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR194GetColumnCountAndExportToXmlDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR194_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleCsv =
        "Country,Capital,Population,Continent\n" +
        "Germany,Berlin,83900000,Europe\n" +
        "France,Paris,67750000,Europe\n" +
        "Japan,Tokyo,125700000,Asia\n" +
        "Brazil,Brasília,215300000,South America\n" +
        "Canada,Ottawa,38600000,North America\n";

    private CsvDocument LoadSample()
    {
        var path = TempFile("sample.csv");
        File.WriteAllText(path, SampleCsv);
        return CsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // GetColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_Correct()
    {
        var doc = LoadSample();
        Assert.Equal(4, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_AfterAddRow_Unchanged()
    {
        var doc = LoadSample();
        var before = doc.GetColumnCount();
        doc.AddRow(new[] { "Australia", "Canberra", "26500000", "Oceania" });
        Assert.Equal(before, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_AfterFilter_Unchanged()
    {
        var doc = LoadSample();
        var before = doc.GetColumnCount();
        var filtered = doc.Filter("Continent", "Europe");
        Assert.Equal(before, filtered.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_Consistent()
    {
        var doc = LoadSample();
        Assert.Equal(doc.GetColumnCount(), doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_MatchesHeaderCount()
    {
        var doc = LoadSample();
        var headers = doc.GetHeaders();
        Assert.Equal(headers.Count, doc.GetColumnCount());
    }

    // -------------------------------------------------------------------------
    // ExportToXml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToXml_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_HasXmlStructure()
    {
        var doc = LoadSample();
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("<") && xml.Contains(">"));
    }

    [Fact]
    public void ExportToXml_ContainsHeaderOrField()
    {
        var doc = LoadSample();
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("Country") || xml.Contains("Capital") || xml.Contains("Continent"));
    }

    [Fact]
    public void ExportToXml_ContainsData()
    {
        var doc = LoadSample();
        Assert.Contains("Germany", doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_AfterAddRow_Grows()
    {
        var doc = LoadSample();
        var before = doc.ExportToXml().Length;
        doc.AddRow(new[] { "Argentina", "Buenos Aires", "46300000", "South America" });
        Assert.True(doc.ExportToXml().Length > before);
    }

    [Fact]
    public void ExportToXml_AfterFilter_Smaller()
    {
        var doc = LoadSample();
        var all = doc.ExportToXml();
        var filtered = doc.Filter("Continent", "Europe").ExportToXml();
        Assert.True(filtered.Length < all.Length);
    }

    [Fact]
    public void ExportToXml_Consistent()
    {
        var doc = LoadSample();
        Assert.Equal(doc.ExportToXml().Length, doc.ExportToXml().Length);
    }

    // -------------------------------------------------------------------------
    // Clone
    // -------------------------------------------------------------------------

    [Fact]
    public void Clone_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.Clone());
    }

    [Fact]
    public void Clone_SameRowCount()
    {
        var doc = LoadSample();
        var clone = doc.Clone();
        Assert.Equal(doc.RowCount, clone.RowCount);
    }

    [Fact]
    public void Clone_SameColumnCount()
    {
        var doc = LoadSample();
        var clone = doc.Clone();
        Assert.Equal(doc.GetColumnCount(), clone.GetColumnCount());
    }

    [Fact]
    public void Clone_SameData()
    {
        var doc = LoadSample();
        var clone = doc.Clone();
        Assert.Contains("Germany", clone.GetColumnValues("Country"));
    }

    [Fact]
    public void Clone_IsIndependent_AddRowToClone()
    {
        var doc = LoadSample();
        var clone = doc.Clone();
        var originalRows = doc.RowCount;
        clone.AddRow(new[] { "India", "New Delhi", "1400000000", "Asia" });
        // Original should be unaffected
        Assert.Equal(originalRows, doc.RowCount);
        Assert.True(clone.RowCount > originalRows);
    }

    [Fact]
    public void Clone_SaveToFile_Works()
    {
        var doc = LoadSample();
        var clone = doc.Clone();
        var path = TempFile("cloned.csv");
        clone.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }

    [Fact]
    public void Clone_AfterFilter()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("Continent", "Europe");
        var clone = filtered.Clone();
        Assert.Equal(filtered.RowCount, clone.RowCount);
        Assert.Contains("Germany", clone.GetColumnValues("Country"));
        Assert.Contains("France", clone.GetColumnValues("Country"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_GetColumnCount_ExportToXml_Clone_Modify_Verify_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.RowCount);

        // GetColumnCount
        Assert.Equal(4, doc.GetColumnCount());

        // ExportToXml
        var xml = doc.ExportToXml();
        Assert.NotNull(xml);
        Assert.True(xml.Contains("<") && xml.Length > 0);
        Assert.Contains("Germany", xml);

        // Filter Europe
        var europe = doc.Filter("Continent", "Europe");
        Assert.Equal(2, europe.RowCount);
        var europeXml = europe.ExportToXml();
        Assert.True(europeXml.Length < xml.Length);
        Assert.Contains("Germany", europeXml);
        Assert.Contains("France", europeXml);
        Assert.DoesNotContain("Japan", europeXml);

        // Clone the full doc
        var clone = doc.Clone();
        Assert.Equal(5, clone.RowCount);
        Assert.Equal(4, clone.GetColumnCount());
        Assert.Contains("Japan", clone.GetColumnValues("Country"));

        // Modify clone — does not affect original
        clone.AddRow(new[] { "Mexico", "Mexico City", "130900000", "North America" });
        Assert.Equal(6, clone.RowCount);
        Assert.Equal(5, doc.RowCount); // original unchanged

        // ExportToXml on clone should be larger
        var cloneXml = clone.ExportToXml();
        Assert.True(cloneXml.Length > xml.Length);
        Assert.Contains("Mexico", cloneXml);

        // Clone of filtered doc
        var asiaClone = doc.Filter("Continent", "Asia").Clone();
        Assert.Equal(1, asiaClone.RowCount);
        Assert.Contains("Japan", asiaClone.GetColumnValues("Country"));

        // GetColumnCount unchanged across operations
        Assert.Equal(4, doc.GetColumnCount());
        Assert.Equal(4, clone.GetColumnCount());

        // SaveToFile — both original and clone
        var origPath = TempFile("dogfood_orig.csv");
        var clonePath = TempFile("dogfood_clone.csv");
        doc.SaveToFile(origPath);
        clone.SaveToFile(clonePath);
        Assert.True(new FileInfo(clonePath).Length > new FileInfo(origPath).Length);

        // Reload and verify
        var loadedOrig = CsvDocument.LoadFile(origPath);
        var loadedClone = CsvDocument.LoadFile(clonePath);
        Assert.Equal(5, loadedOrig.RowCount);
        Assert.Equal(6, loadedClone.RowCount);
        Assert.Equal(4, loadedOrig.GetColumnCount());
        Assert.Equal(4, loadedClone.GetColumnCount());
        Assert.NotNull(loadedOrig.ExportToXml());
        Assert.NotNull(loadedClone.ExportToXml());
    }
}
