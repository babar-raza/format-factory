// Tests for FodsHtmlExporter.ExportToHtml() and FodsJsonExporter.ExportToJson() result objects.
// Sprint: FORMAT-FACTORY-FODS-EXPORT-RESULT-R134-20260627
// Ledger: R134-GOVERNED-DOTNET-FODS-EXPORT-RESULT-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R134: FodsHtmlExporter.ExportToHtml(doc, sourcePath, htmlPath) returns a
/// FodsHtmlExportResult with SheetsExported >= 1, TotalRowsExported >= 0, and
/// non-empty SourcePath/OutputPath. FodsJsonExporter.ExportToJson(doc, sourcePath,
/// jsonPath) returns FodsJsonExportResult with Status and Warnings accessible.
/// Both exporters write to the given output path and the output file exists afterward.
/// </summary>
public class FodsR134ExportResultObjectTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory, "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    private static string TempPath(string ext) =>
        Path.Combine(Path.GetTempPath(), $"ff_fods_r134_{Guid.NewGuid():N}{ext}");

    // ---- FodsHtmlExportResult: SheetsExported ----

    [Fact]
    public void ExportToHtml_Result_SheetsExportedAtLeastOne()
    {
        var doc   = FodsDocument.Load(MinimalPath);
        var html  = TempPath(".html");
        try
        {
            var result = FodsHtmlExporter.ExportToHtml(doc, MinimalPath, html);
            Assert.True(result.SheetsExported >= 1);
        }
        finally { if (File.Exists(html)) File.Delete(html); }
    }

    [Fact]
    public void ExportToHtml_Result_TotalRowsExportedNonNegative()
    {
        var doc  = FodsDocument.Load(MinimalPath);
        var html = TempPath(".html");
        try
        {
            var result = FodsHtmlExporter.ExportToHtml(doc, MinimalPath, html);
            Assert.True(result.TotalRowsExported >= 0);
        }
        finally { if (File.Exists(html)) File.Delete(html); }
    }

    [Fact]
    public void ExportToHtml_Result_OutputPathMatches()
    {
        var doc  = FodsDocument.Load(MinimalPath);
        var html = TempPath(".html");
        try
        {
            var result = FodsHtmlExporter.ExportToHtml(doc, MinimalPath, html);
            Assert.Equal(html, result.OutputPath);
        }
        finally { if (File.Exists(html)) File.Delete(html); }
    }

    [Fact]
    public void ExportToHtml_Result_OutputFileExists()
    {
        var doc  = FodsDocument.Load(MinimalPath);
        var html = TempPath(".html");
        try
        {
            FodsHtmlExporter.ExportToHtml(doc, MinimalPath, html);
            Assert.True(File.Exists(html));
        }
        finally { if (File.Exists(html)) File.Delete(html); }
    }

    [Fact]
    public void ExportToHtml_Result_SourcePathPreserved()
    {
        var doc  = FodsDocument.Load(MinimalPath);
        var html = TempPath(".html");
        try
        {
            var result = FodsHtmlExporter.ExportToHtml(doc, MinimalPath, html);
            Assert.Equal(MinimalPath, result.SourcePath);
        }
        finally { if (File.Exists(html)) File.Delete(html); }
    }

    // ---- FodsJsonExportResult: Status, Warnings, SheetsExported ----

    [Fact]
    public void ExportToJson_Result_SheetsExportedAtLeastOne()
    {
        var doc  = FodsDocument.Load(MinimalPath);
        var json = TempPath(".json");
        try
        {
            var result = FodsJsonExporter.ExportToJson(doc, MinimalPath, json);
            Assert.True(result.SheetsExported >= 1);
        }
        finally { if (File.Exists(json)) File.Delete(json); }
    }

    [Fact]
    public void ExportToJson_Result_StatusIsNotNull()
    {
        var doc  = FodsDocument.Load(MinimalPath);
        var json = TempPath(".json");
        try
        {
            var result = FodsJsonExporter.ExportToJson(doc, MinimalPath, json);
            Assert.NotNull(result.Status);
        }
        finally { if (File.Exists(json)) File.Delete(json); }
    }

    [Fact]
    public void ExportToJson_Result_WarningsIsNotNull()
    {
        var doc  = FodsDocument.Load(MinimalPath);
        var json = TempPath(".json");
        try
        {
            var result = FodsJsonExporter.ExportToJson(doc, MinimalPath, json);
            Assert.NotNull(result.Warnings);
        }
        finally { if (File.Exists(json)) File.Delete(json); }
    }

    [Fact]
    public void ExportToJson_Result_OutputFileExists()
    {
        var doc  = FodsDocument.Load(MinimalPath);
        var json = TempPath(".json");
        try
        {
            FodsJsonExporter.ExportToJson(doc, MinimalPath, json);
            Assert.True(File.Exists(json));
        }
        finally { if (File.Exists(json)) File.Delete(json); }
    }

    // ---- Dogfood: export both formats and compare metadata ----

    [Fact]
    public void DogfoodPipeline_HtmlAndJsonBothExported_MetadataConsistent()
    {
        var doc  = FodsDocument.Load(MinimalPath);
        var html = TempPath(".html");
        var json = TempPath(".json");
        try
        {
            var htmlResult = FodsHtmlExporter.ExportToHtml(doc, MinimalPath, html);
            var jsonResult = FodsJsonExporter.ExportToJson(doc, MinimalPath, json);

            // Both export the same number of sheets
            Assert.Equal(htmlResult.SheetsExported, jsonResult.SheetsExported);

            // Both output files exist
            Assert.True(File.Exists(html));
            Assert.True(File.Exists(json));

            // JSON result has non-empty status
            Assert.False(string.IsNullOrWhiteSpace(jsonResult.Status));
        }
        finally
        {
            if (File.Exists(html)) File.Delete(html);
            if (File.Exists(json)) File.Delete(json);
        }
    }
}
