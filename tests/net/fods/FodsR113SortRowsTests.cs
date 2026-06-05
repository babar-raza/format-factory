using Xunit;
using System;
using System.IO;
using FormatFactory.Fods;

namespace FormatFactory.Fods.Tests;

public class FodsR113SortRowsTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));
    private static string SamplePath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    private (FodsDocument doc, string sheetName) CreateCleanSheet(params string[] rowValues)
    {
        var doc = FodsDocument.Load(SamplePath);
        var sheet = doc.AddSheet("SortTest");
        for (int i = 0; i < rowValues.Length; i++)
            doc.InsertRowWithValues("SortTest", i, new[] { rowValues[i] });
        return (doc, "SortTest");
    }

    [Fact]
    public void SortRows_Ascending_SortsCorrectly()
    {
        var (doc, name) = CreateCleanSheet("Banana", "Apple", "Cherry");
        doc.SortRows(name, 0, ascending: true);
        var sheet = doc.GetSheetByName(name)!;
        Assert.Equal("Apple", FodsDocument.GetCellValue(sheet, 0, 0));
    }

    [Fact]
    public void SortRows_Descending_SortsCorrectly()
    {
        var (doc, name) = CreateCleanSheet("A", "C", "B");
        doc.SortRows(name, 0, ascending: false);
        var sheet = doc.GetSheetByName(name)!;
        Assert.Equal("C", FodsDocument.GetCellValue(sheet, 0, 0));
    }

    [Fact]
    public void SortRows_NumericValues_SortsNumerically()
    {
        var (doc, name) = CreateCleanSheet("10", "2", "30");
        doc.SortRows(name, 0, ascending: true);
        var sheet = doc.GetSheetByName(name)!;
        Assert.Equal("2", FodsDocument.GetCellValue(sheet, 0, 0));
    }

    [Fact]
    public void SortRows_SingleRow_NoChange()
    {
        var (doc, name) = CreateCleanSheet("OnlyRow");
        doc.SortRows(name, 0);
        var sheet = doc.GetSheetByName(name)!;
        Assert.Equal("OnlyRow", FodsDocument.GetCellValue(sheet, 0, 0));
    }

    [Fact]
    public void SortRows_NullSheetName_Throws()
    {
        var doc = FodsDocument.Load(SamplePath);
        Assert.Throws<ArgumentException>(() => doc.SortRows(null!, 0));
    }

    [Fact]
    public void SortRows_InvalidSheetName_Throws()
    {
        var doc = FodsDocument.Load(SamplePath);
        Assert.Throws<InvalidOperationException>(() => doc.SortRows("NoSuchSheet", 0));
    }

    [Fact]
    public void SortRows_NegativeColumn_Throws()
    {
        var doc = FodsDocument.Load(SamplePath);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SortRows(doc.Sheets[0].Name, -1));
    }

    [Fact]
    public void SortRows_SaveRoundtrip_PreservesSort()
    {
        var (doc, name) = CreateCleanSheet("Z", "A");
        doc.SortRows(name, 0, ascending: true);
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var sheet = reloaded.GetSheetByName(name)!;
            Assert.Equal("A", FodsDocument.GetCellValue(sheet, 0, 0));
            Assert.Equal("Z", FodsDocument.GetCellValue(sheet, 1, 0));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
