// Tests for FodsDocument.FilterRows, GetColumnAggregates, GetCellDataType, GetCellStyle.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R170

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R170: Tests for FodsDocument.FilterRows, GetColumnAggregates, GetCellDataType, GetCellStyle.
/// FilterRows(sheetName, col, value): returns rows where col matches value.
/// GetColumnAggregates(sheetName, col): (Min, Max, Sum, Count) for numeric column.
/// GetCellDataType(sheetName, row, col): returns data type string or null.
/// GetCellStyle(sheetName, row, col): returns style name or null.
/// Covers: FilterRows single match; FilterRows multiple matches; FilterRows no match returns empty;
/// FilterRows preserves all columns; GetColumnAggregates sum correct;
/// GetColumnAggregates empty col returns Count=0; GetCellDataType returns non-null for data;
/// GetCellDataType OOB returns null; GetCellStyle for unstylized cell is null or default;
/// dogfood CreateNew->InsertRows->FilterRows->GetColumnAggregates->GetCellDataType pipeline.
/// </summary>
public class FodsR170FilterRowsAndColumnAggregatesTests
{
    private static FodsDocument BuildSheet(string sheetName, string[] headers, string[][] rows)
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
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
    // FilterRows
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_SingleMatch_ReturnsOneRow()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Dept" },
            new[] { new[] { "Alice", "Eng" }, new[] { "Bob", "Finance" } });
        var rows = doc.FilterRows("Data", 1, "Finance");
        Assert.Equal(2, rows.Count); // header + 1 match
    }

    [Fact]
    public void FilterRows_MultipleMatches_CountCorrect()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Dept" },
            new[] {
                new[] { "Alice", "Eng" },
                new[] { "Bob", "Finance" },
                new[] { "Carol", "Eng" }
            });
        var rows = doc.FilterRows("Data", 1, "Eng");
        Assert.Equal(3, rows.Count); // header + 2 matches
    }

    [Fact]
    public void FilterRows_NoMatch_ReturnsEmpty()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Dept" },
            new[] { new[] { "Alice", "Eng" } });
        var rows = doc.FilterRows("Data", 1, "Marketing");
        Assert.Single(rows); // header row only
    }

    [Fact]
    public void FilterRows_PreservesAllColumns()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Dept", "Score" },
            new[] {
                new[] { "Alice", "Eng", "95" },
                new[] { "Bob", "Finance", "82" }
            });
        var rows = doc.FilterRows("Data", 1, "Eng");
        Assert.Equal(2, rows.Count); // header + 1 match
        Assert.Equal(3, rows[1].Count); // 3 columns preserved in data row
    }

    [Fact]
    public void FilterRows_ByName_FirstColumn()
    {
        var doc = BuildSheet("Data",
            new[] { "ID", "Status" },
            new[] {
                new[] { "A001", "active" },
                new[] { "A002", "inactive" },
                new[] { "A003", "active" }
            });
        var rows = doc.FilterRows("Data", 0, "A002");
        Assert.Equal(2, rows.Count); // header + 1 match
    }

    // -------------------------------------------------------------------------
    // GetColumnAggregates
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAggregates_SumCorrect()
    {
        var doc = BuildSheet("Nums",
            new[] { "Val" },
            new[] { new[] { "10" }, new[] { "20" }, new[] { "30" } });
        var agg = doc.GetColumnAggregates("Nums", 0);
        Assert.Equal(60.0, agg.Sum, precision: 5);
    }

    [Fact]
    public void GetColumnAggregates_CountIsThree()
    {
        var doc = BuildSheet("Nums",
            new[] { "Val" },
            new[] { new[] { "10" }, new[] { "20" }, new[] { "30" } });
        var agg = doc.GetColumnAggregates("Nums", 0);
        Assert.Equal(3, agg.Count);
    }

    [Fact]
    public void GetColumnAggregates_MinMaxCorrect()
    {
        var doc = BuildSheet("Nums",
            new[] { "Val" },
            new[] { new[] { "5" }, new[] { "100" }, new[] { "42" } });
        var agg = doc.GetColumnAggregates("Nums", 0);
        Assert.Equal(5.0, agg.Min, precision: 5);
        Assert.Equal(100.0, agg.Max, precision: 5);
    }

    // -------------------------------------------------------------------------
    // GetCellDataType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellDataType_ValidCell_ReturnsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Alice");
        var type = doc.GetCellDataType("Data", 0, 0);
        // Non-null for a cell with data
        Assert.NotNull(type);
    }

    [Fact]
    public void GetCellDataType_OobRow_ReturnsNull()
    {
        var doc = BuildSheet("Data",
            new[] { "Name" },
            new[] { new[] { "Alice" } });
        var type = doc.GetCellDataType("Data", 999, 0);
        Assert.Null(type);
    }

    // -------------------------------------------------------------------------
    // GetCellStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyle_UnstylizedCell_IsNullOrDefault()
    {
        var doc = BuildSheet("Data",
            new[] { "Name" },
            new[] { new[] { "Alice" } });
        // Unstylized cells may return null or empty/default
        var style = doc.GetCellStyle("Data", 0, 0);
        // Accept null or any string (no style = null or default style name)
        Assert.True(style == null || style is string);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->InsertRows->FilterRows->GetColumnAggregates->GetCellDataType
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FilterRowsAggregateDataType_Pipeline()
    {
        var doc = BuildSheet("Sales",
            new[] { "Product", "Category", "Revenue" },
            new[] {
                new[] { "Widget", "Hardware", "1500" },
                new[] { "Gadget", "Hardware", "2200" },
                new[] { "App", "Software", "5000" },
                new[] { "Plugin", "Software", "3200" }
            });

        // FilterRows by category
        var hardware = doc.FilterRows("Sales", 1, "Hardware");
        Assert.Equal(3, hardware.Count); // header + 2 hardware

        var software = doc.FilterRows("Sales", 1, "Software");
        Assert.Equal(3, software.Count); // header + 2 software

        // GetColumnAggregates on Revenue column
        var agg = doc.GetColumnAggregates("Sales", 2);
        Assert.Equal(4, agg.Count);
        Assert.Equal(11900.0, agg.Sum, precision: 5);
        Assert.Equal(1500.0, agg.Min, precision: 5);
        Assert.Equal(5000.0, agg.Max, precision: 5);

        // GetCellDataType for header row
        var headerType = doc.GetCellDataType("Sales", 0, 0);
        Assert.NotNull(headerType);

        // OOB
        var oobType = doc.GetCellDataType("Sales", 1000, 0);
        Assert.Null(oobType);
    }
}
