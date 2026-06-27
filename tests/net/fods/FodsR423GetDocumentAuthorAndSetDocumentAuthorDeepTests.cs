// Tests for FodsDocument.GetDocumentAuthor, SetDocumentAuthor deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R423

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R423: Tests for FodsDocument.GetDocumentAuthor, SetDocumentAuthor deeper.
/// GetDocumentAuthor(): returns the author metadata of the document.
/// SetDocumentAuthor(author): sets the author metadata field.
/// Covers: GetDocumentAuthor no-throw; GetDocumentAuthor non-null;
/// GetDocumentAuthor consistent; GetDocumentAuthor save-load;
/// SetDocumentAuthor no-throw; SetDocumentAuthor updates GetDocumentAuthor;
/// SetDocumentAuthor overwritable; SetDocumentAuthor save-load;
/// SetDocumentAuthor empty string accepted; dogfood pipeline.
/// </summary>
public class FodsR423GetDocumentAuthorAndSetDocumentAuthorDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR423GetDocumentAuthorAndSetDocumentAuthorDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR423_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateSampleDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, 0, "Name");
        doc.SetCellValue(0, 0, 1, "Value");
        doc.SetCellValue(0, 1, 0, "Alpha");
        doc.SetCellValue(0, 1, 1, "100");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetDocumentAuthor
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentAuthor_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.GetDocumentAuthor());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDocumentAuthor_NonNull()
    {
        var doc = CreateSampleDoc();
        Assert.NotNull(doc.GetDocumentAuthor());
    }

    [Fact]
    public void GetDocumentAuthor_Consistent()
    {
        var doc = CreateSampleDoc();
        Assert.Equal(doc.GetDocumentAuthor(), doc.GetDocumentAuthor());
    }

    [Fact]
    public void GetDocumentAuthor_SaveLoad_Consistent()
    {
        var doc = CreateSampleDoc();
        doc.SetDocumentAuthor("Test Author");
        var before = doc.GetDocumentAuthor();
        var path = TempFile("da_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDocumentAuthor());
    }

    // -------------------------------------------------------------------------
    // SetDocumentAuthor
    // -------------------------------------------------------------------------

    [Fact]
    public void SetDocumentAuthor_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.SetDocumentAuthor("Jane Smith"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetDocumentAuthor_UpdatesGetDocumentAuthor()
    {
        var doc = CreateSampleDoc();
        doc.SetDocumentAuthor("Dr. Emily Clarke");
        Assert.Equal("Dr. Emily Clarke", doc.GetDocumentAuthor());
    }

    [Fact]
    public void SetDocumentAuthor_Overwritable()
    {
        var doc = CreateSampleDoc();
        doc.SetDocumentAuthor("First Author");
        doc.SetDocumentAuthor("Second Author");
        Assert.Equal("Second Author", doc.GetDocumentAuthor());
    }

    [Fact]
    public void SetDocumentAuthor_SaveLoad_Consistent()
    {
        var doc = CreateSampleDoc();
        doc.SetDocumentAuthor("Analyst: OBR Research Team");
        var path = TempFile("da_set_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("Analyst: OBR Research Team", loaded.GetDocumentAuthor());
    }

    [Fact]
    public void SetDocumentAuthor_EmptyString_Accepted()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.SetDocumentAuthor(string.Empty));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDocumentAuthor_SetDocumentAuthor_Pipeline()
    {
        // Government — Cabinet Office / GDS: Government Digital Service Metrics Workbook
        // Departmental spreadsheet with author tracking for version control compliance
        // Author metadata supports audit trails for government transparency obligations

        var doc = FodsDocument.CreateEmpty();

        // Sheet 0: Service performance metrics
        doc.AddSheet("Service_Performance");
        doc.SetCellValue(0, 0, 0, "Service");
        doc.SetCellValue(0, 0, 1, "Monthly_Users");
        doc.SetCellValue(0, 0, 2, "Completion_Rate_Pct");
        doc.SetCellValue(0, 0, 3, "User_Satisfaction_Pct");
        doc.SetCellValue(0, 0, 4, "Error_Rate_Pct");

        string[] services = {
            "GOV.UK_Verify", "Renew_Driving_Licence", "Apply_Universal_Credit",
            "Register_to_Vote", "Self_Assessment_Tax_Return", "Passport_Renewal_Online",
            "Blue_Badge_Application", "Carer_Allowance_Claim"
        };
        double[] users = { 48000, 125000, 310000, 87000, 520000, 195000, 22000, 41000 };
        double[] completion = { 72.3, 88.1, 65.4, 94.2, 91.7, 85.6, 71.8, 68.3 };
        double[] satisfaction = { 68.0, 82.4, 59.1, 88.7, 79.3, 81.5, 70.2, 64.9 };
        double[] errorRate = { 3.2, 1.8, 5.7, 0.9, 2.1, 2.4, 4.3, 5.1 };

        for (int i = 0; i < services.Length; i++)
        {
            doc.SetCellValue(0, i + 1, 0, services[i]);
            doc.SetCellValue(0, i + 1, 1, users[i].ToString("F0"));
            doc.SetCellValue(0, i + 1, 2, completion[i].ToString("F1"));
            doc.SetCellValue(0, i + 1, 3, satisfaction[i].ToString("F1"));
            doc.SetCellValue(0, i + 1, 4, errorRate[i].ToString("F1"));
        }

        // Sheet 1: Departmental summary
        doc.AddSheet("Departmental_Summary");
        doc.SetCellValue(1, 0, 0, "Department");
        doc.SetCellValue(1, 0, 1, "Digital_Services");
        doc.SetCellValue(1, 0, 2, "Total_Transactions_M");
        string[] depts = { "HMRC", "DWP", "Home_Office", "DVLA", "Cabinet_Office" };
        int[] svcCounts = { 45, 38, 22, 17, 8 };
        double[] transactions = { 520.3, 412.7, 178.9, 234.1, 89.5 };
        for (int i = 0; i < depts.Length; i++)
        {
            doc.SetCellValue(1, i + 1, 0, depts[i]);
            doc.SetCellValue(1, i + 1, 1, svcCounts[i].ToString());
            doc.SetCellValue(1, i + 1, 2, transactions[i].ToString("F1"));
        }

        // Initial author not set — non-null
        var initialAuthor = doc.GetDocumentAuthor();
        Assert.NotNull(initialAuthor);
        Assert.Equal(initialAuthor, doc.GetDocumentAuthor()); // consistent

        // Set author to primary analyst
        doc.SetDocumentAuthor("GDS Analytics Team — Q3 2024 Review");
        Assert.Equal("GDS Analytics Team — Q3 2024 Review", doc.GetDocumentAuthor());

        // SaveToFile
        var path1 = TempFile("gds_metrics_draft.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify author preserved
        var loaded = FodsDocument.LoadFile(path1);
        Assert.Equal("GDS Analytics Team — Q3 2024 Review", loaded.GetDocumentAuthor());
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // Update author after peer review
        loaded.SetDocumentAuthor("GDS Analytics Team — Q3 2024 Final (Peer Reviewed: D. Marshall, Cabinet Office)");
        Assert.Equal(
            "GDS Analytics Team — Q3 2024 Final (Peer Reviewed: D. Marshall, Cabinet Office)",
            loaded.GetDocumentAuthor());

        // Overwrite again to final sign-off format
        loaded.SetDocumentAuthor("GDS/CO — Q3 2024 FINAL v1.3");
        Assert.Equal("GDS/CO — Q3 2024 FINAL v1.3", loaded.GetDocumentAuthor());

        var path2 = TempFile("gds_metrics_final.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodsDocument.LoadFile(path2);
        Assert.Equal("GDS/CO — Q3 2024 FINAL v1.3", final.GetDocumentAuthor());
        Assert.Equal(loaded.RowCount, final.RowCount);

        var ex1 = Record.Exception(() => final.GetDocumentAuthor());
        var ex2 = Record.Exception(() => final.SetDocumentAuthor("Archived"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
