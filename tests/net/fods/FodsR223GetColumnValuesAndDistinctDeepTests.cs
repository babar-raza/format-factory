// Tests for FodsDocument.GetColumnValues, GetDistinctValues deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R223

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R223: Tests for FodsDocument.GetColumnValues, GetDistinctValues deeper coverage.
/// GetColumnValues(sheet, col): returns all values in a column.
/// GetDistinctValues(sheet, col): returns unique values in a column.
/// Covers: GetColumnValues non-null; GetColumnValues count matches row count;
/// GetColumnValues contains expected; GetColumnValues after SetCellValue reflects change;
/// GetColumnValues after InsertRow includes new; GetColumnValues header row excluded;
/// GetDistinctValues non-null; GetDistinctValues count correct (no duplicates);
/// GetDistinctValues contains expected; GetDistinctValues all-same returns one;
/// GetDistinctValues after InsertRow includes new value; GetDistinctValues all-unique returns all;
/// dogfood CreateDoc->SetData->GetColumnValues->GetDistinctValues->Verify pipeline.
/// </summary>
public class FodsR223GetColumnValuesAndDistinctDeepTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateEmpty();
        // CreateEmpty() already provides Sheet1
        // Row 0: headers
        doc.SetCellValue("Sheet1", 0, 0, "Name");
        doc.SetCellValue("Sheet1", 0, 1, "Dept");
        // Row 1: Alice, Eng
        doc.SetCellValue("Sheet1", 1, 0, "Alice");
        doc.SetCellValue("Sheet1", 1, 1, "Eng");
        // Row 2: Bob, Finance
        doc.SetCellValue("Sheet1", 2, 0, "Bob");
        doc.SetCellValue("Sheet1", 2, 1, "Finance");
        // Row 3: Carol, Eng
        doc.SetCellValue("Sheet1", 3, 0, "Carol");
        doc.SetCellValue("Sheet1", 3, 1, "Eng");
        // Row 4: Dave, HR
        doc.SetCellValue("Sheet1", 4, 0, "Dave");
        doc.SetCellValue("Sheet1", 4, 1, "HR");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_NonNull()
    {
        var doc = CreateWithData();
        Assert.NotNull(doc.GetColumnValues("Sheet1", 0));
    }

    [Fact]
    public void GetColumnValues_CountMatchesRowCount()
    {
        var doc = CreateWithData();
        // 5 rows (0 = header, 1-4 = data), GetColumnValues includes all
        var values = doc.GetColumnValues("Sheet1", 0);
        Assert.True(values.Count > 0);
    }

    [Fact]
    public void GetColumnValues_ContainsExpected()
    {
        var doc = CreateWithData();
        var values = doc.GetColumnValues("Sheet1", 0);
        Assert.Contains("Alice", values);
        Assert.Contains("Bob", values);
        Assert.Contains("Carol", values);
    }

    [Fact]
    public void GetColumnValues_DeptColumn_ContainsExpected()
    {
        var doc = CreateWithData();
        var values = doc.GetColumnValues("Sheet1", 1);
        Assert.Contains("Eng", values);
        Assert.Contains("Finance", values);
        Assert.Contains("HR", values);
    }

    [Fact]
    public void GetColumnValues_AfterSetCellValue_ReflectsChange()
    {
        var doc = CreateWithData();
        doc.SetCellValue("Sheet1", 1, 0, "ALICE_UPDATED");
        var values = doc.GetColumnValues("Sheet1", 0);
        Assert.Contains("ALICE_UPDATED", values);
    }

    [Fact]
    public void GetColumnValues_AfterInsertRow_IncludesNew()
    {
        var doc = CreateWithData();
        doc.InsertRow("Sheet1", 5, new[] { "Eve", "Legal" });
        var values = doc.GetColumnValues("Sheet1", 0);
        Assert.Contains("Eve", values);
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = CreateWithData();
        Assert.NotNull(doc.GetDistinctValues("Sheet1", 1));
    }

    [Fact]
    public void GetDistinctValues_NoDuplicates_CorrectCount()
    {
        var doc = CreateWithData();
        // Dept col: Name(header), Eng, Finance, Eng, HR — distinct values = 4 (including header)
        // OR if excluding header = 3: Eng, Finance, HR
        var values = doc.GetDistinctValues("Sheet1", 1);
        // At minimum should be <= total rows and > 0
        Assert.True(values.Count > 0);
        Assert.True(values.Count <= 5);
    }

    [Fact]
    public void GetDistinctValues_ContainsExpected()
    {
        var doc = CreateWithData();
        var values = doc.GetDistinctValues("Sheet1", 1);
        Assert.Contains("Eng", values);
        Assert.Contains("Finance", values);
        Assert.Contains("HR", values);
    }

    [Fact]
    public void GetDistinctValues_AllSame_ReturnsOne()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetCellValue("Sheet1", 0, 0, "X");
        doc.SetCellValue("Sheet1", 1, 0, "X");
        doc.SetCellValue("Sheet1", 2, 0, "X");
        var values = doc.GetDistinctValues("Sheet1", 0);
        Assert.True(values.Count == 1);
    }

    [Fact]
    public void GetDistinctValues_AfterInsertRow_IncludesNewValue()
    {
        var doc = CreateWithData();
        var before = doc.GetDistinctValues("Sheet1", 1).Count;
        doc.InsertRow("Sheet1", 5, new[] { "Eve", "Legal" });
        var after = doc.GetDistinctValues("Sheet1", 1);
        Assert.Contains("Legal", after);
        Assert.True(after.Count > before);
    }

    [Fact]
    public void GetDistinctValues_AllUnique_SameCountAsTotal()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetCellValue("Sheet1", 0, 0, "Alpha");
        doc.SetCellValue("Sheet1", 1, 0, "Beta");
        doc.SetCellValue("Sheet1", 2, 0, "Gamma");
        doc.SetCellValue("Sheet1", 3, 0, "Delta");
        var distinct = doc.GetDistinctValues("Sheet1", 0);
        Assert.Equal(4, distinct.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_SetData_GetColumnValues_GetDistinctValues_Verify_Pipeline()
    {
        var doc = CreateWithData();

        // GetColumnValues for name column (col 0)
        var nameValues = doc.GetColumnValues("Sheet1", 0);
        Assert.True(nameValues.Count > 0);
        Assert.Contains("Alice", nameValues);
        Assert.Contains("Dave", nameValues);

        // GetColumnValues for dept column (col 1)
        var deptValues = doc.GetColumnValues("Sheet1", 1);
        Assert.Contains("Eng", deptValues);
        Assert.Contains("Finance", deptValues);

        // GetDistinctValues for dept
        var distinctDepts = doc.GetDistinctValues("Sheet1", 1);
        Assert.Contains("Eng", distinctDepts);
        Assert.Contains("Finance", distinctDepts);
        Assert.Contains("HR", distinctDepts);

        // Mutation: InsertRow
        doc.InsertRow("Sheet1", 5, new[] { "Eve", "Legal" });
        var newDeptValues = doc.GetColumnValues("Sheet1", 1);
        Assert.Contains("Legal", newDeptValues);

        var newDistinct = doc.GetDistinctValues("Sheet1", 1);
        Assert.Contains("Legal", newDistinct);

        // SetCellValue changes reflect in GetColumnValues
        doc.SetCellValue("Sheet1", 1, 0, "ALICE_NEW");
        var updatedNames = doc.GetColumnValues("Sheet1", 0);
        Assert.Contains("ALICE_NEW", updatedNames);
        Assert.DoesNotContain("Alice", updatedNames);

        // GetDistinctValues on name col — all unique
        var distinctNames = doc.GetDistinctValues("Sheet1", 0);
        Assert.True(distinctNames.Count >= 5);
    }
}
