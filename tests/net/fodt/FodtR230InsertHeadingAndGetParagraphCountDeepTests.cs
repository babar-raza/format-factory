// Tests for FodtDocument.InsertHeading, GetParagraphCount, GetHeadingCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R230

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R230: Tests for FodtDocument.InsertHeading, GetParagraphCount, GetHeadingCount deeper.
/// InsertHeading(index, text, level): inserts a heading at the given paragraph index.
/// GetParagraphCount(): returns the total number of paragraphs (headings + body).
/// GetHeadingCount(): returns the number of heading paragraphs.
/// Covers: InsertHeading increases paragraph count; InsertHeading increases heading count;
/// InsertHeading at 0 is first; InsertHeading at end is last; InsertHeading multiple levels;
/// InsertHeading appears in GetDocumentOutline; InsertHeading then GetHeadingParagraphs;
/// GetParagraphCount returns sum of headings + body; GetParagraphCount after AppendParagraph;
/// GetParagraphCount after RemoveAllParagraphs; GetParagraphCount empty doc 0 or minimal;
/// GetHeadingCount non-negative; GetHeadingCount equals GetDocumentOutline count;
/// GetHeadingCount after InsertHeading increases; GetHeadingCount empty doc 0;
/// dogfood CreateEmpty→InsertHeading×4→AppendParagraph×3→GetParagraphCount→GetHeadingCount→SaveToFile pipeline.
/// </summary>
public class FodtR230InsertHeadingAndGetParagraphCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR230InsertHeadingAndGetParagraphCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR230_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // InsertHeading
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertHeading_IncreasesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetParagraphCount();
        doc.InsertHeading(0, "Chapter One", 1);
        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    [Fact]
    public void InsertHeading_IncreasesHeadingCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetHeadingCount();
        doc.InsertHeading(0, "Chapter One", 1);
        Assert.Equal(before + 1, doc.GetHeadingCount());
    }

    [Fact]
    public void InsertHeading_AtZero_IsFirst()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing body paragraph.");
        doc.InsertHeading(0, "First Heading", 1);
        var outline = doc.GetDocumentOutline();
        Assert.Equal("First Heading", outline[0].Text);
    }

    [Fact]
    public void InsertHeading_AtEnd_IsLast()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "First", 1);
        doc.AppendParagraph("Body text.");
        doc.InsertHeading(doc.GetParagraphCount(), "Last Heading", 1);
        var outline = doc.GetDocumentOutline();
        Assert.Equal("Last Heading", outline[outline.Count - 1].Text);
    }

    [Fact]
    public void InsertHeading_MultipleLevels_AllInOutline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter", 1);
        doc.InsertHeading(1, "Section", 2);
        doc.InsertHeading(2, "Subsection", 3);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(3, outline.Count);
        Assert.Equal(1, outline[0].Level);
        Assert.Equal(2, outline[1].Level);
        Assert.Equal(3, outline[2].Level);
    }

    [Fact]
    public void InsertHeading_AppearsInGetDocumentOutline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Unique Heading XYZ", 1);
        var outline = doc.GetDocumentOutline();
        Assert.True(outline.Exists(h => h.Text == "Unique Heading XYZ"));
    }

    [Fact]
    public void InsertHeading_ThenGetHeadingParagraphs_IncludesNew()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "New Heading", 1);
        var headings = doc.GetHeadingParagraphs();
        Assert.NotNull(headings);
        Assert.True(headings.Count > 0);
        Assert.True(headings.Exists(h => h.Text == "New Heading"));
    }

    // -------------------------------------------------------------------------
    // GetParagraphCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphCount_ReturnsSumOfHeadingsAndBody()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.AppendParagraph("Body 1");
        doc.AppendParagraph("Body 2");
        Assert.Equal(3, doc.GetParagraphCount()); // 1 heading + 2 body
    }

    [Fact]
    public void GetParagraphCount_AfterAppendParagraph_Increases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        var before = doc.GetParagraphCount();
        doc.AppendParagraph("New body paragraph.");
        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_EmptyDoc_ZeroOrMinimal()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.GetParagraphCount() >= 0);
    }

    [Fact]
    public void GetParagraphCount_AfterRemoveAll_Decreases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.AppendParagraph("Body 1");
        var before = doc.GetParagraphCount();
        doc.RemoveAllParagraphs();
        Assert.True(doc.GetParagraphCount() < before);
    }

    [Fact]
    public void GetParagraphCount_MatchesHeadingPlusBodyCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.InsertHeading(1, "H2", 2);
        doc.AppendParagraph("Body 1");
        doc.AppendParagraph("Body 2");
        doc.AppendParagraph("Body 3");
        Assert.Equal(5, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // GetHeadingCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingCount_NonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.GetHeadingCount() >= 0);
    }

    [Fact]
    public void GetHeadingCount_EqualsDocumentOutlineCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.AppendParagraph("Body.");
        doc.InsertHeading(2, "H2", 2);
        Assert.Equal(doc.GetDocumentOutline().Count, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_AfterInsertHeading_Increases()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetHeadingCount();
        doc.InsertHeading(0, "New", 1);
        Assert.Equal(before + 1, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_EmptyDoc_Zero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_AfterMultipleInserts_CorrectCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.InsertHeading(1, "H2", 2);
        doc.InsertHeading(2, "H3", 3);
        doc.InsertHeading(3, "H4", 1);
        Assert.Equal(4, doc.GetHeadingCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_InsertHeading_AppendParagraph_GetCounts_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetHeadingCount());

        // InsertHeading × 4
        doc.InsertHeading(0, "Part One", 1);
        doc.InsertHeading(1, "Chapter 1", 2);
        doc.InsertHeading(2, "Section 1.1", 3);
        doc.InsertHeading(3, "Part Two", 1);

        // 4 headings so far
        Assert.Equal(4, doc.GetHeadingCount());
        Assert.Equal(4, doc.GetParagraphCount());

        // AppendParagraph × 3
        doc.AppendParagraph("First body paragraph with initial content.");
        doc.AppendParagraph("Second paragraph provides supporting detail.");
        doc.AppendParagraph("Third paragraph summarizes the section.");

        // 4 headings + 3 body = 7 total
        Assert.Equal(7, doc.GetParagraphCount());
        Assert.Equal(4, doc.GetHeadingCount());

        // GetDocumentOutline matches heading count
        var outline = doc.GetDocumentOutline();
        Assert.Equal(4, outline.Count);
        Assert.Equal("Part One", outline[0].Text);
        Assert.Equal(1, outline[0].Level);
        Assert.Equal("Section 1.1", outline[2].Text);
        Assert.Equal(3, outline[2].Level);

        // GetHeadingParagraphs matches GetHeadingCount
        var headings = doc.GetHeadingParagraphs();
        Assert.Equal(4, headings.Count);

        // SaveToFile
        var path = TempFile("dogfood_counts.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile — verify counts preserved
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.Equal(7, loaded.GetParagraphCount());
        Assert.Equal(4, loaded.GetHeadingCount());

        // InsertHeading on loaded — increases count
        loaded.InsertHeading(loaded.GetParagraphCount(), "Appendix", 1);
        Assert.Equal(5, loaded.GetHeadingCount());
        Assert.Equal(8, loaded.GetParagraphCount());
    }
}
