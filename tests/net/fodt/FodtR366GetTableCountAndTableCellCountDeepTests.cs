// Tests for FodtDocument.GetTableCount, GetTableCellCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R366

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R366: Tests for FodtDocument.GetTableCount, GetTableCellCount deeper.
/// GetTableCount(): returns the number of tables in the document.
/// GetTableCellCount(): returns the total number of table cells across all tables.
/// Covers: GetTableCount no-throw; GetTableCount non-negative; GetTableCount consistent;
/// GetTableCount save-load; GetTableCellCount no-throw; GetTableCellCount non-negative;
/// GetTableCellCount consistent; GetTableCellCount save-load;
/// GetTableCellCount >= GetTableCount; InsertTable then GetTableCount increases;
/// InsertTable then GetParagraphCount unchanged;
/// dogfood CreateDoc→InsertTable→GetTableCount→GetTableCellCount→SaveToFile pipeline.
/// </summary>
public class FodtR366GetTableCountAndTableCellCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR366GetTableCountAndTableCellCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR366_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Annual Corporate Governance Report", 1);
        doc.AppendParagraph("This report sets out the Board's approach to corporate governance in the financial year ended 31 December 2024, in accordance with the UK Corporate Governance Code 2018 (the 'Code').");
        doc.AppendParagraph("The Company has complied with all provisions of the Code throughout the financial year, save for the deviations explained in the relevant sections below.");
        return doc;
    }

    private static FodtDocument CreateDocWithTable()
    {
        var doc = CreatePlainDoc();
        doc.InsertTable(new string[,] {
            { "Director", "Role", "Independence", "Committee" },
            { "Sir Geoffrey Hartley", "Chair", "Independent", "Nomination (Chair)" },
            { "Amanda Thornton-Scott", "CEO", "Executive", "None" },
            { "Richard Blakemore", "CFO", "Executive", "None" }
        });
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCount_NoThrow()
    {
        var doc = CreateDocWithTable();
        var ex = Record.Exception(() => doc.GetTableCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCount_NonNegative()
    {
        var doc = CreateDocWithTable();
        Assert.True(doc.GetTableCount() >= 0);
    }

    [Fact]
    public void GetTableCount_Consistent()
    {
        var doc = CreateDocWithTable();
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_SaveLoad_Consistent()
    {
        var doc = CreateDocWithTable();
        var before = doc.GetTableCount();
        var path = TempFile("gtc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    // -------------------------------------------------------------------------
    // GetTableCellCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellCount_NoThrow()
    {
        var doc = CreateDocWithTable();
        var ex = Record.Exception(() => doc.GetTableCellCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCellCount_NonNegative()
    {
        var doc = CreateDocWithTable();
        Assert.True(doc.GetTableCellCount() >= 0);
    }

    [Fact]
    public void GetTableCellCount_Consistent()
    {
        var doc = CreateDocWithTable();
        Assert.Equal(doc.GetTableCellCount(), doc.GetTableCellCount());
    }

    [Fact]
    public void GetTableCellCount_SaveLoad_Consistent()
    {
        var doc = CreateDocWithTable();
        var before = doc.GetTableCellCount();
        var path = TempFile("gtcc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCellCount());
    }

    [Fact]
    public void GetTableCellCount_GreaterOrEqualTo_GetTableCount()
    {
        var doc = CreateDocWithTable();
        Assert.True(doc.GetTableCellCount() >= doc.GetTableCount());
    }

    [Fact]
    public void InsertTable_Then_GetTableCount_Increases()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetTableCount();
        doc.InsertTable(new string[,] {
            { "Item", "Value" },
            { "Revenue", "£2.4bn" },
            { "EBITDA", "£480m" }
        });
        Assert.True(doc.GetTableCount() > before);
    }

    [Fact]
    public void InsertTable_Then_GetParagraphCount_Unchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetParagraphCount();
        doc.InsertTable(new string[,] {
            { "A", "B" },
            { "1", "2" }
        });
        Assert.Equal(before, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetTableCount_GetTableCellCount_SaveToFile_Pipeline()
    {
        // Legal — UK M&A Due Diligence Report: Public-to-Private (P2P) Transaction
        // Multi-table document: target summary, key metrics, risk register, conditions
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Project Neptune — Due Diligence Summary Report", 1);
        doc.AppendParagraph("This report has been prepared by Clifford Chance LLP for the benefit of Neptune BidCo Limited ('Bidco') in connection with the proposed recommended cash acquisition of the entire issued share capital of Meridian Technology Solutions plc ('Target') (the 'Transaction').");
        doc.AppendParagraph("This report is confidential and is addressed solely to Bidco. It should not be relied upon by any other person.");

        Assert.True(doc.GetTableCount() >= 0);
        var tableCountBefore = doc.GetTableCount();
        var cellCountBefore = doc.GetTableCellCount();
        Assert.True(cellCountBefore >= tableCountBefore);

        // Table 1: Transaction Summary
        doc.InsertHeading(3, "1. Transaction Overview", 2);
        doc.InsertTable(new string[,] {
            { "Parameter", "Detail" },
            { "Target Company", "Meridian Technology Solutions plc" },
            { "Target Registration", "Registered in England & Wales (Co. No. 04512837)" },
            { "Bidco", "Neptune BidCo Limited (backed by Arcturus Capital Partners)" },
            { "Transaction Structure", "Recommended Cash Offer under Part 26 CA 2006 (Scheme)" },
            { "Consideration", "425 pence per Target Share (aggregate: £1.82bn)" },
            { "Premium", "32.8% to undisturbed closing price (320p, 14 November 2024)" },
            { "Regulatory Approvals Required", "CMA Phase 1; NSIB (NSI Act 2021 — mandatory notification)" },
            { "Indicative Timetable", "Scheme Court Hearing: March 2025; Effective Date: April 2025" },
            { "Adviser (Target)", "Rothschild & Co; Linklaters LLP" },
            { "Adviser (Bidco)", "Goldman Sachs International; Clifford Chance LLP" }
        });

        var tableCountAfterTable1 = doc.GetTableCount();
        var cellCountAfterTable1 = doc.GetTableCellCount();
        Assert.True(tableCountAfterTable1 > tableCountBefore);
        Assert.True(cellCountAfterTable1 > cellCountBefore);
        Assert.True(cellCountAfterTable1 >= tableCountAfterTable1);

        // Table 2: Financial Metrics
        doc.InsertHeading(3, "2. Target Financial Highlights", 2);
        doc.AppendParagraph("The following key financial metrics have been extracted from Target's audited consolidated accounts for the three years ended 31 March 2024:");
        doc.InsertTable(new string[,] {
            { "Metric (£m)", "FY2022A", "FY2023A", "FY2024A", "FY2025F" },
            { "Revenue", "342.1", "389.4", "421.8", "458.0" },
            { "Gross Profit", "187.2", "217.4", "243.2", "265.7" },
            { "Gross Margin (%)", "54.7%", "55.8%", "57.7%", "58.0%" },
            { "EBITDA", "78.4", "91.6", "104.3", "118.0" },
            { "EBITDA Margin (%)", "22.9%", "23.5%", "24.7%", "25.8%" },
            { "EBIT", "62.1", "73.8", "84.7", "96.0" },
            { "Net Debt / (Cash)", "41.2", "28.7", "(5.4)", "(22.0)" },
            { "Net Debt / EBITDA", "0.5x", "0.3x", "n/m", "n/m" }
        });

        var tableCountAfterTable2 = doc.GetTableCount();
        var cellCountAfterTable2 = doc.GetTableCellCount();
        Assert.True(tableCountAfterTable2 > tableCountAfterTable1);
        Assert.True(cellCountAfterTable2 > cellCountAfterTable1);

        // Table 3: Legal Risk Register
        doc.InsertHeading(3, "3. Key Legal Risk Register", 2);
        doc.InsertTable(new string[,] {
            { "Risk Area", "Severity", "Probability", "Mitigant", "Responsibility" },
            { "NSIB Mandatory Notification", "High", "Certain", "File notification within 30 days of announcement", "Bidco" },
            { "CMA Phase 2 Reference", "Medium", "Low (15%)", "Prepare remedy package: SaaS divestiture", "Bidco" },
            { "Material Adverse Change", "Medium", "Low", "Scheme condition: no MAC — FCA standard definition", "Linklaters" },
            { "Pension Deficit (c.£28m)", "Medium", "Certain", "Agree Pension Trustee support undertaking", "Clifford Chance" },
            { "IP Ownership (3 patents)", "Low", "Medium", "Assignment confirmations from subsidiary", "IP Unit" },
            { "GDPR Data Transfer", "Low", "Low", "Standard Contractual Clauses in place", "DPO" }
        });

        var tableCountAfterTable3 = doc.GetTableCount();
        var cellCountAfterTable3 = doc.GetTableCellCount();
        Assert.True(tableCountAfterTable3 > tableCountAfterTable2);
        Assert.True(cellCountAfterTable3 > cellCountAfterTable2);
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount()); // consistent
        Assert.Equal(doc.GetTableCellCount(), doc.GetTableCellCount()); // consistent

        // Paragraph count unchanged by tables
        var paraCount = doc.GetParagraphCount();
        doc.InsertTable(new string[,] {
            { "Condition", "Status" },
            { "CMA Clearance", "Pending" },
            { "NSIB Clearance", "Pending" }
        });
        Assert.Equal(paraCount, doc.GetParagraphCount());

        var finalTableCount = doc.GetTableCount();
        var finalCellCount = doc.GetTableCellCount();
        Assert.True(finalTableCount > tableCountAfterTable3);
        Assert.True(finalCellCount >= finalTableCount);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // SaveToFile
        var path1 = TempFile("dogfood_neptune_dd_report.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(finalTableCount, loaded.GetTableCount());
        Assert.Equal(finalCellCount, loaded.GetTableCellCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Append additional table to loaded
        loaded.InsertHeading(3, "4. Conditions to the Scheme", 2);
        loaded.InsertTable(new string[,] {
            { "Condition", "Type", "Long-Stop Date" },
            { "Target Shareholder Approval (75% threshold)", "Regulatory", "31 July 2025" },
            { "High Court Sanction", "Regulatory", "31 July 2025" },
            { "CMA Phase 1 Clearance (or expiry of NSIA period)", "Regulatory", "31 May 2025" },
            { "NSIB Clearance or 30-day period expiry", "Regulatory", "30 January 2025" }
        });

        Assert.True(loaded.GetTableCount() > finalTableCount);
        Assert.True(loaded.GetTableCellCount() > finalCellCount);

        // Final save
        var path2 = TempFile("dogfood_neptune_dd_report_final.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(loaded.GetTableCount(), final.GetTableCount());
        Assert.Equal(loaded.GetTableCellCount(), final.GetTableCellCount());

        Assert.True(final.GetWordCount() > 0);
        Assert.True(final.GetCharCount() > 0);

        var ex1 = Record.Exception(() => final.ExportToHtml());
        var ex2 = Record.Exception(() => final.ExportToMarkdown());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
