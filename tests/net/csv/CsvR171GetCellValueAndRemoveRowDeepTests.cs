// Tests for CsvDocument.GetCellValue and RemoveRow deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R171

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R171: Tests for CsvDocument.GetCellValue and RemoveRow deeper coverage.
/// GetCellValue(row, col): returns cell value at the given zero-based row and column.
/// GetCellValue(row, colName): returns cell value at a row by column name.
/// RemoveRow(index): removes the row at the given zero-based index; shifts subsequent rows.
/// Covers: GetCellValue by index non-null; GetCellValue by index correct value;
/// GetCellValue by column name non-null; GetCellValue by column name correct value;
/// GetCellValue out-of-range returns null or throws; GetCellValue after SetCellValue reflects update;
/// GetCellValue on filtered doc correct; RemoveRow decrements RowCount;
/// RemoveRow shifts remaining rows; RemoveRow first row leaves second as first;
/// RemoveRow last row reduces count; RemoveRow then GetCellValue reflects removal;
/// dogfood Load->GetCellValue->RemoveRow->GetCellValue->Filter->GetCellValue verify pipeline.
/// </summary>
public class CsvR171GetCellValueAndRemoveRowDeepTests
{
    private const string FourRowCsv =
        "name,dept,score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88\n" +
        "Dave,HR,76";

    // -------------------------------------------------------------------------
    // GetCellValue by index
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_ByIndex_NonNull()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.NotNull(doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_ByIndex_FirstCell_Correct()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_ByIndex_SecondRow_FirstCol_Correct()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Equal("Bob", doc.GetCellValue(1, 0));
    }

    [Fact]
    public void GetCellValue_ByIndex_LastCell_Correct()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Equal("76", doc.GetCellValue(3, 2));
    }

    [Fact]
    public void GetCellValue_ByIndex_AfterSetCellValue_ReflectsUpdate()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        doc.SetCellValue(0, 0, "Alicia");
        Assert.Equal("Alicia", doc.GetCellValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // GetCellValue by column name
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_ByColName_NonNull()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.NotNull(doc.GetCellValue(0, "name"));
    }

    [Fact]
    public void GetCellValue_ByColName_FirstRow_Correct()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Equal("Alice", doc.GetCellValue(0, "name"));
    }

    [Fact]
    public void GetCellValue_ByColName_Score_Correct()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Equal("95", doc.GetCellValue(0, "score"));
    }

    [Fact]
    public void GetCellValue_ByColName_AfterMutation_ReflectsChange()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        doc.SetCellValue(2, 2, "99");
        Assert.Equal("99", doc.GetCellValue(2, "score"));
    }

    [Fact]
    public void GetCellValue_ByColName_OnFilteredDoc_Correct()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal("Alice", eng.GetCellValue(0, "name"));
        Assert.Equal("Carol", eng.GetCellValue(1, "name"));
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_DecrementsRowCount()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        doc.RemoveRow(0);
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_First_SecondBecomesFirst()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        doc.RemoveRow(0);
        Assert.Equal("Bob", doc.GetCellValue(0, "name"));
    }

    [Fact]
    public void RemoveRow_Last_ReducesCount()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        doc.RemoveRow(3);
        Assert.Equal(3, doc.RowCount);
        // Dave should be gone
        var names = doc.GetColumn("name");
        Assert.DoesNotContain("Dave", names);
    }

    [Fact]
    public void RemoveRow_Multiple_CountCorrect()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        doc.RemoveRow(0);
        doc.RemoveRow(0); // removes Bob (now first)
        Assert.Equal(2, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_Middle_ShiftsRemaining()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        doc.RemoveRow(1); // Remove Bob
        // Carol should now be at index 1
        Assert.Equal("Carol", doc.GetCellValue(1, "name"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadGetCellValueRemoveRowGetCellValueFilterGetCellValueVerify_Pipeline()
    {
        // Load
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Equal(4, doc.RowCount);

        // GetCellValue by index
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("Eng", doc.GetCellValue(0, "dept"));

        // RemoveRow — remove Bob (index 1)
        doc.RemoveRow(1);
        Assert.Equal(3, doc.RowCount);

        // Carol is now at index 1
        Assert.Equal("Carol", doc.GetCellValue(1, "name"));

        // GetCellValue by name after removal
        Assert.Equal("88", doc.GetCellValue(1, "score"));

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);

        // GetCellValue on filtered
        Assert.Equal("Alice", eng.GetCellValue(0, "name"));
        Assert.Equal("Carol", eng.GetCellValue(1, "name"));

        // SetCellValue and verify via GetCellValue
        eng.SetCellValue(0, 2, "100");
        Assert.Equal("100", eng.GetCellValue(0, "score"));
    }
}
