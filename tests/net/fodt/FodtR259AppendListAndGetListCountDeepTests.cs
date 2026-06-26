// Tests for FodtDocument.AppendList, GetListCount, GetListItems deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R259

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R259: Tests for FodtDocument.AppendList, GetListCount, GetListItems deeper.
/// AppendList(items): appends a bulleted/numbered list to the document.
/// GetListCount(): returns the number of lists in the document.
/// GetListItems(listIndex): returns the items in the specified list.
/// Covers: AppendList no-throw; AppendList increases list count; AppendList multiple;
/// AppendList persist; AppendList single item; AppendList many items;
/// AppendList then ExportToHtml; AppendList then ExportToMarkdown;
/// AppendList then GetListItems count; AppendList then SaveToFile;
/// GetListCount zero for plain doc; GetListCount increases after AppendList;
/// GetListCount consistent; GetListCount no-throw; GetListCount save-load;
/// GetListCount after AppendParagraph unchanged; GetListCount after multiple;
/// GetListItems non-null; GetListItems non-empty; GetListItems count correct;
/// GetListItems contains known; GetListItems consistent; GetListItems no-throw;
/// GetListItems after AppendList correct; GetListItems for second list correct;
/// GetListItems save-load preserved;
/// dogfood CreateDoc→AppendList→GetListCount→GetListItems→SaveToFile pipeline.
/// </summary>
public class FodtR259AppendListAndGetListCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR259AppendListAndGetListCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR259_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateDocWithLists()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Project Overview", 1);
        doc.AppendParagraph("Introduction paragraph before the first list.");
        doc.AppendList(new[] { "Requirement 1: Complete API design", "Requirement 2: Implement core modules", "Requirement 3: Write unit tests", "Requirement 4: Integration testing" });
        doc.AppendParagraph("Paragraph between lists.");
        doc.AppendList(new[] { "Phase 1: Analysis", "Phase 2: Development", "Phase 3: Validation" });
        doc.AppendParagraph("Closing paragraph after lists.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // AppendList
    // -------------------------------------------------------------------------

    [Fact]
    public void AppendList_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.AppendList(new[] { "Item A", "Item B", "Item C" }));
        Assert.Null(ex);
    }

    [Fact]
    public void AppendList_IncreasesListCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetListCount();
        doc.AppendList(new[] { "Alpha", "Beta", "Gamma" });
        Assert.Equal(before + 1, doc.GetListCount());
    }

    [Fact]
    public void AppendList_Multiple()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendList(new[] { "List1-A", "List1-B" });
        doc.AppendList(new[] { "List2-A", "List2-B", "List2-C" });
        doc.AppendList(new[] { "List3-A" });
        Assert.Equal(3, doc.GetListCount());
    }

    [Fact]
    public void AppendList_Persist()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendList(new[] { "Persist-A", "Persist-B", "Persist-C" });
        var path = TempFile("list_persist.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(1, loaded.GetListCount());
    }

    [Fact]
    public void AppendList_SingleItem_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.AppendList(new[] { "Only item" }));
        Assert.Null(ex);
    }

    [Fact]
    public void AppendList_ManyItems_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        var items = new string[20];
        for (int i = 0; i < 20; i++)
            items[i] = $"Item {i + 1}: description for this list entry";
        var ex = Record.Exception(() => doc.AppendList(items));
        Assert.Null(ex);
    }

    [Fact]
    public void AppendList_ThenExportToHtml_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendList(new[] { "Alpha", "Beta", "Gamma" });
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);
    }

    [Fact]
    public void AppendList_ThenExportToMarkdown_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        doc.AppendList(new[] { "First item", "Second item", "Third item" });
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);
    }

    [Fact]
    public void AppendList_ThenGetListItems_CorrectCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendList(new[] { "One", "Two", "Three", "Four" });
        var items = doc.GetListItems(0);
        Assert.Equal(4, items.Count);
    }

    [Fact]
    public void AppendList_ThenSaveToFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendList(new[] { "Save-A", "Save-B" });
        var path = TempFile("list_save.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
    }

    // -------------------------------------------------------------------------
    // GetListCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListCount_ZeroForPlainDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        doc.AppendParagraph("No lists here.");
        Assert.Equal(0, doc.GetListCount());
    }

    [Fact]
    public void GetListCount_IncreasesAfterAppendList()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetListCount());
        doc.AppendList(new[] { "A", "B" });
        Assert.Equal(1, doc.GetListCount());
        doc.AppendList(new[] { "C", "D", "E" });
        Assert.Equal(2, doc.GetListCount());
    }

    [Fact]
    public void GetListCount_Consistent()
    {
        var doc = CreateDocWithLists();
        Assert.Equal(doc.GetListCount(), doc.GetListCount());
    }

    [Fact]
    public void GetListCount_NoThrow()
    {
        var doc = CreateDocWithLists();
        var ex = Record.Exception(() => doc.GetListCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetListCount_SaveLoad_Preserved()
    {
        var doc = CreateDocWithLists();
        var before = doc.GetListCount();
        var path = TempFile("list_count_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListCount());
    }

    [Fact]
    public void GetListCount_AfterAppendParagraph_Unchanged()
    {
        var doc = CreateDocWithLists();
        var before = doc.GetListCount();
        doc.AppendParagraph("Extra paragraph.");
        Assert.Equal(before, doc.GetListCount());
    }

    [Fact]
    public void GetListCount_MultipleInserts()
    {
        var doc = FodtDocument.CreateEmpty();
        for (int i = 0; i < 5; i++)
            doc.AppendList(new[] { $"List {i + 1} item A", $"List {i + 1} item B" });
        Assert.Equal(5, doc.GetListCount());
    }

    // -------------------------------------------------------------------------
    // GetListItems
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListItems_NonNull()
    {
        var doc = CreateDocWithLists();
        Assert.NotNull(doc.GetListItems(0));
    }

    [Fact]
    public void GetListItems_NonEmpty()
    {
        var doc = CreateDocWithLists();
        Assert.True(doc.GetListItems(0).Count > 0);
    }

    [Fact]
    public void GetListItems_CountCorrect_FirstList()
    {
        var doc = CreateDocWithLists();
        // First list has 4 items (Requirements 1-4)
        Assert.Equal(4, doc.GetListItems(0).Count);
    }

    [Fact]
    public void GetListItems_CountCorrect_SecondList()
    {
        var doc = CreateDocWithLists();
        // Second list has 3 items (Phases 1-3)
        Assert.Equal(3, doc.GetListItems(1).Count);
    }

    [Fact]
    public void GetListItems_ContainsKnown()
    {
        var doc = CreateDocWithLists();
        var items = doc.GetListItems(0);
        Assert.True(items.Exists(i => i.Contains("Requirement") || i.Contains("API") || i.Contains("tests")));
    }

    [Fact]
    public void GetListItems_Consistent()
    {
        var doc = CreateDocWithLists();
        var i1 = doc.GetListItems(0);
        var i2 = doc.GetListItems(0);
        Assert.Equal(i1.Count, i2.Count);
    }

    [Fact]
    public void GetListItems_NoThrow()
    {
        var doc = CreateDocWithLists();
        var ex = Record.Exception(() => doc.GetListItems(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetListItems_AfterAppendList_Correct()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendList(new[] { "Apple", "Banana", "Cherry" });
        var items = doc.GetListItems(0);
        Assert.Equal(3, items.Count);
        Assert.True(items.Exists(i => i.Contains("Apple") || i.Contains("Banana") || i.Contains("Cherry")));
    }

    [Fact]
    public void GetListItems_SaveLoad_Preserved()
    {
        var doc = CreateDocWithLists();
        var before = doc.GetListItems(0).Count;
        var path = TempFile("list_items_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListItems(0).Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AppendList_GetListCount_GetListItems_SaveToFile_Pipeline()
    {
        // Build a comprehensive document with multiple lists
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Annual Report 2026", 1);
        doc.AppendParagraph("This report summarizes the company performance for fiscal year 2026.");
        doc.AppendParagraph("Key highlights include record revenue, expanded team, and new product launches.");

        // First list: Achievements
        doc.InsertHeading(3, "Key Achievements", 2);
        doc.AppendList(new[]
        {
            "Revenue exceeded one hundred twenty million dollars",
            "Headcount grew from three hundred to four hundred fifty employees",
            "Launched three new product lines in emerging markets",
            "Customer satisfaction scores reached ninety-two percent",
            "Opened two new regional offices in APAC and LATAM"
        });

        Assert.Equal(1, doc.GetListCount());
        var achievementItems = doc.GetListItems(0);
        Assert.Equal(5, achievementItems.Count);

        // Second list: Challenges
        doc.InsertHeading(doc.GetParagraphCount(), "Challenges", 2);
        doc.AppendParagraph("The following challenges were identified during the year.");
        doc.AppendList(new[]
        {
            "Supply chain disruptions impacted product delivery timelines",
            "Regulatory changes required compliance framework updates",
            "Talent retention in engineering remained competitive"
        });

        Assert.Equal(2, doc.GetListCount());
        var challengeItems = doc.GetListItems(1);
        Assert.Equal(3, challengeItems.Count);

        // Third list: Priorities for 2027
        doc.InsertHeading(doc.GetParagraphCount(), "Priorities for 2027", 1);
        doc.AppendList(new[]
        {
            "Accelerate digital transformation initiatives",
            "Invest in artificial intelligence capabilities",
            "Expand customer success team by thirty percent",
            "Complete ERP system migration by Q2",
            "Launch sustainability report and carbon neutrality program",
            "Increase engineering velocity through platform modernization"
        });

        Assert.Equal(3, doc.GetListCount());
        var priorityItems = doc.GetListItems(2);
        Assert.Equal(6, priorityItems.Count);

        // GetListCount consistent
        Assert.Equal(doc.GetListCount(), doc.GetListCount());

        // GetListItems consistent
        Assert.Equal(doc.GetListItems(0).Count, doc.GetListItems(0).Count);

        // GetListItems contains known text
        Assert.True(achievementItems.Exists(i => i.Contains("Revenue") || i.Contains("revenue") || i.Contains("million")));
        Assert.True(challengeItems.Exists(i => i.Contains("Supply chain") || i.Contains("Regulatory") || i.Contains("Talent")));
        Assert.True(priorityItems.Exists(i => i.Contains("digital") || i.Contains("artificial") || i.Contains("customer")));

        // AppendParagraph does not change list count
        doc.AppendParagraph("Conclusion: the company is positioned for continued growth.");
        Assert.Equal(3, doc.GetListCount());

        // ExportToHtml includes content
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown has headings
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.Contains("#", md);

        // GetWordCount positive
        var wc = doc.GetWordCount();
        Assert.True(wc > 0);

        // Append another list after paragraph
        doc.AppendList(new[] { "Action item 1: Review and approve budget", "Action item 2: Assign department leads" });
        Assert.Equal(4, doc.GetListCount());
        Assert.Equal(2, doc.GetListItems(3).Count);

        // GetListItems for all lists no-throw
        for (int i = 0; i < doc.GetListCount(); i++)
        {
            var ex = Record.Exception(() => doc.GetListItems(i));
            Assert.Null(ex);
            Assert.NotNull(doc.GetListItems(i));
        }

        // SaveToFile
        var path = TempFile("dogfood_report.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetListCount());

        // GetListItems on loaded
        Assert.Equal(5, loaded.GetListItems(0).Count);
        Assert.Equal(3, loaded.GetListItems(1).Count);
        Assert.Equal(6, loaded.GetListItems(2).Count);
        Assert.Equal(2, loaded.GetListItems(3).Count);

        // AppendList on loaded
        loaded.AppendList(new[] { "New action: Prepare Q1 roadmap", "New action: Budget allocation review" });
        Assert.Equal(5, loaded.GetListCount());
        Assert.Equal(2, loaded.GetListItems(4).Count);

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // Final SaveToFile
        var path2 = TempFile("dogfood_report_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetListCount());
        Assert.Equal(5, loaded2.GetListItems(0).Count);
    }
}
