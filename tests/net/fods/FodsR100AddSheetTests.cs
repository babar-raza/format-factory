// R100 Train B: FODS .NET AddSheet deep product lane tests
// Governed skill: /add-dotnet-api
// Ledger: R100-GOVERNED-DOTNET-FODS-ADDSHEET-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR100AddSheetTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void AddSheet_CreatesNewSheet()
    {
        var doc = FodsDocument.Load(MinimalPath);
        int before = doc.SheetCount;
        doc.AddSheet("NewSheet");
        Assert.Equal(before + 1, doc.SheetCount);
    }

    [Fact]
    public void AddSheet_NameAppearsInGetSheetNames()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("R100Test");
        var names = doc.GetSheetNames();
        Assert.Contains("R100Test", names);
    }

    [Fact]
    public void AddSheet_GetSheetByName_FindsIt()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("Lookup");
        var sheet = doc.GetSheetByName("Lookup");
        Assert.NotNull(sheet);
        Assert.Equal("Lookup", sheet.Name);
    }

    [Fact]
    public void AddSheet_DuplicateName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var existing = doc.GetSheetNames()[0];
        Assert.Throws<InvalidOperationException>(() => doc.AddSheet(existing));
    }

    [Fact]
    public void AddSheet_EmptyName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.AddSheet(""));
        Assert.Throws<ArgumentException>(() => doc.AddSheet("  "));
    }

    [Fact]
    public void AddSheet_PersistsAfterSaveReload()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("Persistent");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Contains("Persistent", reloaded.GetSheetNames());
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void AddSheet_NewSheetHasZeroRows()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.AddSheet("Empty");
        Assert.Empty(sheet.Rows);
    }

    [Fact]
    public void AddSheet_OriginalSheetsPreserved()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var origNames = doc.GetSheetNames();
        doc.AddSheet("Extra");
        var newNames = doc.GetSheetNames();
        foreach (var name in origNames)
            Assert.Contains(name, newNames);
    }

    [Fact]
    public void AddSheet_MultipleSheets_AllPersist()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.AddSheet("Gamma");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var names = reloaded.GetSheetNames();
            Assert.Contains("Alpha", names);
            Assert.Contains("Beta", names);
            Assert.Contains("Gamma", names);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void AddSheet_HtmlExport_FirstSheetUnaffected()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var htmlBefore = doc.ExportSheetToHtml();
        doc.AddSheet("ExtraSheet");
        var htmlAfter = doc.ExportSheetToHtml();
        Assert.Equal(htmlBefore, htmlAfter);
    }
}
