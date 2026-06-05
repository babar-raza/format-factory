// R105 Wave 2: FODS .NET InsertRow tests
// Governed skill: /add-dotnet-api
// Ledger: R105-GOVERNED-DOTNET-FODS-INSERTROW-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR105InsertRowTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void InsertRow_IncreasesRowCount()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        doc.InsertRow(sheet, 0);
        Assert.Equal(before + 1, doc.GetRowCount(sheet));
    }

    [Fact]
    public void InsertRow_AtEnd()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        doc.InsertRow(sheet, before);
        Assert.Equal(before + 1, doc.GetRowCount(sheet));
    }

    [Fact]
    public void InsertRow_SheetNotFound_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<InvalidOperationException>(() => doc.InsertRow("NoSuch", 0));
    }

    [Fact]
    public void InsertRow_NegativeIndex_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertRow(sheet, -1));
    }

    [Fact]
    public void InsertRow_OutOfRange_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int count = doc.GetRowCount(sheet);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertRow(sheet, count + 1));
    }

    [Fact]
    public void InsertRow_EmptySheetName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.InsertRow("", 0));
    }

    [Fact]
    public void InsertRow_PersistsAfterSaveReload()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        doc.InsertRow(sheet, 0);
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal(before + 1, reloaded.GetRowCount(reloaded.GetSheetNames()[0]));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void InsertRow_MultipleInserts()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        doc.InsertRow(sheet, 0);
        doc.InsertRow(sheet, 0);
        doc.InsertRow(sheet, 0);
        Assert.Equal(before + 3, doc.GetRowCount(sheet));
    }
}
