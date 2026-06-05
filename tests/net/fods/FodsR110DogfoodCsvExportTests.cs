// R110 Wave 6: FODS CSV Export Dogfood Pipeline Tests
// Dogfood: load→edit→ExportSheetToCsv pipeline

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR110DogfoodCsvExportTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void Dogfood_LoadEditExportCsv_Pipeline()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        Assert.NotEmpty(names);
        doc.SetCellValue(0, 0, "DogfoodR110");
        var csv = doc.ExportSheetToCsv(names[0]);
        Assert.Contains("DogfoodR110", csv);
    }

    [Fact]
    public void Dogfood_CsvExport_MultipleRows()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        var csv = doc.ExportSheetToCsv(names[0]);
        Assert.NotNull(csv);
        Assert.True(csv.Length > 0);
    }

    [Fact]
    public void Dogfood_FindThenExport_Pipeline()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        doc.SetCellValue(0, 0, "SEARCH_ME");
        var found = doc.FindCellsByValue(names[0], "SEARCH_ME");
        Assert.NotEmpty(found);
        var csv = doc.ExportSheetToCsv(names[0]);
        Assert.Contains("SEARCH_ME", csv);
    }

    [Fact]
    public void Dogfood_HasSheetThenExport_Pipeline()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        Assert.True(doc.HasSheet(names[0]));
        var csv = doc.ExportSheetToCsv(names[0]);
        Assert.NotEmpty(csv);
    }
}
