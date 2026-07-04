// Tests for CsvDocument.Filter chain and GetColumn deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R170

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R170: Tests for CsvDocument.Filter chain, GetColumn deeper.
/// Filter(predicate): returns new CsvDocument with matching rows.
/// GetColumn(name): returns all values for a named column.
/// GetColumn(index): returns all values for a column by index.
/// Covers: Filter non-null; Filter count correct; Filter non-matching empty;
/// Filter chain narrows; Filter preserves headers; Filter->GetColumn correct;
/// GetColumn by name count equals RowCount; GetColumn by name all values correct;
/// GetColumn by index matches by name; GetColumn after AddRow includes new row;
/// Filter->Filter->Filter chain; GetColumn for non-existent returns empty;
/// Filter->GetColumn->Contains chain; Filter by numeric condition;
/// GetColumn after SetCellValue reflects mutation;
/// dogfood Load->Filter->GetColumn->Filter->GetColumn->ToCsv->Load verify.
/// </summary>
public class CsvR170FilterAndGetColumnDeepTests
{
    private const string FiveRowCsv =
        "name,dept,salary,level\n" +
        "Alice,Eng,95000,Senior\n" +
        "Bob,Finance,82000,Mid\n" +
        "Carol,Eng,88000,Senior\n" +
        "Dave,HR,76000,Mid\n" +
        "Eve,Eng,91000,Senior";

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_NonNull()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var result = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.NotNull(result);
    }

    [Fact]
    public void Filter_ByDept_Eng_CountIsThree()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(3, eng.RowCount);
    }

    [Fact]
    public void Filter_NonMatching_ReturnsEmpty()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var none = doc.Filter(r => r.GetValue("dept") == "Marketing");
        Assert.Equal(0, none.RowCount);
    }

    [Fact]
    public void Filter_Chain_NarrowsResult()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var senior = eng.Filter(r => r.GetValue("level") == "Senior");
        Assert.Equal(3, senior.RowCount); // All Eng are Senior
    }

    [Fact]
    public void Filter_PreservesHeaders()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var filtered = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.True(filtered.HasHeaders);
        Assert.Contains("name", filtered.Headers);
        Assert.Contains("salary", filtered.Headers);
    }

    [Fact]
    public void Filter_ByNumericCondition()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var high = doc.Filter(r =>
            int.TryParse(r.GetValue("salary"), out var s) && s > 88000);
        Assert.Equal(2, high.RowCount); // Alice(95000), Eve(91000)
    }

    [Fact]
    public void Filter_TripleChain()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var step1 = doc.Filter(r => r.GetValue("dept") == "Eng");
        var step2 = step1.Filter(r => r.GetValue("level") == "Senior");
        var step3 = step2.Filter(r =>
            int.TryParse(r.GetValue("salary"), out var s) && s > 90000);
        Assert.Equal(2, step3.RowCount); // Alice(95000), Eve(91000)
    }

    // -------------------------------------------------------------------------
    // GetColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumn_ByName_CountEqualsRowCount()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var names = doc.GetColumn("name");
        Assert.Equal(doc.RowCount, names.Count);
    }

    [Fact]
    public void GetColumn_ByName_AllValues()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var names = doc.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);
    }

    [Fact]
    public void GetColumn_ByIndex_MatchesByName()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var byName = doc.GetColumn("dept");
        var byIndex = doc.GetColumn(1);
        Assert.Equal(byName.Count, byIndex.Count);
        for (var i = 0; i < byName.Count; i++)
            Assert.Equal(byName[i], byIndex[i]);
    }

    [Fact]
    public void GetColumn_AfterFilter_CorrectValues()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var names = eng.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Eve", names);
        Assert.DoesNotContain("Bob", names);
    }

    [Fact]
    public void GetColumn_AfterAddRow_IncludesNewRow()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        doc.AddRow(new[] { "Frank", "Eng", "93000", "Senior" });
        var names = doc.GetColumn("name");
        Assert.Contains("Frank", names);
    }

    [Fact]
    public void GetColumn_AfterSetCellValue_ReflectsMutation()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        doc.SetCellValue(0, 0, "Alicia");
        var names = doc.GetColumn("name");
        Assert.Contains("Alicia", names);
        Assert.DoesNotContain("Alice", names);
    }

    [Fact]
    public void GetColumn_NonExistent_ReturnsEmptyOrNull()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        try
        {
            var result = doc.GetColumn("nonexistent");
            Assert.True(result == null || result.Count == 0);
        }
        catch (CsvReaderException)
        {
            // Also acceptable: GetColumn throws for unknown header name
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterGetColumnFilterGetColumnToCsvLoadVerify_Pipeline()
    {
        // Load
        var doc = CsvDocument.Load(FiveRowCsv);
        Assert.Equal(5, doc.RowCount);

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(3, eng.RowCount);

        // GetColumn names from Eng
        var engNames = eng.GetColumn("name");
        Assert.Equal(3, engNames.Count);
        Assert.Contains("Alice", engNames);

        // Filter high salary from Eng
        var highSalary = eng.Filter(r =>
            int.TryParse(r.GetValue("salary"), out var s) && s > 90000);
        Assert.Equal(2, highSalary.RowCount);

        // GetColumn salaries
        var salaries = highSalary.GetColumn("salary");
        Assert.Contains("95000", salaries);
        Assert.Contains("91000", salaries);

        // ToCsv
        var csv = highSalary.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Eve", csv);
        Assert.DoesNotContain("Carol", csv);

        // Load round-trip
        var loaded = CsvDocument.Load(csv);
        Assert.Equal(2, loaded.RowCount);
        Assert.True(loaded.HasHeaders);
        var loadedNames = loaded.GetColumn("name");
        Assert.Contains("Alice", loadedNames);
        Assert.Contains("Eve", loadedNames);
    }
}
