// FodsRealFileTests — Tests that load real FODS files (not CreateEmpty/CreateNew)
// and verify known content. Anchors the library against actual ODF documents.
// Sprint: depth-quality-improvement
// Purpose: Replace synthetic-only testing with real-file validation.

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// Tests loading real FODS files from samples/by-format/fods/valid/ and verifying
/// known cell values, sheet names, and document structure.
/// </summary>
public class FodsRealFileTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods/valid"));

    // -----------------------------------------------------------------
    // RF-01: Load simple.fods — verify sheet structure and cell values
    // -----------------------------------------------------------------
    [Fact]
    public void LoadSimple_HasOneSheet_Named_Sheet1()
    {
        var path = Path.Combine(SamplesDir, "simple.fods");
        var doc = FodsDocument.Load(path);

        var names = doc.GetSheetNames();
        Assert.Single(names);
        Assert.Equal("Sheet1", names[0]);
    }

    [Fact]
    public void LoadSimple_CellValues_MatchKnownContent()
    {
        var path = Path.Combine(SamplesDir, "simple.fods");
        var doc = FodsDocument.Load(path);

        // Row 0: "Name", "Value"
        Assert.Equal("Name", doc.GetCellValue("Sheet1", 0, 0));
        Assert.Equal("Value", doc.GetCellValue("Sheet1", 0, 1));

        // Row 1: "Alpha", "42"
        Assert.Equal("Alpha", doc.GetCellValue("Sheet1", 1, 0));
        Assert.Equal("42", doc.GetCellValue("Sheet1", 1, 1));
    }

    [Fact]
    public void LoadSimple_MimeType_IsCorrect()
    {
        var path = Path.Combine(SamplesDir, "simple.fods");
        var doc = FodsDocument.Load(path);

        Assert.Equal("application/vnd.oasis.opendocument.spreadsheet-flat-xml",
            doc.MimeType);
    }

    [Fact]
    public void LoadSimple_OdfVersion_Is13()
    {
        var path = Path.Combine(SamplesDir, "simple.fods");
        var doc = FodsDocument.Load(path);

        Assert.Equal("1.3", doc.OdfVersion);
    }

    // -----------------------------------------------------------------
    // RF-02: Load multi-sheet-data.fods — verify multi-sheet structure
    // -----------------------------------------------------------------
    [Fact]
    public void LoadMultiSheet_HasThreeSheets()
    {
        var path = Path.Combine(SamplesDir, "multi-sheet-data.fods");
        var doc = FodsDocument.Load(path);

        var names = doc.GetSheetNames();
        Assert.Equal(3, names.Count);
        Assert.Equal("Products", names[0]);
        Assert.Equal("Orders", names[1]);
        Assert.Equal("Summary", names[2]);
    }

    [Fact]
    public void LoadMultiSheet_ProductsSheet_CellValues()
    {
        var path = Path.Combine(SamplesDir, "multi-sheet-data.fods");
        var doc = FodsDocument.Load(path);

        // Headers
        Assert.Equal("ID", doc.GetCellValue("Products", 0, 0));
        Assert.Equal("Name", doc.GetCellValue("Products", 0, 1));
        Assert.Equal("Price", doc.GetCellValue("Products", 0, 2));

        // Data rows
        Assert.Equal("P001", doc.GetCellValue("Products", 1, 0));
        Assert.Equal("Widget", doc.GetCellValue("Products", 1, 1));
        Assert.Equal("19.99", doc.GetCellValue("Products", 1, 2));

        Assert.Equal("P002", doc.GetCellValue("Products", 2, 0));
        Assert.Equal("Gadget", doc.GetCellValue("Products", 2, 1));

        Assert.Equal("P003", doc.GetCellValue("Products", 3, 0));
        Assert.Equal("Sprocket", doc.GetCellValue("Products", 3, 1));
        Assert.Equal("5.75", doc.GetCellValue("Products", 3, 2));
    }

    [Fact]
    public void LoadMultiSheet_OrdersSheet_CellValues()
    {
        var path = Path.Combine(SamplesDir, "multi-sheet-data.fods");
        var doc = FodsDocument.Load(path);

        Assert.Equal("OrderID", doc.GetCellValue("Orders", 0, 0));
        Assert.Equal("ORD-100", doc.GetCellValue("Orders", 1, 0));
        Assert.Equal("P001", doc.GetCellValue("Orders", 1, 1));
        Assert.Equal("3", doc.GetCellValue("Orders", 1, 2));
        Assert.Equal("ORD-101", doc.GetCellValue("Orders", 2, 0));
        Assert.Equal("12", doc.GetCellValue("Orders", 2, 2));
    }

    [Fact]
    public void LoadMultiSheet_SummarySheet_CellValues()
    {
        var path = Path.Combine(SamplesDir, "multi-sheet-data.fods");
        var doc = FodsDocument.Load(path);

        Assert.Equal("Total Products", doc.GetCellValue("Summary", 0, 0));
        Assert.Equal("3", doc.GetCellValue("Summary", 0, 1));
    }

    // -----------------------------------------------------------------
    // RF-03: Roundtrip a real file — load → save → reload → verify
    // -----------------------------------------------------------------
    [Fact]
    public void LoadMultiSheet_RoundtripPreservesContent()
    {
        var path = Path.Combine(SamplesDir, "multi-sheet-data.fods");
        var doc = FodsDocument.Load(path);

        // Roundtrip through XML serialization
        string xml = doc.ToFodsXml();
        var reloaded = FodsDocument.LoadFromXml(xml);

        // Verify structure preserved
        var names = reloaded.GetSheetNames();
        Assert.Equal(3, names.Count);
        Assert.Equal("Products", names[0]);
        Assert.Equal("Orders", names[1]);
        Assert.Equal("Summary", names[2]);

        // Verify cell values preserved
        Assert.Equal("Widget", reloaded.GetCellValue("Products", 1, 1));
        Assert.Equal("ORD-101", reloaded.GetCellValue("Orders", 2, 0));
        Assert.Equal("3", reloaded.GetCellValue("Summary", 0, 1));
    }

    // -----------------------------------------------------------------
    // RF-04: Mutate a real file and verify mutations
    // -----------------------------------------------------------------
    [Fact]
    public void LoadMultiSheet_MutateAndRoundtrip()
    {
        var path = Path.Combine(SamplesDir, "multi-sheet-data.fods");
        var doc = FodsDocument.Load(path);

        // Add a new product
        doc.SetCellValue("Products", 4, 0, "P004");
        doc.SetCellValue("Products", 4, 1, "Thingamajig");
        doc.SetCellValue("Products", 4, 2, "12.00");

        // Update summary
        doc.SetCellValue("Summary", 0, 1, "4");

        // Roundtrip
        string xml = doc.ToFodsXml();
        var reloaded = FodsDocument.LoadFromXml(xml);

        // Original data preserved
        Assert.Equal("Widget", reloaded.GetCellValue("Products", 1, 1));

        // New data persisted
        Assert.Equal("P004", reloaded.GetCellValue("Products", 4, 0));
        Assert.Equal("Thingamajig", reloaded.GetCellValue("Products", 4, 1));
        Assert.Equal("12.00", reloaded.GetCellValue("Products", 4, 2));

        // Updated summary
        Assert.Equal("4", reloaded.GetCellValue("Summary", 0, 1));
    }
}
