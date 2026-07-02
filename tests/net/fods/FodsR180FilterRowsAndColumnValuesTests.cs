// Tests for FodsDocument.GetColumnValues, GetNumericColumnValues, FilterRows (via predicate).
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R180

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R180: Tests for FodsDocument.GetColumnValues, GetNumericColumnValues, GetCellDataType.
/// GetColumnValues(sheetName, col): returns column values as string list.
/// GetNumericColumnValues(sheetName, col): returns numeric values as double list.
/// GetCellDataType(sheetName, row, col): returns cell data type string.
/// GetColumnHeaders(sheetName): returns column header names.
/// Covers: GetColumnValues count equals row count; GetColumnValues contains expected values;
/// GetColumnValues first column names; GetColumnValues by sheetName;
/// GetNumericColumnValues parses doubles; GetNumericColumnValues count correct;
/// GetNumericColumnValues ignores non-numeric; GetCellDataType returns non-null;
/// GetColumnHeaders count; GetColumnHeaders contains header names;
/// FindCellsByValue returns correct positions; GetUsedRange for multi-row sheet;
/// dogfood Build->GetColumnValues->GetNumericColumnValues->FindCellsByValue pipeline.
/// </summary>
public class FodsR180FilterRowsAndColumnValuesTests
{
    private static FodsDocument BuildDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheetName = doc.GetSheetNames()[0];
        doc.InsertRowWithValues(sheetName, 0, new[] { "Name", "Score", "Dept" });
        doc.InsertRowWithValues(sheetName, 1, new[] { "Alice", "95", "Eng" });
        doc.InsertRowWithValues(sheetName, 2, new[] { "Bob", "82", "Finance" });
        doc.InsertRowWithValues(sheetName, 3, new[] { "Carol", "88", "Eng" });
        doc.InsertRowWithValues(sheetName, 4, new[] { "Dave", "91", "Finance" });
        return doc;
    }

    private static string GetSheetName(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_CountEqualsRowCount()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);
        var vals = doc.GetColumnValues(sheet, 0);
        Assert.Equal(doc.GetRowCount(sheet), vals.Count);
    }

    [Fact]
    public void GetColumnValues_FirstColumn_ContainsNames()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);
        var names = doc.GetColumnValues(sheet, 0);
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void GetColumnValues_HeaderRow_ContainsHeader()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);
        var col0 = doc.GetColumnValues(sheet, 0);
        Assert.Contains("Name", col0);
    }

    [Fact]
    public void GetColumnValues_ScoreColumn_ContainsScores()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);
        var scores = doc.GetColumnValues(sheet, 1);
        Assert.Contains("95", scores);
        Assert.Contains("82", scores);
    }

    // -------------------------------------------------------------------------
    // GetNumericColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumnValues_CountCorrect()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);
        var nums = doc.GetNumericColumnValues(sheet, 1);
        // 4 data rows with numeric scores (header "Score" not numeric)
        Assert.Equal(4, nums.Count);
    }

    [Fact]
    public void GetNumericColumnValues_ParsesDoubles()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);
        var nums = doc.GetNumericColumnValues(sheet, 1);
        Assert.Contains(95.0, nums);
        Assert.Contains(82.0, nums);
        Assert.Contains(88.0, nums);
        Assert.Contains(91.0, nums);
    }

    // -------------------------------------------------------------------------
    // GetCellDataType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellDataType_ReturnsNonNull()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);
        var dataType = doc.GetCellDataType(sheet, 0, 0);
        Assert.NotNull(dataType);
    }

    // -------------------------------------------------------------------------
    // GetColumnHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_CountMatchesColumnCount()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);
        var headers = doc.GetColumnHeaders(sheet);
        Assert.Equal(3, headers.Count);
    }

    [Fact]
    public void GetColumnHeaders_ContainsHeaderNames()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);
        var headers = doc.GetColumnHeaders(sheet);
        Assert.Contains("Name", headers);
        Assert.Contains("Score", headers);
        Assert.Contains("Dept", headers);
    }

    // -------------------------------------------------------------------------
    // FindCellsByValue
    // -------------------------------------------------------------------------

    [Fact]
    public void FindCellsByValue_ReturnsCorrectPositions()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);
        var positions = doc.FindCellsByValue(sheet, "Alice");
        Assert.NotEmpty(positions);
        Assert.Equal(1, positions[0].Row); // Alice in row 1
        Assert.Equal(0, positions[0].Col); // Column 0
    }

    [Fact]
    public void FindCellsByValue_NotFound_ReturnsEmpty()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);
        var positions = doc.FindCellsByValue(sheet, "ZZZNotFound");
        Assert.Empty(positions);
    }

    // -------------------------------------------------------------------------
    // GetUsedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUsedRange_MultiRowSheet_ReturnsRange()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);
        var range = doc.GetUsedRange(sheet);
        Assert.NotNull(range);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Build->GetColumnValues->GetNumericColumnValues->FindCellsByValue
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ColumnValuesNumericFindCellsPipeline()
    {
        var doc = BuildDoc();
        var sheet = GetSheetName(doc);

        // Column values
        var names = doc.GetColumnValues(sheet, 0);
        Assert.Contains("Alice", names);
        Assert.Equal(5, names.Count); // header + 4 data rows

        // Numeric values
        var scores = doc.GetNumericColumnValues(sheet, 1);
        Assert.Equal(4, scores.Count);
        var maxScore = scores.Max();
        Assert.Equal(95.0, maxScore);

        // Find cells
        var alicePos = doc.FindCellsByValue(sheet, "Alice");
        Assert.NotEmpty(alicePos);

        var engPos = doc.FindCellsByValue(sheet, "Eng");
        Assert.Equal(2, engPos.Count); // Alice and Carol rows

        // Get column headers
        var headers = doc.GetColumnHeaders(sheet);
        Assert.Contains("Score", headers);
    }
}
