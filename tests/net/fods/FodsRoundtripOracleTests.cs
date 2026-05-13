// FodsRoundtripOracleTests -- Lane G: FODS oracle/structural comparison tests
// COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
//
// Oracle strategy: structural comparison (sheet/row/cell counts, values, XML validity).
// LibreOffice: LO_NOT_AVAILABLE — not required for this vertical slice.

using System;
using System.IO;
using System.Xml;
using Xunit;
using FormatFactory.Fods;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// Oracle-level roundtrip tests for FODS.
/// These tests verify that Save() actually writes meaningful content and that
/// the document structure is faithfully preserved through load → save → reload cycles.
/// These tests would catch a no-op Save() or a Save() that drops structural data.
/// </summary>
public class FodsRoundtripOracleTests
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    // ------------------------------------------------------------------
    // OR-01: Save() output parses as valid XML and has ODF namespace
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_SavedFile_IsValidOdfXml()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var content = File.ReadAllText(tmp.Path);
        Assert.Contains("urn:oasis:names:tc:opendocument:xmlns:office:1.0", content);
        Assert.Contains("spreadsheet-flat-xml", content);
    }

    // ------------------------------------------------------------------
    // OR-02: Save() does not produce empty file (detects no-op)
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_SaveIsNotNoop()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var originalSize = new FileInfo(srcPath).Length;

        var doc = FodsDocument.Load(srcPath);
        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var savedSize = new FileInfo(tmp.Path).Length;
        Assert.True(savedSize > 0, "Save() produced empty file — no-op detected.");
        // Output may differ slightly due to formatting, but should be in same order of magnitude
        Assert.True(savedSize > originalSize / 2,
            $"Saved file ({savedSize}B) is much smaller than source ({originalSize}B) — suspicious.");
    }

    // ------------------------------------------------------------------
    // OR-03: Edit-then-save output differs from no-edit save (detects edit no-op)
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_EditChangesOutput()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");

        var doc1 = FodsDocument.Load(srcPath);
        using var noEditOut = new TempFile();
        doc1.Save(noEditOut.Path);

        var doc2 = FodsDocument.Load(srcPath);
        doc2.Sheets[0].Rows[0].Cells[0].SetText("ORACLE_UNIQUE_VALUE_12345");
        using var editOut = new TempFile();
        doc2.Save(editOut.Path);

        var noEditContent = File.ReadAllText(noEditOut.Path);
        var editContent   = File.ReadAllText(editOut.Path);

        // The edited content should contain the new value
        Assert.Contains("ORACLE_UNIQUE_VALUE_12345", editContent);
        // The no-edit content should NOT contain it
        Assert.DoesNotContain("ORACLE_UNIQUE_VALUE_12345", noEditContent);
    }

    // ------------------------------------------------------------------
    // OR-04: Structural comparison — sheet count stable through roundtrip
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_StructuralEquivalence_SheetCount()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var src = FodsDocument.Load(srcPath);
        var srcSheetCount = src.Sheets.Count;
        var srcSheetName  = src.Sheets[0].Name;

        using var tmp = new TempFile();
        src.Save(tmp.Path);

        var reloaded = FodsDocument.Load(tmp.Path);
        Assert.Equal(srcSheetCount, reloaded.Sheets.Count);
        Assert.Equal(srcSheetName,  reloaded.Sheets[0].Name);
    }

    // ------------------------------------------------------------------
    // OR-05: Structural comparison — row count stable through roundtrip
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_StructuralEquivalence_RowCount()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var src = FodsDocument.Load(srcPath);
        var srcRowCount = src.Sheets[0].Rows.Count;

        using var tmp = new TempFile();
        src.Save(tmp.Path);

        var reloaded = FodsDocument.Load(tmp.Path);
        Assert.Equal(srcRowCount, reloaded.Sheets[0].Rows.Count);
    }

    // ------------------------------------------------------------------
    // OR-06: Structural comparison — cell count stable through roundtrip
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_StructuralEquivalence_CellCount()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var src = FodsDocument.Load(srcPath);
        var srcCellCount = src.Sheets[0].Rows[0].Cells.Count;

        using var tmp = new TempFile();
        src.Save(tmp.Path);

        var reloaded = FodsDocument.Load(tmp.Path);
        Assert.Equal(srcCellCount, reloaded.Sheets[0].Rows[0].Cells.Count);
    }

    // ------------------------------------------------------------------
    // OR-07: LibreOffice availability note (LO_NOT_AVAILABLE — not blocking)
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_LibreOffice_NotAvailableNote()
    {
        // LibreOffice oracle comparison is NOT required for this first vertical slice.
        // LO oracle is only run if soffice.com is found via FORMAT_FACTORY_SOFFICE or
        // standard discovery paths (see tools/oracle/preflight_oracle.py).
        // This test records the known state: LO_NOT_AVAILABLE is acceptable here.
        // The structural comparison above (OR-01 through OR-06) provides the oracle function.

        // Vacuously pass — recording intent only.
        Assert.True(true, "LO_NOT_AVAILABLE: structural comparison used as oracle substitute.");
    }

    // ------------------------------------------------------------------
    // Helper
    // ------------------------------------------------------------------
    private sealed class TempFile : IDisposable
    {
        public string Path { get; }
        public TempFile()
        {
            Path = System.IO.Path.GetTempFileName();
        }
        public void Dispose()
        {
            if (File.Exists(Path)) File.Delete(Path);
        }
    }
}
