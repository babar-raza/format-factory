// Tests for FodsDocument.CopySheet dedicated coverage.
// Sprint: ff-sprint-s152-dotnet-deepening-20260628
// Ledger: PC-FODS-R159

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R159: Dedicated tests for FodsDocument.CopySheet(string sourceName, string newName).
/// CopySheet copies the source sheet to a new sheet with the given name.
/// Throws ArgumentException for null/whitespace sourceName or newName.
/// Throws InvalidOperationException if sourceName does not exist or newName already exists.
/// Covers: null sourceName throws ArgumentException; whitespace sourceName throws ArgumentException;
/// null newName throws ArgumentException; whitespace newName throws ArgumentException;
/// nonexistent sourceName throws InvalidOperationException;
/// duplicate newName throws InvalidOperationException;
/// sheet count increases after copy; new sheet appears in GetSheetNames;
/// dogfood CreateNew->AddSheet->SetCellValue->CopySheet pipeline;
/// dogfood copy preserves source sheet and adds new sheet.
/// </summary>
public class FodsR159CopySheetDedicatedTests
{
    private static FodsDocument MakeDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Source");
        doc.SetCellValue("Source", 0, 0, "Original");
        return doc;
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CopySheet_NullSourceName_ThrowsArgumentException()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() => doc.CopySheet(null!, "Copy"));
    }

    [Fact]
    public void CopySheet_WhitespaceSourceName_ThrowsArgumentException()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() => doc.CopySheet("   ", "Copy"));
    }

    [Fact]
    public void CopySheet_NullNewName_ThrowsArgumentException()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() => doc.CopySheet("Source", null!));
    }

    [Fact]
    public void CopySheet_WhitespaceNewName_ThrowsArgumentException()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() => doc.CopySheet("Source", "   "));
    }

    [Fact]
    public void CopySheet_NonexistentSourceName_ThrowsInvalidOperationException()
    {
        var doc = MakeDoc();
        Assert.Throws<InvalidOperationException>(() => doc.CopySheet("NoSheet", "Copy"));
    }

    [Fact]
    public void CopySheet_DuplicateNewName_ThrowsInvalidOperationException()
    {
        var doc = MakeDoc();
        doc.AddSheet("ExistingSheet");
        Assert.Throws<InvalidOperationException>(() => doc.CopySheet("Source", "ExistingSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CopySheet_SheetCountIncreases()
    {
        var doc = MakeDoc();
        var before = doc.GetSheetNames().Count;
        doc.CopySheet("Source", "CopyOfSource");
        var after = doc.GetSheetNames().Count;
        Assert.Equal(before + 1, after);
    }

    [Fact]
    public void CopySheet_NewSheetAppearsInGetSheetNames()
    {
        var doc = MakeDoc();
        doc.CopySheet("Source", "MyCopy");
        var names = doc.GetSheetNames();
        Assert.Contains("MyCopy", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_SetCellValue_CopySheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Name");
        doc.SetCellValue("Data", 0, 1, "Score");
        doc.CopySheet("Data", "DataBackup");
        var names = doc.GetSheetNames();
        Assert.Contains("DataBackup", names);
        Assert.Contains("Data", names);
    }

    [Fact]
    public void DogfoodPipeline_CopySheet_PreservesSourceAndAddsNew()
    {
        var doc = MakeDoc();
        doc.CopySheet("Source", "Duplicate");
        var names = doc.GetSheetNames();
        // Both source and copy should exist
        Assert.Contains("Source", names);
        Assert.Contains("Duplicate", names);
        Assert.Equal(2, names.Count);
    }
}
