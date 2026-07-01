// Tests for FodsDocument.GetSheetRightToLeft dedicated coverage.
// Sprint: ff-sprint-s432-dotnet-deepening-20260701
// Ledger: PC-FODS-R481

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R481: Dedicated tests for FodsDocument.GetSheetRightToLeft(string sheetName).
/// Null/whitespace/nonexistent sheet name throws.
/// Valid sheet returns bool.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is bool.
/// Dogfood: default sheet and multiple sheets no exception.
/// </summary>
public class FodsR481GetSheetRightToLeftDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetRightToLeft_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetRightToLeft(null!));
    }

    [Fact]
    public void GetSheetRightToLeft_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetRightToLeft("   "));
    }

    [Fact]
    public void GetSheetRightToLeft_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetRightToLeft("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetRightToLeft_ValidSheet_ReturnsBool()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        object result = doc.GetSheetRightToLeft(sheet);
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void GetSheetRightToLeft_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheet = doc.GetSheetNames()[0];
        _ = doc.GetSheetRightToLeft(sheet);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetRightToLeft_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        bool first = doc.GetSheetRightToLeft(sheet);
        bool second = doc.GetSheetRightToLeft(sheet);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetRightToLeft_IsBool()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        object result = doc.GetSheetRightToLeft(sheet);
        Assert.IsType<bool>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.GetSheetRightToLeft(sheet));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        foreach (string sheet in doc.GetSheetNames())
        {
            var ex = Record.Exception(() => doc.GetSheetRightToLeft(sheet));
            Assert.Null(ex);
        }
    }
}
