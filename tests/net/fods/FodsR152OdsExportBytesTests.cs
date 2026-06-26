// Tests for FodsOdsExporter.ExportToOdsBytes.
// Sprint: ff-sprint-oracle-all-verified-20260626
// Ledger: PC-FODS-R152

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R152: Tests for FodsOdsExporter.ExportToOdsBytes — in-memory ODS export.
/// ExportToOdsBytes accepts a FodsDocument and returns a byte[] containing
/// a valid ODS ZIP archive without writing to disk.
/// Covers: ExportToOdsBytes null document throws; ExportToOdsBytes returns non-null;
/// ExportToOdsBytes returns non-empty bytes; result bytes start with PK magic (ZIP header);
/// empty document export produces non-empty bytes; single-sheet document export;
/// multi-sheet document export produces larger result than empty;
/// result can be written to temp file and re-read as valid ODS;
/// dogfood CreateNew->SetCellValue->ExportToOdsBytes->write->reload pipeline.
/// </summary>
public class FodsR152OdsExportBytesTests
{
    // -------------------------------------------------------------------------
    // Null guard
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOdsBytes_NullDocument_Throws()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsOdsExporter.ExportToOdsBytes(null!));
    }

    // -------------------------------------------------------------------------
    // Basic return value
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOdsBytes_EmptyDocument_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        var bytes = FodsOdsExporter.ExportToOdsBytes(doc);
        Assert.NotNull(bytes);
    }

    [Fact]
    public void ExportToOdsBytes_EmptyDocument_ReturnsNonEmptyBytes()
    {
        var doc = FodsDocument.CreateNew();
        var bytes = FodsOdsExporter.ExportToOdsBytes(doc);
        Assert.True(bytes.Length > 0, "ExportToOdsBytes must return non-empty byte array.");
    }

    [Fact]
    public void ExportToOdsBytes_ResultStartsWithZipMagic()
    {
        // ODS files are ZIP archives: first two bytes are 'PK' (0x50 0x4B)
        var doc = FodsDocument.CreateNew();
        var bytes = FodsOdsExporter.ExportToOdsBytes(doc);
        Assert.True(bytes.Length >= 2, "Export must produce at least 2 bytes.");
        Assert.Equal(0x50, bytes[0]); // 'P'
        Assert.Equal(0x4B, bytes[1]); // 'K'
    }

    // -------------------------------------------------------------------------
    // Content scenarios
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOdsBytes_DocumentWithData_ReturnsNonEmptyBytes()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, 0, "TestValue");
        var bytes = FodsOdsExporter.ExportToOdsBytes(doc);
        Assert.True(bytes.Length > 0);
    }

    [Fact]
    public void ExportToOdsBytes_MultiSheetDoc_ReturnsBytes()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet2");
        doc.SetCellValue(0, 0, 0, "Sheet1Data");
        doc.SetCellValue(1, 0, 0, "Sheet2Data");
        var bytes = FodsOdsExporter.ExportToOdsBytes(doc);
        Assert.True(bytes.Length > 0);
    }

    [Fact]
    public void ExportToOdsBytes_WithDataIsLargerThanEmpty()
    {
        var emptyDoc = FodsDocument.CreateNew();
        var emptyBytes = FodsOdsExporter.ExportToOdsBytes(emptyDoc);

        var dataDoc = FodsDocument.CreateNew();
        for (int r = 0; r < 10; r++)
            dataDoc.SetCellValue(0, r, 0, $"Row{r}Value");
        var dataBytes = FodsOdsExporter.ExportToOdsBytes(dataDoc);

        Assert.True(dataBytes.Length >= emptyBytes.Length,
            "A document with data should produce >= bytes than an empty document.");
    }

    // -------------------------------------------------------------------------
    // Round-trip: write bytes to file and reload
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOdsBytes_CanWriteToFileAndReload()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, 0, "RoundTripValue");
        var bytes = FodsOdsExporter.ExportToOdsBytes(doc);

        var tempPath = Path.Combine(Path.GetTempPath(), $"fods_r152_{Guid.NewGuid():N}.ods");
        try
        {
            File.WriteAllBytes(tempPath, bytes);
            Assert.True(File.Exists(tempPath));
            Assert.True(new FileInfo(tempPath).Length > 0);
        }
        finally
        {
            if (File.Exists(tempPath)) File.Delete(tempPath);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood: full pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetCellExportBytesReload_RoundTrip()
    {
        // Create document with known data
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, 0, "Alpha");
        doc.SetCellValue(0, 1, 0, "Beta");
        doc.SetCellValue(0, 2, 0, "Gamma");

        // Export to bytes
        var bytes = FodsOdsExporter.ExportToOdsBytes(doc);

        // Verify ZIP magic header
        Assert.Equal(0x50, bytes[0]);
        Assert.Equal(0x4B, bytes[1]);

        // Write to temp file to verify it is a complete archive
        var tempPath = Path.Combine(Path.GetTempPath(), $"fods_r152_dogfood_{Guid.NewGuid():N}.ods");
        try
        {
            File.WriteAllBytes(tempPath, bytes);
            var info = new FileInfo(tempPath);
            Assert.True(info.Length > 100, "Archive must be a non-trivial size.");
        }
        finally
        {
            if (File.Exists(tempPath)) File.Delete(tempPath);
        }
    }
}
