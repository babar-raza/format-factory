// Tests for CsvDocument.RowCount, Filter, mutation patterns deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R164

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R164: Tests for CsvDocument.RowCount, Filter, mutation patterns deeper coverage.
/// RowCount: number of data rows.
/// Filter(predicate): returns filtered document.
/// AddRow(values): adds a row.
/// RemoveRow(index): removes a row.
/// Covers: RowCount zero for empty doc; RowCount positive for data;
/// RowCount after AddRow; RowCount after RemoveRow; Filter RowCount;
/// Filter after AddRow; AddRow then GetColumnValues; RemoveRow then GetColumnValues;
/// Filter->AddRow chain; AddRow multiple then Filter;
/// RowCount after Filter; GetColumn after mutation; RowCount consistent;
/// RemoveRow preserves headers; Filter non-matching empty;
/// dogfood Load->Filter->AddRow->RemoveRow->GetColumn->ToCsv->Load verify.
/// </summary>
public class CsvR164RowCountAndMutationTests
{
    private const string ThreeRowCsv =
        "name,dept,score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88";

    // -------------------------------------------------------------------------
    // RowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void RowCount_ZeroForEmptyDoc()
    {
        var doc = CsvDocument.Load("name,dept\n");
        Assert.Equal(0, doc.RowCount);
    }

    [Fact]
    public void RowCount_ThreeForThreeRows()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void RowCount_AfterAddRow_Increases()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.AddRow(new[] { "Dave", "HR", "77" });
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void RowCount_AfterRemoveRow_Decreases()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.RemoveRow(0);
        Assert.Equal(2, doc.RowCount);
    }

    [Fact]
    public void RowCount_ConsistentAfterMutations()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.AddRow(new[] { "Dave", "HR", "77" });
        doc.RemoveRow(0);
        Assert.Equal(3, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_RowCount_CorrectForEngDept()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);
    }

    [Fact]
    public void Filter_NonMatching_RowCountZero()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var none = doc.Filter(r => r.GetValue("dept") == "Marketing");
        Assert.Equal(0, none.RowCount);
    }

    [Fact]
    public void Filter_AfterAddRow_IncludesNewRow()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.AddRow(new[] { "Dave", "Eng", "70" });
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(3, eng.RowCount);
    }

    // -------------------------------------------------------------------------
    // AddRow with GetColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_ThenGetColumn_ContainsNewValue()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.AddRow(new[] { "Dave", "HR", "77" });
        var names = doc.GetColumn("name");
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void AddRow_Multiple_ThenFilter()
    {
        var doc = CsvDocument.Load("name,dept\n");
        doc.AddRow(new[] { "Alice", "Eng" });
        doc.AddRow(new[] { "Bob", "Finance" });
        doc.AddRow(new[] { "Carol", "Eng" });
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);
    }

    // -------------------------------------------------------------------------
    // RemoveRow with GetColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_ThenGetColumn_DoesNotContainRemoved()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        // Alice is row 0
        doc.RemoveRow(0);
        var names = doc.GetColumn("name");
        Assert.DoesNotContain("Alice", names);
    }

    [Fact]
    public void RemoveRow_PreservesHeaders()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.RemoveRow(0);
        Assert.Contains("name", doc.Headers);
        Assert.Contains("dept", doc.Headers);
    }

    [Fact]
    public void RemoveRow_ThenFilter_OnlyRemainingRows()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.RemoveRow(1); // Remove Bob
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->AddRow->RemoveRow->GetColumn->ToCsv->Load verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterAddRemoveGetColumnToCsvLoad_Verify()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal(3, doc.RowCount);

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);

        // AddRow to original
        doc.AddRow(new[] { "Dave", "Eng", "70" });
        Assert.Equal(4, doc.RowCount);

        // RemoveRow (Bob at index 1)
        doc.RemoveRow(1);
        Assert.Equal(3, doc.RowCount);
        Assert.DoesNotContain("Bob", doc.GetColumn("name"));

        // GetColumn
        var depts = doc.GetColumn("dept");
        Assert.Equal(3, depts.Count);

        // ToCsv -> Load
        var csv = doc.ToCsv();
        var loaded = CsvDocument.Load(csv);
        Assert.Equal(3, loaded.RowCount);
        Assert.DoesNotContain("Bob", loaded.GetColumn("name"));
        Assert.Contains("Dave", loaded.GetColumn("name"));
    }
}
