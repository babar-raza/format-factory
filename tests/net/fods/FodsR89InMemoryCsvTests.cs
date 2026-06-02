// R89 Train I: FODS In-Memory CSV Export Tests
// New API: ExportSheetToCsvString
// Sprint: FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR89InMemoryCsvExportTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string SampleFodsPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void ExportSheetToCsvString_ReturnsNonEmptyString()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var sheet = doc.Sheets[0];
        var csv = FodsCsvExporter.ExportSheetToCsvString(sheet);
        Assert.False(string.IsNullOrEmpty(csv));
    }

    [Fact]
    public void ExportSheetToCsvString_ContainsCellValues()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var sheet = doc.Sheets[0];
        var csv = FodsCsvExporter.ExportSheetToCsvString(sheet);
        // The sample has at least one non-empty cell
        Assert.True(csv.Length > 2, "CSV should contain cell data");
    }

    [Fact]
    public void ExportSheetToCsvString_UsesLfLineEndings()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var sheet = doc.Sheets[0];
        var csv = FodsCsvExporter.ExportSheetToCsvString(sheet);
        // Should have LF endings, not CRLF
        Assert.DoesNotContain("\r\n", csv);
        Assert.Contains("\n", csv);
    }

    [Fact]
    public void ExportSheetToCsvString_NullSheet_Throws()
    {
        Assert.Throws<System.ArgumentNullException>(() =>
            FodsCsvExporter.ExportSheetToCsvString(null!));
    }

    [Fact]
    public void ExportSheetToCsvString_RowCountMatchesSheet()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var sheet = doc.Sheets[0];
        var csv = FodsCsvExporter.ExportSheetToCsvString(sheet);
        // Count LF-terminated lines (last line ends with \n too)
        int lineCount = csv.Split('\n', System.StringSplitOptions.RemoveEmptyEntries).Length;
        Assert.Equal(sheet.Rows.Count, lineCount);
    }

    [Fact]
    public void ExportSheetToCsvString_EscapesCsvSpecialChars()
    {
        // Verify the EscapeCsvField static method works
        var escaped = FodsCsvExporter.EscapeCsvField("hello,world");
        Assert.Equal("\"hello,world\"", escaped);
    }
}
