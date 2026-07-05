// Tests for FodtDocument.GetBookmarkCount, AddBookmark, GetBookmarkName deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R337

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R337: Tests for FodtDocument.GetBookmarkCount, AddBookmark, GetBookmarkName deeper.
/// GetBookmarkCount(): returns the number of bookmarks in the document.
/// AddBookmark(paragraphIndex, name): inserts a named bookmark anchor at the given paragraph.
/// GetBookmarkName(index): returns the name of the bookmark at the given index.
/// Covers: GetBookmarkCount no-throw; GetBookmarkCount non-negative; GetBookmarkCount consistent;
/// GetBookmarkCount zero for new doc; GetBookmarkCount after AddBookmark increases;
/// GetBookmarkCount save-load;
/// AddBookmark no-throw; AddBookmark increases count; AddBookmark save-load;
/// AddBookmark multiple; AddBookmark then ExportToHtml no-throw;
/// AddBookmark then ExportToMarkdown no-throw; AddBookmark then GetWordCount positive;
/// GetBookmarkName no-throw; GetBookmarkName non-null; GetBookmarkName consistent;
/// GetBookmarkName save-load;
/// dogfood CreateDoc→AddBookmark→GetBookmarkCount→GetBookmarkName→SaveToFile pipeline.
/// </summary>
public class FodtR337GetBookmarkCountAndAddBookmarkDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR337GetBookmarkCountAndAddBookmarkDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR337_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateLegalDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Service Level Agreement: Cloud Infrastructure Managed Services — Enterprise Tier", 1);
        doc.AppendParagraph("This Service Level Agreement (SLA) between CloudOps Limited (\"Provider\") and the subscribing enterprise entity (\"Customer\") defines availability commitments, performance metrics, and remediation procedures for managed cloud infrastructure services.");
        doc.AppendParagraph("Capitalised terms used herein shall have the meanings ascribed in Schedule 1 (Definitions) and the Master Services Agreement (MSA) referenced by its execution date.");
        doc.InsertHeading(3, "Service Availability Commitments", 2);
        doc.AppendParagraph("The Provider commits to 99.95% monthly uptime for Tier 1 production workloads, calculated as [(Total Minutes − Downtime Minutes) / Total Minutes] × 100, excluding scheduled maintenance windows notified with minimum 72 hours' notice.");
        doc.AppendParagraph("Downtime is defined as a continuous period exceeding five (5) minutes during which the service is unavailable or response latency exceeds the P99 threshold specified in Schedule 2 for more than 10% of API calls.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetBookmarkCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBookmarkCount_NoThrow()
    {
        var doc = CreateLegalDoc();
        var ex = Record.Exception(() => doc.GetBookmarkCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBookmarkCount_NonNegative()
    {
        var doc = CreateLegalDoc();
        Assert.True(doc.GetBookmarkCount() >= 0);
    }

    [Fact]
    public void GetBookmarkCount_Consistent()
    {
        var doc = CreateLegalDoc();
        Assert.Equal(doc.GetBookmarkCount(), doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with no bookmarks.");
        Assert.Equal(0, doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_AfterAddBookmark_Increases()
    {
        var doc = CreateLegalDoc();
        var before = doc.GetBookmarkCount();
        doc.AddBookmark(1, "sec_definitions");
        Assert.Equal(before + 1, doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_SaveLoad_Consistent()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(2, "sec_availability");
        var before = doc.GetBookmarkCount();
        var path = TempFile("bmc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBookmarkCount());
    }

    // -------------------------------------------------------------------------
    // AddBookmark
    // -------------------------------------------------------------------------

    [Fact]
    public void AddBookmark_NoThrow()
    {
        var doc = CreateLegalDoc();
        var ex = Record.Exception(() => doc.AddBookmark(0, "bm_introduction"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Increases_Count()
    {
        var doc = CreateLegalDoc();
        var before = doc.GetBookmarkCount();
        doc.AddBookmark(3, "bm_uptime_commitment");
        Assert.Equal(before + 1, doc.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_SaveLoad_Persists()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(4, "bm_downtime_definition");
        var before = doc.GetBookmarkCount();
        var path = TempFile("ab_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_Multiple()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(0, "bm_preamble");
        doc.AddBookmark(1, "bm_definitions");
        doc.AddBookmark(3, "bm_availability");
        Assert.Equal(3, doc.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(2, "bm_html_export");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(1, "bm_md_export");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Then_GetWordCount_Positive()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(0, "bm_wordcount");
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetBookmarkName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBookmarkName_NoThrow()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(1, "bm_retrieve");
        var ex = Record.Exception(() => doc.GetBookmarkName(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBookmarkName_NonNull()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(2, "bm_nonnull");
        Assert.NotNull(doc.GetBookmarkName(0));
    }

    [Fact]
    public void GetBookmarkName_Consistent()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(0, "bm_consistent");
        Assert.Equal(doc.GetBookmarkName(0), doc.GetBookmarkName(0));
    }

    [Fact]
    public void GetBookmarkName_SaveLoad_Consistent()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(3, "bm_saveload");
        var path = TempFile("bmn_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetBookmarkName(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddBookmark_GetBookmarkCount_GetBookmarkName_SaveToFile_Pipeline()
    {
        // Policy document — UK Government Digital Service (GDS) accessibility and design standards
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Government Digital Service: Accessibility Requirements and Design Standards for Public-Facing Digital Services", 1);
        doc.AppendParagraph("All public-facing digital services provided by UK government departments and arm's-length bodies must comply with the Web Content Accessibility Guidelines (WCAG) 2.2 at Level AA as mandated by the Public Sector Bodies Accessibility Regulations 2018, SI 2018/952.");
        doc.AppendParagraph("These requirements apply to websites, mobile applications, and digital tools that are intended to be used by or on behalf of members of the public, regardless of whether they are hosted on GOV.UK or on departmental domains.");

        doc.InsertHeading(3, "Perceivable Content Standards", 2);
        doc.AppendParagraph("All non-text content must have a text alternative that serves the equivalent purpose, with appropriate implementation depending on whether the content is decorative, functional, or informational (WCAG Success Criterion 1.1.1).");
        doc.AppendParagraph("Sufficient colour contrast ratios must be maintained: minimum 4.5:1 for normal text (below 18pt regular or 14pt bold) and 3:1 for large text and user interface components (WCAG SC 1.4.3 and 1.4.11).");

        doc.InsertHeading(6, "Operable Interface Requirements", 2);
        doc.AppendParagraph("All functionality must be operable through a keyboard interface without requiring specific timings for individual keystrokes, ensuring compatibility with keyboard-only users and alternative input devices (WCAG SC 2.1.1).");
        doc.AppendParagraph("Focus order must be logical and sequential, preserving meaning and operability. Focus indicators must have a minimum area of the perimeter of the unfocused component multiplied by the CSS property outline-width, with a contrast ratio of at least 3:1 against adjacent colours (WCAG SC 2.4.11).");

        doc.InsertHeading(9, "Understandable Content", 1);
        doc.AppendParagraph("Error messages must identify the item in error and describe what the error is in text, using clear, plain English language following the GDS style guide. Inline validation should be provided where technically feasible for form fields exceeding three inputs.");
        doc.AppendParagraph("Time limits must include mechanisms to extend, adjust, or disable them, unless the time limit is a fundamental requirement or extends beyond 20 hours, in accordance with WCAG SC 2.2.1.");

        Assert.Equal(12, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetBookmarkCount());

        // AddBookmark — navigation anchors for accessibility standards document
        doc.AddBookmark(0, "bm_introduction");
        Assert.Equal(1, doc.GetBookmarkCount());

        doc.AddBookmark(1, "bm_scope_definition");
        Assert.Equal(2, doc.GetBookmarkCount());

        doc.AddBookmark(3, "bm_perceivable_non_text");
        Assert.Equal(3, doc.GetBookmarkCount());

        doc.AddBookmark(4, "bm_colour_contrast");
        Assert.Equal(4, doc.GetBookmarkCount());

        doc.AddBookmark(5, "bm_keyboard_operability");
        Assert.Equal(5, doc.GetBookmarkCount());

        doc.AddBookmark(6, "bm_focus_order");
        Assert.Equal(6, doc.GetBookmarkCount());

        // Consistent
        Assert.Equal(doc.GetBookmarkCount(), doc.GetBookmarkCount());

        // GetBookmarkName
        var name0 = doc.GetBookmarkName(0);
        Assert.NotNull(name0);
        Assert.Equal(name0, doc.GetBookmarkName(0)); // consistent

        var name3 = doc.GetBookmarkName(3);
        Assert.NotNull(name3);

        var name5 = doc.GetBookmarkName(5);
        Assert.NotNull(name5);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // GetWordCount positive
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_gds_accessibility.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetBookmarkCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetBookmarkName(0));
        Assert.NotNull(loaded.GetBookmarkName(5));

        // AddBookmark on loaded
        loaded.AddBookmark(8, "bm_error_messages");
        Assert.Equal(7, loaded.GetBookmarkCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: compliance with WCAG 2.2 AA and the GDS design standards is a legal obligation and a fundamental design requirement for all UK government digital services, ensuring equitable access for all users including those with disabilities.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_gds_accessibility_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetBookmarkCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetBookmarkName(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddBookmark(0, "bm_final"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
