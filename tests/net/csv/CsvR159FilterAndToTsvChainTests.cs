// Tests for CsvDocument.Filter chain, HasColumn, GetColumn by index and name.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R159

using System.Linq;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R159: Tests for CsvDocument.Filter chain, HasColumn, GetColumn combinations.
/// Filter(predicate): returns new CsvDocument with matching rows.
/// HasColumn(name): returns true if column exists by name.
/// GetColumn(name): returns all values for the named column.
/// GetColumn(index): returns all values for column at zero-based index.
/// Covers: Filter by column value returns rows; Filter count correct;
/// Filter non-matching returns zero rows; Filter chain narrows result;
/// HasColumn true for existing; HasColumn false for non-existent;
/// GetColumn by name count matches row count; GetColumn by name values correct;
/// GetColumn by index count matches row count; GetColumn after Filter count correct;
/// Filter->ToCsv->Load round-trip; Filter preserves headers;
/// GetColumn by index matches by name;
/// dogfood Load->Filter->HasColumn->GetColumn->ToCsv->Load verify pipeline.
/// </summary>
public class CsvR159FilterAndToTsvChainTests
{
    private const string ThreeRowCsv =
        "name,dept,score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88";

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_ByDept_Eng_CountIsTwo()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);
    }

    [Fact]
    public void Filter_ByDept_Finance_CountIsOne()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var fin = doc.Filter(r => r.GetValue("dept") == "Finance");
        Assert.Equal(1, fin.RowCount);
    }

    [Fact]
    public void Filter_NonMatching_CountIsZero()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var none = doc.Filter(r => r.GetValue("dept") == "HR");
        Assert.Equal(0, none.RowCount);
    }

    [Fact]
    public void Filter_Chain_NarrowsResult()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var high = eng.Filter(r =>
            int.TryParse(r.GetValue("score"), out var s) && s > 90);
        Assert.Equal(1, high.RowCount);
    }

    [Fact]
    public void Filter_PreservesHeaders()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Contains("name", eng.Headers);
        Assert.Contains("dept", eng.Headers);
        Assert.Contains("score", eng.Headers);
    }

    // -------------------------------------------------------------------------
    // HasColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_ExistingColumn_ReturnsTrue()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.True(doc.HasColumn("name"));
    }

    [Fact]
    public void HasColumn_NonExistentColumn_ReturnsFalse()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.False(doc.HasColumn("salary"));
    }

    // -------------------------------------------------------------------------
    // GetColumn by name
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnByName_Count_MatchesRowCount()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var names = doc.GetColumn("name");
        Assert.Equal(3, names.Count);
    }

    [Fact]
    public void GetColumnByName_ContainsAllValues()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var names = doc.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void GetColumnByName_AfterFilter_CorrectValues()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var names = eng.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }

    // -------------------------------------------------------------------------
    // GetColumn by index
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnByIndex_Zero_MatchesNameColumn()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var byName = doc.GetColumn("name");
        var byIndex = doc.GetColumn(0);
        Assert.Equal(byName.Count, byIndex.Count);
    }

    [Fact]
    public void GetColumnByIndex_One_ContainsDepts()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var depts = doc.GetColumn(1);
        Assert.Contains("Eng", depts);
        Assert.Contains("Finance", depts);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->HasColumn->GetColumn->ToCsv->Load verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterHasColumnGetColumnToCsvLoad_Pipeline()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal(3, doc.RowCount);

        // HasColumn
        Assert.True(doc.HasColumn("name"));
        Assert.True(doc.HasColumn("dept"));
        Assert.False(doc.HasColumn("nonexistent"));

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);

        // GetColumn
        var names = eng.GetColumn("name");
        Assert.Equal(2, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);

        // ToCsv
        var csv = eng.ToCsv();
        Assert.NotNull(csv);
        Assert.Contains("Alice", csv);

        // Load
        var loaded = CsvDocument.Load(csv);
        Assert.Equal(2, loaded.RowCount);
        Assert.True(loaded.HasColumn("name"));
        Assert.True(loaded.HasColumn("dept"));
    }
}
