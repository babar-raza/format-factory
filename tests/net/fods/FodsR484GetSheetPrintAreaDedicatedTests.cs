// Tests for FodsDocument.GetSheetPrintArea dedicated coverage.
// Sprint: ff-sprint-s435-dotnet-deepening-20260701
// Ledger: PC-FODS-R484

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R484: Dedicated tests for FodsDocument.GetSheetPrintArea(string sheetName).
/// Null/whitespace/nonexistent sheet name throws.
/// Valid sheet returns non-null string.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is string.
/// Dogfood: default sheet and multiple sheets no exception.
/// </summary>
public class FodsR484GetSheetPrintAreaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetPrintArea_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetPrintArea(null!));
    }

    [Fact]
    public void GetSheetPrintArea_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetPrintArea("   "));
    }

    [Fact]
    public void GetSheetPrintArea_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetPrintArea("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetPrintArea_ValidSheet_ReturnsNotNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        string result = doc.GetSheetPrintArea(sheet);
        Assert.NotNull(result);
    }

    [Fact]
    public void GetSheetPrintArea_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheet = doc.GetSheetNames()[0];
        _ = doc.GetSheetPrintArea(sheet);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetPrintArea_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        string first = doc.GetSheetPrintArea(sheet);
        string second = doc.GetSheetPrintArea(sheet);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetPrintArea_IsString()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        object result = doc.GetSheetPrintArea(sheet);
        Assert.IsType<string>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.GetSheetPrintArea(sheet));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        foreach (string sheet in doc.GetSheetNames())
        {
            var ex = Record.Exception(() => doc.GetSheetPrintArea(sheet));
            Assert.Null(ex);
        }
    }
}
