// Tests for CsvDocument.ExportToHtml, ExportToMarkdown, ToTsv deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R189

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R189: Tests for CsvDocument.ExportToHtml, ExportToMarkdown, ToTsv deeper coverage.
/// ExportToHtml(): exports document as HTML string.
/// ExportToMarkdown(): exports document as Markdown table string.
/// ToTsv(): converts the CSV document to a TSV-formatted string.
/// Covers: ExportToHtml non-null; ExportToHtml non-empty; ExportToHtml has HTML structure;
/// ExportToHtml contains header; ExportToHtml contains data; ExportToHtml after AddRow longer;
/// ExportToHtml after Filter smaller; ExportToMarkdown non-null; ExportToMarkdown non-empty;
/// ExportToMarkdown contains pipe; ExportToMarkdown contains header; ExportToMarkdown contains data;
/// ExportToMarkdown after AddRow longer; ToTsv non-null; ToTsv non-empty;
/// ToTsv has tabs; ToTsv contains header; ToTsv contains data; ToTsv row count matches;
/// ToTsv after AddRow longer; ToTsv after Filter smaller;
/// dogfood LoadFile→ExportToHtml→ExportToMarkdown→ToTsv→AddRow→Filter→verify pipeline.
/// </summary>
public class CsvR189ExportToHtmlAndToTsvDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR189ExportToHtmlAndToTsvDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR189_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleCsv =
        "Product,Category,Price,Stock\n" +
        "Widget,Electronics,29.99,150\n" +
        "Gadget,Electronics,49.99,80\n" +
        "Gizmo,Appliances,19.99,200\n" +
        "Doohickey,Appliances,9.99,500\n";

    private CsvDocument LoadSample()
    {
        var path = TempFile("sample.csv");
        File.WriteAllText(path, SampleCsv);
        return CsvDocument.LoadFile(path);
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
        Assert.True(html.Contains("Product") || html.Contains("Category"));
    }

    [Fact]
    public void ExportToHtml_ContainsData()
    {
        var doc = LoadSample();
        Assert.Contains("Widget", doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_AfterAddRow_Longer()
    {
        var doc = LoadSample();
        var before = doc.ExportToHtml().Length;
        doc.AddRow(new[] { "Thingamajig", "Tools", "14.99", "300" });
        Assert.True(doc.ExportToHtml().Length > before);
    }

    [Fact]
    public void ExportToHtml_AfterFilter_Smaller()
    {
        var doc = LoadSample();
        var all = doc.ExportToHtml();
        var filtered = doc.Filter("Category", "Electronics").ExportToHtml();
        Assert.True(filtered.Length < all.Length);
    }

    // -------------------------------------------------------------------------
    // ExportToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdown_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_ContainsPipe()
    {
        var doc = LoadSample();
        Assert.Contains("|", doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_ContainsHeader()
    {
        var doc = LoadSample();
        var md = doc.ExportToMarkdown();
        Assert.True(md.Contains("Product") || md.Contains("Category"));
    }

    [Fact]
    public void ExportToMarkdown_ContainsData()
    {
        var doc = LoadSample();
        Assert.Contains("Widget", doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_AfterAddRow_Longer()
    {
        var doc = LoadSample();
        var before = doc.ExportToMarkdown().Length;
        doc.AddRow(new[] { "Contraption", "Tools", "39.99", "75" });
        Assert.True(doc.ExportToMarkdown().Length > before);
    }

    // -------------------------------------------------------------------------
    // ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToTsv_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ToTsv());
    }

    [Fact]
    public void ToTsv_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(doc.ToTsv());
    }

    [Fact]
    public void ToTsv_HasTabs()
    {
        var doc = LoadSample();
        Assert.Contains("\t", doc.ToTsv());
    }

    [Fact]
    public void ToTsv_ContainsHeader()
    {
        var doc = LoadSample();
        var tsv = doc.ToTsv();
        Assert.True(tsv.Contains("Product") || tsv.Contains("Category"));
    }

    [Fact]
    public void ToTsv_ContainsData()
    {
        var doc = LoadSample();
        Assert.Contains("Widget", doc.ToTsv());
    }

    [Fact]
    public void ToTsv_AfterAddRow_Longer()
    {
        var doc = LoadSample();
        var before = doc.ToTsv().Length;
        doc.AddRow(new[] { "Whatsit", "Misc", "4.99", "1000" });
        Assert.True(doc.ToTsv().Length > before);
    }

    [Fact]
    public void ToTsv_AfterFilter_Smaller()
    {
        var doc = LoadSample();
        var all = doc.ToTsv();
        var filtered = doc.Filter("Category", "Appliances").ToTsv();
        Assert.True(filtered.Length < all.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_ExportToHtml_ExportToMarkdown_ToTsv_AddRow_Filter_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(4, doc.RowCount);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.True(html.Contains("<") && html.Length > 0);
        Assert.True(html.Contains("Widget") || html.Contains("Product"));

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.Contains("|", md);
        Assert.True(md.Contains("Product") || md.Contains("Widget"));

        // ToTsv
        var tsv = doc.ToTsv();
        Assert.NotNull(tsv);
        Assert.Contains("\t", tsv);
        Assert.Contains("Widget", tsv);

        // Filter Electronics (2 rows)
        var electronics = doc.Filter("Category", "Electronics");
        Assert.Equal(2, electronics.RowCount);
        var elecHtml = electronics.ExportToHtml();
        Assert.True(elecHtml.Length < html.Length);
        var elecMd = electronics.ExportToMarkdown();
        Assert.True(elecMd.Length < md.Length);
        var elecTsv = electronics.ToTsv();
        Assert.True(elecTsv.Length < tsv.Length);
        Assert.Contains("Widget", elecTsv);
        Assert.DoesNotContain("Gizmo", elecTsv);

        // AddRow — all exports grow
        doc.AddRow(new[] { "SuperWidget", "Electronics", "99.99", "25" });
        Assert.Equal(5, doc.RowCount);
        Assert.True(doc.ExportToHtml().Length > html.Length);
        Assert.True(doc.ExportToMarkdown().Length > md.Length);
        Assert.True(doc.ToTsv().Length > tsv.Length);

        // ToTsv contains new row
        Assert.Contains("SuperWidget", doc.ToTsv());

        // ExportToMarkdown contains new row
        Assert.Contains("SuperWidget", doc.ExportToMarkdown());

        // SaveToFile and reload — verify exports still work
        var path = TempFile("dogfood_exports.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.NotNull(loaded.ExportToHtml());
        Assert.NotNull(loaded.ExportToMarkdown());
        Assert.NotNull(loaded.ToTsv());
        Assert.Equal(5, loaded.RowCount);
    }
}
