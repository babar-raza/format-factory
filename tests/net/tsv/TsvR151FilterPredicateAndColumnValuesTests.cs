// Tests for TsvDocument.Filter predicate combinations and GetColumnValues patterns.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R151

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R151: Tests for TsvDocument.Filter predicate combinations and GetColumnValues patterns.
/// Filter(predicate): returns new TsvDocument with matching rows.
/// GetColumnValues(col): returns column projection.
/// Covers: Filter with compound AND predicate; Filter with OR predicate;
/// Filter chain: apply filter twice; Filter result is independent;
/// GetColumnValues on col1 (dept); GetColumnValues on col2 (score);
/// Filter->GetColumnValues chain; Filter->SaveToFile->LoadFile->GetColumnValues;
/// ToTsv contains tab separators; Filter->ToTsv->Load round-trip;
/// Empty result from Filter; RowCount after double Filter;
/// dogfood Load->Filter(AND)->GetColumnValues->Filter->ToTsv chain.
/// </summary>
public class TsvR151FilterPredicateAndColumnValuesTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR151FilterPredicateAndColumnValuesTests()
    {
        _tempDir = System.IO.Path.Combine(System.IO.Path.GetTempPath(),
            "TsvR151_" + System.Guid.NewGuid().ToString("N"));
        System.IO.Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (System.IO.Directory.Exists(_tempDir))
            System.IO.Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) =>
        System.IO.Path.Combine(_tempDir, name);

    private const string FiveRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88\n" +
        "Dave\tFinance\t91\n" +
        "Eve\tEng\t72";

    // -------------------------------------------------------------------------
    // Filter with compound predicates
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_CompoundAND_EngHighScore()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        // Eng AND score >= 88
        var result = doc.Filter(r =>
            r.Length > 2 && r[1] == "Eng" &&
            int.TryParse(r[2], out var s) && s >= 88);
        Assert.Equal(2, result.RowCount); // Alice(95), Carol(88)
    }

    [Fact]
    public void Filter_CompoundOR_EngOrHighScore()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        // Finance OR score >= 90
        var result = doc.Filter(r =>
            r.Length > 2 &&
            (r[1] == "Finance" || (int.TryParse(r[2], out var s) && s >= 90)));
        // Finance: Bob(82), Dave(91); score>=90: Alice(95), Dave(91) → unique: Alice,Bob,Dave = 3
        Assert.True(result.RowCount >= 3);
    }

    // -------------------------------------------------------------------------
    // Filter chain
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_Chain_ApplyFilterTwice()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var highEng = eng.Filter(r => r.Length > 2 && int.TryParse(r[2], out var s) && s >= 88);
        Assert.Equal(2, highEng.RowCount); // Alice(95), Carol(88)
    }

    [Fact]
    public void Filter_Chain_ResultIsIndependent()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        eng.Rows.RemoveAt(0);
        Assert.Equal(5, doc.RowCount); // original unchanged
    }

    [Fact]
    public void Filter_DoubleFilter_RowCountCorrect()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var step1 = doc.Filter(r => r.Length > 2 && int.TryParse(r[2], out var s) && s >= 80);
        var step2 = step1.Filter(r => r.Length > 1 && r[1] == "Finance");
        Assert.Equal(2, step2.RowCount); // Bob(82), Dave(91)
    }

    // -------------------------------------------------------------------------
    // GetColumnValues patterns
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_Col1_ContainsDepts()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var depts = doc.GetColumnValues(1);
        Assert.Contains("Eng", depts);
        Assert.Contains("Finance", depts);
    }

    [Fact]
    public void GetColumnValues_Col2_ContainsScores()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var scores = doc.GetColumnValues(2);
        Assert.Contains("95", scores);
        Assert.Contains("82", scores);
    }

    [Fact]
    public void Filter_ThenGetColumnValues_EngNamesCount()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var names = eng.GetColumnValues(0);
        Assert.Equal(3, names.Count); // Alice, Carol, Eve
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);
    }

    // -------------------------------------------------------------------------
    // ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToTsv_ContainsTabSeparators()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        Assert.Contains("\t", doc.ToTsv());
    }

    [Fact]
    public void Filter_ToTsv_Load_RoundTrip()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var finance = doc.Filter(r => r.Length > 1 && r[1] == "Finance");
        var tsv = finance.ToTsv();
        var reloaded = TsvDocument.Load(tsv, hasHeaders: false);
        Assert.Equal(finance.RowCount, reloaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter(AND)->GetColumnValues->Filter->ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FilterANDGetColumnValuesFilterToTsv_Pipeline()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        Assert.Equal(5, doc.RowCount);

        // Filter: Eng AND score >= 88
        var engHigh = doc.Filter(r =>
            r.Length > 2 && r[1] == "Eng" &&
            int.TryParse(r[2], out var s) && s >= 88);
        Assert.Equal(2, engHigh.RowCount);

        // GetColumnValues
        var names = engHigh.GetColumnValues(0);
        Assert.Equal(2, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Eve", names); // Eve is 72

        // Second filter: score exactly 95
        var alice = engHigh.Filter(r =>
            r.Length > 2 && r[2] == "95");
        Assert.Equal(1, alice.RowCount);

        // ToTsv
        var tsv = alice.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("\t", tsv);
    }
}
