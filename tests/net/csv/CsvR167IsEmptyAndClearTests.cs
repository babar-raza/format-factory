// Tests for CsvDocument.IsEmpty, Clear, RemoveRow, CreateEmpty deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R167

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R167: Tests for CsvDocument.IsEmpty, Clear, RemoveRow, CreateEmpty.
/// IsEmpty: true when document has no rows.
/// Clear(): removes all rows from the document (preserves headers).
/// RemoveRow(index): removes a specific row by index.
/// CreateEmpty(headers): creates a new empty document with given headers.
/// Covers: IsEmpty true for empty doc; IsEmpty false after AddRow;
/// IsEmpty true after Clear; Clear sets RowCount to 0;
/// Clear preserves Headers; Clear->AddRow works after clear;
/// RemoveRow decreases RowCount; RemoveRow correct row removed;
/// RemoveRow leaves other rows intact; RemoveRow first row works;
/// CreateEmpty non-null; CreateEmpty RowCount is 0;
/// CreateEmpty HasHeaders true; CreateEmpty Headers correct;
/// CreateEmpty->AddRow->ToCsv works; IsEmpty after RemoveRow last row;
/// dogfood CreateEmpty->AddRows->RemoveRow->Clear->AddRow->ToCsv->Load verify.
/// </summary>
public class CsvR167IsEmptyAndClearTests
{
    private const string ThreeRowCsv =
        "name,dept,score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88";

    // -------------------------------------------------------------------------
    // IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_True_ForCreatedEmptyDoc()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "name", "dept" });
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_False_AfterAddRow()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "name", "dept" });
        doc.AddRow(new[] { "Alice", "Eng" });
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_False_AfterLoad()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_True_AfterClear()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.Clear();
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // Clear
    // -------------------------------------------------------------------------

    [Fact]
    public void Clear_SetsRowCountToZero()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.Clear();
        Assert.Equal(0, doc.RowCount);
    }

    [Fact]
    public void Clear_PreservesHeaders()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.Clear();
        Assert.True(doc.HasHeaders);
        Assert.Contains("name", doc.Headers);
    }

    [Fact]
    public void Clear_AddRowAfterClear_Works()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.Clear();
        doc.AddRow(new[] { "Dave", "HR", "76" });
        Assert.Equal(1, doc.RowCount);
        Assert.Equal("Dave", doc.GetCellValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_DecreasesRowCount()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.RemoveRow(1);
        Assert.Equal(2, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_CorrectRowRemoved()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.RemoveRow(1); // Remove Bob
        var names = doc.GetColumn("name");
        Assert.DoesNotContain("Bob", names);
    }

    [Fact]
    public void RemoveRow_OtherRowsIntact()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.RemoveRow(1); // Remove Bob
        var names = doc.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void RemoveRow_FirstRow_Works()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.RemoveRow(0); // Remove Alice
        Assert.Equal(2, doc.RowCount);
        var names = doc.GetColumn("name");
        Assert.DoesNotContain("Alice", names);
    }

    [Fact]
    public void RemoveRow_AllRows_IsEmpty()
    {
        var doc = CsvDocument.Load("a,b\nX,Y");
        doc.RemoveRow(0);
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // CreateEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void CreateEmpty_NonNull()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "id", "value" });
        Assert.NotNull(doc);
    }

    [Fact]
    public void CreateEmpty_RowCount_IsZero()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "id", "value" });
        Assert.Equal(0, doc.RowCount);
    }

    [Fact]
    public void CreateEmpty_HasHeaders_True()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "id", "value" });
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void CreateEmpty_Headers_Correct()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "col1", "col2", "col3" });
        Assert.Contains("col1", doc.Headers);
        Assert.Contains("col2", doc.Headers);
        Assert.Contains("col3", doc.Headers);
    }

    [Fact]
    public void CreateEmpty_AddRow_ToCsv_Works()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "name", "score" });
        doc.AddRow(new[] { "Alice", "95" });
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("name", csv);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmptyAddRowsRemoveRowClearAddRowToCsvLoadVerify_Pipeline()
    {
        // CreateEmpty
        var doc = CsvDocument.CreateEmpty(new[] { "name", "dept", "score" });
        Assert.True(doc.IsEmpty);
        Assert.True(doc.HasHeaders);

        // AddRows
        doc.AddRow(new[] { "Alice", "Eng", "95" });
        doc.AddRow(new[] { "Bob", "Finance", "82" });
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        Assert.Equal(3, doc.RowCount);
        Assert.False(doc.IsEmpty);

        // RemoveRow (Bob)
        doc.RemoveRow(1);
        Assert.Equal(2, doc.RowCount);
        Assert.DoesNotContain("Bob", doc.GetColumn("name"));

        // Clear
        doc.Clear();
        Assert.Equal(0, doc.RowCount);
        Assert.True(doc.IsEmpty);
        Assert.True(doc.HasHeaders); // headers preserved

        // AddRow after Clear
        doc.AddRow(new[] { "Dave", "HR", "76" });
        Assert.Equal(1, doc.RowCount);

        // ToCsv
        var csv = doc.ToCsv();
        Assert.Contains("Dave", csv);
        Assert.Contains("name", csv);

        // Load
        var loaded = CsvDocument.Load(csv);
        Assert.Equal(1, loaded.RowCount);
        Assert.Equal("Dave", loaded.GetCellValue(0, "name"));
    }
}
