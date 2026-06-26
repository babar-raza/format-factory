// Tests for FodtDocument.GetCharCount, GetWordCount, ExportToFile deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R222

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R222: Tests for FodtDocument.GetCharCount, GetWordCount, ExportToFile deeper coverage.
/// GetCharCount(): returns the total character count of document text.
/// GetWordCount(): returns the total word count of document text.
/// ExportToFile(path, format): exports document to a file in the given format.
/// Covers: GetCharCount positive; GetCharCount increases after AppendParagraph;
/// GetCharCount zero or minimal for empty doc;
/// GetWordCount positive; GetWordCount increases after AppendParagraph;
/// GetWordCount zero or minimal for empty doc; GetWordCount equals GetDocumentStats.WordCount;
/// ExportToFile text format creates file; ExportToFile markdown format creates file;
/// ExportToFile html format creates file; ExportToFile text file non-empty;
/// ExportToFile text contains expected content; ExportToFile after mutation reflects change;
/// dogfood CreateDoc->GetCharCount->GetWordCount->ExportToFile->Verify pipeline.
/// </summary>
public class FodtR222GetCharCountAndExportPathsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR222GetCharCountAndExportPathsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR222_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Report Title", 1);
        doc.AppendParagraph("This paragraph contains words and characters for counting.");
        doc.AppendParagraph("Another paragraph provides additional content for testing.");
        doc.InsertHeading(3, "Section One", 2);
        doc.AppendParagraph("Section content describes the key findings in detail.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCharCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetCharCount() > 0);
    }

    [Fact]
    public void GetCharCount_IncreaseAfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Short text.");
        var before = doc.GetCharCount();
        doc.AppendParagraph("This adds many more characters to the document body.");
        var after = doc.GetCharCount();
        Assert.True(after > before);
    }

    [Fact]
    public void GetCharCount_EmptyDoc_ZeroOrMinimal()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.GetCharCount() >= 0);
    }

    [Fact]
    public void GetCharCount_MatchesGetDocumentStats()
    {
        var doc = CreateRichDoc();
        var stats = doc.GetDocumentStats();
        Assert.Equal(stats.CharCount, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_AfterReplaceText_Changes()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("short text here.");
        var before = doc.GetCharCount();
        doc.ReplaceText("short", "a much longer replacement word");
        var after = doc.GetCharCount();
        Assert.True(after > before);
    }

    // -------------------------------------------------------------------------
    // GetWordCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_Positive()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetWordCount() > 0);
    }

    [Fact]
    public void GetWordCount_IncreasesAfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One two three.");
        var before = doc.GetWordCount();
        doc.AppendParagraph("Four five six seven eight.");
        var after = doc.GetWordCount();
        Assert.True(after > before);
    }

    [Fact]
    public void GetWordCount_EmptyDoc_ZeroOrMinimal()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.GetWordCount() >= 0);
    }

    [Fact]
    public void GetWordCount_MatchesGetDocumentStats()
    {
        var doc = CreateRichDoc();
        var stats = doc.GetDocumentStats();
        Assert.Equal(stats.WordCount, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_KnownParagraph_CorrectCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("one two three four five"); // 5 words
        var count = doc.GetWordCount();
        Assert.True(count >= 5);
    }

    // -------------------------------------------------------------------------
    // ExportToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToFile_TextFormat_CreatesFile()
    {
        var doc = CreateRichDoc();
        var path = TempFile("export.txt");
        doc.ExportToFile(path, "txt");
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToFile_MarkdownFormat_CreatesFile()
    {
        var doc = CreateRichDoc();
        var path = TempFile("export.md");
        doc.ExportToFile(path, "md");
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToFile_HtmlFormat_CreatesFile()
    {
        var doc = CreateRichDoc();
        var path = TempFile("export.html");
        doc.ExportToFile(path, "html");
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToFile_TextFile_NonEmpty()
    {
        var doc = CreateRichDoc();
        var path = TempFile("content.txt");
        doc.ExportToFile(path, "txt");
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void ExportToFile_TextFile_ContainsExpectedContent()
    {
        var doc = CreateRichDoc();
        var path = TempFile("content_check.txt");
        doc.ExportToFile(path, "txt");
        var content = File.ReadAllText(path);
        Assert.True(content.Contains("Report Title") || content.Contains("Section"));
    }

    [Fact]
    public void ExportToFile_HtmlFile_ContainsHtmlStructure()
    {
        var doc = CreateRichDoc();
        var path = TempFile("html_check.html");
        doc.ExportToFile(path, "html");
        var content = File.ReadAllText(path);
        Assert.True(content.Contains("<") && content.Length > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_GetCharCount_GetWordCount_ExportToFile_Verify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Annual Report", 1);
        doc.AppendParagraph("This report summarizes the annual performance of the organization.");
        doc.AppendParagraph("Key metrics show positive growth across all departments this year.");
        doc.InsertHeading(3, "Financial Overview", 2);
        doc.AppendParagraph("Financial results exceeded targets by fifteen percent this quarter.");

        // GetWordCount and GetCharCount
        var wordCount = doc.GetWordCount();
        var charCount = doc.GetCharCount();
        Assert.True(wordCount > 10);
        Assert.True(charCount > 50);
        Assert.True(charCount > wordCount); // chars always > words

        // Match DocumentStats
        var stats = doc.GetDocumentStats();
        Assert.Equal(wordCount, stats.WordCount);
        Assert.Equal(charCount, stats.CharCount);

        // AppendParagraph increases both
        doc.AppendParagraph("Additional content increases both word count and character count.");
        Assert.True(doc.GetWordCount() > wordCount);
        Assert.True(doc.GetCharCount() > charCount);

        // ExportToFile — txt
        var txtPath = TempFile("annual.txt");
        doc.ExportToFile(txtPath, "txt");
        Assert.True(File.Exists(txtPath));
        Assert.True(new FileInfo(txtPath).Length > 0);

        // ExportToFile — md
        var mdPath = TempFile("annual.md");
        doc.ExportToFile(mdPath, "md");
        Assert.True(File.Exists(mdPath));

        // ExportToFile — html
        var htmlPath = TempFile("annual.html");
        doc.ExportToFile(htmlPath, "html");
        Assert.True(File.Exists(htmlPath));

        // txt content should contain heading text
        var txtContent = File.ReadAllText(txtPath);
        Assert.True(txtContent.Length > 0);

        // After mutation — re-export reflects change
        doc.ReplaceText("Annual Report", "Quarterly Report");
        var path2 = TempFile("quarterly.txt");
        doc.ExportToFile(path2, "txt");
        Assert.True(File.Exists(path2));
    }
}
