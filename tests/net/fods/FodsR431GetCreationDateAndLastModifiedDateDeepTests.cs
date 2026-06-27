// Tests for FodsDocument.GetCreationDate, GetLastModifiedDate deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R431

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R431: Tests for FodsDocument.GetCreationDate, GetLastModifiedDate deeper.
/// GetCreationDate(): returns the document creation date from ODF metadata.
/// GetLastModifiedDate(): returns the last modification date from ODF metadata.
/// Covers: GetCreationDate no-throw; GetCreationDate non-null;
/// GetCreationDate consistent; GetCreationDate save-load;
/// GetLastModifiedDate no-throw; GetLastModifiedDate non-null;
/// GetLastModifiedDate consistent; GetLastModifiedDate save-load; dogfood pipeline.
/// </summary>
public class FodsR431GetCreationDateAndLastModifiedDateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR431GetCreationDateAndLastModifiedDateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR431_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // GetCreationDate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCreationDate_NoThrow()
    {
        var doc = FodsDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetCreationDate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCreationDate_NonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        Assert.NotNull(doc.GetCreationDate());
    }

    [Fact]
    public void GetCreationDate_Consistent()
    {
        var doc = FodsDocument.CreateEmpty();
        Assert.Equal(doc.GetCreationDate(), doc.GetCreationDate());
    }

    [Fact]
    public void GetCreationDate_SaveLoad_Consistent()
    {
        var doc = FodsDocument.CreateEmpty();
        var before = doc.GetCreationDate();
        var path = TempFile("cd_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCreationDate());
    }

    // -------------------------------------------------------------------------
    // GetLastModifiedDate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLastModifiedDate_NoThrow()
    {
        var doc = FodsDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetLastModifiedDate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLastModifiedDate_NonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        Assert.NotNull(doc.GetLastModifiedDate());
    }

    [Fact]
    public void GetLastModifiedDate_Consistent()
    {
        var doc = FodsDocument.CreateEmpty();
        Assert.Equal(doc.GetLastModifiedDate(), doc.GetLastModifiedDate());
    }

    [Fact]
    public void GetLastModifiedDate_SaveLoad_Consistent()
    {
        var doc = FodsDocument.CreateEmpty();
        var before = doc.GetLastModifiedDate();
        var path = TempFile("lm_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetLastModifiedDate());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCreationDate_GetLastModifiedDate_Pipeline()
    {
        // Audit — NAO / Cabinet Office: Cross-Government Spending Review Data Collection 2024
        // Multi-sheet workbook tracking departmental spending submissions for SR2025
        // Creation and modification dates are mandatory audit trail fields under Government Accounting rules

        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentTitle("Cross-Government Spending Review 2025 — Data Collection Template");
        doc.SetDocumentAuthor("HM Treasury Spending Team");
        doc.SetDocumentSubject("SR2025 Departmental Spending Data — Official Use Only");
        doc.SetDocumentCategory("Spending Review Data Collection");

        var cd0 = doc.GetCreationDate();
        var lm0 = doc.GetLastModifiedDate();
        Assert.NotNull(cd0);
        Assert.NotNull(lm0);

        // Sheet 1: Departmental RDEL allocations
        doc.AddSheet("RDEL_Allocations");
        doc.SetCellValue("RDEL_Allocations", 0, 0, "Department");
        doc.SetCellValue("RDEL_Allocations", 0, 1, "RDEL_2024_25_GBPm");
        doc.SetCellValue("RDEL_Allocations", 0, 2, "RDEL_2025_26_Bid_GBPm");
        doc.SetCellValue("RDEL_Allocations", 0, 3, "RDEL_2026_27_Bid_GBPm");
        doc.SetCellValue("RDEL_Allocations", 0, 4, "Submission_Status");

        string[] departments = {
            "DHSC", "DfE", "MoD", "DWP", "Home_Office",
            "MoJ", "FCDO", "DESNZ", "DBT", "DLUHC",
            "DCMS", "HO_Borders", "DEFRA", "DfT", "CO"
        };
        int[] rdel24 = { 181200, 73800, 54100, 121300, 19800,
                          10200, 3100, 4700, 3200, 2800,
                          2100, 4100, 3600, 7200, 4300 };

        for (int i = 0; i < departments.Length; i++)
        {
            double bid25 = rdel24[i] * (1.02 + new Random(i).NextDouble() * 0.05);
            double bid26 = bid25 * (1.01 + new Random(i + 100).NextDouble() * 0.04);
            doc.SetCellValue("RDEL_Allocations", i + 1, 0, departments[i]);
            doc.SetCellValue("RDEL_Allocations", i + 1, 1, rdel24[i].ToString());
            doc.SetCellValue("RDEL_Allocations", i + 1, 2, bid25.ToString("F0"));
            doc.SetCellValue("RDEL_Allocations", i + 1, 3, bid26.ToString("F0"));
            doc.SetCellValue("RDEL_Allocations", i + 1, 4, "Submitted");
        }

        // Sheet 2: Capital allocations (CDEL)
        doc.AddSheet("CDEL_Allocations");
        doc.SetCellValue("CDEL_Allocations", 0, 0, "Department");
        doc.SetCellValue("CDEL_Allocations", 0, 1, "CDEL_2024_25_GBPm");
        doc.SetCellValue("CDEL_Allocations", 0, 2, "CDEL_2025_26_Bid_GBPm");
        doc.SetCellValue("CDEL_Allocations", 0, 3, "Infrastructure_Category");

        int[] cdel24 = { 12400, 8700, 12100, 1200, 1600,
                          900, 600, 8100, 2300, 14200,
                          1700, 2100, 1300, 9100, 900 };
        string[] infraCats = {
            "NHS_Buildings", "School_Rebuilding", "Defence_Estate", "Digital_Benefits", "Border_Infrastructure",
            "Prison_Programme", "Overseas_Missions", "Net_Zero_Infrastructure", "Freeports", "Housing_Delivery",
            "Culture_and_Sport", "Security_Infrastructure", "Flood_Defence", "Integrated_Rail", "Gov_Digital"
        };

        for (int i = 0; i < departments.Length; i++)
        {
            double bid25 = cdel24[i] * (1.05 + new Random(i + 200).NextDouble() * 0.1);
            doc.SetCellValue("CDEL_Allocations", i + 1, 0, departments[i]);
            doc.SetCellValue("CDEL_Allocations", i + 1, 1, cdel24[i].ToString());
            doc.SetCellValue("CDEL_Allocations", i + 1, 2, bid25.ToString("F0"));
            doc.SetCellValue("CDEL_Allocations", i + 1, 3, infraCats[i]);
        }

        // Verify dates are consistent after data entry
        var cd1 = doc.GetCreationDate();
        var lm1 = doc.GetLastModifiedDate();
        Assert.NotNull(cd1);
        Assert.NotNull(lm1);
        Assert.Equal(cd1, doc.GetCreationDate()); // consistent
        Assert.Equal(lm1, doc.GetLastModifiedDate()); // consistent

        // Sheet count
        Assert.True(doc.GetSheetCount() >= 2);

        // SaveToFile
        var path1 = TempFile("sr2025_data_collection_template.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path1);
        Assert.Equal(cd1, loaded.GetCreationDate());
        Assert.Equal(lm1, loaded.GetLastModifiedDate());
        Assert.Equal(doc.GetDocumentTitle(), loaded.GetDocumentTitle());
        Assert.Equal(doc.GetSheetCount(), loaded.GetSheetCount());

        // Further save
        var path2 = TempFile("sr2025_data_collection_v2.fods");
        loaded.SaveToFile(path2);
        var final = FodsDocument.LoadFile(path2);
        Assert.NotNull(final.GetCreationDate());
        Assert.NotNull(final.GetLastModifiedDate());

        var ex1 = Record.Exception(() => final.GetCreationDate());
        var ex2 = Record.Exception(() => final.GetLastModifiedDate());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
