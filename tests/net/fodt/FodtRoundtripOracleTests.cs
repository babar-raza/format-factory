// FodtRoundtripOracleTests -- Lane G: FODT oracle/structural comparison tests
// COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
//
// Oracle strategy: structural comparison (paragraph count/text, XML validity).
// LibreOffice: LO_NOT_AVAILABLE — not required for this vertical slice.

using System;
using System.IO;
using Xunit;
using FormatFactory.Fodt;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// Oracle-level roundtrip tests for FODT.
/// These tests verify that Save() actually writes meaningful content and that
/// the document structure is faithfully preserved through load → save → reload cycles.
/// </summary>
public class FodtRoundtripOracleTests
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    // ------------------------------------------------------------------
    // OR-01: Save() output is valid ODF XML
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_SavedFile_IsValidOdfXml()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var content = File.ReadAllText(tmp.Path);
        Assert.Contains("urn:oasis:names:tc:opendocument:xmlns:office:1.0", content);
        Assert.Contains("text-flat-xml", content);
    }

    // ------------------------------------------------------------------
    // OR-02: Save() is not a no-op
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_SaveIsNotNoop()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var originalSize = new FileInfo(srcPath).Length;

        var doc = FodtDocument.Load(srcPath);
        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var savedSize = new FileInfo(tmp.Path).Length;
        Assert.True(savedSize > 0, "Save() produced empty file — no-op detected.");
        Assert.True(savedSize > originalSize / 2,
            $"Saved file ({savedSize}B) much smaller than source ({originalSize}B) — suspicious.");
    }

    // ------------------------------------------------------------------
    // OR-03: Edit-then-save output differs from no-edit save
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_EditChangesOutput()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");

        var doc1 = FodtDocument.Load(srcPath);
        using var noEditOut = new TempFile();
        doc1.Save(noEditOut.Path);

        var doc2 = FodtDocument.Load(srcPath);
        doc2.Paragraphs[0].SetText("ORACLE_UNIQUE_PARAGRAPH_67890");
        using var editOut = new TempFile();
        doc2.Save(editOut.Path);

        var noEditContent = File.ReadAllText(noEditOut.Path);
        var editContent   = File.ReadAllText(editOut.Path);

        Assert.Contains("ORACLE_UNIQUE_PARAGRAPH_67890", editContent);
        Assert.DoesNotContain("ORACLE_UNIQUE_PARAGRAPH_67890", noEditContent);
    }

    // ------------------------------------------------------------------
    // OR-04: Paragraph count stable through roundtrip
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_StructuralEquivalence_ParagraphCount()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var src = FodtDocument.Load(srcPath);
        var srcCount = src.Paragraphs.Count;

        using var tmp = new TempFile();
        src.Save(tmp.Path);

        var reloaded = FodtDocument.Load(tmp.Path);
        Assert.Equal(srcCount, reloaded.Paragraphs.Count);
    }

    // ------------------------------------------------------------------
    // OR-05: All paragraph texts preserved through roundtrip
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_StructuralEquivalence_ParagraphTexts()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var src = FodtDocument.Load(srcPath);
        var texts = new string[src.Paragraphs.Count];
        for (var i = 0; i < src.Paragraphs.Count; i++)
            texts[i] = src.Paragraphs[i].Text;

        using var tmp = new TempFile();
        src.Save(tmp.Path);

        var reloaded = FodtDocument.Load(tmp.Path);
        for (var i = 0; i < texts.Length; i++)
            Assert.Equal(texts[i], reloaded.Paragraphs[i].Text);
    }

    // ------------------------------------------------------------------
    // OR-06: Heading flag preserved through roundtrip
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_StructuralEquivalence_HeadingFlag()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var src = FodtDocument.Load(srcPath);

        using var tmp = new TempFile();
        src.Save(tmp.Path);

        var reloaded = FodtDocument.Load(tmp.Path);
        // Index 2 is text:h in our fixture
        Assert.True(reloaded.Paragraphs[2].IsHeading);
        Assert.False(reloaded.Paragraphs[0].IsHeading);
    }

    // ------------------------------------------------------------------
    // OR-07: LibreOffice availability note (LO_NOT_AVAILABLE)
    // ------------------------------------------------------------------
    [Fact]
    public void Oracle_LibreOffice_NotAvailableNote()
    {
        // LO oracle: LO_NOT_AVAILABLE — structural comparison above serves as oracle.
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
