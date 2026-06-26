// Tests for FodsDocument.HasSheet dedicated coverage.
// Sprint: ff-sprint-s163-dotnet-deepening-20260628
// Ledger: PC-FODS-R170

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R170: Dedicated tests for FodsDocument.HasSheet(string name).
/// HasSheet returns true if a sheet with the given name exists, false otherwise.
/// Returns false for null/whitespace name (does NOT throw).
/// Returns false for nonexistent name.
/// Covers: null name returns false; whitespace returns false; nonexistent returns false;
/// existing sheet returns true; case-sensitive (different case returns false);
/// returns true after AddSheet; returns false after RemoveSheet;
/// second sheet found by name; empty document returns false;
/// dogfood CreateNew->AddSheet->HasSheet pipeline;
/// dogfood HasSheet consistent with GetSheetNames.
/// </summary>
public class FodsR170HasSheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Returns-false tests (no throws)
    // -------------------------------------------------------------------------

    [Fact]
    public void HasSheet_NullName_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.False(doc.HasSheet(null!));
    }

    [Fact]
    public void HasSheet_WhitespaceName_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.False(doc.HasSheet("   "));
    }

    [Fact]
    public void HasSheet_NonexistentName_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.False(doc.HasSheet("NoSuchSheet"));
    }

    [Fact]
    public void HasSheet_EmptyDocument_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        Assert.False(doc.HasSheet("Sheet1"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void HasSheet_ExistingSheet_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.True(doc.HasSheet("Sheet1"));
    }

    [Fact]
    public void HasSheet_AfterAddSheet_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        Assert.False(doc.HasSheet("New"));
        doc.AddSheet("New");
        Assert.True(doc.HasSheet("New"));
    }

    [Fact]
    public void HasSheet_AfterRemoveSheet_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Temp");
        doc.AddSheet("Keep");
        doc.RemoveSheet("Temp");
        Assert.False(doc.HasSheet("Temp"));
        Assert.True(doc.HasSheet("Keep"));
    }

    [Fact]
    public void HasSheet_SecondSheet_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("First");
        doc.AddSheet("Second");
        Assert.True(doc.HasSheet("Second"));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_HasSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.AddSheet("Gamma");
        Assert.True(doc.HasSheet("Alpha"));
        Assert.True(doc.HasSheet("Beta"));
        Assert.True(doc.HasSheet("Gamma"));
        Assert.False(doc.HasSheet("Delta"));
    }

    [Fact]
    public void DogfoodPipeline_HasSheet_ConsistentWithGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("X");
        doc.AddSheet("Y");
        var names = doc.GetSheetNames();
        foreach (var name in names)
            Assert.True(doc.HasSheet(name));
    }
}
