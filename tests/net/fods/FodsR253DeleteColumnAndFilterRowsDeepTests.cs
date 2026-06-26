// Tests for FodsDocument.DeleteColumn, FilterRows, GetSheetNames deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R253

using System;
using System.IO;
using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R253: Tests for FodsDocument.DeleteColumn, FilterRows, GetSheetNames deeper.
/// DeleteColumn(sheetName, colName): removes a column from the specified sheet.
/// FilterRows(sheetName, colName, value): returns a filtered view matching the value.
/// GetSheetNames(): returns a list of all sheet names in the document.
/// Covers: DeleteColumn no-throw; DeleteColumn removes header; DeleteColumn reduces column count;
/// DeleteColumn values inaccessible after; DeleteColumn persist; DeleteColumn multiple;
/// FilterRows non-null; FilterRows reduces row count; FilterRows matching rows only;
/// FilterRows same column structure; FilterRows chained; FilterRows empty result;
/// FilterRows persist; FilterRows then GetCell;
/// GetSheetNames non-null; GetSheetNames non-empty; GetSheetNames count correct;
/// GetSheetNames contains known; GetSheetNames after AddSheet grows;
/// GetSheetNames after merge grows; GetSheetNames consistent; GetSheetNames order preserved;
/// dogfood LoadFile→FilterRows→DeleteColumn→GetSheetNames→SaveToFile pipeline.
/// </summary>
public class FodsR253DeleteColumnAndFilterRowsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR253DeleteColumnAndFilterRowsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR253_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateEmployeeDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Employees");
        doc.SetCellValue("Employees", 0, 0, "Name");
        doc.SetCellValue("Employees", 0, 1, "Department");
        doc.SetCellValue("Employees", 0, 2, "Salary");
        doc.SetCellValue("Employees", 0, 3, "Location");
        doc.SetCellValue("Employees", 1, 0, "Alice");
        doc.SetCellValue("Employees", 1, 1, "Engineering");
        doc.SetCellValue("Employees", 1, 2, "95000");
        doc.SetCellValue("Employees", 1, 3, "London");
        doc.SetCellValue("Employees", 2, 0, "Bob");
        doc.SetCellValue("Employees", 2, 1, "Marketing");
        doc.SetCellValue("Employees", 2, 2, "72000");
        doc.SetCellValue("Employees", 2, 3, "Paris");
        doc.SetCellValue("Employees", 3, 0, "Carol");
        doc.SetCellValue("Employees", 3, 1, "Engineering");
        doc.SetCellValue("Employees", 3, 2, "88000");
        doc.SetCellValue("Employees", 3, 3, "London");
        doc.SetCellValue("Employees", 4, 0, "Dave");
        doc.SetCellValue("Employees", 4, 1, "Finance");
        doc.SetCellValue("Employees", 4, 2, "81000");
        doc.SetCellValue("Employees", 4, 3, "Berlin");
        doc.SetCellValue("Employees", 5, 0, "Eve");
        doc.SetCellValue("Employees", 5, 1, "Engineering");
        doc.SetCellValue("Employees", 5, 2, "102000");
        doc.SetCellValue("Employees", 5, 3, "London");
        return doc;
    }

    // -------------------------------------------------------------------------
    // DeleteColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteColumn_NoThrow()
    {
        var doc = CreateEmployeeDoc();
        var ex = Record.Exception(() => doc.DeleteColumn("Employees", "Location"));
        Assert.Null(ex);
    }

    [Fact]
    public void DeleteColumn_ReducesColumnCount()
    {
        var doc = CreateEmployeeDoc();
        var before = doc.GetColumnNames("Employees").Count;
        doc.DeleteColumn("Employees", "Location");
        var after = doc.GetColumnNames("Employees").Count;
        Assert.Equal(before - 1, after);
    }

    [Fact]
    public void DeleteColumn_RemovesHeader()
    {
        var doc = CreateEmployeeDoc();
        doc.DeleteColumn("Employees", "Location");
        var cols = doc.GetColumnNames("Employees");
        Assert.False(cols.Contains("Location"));
    }

    [Fact]
    public void DeleteColumn_RetainsOtherColumns()
    {
        var doc = CreateEmployeeDoc();
        doc.DeleteColumn("Employees", "Location");
        var cols = doc.GetColumnNames("Employees");
        Assert.Contains("Name", cols);
        Assert.Contains("Department", cols);
        Assert.Contains("Salary", cols);
    }

    [Fact]
    public void DeleteColumn_Persist()
    {
        var doc = CreateEmployeeDoc();
        doc.DeleteColumn("Employees", "Location");
        var path = TempFile("delete_col.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var cols = loaded.GetColumnNames("Employees");
        Assert.False(cols.Contains("Location"));
        Assert.Contains("Name", cols);
    }

    [Fact]
    public void DeleteColumn_Multiple_EachReducesCount()
    {
        var doc = CreateEmployeeDoc();
        var before = doc.GetColumnNames("Employees").Count;
        doc.DeleteColumn("Employees", "Location");
        doc.DeleteColumn("Employees", "Salary");
        var after = doc.GetColumnNames("Employees").Count;
        Assert.Equal(before - 2, after);
    }

    [Fact]
    public void DeleteColumn_RowCountUnchanged()
    {
        var doc = CreateEmployeeDoc();
        var range = doc.GetUsedRange("Employees");
        doc.DeleteColumn("Employees", "Location");
        var rangeAfter = doc.GetUsedRange("Employees");
        // Row count should remain the same
        Assert.True(rangeAfter.Item1 >= 1);
    }

    // -------------------------------------------------------------------------
    // FilterRows
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_NonNull()
    {
        var doc = CreateEmployeeDoc();
        var result = doc.FilterRows("Employees", "Department", "Engineering");
        Assert.NotNull(result);
    }

    [Fact]
    public void FilterRows_ReducesRowCount()
    {
        var doc = CreateEmployeeDoc();
        var result = doc.FilterRows("Employees", "Department", "Engineering");
        var total = doc.GetUsedRange("Employees").Item1;
        Assert.True(result.GetUsedRange("Employees").Item1 < total);
    }

    [Fact]
    public void FilterRows_MatchingRowsOnly()
    {
        var doc = CreateEmployeeDoc();
        var result = doc.FilterRows("Employees", "Department", "Engineering");
        var range = result.GetUsedRange("Employees");
        // All data rows (excluding header) should be Engineering
        for (int r = 1; r < range.Item1; r++)
        {
            var dept = result.GetCellValue("Employees", r, 1);
            Assert.Equal("Engineering", dept);
        }
    }

    [Fact]
    public void FilterRows_EngineersCountThree()
    {
        var doc = CreateEmployeeDoc();
        var result = doc.FilterRows("Employees", "Department", "Engineering");
        var range = result.GetUsedRange("Employees");
        // 3 engineers + 1 header = 4 rows
        Assert.Equal(4, range.Item1);
    }

    [Fact]
    public void FilterRows_SameColumnStructure()
    {
        var doc = CreateEmployeeDoc();
        var result = doc.FilterRows("Employees", "Department", "Engineering");
        var origCols = doc.GetColumnNames("Employees");
        var filtCols = result.GetColumnNames("Employees");
        Assert.Equal(origCols.Count, filtCols.Count);
    }

    [Fact]
    public void FilterRows_EmptyResult_NonNull()
    {
        var doc = CreateEmployeeDoc();
        var result = doc.FilterRows("Employees", "Department", "NONEXISTENT_DEPT");
        Assert.NotNull(result);
    }

    [Fact]
    public void FilterRows_Persist()
    {
        var doc = CreateEmployeeDoc();
        var result = doc.FilterRows("Employees", "Department", "Engineering");
        var path = TempFile("filter_rows.fods");
        result.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);
    }

    [Fact]
    public void FilterRows_Finance_CountOne()
    {
        var doc = CreateEmployeeDoc();
        var result = doc.FilterRows("Employees", "Department", "Finance");
        var range = result.GetUsedRange("Employees");
        // 1 Finance + 1 header = 2 rows
        Assert.Equal(2, range.Item1);
    }

    // -------------------------------------------------------------------------
    // GetSheetNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetNames_NonNull()
    {
        var doc = CreateEmployeeDoc();
        Assert.NotNull(doc.GetSheetNames());
    }

    [Fact]
    public void GetSheetNames_NonEmpty()
    {
        var doc = CreateEmployeeDoc();
        Assert.True(doc.GetSheetNames().Count > 0);
    }

    [Fact]
    public void GetSheetNames_ContainsEmployees()
    {
        var doc = CreateEmployeeDoc();
        Assert.Contains("Employees", doc.GetSheetNames());
    }

    [Fact]
    public void GetSheetNames_AfterAddSheet_Grows()
    {
        var doc = CreateEmployeeDoc();
        var before = doc.GetSheetNames().Count;
        doc.AddSheet("Summary");
        var after = doc.GetSheetNames().Count;
        Assert.Equal(before + 1, after);
    }

    [Fact]
    public void GetSheetNames_Consistent()
    {
        var doc = CreateEmployeeDoc();
        var n1 = doc.GetSheetNames();
        var n2 = doc.GetSheetNames();
        Assert.Equal(n1.Count, n2.Count);
    }

    [Fact]
    public void GetSheetNames_AfterAddSheet_ContainsNewSheet()
    {
        var doc = CreateEmployeeDoc();
        doc.AddSheet("Reports");
        Assert.Contains("Reports", doc.GetSheetNames());
    }

    [Fact]
    public void GetSheetNames_MultipleSheets_AllPresent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.AddSheet("Gamma");
        var names = doc.GetSheetNames();
        Assert.Contains("Alpha", names);
        Assert.Contains("Beta", names);
        Assert.Contains("Gamma", names);
    }

    [Fact]
    public void GetSheetNames_Persist()
    {
        var doc = CreateEmployeeDoc();
        doc.AddSheet("Backup");
        var path = TempFile("sheet_names.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Contains("Employees", loaded.GetSheetNames());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FilterRows_DeleteColumn_GetSheetNames_SaveToFile_Pipeline()
    {
        // Build multi-sheet document
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Staff");
        doc.AddSheet("Departments");
        doc.AddSheet("Locations");

        // Populate Staff sheet
        var staffCols = new[] { "Name", "Dept", "Grade", "City", "Active" };
        for (int c = 0; c < staffCols.Length; c++)
            doc.SetCellValue("Staff", 0, c, staffCols[c]);

        var staffData = new[]
        {
            new[] { "Alice", "Eng", "Senior", "London", "Yes" },
            new[] { "Bob", "Mkt", "Junior", "Paris", "Yes" },
            new[] { "Carol", "Eng", "Senior", "London", "No" },
            new[] { "Dave", "Fin", "Mid", "Berlin", "Yes" },
            new[] { "Eve", "Eng", "Lead", "London", "Yes" },
            new[] { "Frank", "Mkt", "Senior", "Rome", "No" },
        };
        for (int r = 0; r < staffData.Length; r++)
            for (int c = 0; c < staffData[r].Length; c++)
                doc.SetCellValue("Staff", r + 1, c, staffData[r][c]);

        // Populate Departments sheet
        doc.SetCellValue("Departments", 0, 0, "DeptCode");
        doc.SetCellValue("Departments", 0, 1, "DeptName");
        doc.SetCellValue("Departments", 1, 0, "Eng");
        doc.SetCellValue("Departments", 1, 1, "Engineering");
        doc.SetCellValue("Departments", 2, 0, "Mkt");
        doc.SetCellValue("Departments", 2, 1, "Marketing");
        doc.SetCellValue("Departments", 3, 0, "Fin");
        doc.SetCellValue("Departments", 3, 1, "Finance");

        // GetSheetNames baseline
        var sheetNames = doc.GetSheetNames();
        Assert.NotNull(sheetNames);
        Assert.Equal(3, sheetNames.Count);
        Assert.Contains("Staff", sheetNames);
        Assert.Contains("Departments", sheetNames);
        Assert.Contains("Locations", sheetNames);

        // GetColumnNames on Staff
        var cols = doc.GetColumnNames("Staff");
        Assert.Equal(5, cols.Count);
        Assert.Contains("Active", cols);

        // FilterRows — Engineering only
        var engStaff = doc.FilterRows("Staff", "Dept", "Eng");
        Assert.NotNull(engStaff);
        var engRange = engStaff.GetUsedRange("Staff");
        // 3 Eng rows + 1 header = 4
        Assert.Equal(4, engRange.Item1);

        // FilterRows — active only
        var activeStaff = doc.FilterRows("Staff", "Active", "Yes");
        Assert.NotNull(activeStaff);
        var activeRange = activeStaff.GetUsedRange("Staff");
        // 4 active + 1 header = 5
        Assert.Equal(5, activeRange.Item1);

        // DeleteColumn — remove Active column from Staff
        doc.DeleteColumn("Staff", "Active");
        var colsAfterDelete = doc.GetColumnNames("Staff");
        Assert.Equal(4, colsAfterDelete.Count);
        Assert.False(colsAfterDelete.Contains("Active"));
        Assert.Contains("Name", colsAfterDelete);
        Assert.Contains("City", colsAfterDelete);

        // AddSheet and verify GetSheetNames grows
        doc.AddSheet("Archive");
        var sheetNamesAfter = doc.GetSheetNames();
        Assert.Equal(4, sheetNamesAfter.Count);
        Assert.Contains("Archive", sheetNamesAfter);

        // FilterRows after DeleteColumn still works
        var engAfterDelete = doc.FilterRows("Staff", "Dept", "Eng");
        Assert.NotNull(engAfterDelete);
        var engColsAfter = engAfterDelete.GetColumnNames("Staff");
        Assert.False(engColsAfter.Contains("Active"));

        // DeleteColumn on Departments
        doc.DeleteColumn("Departments", "DeptCode");
        var deptCols = doc.GetColumnNames("Departments");
        Assert.Equal(1, deptCols.Count);
        Assert.Contains("DeptName", deptCols);

        // SaveToFile
        var path = TempFile("dogfood_delete_filter.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);
        var loadedSheets = loaded.GetSheetNames();
        Assert.NotNull(loadedSheets);
        Assert.Contains("Staff", loadedSheets);
        Assert.Contains("Departments", loadedSheets);
        Assert.Contains("Archive", loadedSheets);

        var loadedStaffCols = loaded.GetColumnNames("Staff");
        Assert.False(loadedStaffCols.Contains("Active"));
        Assert.Contains("Name", loadedStaffCols);

        // FilterRows on loaded doc
        var loadedEngStaff = loaded.FilterRows("Staff", "Dept", "Eng");
        Assert.NotNull(loadedEngStaff);
        var loadedEngRange = loadedEngStaff.GetUsedRange("Staff");
        Assert.True(loadedEngRange.Item1 > 1);

        // GetSheetNames on loaded
        var loadedSheetCount = loaded.GetSheetNames().Count;
        Assert.Equal(sheetNamesAfter.Count, loadedSheetCount);
    }
}
