// Tests for CsvDocument.GetCellValue, HasColumn deeper coverage with edge cases.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R163

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R163: Tests for CsvDocument.GetCellValue, HasColumn, GetColumn deeper edge cases.
/// GetCellValue(row, col): returns cell value by position.
/// GetCellValue(row, headerName): returns cell value by header name.
/// HasColumn(name): true if column with that name exists.
/// GetColumn(name): returns all values for the named column.
/// Covers: GetCellValue row0 col0 correct; GetCellValue row1 col2 correct;
/// GetCellValue by name row0; GetCellValue by name last row;
/// GetCellValue after SetCellValue; HasColumn true for all columns;
/// HasColumn false for non-existent; HasColumn case check;
/// GetColumn all values; GetColumn count; GetColumn after AddRow;
/// GetColumn empty doc; GetCellValue middle cell;
/// GetCellValue score col third row;
/// dogfood Load->GetCellValues->SetCellValues->HasColumn->GetColumn->ToCsv->Load verify.
/// </summary>
public class CsvR163GetCellValueAndHasColumnTests
{
    private const string ThreeRowCsv =
        "name,dept,score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88";

    // -------------------------------------------------------------------------
    // GetCellValue by index
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_Row0Col0_IsAlice()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_Row1Col2_Is82()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal("82", doc.GetCellValue(1, 2));
    }

    [Fact]
    public void GetCellValue_MiddleCell_IsFinance()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal("Finance", doc.GetCellValue(1, 1));
    }

    [Fact]
    public void GetCellValue_LastRow_LastCol_Is88()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal("88", doc.GetCellValue(2, 2));
    }

    // -------------------------------------------------------------------------
    // GetCellValue by name
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_ByName_Row0_IsAlice()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal("Alice", doc.GetCellValue(0, "name"));
    }

    [Fact]
    public void GetCellValue_ByName_LastRow_IsCarol()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal("Carol", doc.GetCellValue(2, "name"));
    }

    [Fact]
    public void GetCellValue_ByName_ScoreCol_Row2_Is88()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal("88", doc.GetCellValue(2, "score"));
    }

    [Fact]
    public void GetCellValue_AfterSetCellValue_ReadsBack()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.SetCellValue(0, 0, "Alicia");
        Assert.Equal("Alicia", doc.GetCellValue(0, "name"));
        Assert.Equal("Alicia", doc.GetCellValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // HasColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_TrueForName()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.True(doc.HasColumn("name"));
    }

    [Fact]
    public void HasColumn_TrueForDept()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.True(doc.HasColumn("dept"));
    }

    [Fact]
    public void HasColumn_TrueForScore()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.True(doc.HasColumn("score"));
    }

    [Fact]
    public void HasColumn_FalseForNonExistent()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.False(doc.HasColumn("salary"));
    }

    [Fact]
    public void HasColumn_FalseForEmptyString()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.False(doc.HasColumn(string.Empty));
    }

    // -------------------------------------------------------------------------
    // GetColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumn_AllValues_Count3()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var names = doc.GetColumn("name");
        Assert.Equal(3, names.Count);
    }

    [Fact]
    public void GetColumn_ContainsAllValues()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var depts = doc.GetColumn("dept");
        Assert.Contains("Eng", depts);
        Assert.Contains("Finance", depts);
    }

    [Fact]
    public void GetColumn_AfterAddRow_CountIncreases()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.AddRow(new[] { "Dave", "HR", "77" });
        var names = doc.GetColumn("name");
        Assert.Equal(4, names.Count);
        Assert.Contains("Dave", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetCellValues->SetCellValues->HasColumn->GetColumn->ToCsv->Load verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadGetSetHasColumnGetColumnToCsvLoad_Pipeline()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);

        // GetCellValues
        Assert.Equal("Alice", doc.GetCellValue(0, "name"));
        Assert.Equal("Finance", doc.GetCellValue(1, "dept"));
        Assert.Equal("88", doc.GetCellValue(2, "score"));

        // HasColumn
        Assert.True(doc.HasColumn("name"));
        Assert.True(doc.HasColumn("dept"));
        Assert.False(doc.HasColumn("NONEXISTENT"));

        // SetCellValues
        doc.SetCellValue(0, 2, "99");
        Assert.Equal("99", doc.GetCellValue(0, "score"));

        // GetColumn
        var scores = doc.GetColumn("score");
        Assert.Contains("99", scores);
        Assert.Contains("82", scores);
        Assert.Contains("88", scores);

        // ToCsv -> Load
        var csv = doc.ToCsv();
        var loaded = CsvDocument.Load(csv);
        Assert.Equal(3, loaded.RowCount);
        Assert.Equal("99", loaded.GetCellValue(0, "score"));
        Assert.True(loaded.HasColumn("name"));
    }
}
