// Tests for FodsDocument.AddSheet, SwitchSheet, GetSheetNames deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R231

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R231: Tests for FodsDocument.AddSheet, SwitchSheet, GetSheetNames deeper coverage.
/// AddSheet(name): adds a new sheet with the given name.
/// SwitchSheet(name): switches the active sheet to the one with given name.
/// GetSheetNames(): returns list of all sheet names.
/// Covers: AddSheet increases sheet count; AddSheet with unique name works;
/// AddSheet then GetSheetNames includes new; AddSheet multiple sheets;
/// SwitchSheet no throw; SwitchSheet then SetCellValue on new sheet;
/// SwitchSheet then GetRowCount reflects new sheet; SwitchSheet isolates data;
/// GetSheetNames non-null; GetSheetNames non-empty; GetSheetNames contains added sheet;
/// GetSheetNames count matches AddSheet calls; GetSheetNames after SaveToFile/LoadFile preserved;
/// dogfood CreateDoc→AddSheet×3→SwitchSheet→SetData→GetSheetNames→SaveToFile→LoadFile pipeline.
/// </summary>
public class FodsR231AddSheetAndSwitchSheetDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR231AddSheetAndSwitchSheetDeepTests()
    {
        _tempDir = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "FodsR231_" + Guid.NewGuid().ToString("N"));
        System.IO.Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (System.IO.Directory.Exists(_tempDir))
            System.IO.Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => System.IO.Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // AddSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void AddSheet_IncreasesSheetCount()
    {
        var doc = FodsDocument.CreateEmpty();
        var before = doc.GetSheetCount();
        doc.AddSheet("NewSheet");
        Assert.Equal(before + 1, doc.GetSheetCount());
    }

    [Fact]
    public void AddSheet_ThenGetSheetNames_IncludesNew()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sales");
        var names = doc.GetSheetNames();
        Assert.Contains("Sales", names);
    }

    [Fact]
    public void AddSheet_Multiple_AllInGetSheetNames()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.AddSheet("Gamma");
        var names = doc.GetSheetNames();
        Assert.Contains("Alpha", names);
        Assert.Contains("Beta", names);
        Assert.Contains("Gamma", names);
    }

    [Fact]
    public void AddSheet_NoThrow()
    {
        var doc = FodsDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.AddSheet("TestSheet"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSheet_CountReflectsMultipleAdds()
    {
        var doc = FodsDocument.CreateEmpty();
        var initial = doc.GetSheetCount();
        doc.AddSheet("Sheet2");
        doc.AddSheet("Sheet3");
        Assert.Equal(initial + 2, doc.GetSheetCount());
    }

    // -------------------------------------------------------------------------
    // SwitchSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void SwitchSheet_NoThrow()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("AnotherSheet");
        var ex = Record.Exception(() => doc.SwitchSheet("AnotherSheet"));
        Assert.Null(ex);
    }

    [Fact]
    public void SwitchSheet_ThenSetCellValue_OnNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");

        // Add data to first sheet
        doc.SetCellValue(0, 0, "From Sheet 1");

        // Switch to Data sheet and add different data
        doc.SwitchSheet("Data");
        doc.SetCellValue(0, 0, "From Data Sheet");

        // Data sheet has its value
        Assert.Equal("From Data Sheet", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SwitchSheet_IsolatesData()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("SheetA");
        doc.AddSheet("SheetB");

        // Add rows to SheetA
        doc.SwitchSheet("SheetA");
        doc.AddRow(new List<string> { "A1", "A2" });
        doc.AddRow(new List<string> { "A3", "A4" });

        var sheetACount = doc.GetRowCount();

        // Add rows to SheetB
        doc.SwitchSheet("SheetB");
        doc.AddRow(new List<string> { "B1", "B2" });

        // SheetB should have 1 row, not 2
        Assert.Equal(1, doc.GetRowCount());
        Assert.NotEqual(sheetACount, doc.GetRowCount());
    }

    [Fact]
    public void SwitchSheet_BackToFirst_PreservesData()
    {
        var doc = FodsDocument.CreateEmpty();
        var firstName = doc.GetSheetNames()[0];
        doc.SetCellValue(0, 0, "OriginalValue");
        doc.AddSheet("Second");
        doc.SwitchSheet("Second");
        doc.SetCellValue(0, 0, "SecondValue");

        // Switch back to first sheet
        doc.SwitchSheet(firstName);
        Assert.Equal("OriginalValue", doc.GetCellValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // GetSheetNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetNames_NonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        Assert.NotNull(doc.GetSheetNames());
    }

    [Fact]
    public void GetSheetNames_NonEmpty()
    {
        var doc = FodsDocument.CreateEmpty();
        Assert.True(doc.GetSheetNames().Count > 0);
    }

    [Fact]
    public void GetSheetNames_CountMatchesSheetCount()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Extra");
        Assert.Equal(doc.GetSheetCount(), doc.GetSheetNames().Count);
    }

    [Fact]
    public void GetSheetNames_AfterSaveAndLoad_Preserved()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Reports");
        doc.AddSheet("Summary");
        var path = TempFile("multisheet.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var names = loaded.GetSheetNames();
        Assert.Contains("Reports", names);
        Assert.Contains("Summary", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_AddSheet_SwitchSheet_SetData_GetSheetNames_SaveToFile_LoadFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        var defaultSheet = doc.GetSheetNames()[0];

        // Populate default sheet
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Q1");
        doc.AddRow(new List<string> { "Alice", "1000" });
        doc.AddRow(new List<string> { "Bob", "2000" });

        // AddSheet — Sales
        doc.AddSheet("Sales");
        doc.SwitchSheet("Sales");
        doc.SetCellValue(0, 0, "Product");
        doc.SetCellValue(0, 1, "Revenue");
        doc.AddRow(new List<string> { "Widget A", "5000" });
        doc.AddRow(new List<string> { "Widget B", "3000" });
        doc.AddRow(new List<string> { "Widget C", "7500" });

        // AddSheet — Summary
        doc.AddSheet("Summary");
        doc.SwitchSheet("Summary");
        doc.SetCellValue(0, 0, "Metric");
        doc.SetCellValue(0, 1, "Value");
        doc.AddRow(new List<string> { "Total Revenue", "15500" });

        // GetSheetNames — should have 3 sheets
        var names = doc.GetSheetNames();
        Assert.True(names.Count >= 3);
        Assert.Contains("Sales", names);
        Assert.Contains("Summary", names);

        // SwitchSheet to Sales and verify row count
        doc.SwitchSheet("Sales");
        Assert.Equal(3, doc.GetRowCount());

        // SwitchSheet to Summary and verify
        doc.SwitchSheet("Summary");
        Assert.Equal(1, doc.GetRowCount());

        // Switch to default and verify
        doc.SwitchSheet(defaultSheet);
        Assert.Equal(2, doc.GetRowCount());
        Assert.Equal("Alice", doc.GetCellValue(1, 0));

        // SaveToFile
        var path = TempFile("multisheet.fods");
        doc.SaveToFile(path);
        Assert.True(System.IO.File.Exists(path));

        // LoadFile and verify sheet names preserved
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);
        var loadedNames = loaded.GetSheetNames();
        Assert.True(loadedNames.Count >= 3);
        Assert.Contains("Sales", loadedNames);
        Assert.Contains("Summary", loadedNames);

        // SwitchSheet on loaded and verify data
        loaded.SwitchSheet("Sales");
        Assert.Equal(3, loaded.GetRowCount());
    }
}
