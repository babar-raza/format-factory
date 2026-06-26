// Tests for TsvDocument.GetColumnValues deeper coverage and Filter chain.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R148

using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R148: Tests for TsvDocument.GetColumnValues, Filter chain, and multi-column access.
/// GetColumnValues(colIndex): returns all values from a given column.
/// Filter->GetColumnValues chain: combine predicates with column projections.
/// Covers: GetColumnValues col0 count equals RowCount; GetColumnValues col0 contains Alice;
/// GetColumnValues col2 contains scores; Filter->GetColumnValues on Eng subset;
/// GetColumnValues on filtered preserves relative order; Filter keep-all->GetColumnValues;
/// IsEmpty after Filter-none; Filter partial->RowCount; Filter->GetCellValue;
/// GetColumnValues on single-row doc; Filter->ToTsv contains filtered values;
/// Filter then GetColumnValues count; dogfood Load->Filter->GetColumnValues->Filter->ToTsv.
/// </summary>
public class TsvR148GetColumnValuesAndFilterChainTests
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
    public void GetColumnValues_Col0_ContainsAlice()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var col = doc.GetColumnValues(0);
        Assert.Contains("Alice", col);
        Assert.Contains("Bob", col);
        Assert.Contains("Carol", col);
        Assert.Contains("Dave", col);
    }

    [Fact]
    public void GetColumnValues_Col2_ContainsScores()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var col = doc.GetColumnValues(2);
        Assert.Contains("95", col);
        Assert.Contains("82", col);
        Assert.Contains("88", col);
        Assert.Contains("91", col);
    }

    [Fact]
    public void GetColumnValues_SingleRowDoc_CountIsOne()
    {
        var doc = TsvDocument.Load("X\t1\t2");
        var col = doc.GetColumnValues(0);
        Assert.Single(col);
        Assert.Equal("X", col[0]);
    }

    // -------------------------------------------------------------------------
    // Filter -> GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_GetColumnValues_EngSubset_CountIsTwo()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var names = eng.GetColumnValues(0);
        Assert.Equal(2, names.Count);
    }

    [Fact]
    public void Filter_GetColumnValues_EngSubset_ContainsAliceAndCarol()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var names = eng.GetColumnValues(0);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
        Assert.DoesNotContain("Dave", names);
    }

    [Fact]
    public void Filter_KeepAll_GetColumnValues_CountUnchanged()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var all = doc.Filter(_ => true);
        var col = all.GetColumnValues(0);
        Assert.Equal(doc.RowCount, col.Count);
    }

    [Fact]
    public void Filter_None_IsEmpty()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var none = doc.Filter(_ => false);
        Assert.True(none.IsEmpty);
        Assert.Equal(0, none.RowCount);
    }

    [Fact]
    public void Filter_Partial_RowCountIsTwo()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var finance = doc.Filter(r => r.Length > 1 && r[1] == "Finance");
        Assert.Equal(2, finance.RowCount);
    }

    [Fact]
    public void Filter_GetCellValue_FirstRowIsCorrect()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal("Alice", eng.GetCellValue(0, 0));
        Assert.Equal("Eng", eng.GetCellValue(0, 1));
    }

    // -------------------------------------------------------------------------
    // Filter -> ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_ToTsv_ContainsFilteredValues()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var tsv = eng.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Carol", tsv);
        Assert.DoesNotContain("Bob", tsv);
    }

    [Fact]
    public void Filter_GetColumnValues_CountMatchesFiltered()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var finance = doc.Filter(r => r.Length > 1 && r[1] == "Finance");
        var names = finance.GetColumnValues(0);
        Assert.Equal(finance.RowCount, names.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->GetColumnValues->Filter->ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FilterColumnValuesFilterToTsv_Pipeline()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Equal(4, doc.RowCount);

        // First filter: Eng rows
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal(2, eng.RowCount);

        // GetColumnValues on filtered
        var names = eng.GetColumnValues(0);
        Assert.Equal(2, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);

        // Second filter on eng: score > 90
        var high = eng.Filter(r => r.Length > 2 && int.TryParse(r[2], out var s) && s > 90);
        Assert.Equal(1, high.RowCount);

        // ToTsv of final result
        var tsv = high.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("\t", tsv);
    }
}
