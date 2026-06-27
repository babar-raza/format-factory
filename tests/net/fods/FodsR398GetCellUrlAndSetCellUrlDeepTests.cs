// Tests for FodsDocument.GetCellUrl, SetCellUrl deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R398

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R398: Tests for FodsDocument.GetCellUrl, SetCellUrl deeper.
/// GetCellUrl(sheet, row, col): returns the URL/hyperlink associated with a cell, or null if none.
/// SetCellUrl(sheet, row, col, url): attaches a URL hyperlink to the specified cell.
/// Covers: GetCellUrl no-throw; GetCellUrl null for no-url cell; GetCellUrl consistent;
/// GetCellUrl save-load; SetCellUrl no-throw; SetCellUrl then GetCellUrl non-null;
/// SetCellUrl value unchanged; SetCellUrl sheet count unchanged;
/// SetCellUrl then ExportToHtml no-throw; SetCellUrl override; SetCellUrl save-load;
/// SetCellUrl multiple cells; dogfood CreateDoc→SetCellUrl→GetCellUrl→SaveToFile pipeline.
/// </summary>
public class FodsR398GetCellUrlAndSetCellUrlDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR398GetCellUrlAndSetCellUrlDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR398_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateRegulatoryDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Regulatory References");
        doc.SetCellValue("Regulatory References", 0, 0, "Regulation");
        doc.SetCellValue("Regulatory References", 0, 1, "Short Title");
        doc.SetCellValue("Regulatory References", 0, 2, "Authority");
        doc.SetCellValue("Regulatory References", 0, 3, "Link");
        doc.SetCellValue("Regulatory References", 1, 0, "CRR2");
        doc.SetCellValue("Regulatory References", 1, 1, "Capital Requirements Regulation (EU) 2019/876");
        doc.SetCellValue("Regulatory References", 1, 2, "EBA");
        doc.SetCellValue("Regulatory References", 1, 3, "View");
        doc.SetCellValue("Regulatory References", 2, 0, "DORA");
        doc.SetCellValue("Regulatory References", 2, 1, "Digital Operational Resilience Act (EU) 2022/2554");
        doc.SetCellValue("Regulatory References", 2, 2, "EBA/ESMA/EIOPA");
        doc.SetCellValue("Regulatory References", 2, 3, "View");
        doc.SetCellValue("Regulatory References", 3, 0, "SFDR");
        doc.SetCellValue("Regulatory References", 3, 1, "Sustainable Finance Disclosure Regulation (EU) 2019/2088");
        doc.SetCellValue("Regulatory References", 3, 2, "ESMA");
        doc.SetCellValue("Regulatory References", 3, 3, "View");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellUrl
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellUrl_NoThrow()
    {
        var doc = CreateRegulatoryDoc();
        doc.SetCellUrl("Regulatory References", 1, 3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0876");
        var ex = Record.Exception(() => doc.GetCellUrl("Regulatory References", 1, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellUrl_Null_ForNoUrl()
    {
        var doc = CreateRegulatoryDoc();
        Assert.Null(doc.GetCellUrl("Regulatory References", 1, 0));
    }

    [Fact]
    public void GetCellUrl_Consistent()
    {
        var doc = CreateRegulatoryDoc();
        doc.SetCellUrl("Regulatory References", 1, 3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0876");
        Assert.Equal(doc.GetCellUrl("Regulatory References", 1, 3),
                     doc.GetCellUrl("Regulatory References", 1, 3));
    }

    [Fact]
    public void GetCellUrl_SaveLoad_Consistent()
    {
        var doc = CreateRegulatoryDoc();
        doc.SetCellUrl("Regulatory References", 2, 3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554");
        var before = doc.GetCellUrl("Regulatory References", 2, 3);
        var path = TempFile("gcu_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellUrl("Regulatory References", 2, 3));
    }

    // -------------------------------------------------------------------------
    // SetCellUrl
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellUrl_NoThrow()
    {
        var doc = CreateRegulatoryDoc();
        var ex = Record.Exception(() =>
            doc.SetCellUrl("Regulatory References", 1, 3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0876"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellUrl_Then_GetCellUrl_NonNull()
    {
        var doc = CreateRegulatoryDoc();
        doc.SetCellUrl("Regulatory References", 1, 3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0876");
        Assert.NotNull(doc.GetCellUrl("Regulatory References", 1, 3));
    }

    [Fact]
    public void SetCellUrl_ValueUnchanged()
    {
        var doc = CreateRegulatoryDoc();
        var before = doc.GetCellValue("Regulatory References", 1, 3);
        doc.SetCellUrl("Regulatory References", 1, 3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0876");
        Assert.Equal(before, doc.GetCellValue("Regulatory References", 1, 3));
    }

    [Fact]
    public void SetCellUrl_Then_GetSheetCount_Unchanged()
    {
        var doc = CreateRegulatoryDoc();
        var before = doc.GetSheetCount();
        doc.SetCellUrl("Regulatory References", 1, 3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0876");
        Assert.Equal(before, doc.GetSheetCount());
    }

    [Fact]
    public void SetCellUrl_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRegulatoryDoc();
        doc.SetCellUrl("Regulatory References", 1, 3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0876");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellUrl_Override()
    {
        var doc = CreateRegulatoryDoc();
        doc.SetCellUrl("Regulatory References", 1, 3, "https://example.com/old");
        doc.SetCellUrl("Regulatory References", 1, 3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0876");
        Assert.NotNull(doc.GetCellUrl("Regulatory References", 1, 3));
    }

    [Fact]
    public void SetCellUrl_SaveLoad_Persists()
    {
        var doc = CreateRegulatoryDoc();
        doc.SetCellUrl("Regulatory References", 3, 3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R2088");
        var path = TempFile("scu_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetCellUrl("Regulatory References", 3, 3));
    }

    [Fact]
    public void SetCellUrl_MultipleCells()
    {
        var doc = CreateRegulatoryDoc();
        doc.SetCellUrl("Regulatory References", 1, 3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0876");
        doc.SetCellUrl("Regulatory References", 2, 3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554");
        doc.SetCellUrl("Regulatory References", 3, 3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R2088");
        Assert.NotNull(doc.GetCellUrl("Regulatory References", 1, 3));
        Assert.NotNull(doc.GetCellUrl("Regulatory References", 2, 3));
        Assert.NotNull(doc.GetCellUrl("Regulatory References", 3, 3));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCellUrl_SetCellUrl_SaveToFile_Pipeline()
    {
        // Legal — UK Law Commission: Law Reform Reference Workbook
        // Spreadsheet linking statutory provisions to Law Commission reports and consultations
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Law Reform References");
        doc.AddSheet("Case Law Links");

        // Law Reform References sheet
        doc.SetCellValue("Law Reform References", 0, 0, "Area");
        doc.SetCellValue("Law Reform References", 0, 1, "LC Report No.");
        doc.SetCellValue("Law Reform References", 0, 2, "Title");
        doc.SetCellValue("Law Reform References", 0, 3, "Status");
        doc.SetCellValue("Law Reform References", 0, 4, "Report Link");
        doc.SetCellValue("Law Reform References", 0, 5, "Legislation Link");

        string[,] reports = {
            { "Company Law", "LC400", "Automated Vehicles Act: Connected and Automated Vehicles", "Implemented", "Report", "Legislation" },
            { "Criminal Law", "LC398", "Modernising Communications Offences", "Implemented", "Report", "Legislation" },
            { "Land Law", "LC392", "Updating the Land Registration Act 2002", "Consultation", "Report", "" },
            { "Family Law", "LC382", "Weddings: Getting the Law Right", "Under Review", "Report", "" },
            { "Consumer Law", "LC378", "Consumer Sales Contracts: Transfer of Risk", "Implemented", "Report", "Legislation" }
        };
        for (int i = 0; i < reports.GetLength(0); i++)
            for (int j = 0; j < reports.GetLength(1); j++)
                doc.SetCellValue("Law Reform References", i + 1, j, reports[i, j]);

        // Set URLs for report links
        doc.SetCellUrl("Law Reform References", 1, 4, "https://www.lawcom.gov.uk/project/automated-vehicles/");
        doc.SetCellUrl("Law Reform References", 2, 4, "https://www.lawcom.gov.uk/project/modernising-communications-offences/");
        doc.SetCellUrl("Law Reform References", 3, 4, "https://www.lawcom.gov.uk/project/updating-the-land-registration-act-2002/");
        doc.SetCellUrl("Law Reform References", 4, 4, "https://www.lawcom.gov.uk/project/weddings/");
        doc.SetCellUrl("Law Reform References", 5, 4, "https://www.lawcom.gov.uk/project/consumer-sales-contracts-transfer-of-risk/");

        // Set URLs for legislation links (where implemented)
        doc.SetCellUrl("Law Reform References", 1, 5, "https://www.legislation.gov.uk/ukpga/2024/automated-vehicles");
        doc.SetCellUrl("Law Reform References", 2, 5, "https://www.legislation.gov.uk/ukpga/2023/communications");
        doc.SetCellUrl("Law Reform References", 5, 5, "https://www.legislation.gov.uk/consumer-sales-contracts");

        // Verify report links set
        for (int row = 1; row <= 5; row++)
            Assert.NotNull(doc.GetCellUrl("Law Reform References", row, 4));

        // Verify legislation links only where set
        Assert.NotNull(doc.GetCellUrl("Law Reform References", 1, 5));
        Assert.NotNull(doc.GetCellUrl("Law Reform References", 2, 5));
        Assert.Null(doc.GetCellUrl("Law Reform References", 3, 5)); // no legislation yet
        Assert.Null(doc.GetCellUrl("Law Reform References", 4, 5)); // no legislation yet
        Assert.NotNull(doc.GetCellUrl("Law Reform References", 5, 5));
        Assert.Null(doc.GetCellUrl("Law Reform References", 1, 0)); // non-URL cell

        // Case Law Links sheet
        doc.SetCellValue("Case Law Links", 0, 0, "Case Name");
        doc.SetCellValue("Case Law Links", 0, 1, "Citation");
        doc.SetCellValue("Case Law Links", 0, 2, "Court");
        doc.SetCellValue("Case Law Links", 0, 3, "BAILII Link");
        string[,] cases = {
            { "Uber BV v Aslam", "[2021] UKSC 5", "Supreme Court", "View" },
            { "R (Miller) v Prime Minister", "[2019] UKSC 41", "Supreme Court", "View" },
            { "Lloyds Banking Group Pensions Trustees v Lloyds Bank plc", "[2018] EWHC 2839", "High Court", "View" }
        };
        for (int i = 0; i < cases.GetLength(0); i++)
            for (int j = 0; j < cases.GetLength(1); j++)
                doc.SetCellValue("Case Law Links", i + 1, j, cases[i, j]);

        doc.SetCellUrl("Case Law Links", 1, 3, "https://www.bailii.org/uk/cases/UKSC/2021/5.html");
        doc.SetCellUrl("Case Law Links", 2, 3, "https://www.bailii.org/uk/cases/UKSC/2019/41.html");
        doc.SetCellUrl("Case Law Links", 3, 3, "https://www.bailii.org/ew/cases/EWHC/Ch/2018/2839.html");

        for (int row = 1; row <= 3; row++)
            Assert.NotNull(doc.GetCellUrl("Case Law Links", row, 3));

        Assert.Equal(2, doc.GetSheetCount());
        Assert.Equal("Report", doc.GetCellValue("Law Reform References", 1, 4));

        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        var path1 = TempFile("dogfood_law_reform_refs.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        var loaded = FodsDocument.LoadFile(path1);
        Assert.Equal(2, loaded.GetSheetCount());
        for (int row = 1; row <= 5; row++)
            Assert.NotNull(loaded.GetCellUrl("Law Reform References", row, 4));
        Assert.Null(loaded.GetCellUrl("Law Reform References", 3, 5));
        for (int row = 1; row <= 3; row++)
            Assert.NotNull(loaded.GetCellUrl("Case Law Links", row, 3));

        // Override a URL
        loaded.SetCellUrl("Law Reform References", 3, 5, "https://www.legislation.gov.uk/land-registration-update");
        Assert.NotNull(loaded.GetCellUrl("Law Reform References", 3, 5));

        // Add a new sheet with links
        loaded.AddSheet("EBA Guidelines");
        loaded.SetCellValue("EBA Guidelines", 0, 0, "Guideline");
        loaded.SetCellValue("EBA Guidelines", 0, 1, "Link");
        loaded.SetCellValue("EBA Guidelines", 1, 0, "EBA/GL/2021/05 — ICT Risk");
        loaded.SetCellValue("EBA Guidelines", 1, 1, "View");
        loaded.SetCellUrl("EBA Guidelines", 1, 1, "https://www.eba.europa.eu/eba-guidelines-ict-and-security-risk-management");
        Assert.NotNull(loaded.GetCellUrl("EBA Guidelines", 1, 1));

        var path2 = TempFile("dogfood_law_reform_refs_final.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodsDocument.LoadFile(path2);
        Assert.NotNull(final.GetCellUrl("Law Reform References", 3, 5));
        Assert.NotNull(final.GetCellUrl("EBA Guidelines", 1, 1));

        var ex1 = Record.Exception(() => final.ExportToHtml());
        var ex2 = Record.Exception(() => final.SetCellUrl("EBA Guidelines", 1, 1, "https://www.eba.europa.eu/updated-ict-guidelines"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
