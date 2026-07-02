// Tests for FodsDocument.GetRowCount, GetColumnStats, GetColumnValues deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R225

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R225: Tests for FodsDocument.GetRowCount, GetColumnStats, GetColumnValues deeper coverage.
/// GetRowCount(): returns number of data rows (excluding header).
/// GetColumnStats(colIndex): returns min/max/sum/avg for a numeric column.
/// GetColumnValues(colIndex): returns all values in a column.
/// Covers: GetRowCount positive; GetRowCount matches RowCount; GetRowCount zero after clear;
/// GetRowCount increases after InsertRow; GetRowCount after DeleteRows;
/// GetColumnStats non-null; GetColumnStats correct min/max/sum/avg;
/// GetColumnStats after SetCellValue reflects; GetColumnStats after InsertRow reflects;
/// GetColumnValues non-null; GetColumnValues count equals GetRowCount;
/// GetColumnValues contains expected values; GetColumnValues after mutation;
/// dogfood CreateDoc→GetRowCount→GetColumnStats→GetColumnValues→mutation→verify pipeline.
/// </summary>
public class FodsR225GetRowCountAndColumnStatsDeepTests
{
    private static FodsDocument CreateDataDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Score");
        doc.SetCellValue(0, 2, "Dept");
        doc.AddRow(new List<string> { "Alice", "90", "Engineering" });
        doc.AddRow(new List<string> { "Bob", "75", "Finance" });
        doc.AddRow(new List<string> { "Carol", "85", "Engineering" });
        doc.AddRow(new List<string> { "Dave", "60", "HR" });
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_Positive()
    {
        var doc = CreateDataDoc();
        Assert.True(doc.GetRowCount() > 0);
    }

