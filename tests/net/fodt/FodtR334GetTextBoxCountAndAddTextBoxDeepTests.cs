// Tests for FodtDocument.GetTextBoxCount, AddTextBox, GetTextBoxContent deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R334

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R334: Tests for FodtDocument.GetTextBoxCount, AddTextBox, GetTextBoxContent deeper.
/// GetTextBoxCount(): returns the number of text boxes (draw:text-box frames) in the document.
/// AddTextBox(paragraphIndex, content, width, height): inserts a text box at the given paragraph.
/// GetTextBoxContent(index): returns the text content of the text box at the given index.
/// Covers: GetTextBoxCount no-throw; GetTextBoxCount non-negative; GetTextBoxCount consistent;
/// GetTextBoxCount zero for new doc; GetTextBoxCount after AddTextBox increases; GetTextBoxCount save-load;
/// AddTextBox no-throw; AddTextBox increases count; AddTextBox save-load;
/// AddTextBox multiple; AddTextBox then ExportToHtml no-throw;
/// AddTextBox then ExportToMarkdown no-throw; AddTextBox then GetWordCount positive;
/// GetTextBoxContent no-throw; GetTextBoxContent non-null; GetTextBoxContent consistent;
/// GetTextBoxContent save-load;
/// dogfood CreateDoc→AddTextBox→GetTextBoxCount→GetTextBoxContent→SaveToFile pipeline.
/// </summary>
public class FodtR334GetTextBoxCountAndAddTextBoxDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR334GetTextBoxCountAndAddTextBoxDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR334_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateEngineeringDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Offshore Wind Turbine Foundation Design: Monopile Fatigue Assessment for North Sea Conditions", 1);
        doc.AppendParagraph("Monopile foundations for offshore wind turbines in the North Sea must withstand combined loading from wind thrust, wave forces, current drag, and soil-pile interaction across a design life exceeding 25 years.");
        doc.AppendParagraph("Fatigue analysis follows DNV-ST-0126 and IEC 61400-3-1 standards, incorporating site-specific metocean data from ERA5 reanalysis combined with long-term hindcast databases covering 30-year return periods.");
        doc.InsertHeading(3, "Load Cases and DLC Analysis", 2);
        doc.AppendParagraph("Design Load Cases (DLC) defined in IEC 61400-3 specify operational, start-up, emergency stop, fault, and parked conditions requiring probabilistic combination with environmental loading spectra.");
        doc.AppendParagraph("Damage Equivalent Load (DEL) calculations aggregate cycle counts from aeroelastic simulations across wind speed bins, applying Miner's rule with S-N curve data for welded steel connections.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetTextBoxCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBoxCount_NoThrow()
    {
        var doc = CreateEngineeringDoc();
        var ex = Record.Exception(() => doc.GetTextBoxCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTextBoxCount_NonNegative()
    {
        var doc = CreateEngineeringDoc();
        Assert.True(doc.GetTextBoxCount() >= 0);
    }

    [Fact]
    public void GetTextBoxCount_Consistent()
    {
        var doc = CreateEngineeringDoc();
        Assert.Equal(doc.GetTextBoxCount(), doc.GetTextBoxCount());
    }

    [Fact]
    public void GetTextBoxCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with no text boxes.");
        Assert.Equal(0, doc.GetTextBoxCount());
    }

    [Fact]
    public void GetTextBoxCount_AfterAddTextBox_Increases()
    {
        var doc = CreateEngineeringDoc();
        var before = doc.GetTextBoxCount();
        doc.AddTextBox(1, "NOTE: Pile diameter typically 8-10m for modern 12-15 MW turbines.", 10.0, 3.0);
        Assert.Equal(before + 1, doc.GetTextBoxCount());
    }

    [Fact]
    public void GetTextBoxCount_SaveLoad_Consistent()
    {
        var doc = CreateEngineeringDoc();
        doc.AddTextBox(2, "CAUTION: Wave breaking loads require specialist assessment per DNVGL-RP-C205.", 12.0, 3.0);
        var before = doc.GetTextBoxCount();
        var path = TempFile("tbc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTextBoxCount());
    }

    // -------------------------------------------------------------------------
    // AddTextBox
    // -------------------------------------------------------------------------

    [Fact]
    public void AddTextBox_NoThrow()
    {
        var doc = CreateEngineeringDoc();
        var ex = Record.Exception(() => doc.AddTextBox(0, "Key parameter: Hs=7.5m, Tp=12.5s design wave.", 10.0, 2.5));
        Assert.Null(ex);
    }

    [Fact]
    public void AddTextBox_Increases_Count()
    {
        var doc = CreateEngineeringDoc();
        var before = doc.GetTextBoxCount();
        doc.AddTextBox(3, "DLC 1.2: Normal production — fatigue loading (most cycles).", 10.0, 2.5);
        Assert.Equal(before + 1, doc.GetTextBoxCount());
    }

    [Fact]
    public void AddTextBox_SaveLoad_Persists()
    {
        var doc = CreateEngineeringDoc();
        doc.AddTextBox(4, "S-N curve FAT90 per IEC 61400-3 Annex A for circumferential welds.", 12.0, 3.0);
        var before = doc.GetTextBoxCount();
        var path = TempFile("atb_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTextBoxCount());
    }

    [Fact]
    public void AddTextBox_Multiple()
    {
        var doc = CreateEngineeringDoc();
        doc.AddTextBox(0, "Text box 1: Site coordinates 56.5°N, 2.1°E.", 10.0, 2.5);
        doc.AddTextBox(1, "Text box 2: Water depth 28m LAT.", 10.0, 2.5);
        doc.AddTextBox(3, "Text box 3: Soil profile: dense sand, φ=38°.", 10.0, 2.5);
        Assert.Equal(3, doc.GetTextBoxCount());
    }

    [Fact]
    public void AddTextBox_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateEngineeringDoc();
        doc.AddTextBox(2, "HTML export text box — mudline moment resisted by p-y springs.", 10.0, 2.5);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddTextBox_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateEngineeringDoc();
        doc.AddTextBox(1, "Markdown export text box — scour protection layer required within 1D pile diameter.", 10.0, 2.5);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddTextBox_Then_GetWordCount_Positive()
    {
        var doc = CreateEngineeringDoc();
        doc.AddTextBox(0, "Word count text box — fatigue damage sum D < 1.0 over design life.", 10.0, 2.5);
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetTextBoxContent
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBoxContent_NoThrow()
    {
        var doc = CreateEngineeringDoc();
        doc.AddTextBox(1, "Content retrieval text box — DFF = 3.0 for primary structural connections.", 10.0, 2.5);
        var ex = Record.Exception(() => doc.GetTextBoxContent(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTextBoxContent_NonNull()
    {
        var doc = CreateEngineeringDoc();
        doc.AddTextBox(2, "Non-null text box — Uy_max < D/750 serviceability limit (DNV).", 10.0, 2.5);
        Assert.NotNull(doc.GetTextBoxContent(0));
    }

    [Fact]
    public void GetTextBoxContent_Consistent()
    {
        var doc = CreateEngineeringDoc();
        doc.AddTextBox(0, "Consistent text box — eigenfrequency must avoid 1P/3P excitation bands.", 10.0, 2.5);
        Assert.Equal(doc.GetTextBoxContent(0), doc.GetTextBoxContent(0));
    }

    [Fact]
    public void GetTextBoxContent_SaveLoad_Consistent()
    {
        var doc = CreateEngineeringDoc();
        doc.AddTextBox(3, "Save-load text box — grouted connection design per DNVGL-ST-0126 §9.", 10.0, 2.5);
        var path = TempFile("tbc_sl_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetTextBoxContent(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddTextBox_GetTextBoxCount_GetTextBoxContent_SaveToFile_Pipeline()
    {
        // Structural engineering report — bridge assessment with callout text boxes
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Structural Assessment: Grade II Listed Railway Viaduct — Inspection and Remaining Fatigue Life Evaluation", 1);
        doc.AppendParagraph("This assessment evaluates the structural condition and remaining fatigue life of a 19-span wrought iron viaduct constructed between 1866 and 1869, carrying a single-track railway over a river valley in northern England.");
        doc.AppendParagraph("Inspection findings are classified according to Network Rail's Structures Condition Index (SCI) methodology, with fatigue assessments following BS EN 1993-1-9 and the historic railway structure guidance in NR/SP/CIV/017.");

        doc.InsertHeading(3, "Inspection Findings", 2);
        doc.AppendParagraph("Visual inspection of all 19 spans completed in March 2024 identified significant pack rust accumulation on the bottom flanges of bowstring girders in spans 7-11, with measured section loss up to 18% in the worst-affected locations.");
        doc.AppendParagraph("Ultrasonic thickness gauging of 480 measurement points confirmed section losses consistent with visual assessment, with 34 locations exceeding the 15% threshold requiring structural intervention.");

        doc.InsertHeading(6, "Fatigue Assessment", 2);
        doc.AppendParagraph("Traffic spectrum analysis using SCATS axle weight data from adjacent weighbridge stations over 10 years provides the basis for equivalent stress range calculation at critical weld details.");
        doc.AppendParagraph("Detail category C90 governs at the rivet holes of the main longitudinal girder bottom flange splice plates, where stress concentration factors from FE modelling indicate significant fatigue damage accumulation.");

        doc.InsertHeading(9, "Intervention Recommendations", 1);
        doc.AppendParagraph("Immediate access restrictions to Class 6 axle loading apply to spans 7-11 pending steelwork remediation, with reblasting and metal spray zinc coating specified for the affected bottom flange sections.");
        doc.AppendParagraph("Post-remediation fatigue life assessment projects a remaining safe service life of 22 years at current traffic loading, subject to five-yearly re-inspection and monitoring of crack initiation at identified high-damage locations.");

        Assert.Equal(12, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetTextBoxCount());

        // AddTextBox — callout boxes for critical data
        doc.AddTextBox(1, "CRITICAL: SCI Rating — Span 9: SCI-4 (Serious Defect). Immediate action required.", 14.0, 3.0);
        Assert.Equal(1, doc.GetTextBoxCount());

        doc.AddTextBox(3, "KEY FINDING: Maximum section loss 18.3% at Span 9 Bottom Flange Node 9B-47 (see Drawing C-1247-A).", 14.0, 3.5);
        Assert.Equal(2, doc.GetTextBoxCount());

        doc.AddTextBox(5, "TRAFFIC DATA: Annual tonnage 8.2M tonnes (2019-2024 average). Proportion HGV axles: 67%.", 14.0, 3.0);
        Assert.Equal(3, doc.GetTextBoxCount());

        doc.AddTextBox(6, "FATIGUE LIFE: Remaining life at current loading = 22 years (2024-2046). Confidence interval: ±4 years at 95%.", 14.0, 3.0);
        Assert.Equal(4, doc.GetTextBoxCount());

        doc.AddTextBox(8, "IMMEDIATE ACTION: Access restriction to Class 6 loading effective from date of issue. Network Rail Form NR1992 submitted.", 14.0, 3.5);
        Assert.Equal(5, doc.GetTextBoxCount());

        doc.AddTextBox(9, "MONITORING: Install 6 strain gauges at Span 9 critical section. Review data quarterly.", 12.0, 2.5);
        Assert.Equal(6, doc.GetTextBoxCount());

        // Consistent
        Assert.Equal(doc.GetTextBoxCount(), doc.GetTextBoxCount());

        // GetTextBoxContent
        var content0 = doc.GetTextBoxContent(0);
        Assert.NotNull(content0);
        Assert.Equal(content0, doc.GetTextBoxContent(0)); // consistent

        var content3 = doc.GetTextBoxContent(3);
        Assert.NotNull(content3);

        var content5 = doc.GetTextBoxContent(5);
        Assert.NotNull(content5);

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
        var path = TempFile("dogfood_viaduct_assessment.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetTextBoxCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetTextBoxContent(0));
        Assert.NotNull(loaded.GetTextBoxContent(5));

        // AddTextBox on loaded
        loaded.AddTextBox(0, "REVISION: v1.1 — Revised section loss figures following calibration check on UTG instrument.", 14.0, 2.5);
        Assert.Equal(7, loaded.GetTextBoxCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: the viaduct remains serviceable at restricted loading pending remediation of spans 7-11, with the intervention programme estimated for completion within 18 months subject to procurement and access scheduling.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_viaduct_assessment_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetTextBoxCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetTextBoxContent(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddTextBox(0, "Final text box.", 10.0, 2.5));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
