// Tests for FodsDocument.HasColumn dedicated coverage.
// Sprint: ff-sprint-s232-dotnet-deepening-20260629
// Ledger: PC-FODS-R250

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R250: Dedicated tests for FodsDocument.HasColumn(sheetName, columnName).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Empty sheet → returns false for any column name.
/// Returns false for nonexistent column.
/// Returns true for existing column header.
/// SheetCount unchanged after call.
/// After AddRow with header, returns true.
/// Called twice returns same value.
/// Dogfood: set headers, verify HasColumn reflects all.
/// </summary>
public class FodsR250HasColumnDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.HasColumn(null!, "ColA"));
    }

    [Fact]
    public void HasColumn_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.HasColumn("   ", "ColA"));
    }

    [Fact]
    public void HasColumn_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.HasColumn("NoSuchSheet", "ColA"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_EmptySheet_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.False(doc.HasColumn(sheetName, "AnyColumn"));
    }

    [Fact]
    public void HasColumn_NonexistentColumn_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Name", "Age" });
        Assert.False(doc.HasColumn(sheetName, "Salary"));
    }

    [Fact]
    public void HasColumn_ExistingColumn_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Name", "Age", "City" });
        Assert.True(doc.HasColumn(sheetName, "Name"));
    }

    [Fact]
    public void HasColumn_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        _ = doc.HasColumn(sheetName, "ColA");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void HasColumn_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Product", "Price" });
        bool first = doc.HasColumn(sheetName, "Product");
        bool second = doc.HasColumn(sheetName, "Product");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetHeaders_HasColumnReflectsAll()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "ID", "FirstName", "LastName", "Email" });
        Assert.True(doc.HasColumn(sheetName, "ID"));
        Assert.True(doc.HasColumn(sheetName, "FirstName"));
        Assert.True(doc.HasColumn(sheetName, "LastName"));
        Assert.True(doc.HasColumn(sheetName, "Email"));
        Assert.False(doc.HasColumn(sheetName, "Phone"));
    }
}
