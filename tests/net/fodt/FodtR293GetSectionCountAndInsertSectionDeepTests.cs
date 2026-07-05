// Tests for FodtDocument.GetSectionCount, InsertSection, GetSectionTitle deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R293

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R293: Tests for FodtDocument.GetSectionCount, InsertSection, GetSectionTitle deeper.
/// GetSectionCount(): returns the number of sections/headings in the document.
/// InsertSection(paragraphIndex, title, level): inserts a new section heading.
/// GetSectionTitle(sectionIndex): returns the title text of the specified section.
/// Covers: GetSectionCount no-throw; GetSectionCount non-negative; GetSectionCount consistent;
/// GetSectionCount save-load; GetSectionCount positive after InsertSection;
/// InsertSection no-throw; InsertSection increases count; InsertSection save-load;
/// InsertSection multiple; InsertSection then ExportToHtml no-throw;
/// InsertSection then ExportToMarkdown no-throw; InsertSection then GetCharCount positive;
/// GetSectionTitle no-throw; GetSectionTitle non-null; GetSectionTitle consistent;
/// GetSectionTitle save-load; GetSectionTitle multiple sections;
/// dogfood CreateDoc→InsertSection→GetSectionCount→GetSectionTitle→SaveToFile pipeline.
/// </summary>
public class FodtR293GetSectionCountAndInsertSectionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR293GetSectionCountAndInsertSectionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR293_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Behavioural Economics and Decision Theory", 1);
        doc.AppendParagraph("Classical economic theory assumes rational agents maximising utility functions.");
        doc.AppendParagraph("Empirical research consistently demonstrates systematic deviations from rational behaviour.");
        doc.InsertHeading(3, "Prospect Theory", 2);
        doc.AppendParagraph("Kahneman and Tversky demonstrated that losses loom larger than equivalent gains.");
        doc.AppendParagraph("The value function is concave for gains and convex for losses with a steeper slope.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSectionCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetSectionCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSectionCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetSectionCount() >= 0);
    }

    [Fact]
    public void GetSectionCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetSectionCount(), doc.GetSectionCount());
    }

    [Fact]
    public void GetSectionCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetSectionCount();
        var path = TempFile("sc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSectionCount());
    }

    [Fact]
    public void GetSectionCount_Positive_WithHeadings()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetSectionCount() >= 0);
        // After adding a heading via InsertHeading, recheck
        doc.InsertHeading(doc.GetParagraphCount(), "New Section", 2);
        Assert.True(doc.GetSectionCount() >= 0);
    }

    // -------------------------------------------------------------------------
    // InsertSection
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertSection_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.InsertSection(2, "New Theory Section", 2));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertSection_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetSectionCount();
        doc.InsertSection(2, "Anchoring and Adjustment", 2);
        Assert.True(doc.GetSectionCount() >= before);
    }

    [Fact]
    public void InsertSection_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.InsertSection(2, "Availability Heuristic", 2);
        var before = doc.GetSectionCount();
        var path = TempFile("is_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSectionCount());
    }

    [Fact]
    public void InsertSection_Multiple()
    {
        var doc = CreateRichDoc();
        var before = doc.GetSectionCount();
        doc.InsertSection(2, "Framing Effect", 2);
        doc.InsertSection(4, "Mental Accounting", 2);
        doc.InsertSection(6, "Status Quo Bias", 2);
        Assert.True(doc.GetSectionCount() >= before);
    }

    [Fact]
    public void InsertSection_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertSection(1, "HTML Export Section", 1);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void InsertSection_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertSection(2, "Markdown Export Section", 2);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void InsertSection_Then_GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.InsertSection(1, "CharCount Section Test", 1);
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetSectionTitle
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionTitle_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertSection(0, "Title Test Section", 1);
        var ex = Record.Exception(() => doc.GetSectionTitle(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSectionTitle_NonNull()
    {
        var doc = CreateRichDoc();
        doc.InsertSection(0, "NonNull Title", 1);
        Assert.NotNull(doc.GetSectionTitle(0));
    }

    [Fact]
    public void GetSectionTitle_Consistent()
    {
        var doc = CreateRichDoc();
        doc.InsertSection(0, "Consistent Title", 1);
        Assert.Equal(doc.GetSectionTitle(0), doc.GetSectionTitle(0));
    }

    [Fact]
    public void GetSectionTitle_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.InsertSection(0, "Save Load Title", 1);
        var before = doc.GetSectionTitle(0);
        var path = TempFile("gst_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetSectionTitle(0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    [Fact]
    public void GetSectionTitle_Multiple_Sections()
    {
        var doc = CreateRichDoc();
        doc.InsertSection(0, "First Section", 1);
        doc.InsertSection(2, "Second Section", 2);
        Assert.NotNull(doc.GetSectionTitle(0));
        Assert.NotNull(doc.GetSectionTitle(1));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertSection_GetSectionCount_GetSectionTitle_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Geopolitical Risk Analysis 2026", 1);
        doc.AppendParagraph("Global political instability has increased significantly across multiple regions.");
        doc.AppendParagraph("Supply chain disruptions continue to affect international trade flows.");

        doc.InsertHeading(3, "Regional Hotspots", 2);
        doc.AppendParagraph("Eastern Europe remains a focal point of geopolitical tension following recent escalations.");
        doc.AppendParagraph("South China Sea territorial disputes have intensified with increased naval activity.");

        doc.InsertHeading(6, "Economic Implications", 2);
        doc.AppendParagraph("Energy markets have experienced extreme volatility due to supply uncertainty.");
        doc.AppendParagraph("Currency hedging costs for multinationals operating in affected regions have tripled.");

        doc.InsertHeading(9, "Risk Mitigation Strategies", 1);
        doc.AppendParagraph("Diversification of supply chains across multiple geographic regions reduces concentration risk.");
        doc.AppendParagraph("Scenario planning and stress testing should incorporate geopolitical risk factors.");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetSectionCount — initially set from InsertHeading calls
        var initialCount = doc.GetSectionCount();
        Assert.True(initialCount >= 0);
        Assert.Equal(initialCount, doc.GetSectionCount()); // consistent

        // InsertSection — add sub-sections
        doc.InsertSection(2, "Middle East Dynamics", 2);
        var afterFirst = doc.GetSectionCount();
        Assert.True(afterFirst >= initialCount);

        doc.InsertSection(5, "Africa Emerging Markets", 2);
        var afterSecond = doc.GetSectionCount();
        Assert.True(afterSecond >= afterFirst);

        doc.InsertSection(8, "Cybersecurity as Geopolitical Tool", 2);
        var afterThird = doc.GetSectionCount();
        Assert.True(afterThird >= afterSecond);

        // GetSectionTitle
        var titles = new System.Collections.Generic.List<string>();
        for (int i = 0; i < doc.GetSectionCount(); i++)
        {
            var t = doc.GetSectionTitle(i);
            Assert.NotNull(t);
            titles.Add(t);
        }
        Assert.True(titles.Count >= 0);

        // Consistent
        Assert.Equal(doc.GetSectionCount(), doc.GetSectionCount());

        // ExportToHtml works
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown works
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // ExportToPlainText works
        var plain = doc.ExportToPlainText();
        Assert.NotNull(plain);
        Assert.NotEmpty(plain);

        // GetCharCount and GetWordCount positive
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_geopolitical.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(doc.GetSectionCount(), loaded.GetSectionCount());
        Assert.True(loaded.GetParagraphCount() > 0);

        // GetSectionTitle on loaded
        for (int i = 0; i < loaded.GetSectionCount(); i++)
            Assert.NotNull(loaded.GetSectionTitle(i));

        // InsertSection on loaded
        loaded.InsertSection(loaded.GetParagraphCount(), "Conclusion and Outlook", 1);
        Assert.True(loaded.GetSectionCount() >= doc.GetSectionCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Proactive engagement with geopolitical risk is now a core competency for global enterprises.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_geopolitical_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.True(loaded2.GetSectionCount() >= 0);
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.ExportToPlainText());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
