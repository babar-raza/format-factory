// Tests for FodsDocument.ToFodsXml, OdfVersion, MimeType deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R208

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R208: Tests for FodsDocument.ToFodsXml, OdfVersion, MimeType deeper coverage.
/// ToFodsXml(): serializes the document to an FODS XML string.
/// OdfVersion: the ODF version string (e.g., "1.3").
/// MimeType: the MIME type string for FODS format.
/// Covers: ToFodsXml non-null; ToFodsXml non-empty; ToFodsXml contains XML tags;
/// ToFodsXml contains cell data; ToFodsXml contains spreadsheet structure;
/// ToFodsXml after SetCellValue reflects data; ToFodsXml load round-trip count preserved;
/// OdfVersion non-null; OdfVersion non-empty; OdfVersion contains version number;
/// MimeType non-null; MimeType non-empty; MimeType contains spreadsheet;
/// MimeType contains oasis; ToFodsXml length increases with more data;
/// dogfood CreateEmpty->SetCellValues->ToFodsXml->OdfVersion->MimeType->Load->verify.
/// </summary>
public class FodsR208ToFodsXmlAndOdfVersionDeepTests
{
    private static FodsDocument CreatePopulatedDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Product");
        doc.SetCellValue("Sheet1", 0, 1, "Price");
        doc.SetCellValue("Sheet1", 1, 0, "Widget A");
        doc.SetCellValue("Sheet1", 1, 1, "9.99");
        doc.SetCellValue("Sheet1", 2, 0, "Widget B");
        doc.SetCellValue("Sheet1", 2, 1, "19.99");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ToFodsXml
    // -------------------------------------------------------------------------

    [Fact]
    public void ToFodsXml_NonNull()
    {
        var doc = CreatePopulatedDoc();
        Assert.NotNull(doc.ToFodsXml());
    }

    [Fact]
    public void ToFodsXml_NonEmpty()
    {
        var doc = CreatePopulatedDoc();
        Assert.False(string.IsNullOrWhiteSpace(doc.ToFodsXml()));
    }

    [Fact]
    public void ToFodsXml_ContainsXmlTags()
    {
        var doc = CreatePopulatedDoc();
        var xml = doc.ToFodsXml();
        Assert.Contains("<", xml);
        Assert.Contains(">", xml);
    }

    [Fact]
    public void ToFodsXml_ContainsCellData()
    {
        var doc = CreatePopulatedDoc();
        var xml = doc.ToFodsXml();
        Assert.Contains("Widget A", xml);
        Assert.Contains("Widget B", xml);
        Assert.Contains("9.99", xml);
    }

    [Fact]
    public void ToFodsXml_ContainsSpreadsheetStructure()
    {
        var doc = CreatePopulatedDoc();
        var xml = doc.ToFodsXml();
        // Should have office or spreadsheet namespace markers
        Assert.True(xml.Contains("office") || xml.Contains("spreadsheet") || xml.Contains("table"));
    }

    [Fact]
    public void ToFodsXml_AfterSetCellValue_ReflectsData()
    {
        var doc = CreatePopulatedDoc();
        doc.SetCellValue("Sheet1", 3, 0, "Widget C");
        var xml = doc.ToFodsXml();
        Assert.Contains("Widget C", xml);
    }

    [Fact]
    public void ToFodsXml_LoadRoundTrip_CountPreserved()
    {
        var doc = CreatePopulatedDoc();
        var xml = doc.ToFodsXml();
        var loaded = FodsDocument.Load(xml);
        Assert.Equal(doc.GetRowCount("Sheet1"), loaded.GetRowCount("Sheet1"));
    }

    [Fact]
    public void ToFodsXml_LengthIncreasesWithMoreData()
    {
        var docSmall = FodsDocument.CreateEmpty();
        docSmall.AddSheet("Sheet1");
        docSmall.SetCellValue("Sheet1", 0, 0, "A");
        var xmlSmall = docSmall.ToFodsXml();

        var docLarge = FodsDocument.CreateEmpty();
        docLarge.AddSheet("Sheet1");
        for (var i = 0; i < 10; i++)
            docLarge.SetCellValue("Sheet1", i, 0, $"Value {i}");
        var xmlLarge = docLarge.ToFodsXml();

        Assert.True(xmlLarge.Length >= xmlSmall.Length);
    }

    // -------------------------------------------------------------------------
    // OdfVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void OdfVersion_NonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        Assert.NotNull(doc.OdfVersion);
    }

    [Fact]
    public void OdfVersion_NonEmpty()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        Assert.False(string.IsNullOrWhiteSpace(doc.OdfVersion));
    }

    [Fact]
    public void OdfVersion_ContainsVersionNumber()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        // Should contain a version number like "1.3" or "1.2"
        Assert.True(doc.OdfVersion.Contains("1") || doc.OdfVersion.Contains("2"));
    }

    // -------------------------------------------------------------------------
    // MimeType
    // -------------------------------------------------------------------------

    [Fact]
    public void MimeType_NonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        Assert.NotNull(doc.MimeType);
    }

    [Fact]
    public void MimeType_NonEmpty()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        Assert.False(string.IsNullOrWhiteSpace(doc.MimeType));
    }

    [Fact]
    public void MimeType_ContainsSpreadsheetOrCalc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        var mt = doc.MimeType.ToLowerInvariant();
        Assert.True(mt.Contains("spreadsheet") || mt.Contains("calc") || mt.Contains("oasis"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetCellValuesToFodsXmlOdfVersionMimeTypeLoadVerify_Pipeline()
    {
        // Create document with data
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Name");
        doc.SetCellValue("Sheet1", 0, 1, "Score");
        doc.SetCellValue("Sheet1", 1, 0, "Alice");
        doc.SetCellValue("Sheet1", 1, 1, "95");
        doc.SetCellValue("Sheet1", 2, 0, "Bob");
        doc.SetCellValue("Sheet1", 2, 1, "82");

        // OdfVersion
        Assert.NotNull(doc.OdfVersion);
        Assert.False(string.IsNullOrWhiteSpace(doc.OdfVersion));

        // MimeType
        Assert.NotNull(doc.MimeType);
        Assert.False(string.IsNullOrWhiteSpace(doc.MimeType));

        // ToFodsXml
        var xml = doc.ToFodsXml();
        Assert.NotNull(xml);
        Assert.Contains("Alice", xml);
        Assert.Contains("95", xml);
        Assert.Contains("<", xml);

        // Load from XML
        var loaded = FodsDocument.Load(xml);
        Assert.NotNull(loaded);
        Assert.Equal(doc.GetRowCount("Sheet1"), loaded.GetRowCount("Sheet1"));

        // Verify loaded values
        Assert.Equal("Alice", loaded.GetCellValue("Sheet1", 1, 0));
        Assert.Equal("95", loaded.GetCellValue("Sheet1", 1, 1));
    }
}
