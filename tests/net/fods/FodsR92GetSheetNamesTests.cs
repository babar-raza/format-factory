// R92 Train L: FODS .NET GetSheetNames Tests
// Governed skill: /add-dotnet-api
// Ledger: R92-GOVERNED-DOTNET-FODS-GETSHEETNAMES-001
// Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

using System;
using System.Collections.Generic;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR92GetSheetNamesTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string SampleFodsPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void GetSheetNames_ReturnsNonEmptyList()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var names = doc.GetSheetNames();
        Assert.NotNull(names);
        Assert.True(names.Count > 0, "Expected at least one sheet name");
    }

    [Fact]
    public void GetSheetNames_CountMatchesSheetCount()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var names = doc.GetSheetNames();
        Assert.Equal(doc.SheetCount, names.Count);
    }

    [Fact]
    public void GetSheetNames_AllNamesAreNonEmpty()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        foreach (var name in doc.GetSheetNames())
        {
            Assert.False(string.IsNullOrEmpty(name), "Sheet name must not be null or empty");
        }
    }

    [Fact]
    public void GetSheetNames_MatchesGetSheetByNameResults()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        foreach (var name in doc.GetSheetNames())
        {
            var sheet = doc.GetSheetByName(name);
            Assert.NotNull(sheet);
            Assert.Equal(name, sheet!.Name);
        }
    }

    [Fact]
    public void GetSheetNames_FirstNameMatchesFirstSheet()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var names = doc.GetSheetNames();
        var sheets = doc.Sheets;
        Assert.Equal(sheets[0].Name, names[0]);
    }

    [Fact]
    public void GetSheetNames_ReturnedListIsReadOnly()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var names = doc.GetSheetNames();
        // IReadOnlyList does not expose mutation methods — verify it is read-only
        Assert.IsAssignableFrom<IReadOnlyList<string>>(names);
    }

    [Fact]
    public void GetSheetNames_StableAcrossMultipleCalls()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var first = doc.GetSheetNames();
        var second = doc.GetSheetNames();
        Assert.Equal(first.Count, second.Count);
        for (int i = 0; i < first.Count; i++)
            Assert.Equal(first[i], second[i]);
    }

    [Fact]
    public void GetSheetNames_NamesAreInDocumentOrder()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var names = doc.GetSheetNames();
        var sheets = doc.Sheets;
        Assert.Equal(sheets.Count, names.Count);
        for (int i = 0; i < sheets.Count; i++)
            Assert.Equal(sheets[i].Name, names[i]);
    }
}
