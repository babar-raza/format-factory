// Tests for FodsDocument.GetCellHyperlink, SetCellHyperlink deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R417

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R417: Tests for FodsDocument.GetCellHyperlink, SetCellHyperlink deeper.
/// GetCellHyperlink(sheet, row, col): returns the hyperlink URL string for the cell, or null if none.
/// SetCellHyperlink(sheet, row, col, url): sets the hyperlink URL for the cell.
/// Covers: GetCellHyperlink null for new cell; GetCellHyperlink no-throw; SetCellHyperlink no-throw;
/// GetCellHyperlink non-null after Set; GetCellHyperlink consistent after Set; GetCellHyperlink save-load;
/// SetCellHyperlink overwrite; SetCellHyperlink multiple cells;
/// dogfood UK Parliament Select Committee evidence links model.
/// </summary>
public class FodsR417GetCellHyperlinkAndSetCellHyperlinkDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR417GetCellHyperlinkAndSetCellHyperlinkDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR417_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("Links");
        doc.SetCellValue("Links", 0, 0, "description");
        doc.SetCellValue("Links", 0, 1, "url");
        doc.SetCellValue("Links", 0, 2, "category");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellHyperlink
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellHyperlink_Null_ForNewCell()
    {
        var doc = CreateSampleDoc();
        Assert.Null(doc.GetCellHyperlink("Links", 1, 1));
    }

    [Fact]
    public void GetCellHyperlink_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.GetCellHyperlink("Links", 1, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellHyperlink_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.SetCellHyperlink("Links", 1, 1, "https://www.gov.uk"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellHyperlink_NonNull_AfterSet()
    {
        var doc = CreateSampleDoc();
        doc.SetCellHyperlink("Links", 1, 1, "https://www.gov.uk");
        Assert.NotNull(doc.GetCellHyperlink("Links", 1, 1));
    }

    [Fact]
    public void GetCellHyperlink_Consistent_AfterSet()
    {
        var doc = CreateSampleDoc();
        doc.SetCellHyperlink("Links", 1, 1, "https://www.parliament.uk");
        var v1 = doc.GetCellHyperlink("Links", 1, 1);
        var v2 = doc.GetCellHyperlink("Links", 1, 1);
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetCellHyperlink_SaveLoad_Consistent()
    {
        var doc = CreateSampleDoc();
        doc.SetCellHyperlink("Links", 1, 1, "https://www.legislation.gov.uk/ukpga/2023/55");
        var before = doc.GetCellHyperlink("Links", 1, 1);
        var path = TempFile("hl_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellHyperlink("Links", 1, 1));
    }

    [Fact]
    public void SetCellHyperlink_Overwrite()
    {
        var doc = CreateSampleDoc();
        doc.SetCellHyperlink("Links", 1, 1, "https://old.example.gov.uk");
        doc.SetCellHyperlink("Links", 1, 1, "https://www.gov.uk/guidance/updated");
        Assert.NotNull(doc.GetCellHyperlink("Links", 1, 1));
    }

    [Fact]
    public void SetCellHyperlink_MultipleCells()
    {
        var doc = CreateSampleDoc();
        doc.SetCellHyperlink("Links", 1, 0, "https://www.gov.uk/a");
        doc.SetCellHyperlink("Links", 1, 1, "https://www.gov.uk/b");
        doc.SetCellHyperlink("Links", 2, 1, "https://www.gov.uk/c");
        Assert.NotNull(doc.GetCellHyperlink("Links", 1, 0));
        Assert.NotNull(doc.GetCellHyperlink("Links", 1, 1));
        Assert.NotNull(doc.GetCellHyperlink("Links", 2, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCellHyperlink_SetCellHyperlink_Pipeline()
    {
        // Parliament — House of Commons Science and Technology Committee:
        // AI in the UK: Preparedness and Regulation Evidence Tracker
        // Hyperlinked evidence register for select committee inquiry management

        var doc = FodsDocument.CreateEmpty();

        // Sheet 1: Written evidence submissions
        doc.AddSheet("Written_Evidence");
        doc.SetCellValue("Written_Evidence", 0, 0, "ref");
        doc.SetCellValue("Written_Evidence", 0, 1, "submitter");
        doc.SetCellValue("Written_Evidence", 0, 2, "organisation_type");
        doc.SetCellValue("Written_Evidence", 0, 3, "date_received");
        doc.SetCellValue("Written_Evidence", 0, 4, "link");
        doc.SetCellValue("Written_Evidence", 0, 5, "key_themes");

        // No hyperlink on header
        Assert.Null(doc.GetCellHyperlink("Written_Evidence", 0, 4));

        string[] refs = { "AIP0001", "AIP0002", "AIP0003", "AIP0004", "AIP0005",
                           "AIP0006", "AIP0007", "AIP0008" };
        string[] submitters = { "Alan_Turing_Institute", "DeepMind", "Ada_Lovelace_Institute",
                                  "TechUK", "Royal_Society", "Imperial_College_London",
                                  "Centre_for_Data_Ethics", "Open_Rights_Group" };
        string[] orgTypes = { "Research_Institute", "Industry", "Civil_Society", "Trade_Body",
                               "Learned_Society", "University", "Advisory_Body", "Campaign_Group" };
        string[] urls = {
            "https://committees.parliament.uk/writtenevidence/AIP0001",
            "https://committees.parliament.uk/writtenevidence/AIP0002",
            "https://committees.parliament.uk/writtenevidence/AIP0003",
            "https://committees.parliament.uk/writtenevidence/AIP0004",
            "https://committees.parliament.uk/writtenevidence/AIP0005",
            "https://committees.parliament.uk/writtenevidence/AIP0006",
            "https://committees.parliament.uk/writtenevidence/AIP0007",
            "https://committees.parliament.uk/writtenevidence/AIP0008"
        };

        for (int i = 0; i < refs.Length; i++)
        {
            doc.SetCellValue("Written_Evidence", i + 1, 0, refs[i]);
            doc.SetCellValue("Written_Evidence", i + 1, 1, submitters[i]);
            doc.SetCellValue("Written_Evidence", i + 1, 2, orgTypes[i]);
            doc.SetCellValue("Written_Evidence", i + 1, 3, $"2024-0{i % 9 + 1:D1}-{(i * 3 + 10) % 28 + 1:D2}");
            doc.SetCellValue("Written_Evidence", i + 1, 4, urls[i]);
            doc.SetCellHyperlink("Written_Evidence", i + 1, 4, urls[i]);
        }

        var link1 = doc.GetCellHyperlink("Written_Evidence", 1, 4);
        Assert.NotNull(link1);
        Assert.Equal(link1, doc.GetCellHyperlink("Written_Evidence", 1, 4)); // consistent

        // Sheet 2: Oral evidence sessions
        doc.AddSheet("Oral_Evidence");
        doc.SetCellValue("Oral_Evidence", 0, 0, "session");
        doc.SetCellValue("Oral_Evidence", 0, 1, "witness");
        doc.SetCellValue("Oral_Evidence", 0, 2, "transcript_link");
        doc.SetCellValue("Oral_Evidence", 0, 3, "video_link");

        string[] sessions = { "Session_1", "Session_2", "Session_3" };
        string[] witnesses = { "Prof_Yoshua_Bengio", "Dame_Wendy_Hall", "Dr_Kate_Crawford" };
        string[] transcriptUrls = {
            "https://committees.parliament.uk/oralevidence/14721/html",
            "https://committees.parliament.uk/oralevidence/14722/html",
            "https://committees.parliament.uk/oralevidence/14723/html"
        };
        string[] videoUrls = {
            "https://www.parliamentlive.tv/Event/Index/14721",
            "https://www.parliamentlive.tv/Event/Index/14722",
            "https://www.parliamentlive.tv/Event/Index/14723"
        };

        for (int i = 0; i < 3; i++)
        {
            doc.SetCellValue("Oral_Evidence", i + 1, 0, sessions[i]);
            doc.SetCellValue("Oral_Evidence", i + 1, 1, witnesses[i]);
            doc.SetCellValue("Oral_Evidence", i + 1, 2, transcriptUrls[i]);
            doc.SetCellValue("Oral_Evidence", i + 1, 3, videoUrls[i]);
            doc.SetCellHyperlink("Oral_Evidence", i + 1, 2, transcriptUrls[i]);
            doc.SetCellHyperlink("Oral_Evidence", i + 1, 3, videoUrls[i]);
        }

        var transcriptLink = doc.GetCellHyperlink("Oral_Evidence", 1, 2);
        Assert.NotNull(transcriptLink);
        var videoLink = doc.GetCellHyperlink("Oral_Evidence", 1, 3);
        Assert.NotNull(videoLink);

        // Header cells have no hyperlinks
        Assert.Null(doc.GetCellHyperlink("Written_Evidence", 0, 4));
        Assert.Null(doc.GetCellHyperlink("Oral_Evidence", 0, 2));

        // Overwrite a hyperlink
        doc.SetCellHyperlink("Written_Evidence", 1, 4, "https://committees.parliament.uk/writtenevidence/AIP0001/updated");
        Assert.NotNull(doc.GetCellHyperlink("Written_Evidence", 1, 4));

        // SaveToFile
        var path = TempFile("parliament_stc_ai_evidence.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetCellHyperlink("Written_Evidence", 1, 4));
        Assert.NotNull(loaded.GetCellHyperlink("Written_Evidence", 2, 4));
        Assert.Equal(transcriptLink, loaded.GetCellHyperlink("Oral_Evidence", 1, 2));
        Assert.Equal(videoLink, loaded.GetCellHyperlink("Oral_Evidence", 1, 3));
        Assert.Null(loaded.GetCellHyperlink("Written_Evidence", 0, 4)); // header still null

        var ex1 = Record.Exception(() => loaded.GetCellHyperlink("Written_Evidence", 1, 4));
        var ex2 = Record.Exception(() => loaded.SetCellHyperlink("Written_Evidence", 9, 4, "https://www.gov.uk"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
