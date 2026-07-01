// Tests for FodsDocument.GetSheetProtectionPassword dedicated coverage.
// Sprint: ff-sprint-s420-dotnet-deepening-20260701
// Ledger: PC-FODS-R469

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R469: Dedicated tests for FodsDocument.GetSheetProtectionPassword().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Valid sheet returns non-null string.
/// SheetCount unchanged after GetSheetProtectionPassword.
/// Idempotent (called twice same result).
/// Return type is string.
/// SetSheetProtectionPassword + GetSheetProtectionPassword round-trips.
/// Dogfood: default sheet protection password non-null.
/// Dogfood: multiple sheets have non-null protection password.
/// </summary>
public class FodsR469GetSheetProtectionPasswordDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetProtectionPassword_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetProtectionPassword(null!));
    }

    [Fact]
    public void GetSheetProtectionPassword_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetProtectionPassword("   "));
    }

    [Fact]
    public void GetSheetProtectionPassword_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetProtectionPassword("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetProtectionPassword_ValidSheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string pwd = doc.GetSheetProtectionPassword("Sheet1");
        Assert.NotNull(pwd);
    }

    [Fact]
    public void GetSheetProtectionPassword_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetSheetProtectionPassword("Sheet1");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetProtectionPassword_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string first = doc.GetSheetProtectionPassword("Sheet1");
        string second = doc.GetSheetProtectionPassword("Sheet1");
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetProtectionPassword_IsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        object result = doc.GetSheetProtectionPassword("Sheet1");
        Assert.IsType<string>(result);
    }

    [Fact]
    public void GetSheetProtectionPassword_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Protected");
        doc.SetSheetProtectionPassword("Protected", "secret123");
        string pwd = doc.GetSheetProtectionPassword("Protected");
        Assert.Equal("secret123", pwd);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_PasswordNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        string pwd = doc.GetSheetProtectionPassword("Report");
        Assert.NotNull(pwd);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        var names = new[] { "Sheet1", "Sheet2", "Sheet3" };
        foreach (var name in names)
        {
            doc.AddSheet(name);
            Assert.NotNull(doc.GetSheetProtectionPassword(name));
        }
    }
}
