// R101 Train B: FODS .NET RemoveSheet deep product lane tests
// Governed skill: /add-dotnet-api
// Ledger: R101-GOVERNED-DOTNET-FODS-REMOVESHEET-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR101RemoveSheetTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void RemoveSheet_ReducesSheetCount()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("ToRemove");
        int before = doc.SheetCount;
        doc.RemoveSheet("ToRemove");
        Assert.Equal(before - 1, doc.SheetCount);
    }

    [Fact]
    public void RemoveSheet_SheetNoLongerInNames()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("Gone");
        doc.RemoveSheet("Gone");
        Assert.DoesNotContain("Gone", doc.GetSheetNames());
    }

    [Fact]
    public void RemoveSheet_GetSheetByName_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("Vanish");
        doc.RemoveSheet("Vanish");
        Assert.Null(doc.GetSheetByName("Vanish"));
    }

    [Fact]
    public void RemoveSheet_NonExistentName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<InvalidOperationException>(() => doc.RemoveSheet("NoSuchSheet"));
    }

    [Fact]
    public void RemoveSheet_EmptyName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.RemoveSheet(""));
        Assert.Throws<ArgumentException>(() => doc.RemoveSheet("  "));
    }

    [Fact]
    public void RemoveSheet_PersistsAfterSaveReload()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("Temp");
        doc.RemoveSheet("Temp");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.DoesNotContain("Temp", reloaded.GetSheetNames());
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void RemoveSheet_OtherSheetsPreserved()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var origNames = doc.GetSheetNames();
        doc.AddSheet("Extra");
        doc.RemoveSheet("Extra");
        var afterNames = doc.GetSheetNames();
        Assert.Equal(origNames.Count, afterNames.Count);
        foreach (var name in origNames)
            Assert.Contains(name, afterNames);
    }

    [Fact]
    public void RemoveSheet_AddThenRemove_Roundtrip()
    {
        var doc = FodsDocument.Load(MinimalPath);
        int original = doc.SheetCount;
        doc.AddSheet("Roundtrip");
        Assert.Equal(original + 1, doc.SheetCount);
        doc.RemoveSheet("Roundtrip");
        Assert.Equal(original, doc.SheetCount);
    }

    [Fact]
    public void RemoveSheet_CanRemoveOriginalSheet()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var firstName = doc.GetSheetNames()[0];
        doc.RemoveSheet(firstName);
        Assert.DoesNotContain(firstName, doc.GetSheetNames());
    }

    [Fact]
    public void RemoveSheet_RemoveAll_ThenAdd()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        foreach (var name in names)
            doc.RemoveSheet(name);
        Assert.Equal(0, doc.SheetCount);
        doc.AddSheet("Fresh");
        Assert.Equal(1, doc.SheetCount);
    }
}
