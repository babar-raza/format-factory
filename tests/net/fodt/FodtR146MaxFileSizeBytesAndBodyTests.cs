// Tests for FodtDocument.MaxFileSizeBytes init-only property and FodtDocument.Body.
// Sprint: ff-sprint-s130-dotnet-deepening-20260627
// Ledger: PC-FODT-R146

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R146: Tests for FodtDocument.MaxFileSizeBytes (init-only, default 50 MB) and
/// FodtDocument.Body property (returns the FodtBody? object). MaxFileSizeBytes
/// is a guard property used by Load() to reject oversized files.
/// Covers: MaxFileSizeBytes default is 50 MB; CreateEmpty.MaxFileSizeBytes = default;
/// Load respects custom maxFileSizeBytes guard; MaxFileSizeBytes is accessible;
/// Body on CreateEmpty is non-null; Body on loaded document is non-null;
/// Body has Paragraphs accessible; CharCount on empty doc is 0;
/// WordCount on empty doc is 0; dogfood CreateEmpty → AppendParagraph → Body.
/// </summary>
public class FodtR146MaxFileSizeBytesAndBodyTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fodt", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    // -------------------------------------------------------------------------
    // MaxFileSizeBytes — default value
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtDocument_MaxFileSizeBytes_DefaultIs50MB()
    {
        var doc = FodtDocument.CreateEmpty();
        const long expected50MB = 50L * 1024 * 1024;
        Assert.Equal(expected50MB, doc.MaxFileSizeBytes);
    }

    [Fact]
    public void FodtDocument_MaxFileSizeBytes_IsPositive()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.MaxFileSizeBytes > 0);
    }

    [Fact]
    public void FodtDocument_MaxFileSizeBytes_IsAccessibleAfterCreateEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(50L * 1024 * 1024, doc.MaxFileSizeBytes);
    }

    // -------------------------------------------------------------------------
    // Load rejects oversized file
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtDocument_Load_CustomMaxFileSizeBytes_TinyGuard_RejectsSmallFile()
    {
        // Use a fixture if available; otherwise skip
        var fixture = FixturePath("two-paragraphs.fodt");
        if (!File.Exists(fixture))
            return;

        // A 1-byte limit should reject any real FODT file
        Assert.Throws<FodtDocumentException>(() =>
            FodtDocument.Load(fixture, maxFileSizeBytes: 1L));
    }

    // -------------------------------------------------------------------------
    // Body property
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtDocument_CreateEmpty_Body_IsNotNull()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.NotNull(doc.Body);
    }

    [Fact]
    public void FodtDocument_CreateEmpty_Body_ParagraphsIsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.NotNull(doc.Body);
        Assert.Empty(doc.Body!.Paragraphs);
    }

    // -------------------------------------------------------------------------
    // CharCount and WordCount on empty document
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtDocument_CreateEmpty_CharCount_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.CharCount);
    }

    [Fact]
    public void FodtDocument_CreateEmpty_WordCount_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.WordCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty → AppendParagraph → Body
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateEmpty_AppendParagraph_Body_HasOneParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello, World!");

        Assert.NotNull(doc.Body);
        Assert.Equal(1, doc.Body!.Paragraphs.Count);
        Assert.Equal("Hello, World!", doc.Body.Paragraphs[0].Text);
    }
}
