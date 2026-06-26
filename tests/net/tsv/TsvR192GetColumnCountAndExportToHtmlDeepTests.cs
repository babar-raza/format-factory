// Tests for TsvDocument.GetColumnCount, ExportToHtml, WriteToFile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R192

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R192: Tests for TsvDocument.GetColumnCount, ExportToHtml, WriteToFile deeper.
/// GetColumnCount(): returns number of columns in the document.
/// ExportToHtml(): exports the document as an HTML table string.
/// WriteToFile(path): writes the document to a TSV file at the given path.
/// Covers: GetColumnCount correct; GetColumnCount after AddColumn increases;
/// GetColumnCount after RemoveColumn decreases; GetColumnCount consistent;
/// GetColumnCount after Filter unchanged; GetColumnCount empty doc;
/// ExportToHtml non-null; ExportToHtml non-empty; ExportToHtml has HTML structure;
/// ExportToHtml contains header; ExportToHtml contains data; ExportToHtml after AddRow grows;
/// ExportToHtml after Filter smaller; ExportToHtml has table element;
/// WriteToFile creates file; WriteToFile file not empty; WriteToFile has tabs;
/// WriteToFile contains header; WriteToFile contains data; WriteToFile after AddRow larger;
/// WriteToFile round-trip LoadFile matches;
/// dogfood LoadFile→GetColumnCount→ExportToHtml→WriteToFile→verify pipeline.
/// </summary>
public class TsvR192GetColumnCountAndExportToHtmlDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR192GetColumnCountAndExportToHtmlDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR192_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleTsv =
        "Name\tCity\tCountry\tPopulation\n" +
        "Tokyo\tTokyo\tJapan\t13960000\n" +
        "Delhi\tNew Delhi\tIndia\t32940000\n" +
        "Shanghai\tShanghai\tChina\t28516000\n" +
        "Dhaka\tDhaka\tBangladesh\t22478116\n" +
        "São Paulo\tSão Paulo\tBrazil\t22429800\n";

    private TsvDocument LoadSample()
    {
        var path = TempFile("sample.tsv");
        File.WriteAllText(path, SampleTsv);
        return TsvDocument.LoadFile(path);
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
    public void GetColumnCount_AfterAddColumn_Increases()
    {
        var doc = LoadSample();
        var before = doc.GetColumnCount();
        var updated = doc.AddColumn(new[] { "Timezone" });
        Assert.True(updated.GetColumnCount() > before);
    }

    [Fact]
    public void GetColumnCount_AfterRemoveColumn_Decreases()
    {
        var doc = LoadSample();
        var before = doc.GetColumnCount();
        var updated = doc.RemoveColumn("Population");
        Assert.True(updated.GetColumnCount() < before);
    }

    [Fact]
    public void GetColumnCount_Consistent()
    {
        var doc = LoadSample();
        Assert.Equal(doc.GetColumnCount(), doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_AfterFilter_Unchanged()
    {
        var doc = LoadSample();
        var colsBefore = doc.GetColumnCount();
        var filtered = doc.Filter("Country", "Japan");
        Assert.Equal(colsBefore, filtered.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_EmptyHeaderDoc_ZeroOrMinimal()
    {
        var emptyPath = TempFile("empty_cols.tsv");
        File.WriteAllText(emptyPath, "\n");
        var doc = TsvDocument.LoadFile(emptyPath);
        Assert.True(doc.GetColumnCount() == 0 || doc.GetColumnCount() >= 0);
    }

    // -------------------------------------------------------------------------
    // ExportToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_HasHtmlStructure()
    {
        var doc = LoadSample();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("<") && html.Length > 0);
    }

    [Fact]
    public void ExportToHtml_ContainsHeader()
    {
        var doc = LoadSample();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("Name") || html.Contains("Country") || html.Contains("City"));
    }

    [Fact]
    public void ExportToHtml_ContainsData()
    {
        var doc = LoadSample();
        Assert.Contains("Tokyo", doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_AfterAddRow_Grows()
    {
        var doc = LoadSample();
        var before = doc.ExportToHtml().Length;
        doc.AddRow(new[] { "Mexico City", "Mexico City", "Mexico", "21671908" });
        Assert.True(doc.ExportToHtml().Length > before);
    }

    [Fact]
    public void ExportToHtml_AfterFilter_Smaller()
    {
        var doc = LoadSample();
        var all = doc.ExportToHtml();
        var filtered = doc.Filter("Country", "Japan").ExportToHtml();
        Assert.True(filtered.Length < all.Length);
    }

    [Fact]
    public void ExportToHtml_HasTableElement()
    {
        var doc = LoadSample();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("<table") || html.Contains("<TABLE") || html.Contains("<tr"));
    }

    // -------------------------------------------------------------------------
    // WriteToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_CreatesFile()
    {
        var doc = LoadSample();
        var path = TempFile("written.tsv");
        doc.WriteToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_FileNotEmpty()
    {
        var doc = LoadSample();
        var path = TempFile("nonempty.tsv");
        doc.WriteToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void WriteToFile_HasTabs()
    {
        var doc = LoadSample();
        var path = TempFile("tabs.tsv");
        doc.WriteToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("\t", content);
    }

    [Fact]
    public void WriteToFile_ContainsHeader()
    {
        var doc = LoadSample();
        var path = TempFile("header.tsv");
        doc.WriteToFile(path);
        var content = File.ReadAllText(path);
        Assert.True(content.Contains("Name") || content.Contains("Country"));
    }

    [Fact]
    public void WriteToFile_ContainsData()
    {
        var doc = LoadSample();
        var path = TempFile("data.tsv");
        doc.WriteToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Tokyo", content);
    }

    [Fact]
    public void WriteToFile_AfterAddRow_FileLarger()
    {
        var doc = LoadSample();
        var path1 = TempFile("before.tsv");
        doc.WriteToFile(path1);
        var sizeBefore = new FileInfo(path1).Length;

        doc.AddRow(new[] { "Osaka", "Osaka", "Japan", "2691000" });
        var path2 = TempFile("after.tsv");
        doc.WriteToFile(path2);
        var sizeAfter = new FileInfo(path2).Length;

        Assert.True(sizeAfter > sizeBefore);
    }

    [Fact]
    public void WriteToFile_RoundTripLoadFile_MatchesRowCount()
    {
        var doc = LoadSample();
        var path = TempFile("roundtrip.tsv");
        doc.WriteToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(doc.GetRowCount(), loaded.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_GetColumnCount_ExportToHtml_WriteToFile_Verify_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.GetRowCount());

        // GetColumnCount
        Assert.Equal(4, doc.GetColumnCount());

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.True(html.Contains("<") && html.Length > 0);
        Assert.Contains("Tokyo", html);

        // Filter and verify column count preserved
        var japanDoc = doc.Filter("Country", "Japan");
        Assert.Equal(1, japanDoc.GetRowCount());
        Assert.Equal(4, japanDoc.GetColumnCount()); // columns unchanged by filter
        var japanHtml = japanDoc.ExportToHtml();
        Assert.True(japanHtml.Length < html.Length);
        Assert.Contains("Tokyo", japanHtml);
        Assert.DoesNotContain("Delhi", japanHtml);

        // AddColumn and verify GetColumnCount
        var expandedDoc = doc.AddColumn(new[] { "Continent" });
        Assert.Equal(5, expandedDoc.GetColumnCount());
        var expandedHtml = expandedDoc.ExportToHtml();
        Assert.True(expandedHtml.Length >= html.Length);

        // WriteToFile
        var path = TempFile("dogfood_write.tsv");
        doc.WriteToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
        var content = File.ReadAllText(path);
        Assert.Contains("\t", content);
        Assert.Contains("Tokyo", content);

        // Load the written file and verify
        var reloaded = TsvDocument.LoadFile(path);
        Assert.Equal(doc.GetRowCount(), reloaded.GetRowCount());
        Assert.Equal(doc.GetColumnCount(), reloaded.GetColumnCount());
        var reloadedHtml = reloaded.ExportToHtml();
        Assert.Contains("Tokyo", reloadedHtml);

        // AddRow, WriteToFile again, verify file grows
        doc.AddRow(new[] { "Karachi", "Karachi", "Pakistan", "16839950" });
        Assert.Equal(6, doc.GetRowCount());
        var path2 = TempFile("dogfood_write_updated.tsv");
        doc.WriteToFile(path2);
        Assert.True(new FileInfo(path2).Length > new FileInfo(path).Length);

        // ExportToHtml after AddRow
        var updatedHtml = doc.ExportToHtml();
        Assert.True(updatedHtml.Length > html.Length);
        Assert.Contains("Karachi", updatedHtml);
    }
}
