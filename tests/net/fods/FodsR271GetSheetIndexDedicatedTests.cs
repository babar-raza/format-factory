// Tests for FodsDocument.GetSheetIndex dedicated coverage.
// Sprint: ff-sprint-s252-dotnet-deepening-20260630
// Ledger: PC-FODS-R271

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R271: Dedicated tests for FodsDocument.GetSheetIndex(sheetName).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// First sheet → returns 0.
/// After AddSheet second sheet → returns 1.
/// SheetCount unchanged.
/// Called twice → same result.
/// Dogfood: add 3 sheets, verify indices 0/1/2.
/// Dogfood: GetSheetIndex and GetSheetNames are consistent.
/// </summary>
public class FodsR271GetSheetIndexDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetIndex_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetIndex(null!));
    }

    [Fact]
    public void GetSheetIndex_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetIndex("   "));
    }

    [Fact]
    public void GetSheetIndex_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetIndex("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetIndex_FirstSheet_ReturnsZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string firstSheet = doc.GetSheetNames()[0];
        int index = doc.GetSheetIndex(firstSheet);
        Assert.Equal(0, index);
    }

    [Fact]
    public void GetSheetIndex_SecondSheet_ReturnsOne()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("SecondSheet");
        int index = doc.GetSheetIndex("SecondSheet");
        Assert.Equal(1, index);
    }

    [Fact]
    public void GetSheetIndex_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        int before = doc.SheetCount;
        doc.GetSheetIndex(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetIndex_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        int first = doc.GetSheetIndex(sheetName);
        int second = doc.GetSheetIndex(sheetName);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ThreeSheets_VerifyIndices()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet0 = doc.GetSheetNames()[0];
        doc.AddSheet("SheetB");
        doc.AddSheet("SheetC");
        Assert.Equal(0, doc.GetSheetIndex(sheet0));
        Assert.Equal(1, doc.GetSheetIndex("SheetB"));
        Assert.Equal(2, doc.GetSheetIndex("SheetC"));
    }

    [Fact]
    public void DogfoodPipeline_GetSheetIndexConsistentWithGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Extra");
        var names = doc.GetSheetNames();
        for (int i = 0; i < names.Count; i++)
        {
            int idx = doc.GetSheetIndex(names[i]);
            Assert.Equal(i, idx);
        }
    }
}
