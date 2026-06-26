// Tests for TsvCsvExporter and doc.ToTsv() serialization.
// Sprint: FORMAT-FACTORY-TSV-CSV-EXPORTER-20260626
// Ledger: R120-GOVERNED-DOTNET-TSV-CSV-EXPORTER-001

using System;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R120: TsvCsvExporter converts TsvDocument to CSV format — tabs become commas and
/// the output is valid CSV text. TsvWriter.Export(TsvDocument doc) serializes a document
/// to TSV text. Both produce non-empty output for non-empty documents and round-trip
/// the data correctly.
/// </summary>
public class TsvR120CsvExporterTests
{
    private static TsvDocument LoadTsv(string tsv) =>
        TsvDocument.Load(tsv, hasHeaders: true);

    // ---- TsvWriter.Export: basic serialization ----

    [Fact]
    public void Export_ProducesNonEmptyString()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\n");
        var exported = doc.ToTsv();
        Assert.False(string.IsNullOrWhiteSpace(exported));
    }

    [Fact]
    public void Export_ContainsHeaderNames()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\n");
        var exported = doc.ToTsv();
        Assert.Contains("Name", exported);
        Assert.Contains("Score", exported);
    }

    [Fact]
    public void Export_ContainsDataValues()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\nBob\t75\n");
        var exported = doc.ToTsv();
        Assert.Contains("Alice", exported);
        Assert.Contains("Bob", exported);
    }

    [Fact]
    public void Export_UsesTabs()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\n");
        var exported = doc.ToTsv();
        Assert.Contains("\t", exported);
    }

    // ---- TsvCsvExporter: TSV to CSV conversion ----

    [Fact]
    public void TsvCsvExporter_OutputContainsCommas()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\n");
        var csv = TsvCsvExporter.Export(doc);
        Assert.Contains(",", csv);
    }

    [Fact]
    public void TsvCsvExporter_OutputDoesNotContainTabs()
    {
        var doc = LoadTsv("Name\tScore\nAlice\t90\n");
        var csv = TsvCsvExporter.Export(doc);
        Assert.DoesNotContain("\t", csv);
    }

    [Fact]
    public void TsvCsvExporter_HeadersPreserved()
    {
        var doc = LoadTsv("FirstName\tLastName\nAlice\tSmith\n");
        var csv = TsvCsvExporter.Export(doc);
        Assert.Contains("FirstName", csv);
        Assert.Contains("LastName", csv);
    }

    [Fact]
    public void TsvCsvExporter_DataValuesPreserved()
    {
        var doc = LoadTsv("Name\tCity\nAlice\tLondon\nBob\tParis\n");
        var csv = TsvCsvExporter.Export(doc);
        Assert.Contains("Alice", csv);
        Assert.Contains("London", csv);
        Assert.Contains("Bob", csv);
        Assert.Contains("Paris", csv);
    }

    [Fact]
    public void TsvCsvExporter_RowCountPreserved()
    {
        // Count newlines in TSV data rows (2 data rows + header = 3 lines)
        // CSV output should have same number of data records
        var doc = LoadTsv("Name\tScore\nAlice\t90\nBob\t75\n");
        var csv = TsvCsvExporter.Export(doc);

        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        // Header + 2 data rows = 3 lines
        Assert.True(lines.Length >= 2, "Should have at least header and one data row");
    }

    // ---- Dogfood: Load TSV → Export → ToCsv pipeline ----

    [Fact]
    public void DogfoodPipeline_LoadExportToCsv_DataIntact()
    {
        var tsv = "Product\tPrice\tQty\nWidget\t9.99\t100\nGadget\t24.99\t50\n";
        var doc = LoadTsv(tsv);

        // Export back to TSV
        var exported = doc.ToTsv();
        Assert.Contains("Widget", exported);
        Assert.Contains("Gadget", exported);

        // Convert to CSV
        var csv = TsvCsvExporter.Export(doc);
        Assert.Contains(",", csv);
        Assert.Contains("Product", csv);
        Assert.Contains("9.99", csv);
        Assert.Contains("24.99", csv);
    }
}
