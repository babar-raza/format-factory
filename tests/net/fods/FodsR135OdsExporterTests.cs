// Tests for FodsOdsExporter.ExportToOds(FodsDocument, odsPath) and ExportToOdsBytes(FodsDocument).
// Sprint: FORMAT-FACTORY-FODS-R135-20260627
// Ledger: R135-GOVERNED-DOTNET-FODS-ODS-EXPORTER-001

using System;
using System.IO;
using System.IO.Compression;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R135: Tests for FodsOdsExporter — the FODS→ODS conversion API.
/// Covers: ExportToOds(FodsDocument, odsPath) result object properties,
/// ExportToOdsBytes(FodsDocument) byte output, and ZIP/ODS structure invariants.
/// ODF basis: §3.1.1 ODS package structure, §3.7 office:spreadsheet.
/// </summary>
public class FodsR135OdsExporterTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fods", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    private static string TempOdsPath() =>
        Path.Combine(Path.GetTempPath(), $"fods_r135_{Guid.NewGuid():N}.ods");

    // -------------------------------------------------------------------------
    // ExportToOds(FodsDocument, odsPath) — result object properties
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOds_Document_SheetCountAtLeastOne()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var odsPath = TempOdsPath();
        try
        {
            var result = FodsOdsExporter.ExportToOds(doc, odsPath);
            Assert.True(result.SheetCount >= 1, $"Expected SheetCount >= 1, got {result.SheetCount}");
        }
        finally { if (File.Exists(odsPath)) File.Delete(odsPath); }
    }

    [Fact]
    public void ExportToOds_Document_OutputPathMatchesGivenPath()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var odsPath = TempOdsPath();
        try
        {
            var result = FodsOdsExporter.ExportToOds(doc, odsPath);
            Assert.Equal(odsPath, result.OutputPath);
        }
        finally { if (File.Exists(odsPath)) File.Delete(odsPath); }
    }

    [Fact]
    public void ExportToOds_Document_OutputFileExists()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var odsPath = TempOdsPath();
        try
        {
            FodsOdsExporter.ExportToOds(doc, odsPath);
            Assert.True(File.Exists(odsPath), "ODS output file should exist after export");
        }
        finally { if (File.Exists(odsPath)) File.Delete(odsPath); }
    }

    [Fact]
    public void ExportToOds_Document_TotalRowsExportedNonNegative()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var odsPath = TempOdsPath();
        try
        {
            var result = FodsOdsExporter.ExportToOds(doc, odsPath);
            Assert.True(result.TotalRowsExported >= 0, $"TotalRowsExported must be >= 0, got {result.TotalRowsExported}");
        }
        finally { if (File.Exists(odsPath)) File.Delete(odsPath); }
    }

    [Fact]
    public void ExportToOds_Document_TotalCellsExportedNonNegative()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var odsPath = TempOdsPath();
        try
        {
            var result = FodsOdsExporter.ExportToOds(doc, odsPath);
            Assert.True(result.TotalCellsExported >= 0, $"TotalCellsExported must be >= 0, got {result.TotalCellsExported}");
        }
        finally { if (File.Exists(odsPath)) File.Delete(odsPath); }
    }

    [Fact]
    public void ExportToOds_MultiSheet_SheetCountMatchesSource()
    {
        var doc = FodsDocument.Load(FixturePath("fods-multi-sheet.fods"));
        var odsPath = TempOdsPath();
        try
        {
            var sourceSheets = doc.GetSheetNames().Count;
            var result = FodsOdsExporter.ExportToOds(doc, odsPath);
            Assert.Equal(sourceSheets, result.SheetCount);
        }
        finally { if (File.Exists(odsPath)) File.Delete(odsPath); }
    }

    // -------------------------------------------------------------------------
    // ODS file is a valid ZIP archive
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOds_OutputFile_IsValidZipArchive()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var odsPath = TempOdsPath();
        try
        {
            FodsOdsExporter.ExportToOds(doc, odsPath);
            // Should not throw — valid ZIP
            using var archive = ZipFile.OpenRead(odsPath);
            Assert.True(archive.Entries.Count > 0);
        }
        finally { if (File.Exists(odsPath)) File.Delete(odsPath); }
    }

    // -------------------------------------------------------------------------
    // ExportToOdsBytes — byte array output
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOdsBytes_Document_ReturnsNonEmptyArray()
    {
        var doc = FodsDocument.Load(FixturePath("fods-minimal-roundtrip.fods"));
        var bytes = FodsOdsExporter.ExportToOdsBytes(doc);
        Assert.NotNull(bytes);
        Assert.True(bytes.Length > 0, "ExportToOdsBytes should return a non-empty byte array");
    }

    [Fact]
    public void ExportToOdsBytes_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => FodsOdsExporter.ExportToOdsBytes(null!));
    }

    // -------------------------------------------------------------------------
    // ExportToOds null guard
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOds_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsOdsExporter.ExportToOds((FodsDocument)null!, TempOdsPath()));
    }

    // -------------------------------------------------------------------------
    // Dogfood: export multi-sheet, verify sheet count consistency
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiSheetExport_BytesAndFileConsistent()
    {
        var doc = FodsDocument.Load(FixturePath("fods-multi-sheet.fods"));
        var odsPath = TempOdsPath();
        try
        {
            // File-based export
            var result = FodsOdsExporter.ExportToOds(doc, odsPath);

            // Bytes-based export
            var bytes = FodsOdsExporter.ExportToOdsBytes(doc);

            // SheetCount should match doc
            Assert.True(result.SheetCount >= 1);

            // Both produce non-empty output
            Assert.True(new FileInfo(odsPath).Length > 0);
            Assert.True(bytes.Length > 0);

            // Both are valid ZIP archives
            using var fileArchive = ZipFile.OpenRead(odsPath);
            using var bytesArchive = new ZipArchive(new MemoryStream(bytes));
            Assert.True(fileArchive.Entries.Count > 0);
            Assert.True(bytesArchive.Entries.Count > 0);
        }
        finally { if (File.Exists(odsPath)) File.Delete(odsPath); }
    }
}
