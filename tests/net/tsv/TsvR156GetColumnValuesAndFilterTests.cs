// Tests for TsvDocument.GetColumnValues deeper coverage and filter combinations.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R156

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R156: Tests for TsvDocument.GetColumnValues deeper coverage and Filter combinations.
/// GetColumnValues(colIndex): returns all values in a column as list.
/// Filter(predicate): returns subset document.
/// Covers: GetColumnValues count equals RowCount; GetColumnValues col0 has expected values;
/// GetColumnValues col1 has expected values; GetColumnValues col2 has scores;
/// GetColumnValues out-of-bounds returns empty; Filter then GetColumnValues count;
/// Filter then GetColumnValues values; Filter-all GetColumnValues unchanged;
/// Filter-none GetColumnValues is empty; GetColumnValues after AddRow has new value;
/// GetColumnValues on single-col doc; ColumnCount after Filter-all unchanged;
/// IsEmpty property after Filter-none; ToTsv after Filter contains subset;
/// dogfood Load->GetColumnValues->Filter->GetColumnValues->ToTsv pipeline.
/// </summary>
public class TsvR156GetColumnValuesAndFilterTests
{
    private const string FourRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88\n" +
        "Dave\tFinance\t91";

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_Col0_CountEqualsRowCount()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var col = doc.GetColumnValues(0);
        Assert.Equal(doc.RowCount, col.Count);
    }

    [Fact]
    public void GetColumnValues_Col0_HasExpectedValues()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var col = doc.GetColumnValues(0);
        Assert.Contains("Alice", col);
        Assert.Contains("Bob", col);
        Assert.Contains("Carol", col);
        Assert.Contains("Dave", col);
    }

    [Fact]
    public void GetColumnValues_Col1_HasDeptValues()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var col = doc.GetColumnValues(1);
        Assert.Contains("Eng", col);
        Assert.Contains("Finance", col);
    }

    [Fact]
    public void GetColumnValues_Col2_HasScores()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var col = doc.GetColumnValues(2);
        Assert.Contains("95", col);
        Assert.Contains("82", col);
        Assert.Contains("88", col);
        Assert.Contains("91", col);
    }

    [Fact]
    public void GetColumnValues_OutOfBounds_ReturnsEmpty()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var col = doc.GetColumnValues(999);
        Assert.Empty(col);
    }

    [Fact]
    public void GetColumnValues_AfterAddRow_HasNewValue()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        doc.Rows.Add(new[] { "Eve", "Eng", "79" });
        var col = doc.GetColumnValues(0);
        Assert.Contains("Eve", col);
    }

    [Fact]
    public void GetColumnValues_SingleColDoc_CountIsRowCount()
    {
        var doc = TsvDocument.Load("Name\nAlice\nBob\nCarol");
        var col = doc.GetColumnValues(0);
        Assert.Equal(3, col.Count);
    }

    // -------------------------------------------------------------------------
    // Filter -> GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_GetColumnValues_Count()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var col = eng.GetColumnValues(0);
        Assert.Equal(2, col.Count);
    }

    [Fact]
    public void Filter_GetColumnValues_Values()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var col = eng.GetColumnValues(0);
        Assert.Contains("Alice", col);
        Assert.Contains("Carol", col);
        Assert.DoesNotContain("Bob", col);
    }

    [Fact]
    public void Filter_All_GetColumnValues_Unchanged()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var all = doc.Filter(_ => true);
        var col = all.GetColumnValues(0);
        Assert.Equal(4, col.Count);
    }

    [Fact]
    public void Filter_None_GetColumnValues_IsEmpty()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var none = doc.Filter(_ => false);
        var col = none.GetColumnValues(0);
        Assert.Empty(col);
    }

    [Fact]
    public void Filter_None_IsEmpty_True()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var none = doc.Filter(_ => false);
        Assert.True(none.IsEmpty);
    }

    [Fact]
    public void Filter_All_ColumnCount_Unchanged()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var all = doc.Filter(_ => true);
        Assert.Equal(doc.ColumnCount, all.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // ToTsv after Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void ToTsv_AfterFilter_ContainsSubset()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var tsv = eng.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Carol", tsv);
        Assert.DoesNotContain("Bob", tsv);
        Assert.DoesNotContain("Dave", tsv);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetColumnValues->Filter->GetColumnValues->ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadGetColumnValuesFilterGetColumnValuesToTsv_Pipeline()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Equal(4, doc.RowCount);
        Assert.Equal(3, doc.ColumnCount);

        // GetColumnValues all names
        var allNames = doc.GetColumnValues(0);
        Assert.Equal(4, allNames.Count);

        // Filter: Eng
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal(2, eng.RowCount);

        // GetColumnValues on filtered
        var engNames = eng.GetColumnValues(0);
        Assert.Equal(2, engNames.Count);
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);

        // ToTsv
        var tsv = eng.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.DoesNotContain("Bob", tsv);

        // Load from ToTsv
        var loaded = TsvDocument.Load(tsv);
        Assert.Equal(2, loaded.RowCount);
        var loadedNames = loaded.GetColumnValues(0);
        Assert.Contains("Alice", loadedNames);
        Assert.Contains("Carol", loadedNames);
    }
}
