// Tests for FodtDocument.AppendParagraph, GetPlainText, paragraph management.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R200

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R200: Tests for FodtDocument.AppendParagraph, GetPlainText, paragraph management.
/// AppendParagraph(text): appends a plain paragraph to the document.
/// GetPlainText(): returns all document text as a single string.
/// GetParagraphCount(): returns number of paragraphs.
/// Covers: AppendParagraph increases ParagraphCount; AppendParagraph text in GetPlainText;
/// AppendParagraph multiple paragraphs all in GetPlainText;
/// GetPlainText non-null; GetPlainText non-empty after append;
/// GetPlainText contains paragraph text; GetPlainText contains all paragraphs;
/// GetParagraphCount zero for empty doc; GetParagraphCount positive after append;
/// GetParagraphCount matches inserted count; AppendParagraph order preserved in text;
/// GetPlainText after InsertHeading includes heading text;
/// GetParagraphCount consistent with GetDocumentStats.ParagraphCount;
/// GetPlainText->Contains all appended texts;
/// dogfood CreateEmpty->AppendParagraphs->InsertHeading->GetPlainText->GetParagraphCount verify.
/// </summary>
public class FodtR200AppendParagraphAndGetTextTests
{
    // -------------------------------------------------------------------------
    // AppendParagraph + ParagraphCount
    // -------------------------------------------------------------------------

    [Fact]
    public void AppendParagraph_IncreasesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph.");
        Assert.True(doc.GetParagraphCount() > 0);
    }

    [Fact]
    public void AppendParagraph_MultipleParagraphs_CountMatches()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One.");
        doc.AppendParagraph("Two.");
        doc.AppendParagraph("Three.");
        Assert.Equal(3, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_ZeroForEmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_ConsistentWithDocumentStats()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para A.");
        doc.AppendParagraph("Para B.");
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetParagraphCount(), stats.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // GetPlainText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainText_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text here.");
        var text = doc.GetPlainText();
        Assert.NotNull(text);
    }

    [Fact]
    public void GetPlainText_NonEmpty_AfterAppend()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Content.");
        var text = doc.GetPlainText();
        Assert.False(string.IsNullOrWhiteSpace(text));
    }

    [Fact]
    public void GetPlainText_ContainsParagraphText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox.");
        var text = doc.GetPlainText();
        Assert.Contains("The quick brown fox", text);
    }

    [Fact]
    public void GetPlainText_ContainsAllParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha paragraph.");
        doc.AppendParagraph("Beta paragraph.");
        doc.AppendParagraph("Gamma paragraph.");
        var text = doc.GetPlainText();
        Assert.Contains("Alpha", text);
        Assert.Contains("Beta", text);
        Assert.Contains("Gamma", text);
    }

    [Fact]
    public void GetPlainText_AfterInsertHeading_ContainsHeading()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Heading", 1);
        doc.AppendParagraph("A paragraph.");
        var text = doc.GetPlainText();
        Assert.Contains("My Heading", text);
    }

    [Fact]
    public void GetPlainText_Empty_ForEmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        var text = doc.GetPlainText();
        Assert.True(text == null || text.Trim() == string.Empty);
    }

    [Fact]
    public void GetPlainText_OrderPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First comes first.");
        doc.AppendParagraph("Then comes second.");
        var text = doc.GetPlainText();
        var firstPos = text.IndexOf("First");
        var secondPos = text.IndexOf("second");
        Assert.True(firstPos < secondPos);
    }

    // -------------------------------------------------------------------------
    // GetCharCount / GetWordCount / GetHeadingCount consistency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_PositiveAfterAppend()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Character counting test.");
        Assert.True(doc.GetCharCount() > 0);
    }

    [Fact]
    public void GetWordCount_PositiveAfterAppend()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Word counting in this document.");
        Assert.True(doc.GetWordCount() > 0);
    }

    [Fact]
    public void GetHeadingCount_ZeroWithOnlyParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No headings here.");
        Assert.Equal(0, doc.GetHeadingCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAppendParagraphsInsertHeadingGetPlainTextCountVerify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // InsertHeading
        doc.InsertHeading(0, "Annual Report", 1);

        // AppendParagraph x4
        doc.AppendParagraph("This report covers fiscal year results.");
        doc.AppendParagraph("Revenue grew significantly year over year.");
        doc.InsertHeading(2, "Key Findings", 2);
        doc.AppendParagraph("Key findings highlight operational efficiency.");
        doc.AppendParagraph("Further analysis shows continued improvement.");

        // GetParagraphCount
        Assert.Equal(4, doc.GetParagraphCount());

        // GetHeadingCount
        Assert.Equal(2, doc.GetHeadingCount());

        // GetPlainText
        var text = doc.GetPlainText();
        Assert.NotNull(text);
        Assert.Contains("Annual Report", text);
        Assert.Contains("Revenue grew", text);
        Assert.Contains("Key Findings", text);
        Assert.Contains("Further analysis", text);

        // GetDocumentStats consistency
        var stats = doc.GetDocumentStats();
        Assert.Equal(4, stats.ParagraphCount);
        Assert.Equal(2, stats.HeadingCount);
        Assert.True(stats.WordCount > 0);
        Assert.True(stats.CharacterCount > 0);

        // GetWordCount and GetCharCount
        Assert.Equal(doc.GetWordCount(), stats.WordCount);
        Assert.Equal(doc.GetCharCount(), stats.CharacterCount);
    }
}
