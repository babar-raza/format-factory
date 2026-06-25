// Tests for CsvDocument mutation counts: RowCount/ColumnCount after AddRow, Filter, SetCell.
// Sprint: FORMAT-FACTORY-CSV-DOCUMENT-R123-20260626
// Ledger: R123-GOVERNED-DOTNET-CSV-MUTATIONCOUNT-001

using System.Linq;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R123: CsvDocument RowCount and ColumnCount are consistent after mutations.
/// AddRow increases RowCount by 1. Filter produces a document with RowCount = matching count.
/// SetCell does not change RowCount or ColumnCount. Multi-mutation pipeline stays consistent.
/// </summary>
public class CsvR123MutationCountTests
{
    private static CsvDocument BuildDoc() =>
        CsvDocument.Load(
            "Name,Department,Score\n" +
            "Alice,Engineering,92\n" +
            "Bob,Marketing,78\n" +
            "Carol,Engineering,88\n" +
            "Dave,Finance,65\n",
            hasHeaders: true);

    // ---- RowCount after AddRow ----

    [Fact]
    public void AddRow_IncreasesRowCountByOne()
    {
        var doc = BuildDoc();
        var before = doc.RowCount;
        doc.AddRow(new[] { "Eve", "Legal", "91" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_Twice_RowCountIncreasedByTwo()
    {
        var doc = BuildDoc();
        var before = doc.RowCount;
        doc.AddRow(new[] { "Eve",   "Legal",   "91" });
        doc.AddRow(new[] { "Frank", "Finance", "73" });
        Assert.Equal(before + 2, doc.RowCount);
    }

    // ---- RowCount after Filter ----

    [Fact]
    public void Filter_MatchingTwoOfFour_RowCountIsTwo()
    {
        var doc = BuildDoc();
        var filtered = doc.Filter(row => row[1] == "Engineering");
        Assert.Equal(2, filtered.RowCount);
    }

    [Fact]
    public void Filter_NoMatch_RowCountIsZero()
    {
        var doc = BuildDoc();
        var filtered = doc.Filter(row => row[0] == "Nobody");
        Assert.Equal(0, filtered.RowCount);
    }

    [Fact]
    public void Filter_AllMatch_RowCountSameAsOriginal()
    {
        var doc = BuildDoc();
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.RowCount, filtered.RowCount);
    }

    // ---- ColumnCount unchanged after SetCell and AddRow ----

    [Fact]
    public void SetCell_ColumnCountUnchanged()
    {
        var doc = BuildDoc();
        var before = doc.ColumnCount;
        doc.SetCell(0, 0, "Updated");
        Assert.Equal(before, doc.ColumnCount);
    }

    [Fact]
    public void AddRow_ColumnCountUnchanged()
    {
        var doc = BuildDoc();
        var before = doc.ColumnCount;
        doc.AddRow(new[] { "Eve", "Legal", "91" });
        Assert.Equal(before, doc.ColumnCount);
    }

    // ---- ColumnCount from hasHeaders=false ----

    [Fact]
    public void ColumnCount_HasHeadersFalse_FromFirstRow()
    {
        var doc = CsvDocument.Load("A,B,C,D\n1,2,3,4\n", hasHeaders: false);
        Assert.Equal(4, doc.ColumnCount);
    }

    // ---- IsEmpty after RemoveRow ----

    [Fact]
    public void IsEmpty_AfterRemoveAllRows_IsTrue()
    {
        var doc = CsvDocument.Load("H1,H2\ndata1,data2\n", hasHeaders: true);
        doc.RemoveRow(0);
        Assert.True(doc.IsEmpty);
    }

    // ---- Dogfood: build-up pipeline ----

    [Fact]
    public void DogfoodPipeline_AddFilterCount_AllConsistent()
    {
        var doc = BuildDoc();
        Assert.Equal(4, doc.RowCount);
        Assert.Equal(3, doc.ColumnCount);

        // Add engineering row
        doc.AddRow(new[] { "Eve", "Engineering", "95" });
        Assert.Equal(5, doc.RowCount);

        // Filter for Engineering
        var engOnly = doc.Filter(row => row[1] == "Engineering");
        Assert.Equal(3, engOnly.RowCount);   // Alice + Carol + Eve
        Assert.Equal(3, engOnly.ColumnCount);// Headers preserved

        // Set a cell in filtered doc
        engOnly.SetCell(0, 2, "99");
        Assert.Equal(3, engOnly.RowCount);
        Assert.Equal(3, engOnly.ColumnCount);

        // Verify mutation
        Assert.Equal("99", engOnly.Rows[0][2]);
    }
}
