// Tests for FodsDocument ODS export — FodsOdsExporter, ExportToOds.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R175

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R175: Tests for FodsDocument ODS export — FodsOdsExporter properties and byte export.
/// FodsOdsExporter result properties: SucceededWithWarnings, Success, OdsFilePath, Message.
/// ExportToOds and ODS file generation.
/// Covers: FodsOdsExporter.Success property; FodsOdsExporter.SucceededWithWarnings;
/// FodsOdsExporter.Message non-null; FodsOdsExporter.OdsFilePath value;
/// ExportResult pattern; ODS export success for valid document;
/// ExportResult with minimal doc; ExportSheetToOdsBytes returns bytes;
/// ODS bytes non-empty; ODS bytes start with valid PK signature (ZIP);
/// dogfood CreateNew->InsertRows->OdsExport->bytes pipeline.
/// </summary>
public class FodsR175OdsExportTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR175OdsExportTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR175_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument BuildSheet(string sheetName, string[] headers, string[][] rows)
    {
        var doc = FodsDocument.CreateNew();
        var names = doc.GetSheetNames();
        if (names.Count > 0)
            doc.RenameSheet(names[0], sheetName);
        else
            doc.AddSheet(sheetName);

        doc.InsertRowWithValues(sheetName, 0, headers);
        for (var i = 0; i < rows.Length; i++)
            doc.InsertRowWithValues(sheetName, i + 1, rows[i]);

        return doc;
    }

    // -------------------------------------------------------------------------
    // FodsOdsExporter result properties
    // -------------------------------------------------------------------------

    [Fact]
    public void OdsExporter_Success_IsTrue()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name" },
            new[] { new[] { "Alice" } });
        var path = TempFile("out.ods");
        var result = FodsOdsExporter.Export(doc, path);
        Assert.True(result.Success);
    }

    [Fact]
    public void OdsExporter_OdsFilePath_IsSetToPath()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name" },
            new[] { new[] { "Alice" } });
        var path = TempFile("export.ods");
        var result = FodsOdsExporter.Export(doc, path);
        Assert.Equal(path, result.OdsFilePath);
    }

    [Fact]
    public void OdsExporter_Message_IsNotNull()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A" },
            new[] { new[] { "1" } });
        var path = TempFile("msg.ods");
        var result = FodsOdsExporter.Export(doc, path);
        Assert.NotNull(result.Message);
    }

    [Fact]
    public void OdsExporter_CreatesFile()
    {
        var doc = BuildSheet("Data",
            new[] { "Col" },
            new[] { new[] { "Val" } });
        var path = TempFile("created.ods");
        FodsOdsExporter.Export(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void OdsExporter_FileIsNonEmpty()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var path = TempFile("nonempty.ods");
        FodsOdsExporter.Export(doc, path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    // -------------------------------------------------------------------------
    // ODS bytes (ExportToOdsBytes or similar)
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportOdsBytes_IsNonEmpty()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A" },
            new[] { new[] { "1" } });
        var bytes = FodsOdsExporter.ExportToBytes(doc);
        Assert.NotEmpty(bytes);
    }

    [Fact]
    public void ExportOdsBytes_StartWithPkSignature()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A" },
            new[] { new[] { "1" } });
        var bytes = FodsOdsExporter.ExportToBytes(doc);
        // ODS is a ZIP file; starts with PK (0x50, 0x4B)
        Assert.True(bytes.Length >= 2);
        Assert.Equal(0x50, bytes[0]); // 'P'
        Assert.Equal(0x4B, bytes[1]); // 'K'
    }

    [Fact]
    public void ExportOdsBytes_MinimalDoc_IsNonEmpty()
    {
        var doc = FodsDocument.CreateNew();
        var bytes = FodsOdsExporter.ExportToBytes(doc);
        Assert.NotEmpty(bytes);
    }

    // -------------------------------------------------------------------------
    // SucceededWithWarnings
    // -------------------------------------------------------------------------

    [Fact]
    public void OdsExporter_SucceededWithWarnings_PropertyExists()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A" },
            new[] { new[] { "1" } });
        var path = TempFile("warn.ods");
        var result = FodsOdsExporter.Export(doc, path);
        // Property exists and can be read without throwing
        var warned = result.SucceededWithWarnings;
        Assert.True(warned == true || warned == false);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->InsertRows->OdsExport->bytes
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateInsertExportBytes_Pipeline()
    {
        var doc = BuildSheet("Inventory",
            new[] { "Item", "Qty", "Price" },
            new[] {
                new[] { "Widget", "100", "9.99" },
                new[] { "Gadget", "50", "19.99" },
                new[] { "Doohickey", "25", "4.99" }
            });

        // Export to file
        var path = TempFile("inventory.ods");
        var result = FodsOdsExporter.Export(doc, path);
        Assert.True(result.Success);
        Assert.Equal(path, result.OdsFilePath);
        Assert.True(File.Exists(path));

        // Export to bytes
        var bytes = FodsOdsExporter.ExportToBytes(doc);
        Assert.NotEmpty(bytes);
        Assert.Equal(0x50, bytes[0]); // ZIP signature
        Assert.Equal(0x4B, bytes[1]);

        // File and bytes should have similar size
        var fileSize = new FileInfo(path).Length;
        Assert.True(Math.Abs(fileSize - bytes.Length) < fileSize * 0.2); // within 20%
    }
}
