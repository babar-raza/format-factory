// Tests for FodtDocument.GetImageCount, AddImage, GetImageCaption deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R329

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R329: Tests for FodtDocument.GetImageCount, AddImage, GetImageCaption deeper.
/// GetImageCount(): returns the number of embedded images in the document.
/// AddImage(paragraphIndex, imagePath, caption): embeds an image in the document with an optional caption.
/// GetImageCaption(index): returns the caption text of the image at the given index.
/// Covers: GetImageCount no-throw; GetImageCount non-negative; GetImageCount consistent;
/// GetImageCount zero for new doc; GetImageCount after AddImage increases; GetImageCount save-load;
/// AddImage no-throw; AddImage increases count; AddImage save-load;
/// AddImage multiple; AddImage then ExportToHtml no-throw;
/// AddImage then ExportToMarkdown no-throw; AddImage then GetWordCount positive;
/// GetImageCaption no-throw; GetImageCaption non-null; GetImageCaption consistent;
/// GetImageCaption save-load;
/// dogfood CreateDoc→AddImage→GetImageCount→GetImageCaption→SaveToFile pipeline.
/// </summary>
public class FodtR329GetImageCountAndAddImageDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR329GetImageCountAndAddImageDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR329_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateTestPng()
    {
        // Create a minimal valid PNG (1×1 red pixel)
        var path = TempFile("test_image.png");
        // Minimal PNG bytes for 1×1 red pixel
        byte[] png = {
            0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A, // PNG signature
            0x00,0x00,0x00,0x0D, 0x49,0x48,0x44,0x52, // IHDR chunk
            0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,  // 1×1
            0x08,0x02,0x00,0x00,0x00,0x90,0x77,0x53,0xDE, // depth/color/etc + CRC
            0x00,0x00,0x00,0x0C, 0x49,0x44,0x41,0x54, // IDAT chunk
            0x08,0x99,0x01,0x01,0x00,0xFE,0xFF,0x00,0xFF,0x00,0x00,0x02,0x00,0x01,
            0xE2,0x21,0xBC,0x33, // CRC
            0x00,0x00,0x00,0x00, 0x49,0x45,0x4E,0x44, // IEND chunk
            0xAE,0x42,0x60,0x82  // CRC
        };
        File.WriteAllBytes(path, png);
        return path;
    }

    private static FodtDocument CreateTechReportDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Materials Science Report: Graphene-Based Nanocomposites for Aerospace Applications", 1);
        doc.AppendParagraph("Graphene-reinforced polymer matrix composites exhibit exceptional specific stiffness, electrical conductivity, and barrier properties suited to structural aerospace applications.");
        doc.AppendParagraph("Chemical vapour deposition of graphene on copper foil substrates produces large-area monolayer films with carrier mobilities exceeding 10,000 cm²/V·s.");
        doc.InsertHeading(3, "Characterisation Methods", 2);
        doc.AppendParagraph("Raman spectroscopy identifies graphene layer count and defect density through G-band, D-band, and 2D-band peak analysis with sub-micron spatial resolution.");
        doc.AppendParagraph("Transmission electron microscopy at atomic resolution reveals stacking order, edge termination chemistry, and grain boundary configurations in CVD-grown films.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetImageCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageCount_NoThrow()
    {
        var doc = CreateTechReportDoc();
        var ex = Record.Exception(() => doc.GetImageCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetImageCount_NonNegative()
    {
        var doc = CreateTechReportDoc();
        Assert.True(doc.GetImageCount() >= 0);
    }

    [Fact]
    public void GetImageCount_Consistent()
    {
        var doc = CreateTechReportDoc();
        Assert.Equal(doc.GetImageCount(), doc.GetImageCount());
    }

    [Fact]
    public void GetImageCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with no images.");
        Assert.Equal(0, doc.GetImageCount());
    }

    [Fact]
    public void GetImageCount_AfterAddImage_Increases()
    {
        var doc = CreateTechReportDoc();
        var imagePath = CreateTestPng();
        var before = doc.GetImageCount();
        doc.AddImage(1, imagePath, "Figure 1: Graphene CVD growth substrate");
        Assert.Equal(before + 1, doc.GetImageCount());
    }

    [Fact]
    public void GetImageCount_SaveLoad_Consistent()
    {
        var doc = CreateTechReportDoc();
        var imagePath = CreateTestPng();
        doc.AddImage(2, imagePath, "Figure 2: Raman spectrum analysis");
        var before = doc.GetImageCount();
        var path = TempFile("ic_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetImageCount());
    }

    // -------------------------------------------------------------------------
    // AddImage
    // -------------------------------------------------------------------------

    [Fact]
    public void AddImage_NoThrow()
    {
        var doc = CreateTechReportDoc();
        var imagePath = CreateTestPng();
        var ex = Record.Exception(() => doc.AddImage(0, imagePath, "Test image caption"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddImage_Increases_Count()
    {
        var doc = CreateTechReportDoc();
        var imagePath = CreateTestPng();
        var before = doc.GetImageCount();
        doc.AddImage(3, imagePath, "Figure 3: TEM atomic resolution image");
        Assert.Equal(before + 1, doc.GetImageCount());
    }

    [Fact]
    public void AddImage_SaveLoad_Persists()
    {
        var doc = CreateTechReportDoc();
        var imagePath = CreateTestPng();
        doc.AddImage(4, imagePath, "Figure 4: SEM cross-section");
        var before = doc.GetImageCount();
        var path = TempFile("ai_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetImageCount());
    }

    [Fact]
    public void AddImage_Multiple()
    {
        var doc = CreateTechReportDoc();
        var imagePath = CreateTestPng();
        doc.AddImage(0, imagePath, "Figure 1");
        doc.AddImage(1, imagePath, "Figure 2");
        doc.AddImage(3, imagePath, "Figure 3");
        Assert.Equal(3, doc.GetImageCount());
    }

    [Fact]
    public void AddImage_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateTechReportDoc();
        var imagePath = CreateTestPng();
        doc.AddImage(2, imagePath, "HTML export image test");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddImage_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateTechReportDoc();
        var imagePath = CreateTestPng();
        doc.AddImage(1, imagePath, "Markdown export image test");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddImage_Then_GetWordCount_Positive()
    {
        var doc = CreateTechReportDoc();
        var imagePath = CreateTestPng();
        doc.AddImage(0, imagePath, "Word count image test");
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetImageCaption
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageCaption_NoThrow()
    {
        var doc = CreateTechReportDoc();
        var imagePath = CreateTestPng();
        doc.AddImage(1, imagePath, "Caption retrieval test");
        var ex = Record.Exception(() => doc.GetImageCaption(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetImageCaption_NonNull()
    {
        var doc = CreateTechReportDoc();
        var imagePath = CreateTestPng();
        doc.AddImage(2, imagePath, "Non-null caption");
        Assert.NotNull(doc.GetImageCaption(0));
    }

    [Fact]
    public void GetImageCaption_Consistent()
    {
        var doc = CreateTechReportDoc();
        var imagePath = CreateTestPng();
        doc.AddImage(0, imagePath, "Consistency test caption");
        Assert.Equal(doc.GetImageCaption(0), doc.GetImageCaption(0));
    }

    [Fact]
    public void GetImageCaption_SaveLoad_Consistent()
    {
        var doc = CreateTechReportDoc();
        var imagePath = CreateTestPng();
        doc.AddImage(3, imagePath, "Save-load caption test");
        var path = TempFile("cap_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetImageCaption(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddImage_GetImageCount_GetImageCaption_SaveToFile_Pipeline()
    {
        // Scientific monograph — semiconductor fabrication process characterisation
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "CMOS Process Technology: 3nm Gate-All-Around Nanosheet Transistor Fabrication and Characterisation", 1);
        doc.AppendParagraph("Gate-all-around nanosheet transistors replace FinFET architecture at the 3nm process node, surrounding the channel on all four sides to improve electrostatic control and reduce short-channel effects.");
        doc.AppendParagraph("Epitaxial silicon-germanium (SiGe) sacrificial layers define nanosheet thickness and spacing, with release etch selectivity >50:1 against silicon channels.");

        doc.InsertHeading(3, "Process Flow", 2);
        doc.AppendParagraph("Deposition of alternating Si/SiGe superlattice layers by ultra-high vacuum CVD achieves sub-angstrom thickness control critical for performance uniformity across a 300mm wafer.");
        doc.AppendParagraph("Gate dielectric ALD of hafnium oxide with silicon nitride interlayer achieves equivalent oxide thickness of 0.7nm while maintaining leakage below 0.01 A/cm² at 1V.");

        doc.InsertHeading(6, "Electrical Characterisation", 2);
        doc.AppendParagraph("Transfer characteristic measurements show subthreshold slope of 64 mV/decade and drain-induced barrier lowering of 5 mV/V, demonstrating near-ideal electrostatic performance.");
        doc.AppendParagraph("Ring oscillator test structures at nominal voltage achieve stage delays of 3.2 ps, representing a 15% performance improvement over equivalent 5nm FinFET implementations.");

        doc.InsertHeading(9, "Reliability Assessment", 1);
        doc.AppendParagraph("Bias temperature instability (BTI) stress testing at 125°C demonstrates threshold voltage drift below 10mV after 10-year extrapolation, meeting JEDEC qualification criteria.");
        doc.AppendParagraph("Hot carrier injection reliability measurements using SPICE-level compact models confirm channel lifetime exceeding 20 years at nominal operating conditions.");

        Assert.Equal(12, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetImageCount());

        var imagePath = CreateTestPng();

        // AddImage — process characterisation figures
        doc.AddImage(1, imagePath, "Figure 1: GAA nanosheet transistor cross-section (TEM) — gate stack and channel layers visible");
        Assert.Equal(1, doc.GetImageCount());

        doc.AddImage(2, imagePath, "Figure 2: SiGe superlattice SIMS depth profile — alternating Si/SiGe layers at 5nm pitch");
        Assert.Equal(2, doc.GetImageCount());

        doc.AddImage(3, imagePath, "Figure 3: Post-release nanosheet stack — SEM showing released Si nanosheets after SiGe etch");
        Assert.Equal(3, doc.GetImageCount());

        doc.AddImage(5, imagePath, "Figure 4: Transfer characteristics (Id-Vg) — NMOS and PMOS devices at 0.75V VDD");
        Assert.Equal(4, doc.GetImageCount());

        doc.AddImage(6, imagePath, "Figure 5: Ring oscillator speed-power Pareto — comparison vs 5nm FinFET at matched leakage");
        Assert.Equal(5, doc.GetImageCount());

        doc.AddImage(7, imagePath, "Figure 6: BTI degradation projection — 10-year Vt shift under NBTI/PBTI combined stress");
        Assert.Equal(6, doc.GetImageCount());

        // Consistent
        Assert.Equal(doc.GetImageCount(), doc.GetImageCount());

        // GetImageCaption
        var cap0 = doc.GetImageCaption(0);
        Assert.NotNull(cap0);
        Assert.Equal(cap0, doc.GetImageCaption(0)); // consistent

        var cap3 = doc.GetImageCaption(3);
        Assert.NotNull(cap3);

        var cap5 = doc.GetImageCaption(5);
        Assert.NotNull(cap5);

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
        var path = TempFile("dogfood_gaa_nanosheet.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetImageCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetImageCaption(0));
        Assert.NotNull(loaded.GetImageCaption(5));

        // AddImage on loaded
        loaded.AddImage(8, imagePath, "Figure 7: HCI reliability — Vt shift vs stress time at multiple VDD levels");
        Assert.Equal(7, loaded.GetImageCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: GAA nanosheet technology delivers the electrostatic scaling required for 3nm and below, with demonstrated reliability meeting commercial qualification standards.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_gaa_nanosheet_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetImageCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetImageCaption(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddImage(0, imagePath, "Final figure"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
