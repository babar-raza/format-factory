// R103 Train A: FODS .NET RenameSheet tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R103-GOVERNED-DOTNET-FODS-RENAMESHEET-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR103RenameSheetTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void RenameSheet_ChangesName()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var oldName = doc.GetSheetNames()[0];
        doc.RenameSheet(oldName, "Renamed");
        Assert.Contains("Renamed", doc.GetSheetNames());
        Assert.DoesNotContain(oldName, doc.GetSheetNames());
    }

    [Fact]
    public void RenameSheet_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<InvalidOperationException>(() => doc.RenameSheet("NoSuch", "New"));
    }

    [Fact]
    public void RenameSheet_DuplicateName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("Second");
        var first = doc.GetSheetNames()[0];
        Assert.Throws<InvalidOperationException>(() => doc.RenameSheet(first, "Second"));
    }

    [Fact]
    public void RenameSheet_EmptyOldName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.RenameSheet("", "New"));
    }

    [Fact]
    public void RenameSheet_EmptyNewName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentException>(() => doc.RenameSheet(name, "  "));
    }

    [Fact]
    public void RenameSheet_PersistsAfterSaveReload()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var oldName = doc.GetSheetNames()[0];
        doc.RenameSheet(oldName, "Persisted");
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Contains("Persisted", reloaded.GetSheetNames());
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void RenameSheet_SheetCountUnchanged()
    {
        var doc = FodsDocument.Load(MinimalPath);
        int before = doc.SheetCount;
        doc.RenameSheet(doc.GetSheetNames()[0], "NewName");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void RenameSheet_GetSheetByName_FindsNew()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.RenameSheet(doc.GetSheetNames()[0], "Found");
        Assert.NotNull(doc.GetSheetByName("Found"));
    }
}
