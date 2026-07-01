// Tests for FodsDocument.GetSheetShowHeaders dedicated coverage.
// Sprint: ff-sprint-s434-dotnet-deepening-20260701
// Ledger: PC-FODS-R483

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R483: Dedicated tests for FodsDocument.GetSheetShowHeaders(string sheetName).
/// Null/whitespace/nonexistent sheet name throws.
/// Valid sheet returns bool.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is bool.
/// Dogfood: default sheet and multiple sheets no exception.
/// </summary>
public class FodsR483GetSheetShowHeadersDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetShowHeaders_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetShowHeaders(null!));
    }

    [Fact]
    public void GetSheetShowHeaders_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetShowHeaders("   "));
    }

    [Fact]
    public void GetSheetShowHeaders_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetShowHeaders("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetShowHeaders_ValidSheet_ReturnsBool()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        object result = doc.GetSheetShowHeaders(sheet);
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void GetSheetShowHeaders_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheet = doc.GetSheetNames()[0];
        _ = doc.GetSheetShowHeaders(sheet);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetShowHeaders_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        bool first = doc.GetSheetShowHeaders(sheet);
        bool second = doc.GetSheetShowHeaders(sheet);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetShowHeaders_IsBool()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        object result = doc.GetSheetShowHeaders(sheet);
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
        var ex = Record.Exception(() => doc.GetSheetShowHeaders(sheet));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        foreach (string sheet in doc.GetSheetNames())
        {
            var ex = Record.Exception(() => doc.GetSheetShowHeaders(sheet));
            Assert.Null(ex);
        }
    }
}
