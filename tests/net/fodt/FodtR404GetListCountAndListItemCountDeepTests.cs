// Tests for FodtDocument.GetListCount, GetListItemCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R404

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R404: Tests for FodtDocument.GetListCount, GetListItemCount deeper.
/// GetListCount(): returns the number of list structures (bullet or numbered) in the document.
/// GetListItemCount(): returns the total number of list items across all lists.
/// Covers: GetListCount no-throw; GetListCount non-negative; GetListCount zero for plain doc;
/// GetListCount consistent; GetListCount increases after InsertList;
/// GetListCount save-load;
/// GetListItemCount no-throw; GetListItemCount non-negative;
/// GetListItemCount consistent; GetListItemCount increases after InsertList;
/// GetListItemCount save-load; GetListItemCount geq GetListCount; dogfood pipeline.
/// </summary>
public class FodtR404GetListCountAndListItemCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR404GetListCountAndListItemCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR404_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Plain Document", 1);
        doc.AppendParagraph("This document contains no lists — only paragraph text.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetListCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListCount_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.GetListCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetListCount_NonNegative()
    {
        var doc = CreatePlainDoc();
        Assert.True(doc.GetListCount() >= 0);
    }

    [Fact]
    public void GetListCount_Zero_ForPlainDoc()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(0, doc.GetListCount());
    }

    [Fact]
    public void GetListCount_Consistent()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(doc.GetListCount(), doc.GetListCount());
    }

    [Fact]
    public void GetListCount_Increases_After_InsertList()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetListCount();
        doc.InsertList(0, new[] { "First item", "Second item", "Third item" }, ordered: false);
        Assert.True(doc.GetListCount() > before);
    }

    [Fact]
    public void GetListCount_SaveLoad_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.InsertList(0, new[] { "Alpha", "Beta", "Gamma" }, ordered: false);
        var before = doc.GetListCount();
        var path = TempFile("lc_save.fodt");
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
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.GetListItemCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetListItemCount_NonNegative()
    {
        var doc = CreatePlainDoc();
        Assert.True(doc.GetListItemCount() >= 0);
    }

    [Fact]
    public void GetListItemCount_Consistent()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(doc.GetListItemCount(), doc.GetListItemCount());
    }

    [Fact]
    public void GetListItemCount_Increases_After_InsertList()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetListItemCount();
        doc.InsertList(0, new[] { "Item 1", "Item 2", "Item 3", "Item 4" }, ordered: true);
        Assert.True(doc.GetListItemCount() > before);
    }

    [Fact]
    public void GetListItemCount_SaveLoad_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.InsertList(0, new[] { "Point A", "Point B", "Point C" }, ordered: false);
        var before = doc.GetListItemCount();
        var path = TempFile("li_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListItemCount());
    }

    [Fact]
    public void GetListItemCount_Geq_GetListCount()
    {
        var doc = CreatePlainDoc();
        doc.InsertList(0, new[] { "Item A", "Item B" }, ordered: false);
        doc.InsertList(1, new[] { "Step 1", "Step 2", "Step 3" }, ordered: true);
        Assert.True(doc.GetListItemCount() >= doc.GetListCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetListCount_GetListItemCount_Pipeline()
    {
        // Policy — BEIS / DBT: Industrial Decarbonisation Strategy 2024 Progress Report
        // Policy document with bullet lists of commitments, numbered action plans, and evidence summaries
        // List count and item count verify structural completeness of Parliamentary committee submissions

        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Industrial Decarbonisation Strategy: 2024 Progress Report", 1);
        doc.AppendParagraph("Prepared by: Department for Business and Trade | Reference: DBT/IDS/2024/PROG | October 2024");

        var lc0 = doc.GetListCount();
        var li0 = doc.GetListItemCount();
        Assert.Equal(0, lc0);
        Assert.True(li0 >= 0);

        // Section 1: Priority sectors
        doc.InsertSection("1. Priority Decarbonisation Sectors");
        doc.InsertHeading(1, "1.1 Sector Coverage", 2);
        doc.AppendParagraph("The Industrial Decarbonisation Strategy covers the following key emission-intensive sectors, accounting for 68% of UK industrial CO₂ emissions:");
        doc.InsertList(1, new[] {
            "Iron and Steel — 7.2 MtCO₂e/year (2023 baseline)",
            "Cement and Lime — 6.8 MtCO₂e/year",
            "Chemicals — 12.4 MtCO₂e/year",
            "Refining — 8.1 MtCO₂e/year",
            "Ceramics — 1.4 MtCO₂e/year",
            "Glass — 1.2 MtCO₂e/year",
            "Food and Drink — 3.9 MtCO₂e/year",
            "Paper and Pulp — 2.1 MtCO₂e/year"
        }, ordered: false);

        var lc1 = doc.GetListCount();
        var li1 = doc.GetListItemCount();
        Assert.True(lc1 > lc0); // one list added
        Assert.True(li1 > li0); // 8 items added
        Assert.True(li1 >= lc1);

        // Section 2: Key policy commitments (numbered action plan)
        doc.InsertSection("2. Policy Commitments");
        doc.InsertHeading(2, "2.1 Net Zero Industry Action Plan", 2);
        doc.AppendParagraph("The following actions were committed under the NZIAP framework for delivery by December 2024:");
        doc.InsertList(2, new[] {
            "Establish Industrial Decarbonisation and Energy Efficiency Taskforce with UKIC",
            "Launch £315m Industrial Energy Transformation Fund (IETF) Phase 2B",
            "Complete Heat and Energy Efficiency Deployment Programme pilots",
            "Publish Carbon Capture, Usage and Storage (CCUS) industrial cluster pipeline report",
            "Finalise industrial energy efficiency voluntary agreements with trade bodies",
            "Commission NESTA deep-dive on hydrogen industrial switching economics",
            "Establish Industrial Decarbonisation Research and Innovation Centre (IDRIC) Phase 2"
        }, ordered: true);

        var lc2 = doc.GetListCount();
        var li2 = doc.GetListItemCount();
        Assert.True(lc2 > lc1); // second list added
        Assert.True(li2 > li1); // 7 more items
        Assert.True(li2 >= lc2);

        // Section 3: CCUS cluster status (bullet list)
        doc.InsertSection("3. CCUS Cluster Progress");
        doc.InsertHeading(3, "3.1 Track-1 Clusters", 2);
        doc.AppendParagraph("The following industrial clusters are in Track-1 deployment for CCUS:");
        doc.InsertList(3, new[] {
            "HyNet North West — operational 2027 (industrial capture + hydrogen storage)",
            "East Coast Cluster (Teesside) — operational 2027 (Saltend chemicals + SSI heritage site)",
            "Viking CCS (Humberside) — FID 2025 (National Grid Transmission + bp)",
            "Net Zero Teesside Power — operational 2026 (gas CCGT with full CO₂ capture)"
        }, ordered: false);

        doc.InsertHeading(4, "3.2 Track-2 Pipeline", 2);
        doc.AppendParagraph("Track-2 clusters under evaluation for deployment from 2030:");
        doc.InsertList(4, new[] {
            "Acorn (Scotland) — North Sea CO₂ store using legacy infrastructure",
            "South Wales Industrial Cluster (SWIC) — Port Talbot steel/chemicals integration",
            "Humber Zero — direct air capture integration study"
        }, ordered: false);

        var lc3 = doc.GetListCount();
        var li3 = doc.GetListItemCount();
        Assert.True(lc3 > lc2); // two more lists added
        Assert.True(li3 > li2); // 7 more items
        Assert.True(doc.GetListCount() == lc3); // consistent
        Assert.True(doc.GetListItemCount() == li3); // consistent

        // Basic integrity
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var path1 = TempFile("dbt_ids_progress_2024.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(lc3, loaded.GetListCount());
        Assert.Equal(li3, loaded.GetListItemCount());
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Extend with recommendations
        loaded.InsertSection("4. Parliamentary Committee Recommendations");
        loaded.InsertHeading(5, "4.1 BEIS Committee Response", 2);
        loaded.AppendParagraph("In response to the BEIS Select Committee Inquiry into Industrial Decarbonisation (2023), the Department commits to the following actions:");
        loaded.InsertList(5, new[] {
            "Publish revised industrial carbon intensity targets by sector by March 2025",
            "Increase IETF annual budget from £80m to £120m for 2025/26",
            "Mandate industrial energy audits for all facilities >10GWh/year consumption",
            "Establish cross-departmental working group on industrial hydrogen switching",
            "Publish annual CCUS cluster status dashboard on data.gov.uk"
        }, ordered: true);

        var lcFinal = loaded.GetListCount();
        var liFinal = loaded.GetListItemCount();
        Assert.True(lcFinal > lc3);
        Assert.True(liFinal > li3);
        Assert.True(liFinal >= lcFinal);

        var path2 = TempFile("dbt_ids_with_recommendations.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(lcFinal, final.GetListCount());
        Assert.Equal(liFinal, final.GetListItemCount());

        var ex1 = Record.Exception(() => final.GetListCount());
        var ex2 = Record.Exception(() => final.GetListItemCount());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
