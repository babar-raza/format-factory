// Tests for FodtDocument.GetListCount, GetListItemCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R364

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R364: Tests for FodtDocument.GetListCount, GetListItemCount deeper.
/// GetListCount(): returns the number of lists (numbered or bulleted) in the document.
/// GetListItemCount(): returns the total number of list items across all lists.
/// Covers: GetListCount no-throw; GetListCount non-negative; GetListCount consistent;
/// GetListCount save-load; GetListItemCount no-throw; GetListItemCount non-negative;
/// GetListItemCount consistent; GetListItemCount save-load;
/// GetListItemCount >= GetListCount; AddListItem then GetListItemCount increases;
/// AddListItem then GetParagraphCount unchanged;
/// dogfood CreateDoc→AddListItem→GetListCount→GetListItemCount→SaveToFile pipeline.
/// </summary>
public class FodtR364GetListCountAndListItemCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR364GetListCountAndListItemCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR364_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Annual Report: Environmental Compliance", 1);
        doc.AppendParagraph("This report summarises the organisation's environmental compliance obligations and performance indicators for the reporting year.");
        doc.AppendParagraph("Compliance obligations are assessed against the requirements of the Environment Act 2021 and the Streamlined Energy and Carbon Reporting (SECR) framework.");
        return doc;
    }

    private static FodtDocument CreateDocWithLists()
    {
        var doc = CreatePlainDoc();
        doc.AddListItem("Carbon emissions reduced by 12% year-on-year", false);
        doc.AddListItem("Renewable energy share increased to 68%", false);
        doc.AddListItem("Waste to landfill below 5% target achieved", false);
        doc.AddListItem("Water consumption per employee down 8%", false);
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetListCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListCount_NoThrow()
    {
        var doc = CreateDocWithLists();
        var ex = Record.Exception(() => doc.GetListCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetListCount_NonNegative()
    {
        var doc = CreateDocWithLists();
        Assert.True(doc.GetListCount() >= 0);
    }

    [Fact]
    public void GetListCount_Consistent()
    {
        var doc = CreateDocWithLists();
        Assert.Equal(doc.GetListCount(), doc.GetListCount());
    }

    [Fact]
    public void GetListCount_SaveLoad_Consistent()
    {
        var doc = CreateDocWithLists();
        var before = doc.GetListCount();
        var path = TempFile("glc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListCount());
    }

    // -------------------------------------------------------------------------
    // GetListItemCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListItemCount_NoThrow()
    {
        var doc = CreateDocWithLists();
        var ex = Record.Exception(() => doc.GetListItemCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetListItemCount_NonNegative()
    {
        var doc = CreateDocWithLists();
        Assert.True(doc.GetListItemCount() >= 0);
    }

    [Fact]
    public void GetListItemCount_Consistent()
    {
        var doc = CreateDocWithLists();
        Assert.Equal(doc.GetListItemCount(), doc.GetListItemCount());
    }

    [Fact]
    public void GetListItemCount_SaveLoad_Consistent()
    {
        var doc = CreateDocWithLists();
        var before = doc.GetListItemCount();
        var path = TempFile("glic_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListItemCount());
    }

    [Fact]
    public void GetListItemCount_GreaterOrEqualTo_GetListCount()
    {
        var doc = CreateDocWithLists();
        Assert.True(doc.GetListItemCount() >= doc.GetListCount());
    }

    [Fact]
    public void AddListItem_Then_GetListItemCount_Increases()
    {
        var doc = CreateDocWithLists();
        var before = doc.GetListItemCount();
        doc.AddListItem("Biodiversity net gain target met", false);
        Assert.True(doc.GetListItemCount() > before);
    }

    [Fact]
    public void AddListItem_Then_GetParagraphCount_Unchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetParagraphCount();
        doc.AddListItem("Energy intensity ratio improved", false);
        Assert.Equal(before, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetListCount_GetListItemCount_SaveToFile_Pipeline()
    {
        // Policy — UK Department for Energy Security & Net Zero (DESNZ)
        // Energy Act 2023 compliance obligations checklist for large energy users
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Energy Act 2023 — Large Energy User Compliance Obligations Register", 1);
        doc.AppendParagraph("This obligations register has been prepared for a large energy user (LEU) with annual consumption exceeding 6,000 MWh in accordance with the requirements of the Energy Act 2023 and the associated Statutory Instruments.");

        doc.InsertHeading(3, "Part 1: Mandatory Disclosure Obligations", 2);
        doc.AppendParagraph("The following disclosure obligations apply to large energy users under the Streamlined Energy and Carbon Reporting (SECR) framework and the Energy Savings Opportunity Scheme (ESOS) Phase 3 (2024-2027):");

        // Section 1 list: disclosure obligations
        doc.AddListItem("Annual energy consumption disclosure in Directors' Report (SECR) — due with accounts filing", false);
        doc.AddListItem("Energy intensity ratio and year-on-year comparison — mandatory for quoted companies", false);
        doc.AddListItem("Methodology statement — describe measurement boundaries and conversion factors used", false);
        doc.AddListItem("Organisational boundary — state whether financial control, operational control, or equity share method applied", false);
        doc.AddListItem("Energy efficiency actions report — minimum 3 material actions implemented during reporting year", false);

        Assert.True(doc.GetListCount() >= 0);
        var listCountAfterPart1 = doc.GetListCount();
        var itemCountAfterPart1 = doc.GetListItemCount();
        Assert.True(itemCountAfterPart1 >= 0);
        Assert.True(itemCountAfterPart1 >= listCountAfterPart1);

        doc.InsertHeading(3, "Part 2: ESOS Phase 3 Assessment Requirements", 2);
        doc.AppendParagraph("Under the Energy Savings Opportunity Scheme Phase 3, the following assessment requirements must be fulfilled by the compliance date of 5 December 2027:");

        // Section 2 list: ESOS requirements
        doc.AddListItem("Notify the Environment Agency of intention to comply via ESOS Portal — by 1 January 2025", false);
        doc.AddListItem("Commission Lead Assessor (must hold accreditation from a recognised professional body: CIBSE, EI, IMECHE)", false);
        doc.AddListItem("Conduct energy audit covering at minimum 90% of total energy consumption by activity area", false);
        doc.AddListItem("Identify energy savings opportunities — calculate potential savings in kWh and cost (£)", false);
        doc.AddListItem("Board sign-off of ESOS compliance report", false);
        doc.AddListItem("Submit compliance notification to Environment Agency by 5 December 2027", false);

        var listCountAfterPart2 = doc.GetListCount();
        var itemCountAfterPart2 = doc.GetListItemCount();
        Assert.True(itemCountAfterPart2 >= itemCountAfterPart1);
        Assert.True(itemCountAfterPart2 >= listCountAfterPart2);
        Assert.Equal(doc.GetListCount(), doc.GetListCount()); // consistent

        doc.InsertHeading(3, "Part 3: Recommended Governance Actions", 2);
        doc.AppendParagraph("In addition to mandatory obligations, the following governance actions are recommended by the Board's Sustainability Committee:");

        // Section 3 list: governance
        doc.AddListItem("Appoint dedicated Energy Manager with direct reporting line to CFO", false);
        doc.AddListItem("Establish Energy Steering Group with quarterly Board-level review", false);
        doc.AddListItem("Implement ISO 50001 Energy Management System (not mandatory but demonstrates best practice)", false);
        doc.AddListItem("Set Science Based Target (SBT) aligned with 1.5°C pathway", false);

        var finalListCount = doc.GetListCount();
        var finalItemCount = doc.GetListItemCount();
        Assert.True(finalListCount >= 0);
        Assert.True(finalItemCount >= finalListCount);
        Assert.True(finalItemCount >= itemCountAfterPart2);

        // Paragraph count unchanged by list additions
        var paraCountBefore = doc.GetParagraphCount();
        doc.AddListItem("Annual third-party energy audit (BSI or equivalent)", false);
        Assert.Equal(paraCountBefore, doc.GetParagraphCount());

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // SaveToFile (initial register)
        var path1 = TempFile("dogfood_energy_act_register.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(doc.GetListCount(), loaded.GetListCount());
        Assert.Equal(doc.GetListItemCount(), loaded.GetListItemCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Add amendments: new obligation from SR2024 update
        loaded.InsertHeading(3, "Amendment 1 (SR2024 Update): Additional Offshore Obligations", 2);
        loaded.AppendParagraph("Following SR2024 Statutory Review, the following additional obligations apply to organisations with offshore energy installations:");
        loaded.AddListItem("Offshore Energy Consumption Return — quarterly submission to Ofgem via Secure Gateway", false);
        loaded.AddListItem("Offshore Installation Energy Efficiency Certificate — annual submission from 2025", false);
        loaded.AddListItem("Cross-border energy flow disclosure (EU ETS linked data) — annually with SECR report", false);

        var amendedListCount = loaded.GetListCount();
        var amendedItemCount = loaded.GetListItemCount();
        Assert.True(amendedItemCount >= finalItemCount + 3);
        Assert.True(amendedItemCount >= amendedListCount);

        // Final save
        var path2 = TempFile("dogfood_energy_act_register_amended.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var amended = FodtDocument.LoadFile(path2);
        Assert.Equal(amendedListCount, amended.GetListCount());
        Assert.Equal(amendedItemCount, amended.GetListItemCount());

        Assert.True(amended.GetWordCount() > 0);
        Assert.True(amended.GetCharCount() > 0);

        var ex1 = Record.Exception(() => amended.ExportToHtml());
        var ex2 = Record.Exception(() => amended.ExportToMarkdown());
        var ex3 = Record.Exception(() => amended.AddListItem("Final governance note", false));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
        Assert.True(amended.GetListItemCount() >= amendedItemCount);
    }
}
