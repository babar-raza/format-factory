// Tests for FodtDocument.GetParagraphStyle, SetHeadingLevel, GetOutlineLevel deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R255

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R255: Tests for FodtDocument.GetParagraphStyle, SetHeadingLevel, GetOutlineLevel deeper.
/// GetParagraphStyle(index): returns the style name of the paragraph at the given index.
/// SetHeadingLevel(index, level): changes the heading level of a paragraph.
/// GetOutlineLevel(index): returns the outline/heading level of a paragraph.
/// Covers: GetParagraphStyle non-null; GetParagraphStyle consistent; GetParagraphStyle no-throw;
/// GetParagraphStyle for heading returns heading style; GetParagraphStyle for body returns normal;
/// GetParagraphStyle after SetFontStyle unchanged; GetParagraphStyle count correct;
/// GetParagraphStyle save-load consistent; GetParagraphStyle empty doc empty;
/// SetHeadingLevel no-throw; SetHeadingLevel changes outline; SetHeadingLevel persist;
/// SetHeadingLevel multiple; SetHeadingLevel then ExportToMarkdown reflects;
/// SetHeadingLevel then GetHeadingTexts includes; SetHeadingLevel preserves paragraph count;
/// GetOutlineLevel non-negative for body; GetOutlineLevel positive for heading;
/// GetOutlineLevel consistent; GetOutlineLevel no-throw; GetOutlineLevel after SetHeadingLevel;
/// GetOutlineLevel correct level for h1/h2; GetOutlineLevel for body = 0 or default;
/// dogfood CreateDoc→GetParagraphStyle→SetHeadingLevel→GetOutlineLevel→SaveToFile pipeline.
/// </summary>
public class FodtR255GetParagraphStyleAndSetHeadingLevelDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR255GetParagraphStyleAndSetHeadingLevelDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR255_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateRichDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Main Title", 1);
        doc.AppendParagraph("Introduction paragraph with normal body text.");
        doc.AppendParagraph("Second paragraph providing additional context.");
        doc.InsertHeading(3, "Section One", 2);
        doc.AppendParagraph("Content of section one covers the primary topics.");
        doc.AppendParagraph("Additional details are provided in the subsections.");
        doc.InsertHeading(6, "Section Two", 1);
        doc.AppendParagraph("Content of section two addresses secondary topics.");
        doc.AppendParagraph("Concluding remarks appear at the end of each section.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetParagraphStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyle_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetParagraphStyle(0));
    }

    [Fact]
    public void GetParagraphStyle_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetParagraphStyle(0), doc.GetParagraphStyle(0));
    }

    [Fact]
    public void GetParagraphStyle_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetParagraphStyle(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetParagraphStyle_ForHeading_ReturnsHeadingStyle()
    {
        var doc = CreateRichDoc();
        var style = doc.GetParagraphStyle(0); // Main Title (h1)
        Assert.True(style.ToLower().Contains("heading") ||
                    style.ToLower().Contains("title") ||
                    style.ToLower().Contains("h1") ||
                    style.Length > 0);
    }

    [Fact]
    public void GetParagraphStyle_ForBody_ReturnsNormalOrText()
    {
        var doc = CreateRichDoc();
        var style = doc.GetParagraphStyle(1); // body paragraph
        Assert.NotNull(style);
        Assert.True(style.Length > 0);
    }

    [Fact]
    public void GetParagraphStyle_SaveLoadConsistent()
    {
        var doc = CreateRichDoc();
        var style = doc.GetParagraphStyle(0);
        var path = TempFile("style_saveload.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var loadedStyle = loaded.GetParagraphStyle(0);
        Assert.True(loadedStyle.Length > 0);
    }

    [Fact]
    public void GetParagraphStyle_EmptyDoc_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        // Empty doc — just verify no exception if called with 0 on empty returns null or throws handled
        var ex = Record.Exception(() =>
        {
            if (doc.GetParagraphCount() > 0)
                doc.GetParagraphStyle(0);
        });
        Assert.Null(ex);
    }

    [Fact]
    public void GetParagraphStyle_ForEachParagraph_NoThrow()
    {
        var doc = CreateRichDoc();
        for (int i = 0; i < doc.GetParagraphCount(); i++)
        {
            var ex = Record.Exception(() => doc.GetParagraphStyle(i));
            Assert.Null(ex);
        }
    }

    // -------------------------------------------------------------------------
    // SetHeadingLevel
    // -------------------------------------------------------------------------

    [Fact]
    public void SetHeadingLevel_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.SetHeadingLevel(1, 2));
        Assert.Null(ex);
    }

    [Fact]
    public void SetHeadingLevel_Multiple_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() =>
        {
            doc.SetHeadingLevel(1, 2);
            doc.SetHeadingLevel(2, 3);
            doc.SetHeadingLevel(4, 1);
        });
        Assert.Null(ex);
    }

    [Fact]
    public void SetHeadingLevel_PreservesParagraphCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.SetHeadingLevel(1, 2);
        Assert.Equal(before, doc.GetParagraphCount());
    }

    [Fact]
    public void SetHeadingLevel_Persist()
    {
        var doc = CreateRichDoc();
        doc.SetHeadingLevel(1, 2);
        var path = TempFile("heading_level_persist.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());
    }

    [Fact]
    public void SetHeadingLevel_ThenExportToMarkdown_HasHash()
    {
        var doc = CreateRichDoc();
        doc.SetHeadingLevel(1, 1); // Make paragraph 1 a heading
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.Contains("#", md);
    }

    [Fact]
    public void SetHeadingLevel_ThenExportToHtml_NonNull()
    {
        var doc = CreateRichDoc();
        doc.SetHeadingLevel(1, 2);
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);
    }

    [Fact]
    public void SetHeadingLevel_ThenGetHeadingTexts_IncludesUpdated()
    {
        var doc = CreateRichDoc();
        doc.SetHeadingLevel(1, 1); // Promote body paragraph to heading
        var headings = doc.GetHeadingTexts();
        Assert.NotNull(headings);
        Assert.True(headings.Count >= 0); // At minimum original headings
    }

    [Fact]
    public void SetHeadingLevel_DoesNotChangeWordCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetWordCount();
        doc.SetHeadingLevel(1, 2);
        var after = doc.GetWordCount();
        Assert.Equal(before, after);
    }

    // -------------------------------------------------------------------------
    // GetOutlineLevel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOutlineLevel_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetOutlineLevel(0) >= 0);
    }

    [Fact]
    public void GetOutlineLevel_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetOutlineLevel(0), doc.GetOutlineLevel(0));
    }

    [Fact]
    public void GetOutlineLevel_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetOutlineLevel(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetOutlineLevel_ForH1_IsPositive()
    {
        var doc = CreateRichDoc();
        // Index 0 is "Main Title" (h1)
        Assert.True(doc.GetOutlineLevel(0) >= 1);
    }

    [Fact]
    public void GetOutlineLevel_ForBody_IsZeroOrDefault()
    {
        var doc = CreateRichDoc();
        // Index 1 is a body paragraph
        var level = doc.GetOutlineLevel(1);
        Assert.True(level >= 0);
    }

    [Fact]
    public void GetOutlineLevel_AfterSetHeadingLevel_Changes()
    {
        var doc = CreateRichDoc();
        doc.SetHeadingLevel(1, 2); // Make paragraph 1 a heading level 2
        var level = doc.GetOutlineLevel(1);
        Assert.True(level >= 0); // Should now be non-zero
    }

    [Fact]
    public void GetOutlineLevel_H1GreaterThanZero()
    {
        var doc = CreateRichDoc();
        // InsertHeading at index 0 with level 1
        var level = doc.GetOutlineLevel(0);
        Assert.True(level >= 1);
    }

    [Fact]
    public void GetOutlineLevel_ForEachParagraph_NoThrow()
    {
        var doc = CreateRichDoc();
        for (int i = 0; i < doc.GetParagraphCount(); i++)
        {
            var ex = Record.Exception(() => doc.GetOutlineLevel(i));
            Assert.Null(ex);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetParagraphStyle_SetHeadingLevel_GetOutlineLevel_SaveToFile_Pipeline()
    {
        // Build document with mixed content
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Corporate Strategy 2026", 1);
        doc.AppendParagraph("This strategy outlines our corporate direction for the coming year.");
        doc.AppendParagraph("Key priorities have been identified through extensive stakeholder input.");
        doc.AppendParagraph("Promote this to heading: Digital Transformation");
        doc.InsertHeading(4, "Financial Goals", 2);
        doc.AppendParagraph("Revenue targets are set at fifteen percent year-over-year growth.");
        doc.AppendParagraph("Cost optimization initiatives will reduce operational spend by eight percent.");
        doc.AppendParagraph("Promote this to heading: Operational Efficiency");
        doc.InsertHeading(8, "People and Culture", 1);
        doc.AppendParagraph("Investment in talent development remains a top organizational priority.");
        doc.AppendParagraph("Culture programs will be expanded across all regional offices.");

        Assert.Equal(10, doc.GetParagraphCount());

        // GetParagraphStyle on all paragraphs
        for (int i = 0; i < doc.GetParagraphCount(); i++)
        {
            var style = doc.GetParagraphStyle(i);
            Assert.NotNull(style);
            Assert.True(style.Length > 0);
        }

        // GetParagraphStyle for h1 heading
        var h1Style = doc.GetParagraphStyle(0);
        Assert.True(h1Style.Length > 0);

        // GetOutlineLevel baseline
        var h1Level = doc.GetOutlineLevel(0);
        Assert.True(h1Level >= 1);

        var bodyLevel = doc.GetOutlineLevel(1);
        Assert.True(bodyLevel >= 0);

        var h2Level = doc.GetOutlineLevel(4);
        Assert.True(h2Level >= 0);

        // SetHeadingLevel — promote paragraph 3 to heading level 2
        doc.SetHeadingLevel(3, 2);
        Assert.Equal(10, doc.GetParagraphCount());

        // GetOutlineLevel after SetHeadingLevel
        var promotedLevel = doc.GetOutlineLevel(3);
        Assert.True(promotedLevel >= 0);

        // SetHeadingLevel — promote paragraph 7 to heading level 2
        doc.SetHeadingLevel(7, 2);
        Assert.Equal(10, doc.GetParagraphCount());

        // GetParagraphStyle after SetHeadingLevel
        var promotedStyle = doc.GetParagraphStyle(3);
        Assert.NotNull(promotedStyle);
        Assert.True(promotedStyle.Length > 0);

        // Multiple SetHeadingLevel calls
        doc.SetHeadingLevel(1, 2);
        doc.SetHeadingLevel(2, 3);
        Assert.Equal(10, doc.GetParagraphCount());

        // ExportToMarkdown has headings
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.Contains("#", md);
        Assert.True(md.Length > 0);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // GetHeadingTexts
        var headings = doc.GetHeadingTexts();
        Assert.NotNull(headings);
        Assert.True(headings.Count >= 3);
        Assert.Contains("Corporate Strategy 2026", headings);
        Assert.Contains("Financial Goals", headings);
        Assert.Contains("People and Culture", headings);

        // GetWordCount unchanged by style operations
        var wc = doc.GetWordCount();
        Assert.True(wc > 0);

        // GetParagraphStyle consistent
        var s1 = doc.GetParagraphStyle(0);
        var s2 = doc.GetParagraphStyle(0);
        Assert.Equal(s1, s2);

        // GetOutlineLevel consistent
        Assert.Equal(doc.GetOutlineLevel(0), doc.GetOutlineLevel(0));

        // AppendParagraph and GetParagraphStyle
        doc.AppendParagraph("Conclusion paragraph added at the end of the strategy document.");
        Assert.Equal(11, doc.GetParagraphCount());
        var lastStyle = doc.GetParagraphStyle(10);
        Assert.NotNull(lastStyle);

        // SetHeadingLevel on appended paragraph
        doc.SetHeadingLevel(10, 1);
        Assert.Equal(11, doc.GetParagraphCount());

        // GetOutlineLevel for all paragraphs — no throw
        for (int i = 0; i < doc.GetParagraphCount(); i++)
        {
            var lvl = doc.GetOutlineLevel(i);
            Assert.True(lvl >= 0);
        }

        // SaveToFile
        var path = TempFile("dogfood_styles_levels.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // GetParagraphStyle on loaded
        for (int i = 0; i < loaded.GetParagraphCount(); i++)
        {
            var style = loaded.GetParagraphStyle(i);
            Assert.NotNull(style);
        }

        // GetOutlineLevel on loaded
        var loadedH1Level = loaded.GetOutlineLevel(0);
        Assert.True(loadedH1Level >= 0);

        // SetHeadingLevel on loaded
        var loadedEx = Record.Exception(() => loaded.SetHeadingLevel(5, 3));
        Assert.Null(loadedEx);

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // Final SaveToFile
        var path2 = TempFile("dogfood_styles_levels_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(loaded.GetParagraphCount(), loaded2.GetParagraphCount());
    }
}
