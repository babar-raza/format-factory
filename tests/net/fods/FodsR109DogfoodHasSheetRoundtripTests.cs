// R109 Lane G: FODS HasSheet + GetColumnCount dogfood roundtrip
// Tests multi-API pipeline combining HasSheet with other APIs

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR109DogfoodHasSheetRoundtripTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void HasSheet_Then_GetColumnCount_Pipeline()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        Assert.NotEmpty(names);
        Assert.True(doc.HasSheet(names[0]));
        int cols = doc.GetColumnCount(names[0]);
        Assert.True(cols >= 0);
    }

    [Fact]
    public void AddSheet_HasSheet_InsertRow_SaveReload()
    {
        var doc = FodsDocument.Load(MinimalPath);
        string name = "R109_Dogfood_" + Guid.NewGuid().ToString("N")[..8];
        doc.AddSheet(name);
        Assert.True(doc.HasSheet(name));
        doc.InsertRowWithValues(name, 0, new[] { "A", "B", "C" });
        Assert.Equal(3, doc.GetColumnCount(name));

        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.True(reloaded.HasSheet(name));
            Assert.Equal(3, reloaded.GetColumnCount(name));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void HasSheet_Guard_Before_Export()
    {
        var doc = FodsDocument.Load(MinimalPath);
        string name = doc.GetSheetNames()[0];
        if (doc.HasSheet(name))
        {
            string csv = doc.ExportSheetToCsv(name);
            Assert.NotNull(csv);
            Assert.True(csv.Length >= 0);
        }
    }

    [Fact]
    public void HasSheet_Full_Lifecycle()
    {
        var doc = FodsDocument.Load(MinimalPath);
        string name = "R109_Lifecycle_" + Guid.NewGuid().ToString("N")[..8];
        Assert.False(doc.HasSheet(name));
        doc.AddSheet(name);
        Assert.True(doc.HasSheet(name));
        doc.RemoveSheet(name);
        Assert.False(doc.HasSheet(name));
    }
}
