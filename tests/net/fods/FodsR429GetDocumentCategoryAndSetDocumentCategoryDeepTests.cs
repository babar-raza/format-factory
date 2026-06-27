// Tests for FodsDocument.GetDocumentCategory, SetDocumentCategory deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R429

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R429: Tests for FodsDocument.GetDocumentCategory, SetDocumentCategory deeper.
/// GetDocumentCategory(): returns the document category from ODF metadata.
/// SetDocumentCategory(category): sets the category metadata on the document.
/// Covers: GetDocumentCategory no-throw; GetDocumentCategory non-null;
/// SetDocumentCategory no-throw; SetDocumentCategory updates value;
/// SetDocumentCategory overwritable; SetDocumentCategory save-load consistent;
/// GetDocumentCategory consistent; dogfood pipeline.
/// </summary>
public class FodsR429GetDocumentCategoryAndSetDocumentCategoryDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR429GetDocumentCategoryAndSetDocumentCategoryDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR429_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // GetDocumentCategory
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentCategory_NoThrow()
    {
        var doc = FodsDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetDocumentCategory());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDocumentCategory_NonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        Assert.NotNull(doc.GetDocumentCategory());
    }

    [Fact]
    public void GetDocumentCategory_Consistent()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentCategory("Financial Statistics");
        Assert.Equal(doc.GetDocumentCategory(), doc.GetDocumentCategory());
    }

    // -------------------------------------------------------------------------
    // SetDocumentCategory
    // -------------------------------------------------------------------------

    [Fact]
    public void SetDocumentCategory_NoThrow()
    {
        var doc = FodsDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.SetDocumentCategory("Test Category"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetDocumentCategory_UpdatesValue()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentCategory("Regulatory Reporting");
        Assert.Equal("Regulatory Reporting", doc.GetDocumentCategory());
    }

    [Fact]
    public void SetDocumentCategory_Overwritable()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentCategory("Initial Category");
        doc.SetDocumentCategory("Updated Category — FINAL");
        Assert.Equal("Updated Category — FINAL", doc.GetDocumentCategory());
    }

    [Fact]
    public void SetDocumentCategory_SaveLoad_Consistent()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentCategory("Economic Statistics");
        var path = TempFile("cat_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("Economic Statistics", loaded.GetDocumentCategory());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDocumentCategory_SetDocumentCategory_Pipeline()
    {
        // Science — UKRI / EPSRC: Research Council Grant Portfolio Analysis 2024
        // Workbook categorising active research grants by discipline, institution, and programme
        // Document category supports classification in UKRI's Open Research Repository metadata schema

        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentTitle("EPSRC Active Grant Portfolio Analysis — Q3 2024");
        doc.SetDocumentAuthor("EPSRC Research Portfolio Analytics Team");
        doc.SetDocumentSubject("Engineering and Physical Sciences Research Grants 2024");
        doc.SetDocumentCategory("Research Council Statistics");
        doc.SetDocumentKeywords("EPSRC; UKRI; research grants; portfolio; physical sciences; engineering; 2024");

        var cat0 = doc.GetDocumentCategory();
        Assert.NotNull(cat0);
        Assert.Equal("Research Council Statistics", cat0);

        // Sheet 1: Grant portfolio overview by research area
        doc.AddSheet("Grant_Portfolio");
        doc.SetCellValue("Grant_Portfolio", 0, 0, "Research_Area");
        doc.SetCellValue("Grant_Portfolio", 0, 1, "Active_Grants");
        doc.SetCellValue("Grant_Portfolio", 0, 2, "Total_Value_GBPm");
        doc.SetCellValue("Grant_Portfolio", 0, 3, "Avg_Duration_Months");
        doc.SetCellValue("Grant_Portfolio", 0, 4, "New_Starts_2024");
        doc.SetCellValue("Grant_Portfolio", 0, 5, "Fellowship_Count");

        string[] researchAreas = {
            "Artificial_Intelligence", "Quantum_Technologies", "Advanced_Manufacturing",
            "Net_Zero_Energy", "Biological_Systems", "Mathematical_Sciences",
            "Materials_Research", "Digital_Health_Technology", "Cybersecurity",
            "Space_and_Autonomous_Systems"
        };
        int[] grants = { 412, 138, 267, 389, 201, 445, 312, 178, 156, 93 };
        double[] values = { 387.4, 245.8, 198.6, 412.3, 167.2, 312.7, 224.8, 189.6, 134.5, 112.3 };
        double[] durations = { 38.4, 42.1, 36.8, 41.2, 39.7, 44.3, 37.6, 40.1, 35.9, 43.8 };
        int[] newStarts = { 89, 31, 54, 78, 41, 92, 67, 38, 34, 19 };
        int[] fellowships = { 24, 12, 15, 22, 18, 31, 19, 14, 11, 8 };

        for (int i = 0; i < researchAreas.Length; i++)
        {
            doc.SetCellValue("Grant_Portfolio", i + 1, 0, researchAreas[i]);
            doc.SetCellValue("Grant_Portfolio", i + 1, 1, grants[i].ToString());
            doc.SetCellValue("Grant_Portfolio", i + 1, 2, values[i].ToString("F1"));
            doc.SetCellValue("Grant_Portfolio", i + 1, 3, durations[i].ToString("F1"));
            doc.SetCellValue("Grant_Portfolio", i + 1, 4, newStarts[i].ToString());
            doc.SetCellValue("Grant_Portfolio", i + 1, 5, fellowships[i].ToString());
        }

        // Sheet 2: Institution league table
        doc.AddSheet("Institution_Table");
        doc.SetCellValue("Institution_Table", 0, 0, "Institution");
        doc.SetCellValue("Institution_Table", 0, 1, "Russell_Group");
        doc.SetCellValue("Institution_Table", 0, 2, "Grant_Count");
        doc.SetCellValue("Institution_Table", 0, 3, "Total_Funding_GBPm");
        doc.SetCellValue("Institution_Table", 0, 4, "Success_Rate_Pct");

        string[] institutions = {
            "University_of_Cambridge", "Imperial_College_London", "University_of_Oxford",
            "University_College_London", "University_of_Manchester", "University_of_Edinburgh",
            "University_of_Bristol", "Durham_University", "University_of_Southampton",
            "University_of_Nottingham"
        };
        int[] grantCounts = { 312, 287, 298, 243, 201, 178, 156, 134, 143, 121 };
        double[] funding = { 289.4, 271.6, 281.3, 226.8, 187.3, 163.4, 144.7, 122.8, 131.2, 112.6 };
        double[] successRates = { 28.4, 26.7, 27.9, 24.3, 22.8, 21.4, 20.9, 19.8, 21.2, 18.7 };

        for (int i = 0; i < institutions.Length; i++)
        {
            doc.SetCellValue("Institution_Table", i + 1, 0, institutions[i]);
            doc.SetCellValue("Institution_Table", i + 1, 1, "Yes");
            doc.SetCellValue("Institution_Table", i + 1, 2, grantCounts[i].ToString());
            doc.SetCellValue("Institution_Table", i + 1, 3, funding[i].ToString("F1"));
            doc.SetCellValue("Institution_Table", i + 1, 4, successRates[i].ToString("F1"));
        }

        // Update category to reflect expanded content
        doc.SetDocumentCategory("Research Council Statistics — Portfolio Analysis");
        var cat1 = doc.GetDocumentCategory();
        Assert.Equal("Research Council Statistics — Portfolio Analysis", cat1);
        Assert.NotEqual(cat0, cat1);
        Assert.Equal(cat1, doc.GetDocumentCategory()); // consistent

        // Sheet count
        Assert.True(doc.GetSheetCount() >= 2);

        // SaveToFile
        var path1 = TempFile("epsrc_grant_portfolio_q3_2024.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path1);
        Assert.Equal(cat1, loaded.GetDocumentCategory());
        Assert.Equal(doc.GetDocumentTitle(), loaded.GetDocumentTitle());
        Assert.Equal(doc.GetDocumentKeywords(), loaded.GetDocumentKeywords());
        Assert.Equal(doc.GetSheetCount(), loaded.GetSheetCount());

        // Further update category
        loaded.SetDocumentCategory("Research Council Statistics — FINAL Q3 2024");
        var cat2 = loaded.GetDocumentCategory();
        Assert.Equal("Research Council Statistics — FINAL Q3 2024", cat2);

        var path2 = TempFile("epsrc_grant_portfolio_final.fods");
        loaded.SaveToFile(path2);
        var final = FodsDocument.LoadFile(path2);
        Assert.Equal(cat2, final.GetDocumentCategory());

        var ex1 = Record.Exception(() => final.GetDocumentCategory());
        var ex2 = Record.Exception(() => final.SetDocumentCategory("Any Value"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
