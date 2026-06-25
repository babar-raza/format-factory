// Tests for TsvDocument.Filter(predicate) with various predicates and chaining.
// Sprint: FORMAT-FACTORY-TSV-DOCUMENT-R122-20260626
// Ledger: R122-GOVERNED-DOTNET-TSV-FILTER-001

using System.Linq;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R122: TsvDocument.Filter(predicate) returns a new document with only matching rows.
/// Headers are preserved on the filtered document. Multiple predicates can be chained.
/// Filter result RowCount reflects the number of matching rows. IsEmpty after
/// filtering to zero rows returns true.
/// </summary>
public class TsvR122FilterPredicateTests
{
    private static TsvDocument BuildDoc()
    {
        var content =
            "Name\tDepartment\tScore\n" +
            "Alice\tEngineering\t92\n" +
            "Bob\tMarketing\t78\n" +
            "Carol\tEngineering\t88\n" +
            "Dave\tFinance\t65\n" +
            "Eve\tEngineering\t95\n";
        return TsvDocument.Load(content, hasHeaders: true);
    }

    // ---- Basic filtering ----

    [Fact]
    public void Filter_MatchingThreeRows_RowCountIsThree()
    {
        var filtered = BuildDoc().Filter(row => row[1] == "Engineering");
        Assert.Equal(3, filtered.RowCount);
    }

    [Fact]
    public void Filter_NoMatch_RowCountIsZero()
    {
        var filtered = BuildDoc().Filter(row => row[0] == "Nobody");
        Assert.Equal(0, filtered.RowCount);
    }

    [Fact]
    public void Filter_AllMatch_RowCountSameAsOriginal()
    {
        var doc = BuildDoc();
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.RowCount, filtered.RowCount);
    }

    // ---- Predicate on specific column ----

    [Fact]
    public void Filter_ScoreAbove80_ReturnsHighScorers()
    {
        var filtered = BuildDoc().Filter(row =>
            int.TryParse(row[2], out var score) && score > 80);
        // Alice(92), Carol(88), Eve(95) = 3
        Assert.Equal(3, filtered.RowCount);
    }

    [Fact]
    public void Filter_ScoreBelow70_ReturnsLowScorers()
    {
        var filtered = BuildDoc().Filter(row =>
            int.TryParse(row[2], out var score) && score < 70);
        // Dave(65) = 1
        Assert.Equal(1, filtered.RowCount);
        Assert.Equal("Dave", filtered.Rows[0][0]);
    }

    // ---- Headers preserved on filtered document ----

    [Fact]
    public void Filter_HeadersPreservedInResult()
    {
        var doc = BuildDoc();
        var filtered = doc.Filter(row => row[1] == "Engineering");
        Assert.Equal(doc.Headers!, filtered.Headers!);
    }

    // ---- Chained filters ----

    [Fact]
    public void Filter_Chained_EngineeringAndHighScore()
    {
        var filtered = BuildDoc()
            .Filter(row => row[1] == "Engineering")
            .Filter(row => int.TryParse(row[2], out var s) && s >= 90);
        // Alice(92) + Eve(95) = 2
        Assert.Equal(2, filtered.RowCount);
    }

    // ---- IsEmpty after total filter ----

    [Fact]
    public void Filter_NoMatch_IsEmptyTrue()
    {
        var filtered = BuildDoc().Filter(row => row[0] == "Nobody");
        Assert.True(filtered.IsEmpty);
    }

    // ---- ColumnCount preserved ----

    [Fact]
    public void Filter_ColumnCountPreserved()
    {
        var doc = BuildDoc();
        var filtered = doc.Filter(row => row[1] == "Engineering");
        Assert.Equal(doc.ColumnCount, filtered.ColumnCount);
    }

    // ---- Dogfood: HR report pipeline ----

    [Fact]
    public void DogfoodPipeline_HrReport_FilteredDataCorrect()
    {
        var content =
            "EmployeeId\tName\tDepartment\tSalary\tRating\n" +
            "E001\tAlice Johnson\tEngineering\t95000\t5\n" +
            "E002\tBob Smith\tMarketing\t72000\t3\n" +
            "E003\tCarol Lee\tFinance\t88000\t4\n" +
            "E004\tDave Brown\tEngineering\t105000\t5\n" +
            "E005\tEve Davis\tMarketing\t68000\t2\n";
        var doc = TsvDocument.Load(content, hasHeaders: true);

        // Filter: Engineering with Rating >= 4
        var topEngineers = doc
            .Filter(row => row[2] == "Engineering")
            .Filter(row => int.TryParse(row[4], out var r) && r >= 4);

        Assert.Equal(2, topEngineers.RowCount);

        var names = topEngineers.Rows.Select(r => r[1]).ToList();
        Assert.Contains("Alice Johnson", names);
        Assert.Contains("Dave Brown",   names);

        // Verify headers preserved
        Assert.Equal("EmployeeId", topEngineers.Headers![0]);
        Assert.Equal("Rating",     topEngineers.Headers![4]);
    }
}
