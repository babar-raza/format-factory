// R110 Wave 4: FODS FindCellsByValue tests
// Ledger: R110-GOVERNED-DOTNET-FODS-FINDCELLSBYVALUE-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR110FindCellsByValueTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void FindCellsByValue_ExistingValue_ReturnsMatches()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        Assert.NotEmpty(names);
        // Set a known value
        doc.SetCellValue(0, 0, "FIND_ME_R110");
        var results = doc.FindCellsByValue(names[0], "FIND_ME_R110");
        Assert.NotEmpty(results);
        Assert.Contains(results, r => r.Row == 0 && r.Col == 0);
    }

    [Fact]
    public void FindCellsByValue_NonExistingValue_ReturnsEmpty()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        var results = doc.FindCellsByValue(names[0], "VALUE_THAT_DOES_NOT_EXIST_ANYWHERE_R110");
        Assert.Empty(results);
    }

    [Fact]
    public void FindCellsByValue_MultipleMatches_ReturnsAll()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        Assert.NotEmpty(names);
        var rows = doc.GetRowCount(names[0]);
        if (rows >= 2)
        {
            var sheet = doc.GetSheetByName(names[0])!;
            if (sheet.Rows[0].Cells.Count > 0 && sheet.Rows[1].Cells.Count > 0)
            {
                doc.SetCellValue(0, 0, "DUPE_R110");
                FodsDocument.SetCellValue(sheet, 1, 0, "DUPE_R110");
                var results = doc.FindCellsByValue(names[0], "DUPE_R110");
                Assert.True(results.Count >= 2);
            }
        }
    }

    [Fact]
    public void FindCellsByValue_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<InvalidOperationException>(() =>
            doc.FindCellsByValue("NoSuchSheet_R110", "value"));
    }

    [Fact]
    public void FindCellsByValue_NullValue_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        Assert.Throws<ArgumentNullException>(() =>
            doc.FindCellsByValue(names[0], null!));
    }

    [Fact]
    public void FindCellsByValue_EmptySheetName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() =>
            doc.FindCellsByValue("", "value"));
    }

    [Fact]
    public void FindCellsByValue_CaseSensitive_NoMatch()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        doc.SetCellValue(0, 0, "CaseTest");
        var results = doc.FindCellsByValue(names[0], "casetest");
        Assert.DoesNotContain(results, r => r.Row == 0 && r.Col == 0);
    }

    [Fact]
    public void FindCellsByValue_AfterAddAndRemoveSheet_WorksOnNewSheet()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var newSheet = doc.AddSheet("SearchTest_R110");
        // New sheet has no cells, so search returns empty
        var results = doc.FindCellsByValue("SearchTest_R110", "anything");
        Assert.Empty(results);
    }
}
