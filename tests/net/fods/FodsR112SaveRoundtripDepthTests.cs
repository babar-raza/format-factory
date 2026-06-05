using Xunit;
using System;
using System.IO;
using FormatFactory.Fods;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R112 depth: FODS formula+merge save-reload roundtrip verification.
/// Proves that SetCellFormula, MergeCells, GetUsedRange survive Save→Load.
/// </summary>
public class FodsR112SaveRoundtripDepthTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));
    private static string SamplePath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void Formula_SurvivesSaveReload()
    {
        var doc = FodsDocument.Load(SamplePath);
        var name = doc.Sheets[0].Name;
        doc.SetCellFormula(name, 0, 0, "=A2+A3");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("=A2+A3", reloaded.GetCellFormula(reloaded.Sheets[0].Name, 0, 0));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void MergeCells_SurvivesSaveReload()
    {
        var doc = FodsDocument.Load(Path.Combine(SamplesDir, "multi-sheet-basic.fods"));
        var name = doc.Sheets[0].Name;
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "Merged");
        doc.MergeCells(name, 0, 0, 1, 2);
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            // Verify the merged cell value survived
            Assert.Equal("Merged", FodsDocument.GetCellValue(reloaded.Sheets[0], 0, 0));
            // Verify the XML has the merge attribute by checking raw file
            var xml = File.ReadAllText(tmp);
            Assert.Contains("number-columns-spanned", xml);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void GetUsedRange_SurvivesSaveReload()
    {
        var doc = FodsDocument.Load(SamplePath);
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "RangeTest");
        var rangeBefore = doc.GetUsedRange();
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var rangeAfter = reloaded.GetUsedRange();
            Assert.NotNull(rangeBefore);
            Assert.NotNull(rangeAfter);
            Assert.Equal(rangeBefore.Value.MinRow, rangeAfter.Value.MinRow);
            Assert.Equal(rangeBefore.Value.MinCol, rangeAfter.Value.MinCol);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void InsertRow_SurvivesSaveReload()
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
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ClearSheet_SurvivesSaveReload()
    {
        var doc = FodsDocument.Load(SamplePath);
        var name = doc.Sheets[0].Name;
        doc.ClearSheet(name);
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var range = reloaded.GetUsedRange(reloaded.Sheets[0].Name);
            Assert.Null(range);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void MultipleEdits_SurviveSaveReload()
    {
        var doc = FodsDocument.Load(Path.Combine(SamplesDir, "multi-sheet-basic.fods"));
        var name = doc.Sheets[0].Name;
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "V1");
        doc.SetCellFormula(name, 0, 1, "=A1*2");
        doc.InsertRowWithValues(name, 1, new[] { "R2C1", "R2C2" });
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("V1", FodsDocument.GetCellValue(reloaded.Sheets[0], 0, 0));
            Assert.Equal("=A1*2", reloaded.GetCellFormula(reloaded.Sheets[0].Name, 0, 1));
            Assert.Equal("R2C1", FodsDocument.GetCellValue(reloaded.Sheets[0], 1, 0));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
