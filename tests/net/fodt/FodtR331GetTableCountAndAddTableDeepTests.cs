// Tests for FodtDocument.GetTableCount, AddTable, GetTableCellValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R331

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R331: Tests for FodtDocument.GetTableCount, AddTable, GetTableCellValue deeper.
/// GetTableCount(): returns the number of tables in the document.
/// AddTable(paragraphIndex, rows, columns): inserts a table at the specified paragraph position.
/// GetTableCellValue(tableIndex, row, column): returns the text content of the specified table cell.
/// Covers: GetTableCount no-throw; GetTableCount non-negative; GetTableCount consistent;
/// GetTableCount zero for new doc; GetTableCount after AddTable increases; GetTableCount save-load;
/// AddTable no-throw; AddTable increases count; AddTable save-load;
/// AddTable multiple; AddTable then ExportToHtml no-throw;
/// AddTable then ExportToMarkdown no-throw; AddTable then GetWordCount positive;
/// GetTableCellValue no-throw; GetTableCellValue non-null; GetTableCellValue consistent;
/// GetTableCellValue save-load;
/// dogfood CreateDoc→AddTable→GetTableCount→GetTableCellValue→SaveToFile pipeline.
/// </summary>
public class FodtR331GetTableCountAndAddTableDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR331GetTableCountAndAddTableDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR331_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateResearchDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Climate Change Adaptation in UK Agriculture: Crop Yield Projections Under IPCC AR6 Scenarios", 1);
        doc.AppendParagraph("IPCC AR6 projects significant shifts in UK precipitation patterns and growing degree days under SSP2-4.5 and SSP5-8.5 scenarios through 2050.");
        doc.AppendParagraph("Crop yield modelling using DSSAT and APSIM frameworks integrates soil carbon sequestration models with regional climate downscaling outputs.");
        doc.InsertHeading(3, "Scenario Analysis", 2);
        doc.AppendParagraph("Under SSP2-4.5, winter wheat yields are projected to increase modestly in northern England (+3-8%) due to extended growing seasons, while drought stress reduces yields in East Anglia by 5-12%.");
        doc.AppendParagraph("Under SSP5-8.5, heat-related crop stress events exceeding critical thresholds above 34°C increase threefold by 2050 compared to the 1981-2010 baseline period.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCount_NoThrow()
    {
        var doc = CreateResearchDoc();
        var ex = Record.Exception(() => doc.GetTableCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCount_NonNegative()
    {
        var doc = CreateResearchDoc();
        Assert.True(doc.GetTableCount() >= 0);
    }

    [Fact]
    public void GetTableCount_Consistent()
    {
        var doc = CreateResearchDoc();
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with no tables.");
        Assert.Equal(0, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_AfterAddTable_Increases()
    {
        var doc = CreateResearchDoc();
        var before = doc.GetTableCount();
        doc.AddTable(1, 3, 4);
        Assert.Equal(before + 1, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_SaveLoad_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(2, 4, 3);
        var before = doc.GetTableCount();
        var path = TempFile("tc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    // -------------------------------------------------------------------------
    // AddTable
    // -------------------------------------------------------------------------

    [Fact]
    public void AddTable_NoThrow()
    {
        var doc = CreateResearchDoc();
        var ex = Record.Exception(() => doc.AddTable(0, 2, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_Increases_Count()
    {
        var doc = CreateResearchDoc();
        var before = doc.GetTableCount();
        doc.AddTable(3, 5, 4);
        Assert.Equal(before + 1, doc.GetTableCount());
    }

    [Fact]
    public void AddTable_SaveLoad_Persists()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(4, 3, 5);
        var before = doc.GetTableCount();
        var path = TempFile("at_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    [Fact]
    public void AddTable_Multiple()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(0, 2, 3);
        doc.AddTable(1, 3, 4);
        doc.AddTable(3, 4, 5);
        Assert.Equal(3, doc.GetTableCount());
    }

    [Fact]
    public void AddTable_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(2, 3, 3);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(1, 2, 4);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_Then_GetWordCount_Positive()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(0, 3, 3);
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetTableCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellValue_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(1, 3, 4);
        var ex = Record.Exception(() => doc.GetTableCellValue(0, 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCellValue_NonNull()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(2, 3, 4);
        Assert.NotNull(doc.GetTableCellValue(0, 0, 0));
    }

    [Fact]
    public void GetTableCellValue_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(0, 3, 4);
        Assert.Equal(doc.GetTableCellValue(0, 0, 0), doc.GetTableCellValue(0, 0, 0));
    }

    [Fact]
    public void GetTableCellValue_SaveLoad_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(3, 3, 4);
        var path = TempFile("tcv_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetTableCellValue(0, 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddTable_GetTableCount_GetTableCellValue_SaveToFile_Pipeline()
    {
        // Scientific report — pharmaceutical clinical trial results with data tables
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Phase III Randomised Controlled Trial: Novel GLP-1 Receptor Agonist in Type 2 Diabetes Mellitus", 1);
        doc.AppendParagraph("This multi-centre, double-blind, placebo-controlled Phase III trial enrolled 2,847 participants with established type 2 diabetes mellitus inadequately controlled on metformin monotherapy.");
        doc.AppendParagraph("Participants were randomised 2:1 to receive the investigational GLP-1 receptor agonist (2.4 mg once weekly subcutaneous injection) or placebo for 52 weeks.");

        doc.InsertHeading(3, "Baseline Characteristics", 2);
        doc.AppendParagraph("Baseline characteristics were well-balanced across treatment arms with mean HbA1c of 8.3% (SD 0.9), mean BMI of 31.4 kg/m² (SD 4.7), and median diabetes duration of 7.2 years.");
        doc.AppendParagraph("Prior cardiovascular events were present in 34.2% of participants, reflecting the high-risk nature of the enrolled population.");

        doc.InsertHeading(6, "Primary Endpoints", 2);
        doc.AppendParagraph("The primary composite endpoint of HbA1c reduction ≥1.5% from baseline and body weight reduction ≥5% at week 52 was achieved by 61.3% of treated participants versus 12.1% for placebo (OR 11.2, 95% CI 8.4-14.9, p<0.0001).");
        doc.AppendParagraph("Mean HbA1c reduction at week 52 was -1.8% (95% CI -1.9 to -1.7) in the treatment arm and -0.4% (95% CI -0.5 to -0.3) in placebo.");

        doc.InsertHeading(9, "Safety Summary", 1);
        doc.AppendParagraph("Adverse events of special interest included gastrointestinal events (nausea 28.3%, vomiting 11.7%) predominantly mild-to-moderate and transient, consistent with the GLP-1 agonist drug class profile.");
        doc.AppendParagraph("Serious adverse events occurred in 8.1% (treatment) vs 9.4% (placebo), with no significant difference in major adverse cardiovascular events (MACE).");

        Assert.Equal(12, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetTableCount());

        // AddTable 1 — Baseline Characteristics Summary Table (rows=5, cols=4)
        doc.AddTable(3, 5, 4); // after "Baseline Characteristics" section
        Assert.Equal(1, doc.GetTableCount());

        // AddTable 2 — Primary Endpoint Results (rows=4, cols=5)
        doc.AddTable(5, 4, 5); // after "Primary Endpoints" section paragraph 1
        Assert.Equal(2, doc.GetTableCount());

        // AddTable 3 — Safety Events by System Organ Class (rows=6, cols=4)
        doc.AddTable(7, 6, 4); // after "Safety Summary" section
        Assert.Equal(3, doc.GetTableCount());

        // Consistent
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());

        // GetTableCellValue
        var cell00 = doc.GetTableCellValue(0, 0, 0);
        Assert.NotNull(cell00);
        Assert.Equal(cell00, doc.GetTableCellValue(0, 0, 0)); // consistent

        var cell10 = doc.GetTableCellValue(1, 0, 0);
        Assert.NotNull(cell10);

        var cell20 = doc.GetTableCellValue(2, 0, 0);
        Assert.NotNull(cell20);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // GetWordCount positive
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_glp1_trial.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetTableCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetTableCellValue(0, 0, 0));
        Assert.NotNull(loaded.GetTableCellValue(2, 0, 0));

        // AddTable on loaded
        loaded.AddTable(8, 3, 3);
        Assert.Equal(4, loaded.GetTableCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: the investigational GLP-1 receptor agonist demonstrated statistically significant and clinically meaningful improvements in glycaemic control and body weight with an acceptable safety profile.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_glp1_trial_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetTableCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetTableCellValue(0, 0, 0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddTable(0, 2, 2));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
