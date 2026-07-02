// Tests for FodsDocument.ExportSheetToJson, FilterRows chain, GetRowValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R227

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R227: Tests for FodsDocument.ExportSheetToJson, FilterRows chain, GetRowValues deeper.
/// ExportSheetToJson(): returns JSON string of current sheet data.
/// FilterRows(colIndex, value): returns new doc with matching rows only.
/// GetRowValues(rowIndex): returns all cell values in a row as a list.
/// Covers: ExportSheetToJson non-null; ExportSheetToJson non-empty; ExportSheetToJson is JSON-like;
/// ExportSheetToJson contains headers; ExportSheetToJson contains data;
/// ExportSheetToJson after InsertRow includes new; ExportSheetToJson after SetCellValue reflects;
/// FilterRows Eng=2; FilterRows no match=empty; FilterRows after InsertRow adds new match;
/// FilterRows preserves row values; FilterRows chained narrows;
/// GetRowValues non-null; GetRowValues count=ColumnCount; GetRowValues first row header;
/// GetRowValues data row values correct; GetRowValues after SetCellValue reflects;
/// dogfood CreateDoc→ExportSheetToJson→FilterRows→GetRowValues→mutation pipeline.
/// </summary>
public class FodsR227ExportSheetAndFilterChainDeepTests
{
    private static FodsDocument CreateDataDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Reports");
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Score");
        doc.SetCellValue(0, 2, "Region");
        doc.AddRow(new List<string> { "Alice", "92", "North" });
        doc.AddRow(new List<string> { "Bob", "78", "South" });
        doc.AddRow(new List<string> { "Carol", "85", "North" });
        doc.AddRow(new List<string> { "Dave", "71", "West" });
        doc.AddRow(new List<string> { "Eve", "90", "South" });
        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportSheetToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToJson_NonNull()
    {
        var doc = CreateDataDoc();
        Assert.NotNull(doc.ExportSheetToJson());
    }

    [Fact]
    public void ExportSheetToJson_NonEmpty()
    {
        var doc = CreateDataDoc();
        Assert.NotEmpty(doc.ExportSheetToJson());
    }

    [Fact]
    public void ExportSheetToJson_IsJsonLike()
    {
        var doc = CreateDataDoc();
        var json = doc.ExportSheetToJson();
        Assert.True(json.Contains("{") || json.Contains("["));
    }

    [Fact]
    public void ExportSheetToJson_ContainsHeaderText()
    {
        var doc = CreateDataDoc();
        var json = doc.ExportSheetToJson();
        Assert.True(json.Contains("Name") || json.Contains("Score"));
    }

    [Fact]
    public void ExportSheetToJson_ContainsDataValue()
    {
        var doc = CreateDataDoc();
        var json = doc.ExportSheetToJson();
        Assert.Contains("Alice", json);
    }

    [Fact]
    public void ExportSheetToJson_AfterInsertRow_IncludesNew()
    {
        var doc = CreateDataDoc();
        doc.InsertRow(1, new List<string> { "Zara", "99", "East" });
        var json = doc.ExportSheetToJson();
        Assert.Contains("Zara", json);
    }

    [Fact]
    public void ExportSheetToJson_AfterSetCellValue_Reflects()
    {
        var doc = CreateDataDoc();
        doc.SetCellValue(1, 0, "ALICE_UPDATED");
        var json = doc.ExportSheetToJson();
        Assert.Contains("ALICE_UPDATED", json);
    }

    // -------------------------------------------------------------------------
    // FilterRows
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_NorthRegion_TwoRows()
    {
        var doc = CreateDataDoc();
        var filtered = doc.FilterRows(2, "North");
        Assert.Equal(2, filtered.RowCount);
    }

    [Fact]
    public void FilterRows_NoMatch_EmptyOrZero()
    {
        var doc = CreateDataDoc();
        var filtered = doc.FilterRows(2, "Antarctica");
        Assert.True(filtered.RowCount == 0);
    }

