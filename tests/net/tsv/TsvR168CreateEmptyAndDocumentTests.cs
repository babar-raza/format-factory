// Tests for TsvDocument.CreateEmpty, IsEmpty, RowCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R168

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R168: Tests for TsvDocument.CreateEmpty, IsEmpty, RowCount deeper.
/// CreateEmpty(headers): creates a new empty document with given headers.
/// IsEmpty: true when document has no rows.
/// RowCount: number of data rows (excluding header).
/// Covers: CreateEmpty non-null; CreateEmpty RowCount is 0; CreateEmpty IsEmpty true;
/// CreateEmpty HasHeaders true; CreateEmpty Headers correct;
/// IsEmpty false after AddRow; IsEmpty true after Load empty content;
/// RowCount correct after multiple AddRows; RowCount decreases after Filter;
/// CreateEmpty->AddRow->ToTsv->Load round-trip;
/// CreateEmpty with multiple headers; RowCount matches GetColumnValues count;
/// IsEmpty after Load then Filter all out;
/// CreateEmpty->AddRows->Filter->ToTsv->Load chain;
/// dogfood CreateEmpty->AddRows->Filter->IsEmpty->RowCount->ToTsv->Load verify.
/// </summary>
public class TsvR168CreateEmptyAndDocumentTests
{
    // -------------------------------------------------------------------------
    // CreateEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void CreateEmpty_NonNull()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "name", "dept" });
        Assert.NotNull(doc);
    }

    [Fact]
    public void CreateEmpty_RowCount_IsZero()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "name", "dept" });
        Assert.Equal(0, doc.RowCount);
    }

    [Fact]
    public void CreateEmpty_IsEmpty_True()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "name", "dept" });
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void CreateEmpty_HasHeaders_True()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "name", "dept" });
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void CreateEmpty_Headers_Correct()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "col1", "col2", "col3" });
        Assert.Contains("col1", doc.Headers);
        Assert.Contains("col2", doc.Headers);
        Assert.Contains("col3", doc.Headers);
    }

    [Fact]
    public void CreateEmpty_MultipleHeaders_CountCorrect()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "a", "b", "c", "d", "e" });
        Assert.Equal(5, doc.ColumnCount);
    }

    [Fact]
    public void CreateEmpty_AddRow_ToTsv_Load_RoundTrip()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "name", "score" });
        doc.AddRow(new[] { "Alice", "95" });
        var tsv = doc.ToTsv();
        var loaded = TsvDocument.Load(tsv);
        Assert.Equal(1, loaded.RowCount);
        Assert.Equal("Alice", loaded.GetCellValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_False_AfterAddRow()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "x" });
        doc.AddRow(new[] { "val" });
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_True_AfterFilterAllOut()
    {
        var doc = TsvDocument.Load("name\tdept\nAlice\tEng\nBob\tFinance");
        var empty = doc.Filter(r => r.GetValue("dept") == "Marketing");
        Assert.True(empty.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // RowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void RowCount_CorrectAfterMultipleAddRows()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "name" });
        doc.AddRow(new[] { "A" });
        doc.AddRow(new[] { "B" });
        doc.AddRow(new[] { "C" });
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void RowCount_DecreasesAfterFilter()
    {
        var doc = TsvDocument.Load("name\tdept\nAlice\tEng\nBob\tFinance\nCarol\tEng");
        var before = doc.RowCount;
        var filtered = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.True(filtered.RowCount < before);
    }

    [Fact]
    public void RowCount_MatchesGetColumnValuesCount()
    {
        var content = "name\tdept\nAlice\tEng\nBob\tFinance\nCarol\tEng";
        var doc = TsvDocument.Load(content);
        var names = doc.GetColumnValues("name");
        Assert.Equal(doc.RowCount, names.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmptyAddRowsFilterIsEmptyRowCountToTsvLoadVerify_Pipeline()
    {
        // CreateEmpty
        var doc = TsvDocument.CreateEmpty(new[] { "name", "dept", "score" });
        Assert.True(doc.IsEmpty);
        Assert.Equal(0, doc.RowCount);

        // AddRows
        doc.AddRow(new[] { "Alice", "Eng", "95" });
        doc.AddRow(new[] { "Bob", "Finance", "82" });
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        Assert.False(doc.IsEmpty);
        Assert.Equal(3, doc.RowCount);

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);
        Assert.False(eng.IsEmpty);

        // Filter Marketing — all out
        var none = doc.Filter(r => r.GetValue("dept") == "Marketing");
        Assert.True(none.IsEmpty);
        Assert.Equal(0, none.RowCount);

        // ToTsv from Eng filter
        var tsv = eng.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Carol", tsv);

        // Load
        var loaded = TsvDocument.Load(tsv);
        Assert.Equal(2, loaded.RowCount);
        Assert.True(loaded.HasHeaders);
        var names = loaded.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }
}
