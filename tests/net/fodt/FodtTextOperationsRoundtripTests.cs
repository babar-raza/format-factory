// FodtTextOperationsRoundtripTests -- TRUE-AUTONOMOUS-CONTINUATION: FODT C7 text operations
// Sprint: TRUE-AUTONOMOUS-MAINSTREAM-CONTINUATION-001
// Added: 2026-06-10
// commercial_product_ready: false
//
// Tests advanced text operations (append, insert, remove, replace, stats)
// followed by save -> reload -> verify, exercising APIs beyond basic SetText.

using System;
using System.IO;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtTextOperationsRoundtripTests : IDisposable
{
    private readonly string _tempDir;

    public FodtTextOperationsRoundtripTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fodt-textops-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    [Fact]
    public void CreateEmpty_AppendParagraph_SaveReload_TextPersists()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First appended paragraph");
        doc.AppendParagraph("Second appended paragraph");

        var path = Path.Combine(_tempDir, "append.fodt");
        doc.Save(path);

        var reloaded = FodtDocument.Load(path);
        Assert.True(reloaded.Paragraphs.Count >= 2);
        Assert.Equal("First appended paragraph", reloaded.Paragraphs[^2].Text);
        Assert.Equal("Second appended paragraph", reloaded.Paragraphs[^1].Text);
    }

    [Fact]
    public void InsertParagraph_AtIndex0_SaveReload_CorrectOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original first");
        doc.InsertParagraph(0, "Inserted before");

        var path = Path.Combine(_tempDir, "insert.fodt");
        doc.Save(path);

        var reloaded = FodtDocument.Load(path);
        Assert.Equal("Inserted before", reloaded.Paragraphs[0].Text);
        Assert.Equal("Original first", reloaded.Paragraphs[1].Text);
    }

    [Fact]
    public void RemoveParagraph_SaveReload_ParagraphGone()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Keep this");
        doc.AppendParagraph("Remove this");
        doc.AppendParagraph("Also keep");

        int countBefore = doc.Paragraphs.Count;
        // Remove "Remove this" — find its index
        int removeIdx = -1;
        for (int i = 0; i < doc.Paragraphs.Count; i++)
        {
            if (doc.Paragraphs[i].Text == "Remove this")
            {
                removeIdx = i;
                break;
            }
        }
        Assert.True(removeIdx >= 0, "Should find 'Remove this' paragraph");
        doc.RemoveParagraph(removeIdx);

        var path = Path.Combine(_tempDir, "remove.fodt");
        doc.Save(path);

        var reloaded = FodtDocument.Load(path);
        Assert.Equal(countBefore - 1, reloaded.Paragraphs.Count);
        Assert.DoesNotContain(reloaded.Paragraphs, p => p.Text == "Remove this");
    }

    [Fact]
    public void InsertHeading_SaveReload_HeadingPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text");
        doc.InsertHeading(0, "Chapter One", 1);

        var path = Path.Combine(_tempDir, "heading.fodt");
        doc.Save(path);

        var reloaded = FodtDocument.Load(path);
        Assert.True(reloaded.Paragraphs[0].IsHeading);
        Assert.Equal("Chapter One", reloaded.Paragraphs[0].Text);
        Assert.Equal(1, reloaded.Paragraphs[0].OutlineLevel);
    }

    [Fact]
    public void ReplaceText_SaveReload_ReplacementPersists()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world, hello everyone.");

        int count = doc.ReplaceText("hello", "GREETINGS", StringComparison.OrdinalIgnoreCase);
        Assert.True(count >= 1, "Should replace at least one occurrence");

        var path = Path.Combine(_tempDir, "replace.fodt");
        doc.Save(path);

        var reloaded = FodtDocument.Load(path);
        var text = reloaded.GetPlainText();
        Assert.Contains("GREETINGS", text);
    }

    [Fact]
    public void GetDocumentStats_AfterEdits_ReflectsChanges()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One two three");
        doc.AppendParagraph("Four five");
        doc.InsertHeading(0, "Title", 1);

        var stats = doc.GetDocumentStats();
        Assert.True(stats.ParagraphCount >= 3, "Should have at least 3 paragraphs");
        Assert.True(stats.HeadingCount >= 1, "Should have at least 1 heading");
        Assert.True(stats.WordCount >= 6, "Should count at least 6 words");
    }

    [Fact]
    public void ExportToMarkdown_ProducesValidOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Title", 1);
        doc.AppendParagraph("Body paragraph.");

        var md = doc.ExportToMarkdown();
        Assert.Contains("# My Title", md);
        Assert.Contains("Body paragraph.", md);
    }

    [Fact]
    public void SearchText_FindsMatches()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha beta gamma");
        doc.AppendParagraph("Delta beta epsilon");

        var results = doc.SearchText("beta", StringComparison.Ordinal);
        Assert.True(results.Count >= 2, "Should find 'beta' in at least 2 paragraphs");
    }

    [Fact]
    public void CreateEmpty_SaveReload_MultipleRoundtrips_Stable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Stable text");
        doc.InsertHeading(0, "Stable heading", 2);

        // Round-trip 3 times
        string lastPath = null!;
        for (int i = 0; i < 3; i++)
        {
            lastPath = Path.Combine(_tempDir, $"stable-{i}.fodt");
            doc.Save(lastPath);
            doc = FodtDocument.Load(lastPath);
        }

        Assert.True(doc.Paragraphs[0].IsHeading);
        Assert.Equal("Stable heading", doc.Paragraphs[0].Text);
        Assert.Equal(2, doc.Paragraphs[0].OutlineLevel);
    }
}
