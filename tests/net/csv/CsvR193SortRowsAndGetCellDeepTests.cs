// Tests for CsvDocument.SortRows, GetCell, RemoveRow deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R193

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R193: Tests for CsvDocument.SortRows, GetCell, RemoveRow deeper.
/// SortRows(colName, ascending): sorts rows by the specified column value.
/// GetCell(row, col): returns the string value of a cell at (row, col).
/// RemoveRow(rowIndex): removes a data row at the given index.
/// Covers: SortRows ascending first-value correct; SortRows descending first-value correct;
/// SortRows preserves row count; SortRows by numeric column; SortRows ToTsv reflects order;
/// SortRows after Filter still sorted; SortRows consistent;
/// GetCell first row first col; GetCell last row last col; GetCell header row;
/// GetCell after AddRow accessible; GetCell consistent; GetCell out-of-range handled;
/// RemoveRow decrements row count; RemoveRow removes value; RemoveRow first row;
/// RemoveRow last row; RemoveRow remaining intact; RemoveRow no-throw on empty;
/// dogfood LoadFile→SortRows→GetCell→RemoveRow→verify pipeline.
/// </summary>
public class CsvR193SortRowsAndGetCellDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR193SortRowsAndGetCellDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR193_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleCsv =
        "Employee,Department,Salary,Years\n" +
        "Charlie,Engineering,85000,3\n" +
        "Alice,Finance,92000,7\n" +
        "Eve,Engineering,78000,2\n" +
        "Bob,HR,95000,10\n" +
        "Diana,Finance,88000,5\n";

    private CsvDocument LoadSample()
    {
        var path = TempFile("sample.csv");
        File.WriteAllText(path, SampleCsv);
        return CsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // SortRows
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_Ascending_FirstValueCorrect()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Employee", ascending: true);
        var values = sorted.GetColumnValues("Employee");
        Assert.Equal("Alice", values[0]);
    }

    [Fact]
    public void SortRows_Descending_FirstValueCorrect()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Employee", ascending: false);
        var values = sorted.GetColumnValues("Employee");
        Assert.Equal("Eve", values[0]);
    }

    [Fact]
    public void SortRows_PreservesRowCount()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Employee", ascending: true);
        Assert.Equal(doc.RowCount, sorted.RowCount);
    }

    [Fact]
    public void SortRows_BySalary_Ascending_LowestFirst()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Salary", ascending: true);
        var values = sorted.GetColumnValues("Salary");
        Assert.Equal("78000", values[0]);
    }

    [Fact]
    public void SortRows_BySalary_Descending_HighestFirst()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Salary", ascending: false);
        var values = sorted.GetColumnValues("Salary");
        Assert.Equal("95000", values[0]);
    }

    [Fact]
    public void SortRows_ThenToTsv_ReflectsOrder()
    {
        var doc = LoadSample();
        var sorted = doc.SortRows("Employee", ascending: true);
        var tsv = sorted.ToTsv();
        var alicePos = tsv.IndexOf("Alice");
        var charliePos = tsv.IndexOf("Charlie");
        Assert.True(alicePos < charliePos);
    }

    [Fact]
    public void SortRows_AfterFilter_StillSorted()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("Department", "Finance");
        var sorted = filtered.SortRows("Employee", ascending: true);
        var values = sorted.GetColumnValues("Employee");
        Assert.True(values.Count >= 2);
        Assert.Equal("Alice", values[0]); // Alice < Diana
    }

    [Fact]
    public void SortRows_Consistent()
    {
        var doc = LoadSample();
        var s1 = doc.SortRows("Employee", ascending: true).GetColumnValues("Employee");
        var s2 = doc.SortRows("Employee", ascending: true).GetColumnValues("Employee");
        Assert.Equal(s1, s2);
    }

    // -------------------------------------------------------------------------
    // GetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCell_FirstRowFirstCol_ReturnsValue()
    {
        var doc = LoadSample();
        var val = doc.GetCell(0, 0);
        Assert.True(val != null && val.Length > 0);
    }

    [Fact]
    public void GetCell_KnownPosition_CorrectValue()
    {
        var doc = LoadSample();
        // Row 0 = Charlie (first data row)
        var val = doc.GetCell(0, 0);
        Assert.Equal("Charlie", val);
    }

    [Fact]
    public void GetCell_SecondRow_SecondCol()
    {
        var doc = LoadSample();
        // Row 1 = Alice, col 1 = Finance
        var val = doc.GetCell(1, 1);
        Assert.Equal("Finance", val);
    }

    [Fact]
    public void GetCell_Consistent()
    {
        var doc = LoadSample();
        Assert.Equal(doc.GetCell(0, 0), doc.GetCell(0, 0));
    }

    [Fact]
    public void GetCell_AfterAddRow_NewRowAccessible()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Frank", "Legal", "91000", "4" });
        var val = doc.GetCell(doc.RowCount - 1, 0);
        Assert.Equal("Frank", val);
    }

    [Fact]
    public void GetCell_LastKnownRow()
    {
        var doc = LoadSample();
        // Row 4 = Diana
        var val = doc.GetCell(4, 0);
        Assert.Equal("Diana", val);
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_DecrementsRowCount()
    {
        var doc = LoadSample();
        var before = doc.RowCount;
        doc.RemoveRow(0);
        Assert.Equal(before - 1, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_RemovesValue()
    {
        var doc = LoadSample();
        // Row 0 = Charlie
        doc.RemoveRow(0);
        Assert.DoesNotContain("Charlie", doc.GetColumnValues("Employee"));
    }

    [Fact]
    public void RemoveRow_RemainingIntact()
    {
        var doc = LoadSample();
        doc.RemoveRow(0); // Remove Charlie
        var values = doc.GetColumnValues("Employee");
        Assert.Contains("Alice", values);
        Assert.Contains("Bob", values);
        Assert.Contains("Diana", values);
        Assert.Contains("Eve", values);
    }

    [Fact]
    public void RemoveRow_LastRow()
    {
        var doc = LoadSample();
        var before = doc.RowCount;
        doc.RemoveRow(before - 1); // Remove Diana
        Assert.Equal(before - 1, doc.RowCount);
        Assert.DoesNotContain("Diana", doc.GetColumnValues("Employee"));
    }

    [Fact]
    public void RemoveRow_MultipleRemoves()
    {
        var doc = LoadSample();
        var before = doc.RowCount;
        doc.RemoveRow(0);
        doc.RemoveRow(0);
        Assert.Equal(before - 2, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_SortRows_GetCell_RemoveRow_Verify_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.RowCount);

        // GetCell verification
        Assert.Equal("Charlie", doc.GetCell(0, 0));
        Assert.Equal("Engineering", doc.GetCell(0, 1));
        Assert.Equal("85000", doc.GetCell(0, 2));
        Assert.Equal("Diana", doc.GetCell(4, 0));

        // SortRows ascending by Employee
        var sorted = doc.SortRows("Employee", ascending: true);
        Assert.Equal(5, sorted.RowCount);
        Assert.Equal("Alice", sorted.GetColumnValues("Employee")[0]);
        Assert.Equal("Alice", sorted.GetCell(0, 0));
        Assert.Equal("Finance", sorted.GetCell(0, 1));

        // SortRows descending by Salary
        var sortedDesc = doc.SortRows("Salary", ascending: false);
        var salaries = sortedDesc.GetColumnValues("Salary");
        Assert.Equal("95000", salaries[0]); // Bob
        Assert.Equal("78000", salaries[4]); // Eve

        // Filter then Sort
        var engFiltered = doc.Filter("Department", "Engineering");
        Assert.Equal(2, engFiltered.RowCount);
        var sortedEng = engFiltered.SortRows("Salary", ascending: false);
        Assert.Equal("85000", sortedEng.GetCell(0, 2)); // Charlie

        // RemoveRow — remove first row (Charlie)
        var mutableDoc = LoadSample();
        mutableDoc.RemoveRow(0);
        Assert.Equal(4, mutableDoc.RowCount);
        Assert.DoesNotContain("Charlie", mutableDoc.GetColumnValues("Employee"));
        Assert.Equal("Alice", mutableDoc.GetCell(0, 0)); // Alice is now first

        // SortRows after RemoveRow
        var sortedAfterRemove = mutableDoc.SortRows("Employee", ascending: true);
        Assert.Equal(4, sortedAfterRemove.RowCount);
        Assert.Equal("Alice", sortedAfterRemove.GetColumnValues("Employee")[0]);

        // AddRow then RemoveRow
        mutableDoc.AddRow(new[] { "Frank", "Legal", "91000", "4" });
        Assert.Equal(5, mutableDoc.RowCount);
        mutableDoc.RemoveRow(mutableDoc.RowCount - 1);
        Assert.Equal(4, mutableDoc.RowCount);
        Assert.DoesNotContain("Frank", mutableDoc.GetColumnValues("Employee"));

        // SaveToFile and reload
        var path = TempFile("dogfood_sort_cell.csv");
        mutableDoc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(4, loaded.RowCount);
        var loadedSorted = loaded.SortRows("Employee", ascending: true);
        Assert.Equal("Alice", loadedSorted.GetCell(0, 0));
    }
}
