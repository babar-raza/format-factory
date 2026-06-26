// Tests for TsvDocument.GetCellValue by index and name, SetCellValue mutation.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R164

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R164: Tests for TsvDocument.GetCellValue, SetCellValue, AddRow mutation.
/// GetCellValue(row, col): returns cell value by row and column index.
/// GetCellValue(row, colName): returns cell value by column header name.
/// SetCellValue(row, col, value): mutates a specific cell.
/// AddRow(values): appends a new row to the document.
/// Covers: GetCellValue by index correct; GetCellValue by name correct;
/// GetCellValue all cells accessible; SetCellValue reflects in GetCellValue;
/// SetCellValue reflects in ToTsv; SetCellValue reflects in GetColumnValues;
/// AddRow increases RowCount; AddRow values accessible by GetCellValue;
/// AddRow->ToTsv contains new row; AddRow->Filter includes new row;
/// SetCellValue->Filter reflects mutation; GetCellValue out-of-range returns null;
/// Multiple AddRow calls accumulate;
/// dogfood Load->GetCellValues->SetCellValue->AddRow->Filter->ToTsv->Load verify.
/// </summary>
public class TsvR164GetCellAndMutateTests
{
    private const string ThreeRowTsv =
        "name\tdept\tscore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88";

    // -------------------------------------------------------------------------
    // GetCellValue by index
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_ByIndex_Row0Col0_Correct()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_ByIndex_Row1Col1_Correct()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("Finance", doc.GetCellValue(1, 1));
    }

    [Fact]
    public void GetCellValue_ByIndex_Row2Col2_Correct()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("88", doc.GetCellValue(2, 2));
    }

    [Fact]
    public void GetCellValue_ByIndex_AllCells_NonNull()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        for (var r = 0; r < doc.RowCount; r++)
            for (var c = 0; c < doc.ColumnCount; c++)
                Assert.NotNull(doc.GetCellValue(r, c));
    }

    // -------------------------------------------------------------------------
    // GetCellValue by column name
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_ByName_Row0Name_Correct()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("Alice", doc.GetCellValue(0, "name"));
    }

    [Fact]
    public void GetCellValue_ByName_Row1Dept_Correct()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal("Finance", doc.GetCellValue(1, "dept"));
    }

    [Fact]
    public void GetCellValue_ByName_MissingColumn_NullOrEmpty()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var val = doc.GetCellValue(0, "nonexistent");
        Assert.True(val == null || val == string.Empty);
    }

    // -------------------------------------------------------------------------
    // SetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_ReflectsInGetCellValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, 0, "Alicia");
        Assert.Equal("Alicia", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCellValue_ReflectsInToTsv()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(1, 0, "Robert");
        var tsv = doc.ToTsv();
        Assert.Contains("Robert", tsv);
        Assert.DoesNotContain("Bob", tsv);
    }

    [Fact]
    public void SetCellValue_ReflectsInGetColumnValues()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, 1, "Marketing");
        var depts = doc.GetColumnValues("dept");
        Assert.Contains("Marketing", depts);
    }

    [Fact]
    public void SetCellValue_ReflectsInFilter()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(1, 1, "Eng");
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(3, eng.RowCount);
    }

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncreasesRowCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.AddRow(new[] { "Dave", "HR", "76" });
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void AddRow_ValuesAccessibleByGetCellValue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.AddRow(new[] { "Eve", "Legal", "91" });
        Assert.Equal("Eve", doc.GetCellValue(3, 0));
    }

    [Fact]
    public void AddRow_ToTsv_ContainsNewRow()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.AddRow(new[] { "Frank", "Sales", "79" });
        var tsv = doc.ToTsv();
        Assert.Contains("Frank", tsv);
    }

    [Fact]
    public void AddRow_Filter_IncludesNewRow()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.AddRow(new[] { "Grace", "Eng", "93" });
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(3, eng.RowCount);
    }

    [Fact]
    public void MultipleAddRows_Accumulate()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.AddRow(new[] { "H", "HR", "70" });
        doc.AddRow(new[] { "I", "IT", "85" });
        doc.AddRow(new[] { "J", "Eng", "92" });
        Assert.Equal(6, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadGetCellValuesSetCellAddRowFilterToTsvLoadVerify_Pipeline()
    {
        // Load
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(3, doc.RowCount);

        // GetCellValues
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("Finance", doc.GetCellValue(1, "dept"));

        // SetCellValue
        doc.SetCellValue(1, 0, "Bobby");
        Assert.Equal("Bobby", doc.GetCellValue(1, 0));

        // AddRow
        doc.AddRow(new[] { "Dave", "Eng", "90" });
        Assert.Equal(4, doc.RowCount);

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(3, eng.RowCount); // Alice, Carol, Dave

        // ToTsv
        var tsv = eng.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Dave", tsv);

        // Load round-trip
        var reloaded = TsvDocument.Load(tsv);
        Assert.Equal(3, reloaded.RowCount);
        var names = reloaded.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Dave", names);
    }
}
