using Xunit;
using System;
using System.IO;
using FormatFactory.Fods;

namespace FormatFactory.Fods.Tests;

public class FodsR113InsertRowDepthTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));
    private static string SamplePath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void InsertRowWithValues_SaveReload_PreservesValues()
    {
        var doc = FodsDocument.Load(SamplePath);
        var name = doc.Sheets[0].Name;
        doc.InsertRowWithValues(name, 0, new[] { "X", "Y", "Z" });
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("X", FodsDocument.GetCellValue(reloaded.Sheets[0], 0, 0));
            Assert.Equal("Y", FodsDocument.GetCellValue(reloaded.Sheets[0], 0, 1));
            Assert.Equal("Z", FodsDocument.GetCellValue(reloaded.Sheets[0], 0, 2));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void InsertRowWithValues_IncreasesRowCount()
    {
        var doc = FodsDocument.Load(SamplePath);
        var name = doc.Sheets[0].Name;
        int before = doc.GetRowCount(name);
        doc.InsertRowWithValues(name, 0, new[] { "A" });
        Assert.True(doc.GetRowCount(name) > before);
    }

    [Fact]
    public void InsertRowWithValues_ExportCsv_ContainsValue()
    {
        var doc = FodsDocument.Load(SamplePath);
        var name = doc.Sheets[0].Name;
        doc.InsertRowWithValues(name, 0, new[] { "CsvTest" });
        var csv = doc.ExportSheetToCsv(name);
        Assert.Contains("CsvTest", csv);
    }

    [Fact]
    public void InsertRowWithValues_ThenSort_PreservesData()
    {
        var doc = FodsDocument.Load(SamplePath);
        doc.AddSheet("SortIns");
        doc.InsertRowWithValues("SortIns", 0, new[] { "Zebra" });
        doc.InsertRowWithValues("SortIns", 1, new[] { "Apple" });
        doc.SortRows("SortIns", 0, ascending: true);
        var sheet = doc.GetSheetByName("SortIns")!;
        Assert.Equal("Apple", FodsDocument.GetCellValue(sheet, 0, 0));
    }

    [Fact]
    public void InsertRowWithValues_MultipleRows_AllPreservedAfterSave()
    {
        var doc = FodsDocument.Load(SamplePath);
        var name = doc.Sheets[0].Name;
        doc.InsertRowWithValues(name, 0, new[] { "R1" });
        doc.InsertRowWithValues(name, 1, new[] { "R2" });
        doc.InsertRowWithValues(name, 2, new[] { "R3" });
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("R1", FodsDocument.GetCellValue(reloaded.Sheets[0], 0, 0));
            Assert.Equal("R2", FodsDocument.GetCellValue(reloaded.Sheets[0], 1, 0));
            Assert.Equal("R3", FodsDocument.GetCellValue(reloaded.Sheets[0], 2, 0));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void InsertRowWithValues_GetUsedRange_Consistent()
    {
        var doc = FodsDocument.Load(SamplePath);
        var name = doc.Sheets[0].Name;
        doc.InsertRowWithValues(name, 0, new[] { "A", "B", "C" });
        var range = doc.GetUsedRange(name);
        Assert.NotNull(range);
        Assert.Equal(0, range!.Value.MinRow);
        Assert.Equal(0, range.Value.MinCol);
    }
}
