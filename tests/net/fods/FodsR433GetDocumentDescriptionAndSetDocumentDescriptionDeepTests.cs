// Tests for FodsDocument.GetDocumentDescription, SetDocumentDescription deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R433

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R433: Tests for FodsDocument.GetDocumentDescription, SetDocumentDescription deeper.
/// GetDocumentDescription(): returns the document description from ODF metadata.
/// SetDocumentDescription(description): sets the description metadata on the document.
/// Covers: GetDocumentDescription no-throw; GetDocumentDescription non-null;
/// SetDocumentDescription no-throw; SetDocumentDescription updates value;
/// SetDocumentDescription overwritable; SetDocumentDescription save-load consistent;
/// GetDocumentDescription consistent; dogfood pipeline.
/// </summary>
public class FodsR433GetDocumentDescriptionAndSetDocumentDescriptionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR433GetDocumentDescriptionAndSetDocumentDescriptionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR433_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // GetDocumentDescription
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentDescription_NoThrow()
    {
        var doc = FodsDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetDocumentDescription());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDocumentDescription_NonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        Assert.NotNull(doc.GetDocumentDescription());
    }

    [Fact]
    public void GetDocumentDescription_Consistent()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentDescription("A test description.");
        Assert.Equal(doc.GetDocumentDescription(), doc.GetDocumentDescription());
    }

    // -------------------------------------------------------------------------
    // SetDocumentDescription
    // -------------------------------------------------------------------------

    [Fact]
    public void SetDocumentDescription_NoThrow()
    {
        var doc = FodsDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.SetDocumentDescription("Test description text."));
        Assert.Null(ex);
    }

    [Fact]
    public void SetDocumentDescription_UpdatesValue()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentDescription("Annual fiscal statistics workbook for departmental reporting.");
        Assert.Equal("Annual fiscal statistics workbook for departmental reporting.", doc.GetDocumentDescription());
    }

    [Fact]
    public void SetDocumentDescription_Overwritable()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentDescription("Initial description.");
        doc.SetDocumentDescription("Updated description with additional context — FINAL.");
        Assert.Equal("Updated description with additional context — FINAL.", doc.GetDocumentDescription());
    }

    [Fact]
    public void SetDocumentDescription_SaveLoad_Consistent()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentDescription("Cross-government public expenditure statistical analysis 2024.");
        var path = TempFile("desc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("Cross-government public expenditure statistical analysis 2024.", loaded.GetDocumentDescription());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDocumentDescription_SetDocumentDescription_Pipeline()
    {
        // Infrastructure — UKRI / Innovate UK: Catapult Network Performance Metrics 2024
        // Annual workbook tracking commercialisation, patent filings, and job creation across all Catapults
        // Document description provides discoverability metadata in UKRI's knowledge exchange repository

        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentTitle("Catapult Network Annual Performance Report 2024");
        doc.SetDocumentAuthor("Innovate UK — Knowledge Exchange and Commercialisation");
        doc.SetDocumentSubject("UK Catapult Network: Commercialisation, R&D and Economic Impact Metrics");
        doc.SetDocumentCategory("Innovation Metrics");
        doc.SetDocumentDescription(
            "Annual performance metrics for all nine UK Catapult centres including High Value Manufacturing, " +
            "Digital, Satellite Applications, Offshore Renewable Energy, Cell and Gene Therapy, Transport Systems, " +
            "Connected Places, Compound Semiconductor Applications, and Medicines Discovery. " +
            "Covers commercialisation, patent filings, job creation, and industry collaboration KPIs for 2023/24.");

        var desc0 = doc.GetDocumentDescription();
        Assert.NotNull(desc0);
        Assert.NotEmpty(desc0);
        Assert.Equal(desc0, doc.GetDocumentDescription()); // consistent

        // Sheet 1: Catapult KPIs
        doc.AddSheet("Catapult_KPIs");
        doc.SetCellValue("Catapult_KPIs", 0, 0, "Catapult_Name");
        doc.SetCellValue("Catapult_KPIs", 0, 1, "Establishment_Year");
        doc.SetCellValue("Catapult_KPIs", 0, 2, "Revenue_2024_GBPm");
        doc.SetCellValue("Catapult_KPIs", 0, 3, "Innovation_Projects");
        doc.SetCellValue("Catapult_KPIs", 0, 4, "Patent_Filings");
        doc.SetCellValue("Catapult_KPIs", 0, 5, "Jobs_Created");
        doc.SetCellValue("Catapult_KPIs", 0, 6, "SME_Collaborations");
        doc.SetCellValue("Catapult_KPIs", 0, 7, "Commercialisation_Revenue_GBPm");

        string[] catapults = {
            "High_Value_Manufacturing", "Digital", "Satellite_Applications",
            "Offshore_Renewable_Energy", "Cell_and_Gene_Therapy", "Transport_Systems",
            "Connected_Places", "Compound_Semiconductor_Applications", "Medicines_Discovery"
        };
        int[] estYears = { 2011, 2012, 2013, 2013, 2012, 2013, 2017, 2016, 2017 };
        double[] revenues = { 312.4, 198.7, 87.3, 143.8, 76.2, 94.5, 68.9, 52.4, 44.1 };
        int[] projects = { 487, 312, 198, 267, 143, 187, 124, 98, 76 };
        int[] patents = { 34, 28, 19, 22, 31, 16, 11, 24, 18 };
        int[] jobs = { 2340, 1780, 890, 1230, 640, 780, 520, 410, 340 };
        int[] smes = { 1240, 876, 432, 678, 312, 445, 287, 198, 167 };
        double[] commRevenue = { 89.4, 54.2, 31.8, 47.6, 28.3, 33.1, 22.7, 18.4, 14.2 };

        for (int i = 0; i < catapults.Length; i++)
        {
            doc.SetCellValue("Catapult_KPIs", i + 1, 0, catapults[i]);
            doc.SetCellValue("Catapult_KPIs", i + 1, 1, estYears[i].ToString());
            doc.SetCellValue("Catapult_KPIs", i + 1, 2, revenues[i].ToString("F1"));
            doc.SetCellValue("Catapult_KPIs", i + 1, 3, projects[i].ToString());
            doc.SetCellValue("Catapult_KPIs", i + 1, 4, patents[i].ToString());
            doc.SetCellValue("Catapult_KPIs", i + 1, 5, jobs[i].ToString());
            doc.SetCellValue("Catapult_KPIs", i + 1, 6, smes[i].ToString());
            doc.SetCellValue("Catapult_KPIs", i + 1, 7, commRevenue[i].ToString("F1"));
        }

        // Sheet 2: Trend data
        doc.AddSheet("Trend_2020_2024");
        doc.SetCellValue("Trend_2020_2024", 0, 0, "Year");
        doc.SetCellValue("Trend_2020_2024", 0, 1, "Total_Revenue_GBPm");
        doc.SetCellValue("Trend_2020_2024", 0, 2, "Total_Projects");
        doc.SetCellValue("Trend_2020_2024", 0, 3, "Total_Jobs");

        double[] trendRevenue = { 780.4, 812.3, 921.6, 1034.2, 1079.3 };
        int[] trendProjects = { 1234, 1398, 1567, 1789, 1892 };
        int[] trendJobs = { 4560, 5120, 6240, 7180, 7930 };
        for (int y = 0; y < 5; y++)
        {
            doc.SetCellValue("Trend_2020_2024", y + 1, 0, (2020 + y).ToString());
            doc.SetCellValue("Trend_2020_2024", y + 1, 1, trendRevenue[y].ToString("F1"));
            doc.SetCellValue("Trend_2020_2024", y + 1, 2, trendProjects[y].ToString());
            doc.SetCellValue("Trend_2020_2024", y + 1, 3, trendJobs[y].ToString());
        }

        // Update description to reflect full content
        doc.SetDocumentDescription(
            "Annual performance metrics for all nine UK Catapult centres 2023/24. " +
            "Includes KPIs (revenue, patents, jobs, SME collaborations), 5-year trend data (2020-2024), " +
            "and commercialisation revenue breakdown. Published under Innovate UK open data licence v3.0.");

        var desc1 = doc.GetDocumentDescription();
        Assert.NotNull(desc1);
        Assert.NotEqual(desc0, desc1); // updated
        Assert.Equal(desc1, doc.GetDocumentDescription()); // consistent

        // SaveToFile
        var path1 = TempFile("catapult_network_2024.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path1);
        Assert.Equal(desc1, loaded.GetDocumentDescription());
        Assert.Equal(doc.GetDocumentTitle(), loaded.GetDocumentTitle());
        Assert.Equal(doc.GetSheetCount(), loaded.GetSheetCount());

        // Further update
        loaded.SetDocumentDescription("Catapult Network Annual Performance 2024 — APPROVED FOR PUBLICATION");
        var desc2 = loaded.GetDocumentDescription();
        Assert.Equal("Catapult Network Annual Performance 2024 — APPROVED FOR PUBLICATION", desc2);

        var path2 = TempFile("catapult_network_2024_final.fods");
        loaded.SaveToFile(path2);
        var final = FodsDocument.LoadFile(path2);
        Assert.Equal(desc2, final.GetDocumentDescription());

        var ex1 = Record.Exception(() => final.GetDocumentDescription());
        var ex2 = Record.Exception(() => final.SetDocumentDescription("any value"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
