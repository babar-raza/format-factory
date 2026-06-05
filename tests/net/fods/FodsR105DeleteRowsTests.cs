// R105 Wave 2: FODS .NET DeleteRows tests
// Governed skill: /add-dotnet-api
// Ledger: R105-GOVERNED-DOTNET-FODS-DELETEROWS-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR105DeleteRowsTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void DeleteRows_RemovesSpecifiedRows()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        if (before < 2) return; // need at least 2 rows
        doc.DeleteRows(sheet, 0, 1);
        Assert.Equal(before - 1, doc.GetRowCount(sheet));
    }

    [Fact]
    public void DeleteRows_ZeroCount_NoOp()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        doc.DeleteRows(sheet, 0, 0);
        Assert.Equal(before, doc.GetRowCount(sheet));
    }

    [Fact]
    public void DeleteRows_SheetNotFound_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<InvalidOperationException>(() => doc.DeleteRows("NoSuch", 0, 1));
    }

    [Fact]
    public void DeleteRows_NegativeCount_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.DeleteRows(sheet, 0, -1));
    }

    [Fact]
    public void DeleteRows_OutOfRange_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int count = doc.GetRowCount(sheet);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.DeleteRows(sheet, 0, count + 1));
    }

    [Fact]
    public void DeleteRows_EmptySheetName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.DeleteRows("", 0, 1));
    }

    [Fact]
    public void DeleteRows_PersistsAfterSaveReload()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        if (before < 1) return;
        doc.DeleteRows(sheet, 0, 1);
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal(before - 1, reloaded.GetRowCount(reloaded.GetSheetNames()[0]));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void DeleteRows_MultipleRows()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        if (before < 2) return;
        doc.DeleteRows(sheet, 0, 2);
        Assert.Equal(before - 2, doc.GetRowCount(sheet));
    }
}
