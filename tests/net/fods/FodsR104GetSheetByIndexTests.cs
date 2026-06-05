// R104 Wave 1: FODS .NET GetSheetByIndex tests
// Governed skill: /add-dotnet-api
// Ledger: R104-GOVERNED-DOTNET-FODS-GETSHEETBYINDEX-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR104GetSheetByIndexTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void GetSheetByIndex_Zero_ReturnsFirstSheet()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetByIndex(0);
        Assert.NotNull(sheet);
        Assert.Equal(doc.GetSheetNames()[0], sheet.Name);
    }

    [Fact]
    public void GetSheetByIndex_NegativeIndex_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Null(doc.GetSheetByIndex(-1));
    }

    [Fact]
    public void GetSheetByIndex_OutOfRange_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Null(doc.GetSheetByIndex(doc.SheetCount));
        Assert.Null(doc.GetSheetByIndex(999));
    }

    [Fact]
    public void GetSheetByIndex_MatchesGetSheetByName()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        for (int i = 0; i < names.Count; i++)
        {
            var byIndex = doc.GetSheetByIndex(i);
            var byName = doc.GetSheetByName(names[i]);
            Assert.NotNull(byIndex);
            Assert.Equal(byName!.Name, byIndex.Name);
        }
    }

    [Fact]
    public void GetSheetByIndex_AfterAdd_FindsNewSheet()
    {
        var doc = FodsDocument.Load(MinimalPath);
        int lastIdx = doc.SheetCount;
        doc.AddSheet("Indexed");
        var sheet = doc.GetSheetByIndex(lastIdx);
        Assert.NotNull(sheet);
        Assert.Equal("Indexed", sheet.Name);
    }

    [Fact]
    public void GetSheetByIndex_AfterRemove_UpdatesIndices()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("A");
        doc.AddSheet("B");
        int countBefore = doc.SheetCount;
        doc.RemoveSheet("A");
        Assert.Equal(countBefore - 1, doc.SheetCount);
        Assert.Null(doc.GetSheetByIndex(doc.SheetCount));
    }

    [Fact]
    public void GetSheetByIndex_AllIndicesValid()
    {
        var doc = FodsDocument.Load(MinimalPath);
        for (int i = 0; i < doc.SheetCount; i++)
            Assert.NotNull(doc.GetSheetByIndex(i));
    }

    [Fact]
    public void GetSheetByIndex_PersistsAfterSaveReload()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("Persist");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var last = reloaded.GetSheetByIndex(reloaded.SheetCount - 1);
            Assert.NotNull(last);
            Assert.Equal("Persist", last.Name);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
