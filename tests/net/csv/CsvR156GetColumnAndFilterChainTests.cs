// Tests for CsvDocument.GetColumn(string), Filter chain, and multi-column access.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R156

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R156: Tests for CsvDocument.GetColumn(string), Filter chain, and multi-column access.
/// GetColumn(headerName): returns values for a named column.
/// GetColumn(index): returns values for a column by index.
/// Filter chaining: apply multiple predicates sequentially.
/// Covers: GetColumn by name count equals row count; GetColumn by name contains values;
/// GetColumn by name for dept column; GetColumn by index 0 equals GetColumn by name;
/// Filter->GetColumn by name count matches; Filter->GetColumn by name values correct;
/// Filter->Filter->GetColumn chained; Filter all->GetColumn unchanged count;
/// Filter none->GetColumn is empty; HasColumn after Load;
/// ColumnCount after Filter matches original; GetColumn on filtered is subset;
/// GetCellValue after Filter chain; GetColumn after AddRow;
/// dogfood Load->Filter->GetColumn->Filter->GetColumn chain pipeline.
/// </summary>
public class CsvR156GetColumnAndFilterChainTests
{
    private const string FiveRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88\n" +
        "Dave,Finance,91\n" +
        "Eve,Eng,79";

    // -------------------------------------------------------------------------
    // GetColumn(string headerName)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnByName_Name_CountEqualsRowCount()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var col = doc.GetColumn("Name");
        Assert.Equal(5, col.Count);
    }

    [Fact]
    public void GetColumnByName_Name_ContainsValues()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var col = doc.GetColumn("Name");
        Assert.Contains("Alice", col);
        Assert.Contains("Bob", col);
        Assert.Contains("Carol", col);
    }

    [Fact]
    public void GetColumnByName_Dept_ContainsDepts()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var col = doc.GetColumn("Dept");
        Assert.Contains("Eng", col);
        Assert.Contains("Finance", col);
    }

    [Fact]
    public void GetColumnByName_EqualsGetColumnByIndex()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var byName = doc.GetColumn("Name");
        var byIndex = doc.GetColumn(0);
        Assert.Equal(byName, byIndex);
    }

    [Fact]
    public void GetColumnByName_AfterAddRow_ContainsNewValue()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        doc.AddRow(new[] { "Frank", "Eng", "77" });
        var col = doc.GetColumn("Name");
        Assert.Contains("Frank", col);
    }

    // -------------------------------------------------------------------------
    // Filter -> GetColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_GetColumnByName_CountMatchesFilter()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var col = eng.GetColumn("Name");
        Assert.Equal(3, col.Count);
    }

    [Fact]
    public void Filter_GetColumnByName_ValuesCorrect()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var col = eng.GetColumn("Name");
        Assert.Contains("Alice", col);
        Assert.Contains("Carol", col);
        Assert.Contains("Eve", col);
        Assert.DoesNotContain("Bob", col);
    }

    [Fact]
    public void Filter_All_GetColumn_CountUnchanged()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var all = doc.Filter(_ => true);
        var col = all.GetColumn("Name");
        Assert.Equal(5, col.Count);
    }

    [Fact]
    public void Filter_None_GetColumn_IsEmpty()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var none = doc.Filter(_ => false);
        var col = none.GetColumn(0);
        Assert.Empty(col);
    }

    // -------------------------------------------------------------------------
    // Filter chaining
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_Filter_GetColumn_Chained()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        // Eng rows (Alice=95, Carol=88, Eve=79)
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        // High score (Alice=95, Carol=88)
        var highEng = eng.Filter(r => r.Length > 2 && int.TryParse(r[2], out var s) && s >= 85);
        var names = highEng.GetColumn("Name");
        Assert.Equal(2, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Eve", names);
    }

    [Fact]
    public void Filter_Chain_ColumnCount_MatchesOriginal()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.ColumnCount, filtered.ColumnCount);
    }

    [Fact]
    public void Filter_GetCellValue_AfterChain()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var highEng = eng.Filter(r => r.Length > 2 && int.TryParse(r[2], out var s) && s > 90);
        Assert.Equal("Alice", highEng.GetCellValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->GetColumn->Filter->GetColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterGetColumnFilterGetColumn_Pipeline()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        Assert.Equal(5, doc.RowCount);
        Assert.True(doc.HasColumn("Name"));
        Assert.True(doc.HasColumn("Dept"));

        // Filter Eng
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal(3, eng.RowCount);

        // GetColumn on filtered
        var engNames = eng.GetColumn("Name");
        Assert.Equal(3, engNames.Count);
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);
        Assert.Contains("Eve", engNames);

        // Filter high score (>85)
        var highEng = eng.Filter(r => r.Length > 2 && int.TryParse(r[2], out var s) && s > 85);
        Assert.Equal(2, highEng.RowCount); // Alice=95, Carol=88

        // GetColumn on double-filtered
        var highNames = highEng.GetColumn("Name");
        Assert.Equal(2, highNames.Count);
        Assert.Contains("Alice", highNames);
        Assert.Contains("Carol", highNames);
        Assert.DoesNotContain("Eve", highNames);

        // Scores column
        var scores = highEng.GetColumn("Score");
        Assert.Equal(2, scores.Count);
        Assert.Contains("95", scores);
        Assert.Contains("88", scores);
    }
}
