// Tests for FodsDocument.GetRowValues, GetRowCount, GetColumnCount, GetCellCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R177

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R177: Tests for FodsDocument.GetRowValues, GetRowCount, GetColumnCount, GetCellCount.
/// GetRowValues(row): returns values from the first active sheet.
/// GetRowValues(sheetName, row): returns values from named sheet.
/// GetRowCount(): total rows across all sheets.
/// GetRowCount(sheetName): row count for named sheet.
/// GetColumnCount(): column count for first sheet.
/// GetColumnCount(sheetName): column count for named sheet.
/// GetCellCount(): total non-empty cells.
/// Covers: GetRowValues count matches column count; GetRowValues first row = headers;
/// GetRowValues data row contains values; GetRowValues(sheetName) same as (row);
/// GetRowCount positive after rows added; GetRowCount(sheetName) positive;
/// GetColumnCount matches header count; GetColumnCount(sheetName) positive;
/// GetCellCount positive; GetCellCount(sheet overload) positive;
/// GetNumericColumnValues returns doubles; dogfood Build->GetRowValues->GetColumnCount pipeline.
/// </summary>
public class FodsR177GetRowValuesAndColumnCountTests
{
    private static FodsDocument BuildSheet(string sheetName, string[] headers, string[][] rows)
    {
        var doc = FodsDocument.CreateNew();
        var names = doc.GetSheetNames();
        if (names.Count > 0)
            doc.RenameSheet(names[0], sheetName);
        else
            doc.AddSheet(sheetName);

        doc.InsertRowWithValues(sheetName, 0, headers);
        for (var i = 0; i < rows.Length; i++)
            doc.InsertRowWithValues(sheetName, i + 1, rows[i]);

        return doc;
    }

    // -------------------------------------------------------------------------
    // GetRowValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_Row0_IsHeaders()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var row0 = doc.GetRowValues(0);
        Assert.Contains("Name", row0);
        Assert.Contains("Score", row0);
    }

    [Fact]
    public void GetRowValues_Row1_IsFirstDataRow()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var row1 = doc.GetRowValues(1);
        Assert.Contains("Alice", row1);
        Assert.Contains("95", row1);
    }

    [Fact]
    public void GetRowValues_BySheetName_MatchesByIndex()
    {
        var doc = BuildSheet("MySheet",
            new[] { "Col" },
            new[] { new[] { "Val" } });
        var byIndex = doc.GetRowValues(0);
        var byName = doc.GetRowValues("MySheet", 0);
        Assert.Equal(byIndex.Count, byName.Count);
        Assert.Equal(byIndex[0], byName[0]);
    }

    [Fact]
    public void GetRowValues_CountMatchesColumnCount()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A", "B", "C" },
            new[] { new[] { "1", "2", "3" } });
        var row = doc.GetRowValues(0);
        Assert.Equal(3, row.Count);
    }

    // -------------------------------------------------------------------------
    // GetRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_PositiveAfterRowsAdded()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name" },
            new[] { new[] { "Alice" }, new[] { "Bob" } });
        Assert.True(doc.GetRowCount() > 0);
    }

    [Fact]
    public void GetRowCount_BySheetName_IsPositive()
    {
        var doc = BuildSheet("Data",
            new[] { "Name" },
            new[] { new[] { "Alice" } });
        Assert.True(doc.GetRowCount("Data") > 0);
    }

    [Fact]
    public void GetRowCount_BySheetName_Matches3Rows()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name" },
            new[] { new[] { "Alice" }, new[] { "Bob" }, new[] { "Carol" } });
        // Header + 3 data rows = 4 total
        Assert.Equal(4, doc.GetRowCount("Sheet"));
    }

    // -------------------------------------------------------------------------
    // GetColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_MatchesHeaderCount()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A", "B", "C" },
            new[] { new[] { "1", "2", "3" } });
        Assert.Equal(3, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_BySheetName_Positive()
    {
        var doc = BuildSheet("Named",
            new[] { "X", "Y" },
            new[] { new[] { "1", "2" } });
        Assert.True(doc.GetColumnCount("Named") > 0);
    }

    [Fact]
    public void GetColumnCount_FiveColumns_IsFive()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A", "B", "C", "D", "E" },
            new[] { new[] { "1", "2", "3", "4", "5" } });
        Assert.Equal(5, doc.GetColumnCount());
    }

    // -------------------------------------------------------------------------
    // GetCellCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCount_PositiveAfterDataAdded()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" }, new[] { "Bob", "82" } });
        Assert.True(doc.GetCellCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetNumericColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumnValues_ReturnsDoubles()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" }, new[] { "Bob", "82" } });
        var scores = doc.GetNumericColumnValues("Sheet", 1);
        Assert.Equal(2, scores.Count);
        Assert.Contains(95.0, scores);
        Assert.Contains(82.0, scores);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Build->GetRowValues->GetColumnCount->GetCellCount pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRowValuesColumnCountPipeline()
    {
        var doc = BuildSheet("Sales",
            new[] { "Product", "Units", "Revenue" },
            new[] {
                new[] { "Widget", "100", "999" },
                new[] { "Gadget", "50", "1999" }
            });

        // Row values
        var headerRow = doc.GetRowValues(0);
        Assert.Equal(3, headerRow.Count);
        Assert.Contains("Product", headerRow);

        var dataRow1 = doc.GetRowValues(1);
        Assert.Contains("Widget", dataRow1);

        // Column count
        Assert.Equal(3, doc.GetColumnCount());
        Assert.Equal(3, doc.GetColumnCount("Sales"));

        // Row count
        Assert.Equal(3, doc.GetRowCount("Sales")); // header + 2 data rows

        // Cell count
        Assert.True(doc.GetCellCount() > 0);

        // Numeric column
        var units = doc.GetNumericColumnValues("Sales", 1);
        Assert.Contains(100.0, units);
        Assert.Contains(50.0, units);
    }
}
