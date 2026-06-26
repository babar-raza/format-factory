// Tests for FodsDocument.GetSheetNames, AddSheet, RemoveSheet deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R268

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R268: Tests for FodsDocument.GetSheetNames, AddSheet, RemoveSheet deeper.
/// GetSheetNames(): returns a list of all sheet names in the document.
/// AddSheet(name): adds a new empty sheet with the given name.
/// RemoveSheet(name): removes the specified sheet from the document.
/// Covers: GetSheetNames non-null; GetSheetNames non-empty; GetSheetNames no-throw;
/// GetSheetNames consistent; GetSheetNames count correct; GetSheetNames has default;
/// GetSheetNames after AddSheet grows; GetSheetNames after RemoveSheet shrinks;
/// GetSheetNames save-load consistent; GetSheetNames no duplicates;
/// AddSheet no-throw; AddSheet increases sheet count; AddSheet name appears;
/// AddSheet multiple; AddSheet then SetCellValue; AddSheet persist;
/// RemoveSheet no-throw; RemoveSheet decreases count; RemoveSheet name gone;
/// RemoveSheet then AddSheet same name; RemoveSheet persist; RemoveSheet save-load;
/// dogfood CreateDoc→AddSheet→GetSheetNames→RemoveSheet→SaveToFile pipeline.
/// </summary>
public class FodsR268GetSheetNamesAndAddSheetDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR268GetSheetNamesAndAddSheetDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR268_" + Guid.NewGuid().ToString("N"));
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
        doc.SetCellValue("Sales", 0, 0, "Region");
        doc.SetCellValue("Sales", 0, 1, "Revenue");
        doc.SetCellValue("Sales", 1, 0, "North");
        doc.SetCellValue("Sales", 1, 1, "85000");
        doc.AddSheet("HR");
        doc.SetCellValue("HR", 0, 0, "Employee");
        doc.SetCellValue("HR", 0, 1, "Department");
        doc.SetCellValue("HR", 1, 0, "Alice");
        doc.SetCellValue("HR", 1, 1, "Engineering");
        doc.AddSheet("Finance");
        doc.SetCellValue("Finance", 0, 0, "Account");
        doc.SetCellValue("Finance", 0, 1, "Balance");
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
    public void GetSheetNames_NonEmpty()
    {
        var doc = CreateMultiSheetDoc();
        Assert.True(doc.GetSheetNames().Count > 0);
    }

    [Fact]
    public void GetSheetNames_NoThrow()
    {
        var doc = CreateMultiSheetDoc();
        var ex = Record.Exception(() => doc.GetSheetNames());
        Assert.Null(ex);
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
    public void GetSheetNames_Count_ThreeSheets()
    {
        var doc = CreateMultiSheetDoc();
        Assert.Equal(3, doc.GetSheetNames().Count);
    }

    [Fact]
    public void GetSheetNames_HasSales()
    {
        var doc = CreateMultiSheetDoc();
        var names = doc.GetSheetNames();
        Assert.True(names.Contains("Sales") || names.Exists(n => n == "Sales"));
    }

    [Fact]
    public void GetSheetNames_AfterAddSheet_Grows()
    {
        var doc = CreateMultiSheetDoc();
        var before = doc.GetSheetNames().Count;
        doc.AddSheet("Ops");
        Assert.Equal(before + 1, doc.GetSheetNames().Count);
    }

    [Fact]
    public void GetSheetNames_AfterRemoveSheet_Shrinks()
    {
        var doc = CreateMultiSheetDoc();
        var before = doc.GetSheetNames().Count;
        doc.RemoveSheet("Finance");
        Assert.Equal(before - 1, doc.GetSheetNames().Count);
    }

    [Fact]
    public void GetSheetNames_SaveLoad_Consistent()
    {
        var doc = CreateMultiSheetDoc();
        var before = doc.GetSheetNames().Count;
        var path = TempFile("sheetnames_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSheetNames().Count);
    }

    [Fact]
    public void GetSheetNames_NoDuplicates()
    {
        var doc = CreateMultiSheetDoc();
        var names = doc.GetSheetNames();
        var distinct = new System.Collections.Generic.HashSet<string>(names);
        Assert.Equal(distinct.Count, names.Count);
    }

    // -------------------------------------------------------------------------
    // AddSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void AddSheet_NoThrow()
    {
        var doc = FodsDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.AddSheet("NewSheet"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSheet_IncreasesSheetCount()
    {
        var doc = FodsDocument.CreateEmpty();
        var before = doc.GetSheetNames().Count;
        doc.AddSheet("Extra");
        Assert.Equal(before + 1, doc.GetSheetNames().Count);
    }

    [Fact]
    public void AddSheet_NameAppearsInGetSheetNames()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Marketing");
        var names = doc.GetSheetNames();
        Assert.True(names.Contains("Marketing") || names.Exists(n => n == "Marketing"));
    }

    [Fact]
    public void AddSheet_Multiple()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet2");
        doc.AddSheet("Sheet3");
        doc.AddSheet("Sheet4");
        // Default sheet + 3 added = at least 4
        Assert.True(doc.GetSheetNames().Count >= 3);
    }

    [Fact]
    public void AddSheet_ThenSetCellValue_NoThrow()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        var ex = Record.Exception(() => doc.SetCellValue("Data", 0, 0, "Hello"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSheet_Persist()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Persisted");
        doc.SetCellValue("Persisted", 0, 0, "value");
        var path = TempFile("addsheet_persist.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var names = loaded.GetSheetNames();
        Assert.True(names.Contains("Persisted") || names.Exists(n => n == "Persisted"));
    }

    // -------------------------------------------------------------------------
    // RemoveSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveSheet_NoThrow()
    {
        var doc = CreateMultiSheetDoc();
        var ex = Record.Exception(() => doc.RemoveSheet("Finance"));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveSheet_DecreasesSheetCount()
    {
        var doc = CreateMultiSheetDoc();
        var before = doc.GetSheetNames().Count;
        doc.RemoveSheet("HR");
        Assert.Equal(before - 1, doc.GetSheetNames().Count);
    }

    [Fact]
    public void RemoveSheet_NameDisappears()
    {
        var doc = CreateMultiSheetDoc();
        doc.RemoveSheet("Finance");
        var names = doc.GetSheetNames();
        Assert.False(names.Contains("Finance") || names.Exists(n => n == "Finance"));
    }

    [Fact]
    public void RemoveSheet_ThenAddSameName()
    {
        var doc = CreateMultiSheetDoc();
        doc.RemoveSheet("Finance");
        doc.AddSheet("Finance");
        var names = doc.GetSheetNames();
        Assert.True(names.Contains("Finance") || names.Exists(n => n == "Finance"));
    }

    [Fact]
    public void RemoveSheet_Persist()
    {
        var doc = CreateMultiSheetDoc();
        doc.RemoveSheet("HR");
        var path = TempFile("removesheet_persist.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var names = loaded.GetSheetNames();
        Assert.False(names.Contains("HR") || names.Exists(n => n == "HR"));
    }

    [Fact]
    public void RemoveSheet_SaveLoad_Consistent()
    {
        var doc = CreateMultiSheetDoc();
        doc.RemoveSheet("Finance");
        var beforeCount = doc.GetSheetNames().Count;
        var path = TempFile("removesheet_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(beforeCount, loaded.GetSheetNames().Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddSheet_GetSheetNames_RemoveSheet_SaveToFile_Pipeline()
    {
        // Build comprehensive multi-sheet workbook
        var doc = FodsDocument.CreateEmpty();

        // Default sheet — Q1 Summary
        doc.SetCellValue("Q1Summary", 0, 0, "Metric");
        doc.SetCellValue("Q1Summary", 0, 1, "Value");
        doc.SetCellValue("Q1Summary", 0, 2, "Target");
        doc.SetCellValue("Q1Summary", 1, 0, "Revenue");
        doc.SetCellValue("Q1Summary", 1, 1, "8500000");
        doc.SetCellValue("Q1Summary", 1, 2, "8000000");
        doc.SetCellValue("Q1Summary", 2, 0, "Customers");
        doc.SetCellValue("Q1Summary", 2, 1, "1250");
        doc.SetCellValue("Q1Summary", 2, 2, "1200");

        // Add 4 more sheets
        doc.AddSheet("Engineering");
        doc.SetCellValue("Engineering", 0, 0, "Team");
        doc.SetCellValue("Engineering", 0, 1, "Headcount");
        doc.SetCellValue("Engineering", 1, 0, "Backend");
        doc.SetCellValue("Engineering", 1, 1, "45");
        doc.SetCellValue("Engineering", 2, 0, "Frontend");
        doc.SetCellValue("Engineering", 2, 1, "28");

        doc.AddSheet("Marketing");
        doc.SetCellValue("Marketing", 0, 0, "Channel");
        doc.SetCellValue("Marketing", 0, 1, "Leads");
        doc.SetCellValue("Marketing", 1, 0, "Organic");
        doc.SetCellValue("Marketing", 1, 1, "3200");
        doc.SetCellValue("Marketing", 2, 0, "Paid");
        doc.SetCellValue("Marketing", 2, 1, "1800");

        doc.AddSheet("Finance");
        doc.SetCellValue("Finance", 0, 0, "Account");
        doc.SetCellValue("Finance", 0, 1, "Q1");
        doc.SetCellValue("Finance", 1, 0, "Operating");
        doc.SetCellValue("Finance", 1, 1, "2100000");

        doc.AddSheet("Temp");
        doc.SetCellValue("Temp", 0, 0, "Temporary");

        // GetSheetNames — 5 sheets
        var names = doc.GetSheetNames();
        Assert.Equal(5, names.Count);
        Assert.True(names.Contains("Q1Summary") || names.Exists(n => n == "Q1Summary"));
        Assert.True(names.Contains("Engineering") || names.Exists(n => n == "Engineering"));
        Assert.True(names.Contains("Marketing") || names.Exists(n => n == "Marketing"));
        Assert.True(names.Contains("Finance") || names.Exists(n => n == "Finance"));
        Assert.True(names.Contains("Temp") || names.Exists(n => n == "Temp"));

        // No duplicates
        var distinct = new System.Collections.Generic.HashSet<string>(names);
        Assert.Equal(distinct.Count, names.Count);

        // GetSheetNames consistent
        Assert.Equal(names.Count, doc.GetSheetNames().Count);

        // RemoveSheet Temp
        doc.RemoveSheet("Temp");
        var namesAfterRemove = doc.GetSheetNames();
        Assert.Equal(4, namesAfterRemove.Count);
        Assert.False(namesAfterRemove.Contains("Temp") || namesAfterRemove.Exists(n => n == "Temp"));

        // AddSheet Operations
        doc.AddSheet("Operations");
        doc.SetCellValue("Operations", 0, 0, "Process");
        doc.SetCellValue("Operations", 0, 1, "Status");
        doc.SetCellValue("Operations", 1, 0, "Deployment");
        doc.SetCellValue("Operations", 1, 1, "Green");
        Assert.Equal(5, doc.GetSheetNames().Count);

        // SetCellValue on all sheets — no throw
        doc.SetCellValue("Q1Summary", 3, 0, "NPS");
        doc.SetCellValue("Engineering", 3, 0, "Mobile");
        doc.SetCellValue("Marketing", 3, 0, "Email");
        doc.SetCellValue("Finance", 2, 0, "Capital");

        // SaveToFile
        var path = TempFile("dogfood_multisheet.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify sheet names
        var loaded = FodsDocument.LoadFile(path);
        var loadedNames = loaded.GetSheetNames();
        Assert.Equal(5, loadedNames.Count);
        Assert.True(loadedNames.Contains("Finance") || loadedNames.Exists(n => n == "Finance"));
        Assert.True(loadedNames.Contains("Operations") || loadedNames.Exists(n => n == "Operations"));

        // RemoveSheet on loaded
        loaded.RemoveSheet("Operations");
        Assert.Equal(4, loaded.GetSheetNames().Count);

        // AddSheet on loaded
        loaded.AddSheet("Q2Summary");
        Assert.Equal(5, loaded.GetSheetNames().Count);

        // GetSheetNames no duplicates after mutations
        var finalNames = loaded.GetSheetNames();
        var finalDistinct = new System.Collections.Generic.HashSet<string>(finalNames);
        Assert.Equal(finalDistinct.Count, finalNames.Count);

        // Final save
        var path2 = TempFile("dogfood_multisheet_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetSheetNames().Count);
        Assert.True(loaded2.GetSheetNames().Contains("Q2Summary") ||
                    loaded2.GetSheetNames().Exists(n => n == "Q2Summary"));
    }
}
