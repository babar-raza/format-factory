// Tests for FodtDocument.GetFooterText, SetFooterText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R362

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R362: Tests for FodtDocument.GetFooterText, SetFooterText deeper.
/// GetFooterText(): returns the current footer text of the document.
/// SetFooterText(text): sets the document footer text.
/// Covers: GetFooterText no-throw; GetFooterText non-null; GetFooterText consistent;
/// GetFooterText save-load; SetFooterText no-throw;
/// SetFooterText then GetFooterText updated; SetFooterText then GetParagraphCount unchanged;
/// SetFooterText then ExportToHtml no-throw; SetFooterText then ExportToMarkdown no-throw;
/// SetFooterText save-load; SetFooterText override; SetFooterText then GetWordCount positive;
/// dogfood CreateDoc→SetFooterText→GetFooterText→SaveToFile pipeline.
/// </summary>
public class FodtR362GetFooterTextAndSetFooterTextDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR362GetFooterTextAndSetFooterTextDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR362_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreatePlainDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Contract: Software Development Services Agreement", 1);
        doc.AppendParagraph("This Software Development Services Agreement (the 'Agreement') is entered into as of the Effective Date between TechVentures Ltd (company registration 12345678), a company incorporated under the laws of England and Wales ('Developer'), and ClientCo Ltd (company registration 87654321) ('Client').");
        doc.AppendParagraph("The Developer agrees to provide software development services as described in Schedule 1 to this Agreement, including the design, development, testing, and deployment of the software system specified therein.");
        doc.AppendParagraph("All intellectual property rights in the deliverables shall vest in the Client upon payment of all amounts due under this Agreement, subject to the Developer retaining rights to pre-existing intellectual property incorporated in the deliverables.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetFooterText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFooterText_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.GetFooterText());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFooterText_NonNull()
    {
        var doc = CreatePlainDoc();
        Assert.NotNull(doc.GetFooterText());
    }

    [Fact]
    public void GetFooterText_Consistent()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(doc.GetFooterText(), doc.GetFooterText());
    }

    [Fact]
    public void GetFooterText_SaveLoad_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.SetFooterText("STRICTLY CONFIDENTIAL — Page [n]");
        var before = doc.GetFooterText();
        var path = TempFile("gft_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFooterText());
    }

    // -------------------------------------------------------------------------
    // SetFooterText
    // -------------------------------------------------------------------------

    [Fact]
    public void SetFooterText_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.SetFooterText("Confidential"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetFooterText_Then_GetFooterText_Updated()
    {
        var doc = CreatePlainDoc();
        doc.SetFooterText("TechVentures Ltd — Confidential — v1.0");
        Assert.Equal("TechVentures Ltd — Confidential — v1.0", doc.GetFooterText());
    }

    [Fact]
    public void SetFooterText_Then_GetParagraphCount_Unchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetParagraphCount();
        doc.SetFooterText("Page [n] of [p]");
        Assert.Equal(before, doc.GetParagraphCount());
    }

    [Fact]
    public void SetFooterText_Then_ExportToHtml_NoThrow()
    {
        var doc = CreatePlainDoc();
        doc.SetFooterText("Confidential — Not for Distribution");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void SetFooterText_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreatePlainDoc();
        doc.SetFooterText("Draft Agreement — v0.3");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void SetFooterText_SaveLoad_Persists()
    {
        var doc = CreatePlainDoc();
        doc.SetFooterText("© TechVentures Ltd 2024 — All Rights Reserved");
        var path = TempFile("sft_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal("© TechVentures Ltd 2024 — All Rights Reserved", loaded.GetFooterText());
    }

    [Fact]
    public void SetFooterText_Override()
    {
        var doc = CreatePlainDoc();
        doc.SetFooterText("Draft v1");
        doc.SetFooterText("Final v2");
        Assert.Equal("Final v2", doc.GetFooterText());
    }

    [Fact]
    public void SetFooterText_Then_GetWordCount_Positive()
    {
        var doc = CreatePlainDoc();
        doc.SetFooterText("Confidential");
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFooterText_SetFooterText_SaveToFile_Pipeline()
    {
        // Corporate law — UK Takeover Panel Rules: acquisition announcement lifecycle
        // Document footer management for Rule 2.7 firm offer announcement workflow
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Rule 2.7 Announcement: Recommended Cash Offer for MediaTech Group plc by AcquireCo Holdings Ltd", 1);
        doc.AppendParagraph("NOT FOR RELEASE, PUBLICATION OR DISTRIBUTION, IN WHOLE OR IN PART, IN OR INTO THE UNITED STATES, CANADA, AUSTRALIA, JAPAN, THE REPUBLIC OF SOUTH AFRICA OR ANY OTHER JURISDICTION WHERE TO DO SO WOULD CONSTITUTE A VIOLATION OF THE RELEVANT LAWS OR REGULATIONS OF SUCH JURISDICTION.");

        doc.InsertHeading(3, "The Offer", 2);
        doc.AppendParagraph("AcquireCo Holdings Ltd ('AcquireCo') and the Board of Directors of MediaTech Group plc ('MediaTech') are pleased to announce that they have reached agreement on the terms of a recommended cash offer to be made by AcquireCo for the entire issued and to be issued ordinary share capital of MediaTech (the 'Offer').");
        doc.AppendParagraph("Under the terms of the Offer, MediaTech shareholders will receive: 425 pence in cash for each MediaTech Share. The Offer values the entire issued ordinary share capital of MediaTech at approximately £1.82 billion and represents a premium of approximately 32.8% to MediaTech's closing share price of 320 pence on 15 November 2024 (the last Business Day before the date of this announcement).");

        doc.InsertHeading(3, "Recommendation", 2);
        doc.AppendParagraph("The Board of Directors of MediaTech, who have been so advised by Rothschild & Co as to the financial terms of the Offer, consider the terms of the Offer to be fair and reasonable. In providing advice to the Board of Directors of MediaTech, Rothschild & Co has taken into account the commercial assessments of the Board of Directors of MediaTech.");
        doc.AppendParagraph("Accordingly, the Board of Directors of MediaTech unanimously recommends that MediaTech shareholders accept the Offer, as they have irrevocably undertaken to do in respect of their own holdings.");

        doc.InsertHeading(3, "Financing", 2);
        doc.AppendParagraph("Goldman Sachs International, as financial adviser to AcquireCo, is satisfied that sufficient resources are available to AcquireCo to satisfy in full the consideration payable to MediaTech shareholders under the Offer. The Offer is financed from AcquireCo's existing cash resources and a committed acquisition facility provided by Barclays Bank UK PLC.");

        Assert.Equal(5, doc.GetParagraphCount());

        // GetFooterText — initially empty/default
        var initialFooter = doc.GetFooterText();
        Assert.NotNull(initialFooter);
        Assert.Equal(doc.GetFooterText(), doc.GetFooterText()); // consistent

        // SetFooterText — pre-clearance draft
        doc.SetFooterText("DRAFT — SUBJECT TO RULE 2.7 ANNOUNCEMENT — NOT FOR RELEASE WITHOUT TAKEOVER PANEL CLEARANCE");
        Assert.Equal("DRAFT — SUBJECT TO RULE 2.7 ANNOUNCEMENT — NOT FOR RELEASE WITHOUT TAKEOVER PANEL CLEARANCE",
                     doc.GetFooterText());
        Assert.Equal(5, doc.GetParagraphCount()); // unchanged

        // ExportToHtml with footer
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown with footer
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // GetWordCount positive
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile (draft)
        var path1 = TempFile("dogfood_rule27_draft.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify footer
        var draft = FodtDocument.LoadFile(path1);
        Assert.Equal("DRAFT — SUBJECT TO RULE 2.7 ANNOUNCEMENT — NOT FOR RELEASE WITHOUT TAKEOVER PANEL CLEARANCE",
                     draft.GetFooterText());
        Assert.Equal(5, draft.GetParagraphCount());

        // SetFooterText — panel clearance obtained
        draft.SetFooterText("CLEARED FOR RELEASE — Takeover Panel ref: 2024/TPC/4821 — Release: 07:00 GMT 18 Nov 2024");
        Assert.Equal("CLEARED FOR RELEASE — Takeover Panel ref: 2024/TPC/4821 — Release: 07:00 GMT 18 Nov 2024",
                     draft.GetFooterText());

        // AppendParagraph — dissemination notice added
        draft.AppendParagraph("Evercore ISI and Goldman Sachs International are acting exclusively for AcquireCo and no one else in connection with the Offer and will not be responsible to anyone other than AcquireCo for providing the protections afforded to clients of Evercore ISI or Goldman Sachs International nor for providing advice in relation to the Offer or any other matters referred to in this announcement.");
        Assert.Equal(6, draft.GetParagraphCount());
        Assert.Equal("CLEARED FOR RELEASE — Takeover Panel ref: 2024/TPC/4821 — Release: 07:00 GMT 18 Nov 2024",
                     draft.GetFooterText());

        // SaveToFile (cleared)
        var path2 = TempFile("dogfood_rule27_cleared.fodt");
        draft.SaveToFile(path2);
        Assert.True(File.Exists(path2));

        // LoadFile and verify
        var cleared = FodtDocument.LoadFile(path2);
        Assert.Equal("CLEARED FOR RELEASE — Takeover Panel ref: 2024/TPC/4821 — Release: 07:00 GMT 18 Nov 2024",
                     cleared.GetFooterText());
        Assert.Equal(6, cleared.GetParagraphCount());

        // SetFooterText — post-release archive version
        cleared.SetFooterText("RELEASED — 07:00 GMT 18 Nov 2024 — MediaTech Group plc Rule 2.7 Announcement — AcquireCo Holdings Ltd");
        Assert.Equal("RELEASED — 07:00 GMT 18 Nov 2024 — MediaTech Group plc Rule 2.7 Announcement — AcquireCo Holdings Ltd",
                     cleared.GetFooterText());

        // Final save
        var path3 = TempFile("dogfood_rule27_released.fodt");
        cleared.SaveToFile(path3);
        Assert.True(File.Exists(path3));
        var released = FodtDocument.LoadFile(path3);
        Assert.Equal("RELEASED — 07:00 GMT 18 Nov 2024 — MediaTech Group plc Rule 2.7 Announcement — AcquireCo Holdings Ltd",
                     released.GetFooterText());
        Assert.Equal(6, released.GetParagraphCount());

        var ex1 = Record.Exception(() => released.ExportToHtml());
        var ex2 = Record.Exception(() => released.ExportToMarkdown());
        var ex3 = Record.Exception(() => released.SetFooterText("ARCHIVED"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
        Assert.Equal("ARCHIVED", released.GetFooterText());
    }
}
