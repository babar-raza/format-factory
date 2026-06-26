// Tests for FodsDocument.FilterRows, GetSheetNames deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R207

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R207: Tests for FodsDocument.FilterRows, GetSheetNames deeper coverage.
/// FilterRows(sheet, predicate): returns list of row indices matching a predicate.
/// GetSheetNames(): returns list of sheet names in the document.
/// Covers: FilterRows non-null; FilterRows empty for non-matching;
/// FilterRows correct indices; FilterRows all rows; FilterRows none;
/// FilterRows by column value; FilterRows by numeric comparison;
/// GetSheetNames non-null; GetSheetNames count correct; GetSheetNames contains default sheet;
/// GetSheetNames after AddSheet includes new sheet; GetSheetNames after RenameSheet updated;
/// GetSheetNames after RemoveSheet excludes removed;
/// dogfood CreateEmpty->AddSheet->RenameSheet->FilterRows->GetSheetNames verify.
/// </summary>
public class FodsR207FilterRowsAndGetSheetNamesDeepTests
{
    private static FodsDocument CreateMultiRowDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetCellValue("Sheet1", 0, 0, "Alice");
        doc.SetCellValue("Sheet1", 0, 1, "Eng");
        doc.SetCellValue("Sheet1", 0, 2, "95");
        doc.SetCellValue("Sheet1", 1, 0, "Bob");
        doc.SetCellValue("Sheet1", 1, 1, "Finance");
        doc.SetCellValue("Sheet1", 1, 2, "82");
        doc.SetCellValue("Sheet1", 2, 0, "Carol");
        doc.SetCellValue("Sheet1", 2, 1, "Eng");
        doc.SetCellValue("Sheet1", 2, 2, "91");
        doc.SetCellValue("Sheet1", 3, 0, "Dave");
        doc.SetCellValue("Sheet1", 3, 1, "HR");
        doc.SetCellValue("Sheet1", 3, 2, "77");
        return doc;
    }

    // -------------------------------------------------------------------------
    // FilterRows
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_NonNull()
    {
        var doc = CreateMultiRowDoc();
        Assert.NotNull(doc.FilterRows("Sheet1", row => doc.GetCellValue("Sheet1", row, 1) == "Eng"));
    }

    [Fact]
    public void FilterRows_NonMatchingPredicate_ReturnsEmpty()
    {
        var doc = CreateMultiRowDoc();
        var result = doc.FilterRows("Sheet1", row => doc.GetCellValue("Sheet1", row, 1) == "Marketing");
        Assert.Empty(result);
    }

    [Fact]
    public void FilterRows_ByDept_Eng_CountIsTwo()
    {
        var doc = CreateMultiRowDoc();
        var result = doc.FilterRows("Sheet1", row => doc.GetCellValue("Sheet1", row, 1) == "Eng");
        Assert.Equal(2, result.Count);
    }

    [Fact]
    public void FilterRows_ByDept_Eng_IndicesCorrect()
    {
        var doc = CreateMultiRowDoc();
        var result = doc.FilterRows("Sheet1", row => doc.GetCellValue("Sheet1", row, 1) == "Eng");
        Assert.Contains(0, result); // Alice
        Assert.Contains(2, result); // Carol
    }

    [Fact]
    public void FilterRows_SingleMatch_ReturnsOne()
    {
        var doc = CreateMultiRowDoc();
        var result = doc.FilterRows("Sheet1", row => doc.GetCellValue("Sheet1", row, 0) == "Bob");
        Assert.Equal(1, result.Count);
    }

    [Fact]
    public void FilterRows_ByNumericScore_HighScorers()
    {
        var doc = CreateMultiRowDoc();
        var result = doc.FilterRows("Sheet1", row =>
        {
            var val = doc.GetCellValue("Sheet1", row, 2);
            return int.TryParse(val, out var s) && s >= 91;
        });
        Assert.Equal(2, result.Count); // Alice(95), Carol(91)
    }

    // -------------------------------------------------------------------------
    // GetSheetNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetNames_NonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        Assert.NotNull(doc.GetSheetNames());
    }

    [Fact]
    public void GetSheetNames_ContainsDefaultSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        var names = doc.GetSheetNames();
        Assert.True(names.Count >= 1);
    }

    [Fact]
    public void GetSheetNames_AfterAddSheet_IncludesNew()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Q1Data");
        var names = doc.GetSheetNames();
        Assert.Contains("Q1Data", names);
    }

    [Fact]
    public void GetSheetNames_AfterAddSheet_CountIncremented()
    {
        var doc = FodsDocument.CreateEmpty();
        var before = doc.GetSheetNames().Count;
        doc.AddSheet("NewSheet");
        Assert.Equal(before + 1, doc.GetSheetNames().Count);
    }

    [Fact]
    public void GetSheetNames_AfterRenameSheet_Updated()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("OldName");
        doc.RenameSheet("OldName", "NewName");
        var names = doc.GetSheetNames();
        Assert.Contains("NewName", names);
        Assert.DoesNotContain("OldName", names);
    }

    [Fact]
    public void GetSheetNames_AfterRemoveSheet_Excluded()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Temp");
        doc.RemoveSheet("Temp");
        var names = doc.GetSheetNames();
        Assert.DoesNotContain("Temp", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAddSheetRenameSheetFilterRowsGetSheetNamesVerify_Pipeline()
    {
        // Create with initial data
        var doc = CreateMultiRowDoc();

        // GetSheetNames initially
        var initialNames = doc.GetSheetNames();
        Assert.True(initialNames.Count >= 1);

        // FilterRows — Eng dept
        var engRows = doc.FilterRows("Sheet1", row => doc.GetCellValue("Sheet1", row, 1) == "Eng");
        Assert.Equal(2, engRows.Count);

        // AddSheet
        doc.AddSheet("Summary");
        var afterAddNames = doc.GetSheetNames();
        Assert.Contains("Summary", afterAddNames);

        // SetCellValue on new sheet
        doc.SetCellValue("Summary", 0, 0, "Eng Count");
        doc.SetCellValue("Summary", 0, 1, engRows.Count.ToString());

        // FilterRows on new sheet
        var summaryRows = doc.FilterRows("Summary", row =>
            doc.GetCellValue("Summary", row, 0) == "Eng Count");
        Assert.Equal(1, summaryRows.Count);

        // RenameSheet
        doc.RenameSheet("Summary", "Overview");
        var renamedNames = doc.GetSheetNames();
        Assert.Contains("Overview", renamedNames);
        Assert.DoesNotContain("Summary", renamedNames);

        // FilterRows on renamed sheet
        var overviewRows = doc.FilterRows("Overview", row =>
            doc.GetCellValue("Overview", row, 0) == "Eng Count");
        Assert.Equal(1, overviewRows.Count);

        // RemoveSheet
        doc.RemoveSheet("Overview");
        var finalNames = doc.GetSheetNames();
        Assert.DoesNotContain("Overview", finalNames);

        // Sheet1 still has data
        var sheet1Rows = doc.FilterRows("Sheet1", row =>
            doc.GetCellValue("Sheet1", row, 1) == "Finance");
        Assert.Equal(1, sheet1Rows.Count);
    }
}
