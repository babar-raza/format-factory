// Tests for FodtDocument.GetTableCount, GetBookmarkCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R394

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R394: Tests for FodtDocument.GetTableCount, GetBookmarkCount deeper.
/// GetTableCount(): returns the number of tables in the document.
/// GetBookmarkCount(): returns the number of bookmarks/anchors in the document.
/// Covers: GetTableCount no-throw; GetTableCount non-negative; GetTableCount zero for no-table doc;
/// GetTableCount consistent; GetTableCount increases after InsertTable;
/// GetTableCount save-load; GetBookmarkCount no-throw; GetBookmarkCount non-negative;
/// GetBookmarkCount consistent; GetBookmarkCount save-load;
/// GetBookmarkCount increases after InsertBookmark; dogfood pipeline.
/// </summary>
public class FodtR394GetTableCountAndBookmarkCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR394GetTableCountAndBookmarkCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR394_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateNoTableDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("This document contains no tables — only prose paragraphs.");
        doc.AppendParagraph("A second paragraph provides additional textual content.");
        return doc;
    }

    private static FodtDocument CreateTableDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Financial Summary", 1);
        doc.AppendParagraph("The following tables summarise key performance indicators.");
        doc.InsertTable(0, new[] { "Metric", "Q1", "Q2", "Q3", "Q4" },
            new[] {
                new[] { "Revenue", "1.2M", "1.4M", "1.6M", "1.8M" },
                new[] { "EBITDA", "0.3M", "0.35M", "0.4M", "0.45M" }
            });
        doc.InsertTable(1, new[] { "Region", "Units", "Revenue" },
            new[] {
                new[] { "North", "120", "480K" },
                new[] { "South", "95", "380K" }
            });
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCount_NoThrow()
    {
        var doc = CreateTableDoc();
        var ex = Record.Exception(() => doc.GetTableCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCount_NonNegative()
    {
        var doc = CreateTableDoc();
        Assert.True(doc.GetTableCount() >= 0);
    }

    [Fact]
    public void GetTableCount_Zero_ForNoTableDoc()
    {
        var doc = CreateNoTableDoc();
        Assert.Equal(0, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_Consistent()
    {
        var doc = CreateTableDoc();
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_Increases_After_InsertTable()
    {
        var doc = CreateTableDoc();
        var before = doc.GetTableCount();
        doc.InsertTable(2, new[] { "Item", "Value" },
            new[] { new[] { "Total", "1000K" } });
        Assert.True(doc.GetTableCount() > before);
    }

    [Fact]
    public void GetTableCount_SaveLoad_Consistent()
    {
        var doc = CreateTableDoc();
        var before = doc.GetTableCount();
        var path = TempFile("tc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    // -------------------------------------------------------------------------
    // GetBookmarkCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBookmarkCount_NoThrow()
    {
        var doc = CreateNoTableDoc();
        var ex = Record.Exception(() => doc.GetBookmarkCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBookmarkCount_NonNegative()
    {
        var doc = CreateNoTableDoc();
        Assert.True(doc.GetBookmarkCount() >= 0);
    }

    [Fact]
    public void GetBookmarkCount_Consistent()
    {
        var doc = CreateNoTableDoc();
        Assert.Equal(doc.GetBookmarkCount(), doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_SaveLoad_Consistent()
    {
        var doc = CreateNoTableDoc();
        var before = doc.GetBookmarkCount();
        var path = TempFile("bk_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_Increases_After_InsertBookmark()
    {
        var doc = CreateNoTableDoc();
        var before = doc.GetBookmarkCount();
        doc.InsertBookmark(0, "section_intro");
        Assert.True(doc.GetBookmarkCount() > before);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetTableCount_GetBookmarkCount_Pipeline()
    {
        // Legal — UK Law Commission: Automated Vehicles Act 2024 Explanatory Notes
        // Structured legal document with multiple tables (liability schedules, definitions)
        // and cross-reference bookmarks navigating between sections

        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Automated Vehicles Act 2024 — Explanatory Notes", 1);

        // Part 1: Overview (no tables, no bookmarks yet)
        doc.InsertSection("Part 1: Overview");
        doc.InsertHeading(1, "1.1 Purpose and Scope", 2);
        doc.AppendParagraph("The Automated Vehicles Act 2024 establishes a new legal framework for the authorisation, deployment, and liability regime governing self-driving vehicles on public roads in Great Britain. The Act received Royal Assent on 20 May 2024.");
        doc.AppendParagraph("The legislation implements recommendations from the Law Commission's tripartite review and aligns with the international standards framework established under the UNECE Working Party 29 regulations on automated driving systems.");

        var sc0 = doc.GetTableCount();
        var bk0 = doc.GetBookmarkCount();
        Assert.Equal(0, sc0);
        Assert.True(bk0 >= 0);

        // Part 2: Definitions table
        doc.InsertSection("Part 2: Key Definitions");
        doc.InsertHeading(2, "2.1 Defined Terms", 2);
        doc.InsertBookmark(2, "definitions_table_anchor");
        doc.InsertTable(2, new[] { "Term", "Statutory Definition", "Section Reference" },
            new[] {
                new[] { "Automated Vehicle", "A vehicle capable of performing all driving tasks without human intervention on at least one defined operational design domain", "s.1(2)" },
                new[] { "Authorised Self-Driving Entity", "The person or entity responsible for the safe behaviour of an automated vehicle during authorised self-driving journeys", "s.3(1)" },
                new[] { "No-Driving-Task Limitation", "An operational constraint beyond which the automated vehicle must not engage its self-driving function", "s.2(4)" },
                new[] { "User-In-Charge", "The individual in the vehicle who may be required to take control following a transition demand", "s.4(3)" }
            });

        var sc1 = doc.GetTableCount();
        var bk1 = doc.GetBookmarkCount();
        Assert.True(sc1 > sc0); // one table added
        Assert.True(bk1 > bk0); // one bookmark added

        // Part 3: Liability schedule table
        doc.InsertSection("Part 3: Civil Liability Framework");
        doc.InsertHeading(3, "3.1 Liability Allocation Matrix", 2);
        doc.InsertBookmark(3, "liability_matrix_anchor");
        doc.InsertTable(3, new[] { "Incident Type", "Primary Liable Party", "Secondary Recourse", "Applicable Schedule" },
            new[] {
                new[] { "Collision during authorised self-driving journey", "ASDE (strict liability)", "Manufacturer (product liability)", "Schedule 1" },
                new[] { "Failure of ODD detection", "ASDE", "Software supplier", "Schedule 2" },
                new[] { "User override leading to incident", "User-in-charge", "ASDE (contributory)", "Schedule 3" },
                new[] { "Infrastructure interaction failure", "Local highway authority", "ASDE (shared)", "Schedule 4" },
                new[] { "Cybersecurity breach", "ASDE", "NCSC-certified security provider", "Schedule 5" }
            });

        doc.AppendParagraph("The liability matrix is subject to the caps and time limits set out in Schedule 6 of the Act. Insurers must provide compulsory cover for authorised self-driving journeys under the amended Road Traffic Act 1988, as modified by section 18 of the AV Act 2024.");

        var sc2 = doc.GetTableCount();
        var bk2 = doc.GetBookmarkCount();
        Assert.True(sc2 > sc1); // second table added
        Assert.True(bk2 > bk1); // second bookmark added

        // Part 4: Implementation timeline table
        doc.InsertSection("Part 4: Commencement and Transitional Provisions");
        doc.InsertHeading(4, "4.1 Commencement Schedule", 2);
        doc.InsertBookmark(4, "commencement_schedule_anchor");
        doc.InsertBookmark(4, "transitional_provisions_anchor");
        doc.InsertTable(4, new[] { "Provision", "Commencement Date", "Transitional Arrangement" },
            new[] {
                new[] { "Part 1 (Authorisation regime)", "1 January 2025", "None — immediate effect" },
                new[] { "Part 2 (Incident reporting)", "1 April 2025", "6-month grace period" },
                new[] { "Part 3 (Liability framework)", "1 October 2025", "Prospective only — pre-existing vehicles grandfathered 12 months" },
                new[] { "Part 4 (Enforcement powers)", "1 January 2026", "Phased enforcement — warnings only until July 2026" }
            });

        var sc3 = doc.GetTableCount();
        var bk3 = doc.GetBookmarkCount();
        Assert.True(sc3 > sc2);
        Assert.True(bk3 > bk2); // two additional bookmarks
        Assert.True(doc.GetTableCount() == sc3); // consistent
        Assert.True(doc.GetBookmarkCount() == bk3); // consistent

        // Basic document integrity
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var path1 = TempFile("av_act_2024_explanatory_notes.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(sc3, loaded.GetTableCount());
        Assert.Equal(bk3, loaded.GetBookmarkCount());
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Extend with index table
        loaded.InsertSection("Appendix A: Index of Defined Terms");
        loaded.InsertBookmark(5, "index_anchor");
        loaded.InsertTable(5, new[] { "Term", "First Defined At" },
            new[] {
                new[] { "Automated Vehicle", "s.1" },
                new[] { "ASDE", "s.3" },
                new[] { "User-in-charge", "s.4" }
            });

        var scFinal = loaded.GetTableCount();
        var bkFinal = loaded.GetBookmarkCount();
        Assert.True(scFinal > sc3);
        Assert.True(bkFinal > bk3);

        var path2 = TempFile("av_act_2024_with_index.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(scFinal, final.GetTableCount());
        Assert.Equal(bkFinal, final.GetBookmarkCount());

        var ex1 = Record.Exception(() => final.GetTableCount());
        var ex2 = Record.Exception(() => final.GetBookmarkCount());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
