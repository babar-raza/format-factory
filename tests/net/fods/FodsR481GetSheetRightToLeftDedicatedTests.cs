// Tests for FodsDocument.GetSheetRightToLeft dedicated coverage.
// Sprint: ff-sprint-s432-dotnet-deepening-20260701 (updated TC-FGSQ-015: NSE conversion)
// Ledger: PC-FODS-R481
// TC-FGSQ-015: GetSheetRightToLeft converted to NotSupportedException.
// ODF 1.3 §15.3.5: style:writing-mode is a style attribute, not a config:config-item.
// No standard per-sheet RTL config path exists — honest NotSupportedException.

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R481: Dedicated tests for FodsDocument.GetSheetRightToLeft(string sheetName).
/// Null/whitespace/nonexistent sheet name throws ArgumentException (guard).
/// Valid sheet throws NotSupportedException (TC-FGSQ-015: ODF has no config path for RTL).
/// Calling twice throws same exception (deterministic).
/// </summary>
public class FodsR481GetSheetRightToLeftDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests (unchanged — still throw via RequireSheet)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetRightToLeft_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetRightToLeft(null!));
    }

    [Fact]
    public void GetSheetRightToLeft_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetRightToLeft("   "));
    }

    [Fact]
    public void GetSheetRightToLeft_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetRightToLeft("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // TC-FGSQ-015: Valid sheet → NotSupportedException (ODF has no RTL config path)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetRightToLeft_ValidSheet_ThrowsNotSupportedException()
    {
        // TC-FGSQ-015: ODF 1.3 §15.3.5 — style:writing-mode is a style attribute,
        // not a config:config-item. No per-sheet RTL config exists in ODF.
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        Assert.Throws<NotSupportedException>(() => doc.GetSheetRightToLeft(sheet));
    }

    [Fact]
    public void GetSheetRightToLeft_SheetCountUnchanged_AfterNse()
    {
        // SheetCount must be unchanged even when NSE is thrown
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheet = doc.GetSheetNames()[0];
        Assert.Throws<NotSupportedException>(() => doc.GetSheetRightToLeft(sheet));
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetRightToLeft_Idempotent_BothThrow()
    {
        // TC-FGSQ-015: calling twice both throw NotSupportedException (deterministic)
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        Assert.Throws<NotSupportedException>(() => doc.GetSheetRightToLeft(sheet));
        Assert.Throws<NotSupportedException>(() => doc.GetSheetRightToLeft(sheet));
    }

    [Fact]
    public void GetSheetRightToLeft_MessageMentionsOdf()
    {
        // Exception message should cite ODF spec for diagnosability
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        var ex = Assert.Throws<NotSupportedException>(() => doc.GetSheetRightToLeft(sheet));
        Assert.Contains("ODF", ex.Message, StringComparison.OrdinalIgnoreCase);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline (updated: NSE is expected, not a pipeline failure)
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_ThrowsNotSupportedException()
    {
        // TC-FGSQ-015: dogfood confirms NSE is thrown (not a crash — expected behavior)
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        Assert.Throws<NotSupportedException>(() => doc.GetSheetRightToLeft(sheet));
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllThrowNotSupportedException()
    {
        // TC-FGSQ-015: every sheet throws NSE (feature not supported regardless of sheet)
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Extra");
        foreach (string sheet in doc.GetSheetNames())
        {
            Assert.Throws<NotSupportedException>(() => doc.GetSheetRightToLeft(sheet));
        }
    }
}
