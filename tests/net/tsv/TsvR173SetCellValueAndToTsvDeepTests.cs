// Tests for TsvDocument.SetCellValue, ToTsv round-trip deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R173

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R173: Tests for TsvDocument.SetCellValue, ToTsv round-trip deeper coverage.
/// SetCellValue(row, col, value): sets the cell at (row, col) to value.
/// SetCellValue(row, colName, value): sets the cell in named column at given row.
/// ToTsv(): serializes the document back to TSV string.
/// Covers: SetCellValue by index changes value; SetCellValue by colName changes value;
/// SetCellValue does not change RowCount; SetCellValue does not change ColumnCount;
/// SetCellValue multiple times same cell; SetCellValue all cells in a row;
/// ToTsv non-null; ToTsv contains headers; ToTsv contains row data;
/// ToTsv has tabs; ToTsv->Load round-trip count correct; ToTsv->Load values correct;
/// ToTsv after mutation reflects change;
/// dogfood Load->SetCellValue->ToTsv->Load->verify->Filter->ToTsv->Load pipeline.
/// </summary>
public class TsvR173SetCellValueAndToTsvDeepTests
{
    private const string ThreeRowTsv =
        "name\tdept\tscore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88";

    // -------------------------------------------------------------------------
    // SetCellValue by index
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_ByIndex_ChangesValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, 0, "Alicia");
        Assert.Equal("Alicia", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCellValue_ByIndex_DoesNotChangeRowCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(1, 2, "99");
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void SetCellValue_ByIndex_DoesNotChangeColumnCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, 1, "Finance");
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void SetCellValue_ByIndex_MultipleTimes_LastWins()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, 0, "First");
        doc.SetCellValue(0, 0, "Second");
        doc.SetCellValue(0, 0, "Final");
        Assert.Equal("Final", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCellValue_ByIndex_AllCellsInRow()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(2, 0, "NewName");
        doc.SetCellValue(2, 1, "NewDept");
        doc.SetCellValue(2, 2, "NewScore");
        Assert.Equal("NewName", doc.GetCellValue(2, 0));
        Assert.Equal("NewDept", doc.GetCellValue(2, 1));
        Assert.Equal("NewScore", doc.GetCellValue(2, 2));
    }

    // -------------------------------------------------------------------------
    // SetCellValue by column name
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_ByColName_ChangesValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, "name", "Alicia");
        Assert.Equal("Alicia", doc.GetCellValue(0, "name"));
    }

    [Fact]
    public void SetCellValue_ByColName_Score_ChangesValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(1, "score", "99");
        Assert.Equal("99", doc.GetCellValue(1, "score"));
    }

    [Fact]
    public void SetCellValue_ByColName_DoesNotChangeRowCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, "dept", "HR");
        Assert.Equal(3, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToTsv_NonNull()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.NotNull(doc.ToTsv());
    }

    [Fact]
    public void ToTsv_ContainsHeaders()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var tsv = doc.ToTsv();
        Assert.Contains("name", tsv);
        Assert.Contains("dept", tsv);
        Assert.Contains("score", tsv);
    }

    [Fact]
    public void ToTsv_ContainsRowData()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var tsv = doc.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Carol", tsv);
    }

    [Fact]
    public void ToTsv_HasTabs()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Contains("\t", doc.ToTsv());
    }

    [Fact]
    public void ToTsv_RoundTrip_CountCorrect()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var tsv = doc.ToTsv();
        var reloaded = TsvDocument.Load(tsv);
        Assert.Equal(3, reloaded.RowCount);
    }

    [Fact]
    public void ToTsv_RoundTrip_ValuesCorrect()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var tsv = doc.ToTsv();
        var reloaded = TsvDocument.Load(tsv);
        Assert.Contains("Alice", reloaded.GetColumnValues("name"));
        Assert.Contains("Carol", reloaded.GetColumnValues("name"));
    }

    [Fact]
    public void ToTsv_AfterMutation_ReflectsChange()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, "name", "Alicia");
        var tsv = doc.ToTsv();
        Assert.Contains("Alicia", tsv);
        Assert.DoesNotContain("Alice", tsv);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadSetCellValueToTsvLoadFilterToTsvLoad_Pipeline()
    {
        // Load
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(3, doc.RowCount);

        // SetCellValue
        doc.SetCellValue(0, "dept", "HR");
        Assert.Equal("HR", doc.GetCellValue(0, "dept"));
        Assert.Equal(3, doc.RowCount); // unchanged

        // ToTsv round-trip
        var tsv = doc.ToTsv();
        var reloaded = TsvDocument.Load(tsv);
        Assert.Equal(3, reloaded.RowCount);
        Assert.Equal("HR", reloaded.GetCellValue(0, "dept"));

        // Filter — Alice is now in HR, Bob in Finance, Carol in Eng
        var hr = reloaded.Filter(r => r.GetValue("dept") == "HR");
        Assert.Equal(1, hr.RowCount);

        // ToTsv from filtered
        var hrTsv = hr.ToTsv();
        Assert.Contains("Alice", hrTsv);
        Assert.DoesNotContain("Bob", hrTsv);

        // Load from filtered ToTsv
        var hrLoaded = TsvDocument.Load(hrTsv);
        Assert.Equal(1, hrLoaded.RowCount);
        Assert.True(hrLoaded.HasHeaders);
        Assert.Equal("Alice", hrLoaded.GetCellValue(0, "name"));
    }
}
