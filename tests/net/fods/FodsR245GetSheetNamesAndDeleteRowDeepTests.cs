// Tests for FodsDocument.GetSheetNames, DeleteRow, ClearCellValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R245

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R245: Tests for FodsDocument.GetSheetNames, DeleteRow, ClearCellValue deeper.
/// GetSheetNames(): returns list of all sheet names in the document.
/// DeleteRow(sheetName, rowIndex): deletes a data row at the specified index.
/// ClearCellValue(sheetName, row, col): clears the value of a specific cell.
/// Covers: GetSheetNames non-null; GetSheetNames count correct; GetSheetNames contains known;
/// GetSheetNames after AddSheet grows; GetSheetNames after RemoveSheet shrinks;
/// GetSheetNames consistent; GetSheetNames order preserved;
/// DeleteRow decrements GetRowCount; DeleteRow removes value; DeleteRow first row;
/// DeleteRow other rows intact; DeleteRow persist; DeleteRow no-throw on last;
/// ClearCellValue makes cell empty; ClearCellValue other cells intact;
/// ClearCellValue then SetCellValue works; ClearCellValue persist; ClearCellValue no-throw;
/// dogfood CreateDoc→GetSheetNames→DeleteRow→ClearCellValue→SaveToFile pipeline.
/// </summary>
public class FodsR245GetSheetNamesAndDeleteRowDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR245GetSheetNamesAndDeleteRowDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR245_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateMultiSheetDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Alpha");
        doc.SetCellValue("Alpha", 0, 0, "Name");
        doc.SetCellValue("Alpha", 0, 1, "Score");
        doc.SetCellValue("Alpha", 1, 0, "Alice");
        doc.SetCellValue("Alpha", 1, 1, "92");
        doc.SetCellValue("Alpha", 2, 0, "Bob");
        doc.SetCellValue("Alpha", 2, 1, "78");
        doc.SetCellValue("Alpha", 3, 0, "Carol");
        doc.SetCellValue("Alpha", 3, 1, "85");
        doc.AddSheet("Beta");
        doc.SetCellValue("Beta", 0, 0, "Product");
        doc.SetCellValue("Beta", 0, 1, "Price");
        doc.SetCellValue("Beta", 1, 0, "Widget");
        doc.SetCellValue("Beta", 1, 1, "29.99");
        doc.SetCellValue("Beta", 2, 0, "Gadget");
        doc.SetCellValue("Beta", 2, 1, "49.99");
        doc.AddSheet("Gamma");
        doc.SetCellValue("Gamma", 0, 0, "Region");
        doc.SetCellValue("Gamma", 1, 0, "North");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSheetNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetNames_NonNull()
    {
        var doc = CreateMultiSheetDoc();
        Assert.NotNull(doc.GetSheetNames());
    }

    [Fact]
    public void GetSheetNames_CountCorrect()
    {
        var doc = CreateMultiSheetDoc();
        Assert.Equal(3, doc.GetSheetNames().Count);
    }

    [Fact]
    public void GetSheetNames_ContainsKnownSheets()
    {
        var doc = CreateMultiSheetDoc();
        var names = doc.GetSheetNames();
        Assert.Contains("Alpha", names);
        Assert.Contains("Beta", names);
        Assert.Contains("Gamma", names);
    }

    [Fact]
    public void GetSheetNames_AfterAddSheet_Grows()
    {
        var doc = CreateMultiSheetDoc();
        var before = doc.GetSheetNames().Count;
        doc.AddSheet("Delta");
        Assert.True(doc.GetSheetNames().Count > before);
    }

    [Fact]
    public void GetSheetNames_AfterRemoveSheet_Shrinks()
    {
        var doc = CreateMultiSheetDoc();
        var before = doc.GetSheetNames().Count;
        doc.RemoveSheet("Gamma");
        Assert.True(doc.GetSheetNames().Count < before);
    }

    [Fact]
    public void GetSheetNames_Consistent()
    {
        var doc = CreateMultiSheetDoc();
        var n1 = doc.GetSheetNames();
        var n2 = doc.GetSheetNames();
        Assert.Equal(n1.Count, n2.Count);
    }

    [Fact]
    public void GetSheetNames_OrderPreserved()
    {
        var doc = CreateMultiSheetDoc();
        var names = doc.GetSheetNames();
        Assert.Equal("Alpha", names[0]);
        Assert.Equal("Beta", names[1]);
        Assert.Equal("Gamma", names[2]);
    }

    // -------------------------------------------------------------------------
    // DeleteRow
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRow_DecrementsRowCount()
    {
        var doc = CreateMultiSheetDoc();
        var before = doc.GetRowCount("Alpha");
        doc.DeleteRow("Alpha", 1);
        Assert.True(doc.GetRowCount("Alpha") < before);
    }

    [Fact]
    public void DeleteRow_RemovesValue()
    {
        var doc = CreateMultiSheetDoc();
        doc.DeleteRow("Alpha", 1); // Remove Alice
        var json = doc.ExportToJson("Alpha");
        Assert.DoesNotContain("Alice", json);
    }

    [Fact]
    public void DeleteRow_OtherRowsIntact()
    {
        var doc = CreateMultiSheetDoc();
        doc.DeleteRow("Alpha", 1); // Remove Alice
        var json = doc.ExportToJson("Alpha");
        Assert.Contains("Bob", json);
        Assert.Contains("Carol", json);
    }

    [Fact]
    public void DeleteRow_Persist()
    {
        var doc = CreateMultiSheetDoc();
        doc.DeleteRow("Alpha", 1);
        var path = TempFile("delete_persist.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.DoesNotContain("Alice", loaded.ExportToJson("Alpha"));
    }

    [Fact]
    public void DeleteRow_NoThrow()
    {
        var doc = CreateMultiSheetDoc();
        var rowCount = doc.GetRowCount("Alpha");
        var ex = Record.Exception(() => doc.DeleteRow("Alpha", rowCount - 1));
        Assert.Null(ex);
    }

    [Fact]
    public void DeleteRow_ThenFilterStillWorks()
    {
        var doc = CreateMultiSheetDoc();
        doc.DeleteRow("Alpha", 1); // Remove Alice
        // Verify doc is still usable
        var json = doc.ExportToJson("Alpha");
        Assert.NotNull(json);
    }

    // -------------------------------------------------------------------------
    // ClearCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearCellValue_MakesCellEmpty()
    {
        var doc = CreateMultiSheetDoc();
        doc.ClearCellValue("Alpha", 1, 0);
        var val = doc.GetCellValue("Alpha", 1, 0);
        Assert.True(val == null || val == string.Empty);
    }

    [Fact]
    public void ClearCellValue_OtherCellsIntact()
    {
        var doc = CreateMultiSheetDoc();
        doc.ClearCellValue("Alpha", 1, 0); // Clear Name
        var score = doc.GetCellValue("Alpha", 1, 1); // Score should remain
        Assert.Equal("92", score);
    }

    [Fact]
    public void ClearCellValue_Persist()
    {
        var doc = CreateMultiSheetDoc();
        doc.ClearCellValue("Alpha", 1, 0);
        var path = TempFile("clear_persist.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var val = loaded.GetCellValue("Alpha", 1, 0);
        Assert.True(val == null || val == string.Empty);
    }

    [Fact]
    public void ClearCellValue_NoThrow_OnAlreadyEmpty()
    {
        var doc = CreateMultiSheetDoc();
        doc.ClearCellValue("Alpha", 1, 0);
        var ex = Record.Exception(() => doc.ClearCellValue("Alpha", 1, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void ClearCellValue_ThenSetCellValue_Works()
    {
        var doc = CreateMultiSheetDoc();
        doc.ClearCellValue("Alpha", 1, 0);
        doc.SetCellValue("Alpha", 1, 0, "AliceReplacement");
        Assert.Equal("AliceReplacement", doc.GetCellValue("Alpha", 1, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_GetSheetNames_DeleteRow_ClearCellValue_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Employees");
        doc.SetCellValue("Employees", 0, 0, "Name");
        doc.SetCellValue("Employees", 0, 1, "Dept");
        doc.SetCellValue("Employees", 0, 2, "Salary");
        doc.SetCellValue("Employees", 1, 0, "Alice");
        doc.SetCellValue("Employees", 1, 1, "Engineering");
        doc.SetCellValue("Employees", 1, 2, "90000");
        doc.SetCellValue("Employees", 2, 0, "Bob");
        doc.SetCellValue("Employees", 2, 1, "Finance");
        doc.SetCellValue("Employees", 2, 2, "85000");
        doc.SetCellValue("Employees", 3, 0, "Carol");
        doc.SetCellValue("Employees", 3, 1, "Engineering");
        doc.SetCellValue("Employees", 3, 2, "95000");
        doc.AddSheet("Departments");
        doc.SetCellValue("Departments", 0, 0, "Name");
        doc.SetCellValue("Departments", 0, 1, "Budget");
        doc.SetCellValue("Departments", 1, 0, "Engineering");
        doc.SetCellValue("Departments", 1, 1, "500000");

        // GetSheetNames
        var names = doc.GetSheetNames();
        Assert.NotNull(names);
        Assert.Equal(2, names.Count);
        Assert.Contains("Employees", names);
        Assert.Contains("Departments", names);

        // Add another sheet
        doc.AddSheet("Summary");
        Assert.Equal(3, doc.GetSheetNames().Count);
        Assert.Contains("Summary", doc.GetSheetNames());

        // DeleteRow — remove Bob (row 2)
        var rowsBefore = doc.GetRowCount("Employees");
        doc.DeleteRow("Employees", 2);
        Assert.True(doc.GetRowCount("Employees") < rowsBefore);
        var empJson = doc.ExportToJson("Employees");
        Assert.DoesNotContain("Bob", empJson);
        Assert.Contains("Alice", empJson);
        Assert.Contains("Carol", empJson);

        // ClearCellValue — clear Carol's salary
        doc.ClearCellValue("Employees", 3, 2);
        var carolSalary = doc.GetCellValue("Employees", 3, 2);
        Assert.True(carolSalary == null || carolSalary == string.Empty);

        // Other cells intact
        Assert.Equal("Carol", doc.GetCellValue("Employees", 3, 0));
        Assert.Equal("Engineering", doc.GetCellValue("Employees", 3, 1));

        // SetCellValue after clear
        doc.SetCellValue("Employees", 3, 2, "97000");
        Assert.Equal("97000", doc.GetCellValue("Employees", 3, 2));

        // RemoveSheet and verify GetSheetNames
        doc.RemoveSheet("Summary");
        Assert.Equal(2, doc.GetSheetNames().Count);
        Assert.DoesNotContain("Summary", doc.GetSheetNames());

        // SaveToFile and reload
        var path = TempFile("dogfood_sheetnames.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);

        // Verify reloaded sheet names
        var loadedNames = loaded.GetSheetNames();
        Assert.True(loadedNames.Count >= 2);
        Assert.Contains("Employees", loadedNames);

        // Verify deleted row not present
        Assert.DoesNotContain("Bob", loaded.ExportToJson("Employees"));

        // Verify cleared and re-set cell
        Assert.Equal("97000", loaded.GetCellValue("Employees", 3, 2));
    }
}
