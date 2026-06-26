// Tests for TsvDocument.GetColumnValues and Filter chain deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R169

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R169: Tests for TsvDocument.GetColumnValues and Filter chain deeper coverage.
/// GetColumnValues(name): returns all values for a named column across all rows.
/// Filter(predicate): returns new TsvDocument with rows matching predicate.
/// Covers: GetColumnValues count equals RowCount; GetColumnValues contains expected values;
/// GetColumnValues non-existent returns empty; GetColumnValues after AddRow includes new row;
/// GetColumnValues after SetCellValue reflects mutation;
/// Filter non-null; Filter count correct; Filter non-matching empty; Filter preserves headers;
/// Filter chain narrows; Filter by numeric condition; Filter->GetColumnValues correct;
/// triple Filter chain; dogfood Load->Filter->GetColumnValues->Filter->ToCsv->Load->verify.
/// </summary>
public class TsvR169GetColumnValuesAndFilterChainDeepTests
{
    private const string FiveRowTsv =
        "name\tdept\tsalary\tlevel\n" +
        "Alice\tEng\t95000\tSenior\n" +
        "Bob\tFinance\t82000\tMid\n" +
        "Carol\tEng\t88000\tSenior\n" +
        "Dave\tHR\t76000\tMid\n" +
        "Eve\tEng\t91000\tSenior";

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_CountEqualsRowCount()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var names = doc.GetColumnValues("name");
        Assert.Equal(doc.RowCount, names.Count);
    }

    [Fact]
    public void GetColumnValues_ContainsExpectedValues()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var names = doc.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);
    }

    [Fact]
    public void GetColumnValues_NonExistent_ReturnsEmptyOrNull()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var result = doc.GetColumnValues("nonexistent");
        Assert.True(result == null || result.Count == 0);
    }

    [Fact]
    public void GetColumnValues_AfterAddRow_IncludesNewRow()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        doc.AddRow(new[] { "Frank", "Eng", "93000", "Senior" });
        var names = doc.GetColumnValues("name");
        Assert.Contains("Frank", names);
    }

    [Fact]
    public void GetColumnValues_AfterSetCellValue_ReflectsMutation()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        doc.SetCellValue(0, 0, "Alicia");
        var names = doc.GetColumnValues("name");
        Assert.Contains("Alicia", names);
        Assert.DoesNotContain("Alice", names);
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_NonNull()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        Assert.NotNull(doc.Filter(r => r.GetValue("dept") == "Eng"));
    }

    [Fact]
    public void Filter_ByDept_Eng_CountIsThree()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(3, eng.RowCount);
    }

    [Fact]
    public void Filter_NonMatching_ReturnsEmpty()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var none = doc.Filter(r => r.GetValue("dept") == "Marketing");
        Assert.Equal(0, none.RowCount);
    }

    [Fact]
    public void Filter_PreservesHeaders()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var filtered = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.True(filtered.HasHeaders);
        Assert.Contains("name", filtered.Headers);
        Assert.Contains("salary", filtered.Headers);
    }

    [Fact]
    public void Filter_Chain_NarrowsResult()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var senior = eng.Filter(r => r.GetValue("level") == "Senior");
        Assert.Equal(3, senior.RowCount); // All Eng are Senior
    }

    [Fact]
    public void Filter_ByNumericCondition()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var high = doc.Filter(r =>
            int.TryParse(r.GetValue("salary"), out var s) && s > 88000);
        Assert.Equal(2, high.RowCount); // Alice(95000), Eve(91000)
    }

    [Fact]
    public void Filter_TripleChain()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var step1 = doc.Filter(r => r.GetValue("dept") == "Eng");
        var step2 = step1.Filter(r => r.GetValue("level") == "Senior");
        var step3 = step2.Filter(r =>
            int.TryParse(r.GetValue("salary"), out var s) && s > 90000);
        Assert.Equal(2, step3.RowCount); // Alice(95000), Eve(91000)
    }

    [Fact]
    public void Filter_ThenGetColumnValues_CorrectValues()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var names = eng.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Eve", names);
        Assert.DoesNotContain("Bob", names);
        Assert.DoesNotContain("Dave", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterGetColumnValuesFilterToTsvLoadVerify_Pipeline()
    {
        // Load
        var doc = TsvDocument.Load(FiveRowTsv);
        Assert.Equal(5, doc.RowCount);

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(3, eng.RowCount);

        // GetColumnValues names from Eng
        var engNames = eng.GetColumnValues("name");
        Assert.Equal(3, engNames.Count);
        Assert.Contains("Alice", engNames);

        // Filter high salary
        var highSalary = eng.Filter(r =>
            int.TryParse(r.GetValue("salary"), out var s) && s > 90000);
        Assert.Equal(2, highSalary.RowCount);

        // GetColumnValues salaries
        var salaries = highSalary.GetColumnValues("salary");
        Assert.Contains("95000", salaries);
        Assert.Contains("91000", salaries);

        // ToTsv round-trip
        var tsv = highSalary.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Eve", tsv);
        Assert.DoesNotContain("Carol", tsv);

        // Load round-trip
        var loaded = TsvDocument.Load(tsv);
        Assert.Equal(2, loaded.RowCount);
        Assert.True(loaded.HasHeaders);

        var loadedNames = loaded.GetColumnValues("name");
        Assert.Contains("Alice", loadedNames);
        Assert.Contains("Eve", loadedNames);
    }
}
