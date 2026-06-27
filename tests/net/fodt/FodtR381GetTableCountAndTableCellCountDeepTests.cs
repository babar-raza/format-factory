// Tests for FodtDocument.GetTableCount, GetTableCellCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R381

using System;
using System.IO;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R381: Tests for FodtDocument.GetTableCount, GetTableCellCount deeper.
/// GetTableCount(): returns the total number of tables in the document.
/// GetTableCellCount(): returns the total number of table cells across all tables.
/// Covers: GetTableCount no-throw; GetTableCount non-negative; GetTableCount consistent;
/// GetTableCount save-load; GetTableCount increases after InsertTable;
/// GetTableCellCount no-throw; GetTableCellCount non-negative; GetTableCellCount consistent;
/// GetTableCellCount save-load; GetTableCellCount increases after InsertTable;
/// GetTableCellCount ge GetTableCount; dogfood CreateDoc→GetTableCount→GetTableCellCount→SaveToFile pipeline.
/// </summary>
public class FodtR381GetTableCountAndTableCellCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR381GetTableCountAndTableCellCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR381_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateDocWithTables()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Annual Report 2024", 1);
        doc.AppendParagraph("Financial summary tables.");
        doc.InsertTable(new[] { "Quarter", "Revenue", "EBITDA", "Net Profit" },
            new[] {
                new[] { "Q1 2024", "£12.4m", "£3.1m", "£1.8m" },
                new[] { "Q2 2024", "£14.1m", "£3.8m", "£2.2m" },
                new[] { "Q3 2024", "£13.6m", "£3.5m", "£2.0m" },
                new[] { "Q4 2024", "£15.2m", "£4.1m", "£2.5m" }
            });
        doc.AppendParagraph("Headcount table follows.");
        doc.InsertTable(new[] { "Division", "Headcount" },
            new[] {
                new[] { "Technology", "248" },
                new[] { "Finance", "62" },
                new[] { "Operations", "415" }
            });
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCount_NoThrow()
    {
        var doc = CreateDocWithTables();
        var ex = Record.Exception(() => doc.GetTableCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCount_NonNegative()
    {
        var doc = CreateDocWithTables();
        Assert.True(doc.GetTableCount() >= 0);
    }

    [Fact]
    public void GetTableCount_Consistent()
    {
        var doc = CreateDocWithTables();
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_SaveLoad_Consistent()
    {
        var doc = CreateDocWithTables();
        var before = doc.GetTableCount();
        var path = TempFile("tc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    [Fact]
    public void GetTableCount_Increases_After_InsertTable()
    {
        var doc = CreateDocWithTables();
        var before = doc.GetTableCount();
        doc.InsertTable(new[] { "Item", "Value" },
            new[] { new[] { "New entry", "123" } });
        Assert.True(doc.GetTableCount() > before);
    }

    // -------------------------------------------------------------------------
    // GetTableCellCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellCount_NoThrow()
    {
        var doc = CreateDocWithTables();
        var ex = Record.Exception(() => doc.GetTableCellCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCellCount_NonNegative()
    {
        var doc = CreateDocWithTables();
        Assert.True(doc.GetTableCellCount() >= 0);
    }

    [Fact]
    public void GetTableCellCount_Consistent()
    {
        var doc = CreateDocWithTables();
        Assert.Equal(doc.GetTableCellCount(), doc.GetTableCellCount());
    }

    [Fact]
    public void GetTableCellCount_SaveLoad_Consistent()
    {
        var doc = CreateDocWithTables();
        var before = doc.GetTableCellCount();
        var path = TempFile("tcc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCellCount());
    }

    [Fact]
    public void GetTableCellCount_Increases_After_InsertTable()
    {
        var doc = CreateDocWithTables();
        var before = doc.GetTableCellCount();
        doc.InsertTable(new[] { "Col1", "Col2", "Col3" },
            new[] { new[] { "a", "b", "c" }, new[] { "d", "e", "f" } });
        Assert.True(doc.GetTableCellCount() > before);
    }

    [Fact]
    public void GetTableCellCount_Ge_TableCount()
    {
        var doc = CreateDocWithTables();
        // Each table has at least 1 cell
        Assert.True(doc.GetTableCellCount() >= doc.GetTableCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetTableCount_GetTableCellCount_SaveToFile_Pipeline()
    {
        // Legal — UK Competition and Markets Authority (CMA): Merger Assessment Report
        // Statistical tables in a formal merger phase-2 investigation report
        // Phase 2 inquiry into the proposed merger of two major UK supermarket chains

        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "CMA Phase 2 Investigation: Provisional Findings Report", 1);
        doc.AppendParagraph("This provisional findings report sets out the Competition and Markets Authority's (CMA) findings in its Phase 2 investigation into the anticipated merger of Greenleaf Retail Holdings plc with Freshmarket Group Limited, pursuant to section 36(1) of the Enterprise Act 2002.");

        var initialTableCount = doc.GetTableCount();
        Assert.True(initialTableCount >= 0);
        var initialCellCount = doc.GetTableCellCount();
        Assert.Equal(initialCellCount >= 0, true);

        // Chapter 2: Market Share Analysis
        doc.InsertSection("Chapter 2: Market Definition and Shares of Supply");
        doc.InsertHeading(3, "2.1 Grocery Retail Market Shares", 2);
        doc.AppendParagraph("Table 2.1 sets out the parties' estimated shares of supply in the UK grocery retail market by value of sales for the financial year 2023-24.");

        doc.InsertTable(
            new[] { "Retailer", "2022-23 Share (%)", "2023-24 Share (%)", "Change (pp)" },
            new[] {
                new[] { "Tesco plc", "27.4", "26.8", "-0.6" },
                new[] { "Sainsbury's Group", "15.6", "15.9", "+0.3" },
                new[] { "Asda Group", "14.1", "13.7", "-0.4" },
                new[] { "Morrisons", "9.8", "9.6", "-0.2" },
                new[] { "Aldi UK", "9.4", "10.2", "+0.8" },
                new[] { "Lidl GB", "7.2", "7.8", "+0.6" },
                new[] { "Greenleaf Retail Holdings (Party A)", "5.3", "5.6", "+0.3" },
                new[] { "Freshmarket Group (Party B)", "3.2", "3.4", "+0.2" },
                new[] { "Combined (A+B)", "8.5", "9.0", "+0.5" },
                new[] { "All Other", "7.8", "7.6", "-0.2" }
            });

        var countAfterTable1 = doc.GetTableCount();
        Assert.True(countAfterTable1 > initialTableCount);
        var cellCountAfterTable1 = doc.GetTableCellCount();
        Assert.True(cellCountAfterTable1 > initialCellCount);
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount()); // consistent
        Assert.Equal(doc.GetTableCellCount(), doc.GetTableCellCount()); // consistent

        // Chapter 3: Competitive Effects
        doc.InsertSection("Chapter 3: Horizontal Effects Assessment");
        doc.InsertHeading(3, "3.1 Price Concentration Analysis", 2);
        doc.AppendParagraph("Table 3.1 presents the CMA's price-concentration regression results.");

        doc.InsertTable(
            new[] { "Specification", "Coefficient", "Std Error", "t-statistic", "p-value", "Significant" },
            new[] {
                new[] { "HHI (OLS)", "-0.0042", "0.0011", "-3.82", "<0.001", "Yes" },
                new[] { "HHI (IV)", "-0.0038", "0.0014", "-2.71", "0.007", "Yes" },
                new[] { "Local share (OLS)", "-0.0891", "0.0243", "-3.67", "<0.001", "Yes" },
                new[] { "Local share (IV)", "-0.0814", "0.0291", "-2.80", "0.005", "Yes" }
            });

        var countAfterTable2 = doc.GetTableCount();
        Assert.True(countAfterTable2 > countAfterTable1);
        var cellCountAfterTable2 = doc.GetTableCellCount();
        Assert.True(cellCountAfterTable2 > cellCountAfterTable1);
        Assert.Equal(cellCountAfterTable2 >= cellCountAfterTable1, true);

        // Chapter 4: Remedies
        doc.InsertSection("Chapter 4: Remedies Assessment");
        doc.InsertHeading(3, "4.1 Divestiture Package Assessment", 2);
        doc.AppendParagraph("Table 4.1 sets out the CMA's assessment of proposed divestiture packages.");

        doc.InsertTable(
            new[] { "Store Reference", "Location", "Format", "GFA (sq m)", "Annual Turnover (£m)", "CMA Acceptability" },
            new[] {
                new[] { "GRH-001", "Bristol Broadmead", "Superstore", "3,200", "£18.4m", "Acceptable" },
                new[] { "GRH-004", "Leeds Kirkgate", "Supermarket", "1,850", "£11.2m", "Acceptable" },
                new[] { "GRH-009", "Edinburgh Princes St", "Metro", "920", "£8.6m", "Acceptable" },
                new[] { "FMG-002", "Manchester Piccadilly", "Superstore", "2,750", "£16.9m", "Under review" },
                new[] { "FMG-007", "Birmingham Bullring", "Supermarket", "1,600", "£12.3m", "Under review" }
            });

        var finalTableCount = doc.GetTableCount();
        Assert.True(finalTableCount > countAfterTable2);
        var finalCellCount = doc.GetTableCellCount();
        Assert.True(finalCellCount > cellCountAfterTable2);
        Assert.True(finalCellCount >= finalTableCount); // always at least one cell per table

        // Content checks
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);
        Assert.True(doc.GetSectionCount() > 0);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var path1 = TempFile("dogfood_cma_phase2_report.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(finalTableCount, loaded.GetTableCount());
        Assert.Equal(finalCellCount, loaded.GetTableCellCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Add appendix table
        loaded.InsertSection("Appendix A: Store-level Data");
        loaded.InsertHeading(3, "A.1 Store Format Typology", 2);
        loaded.InsertTable(
            new[] { "Format", "GFA Range", "Weekly Footfall", "Typical Products" },
            new[] {
                new[] { "Superstore", ">2,500 sq m", "15,000-35,000", "Full grocery + GM" },
                new[] { "Supermarket", "1,000-2,500 sq m", "8,000-18,000", "Full grocery" },
                new[] { "Metro", "<1,000 sq m", "3,000-10,000", "Convenience + food-to-go" }
            });

        Assert.True(loaded.GetTableCount() > finalTableCount);
        Assert.True(loaded.GetTableCellCount() > finalCellCount);
        Assert.Equal(loaded.GetTableCount(), loaded.GetTableCount()); // consistent

        // Final save
        var path2 = TempFile("dogfood_cma_phase2_report_final.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(loaded.GetTableCount(), final.GetTableCount());
        Assert.Equal(loaded.GetTableCellCount(), final.GetTableCellCount());

        Assert.True(final.GetWordCount() > 0);
        Assert.True(final.GetTableCount() >= finalTableCount);

        var ex1 = Record.Exception(() => final.GetTableCount());
        var ex2 = Record.Exception(() => final.GetTableCellCount());
        var ex3 = Record.Exception(() => final.ExportToHtml());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