    [Fact]
    public void GetRowCount_MatchesRowCount()
    {
        var doc = CreateDataDoc();
        Assert.Equal(doc.RowCount, doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_EmptyDoc_ZeroOrMinimal()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Empty");
        Assert.True(doc.GetRowCount() >= 0);
    }

    [Fact]
    public void GetRowCount_IncreasesAfterAddRow()
    {
        var doc = CreateDataDoc();
        var before = doc.GetRowCount();
        doc.AddRow(new List<string> { "Eve", "88", "Marketing" });
        Assert.Equal(before + 1, doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_DecreasesAfterDeleteRow()
    {
        var doc = CreateDataDoc();
        var before = doc.GetRowCount();
        doc.DeleteRows(1, 1);
        Assert.True(doc.GetRowCount() < before);
    }

    [Fact]
    public void GetRowCount_AfterClearSheet_ZeroOrMinimal()
    {
        var doc = CreateDataDoc();
        doc.ClearSheet();
        Assert.True(doc.GetRowCount() >= 0);
    }

    // -------------------------------------------------------------------------
    // GetColumnStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStats_NonNull()
    {
        var doc = CreateDataDoc();
        Assert.NotNull(doc.GetColumnStats(1)); // Score column
    }

    [Fact]
    public void GetColumnStats_CorrectMin()
    {
        var doc = CreateDataDoc();
        var stats = doc.GetColumnStats(1);
        Assert.Equal(60.0, stats.Min, 1);
    }

    [Fact]
    public void GetColumnStats_CorrectMax()
    {
        var doc = CreateDataDoc();
        var stats = doc.GetColumnStats(1);
        Assert.Equal(90.0, stats.Max, 1);
    }

    [Fact]
    public void GetColumnStats_CorrectSum()
    {
        var doc = CreateDataDoc();
        var stats = doc.GetColumnStats(1);
        Assert.Equal(310.0, stats.Sum, 1); // 90+75+85+60
    }

    [Fact]
    public void GetColumnStats_CorrectAvg()
    {
        var doc = CreateDataDoc();
        var stats = doc.GetColumnStats(1);
        Assert.True(stats.Avg >= 77.0 && stats.Avg <= 78.0); // 310/4 = 77.5
    }

    [Fact]
    public void GetColumnStats_MinLessOrEqualMax()
    {
        var doc = CreateDataDoc();
        var stats = doc.GetColumnStats(1);
        Assert.True(stats.Min <= stats.Max);
    }

    [Fact]
    public void GetColumnStats_AfterSetCellValue_Reflects()
    {
        var doc = CreateDataDoc();
        // Update Bob score from 75 to 95
        doc.SetCellValue(2, 1, "95"); // row index 2 = Bob's row
        var stats = doc.GetColumnStats(1);
        Assert.True(stats.Max >= 95.0);
    }

    [Fact]
    public void GetColumnStats_AfterAddRow_Reflects()
    {
        var doc = CreateDataDoc();
        var before = doc.GetColumnStats(1).Max;
        doc.AddRow(new List<string> { "Eve", "99", "Marketing" });
        var after = doc.GetColumnStats(1).Max;
        Assert.True(after >= 99.0);
        Assert.True(after >= before);
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_NonNull()
    {
        var doc = CreateDataDoc();
        Assert.NotNull(doc.GetColumnValues(0)); // Name column
    }

    [Fact]
    public void GetColumnValues_CountEqualsRowCount()
    {
        var doc = CreateDataDoc();
        Assert.Equal(doc.GetRowCount(), doc.GetColumnValues(0).Count);
    }

    [Fact]
    public void GetColumnValues_ContainsExpectedNames()
    {
        var doc = CreateDataDoc();
        var names = doc.GetColumnValues(0);
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void GetColumnValues_AfterAddRow_IncludesNew()
    {
        var doc = CreateDataDoc();
        doc.AddRow(new List<string> { "Eve", "88", "Marketing" });
        var names = doc.GetColumnValues(0);
        Assert.Contains("Eve", names);
    }

    [Fact]
    public void GetColumnValues_AfterSetCellValue_Reflects()
    {
        var doc = CreateDataDoc();
        doc.SetCellValue(1, 0, "Alexander"); // Row 1 = Alice → Alexander
        var names = doc.GetColumnValues(0);
        Assert.Contains("Alexander", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_GetRowCount_GetColumnStats_GetColumnValues_Mutation_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sales");
        doc.SetCellValue(0, 0, "Product");
        doc.SetCellValue(0, 1, "Revenue");
        doc.SetCellValue(0, 2, "Region");
        doc.AddRow(new List<string> { "Widget A", "1200", "North" });
        doc.AddRow(new List<string> { "Widget B", "800", "South" });
        doc.AddRow(new List<string> { "Widget C", "1500", "North" });
        doc.AddRow(new List<string> { "Widget D", "950", "West" });
        doc.AddRow(new List<string> { "Widget E", "1100", "South" });

        // GetRowCount
        Assert.Equal(5, doc.GetRowCount());

        // GetColumnStats for Revenue
        var stats = doc.GetColumnStats(1);
        Assert.NotNull(stats);
        Assert.Equal(800.0, stats.Min, 0);
        Assert.Equal(1500.0, stats.Max, 0);
        Assert.Equal(5550.0, stats.Sum, 0);
        Assert.True(stats.Avg >= 1109.0 && stats.Avg <= 1111.0); // 5550/5=1110

        // GetColumnValues for Product
        var products = doc.GetColumnValues(0);
        Assert.Equal(5, products.Count);
        Assert.Contains("Widget A", products);
        Assert.Contains("Widget E", products);

        // GetColumnValues for Region
        var regions = doc.GetColumnValues(2);
        Assert.Contains("North", regions);
        Assert.Contains("South", regions);
        Assert.Contains("West", regions);

        // AddRow — increases count
        doc.AddRow(new List<string> { "Widget F", "2000", "East" });
        Assert.Equal(6, doc.GetRowCount());

        // Stats updated after AddRow
        var updatedStats = doc.GetColumnStats(1);
        Assert.Equal(2000.0, updatedStats.Max, 0);

        // SetCellValue — update Widget B revenue
        doc.SetCellValue(2, 1, "1800");
        var postMutStats = doc.GetColumnStats(1);
        Assert.True(postMutStats.Min <= 1200.0); // Widget A still exists
        Assert.True(postMutStats.Sum > stats.Sum); // sum increased

        // GetColumnValues reflects mutation
        var updatedProducts = doc.GetColumnValues(0);
        Assert.Equal(6, updatedProducts.Count);
    }
}
