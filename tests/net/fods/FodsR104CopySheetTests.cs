// R104 Wave 1: FODS .NET CopySheet tests
// Governed skill: /add-dotnet-api
// Ledger: R104-GOVERNED-DOTNET-FODS-COPYSHEET-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR104CopySheetTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void CopySheet_CreatesNewSheet()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var source = doc.GetSheetNames()[0];
        int before = doc.SheetCount;
        doc.CopySheet(source, "Copy");
        Assert.Equal(before + 1, doc.SheetCount);
    }

    [Fact]
    public void CopySheet_CopiedSheetHasCorrectName()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var source = doc.GetSheetNames()[0];
        var copied = doc.CopySheet(source, "MyCopy");
        Assert.Equal("MyCopy", copied.Name);
    }

    [Fact]
    public void CopySheet_CopiedSheetPreservesRows()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var source = doc.GetSheetNames()[0];
        var original = doc.GetSheetByName(source)!;
        int origRowCount = original.Rows.Count;
        var copied = doc.CopySheet(source, "RowCopy");
        Assert.Equal(origRowCount, copied.Rows.Count);
    }

    [Fact]
    public void CopySheet_SourceNotFound_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<InvalidOperationException>(() => doc.CopySheet("NoSuch", "New"));
    }

    [Fact]
    public void CopySheet_DuplicateName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        Assert.Throws<InvalidOperationException>(() => doc.CopySheet(name, name));
    }

    [Fact]
    public void CopySheet_EmptySourceName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.CopySheet("", "New"));
    }

    [Fact]
    public void CopySheet_EmptyNewName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentException>(() => doc.CopySheet(name, ""));
    }

    [Fact]
    public void CopySheet_PersistsAfterSaveReload()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var source = doc.GetSheetNames()[0];
        doc.CopySheet(source, "Saved");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Contains("Saved", reloaded.GetSheetNames());
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void CopySheet_OriginalUnaffected()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var source = doc.GetSheetNames()[0];
        var origHtml = doc.ExportSheetToHtml(source);
        doc.CopySheet(source, "Clone");
        var afterHtml = doc.ExportSheetToHtml(source);
        Assert.Equal(origHtml, afterHtml);
    }

    [Fact]
    public void CopySheet_IndependentEdit()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var source = doc.GetSheetNames()[0];
        var copied = doc.CopySheet(source, "IndepEdit");
        // Editing the copy doesn't affect the original
        FodsDocument.SetCellValue(copied, 0, 0, "EDITED");
        var origSheet = doc.GetSheetByName(source)!;
        var origVal = FodsDocument.GetCellValue(origSheet, 0, 0);
        Assert.NotEqual("EDITED", origVal);
    }
}