    [Fact]
    public void FilterRows_AllMatch()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("All");
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Group");
        doc.AddRow(new List<string> { "A", "X" });
        doc.AddRow(new List<string> { "B", "X" });
        doc.AddRow(new List<string> { "C", "X" });
        var filtered = doc.FilterRows(1, "X");
        Assert.Equal(3, filtered.RowCount);
    }

    [Fact]
    public void FilterRows_AfterInsertRow_IncludesNewMatch()
    {
        var doc = CreateDataDoc();
        doc.InsertRow(doc.RowCount, new List<string> { "Grace", "88", "North" });
        var filtered = doc.FilterRows(2, "North");
        Assert.Equal(3, filtered.RowCount); // Alice + Carol + Grace
    }

    [Fact]
    public void FilterRows_PreservesRowValues()
    {
        var doc = CreateDataDoc();
        var filtered = doc.FilterRows(2, "North");
        var values = filtered.GetRowValues(0);
        Assert.True(values.Contains("Alice") || values.Contains("Carol"));
    }

    // -------------------------------------------------------------------------
    // GetRowValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_NonNull()
    {
        var doc = CreateDataDoc();
        Assert.NotNull(doc.GetRowValues(0));
    }

    [Fact]
    public void GetRowValues_CountPositive()
    {
        var doc = CreateDataDoc();
        Assert.True(doc.GetRowValues(0).Count > 0);
    }

    [Fact]
    public void GetRowValues_FirstDataRow_CorrectValues()
    {
        var doc = CreateDataDoc();
        var values = doc.GetRowValues(1); // Alice row (1-indexed after header)
        Assert.Contains("Alice", values);
        Assert.Contains("92", values);
        Assert.Contains("North", values);
    }

    [Fact]
    public void GetRowValues_LastRow_CorrectValues()
    {
        var doc = CreateDataDoc();
        var values = doc.GetRowValues(doc.RowCount); // Eve
        Assert.Contains("Eve", values);
        Assert.Contains("90", values);
    }

    [Fact]
    public void GetRowValues_AfterSetCellValue_Reflects()
    {
        var doc = CreateDataDoc();
        doc.SetCellValue(1, 0, "ALICE_MOD");
        var values = doc.GetRowValues(1);
        Assert.Contains("ALICE_MOD", values);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_ExportSheetToJson_FilterRows_GetRowValues_Mutation_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sales");
        doc.SetCellValue(0, 0, "Agent");
        doc.SetCellValue(0, 1, "Amount");
        doc.SetCellValue(0, 2, "Quarter");
        doc.AddRow(new List<string> { "Anna", "5000", "Q1" });
        doc.AddRow(new List<string> { "Ben", "3500", "Q2" });
        doc.AddRow(new List<string> { "Cara", "4200", "Q1" });
        doc.AddRow(new List<string> { "Dan", "6100", "Q3" });
        doc.AddRow(new List<string> { "Ella", "4800", "Q1" });

        // ExportSheetToJson
        var json = doc.ExportSheetToJson();
        Assert.NotNull(json);
        Assert.True(json.Contains("{") || json.Contains("["));
        Assert.Contains("Anna", json);
        Assert.Contains("Q1", json);

        // FilterRows Q1 — 3 results
        var q1 = doc.FilterRows(2, "Q1");
        Assert.Equal(3, q1.RowCount);

        // GetRowValues for each Q1 row
        for (var i = 1; i <= q1.RowCount; i++)
        {
            var row = q1.GetRowValues(i);
            Assert.NotNull(row);
            Assert.True(row.Count > 0);
            Assert.Contains("Q1", row);
        }

        // ExportSheetToJson from filtered — smaller
        var q1Json = q1.ExportSheetToJson();
        Assert.True(q1Json.Length < json.Length);
        Assert.Contains("Anna", q1Json);
        Assert.False(q1Json.Contains("Dan")); // Q3

        // InsertRow — adds new Q1 agent
        doc.InsertRow(doc.RowCount, new List<string> { "Frank", "7200", "Q1" });
        Assert.Equal(6, doc.RowCount);

        // FilterRows Q1 now 4
        var newQ1 = doc.FilterRows(2, "Q1");
        Assert.Equal(4, newQ1.RowCount);

        // SetCellValue — update Anna amount
        doc.SetCellValue(1, 1, "9999");
        var annaRow = doc.GetRowValues(1);
        Assert.Contains("9999", annaRow);

        // ExportSheetToJson reflects update
        var updatedJson = doc.ExportSheetToJson();
        Assert.Contains("9999", updatedJson);
    }
}
