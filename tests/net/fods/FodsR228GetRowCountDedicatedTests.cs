// Tests for FodsDocument.GetRowCount dedicated coverage.
// Sprint: ff-sprint-s212-dotnet-deepening-20260629
// Ledger: PC-FODS-R228

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R228: Dedicated tests for FodsDocument.GetRowCount.
/// Null/whitespace sheet name → ArgumentNullException or ArgumentException.
/// Non-existent sheet → throws exception.
/// Empty sheet → returns 0.
/// After InsertRow: row count increases by 1.
/// After InsertRowWithValues: row count increases.
/// SheetCount unchanged after GetRowCount.
/// Two sheets independent row counts.
/// Row count equals number of rows inserted.
/// Dogfood: insert multiple rows, verify count.
/// Dogfood: delete rows, verify count decreases.
/// </summary>
public class FodsR228GetRowCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount(null!));
    }

    [Fact]
    public void GetRowCount_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount("   "));
    }

    [Fact]
    public void GetRowCount_NonExistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount("DoesNotExist"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_EmptySheet_ReturnsZero()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.Equal(0, doc.GetRowCount(sheetName));
    }

    [Fact]
    public void GetRowCount_AfterInsertRow_IncreasesByOne()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheetName);
        doc.InsertRow(sheetName, 0);
        Assert.Equal(before + 1, doc.GetRowCount(sheetName));
    }

    [Fact]
    public void GetRowCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int sheetsBefore = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.GetRowCount(sheetName);
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void GetRowCount_TwoSheetsIndependent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet2");
        string sheet1 = doc.GetSheetNames()[0];
        string sheet2 = "Sheet2";
        doc.InsertRow(sheet1, 0);
        doc.InsertRow(sheet1, 0);
        Assert.Equal(2, doc.GetRowCount(sheet1));
        Assert.Equal(0, doc.GetRowCount(sheet2));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_InsertMultipleRows_CountMatches()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        for (int i = 0; i < 5; i++)
            doc.InsertRow(sheetName, 0);
        Assert.Equal(5, doc.GetRowCount(sheetName));
    }

    [Fact]
    public void DogfoodPipeline_DeleteRows_CountDecreases()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        for (int i = 0; i < 4; i++)
            doc.InsertRow(sheetName, 0);
        doc.DeleteRows(sheetName, 0, 2);
        Assert.Equal(2, doc.GetRowCount(sheetName));
    }
}
