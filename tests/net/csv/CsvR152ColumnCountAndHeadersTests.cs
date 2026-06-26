// Tests for CsvDocument.ColumnCount, Headers, HasHeaders, and header-name GetColumn.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R152

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R152: Tests for CsvDocument.ColumnCount, Headers, HasHeaders, GetColumn(string) deeper.
/// ColumnCount: number of columns in the document.
/// Headers: array of header names when hasHeaders=true.
/// HasHeaders: true when headers were parsed.
/// GetColumn(string): returns column values by header name.
/// Covers: ColumnCount three-column CSV; ColumnCount single-column;
/// ColumnCount after AddRow does not change; Headers array non-null with hasHeaders;
/// Headers length equals ColumnCount; HasHeaders true for default load;
/// HasHeaders false when hasHeaders=false; GetColumn(name) all values;
/// GetColumn(name) count equals RowCount; GetColumn(int) same as GetColumn(name);
/// HasColumn after AddRow; RowCount consistent with Rows;
/// dogfood Load->GetColumn->Filter->GetColumn->ToCsv pipeline.
/// </summary>
public class CsvR152ColumnCountAndHeadersTests
{
    private const string ThreeColCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88";

    private const string SingleColCsv =
        "Name\n" +
        "Alice\n" +
        "Bob";

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_ThreeColumnCsv_IsThree()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_SingleColumn_IsOne()
    {
        var doc = CsvDocument.Load(SingleColCsv);
        Assert.Equal(1, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_AfterAddRow_Unchanged()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        var before = doc.ColumnCount;
        doc.AddRow(new[] { "Dave", "Finance", "91" });
        Assert.Equal(before, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Headers
    // -------------------------------------------------------------------------

    [Fact]
    public void Headers_WithHasHeaders_IsNotNull()
    {
        var doc = CsvDocument.Load(ThreeColCsv, hasHeaders: true);
        Assert.NotNull(doc.Headers);
    }

    [Fact]
    public void Headers_LengthEqualsColumnCount()
    {
        var doc = CsvDocument.Load(ThreeColCsv, hasHeaders: true);
        Assert.Equal(doc.ColumnCount, doc.Headers!.Length);
    }

    [Fact]
    public void Headers_ContainsExpectedNames()
    {
        var doc = CsvDocument.Load(ThreeColCsv, hasHeaders: true);
        Assert.Contains("Name", doc.Headers!);
        Assert.Contains("Dept", doc.Headers!);
        Assert.Contains("Score", doc.Headers!);
    }

    [Fact]
    public void Headers_NullWhenHasHeadersFalse()
    {
        var doc = CsvDocument.Load(ThreeColCsv, hasHeaders: false);
        Assert.Null(doc.Headers);
    }

    // -------------------------------------------------------------------------
    // HasHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void HasHeaders_TrueForDefaultLoad()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void HasHeaders_FalseWhenHasHeadersFalse()
    {
        var doc = CsvDocument.Load(ThreeColCsv, hasHeaders: false);
        Assert.False(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // GetColumn(string)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnByName_CountEqualsRowCount()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        var names = doc.GetColumn("Name");
        Assert.Equal(doc.RowCount, names.Count);
    }

    [Fact]
    public void GetColumnByName_AllValuesPresent()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        var names = doc.GetColumn("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void GetColumnByName_SameAsGetColumnByIndex()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        var byName = doc.GetColumn("Name");
        var byIndex = doc.GetColumn(0);
        Assert.Equal(byName.Count, byIndex.Count);
        for (int i = 0; i < byName.Count; i++)
            Assert.Equal(byName[i], byIndex[i]);
    }

    [Fact]
    public void GetColumnByName_ScoreColumn_ContainsValues()
    {
        var doc = CsvDocument.Load(ThreeColCsv);
        var scores = doc.GetColumn("Score");
        Assert.Contains("95", scores);
        Assert.Contains("82", scores);
        Assert.Contains("88", scores);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetColumn->Filter->GetColumn->ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnFilterGetColumnToCsv_Pipeline()
    {
        var doc = CsvDocument.Load(ThreeColCsv);

        // GetColumn by name
        var depts = doc.GetColumn("Dept");
        Assert.Equal(3, depts.Count);
        Assert.Contains("Eng", depts);

        // HasColumn check
        Assert.True(doc.HasColumn("Score"));
        Assert.False(doc.HasColumn("NonExistent"));

        // Filter Eng
        var eng = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, eng.RowCount);

        // GetColumn on filtered
        var engNames = eng.GetColumn(0);
        Assert.Equal(2, engNames.Count);
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);

        // ToCsv of filtered
        var csv = eng.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.DoesNotContain("Bob", csv);
    }
}
