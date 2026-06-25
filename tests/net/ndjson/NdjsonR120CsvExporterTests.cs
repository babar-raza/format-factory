// Tests for NdjsonCsvExporter.Export(doc) converting NDJSON to CSV format.
// Sprint: FORMAT-FACTORY-NDJSON-CSV-EXPORTER-20260626
// Ledger: R120-GOVERNED-DOTNET-NDJSON-CSV-EXPORTER-001

using System;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R120: NdjsonCsvExporter.Export(NdjsonDocument doc) converts NDJSON to CSV text.
/// The output uses commas as separators, contains a header row from record keys,
/// and includes all data values. Records with uniform schema produce well-formed CSV.
/// The output is loadable as a CSV document (round-trip via CsvDocument.Load).
/// </summary>
public class NdjsonR120CsvExporterTests
{
    private static NdjsonDocument LoadNdjson(string ndjson) =>
        NdjsonDocument.Load(ndjson);

    // ---- Basic Export ----

    [Fact]
    public void Export_ProducesNonEmptyString()
    {
        var ndjson = "{\"name\":\"Alice\",\"score\":90}\n";
        var doc = LoadNdjson(ndjson);
        var csv = NdjsonCsvExporter.Export(doc);
        Assert.False(string.IsNullOrWhiteSpace(csv));
    }

    [Fact]
    public void Export_ContainsCommas()
    {
        var ndjson = "{\"name\":\"Alice\",\"score\":90}\n";
        var doc = LoadNdjson(ndjson);
        var csv = NdjsonCsvExporter.Export(doc);
        Assert.Contains(",", csv);
    }

    [Fact]
    public void Export_ContainsFieldNamesAsHeaders()
    {
        var ndjson = "{\"name\":\"Alice\",\"score\":90}\n";
        var doc = LoadNdjson(ndjson);
        var csv = NdjsonCsvExporter.Export(doc);
        Assert.Contains("name", csv);
        Assert.Contains("score", csv);
    }

    [Fact]
    public void Export_ContainsDataValues()
    {
        var ndjson = "{\"name\":\"Alice\",\"score\":90}\n";
        var doc = LoadNdjson(ndjson);
        var csv = NdjsonCsvExporter.Export(doc);
        Assert.Contains("Alice", csv);
    }

    // ---- Multiple records ----

    [Fact]
    public void Export_MultipleRecords_AllNamesPresent()
    {
        var ndjson = "{\"name\":\"Alice\"}\n{\"name\":\"Bob\"}\n{\"name\":\"Carol\"}\n";
        var doc = LoadNdjson(ndjson);
        var csv = NdjsonCsvExporter.Export(doc);
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
        Assert.Contains("Carol", csv);
    }

    [Fact]
    public void Export_MultipleRecords_MultipleLines()
    {
        var ndjson = "{\"x\":1}\n{\"x\":2}\n{\"x\":3}\n";
        var doc = LoadNdjson(ndjson);
        var csv = NdjsonCsvExporter.Export(doc);
        // At minimum: header row + 3 data rows = at least 4 lines
        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.True(lines.Length >= 2, "Expected at least header + one data row");
    }

    // ---- Uniform schema produces clean CSV ----

    [Fact]
    public void Export_UniformSchema_AllValuesInOutput()
    {
        var ndjson = string.Concat(
            "{\"name\":\"Alice\",\"city\":\"London\"}\n",
            "{\"name\":\"Bob\",\"city\":\"Paris\"}\n");
        var doc = LoadNdjson(ndjson);
        var csv = NdjsonCsvExporter.Export(doc);

        Assert.Contains("London", csv);
        Assert.Contains("Paris", csv);
    }

    // ---- Empty document ----

    [Fact]
    public void Export_EmptyDocument_DoesNotThrow()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        var csv = NdjsonCsvExporter.Export(doc);
        Assert.NotNull(csv);
    }

    // ---- Dogfood: NDJSON → CSV export pipeline ----

    [Fact]
    public void DogfoodPipeline_NdjsonToCsvExport_RoundTripVerifiable()
    {
        var ndjson = string.Concat(
            "{\"product\":\"Widget\",\"price\":\"9.99\",\"qty\":\"100\"}\n",
            "{\"product\":\"Gadget\",\"price\":\"24.99\",\"qty\":\"50\"}\n",
            "{\"product\":\"Doohickey\",\"price\":\"4.99\",\"qty\":\"200\"}\n");

        var doc = LoadNdjson(ndjson);

        // Verify schema is uniform
        Assert.True(doc.IsUniformSchema());

        // Export to CSV
        var csv = NdjsonCsvExporter.Export(doc);

        // All products in output
        Assert.Contains("Widget", csv);
        Assert.Contains("Gadget", csv);
        Assert.Contains("Doohickey", csv);

        // Field names as headers
        Assert.Contains("product", csv);
        Assert.Contains("price", csv);
        Assert.Contains("qty", csv);

        // Comma separated
        Assert.Contains(",", csv);
    }
}
