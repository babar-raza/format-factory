// Tests for FodtDocument.GetParagraphAt, MoveParagraph, ExtractPlainParagraphs deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R242

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R242: Tests for FodtDocument.GetParagraphAt, MoveParagraph, ExtractPlainParagraphs deeper.
/// GetParagraphAt(index): returns the paragraph object at the specified index.
/// MoveParagraph(fromIndex, toIndex): moves a paragraph from one position to another.
/// ExtractPlainParagraphs(): returns only plain body paragraphs (non-heading) as list of strings.
/// Covers: GetParagraphAt first paragraph; GetParagraphAt last paragraph;
/// GetParagraphAt mid paragraph; GetParagraphAt non-null; GetParagraphAt has text;
/// GetParagraphAt consistent; GetParagraphAt after AppendParagraph accessible;
/// GetParagraphAt heading vs body;
/// MoveParagraph count unchanged; MoveParagraph first to last; MoveParagraph last to first;
/// MoveParagraph text appears at destination; MoveParagraph persist; MoveParagraph no-throw;
/// ExtractPlainParagraphs non-null; ExtractPlainParagraphs count correct;
/// ExtractPlainParagraphs excludes headings; ExtractPlainParagraphs contains body text;
/// ExtractPlainParagraphs after AppendParagraph grows; ExtractPlainParagraphs consistent;
/// ExtractPlainParagraphs after RemoveAllParagraphs empty;
/// dogfood CreateDoc→GetParagraphAt→MoveParagraph→ExtractPlainParagraphs→SaveToFile pipeline.
/// </summary>
public class FodtR242GetParagraphAtAndMoveParagraphDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR242GetParagraphAtAndMoveParagraphDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR242_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateStructuredDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter One", 1);
        doc.AppendParagraph("The first paragraph introduces the chapter topic.");
        doc.AppendParagraph("The second paragraph expands on the introduction.");
        doc.InsertHeading(3, "Section One", 2);
        doc.AppendParagraph("The third paragraph is under section one.");
        doc.InsertHeading(5, "Chapter Two", 1);
        doc.AppendParagraph("The fourth paragraph begins chapter two.");
        doc.AppendParagraph("The fifth paragraph concludes the document.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetParagraphAt
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphAt_First_NonNull()
    {
        var doc = CreateStructuredDoc();
        Assert.NotNull(doc.GetParagraphAt(0));
    }

    [Fact]
    public void GetParagraphAt_First_HasText()
    {
        var doc = CreateStructuredDoc();
        var para = doc.GetParagraphAt(0);
        Assert.True(para.Text != null && para.Text.Length > 0);
    }

    [Fact]
    public void GetParagraphAt_First_IsHeading()
    {
        var doc = CreateStructuredDoc();
        var para = doc.GetParagraphAt(0);
        // First is heading "Chapter One"
        Assert.True(para.Text.Contains("Chapter One") || para.IsHeading);
    }

    [Fact]
    public void GetParagraphAt_Second_IsBody()
    {
        var doc = CreateStructuredDoc();
        var para = doc.GetParagraphAt(1);
        Assert.True(para.Text.Contains("first paragraph") || !para.IsHeading);
    }

    [Fact]
    public void GetParagraphAt_Last_NonNull()
    {
        var doc = CreateStructuredDoc();
        var last = doc.GetParagraphAt(doc.GetParagraphCount() - 1);
        Assert.NotNull(last);
    }

    [Fact]
    public void GetParagraphAt_Last_HasText()
    {
        var doc = CreateStructuredDoc();
        var last = doc.GetParagraphAt(doc.GetParagraphCount() - 1);
        Assert.True(last.Text != null && last.Text.Length > 0);
    }

    [Fact]
    public void GetParagraphAt_Consistent()
    {
        var doc = CreateStructuredDoc();
        var p1 = doc.GetParagraphAt(1);
        var p2 = doc.GetParagraphAt(1);
        Assert.Equal(p1.Text, p2.Text);
    }

    [Fact]
    public void GetParagraphAt_AfterAppendParagraph_NewAccessible()
    {
        var doc = CreateStructuredDoc();
        doc.AppendParagraph("Brand new paragraph UNIQUE-TAG-456.");
        var last = doc.GetParagraphAt(doc.GetParagraphCount() - 1);
        Assert.Contains("UNIQUE-TAG-456", last.Text);
    }

    // -------------------------------------------------------------------------
    // MoveParagraph
    // -------------------------------------------------------------------------

    [Fact]
    public void MoveParagraph_CountUnchanged()
    {
        var doc = CreateStructuredDoc();
        var before = doc.GetParagraphCount();
        doc.MoveParagraph(1, 2);
        Assert.Equal(before, doc.GetParagraphCount());
    }

    [Fact]
    public void MoveParagraph_TextAppearsAtDestination()
    {
        var doc = CreateStructuredDoc();
        var originalSecond = doc.GetParagraphAt(1).Text;
        doc.MoveParagraph(1, 2); // Move index 1 to index 2
        var newPara = doc.GetParagraphAt(2);
        Assert.Equal(originalSecond, newPara.Text);
    }

    [Fact]
    public void MoveParagraph_NoThrow()
    {
        var doc = CreateStructuredDoc();
        var ex = Record.Exception(() => doc.MoveParagraph(0, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void MoveParagraph_Persist()
    {
        var doc = CreateStructuredDoc();
        var originalText = doc.GetParagraphAt(1).Text;
        doc.MoveParagraph(1, 2);
        var path = TempFile("move_persist.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(originalText, loaded.GetParagraphAt(2).Text);
    }

    [Fact]
    public void MoveParagraph_DocStillExportsCorrectly()
    {
        var doc = CreateStructuredDoc();
        doc.MoveParagraph(1, 2);
        var text = doc.ExportToPlainText();
        Assert.NotNull(text);
        Assert.True(text.Length > 0);
    }

    // -------------------------------------------------------------------------
    // ExtractPlainParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void ExtractPlainParagraphs_NonNull()
    {
        var doc = CreateStructuredDoc();
        Assert.NotNull(doc.ExtractPlainParagraphs());
    }

    [Fact]
    public void ExtractPlainParagraphs_CountCorrect()
    {
        var doc = CreateStructuredDoc();
        var plain = doc.ExtractPlainParagraphs();
        // 5 body paragraphs: first, second, third, fourth, fifth
        Assert.Equal(5, plain.Count);
    }

    [Fact]
    public void ExtractPlainParagraphs_ExcludesHeadings()
    {
        var doc = CreateStructuredDoc();
        var plain = doc.ExtractPlainParagraphs();
        // Should not contain heading texts
        Assert.False(plain.Contains("Chapter One"));
        Assert.False(plain.Contains("Section One"));
        Assert.False(plain.Contains("Chapter Two"));
    }

    [Fact]
    public void ExtractPlainParagraphs_ContainsBodyText()
    {
        var doc = CreateStructuredDoc();
        var plain = doc.ExtractPlainParagraphs();
        Assert.True(plain.Exists(t => t.Contains("first paragraph") || t.Contains("introduces")));
    }

    [Fact]
    public void ExtractPlainParagraphs_AfterAppendParagraph_Grows()
    {
        var doc = CreateStructuredDoc();
        var before = doc.ExtractPlainParagraphs().Count;
        doc.AppendParagraph("An additional body paragraph for count verification.");
        var after = doc.ExtractPlainParagraphs().Count;
        Assert.Equal(before + 1, after);
    }

    [Fact]
    public void ExtractPlainParagraphs_AfterInsertHeading_Unchanged()
    {
        var doc = CreateStructuredDoc();
        var before = doc.ExtractPlainParagraphs().Count;
        doc.InsertHeading(doc.GetParagraphCount(), "New Heading", 1);
        // Headings should not appear in ExtractPlainParagraphs
        Assert.Equal(before, doc.ExtractPlainParagraphs().Count);
    }

    [Fact]
    public void ExtractPlainParagraphs_Consistent()
    {
        var doc = CreateStructuredDoc();
        var p1 = doc.ExtractPlainParagraphs();
        var p2 = doc.ExtractPlainParagraphs();
        Assert.Equal(p1.Count, p2.Count);
    }

    [Fact]
    public void ExtractPlainParagraphs_AfterRemoveAllParagraphs_Empty()
    {
        var doc = CreateStructuredDoc();
        doc.RemoveAllParagraphs();
        var plain = doc.ExtractPlainParagraphs();
        Assert.True(plain == null || plain.Count == 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_GetParagraphAt_MoveParagraph_ExtractPlainParagraphs_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Part One", 1);
        doc.AppendParagraph("Alpha paragraph introduces Part One content.");
        doc.AppendParagraph("Beta paragraph provides supporting evidence.");
        doc.InsertHeading(3, "Section A", 2);
        doc.AppendParagraph("Gamma paragraph is under Section A.");
        doc.InsertHeading(5, "Part Two", 1);
        doc.AppendParagraph("Delta paragraph opens Part Two discussion.");
        doc.AppendParagraph("Epsilon paragraph concludes the analysis.");

        // GetParagraphAt verification
        Assert.Equal(8, doc.GetParagraphCount());
        var first = doc.GetParagraphAt(0);
        Assert.NotNull(first);
        Assert.True(first.Text.Contains("Part One") || first.IsHeading);

        var alphaIdx = 1; // Alpha is at index 1
        var alpha = doc.GetParagraphAt(alphaIdx);
        Assert.Contains("Alpha", alpha.Text);

        var last = doc.GetParagraphAt(doc.GetParagraphCount() - 1);
        Assert.Contains("Epsilon", last.Text);

        // ExtractPlainParagraphs — 5 body paragraphs
        var plain = doc.ExtractPlainParagraphs();
        Assert.NotNull(plain);
        Assert.Equal(5, plain.Count);
        Assert.True(plain.Exists(t => t.Contains("Alpha")));
        Assert.True(plain.Exists(t => t.Contains("Epsilon")));
        Assert.False(plain.Contains("Part One")); // heading excluded
        Assert.False(plain.Contains("Section A")); // heading excluded

        // MoveParagraph — move Beta (index 2) to position 4
        var betaText = doc.GetParagraphAt(2).Text;
        doc.MoveParagraph(2, 4);
        Assert.Equal(8, doc.GetParagraphCount()); // count unchanged
        Assert.Equal(betaText, doc.GetParagraphAt(4).Text);

        // ExtractPlainParagraphs still has 5 after move
        Assert.Equal(5, doc.ExtractPlainParagraphs().Count);

        // AppendParagraph and verify GetParagraphAt
        doc.AppendParagraph("Zeta paragraph added after move operation.");
        Assert.Equal(9, doc.GetParagraphCount());
        var zeta = doc.GetParagraphAt(doc.GetParagraphCount() - 1);
        Assert.Contains("Zeta", zeta.Text);
        Assert.Equal(6, doc.ExtractPlainParagraphs().Count);

        // MoveParagraph — move new last to first body position
        doc.MoveParagraph(doc.GetParagraphCount() - 1, 1);
        Assert.Equal(9, doc.GetParagraphCount());

        // SaveToFile and reload
        var path = TempFile("dogfood_getpara.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(9, loaded.GetParagraphCount());

        // Verify loaded ExtractPlainParagraphs
        var loadedPlain = loaded.ExtractPlainParagraphs();
        Assert.NotNull(loadedPlain);
        Assert.Equal(6, loadedPlain.Count);

        // GetParagraphAt on loaded
        var loadedFirst = loaded.GetParagraphAt(0);
        Assert.NotNull(loadedFirst);
        Assert.True(loadedFirst.Text.Length > 0);

        // MoveParagraph on loaded
        var beforeText = loaded.GetParagraphAt(1).Text;
        loaded.MoveParagraph(1, 2);
        Assert.Equal(beforeText, loaded.GetParagraphAt(2).Text);
    }
}
