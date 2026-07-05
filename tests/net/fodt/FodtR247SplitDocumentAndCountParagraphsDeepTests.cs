// Tests for FodtDocument.SplitDocument, GetParagraphCount, CreateEmpty deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R247

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R247: Tests for FodtDocument.SplitDocument, GetParagraphCount, CreateEmpty deeper.
/// SplitDocument(splitIndex): splits the document at the given paragraph index.
/// GetParagraphCount(): returns the total number of paragraphs including headings.
/// CreateEmpty(): creates a new empty FodtDocument.
/// Covers: SplitDocument returns two parts; SplitDocument first part count correct;
/// SplitDocument second part count correct; SplitDocument total count preserved;
/// SplitDocument persist both parts; SplitDocument no-throw; SplitDocument at index 1;
/// GetParagraphCount correct; GetParagraphCount after AppendParagraph increases;
/// GetParagraphCount after InsertHeading increases; GetParagraphCount after RemoveParagraphAt decreases;
/// GetParagraphCount after RemoveAllParagraphs zero; GetParagraphCount consistent;
/// GetParagraphCount empty doc zero; GetParagraphCount includes headings;
/// CreateEmpty non-null; CreateEmpty zero paragraphs; CreateEmpty Addable;
/// CreateEmpty then AppendParagraph; CreateEmpty then SaveToFile;
/// CreateEmpty then LoadFile round-trip; CreateEmpty multiple instances independent;
/// dogfood CreateEmpty→AppendParagraph→GetParagraphCount→SplitDocument→SaveToFile pipeline.
/// </summary>
public class FodtR247SplitDocumentAndCountParagraphsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR247SplitDocumentAndCountParagraphsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR247_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateDoc10Paragraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter One", 1);
        doc.AppendParagraph("Paragraph one of chapter one.");
        doc.AppendParagraph("Paragraph two of chapter one.");
        doc.AppendParagraph("Paragraph three of chapter one.");
        doc.InsertHeading(4, "Chapter Two", 1);
        doc.AppendParagraph("Paragraph one of chapter two.");
        doc.AppendParagraph("Paragraph two of chapter two.");
        doc.InsertHeading(7, "Chapter Three", 1);
        doc.AppendParagraph("Paragraph one of chapter three.");
        doc.AppendParagraph("Paragraph two of chapter three.");
        doc.AppendParagraph("Paragraph three of chapter three.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // SplitDocument
    // -------------------------------------------------------------------------

    [Fact]
    public void SplitDocument_ReturnsTwoParts()
    {
        var doc = CreateDoc10Paragraphs();
        var parts = doc.SplitDocument(5);
        Assert.NotNull(parts);
        Assert.Equal(2, parts.Length);
    }

    [Fact]
    public void SplitDocument_FirstPartCountCorrect()
    {
        var doc = CreateDoc10Paragraphs();
        var parts = doc.SplitDocument(5);
        Assert.Equal(5, parts[0].GetParagraphCount());
    }

    [Fact]
    public void SplitDocument_SecondPartCountCorrect()
    {
        var doc = CreateDoc10Paragraphs();
        var parts = doc.SplitDocument(5);
        Assert.Equal(6, parts[1].GetParagraphCount());
    }

    [Fact]
    public void SplitDocument_TotalCountPreserved()
    {
        var doc = CreateDoc10Paragraphs();
        var total = doc.GetParagraphCount();
        var parts = doc.SplitDocument(5);
        Assert.Equal(total, parts[0].GetParagraphCount() + parts[1].GetParagraphCount());
    }

    [Fact]
    public void SplitDocument_NoThrow()
    {
        var doc = CreateDoc10Paragraphs();
        var ex = Record.Exception(() => doc.SplitDocument(5));
        Assert.Null(ex);
    }

    [Fact]
    public void SplitDocument_AtIndex1_Works()
    {
        var doc = CreateDoc10Paragraphs();
        var parts = doc.SplitDocument(1);
        Assert.NotNull(parts);
        Assert.Equal(2, parts.Length);
        Assert.Equal(1, parts[0].GetParagraphCount());
        Assert.Equal(doc.GetParagraphCount() - 1, parts[1].GetParagraphCount());
    }

    [Fact]
    public void SplitDocument_PersistBothParts()
    {
        var doc = CreateDoc10Paragraphs();
        var parts = doc.SplitDocument(5);

        var path1 = TempFile("split_part1.fodt");
        var path2 = TempFile("split_part2.fodt");
        parts[0].SaveToFile(path1);
        parts[1].SaveToFile(path2);

        Assert.True(File.Exists(path1));
        Assert.True(File.Exists(path2));

        var loaded1 = FodtDocument.LoadFile(path1);
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(5, loaded1.GetParagraphCount());
        Assert.Equal(6, loaded2.GetParagraphCount());
    }

    [Fact]
    public void SplitDocument_FirstPartHasContent()
    {
        var doc = CreateDoc10Paragraphs();
        var parts = doc.SplitDocument(5);
        var text = parts[0].ExportToPlainText();
        Assert.NotNull(text);
        Assert.True(text.Length > 0);
    }

    // -------------------------------------------------------------------------
    // GetParagraphCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphCount_Correct()
    {
        var doc = CreateDoc10Paragraphs();
        Assert.Equal(11, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_AfterAppendParagraph_Increases()
    {
        var doc = CreateDoc10Paragraphs();
        var before = doc.GetParagraphCount();
        doc.AppendParagraph("New paragraph added.");
        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_AfterInsertHeading_Increases()
    {
        var doc = CreateDoc10Paragraphs();
        var before = doc.GetParagraphCount();
        doc.InsertHeading(doc.GetParagraphCount(), "New Heading", 1);
        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_AfterRemoveParagraphAt_Decreases()
    {
        var doc = CreateDoc10Paragraphs();
        var before = doc.GetParagraphCount();
        doc.RemoveParagraphAt(1);
        Assert.Equal(before - 1, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_AfterRemoveAllParagraphs_Zero()
    {
        var doc = CreateDoc10Paragraphs();
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_Consistent()
    {
        var doc = CreateDoc10Paragraphs();
        Assert.Equal(doc.GetParagraphCount(), doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_EmptyDoc_Zero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_IncludesHeadings()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        doc.AppendParagraph("Body.");
        // Both heading and paragraph count
        Assert.Equal(2, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // CreateEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void CreateEmpty_NonNull()
    {
        Assert.NotNull(FodtDocument.CreateEmpty());
    }

    [Fact]
    public void CreateEmpty_ZeroParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetParagraphCount());
    }

    [Fact]
    public void CreateEmpty_ThenAppendParagraph_Works()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph.");
        Assert.Equal(1, doc.GetParagraphCount());
    }

    [Fact]
    public void CreateEmpty_ThenSaveToFile_Works()
    {
        var doc = FodtDocument.CreateEmpty();
        var path = TempFile("create_empty.fodt");
        var ex = Record.Exception(() => doc.SaveToFile(path));
        Assert.Null(ex);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void CreateEmpty_ThenLoadFile_RoundTrip()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Round-trip paragraph.");
        var path = TempFile("create_empty_rt.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(1, loaded.GetParagraphCount());
    }

    [Fact]
    public void CreateEmpty_MultipleInstances_Independent()
    {
        var doc1 = FodtDocument.CreateEmpty();
        var doc2 = FodtDocument.CreateEmpty();
        doc1.AppendParagraph("Doc1 paragraph.");
        Assert.Equal(1, doc1.GetParagraphCount());
        Assert.Equal(0, doc2.GetParagraphCount());
    }

    [Fact]
    public void CreateEmpty_WordCountZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetWordCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_AppendParagraph_GetParagraphCount_SplitDocument_SaveToFile_Pipeline()
    {
        // CreateEmpty
        var doc = FodtDocument.CreateEmpty();
        Assert.NotNull(doc);
        Assert.Equal(0, doc.GetParagraphCount());

        // Build document
        doc.InsertHeading(0, "Part One", 1);
        doc.AppendParagraph("Alpha introduces the first part of the analysis.");
        doc.AppendParagraph("Beta expands on the key concepts presented.");
        doc.AppendParagraph("Gamma concludes the first part with a summary.");
        doc.InsertHeading(4, "Part Two", 1);
        doc.AppendParagraph("Delta opens the second part of the analysis.");
        doc.AppendParagraph("Epsilon provides supporting evidence for the claims.");
        doc.InsertHeading(7, "Part Three", 1);
        doc.AppendParagraph("Zeta begins the final segment of the document.");
        doc.AppendParagraph("Eta reinforces the conclusions drawn earlier.");
        doc.AppendParagraph("Theta provides the final closing remarks.");

        // GetParagraphCount = 10
        Assert.Equal(11, doc.GetParagraphCount());

        // AppendParagraph increases count
        doc.AppendParagraph("Iota is an additional paragraph for count verification.");
        Assert.Equal(12, doc.GetParagraphCount());

        // InsertHeading increases count
        doc.InsertHeading(11, "Appendix", 1);
        Assert.Equal(13, doc.GetParagraphCount());

        // RemoveParagraphAt decreases count
        doc.RemoveParagraphAt(11); // Remove Appendix
        Assert.Equal(12, doc.GetParagraphCount());

        // GetWordCount positive
        Assert.True(doc.GetWordCount() > 0);

        // SplitDocument at index 5
        var parts = doc.SplitDocument(5);
        Assert.NotNull(parts);
        Assert.Equal(2, parts.Length);
        Assert.Equal(5, parts[0].GetParagraphCount());
        Assert.Equal(7, parts[1].GetParagraphCount());
        Assert.Equal(12, parts[0].GetParagraphCount() + parts[1].GetParagraphCount());

        // SplitDocument doesn't affect original
        Assert.Equal(12, doc.GetParagraphCount());

        // ExportToPlainText on parts
        var part1Text = parts[0].ExportToPlainText();
        var part2Text = parts[1].ExportToPlainText();
        Assert.NotNull(part1Text);
        Assert.NotNull(part2Text);
        Assert.True(part1Text.Length > 0);
        Assert.True(part2Text.Length > 0);

        // CreateEmpty — second instance
        var doc2 = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc2.GetParagraphCount());
        doc2.AppendParagraph("Independent document paragraph.");
        Assert.Equal(1, doc2.GetParagraphCount());
        Assert.Equal(12, doc.GetParagraphCount()); // original unaffected

        // SaveToFile main doc
        var path = TempFile("dogfood_split.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(12, loaded.GetParagraphCount());

        // SplitDocument on loaded
        var loadedParts = loaded.SplitDocument(4);
        Assert.Equal(2, loadedParts.Length);
        Assert.Equal(4, loadedParts[0].GetParagraphCount());
        Assert.Equal(8, loadedParts[1].GetParagraphCount());

        // SaveToFile parts
        var p1Path = TempFile("dogfood_part1.fodt");
        var p2Path = TempFile("dogfood_part2.fodt");
        loadedParts[0].SaveToFile(p1Path);
        loadedParts[1].SaveToFile(p2Path);
        Assert.True(File.Exists(p1Path));
        Assert.True(File.Exists(p2Path));

        var loadedPart1 = FodtDocument.LoadFile(p1Path);
        var loadedPart2 = FodtDocument.LoadFile(p2Path);
        Assert.Equal(4, loadedPart1.GetParagraphCount());
        Assert.Equal(8, loadedPart2.GetParagraphCount());
    }
}
