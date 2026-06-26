// Tests for FodsDocument.FilterRows, InsertRowWithValues, GetRowValues.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R199

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R199: Tests for FodsDocument.FilterRows, InsertRowWithValues, GetRowValues.
/// FilterRows(sheetName, colIndex, predicate): returns matching row indices.
/// InsertRowWithValues(sheetName, rowIndex, values): inserts a row with values.
/// GetRowValues(sheetName, rowIndex): returns all cell values for a row.
/// Covers: FilterRows non-null; FilterRows count correct for known predicate;
/// FilterRows empty for non-matching; FilterRows all rows match universal predicate;
/// InsertRowWithValues increases RowCount; InsertRowWithValues values retrievable;
/// InsertRowWithValues at index 0 prepends; GetRowValues count matches column count;
/// GetRowValues values correct; GetRowValues after SetCellValue reflects update;
/// InsertRowWithValues->GetRowValues pipeline; FilterRows after InsertRowWithValues;
/// dogfood CreateNew->SetCells->InsertRowWithValues->FilterRows->GetRowValues verify.
/// </summary>
public class FodsR199FilterRowsAndInsertRowTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "Alice"); doc.SetCellValue(0, 1, "Eng"); doc.SetCellValue(0, 2, "95");
        doc.SetCellValue(1, 0, "Bob"); doc.SetCellValue(1, 1, "Finance"); doc.SetCellValue(1, 2, "82");
        doc.SetCellValue(2, 0, "Carol"); doc.SetCellValue(2, 1, "Eng"); doc.SetCellValue(2, 2, "88");
        return doc;
    }

    private static string DefaultSheet(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // FilterRows
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_NonNull()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var rows = doc.FilterRows(sheet, 1, val => val == "Eng");
        Assert.NotNull(rows);
    }

    [Fact]
    public void FilterRows_ByDept_Eng_CountIsTwo()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var rows = doc.FilterRows(sheet, 1, val => val == "Eng");
        Assert.Equal(2, rows.Count);
    }

    [Fact]
    public void FilterRows_NonMatching_ReturnsEmpty()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var rows = doc.FilterRows(sheet, 1, val => val == "Marketing");
        Assert.Equal(0, rows.Count);
    }

    [Fact]
    public void FilterRows_UniversalPredicate_AllRows()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var rows = doc.FilterRows(sheet, 0, val => val != null);
        Assert.Equal(3, rows.Count);
    }

    [Fact]
    public void FilterRows_ByScore_HigherThan85_CountIsTwo()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var rows = doc.FilterRows(sheet, 2, val =>
            int.TryParse(val, out var n) && n > 85);
        Assert.Equal(2, rows.Count);
    }

    // -------------------------------------------------------------------------
    // InsertRowWithValues
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRowWithValues_IncreasesRowCount()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var before = doc.GetRowCount(sheet);
        doc.InsertRowWithValues(sheet, 3, new List<string> { "Dave", "HR", "76" });
        var after = doc.GetRowCount(sheet);
        Assert.Equal(before + 1, after);
    }

    [Fact]
    public void InsertRowWithValues_ValuesRetrievable()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.InsertRowWithValues(sheet, 3, new List<string> { "Eve", "Legal", "91" });
        var vals = doc.GetRowValues(sheet, 3);
        Assert.Contains("Eve", vals);
    }

    [Fact]
    public void InsertRowWithValues_AtIndex0_Prepends()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.InsertRowWithValues(sheet, 0, new List<string> { "Header", "Dept", "Score" });
        var vals = doc.GetRowValues(sheet, 0);
        Assert.Contains("Header", vals);
    }

    [Fact]
    public void InsertRowWithValues_MultipleRows_AllRetrievable()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.InsertRowWithValues(sheet, 0, new List<string> { "X", "Y" });
        doc.InsertRowWithValues(sheet, 1, new List<string> { "A", "B" });
        Assert.Equal(2, doc.GetRowCount(sheet));
    }

    // -------------------------------------------------------------------------
    // GetRowValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_CountMatchesColumnCount()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var vals = doc.GetRowValues(sheet, 0);
        Assert.Equal(doc.GetColumnCount(sheet), vals.Count);
    }

    [Fact]
    public void GetRowValues_ValuesCorrect_Row0()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var vals = doc.GetRowValues(sheet, 0);
        Assert.Contains("Alice", vals);
        Assert.Contains("Eng", vals);
        Assert.Contains("95", vals);
    }

    [Fact]
    public void GetRowValues_AfterSetCellValue_Reflects()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(1, 0, "Robert");
        var vals = doc.GetRowValues(sheet, 1);
        Assert.Contains("Robert", vals);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->SetCells->InsertRowWithValues->FilterRows->GetRowValues
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetInsertRowFilterGetRowValuesVerify_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.GetSheetNames()[0];

        // Set initial rows
        doc.SetCellValue(0, 0, "Alice"); doc.SetCellValue(0, 1, "Eng"); doc.SetCellValue(0, 2, "95");
        doc.SetCellValue(1, 0, "Bob"); doc.SetCellValue(1, 1, "Finance"); doc.SetCellValue(1, 2, "82");
        Assert.Equal(2, doc.GetRowCount(sheet));

        // InsertRowWithValues
        doc.InsertRowWithValues(sheet, 2, new List<string> { "Carol", "Eng", "88" });
        Assert.Equal(3, doc.GetRowCount(sheet));

        // GetRowValues for new row
        var newRow = doc.GetRowValues(sheet, 2);
        Assert.Contains("Carol", newRow);
        Assert.Contains("Eng", newRow);
        Assert.Contains("88", newRow);

        // FilterRows for Eng dept
        var engRows = doc.FilterRows(sheet, 1, val => val == "Eng");
        Assert.Equal(2, engRows.Count);

        // FilterRows for high score
        var highRows = doc.FilterRows(sheet, 2, val =>
            int.TryParse(val, out var n) && n > 85);
        Assert.Equal(2, highRows.Count);

        // GetRowValues for each
        foreach (var idx in highRows)
        {
            var vals = doc.GetRowValues(sheet, idx);
            Assert.True(vals.Count > 0);
        }
    }
}
