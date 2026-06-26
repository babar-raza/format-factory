// Tests for FodsDocument.FilterRows, GetRowValues deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R221

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R221: Tests for FodsDocument.FilterRows, GetRowValues deeper coverage.
/// FilterRows(sheet, predicate): returns row indices matching the predicate.
/// GetRowValues(sheet, rowIndex): returns all cell values in a given row.
/// Covers: FilterRows non-null; FilterRows returns matching indices;
/// FilterRows no match returns empty; FilterRows all match returns all;
/// FilterRows by numeric threshold; FilterRows chain (two filters);
/// GetRowValues non-null; GetRowValues correct count; GetRowValues contains expected;
/// GetRowValues first row (header); GetRowValues data row correct;
/// GetRowValues after SetCellValue reflects change;
/// dogfood CreateDoc->SetData->FilterRows->GetRowValues->Verify pipeline.
/// </summary>
public class FodsR221FilterRowsAndGetRowValuesDeepTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Employees");
        doc.SetCellValue("Employees", 0, 0, "Name");
        doc.SetCellValue("Employees", 0, 1, "Dept");
        doc.SetCellValue("Employees", 0, 2, "Score");
        doc.SetCellValue("Employees", 1, 0, "Alice");
        doc.SetCellValue("Employees", 1, 1, "Eng");
        doc.SetCellValue("Employees", 1, 2, "92");
        doc.SetCellValue("Employees", 2, 0, "Bob");
        doc.SetCellValue("Employees", 2, 1, "Finance");
        doc.SetCellValue("Employees", 2, 2, "85");
        doc.SetCellValue("Employees", 3, 0, "Carol");
        doc.SetCellValue("Employees", 3, 1, "Eng");
        doc.SetCellValue("Employees", 3, 2, "78");
        doc.SetCellValue("Employees", 4, 0, "Dave");
        doc.SetCellValue("Employees", 4, 1, "HR");
        doc.SetCellValue("Employees", 4, 2, "91");
        return doc;
    }

    // -------------------------------------------------------------------------
    // FilterRows
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_NonNull()
    {
        var doc = CreateWithData();
        Assert.NotNull(doc.FilterRows("Employees", row => row.Any()));
    }

    [Fact]
    public void FilterRows_ByDept_CorrectCount()
    {
        var doc = CreateWithData();
        var engRows = doc.FilterRows("Employees", row =>
            row.Count > 1 && row[1] == "Eng");
        // Alice (row 1) and Carol (row 3) = 2
        Assert.Equal(2, engRows.Count);
    }

    [Fact]
    public void FilterRows_NoMatch_ReturnsEmpty()
    {
        var doc = CreateWithData();
        var result = doc.FilterRows("Employees", row =>
            row.Count > 1 && row[1] == "Marketing");
        Assert.Empty(result);
    }

    [Fact]
    public void FilterRows_AllMatch_ReturnsAll()
    {
        var doc = CreateWithData();
        var all = doc.FilterRows("Employees", row => row.Count > 0);
        Assert.True(all.Count > 0);
    }

    [Fact]
    public void FilterRows_ByScore_HighScores()
    {
        var doc = CreateWithData();
        var highScore = doc.FilterRows("Employees", row =>
        {
            if (row.Count < 3) return false;
            return int.TryParse(row[2], out var s) && s >= 90;
        });
        // Alice=92 and Dave=91 = 2
        Assert.Equal(2, highScore.Count);
    }

    [Fact]
    public void FilterRows_ContainsCorrectIndices()
    {
        var doc = CreateWithData();
        var engRows = doc.FilterRows("Employees", row =>
            row.Count > 1 && row[1] == "Eng");
        // Row 1 = Alice (Eng), Row 3 = Carol (Eng)
        Assert.Contains(1, engRows);
        Assert.Contains(3, engRows);
        Assert.DoesNotContain(2, engRows); // Bob is Finance
    }

    // -------------------------------------------------------------------------
    // GetRowValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_NonNull()
    {
        var doc = CreateWithData();
        Assert.NotNull(doc.GetRowValues("Employees", 0));
    }

    [Fact]
    public void GetRowValues_CorrectCount()
    {
        var doc = CreateWithData();
        var values = doc.GetRowValues("Employees", 0);
        Assert.Equal(3, values.Count);
    }

    [Fact]
    public void GetRowValues_HeaderRow_ContainsHeaders()
    {
        var doc = CreateWithData();
        var values = doc.GetRowValues("Employees", 0);
        Assert.Contains("Name", values);
        Assert.Contains("Dept", values);
        Assert.Contains("Score", values);
    }

    [Fact]
    public void GetRowValues_DataRow1_ContainsAlice()
    {
        var doc = CreateWithData();
        var values = doc.GetRowValues("Employees", 1);
        Assert.Contains("Alice", values);
        Assert.Contains("Eng", values);
        Assert.Contains("92", values);
    }

    [Fact]
    public void GetRowValues_DataRow2_ContainsBob()
    {
        var doc = CreateWithData();
        var values = doc.GetRowValues("Employees", 2);
        Assert.Contains("Bob", values);
        Assert.Contains("Finance", values);
    }

    [Fact]
    public void GetRowValues_LastRow_ContainsDave()
    {
        var doc = CreateWithData();
        var values = doc.GetRowValues("Employees", 4);
        Assert.Contains("Dave", values);
        Assert.Contains("HR", values);
    }

    [Fact]
    public void GetRowValues_AfterSetCellValue_ReflectsChange()
    {
        var doc = CreateWithData();
        doc.SetCellValue("Employees", 1, 2, "100");
        var values = doc.GetRowValues("Employees", 1);
        Assert.Contains("100", values);
        Assert.DoesNotContain("92", values);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_SetData_FilterRows_GetRowValues_Verify_Pipeline()
    {
        var doc = CreateWithData();

        // GetRowValues for all rows
        for (var i = 0; i <= 4; i++)
        {
            var vals = doc.GetRowValues("Employees", i);
            Assert.NotNull(vals);
            Assert.Equal(3, vals.Count);
        }

        // FilterRows by Eng dept
        var engRows = doc.FilterRows("Employees", row =>
            row.Count > 1 && row[1] == "Eng");
        Assert.Equal(2, engRows.Count);

        // GetRowValues for each matched row
        foreach (var rowIdx in engRows)
        {
            var vals = doc.GetRowValues("Employees", rowIdx);
            Assert.Contains("Eng", vals);
        }

        // FilterRows by high score
        var highScoreRows = doc.FilterRows("Employees", row =>
        {
            if (row.Count < 3) return false;
            return int.TryParse(row[2], out var s) && s >= 90;
        });
        Assert.Equal(2, highScoreRows.Count);

        // Mutate one score and re-filter
        doc.SetCellValue("Employees", 3, 2, "95"); // Carol now 95
        var newHighScoreRows = doc.FilterRows("Employees", row =>
        {
            if (row.Count < 3) return false;
            return int.TryParse(row[2], out var s) && s >= 90;
        });
        Assert.Equal(3, newHighScoreRows.Count); // Alice=92, Carol=95, Dave=91

        // GetRowValues confirms the mutation
        var carolVals = doc.GetRowValues("Employees", 3);
        Assert.Contains("95", carolVals);
    }
}
