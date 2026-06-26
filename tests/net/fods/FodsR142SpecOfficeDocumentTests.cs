// Tests for FormatFactory.Fods.Spec.Office.Document canonical spec-shaped model class.
// Sprint: FORMAT-FACTORY-FODS-R142-20260627
// Ledger: R142-GOVERNED-DOTNET-FODS-SPEC-OFFICE-DOCUMENT-001

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R142: Tests for the canonical spec-shaped model class
/// FormatFactory.Fods.Spec.Office.Document.
/// Document (office:document, FACT-FODS-001) is the root element of a flat ODF
/// spreadsheet (.fods). It carries MimeType ("application/vnd.oasis.opendocument.spreadsheet"),
/// Version (e.g. "1.3"), and SheetCount.
/// Covers: SpecQName constant; SpecFactRef constant; MimeType default value;
/// Version property assignable and null by default; SheetCount assignable;
/// MimeType assignable; dogfood multi-property composition.
/// ODF 1.3 basis: §3.1.2 — office:document root element.
/// </summary>
public class FodsR142SpecOfficeDocumentTests
{
    // -------------------------------------------------------------------------
    // Constants
    // -------------------------------------------------------------------------

    [Fact]
    public void Document_SpecQName_IsCorrect()
    {
        Assert.Equal("office:document", Spec.Office.Document.SpecQName);
    }

    [Fact]
    public void Document_SpecFactRef_IsCorrect()
    {
        Assert.Equal("FACT-FODS-001", Spec.Office.Document.SpecFactRef);
    }

    // -------------------------------------------------------------------------
    // MimeType property
    // -------------------------------------------------------------------------

    [Fact]
    public void Document_MimeType_DefaultIsFodsSpreadsheetMime()
    {
        var doc = new Spec.Office.Document();
        Assert.Equal("application/vnd.oasis.opendocument.spreadsheet", doc.MimeType);
    }

    [Fact]
    public void Document_MimeType_IsAssignable()
    {
        var doc = new Spec.Office.Document { MimeType = "application/octet-stream" };
        Assert.Equal("application/octet-stream", doc.MimeType);
    }

    // -------------------------------------------------------------------------
    // Version property
    // -------------------------------------------------------------------------

    [Fact]
    public void Document_Version_NullByDefault()
    {
        var doc = new Spec.Office.Document();
        Assert.Null(doc.Version);
    }

    [Fact]
    public void Document_Version_IsAssignable()
    {
        var doc = new Spec.Office.Document { Version = "1.3" };
        Assert.Equal("1.3", doc.Version);
    }

    // -------------------------------------------------------------------------
    // SheetCount property
    // -------------------------------------------------------------------------

    [Fact]
    public void Document_SheetCount_DefaultIsZero()
    {
        var doc = new Spec.Office.Document();
        Assert.Equal(0, doc.SheetCount);
    }

    [Fact]
    public void Document_SheetCount_IsAssignable()
    {
        var doc = new Spec.Office.Document { SheetCount = 3 };
        Assert.Equal(3, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: multi-property composition
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiPropertyComposition()
    {
        var doc = new Spec.Office.Document
        {
            MimeType   = "application/vnd.oasis.opendocument.spreadsheet",
            Version    = "1.3",
            SheetCount = 2,
        };

        Assert.Equal("office:document",    Spec.Office.Document.SpecQName);
        Assert.Equal("FACT-FODS-001",      Spec.Office.Document.SpecFactRef);
        Assert.Equal("1.3",                doc.Version);
        Assert.Equal(2,                    doc.SheetCount);
        Assert.Contains("spreadsheet",     doc.MimeType);
    }
}
