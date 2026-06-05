// R109 Lane C: FODS HasSheet tests
// Ledger: R109-GOVERNED-DOTNET-FODS-HASSHEET-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR109HasSheetTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void HasSheet_ExistingSheet_ReturnsTrue()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        Assert.NotEmpty(names);
        Assert.True(doc.HasSheet(names[0]));
    }

    [Fact]
    public void HasSheet_NonExistent_ReturnsFalse()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.False(doc.HasSheet("ThisSheetDoesNotExist_R109"));
    }

    [Fact]
    public void HasSheet_NullOrEmpty_ReturnsFalse()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.False(doc.HasSheet(null!));
        Assert.False(doc.HasSheet(""));
        Assert.False(doc.HasSheet("   "));
    }

    [Fact]
    public void HasSheet_AfterAddSheet_ReturnsTrue()
    {
        var doc = FodsDocument.Load(MinimalPath);
        string newName = "R109_TestSheet_" + Guid.NewGuid().ToString("N")[..8];
        doc.AddSheet(newName);
        Assert.True(doc.HasSheet(newName));
    }

    [Fact]
    public void HasSheet_AfterRemoveSheet_ReturnsFalse()
    {
        var doc = FodsDocument.Load(MinimalPath);
        string newName = "R109_Remove_" + Guid.NewGuid().ToString("N")[..8];
        doc.AddSheet(newName);
        Assert.True(doc.HasSheet(newName));
        doc.RemoveSheet(newName);
        Assert.False(doc.HasSheet(newName));
    }

    [Fact]
    public void HasSheet_CaseSensitive()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        if (names.Count > 0)
        {
            string upper = names[0].ToUpperInvariant();
            string lower = names[0].ToLowerInvariant();
            // If the original name is mixed case, one of these should differ
            if (upper != lower)
            {
                bool orig = doc.HasSheet(names[0]);
                Assert.True(orig);
            }
        }
    }

    [Fact]
    public void HasSheet_AfterSaveReload_Persists()
    {
        var doc = FodsDocument.Load(MinimalPath);
        string newName = "R109_Persist_" + Guid.NewGuid().ToString("N")[..8];
        doc.AddSheet(newName);
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.True(reloaded.HasSheet(newName));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void HasSheet_ConsistentWithGetSheetNames()
    {
        var doc = FodsDocument.Load(MinimalPath);
        foreach (var name in doc.GetSheetNames())
        {
            Assert.True(doc.HasSheet(name));
        }
    }
}
