// Tests for FodtDocument.GetListCount, InsertList, GetListItemCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R275

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R275: Tests for FodtDocument.GetListCount, InsertList, GetListItemCount deeper.
/// GetListCount(): returns the number of lists in the document.
/// InsertList(paragraphIndex, string[]): inserts a bulleted list at the given position.
/// GetListItemCount(listIndex): returns the number of items in the specified list.
/// Covers: GetListCount no-throw; GetListCount non-negative; GetListCount consistent;
/// GetListCount zero for new doc; GetListCount after InsertList increases;
/// GetListCount save-load; InsertList no-throw; InsertList increases GetListCount;
/// InsertList save-load; InsertList multiple lists; InsertList then ExportToHtml no-throw;
/// InsertList then ExportToMarkdown no-throw; InsertList then ExportToPlainText no-throw;
/// GetListItemCount no-throw; GetListItemCount equals items count; GetListItemCount consistent;
/// GetListItemCount save-load; GetListItemCount multiple lists;
/// GetListItems no-throw; GetListItems non-null; GetListItems correct count;
/// dogfood CreateDoc→InsertList→GetListCount→GetListItemCount→GetListItems→SaveToFile pipeline.
/// </summary>
public class FodtR275GetListCountAndInsertListDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR275GetListCountAndInsertListDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR275_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Project Requirements Document", 1);
        doc.AppendParagraph("This document outlines the key requirements for the upcoming platform release.");
        doc.AppendParagraph("All requirements have been approved by the steering committee and product owner.");
        doc.InsertHeading(3, "Functional Requirements", 2);
        doc.AppendParagraph("The system must support all defined functional requirements from the specification.");
        doc.AppendParagraph("Each requirement has been assigned a priority level for implementation planning.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetListCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetListCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetListCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetListCount() >= 0);
    }

    [Fact]
    public void GetListCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetListCount(), doc.GetListCount());
    }

    [Fact]
    public void GetListCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Fresh document without any lists.");
        Assert.Equal(0, doc.GetListCount());
    }

    [Fact]
    public void GetListCount_AfterInsertList_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetListCount();
        doc.InsertList(2, new[] { "Requirement Alpha", "Requirement Beta", "Requirement Gamma" });
        Assert.Equal(before + 1, doc.GetListCount());
    }

    [Fact]
    public void GetListCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "Item One", "Item Two", "Item Three" });
        var before = doc.GetListCount();
        var path = TempFile("lc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListCount());
    }

    // -------------------------------------------------------------------------
    // InsertList
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertList_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.InsertList(2, new[] { "First", "Second", "Third" }));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertList_Increases_GetListCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetListCount();
        doc.InsertList(2, new[] { "A", "B", "C", "D" });
        Assert.Equal(before + 1, doc.GetListCount());
    }

    [Fact]
    public void InsertList_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "Persisted Item 1", "Persisted Item 2" });
        var before = doc.GetListCount();
        var path = TempFile("il_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListCount());
    }

    [Fact]
    public void InsertList_Multiple_Lists()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "Req 1", "Req 2", "Req 3" });
        doc.InsertList(4, new[] { "Dep 1", "Dep 2" });
        doc.InsertList(5, new[] { "Risk A", "Risk B", "Risk C", "Risk D" });
        Assert.Equal(3, doc.GetListCount());
    }

    [Fact]
    public void InsertList_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "HTML item 1", "HTML item 2" });
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void InsertList_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "Markdown item 1", "Markdown item 2" });
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void InsertList_Then_ExportToPlainText_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "Plain text item 1", "Plain text item 2" });
        var ex = Record.Exception(() => doc.ExportToPlainText());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetListItemCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListItemCount_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "A", "B", "C" });
        var ex = Record.Exception(() => doc.GetListItemCount(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetListItemCount_Equals_Items_Count()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "Item 1", "Item 2", "Item 3", "Item 4" });
        Assert.Equal(4, doc.GetListItemCount(0));
    }

    [Fact]
    public void GetListItemCount_Consistent()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "X", "Y", "Z" });
        Assert.Equal(doc.GetListItemCount(0), doc.GetListItemCount(0));
    }

    [Fact]
    public void GetListItemCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "P", "Q", "R", "S" });
        var before = doc.GetListItemCount(0);
        var path = TempFile("lic_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListItemCount(0));
    }

    [Fact]
    public void GetListItemCount_Multiple_Lists()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "A", "B" });
        doc.InsertList(3, new[] { "C", "D", "E", "F" });
        Assert.Equal(2, doc.GetListItemCount(0));
        Assert.Equal(4, doc.GetListItemCount(1));
    }

    // -------------------------------------------------------------------------
    // GetListItems
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListItems_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "Item A", "Item B" });
        var ex = Record.Exception(() => doc.GetListItems(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetListItems_NonNull()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "Item 1", "Item 2" });
        Assert.NotNull(doc.GetListItems(0));
    }

    [Fact]
    public void GetListItems_CorrectCount()
    {
        var doc = CreateRichDoc();
        doc.InsertList(2, new[] { "One", "Two", "Three", "Four", "Five" });
        Assert.Equal(5, doc.GetListItems(0).Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertList_GetListCount_GetListItemCount_GetListItems_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Software Requirements Specification 2026", 1);
        doc.AppendParagraph("This specification defines the complete requirements for the release.");
        doc.AppendParagraph("Requirements are organized by category and priority for implementation.");

        doc.InsertHeading(3, "Functional Requirements", 2);
        doc.AppendParagraph("The following list presents high-priority functional requirements.");
        doc.AppendParagraph("All items have been reviewed and approved by the product steering group.");

        doc.InsertHeading(6, "Non-Functional Requirements", 2);
        doc.AppendParagraph("Performance and security requirements are defined in this section.");
        doc.AppendParagraph("Compliance requirements must be met for all production deployments.");

        doc.InsertHeading(9, "Dependencies", 1);
        doc.AppendParagraph("External system dependencies are listed below for planning purposes.");
        doc.AppendParagraph("All dependency versions have been confirmed with respective vendor teams.");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetListCount — zero initially
        Assert.Equal(0, doc.GetListCount());

        // InsertList — functional requirements
        doc.InsertList(5, new[]
        {
            "User authentication via SSO integration with corporate identity provider",
            "Role-based access control for all document management operations",
            "Real-time collaboration with conflict resolution for concurrent edits",
            "Audit logging for all user actions with seven-year retention",
            "Automated backup every four hours with point-in-time recovery"
        });
        Assert.Equal(1, doc.GetListCount());
        Assert.Equal(5, doc.GetListItemCount(0));

        // InsertList — non-functional requirements
        doc.InsertList(8, new[]
        {
            "System availability of 99.9 percent uptime during business hours",
            "Response time under two hundred milliseconds for ninety-fifth percentile",
            "Data encryption at rest using AES-256 and in transit using TLS 1.3",
            "Compliance with ISO 27001 and SOC 2 Type II standards"
        });
        Assert.Equal(2, doc.GetListCount());
        Assert.Equal(4, doc.GetListItemCount(1));

        // InsertList — dependencies
        doc.InsertList(10, new[]
        {
            "Identity provider: Okta SSO version 4.2 or higher",
            "Message broker: Apache Kafka 3.6 or higher",
            "Database: PostgreSQL 16.0 with streaming replication",
            "Object storage: AWS S3 with versioning enabled",
            "Container platform: Kubernetes 1.29 with network policies",
            "Monitoring: Prometheus with Grafana dashboard stack"
        });
        Assert.Equal(3, doc.GetListCount());
        Assert.Equal(6, doc.GetListItemCount(2));

        // GetListItems
        var funcItems = doc.GetListItems(0);
        Assert.NotNull(funcItems);
        Assert.Equal(5, funcItems.Count);
        foreach (var item in funcItems)
            Assert.NotNull(item);

        var nfItems = doc.GetListItems(1);
        Assert.NotNull(nfItems);
        Assert.Equal(4, nfItems.Count);

        var depItems = doc.GetListItems(2);
        Assert.NotNull(depItems);
        Assert.Equal(6, depItems.Count);

        // Consistent
        Assert.Equal(3, doc.GetListCount());
        Assert.Equal(doc.GetListCount(), doc.GetListCount());
        Assert.Equal(doc.GetListItemCount(0), doc.GetListItemCount(0));

        // ExportToHtml works after lists
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
        var path = TempFile("dogfood_srs.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetListCount());
        Assert.Equal(5, loaded.GetListItemCount(0));
        Assert.Equal(4, loaded.GetListItemCount(1));
        Assert.Equal(6, loaded.GetListItemCount(2));
        Assert.True(loaded.GetParagraphCount() > 0);

        // GetListItems on loaded
        var loadedItems = loaded.GetListItems(0);
        Assert.NotNull(loadedItems);
        Assert.Equal(5, loadedItems.Count);

        // InsertList on loaded
        loaded.InsertList(loaded.GetParagraphCount() - 1, new[] { "Addendum Item 1", "Addendum Item 2" });
        Assert.Equal(4, loaded.GetListCount());
        Assert.Equal(2, loaded.GetListItemCount(3));

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Addendum: all requirements confirmed by architecture review board.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_srs_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetListCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.ExportToPlainText());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
