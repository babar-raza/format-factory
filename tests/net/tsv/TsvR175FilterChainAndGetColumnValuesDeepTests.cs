// Tests for TsvDocument.Filter chain, GetColumnValues on filtered results deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R175

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R175: Tests for TsvDocument.Filter chain and GetColumnValues on filtered results deeper.
/// Filter(predicate): returns a new TsvDocument with rows matching the predicate.
/// GetColumnValues(colName): returns all values in the named column.
/// Covers: Filter returns non-null; Filter count less than original; Filter correct rows kept;
/// Filter then GetColumnValues returns correct values; Filter chain (two conditions);
/// Filter empty result; Filter all match; GetColumnValues on filtered doc correct count;
/// GetColumnValues distinct values after filter; Filter then AddRow increases count;
/// dogfood Load->Filter->GetColumnValues->Filter chain->AddRow->verify pipeline.
/// </summary>
public class TsvR175FilterChainAndGetColumnValuesDeepTests
{
    private static TsvDocument CreateWithData()
    {
        var doc = TsvDocument.CreateEmpty(new List<string> { "Name", "Dept", "Score", "Active" });
        doc.AddRow(new List<string> { "Alice", "Engineering", "92", "true" });
        doc.AddRow(new List<string> { "Bob", "Finance", "85", "true" });
        doc.AddRow(new List<string> { "Carol", "Engineering", "78", "false" });
        doc.AddRow(new List<string> { "Dave", "HR", "91", "true" });
        doc.AddRow(new List<string> { "Eve", "Finance", "88", "false" });
        doc.AddRow(new List<string> { "Frank", "Engineering", "95", "true" });
        return doc;
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_NonNull()
    {
        var doc = CreateWithData();
        Assert.NotNull(doc.Filter(r => r.GetCell("Dept") == "Engineering"));
    }

    [Fact]
    public void Filter_ByDept_CorrectCount()
    {
        var doc = CreateWithData();
        var eng = doc.Filter(r => r.GetCell("Dept") == "Engineering");
        Assert.Equal(3, eng.RowCount);
    }

    [Fact]
    public void Filter_ByDept_CorrectRows()
    {
        var doc = CreateWithData();
        var finance = doc.Filter(r => r.GetCell("Dept") == "Finance");
        Assert.Equal(2, finance.RowCount);
        var names = finance.GetColumnValues("Name");
        Assert.Contains("Bob", names);
        Assert.Contains("Eve", names);
    }

    [Fact]
    public void Filter_EmptyResult_ZeroRows()
    {
        var doc = CreateWithData();
        var none = doc.Filter(r => r.GetCell("Dept") == "Marketing");
        Assert.Equal(0, none.RowCount);
    }

    [Fact]
    public void Filter_AllMatch_SameCount()
    {
        var doc = CreateWithData();
        var all = doc.Filter(r => r.GetCell("Name") != "NONEXISTENT");
        Assert.Equal(doc.RowCount, all.RowCount);
    }

    [Fact]
    public void Filter_ByActive_CorrectCount()
    {
        var doc = CreateWithData();
        var active = doc.Filter(r => r.GetCell("Active") == "true");
        Assert.Equal(4, active.RowCount);
    }

    // -------------------------------------------------------------------------
    // Filter chain (two conditions)
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterChain_EngAndActive_CorrectCount()
    {
        var doc = CreateWithData();
        var engActive = doc
            .Filter(r => r.GetCell("Dept") == "Engineering")
            .Filter(r => r.GetCell("Active") == "true");
        Assert.Equal(2, engActive.RowCount);
    }

    [Fact]
    public void FilterChain_EngAndActive_CorrectNames()
    {
        var doc = CreateWithData();
        var engActive = doc
            .Filter(r => r.GetCell("Dept") == "Engineering")
            .Filter(r => r.GetCell("Active") == "true");
        var names = engActive.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Frank", names);
        Assert.DoesNotContain("Carol", names);
    }

    // -------------------------------------------------------------------------
    // GetColumnValues on filtered
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_AfterFilter_CorrectCount()
    {
        var doc = CreateWithData();
        var eng = doc.Filter(r => r.GetCell("Dept") == "Engineering");
        var names = eng.GetColumnValues("Name");
        Assert.Equal(3, names.Count);
    }

    [Fact]
    public void GetColumnValues_AfterFilter_ContainsExpectedValues()
    {
        var doc = CreateWithData();
        var eng = doc.Filter(r => r.GetCell("Dept") == "Engineering");
        var names = eng.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Frank", names);
        Assert.DoesNotContain("Bob", names);
    }

    [Fact]
    public void GetColumnValues_DeptColumn_AllSame_AfterFilter()
    {
        var doc = CreateWithData();
        var hr = doc.Filter(r => r.GetCell("Dept") == "HR");
        var depts = hr.GetColumnValues("Dept");
        Assert.All(depts, d => Assert.Equal("HR", d));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateWithData_Filter_GetColumnValues_FilterChain_AddRow_Verify_Pipeline()
    {
        // Create with data
        var doc = CreateWithData();
        Assert.Equal(6, doc.RowCount);

        // Filter by dept
        var eng = doc.Filter(r => r.GetCell("Dept") == "Engineering");
        Assert.Equal(3, eng.RowCount);

        // GetColumnValues on filtered
        var engNames = eng.GetColumnValues("Name");
        Assert.Equal(3, engNames.Count);
        Assert.Contains("Alice", engNames);
        Assert.Contains("Frank", engNames);

        // Filter chain
        var engActive = eng.Filter(r => r.GetCell("Active") == "true");
        Assert.Equal(2, engActive.RowCount);
        var activeNames = engActive.GetColumnValues("Name");
        Assert.Contains("Alice", activeNames);
        Assert.Contains("Frank", activeNames);
        Assert.DoesNotContain("Carol", activeNames);

        // GetColumnValues from original doc
        var allDepts = doc.GetColumnValues("Dept");
        Assert.Equal(6, allDepts.Count);

        // Filter Finance -> AddRow
        var finance = doc.Filter(r => r.GetCell("Dept") == "Finance");
        Assert.Equal(2, finance.RowCount);
        finance.AddRow(new List<string> { "Grace", "Finance", "82", "true" });
        Assert.Equal(3, finance.RowCount);
        var financeNames = finance.GetColumnValues("Name");
        Assert.Contains("Grace", financeNames);
    }
}
