// Tests for FodtDocument.GetFootnoteCount, AddFootnote, GetFootnoteText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R332

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R332: Tests for FodtDocument.GetFootnoteCount, AddFootnote, GetFootnoteText deeper.
/// GetFootnoteCount(): returns the number of footnotes in the document.
/// AddFootnote(paragraphIndex, text): adds a footnote anchored to the specified paragraph.
/// GetFootnoteText(index): returns the text of the footnote at the given index.
/// Covers: GetFootnoteCount no-throw; GetFootnoteCount non-negative; GetFootnoteCount consistent;
/// GetFootnoteCount zero for new doc; GetFootnoteCount after AddFootnote increases;
/// GetFootnoteCount save-load;
/// AddFootnote no-throw; AddFootnote increases count; AddFootnote save-load;
/// AddFootnote multiple; AddFootnote then ExportToHtml no-throw;
/// AddFootnote then ExportToMarkdown no-throw; AddFootnote then GetWordCount positive;
/// GetFootnoteText no-throw; GetFootnoteText non-null; GetFootnoteText consistent;
/// GetFootnoteText save-load;
/// dogfood CreateDoc→AddFootnote→GetFootnoteCount→GetFootnoteText→SaveToFile pipeline.
/// </summary>
public class FodtR332GetFootnoteCountAndAddFootnoteDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR332GetFootnoteCountAndAddFootnoteDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR332_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateAcademicPaperDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Quantum Chromodynamics in Heavy-Ion Collisions: Quark-Gluon Plasma Formation at CERN LHC", 1);
        doc.AppendParagraph("Relativistic heavy-ion collisions at the Large Hadron Collider produce conditions sufficient to deconfine quarks and gluons from hadronic matter, forming a transient state of quark-gluon plasma (QGP).");
        doc.AppendParagraph("The ALICE experiment at LHC is dedicated to characterising QGP properties through measurements of collective flow, jet quenching, and quarkonium suppression in Pb-Pb collisions at √s_NN = 5.02 TeV.");
        doc.InsertHeading(3, "Experimental Methods", 2);
        doc.AppendParagraph("Time Projection Chamber (TPC) tracking combined with EMCAL electromagnetic calorimetry provides particle identification across a broad transverse momentum range from 0.1 to 100 GeV/c.");
        doc.AppendParagraph("Centrality classification uses the measured V0 amplitude distributions at forward pseudorapidity to select the 0-5%, 5-10%, and 10-30% most central Pb-Pb collision events.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetFootnoteCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFootnoteCount_NoThrow()
    {
        var doc = CreateAcademicPaperDoc();
        var ex = Record.Exception(() => doc.GetFootnoteCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFootnoteCount_NonNegative()
    {
        var doc = CreateAcademicPaperDoc();
        Assert.True(doc.GetFootnoteCount() >= 0);
    }

    [Fact]
    public void GetFootnoteCount_Consistent()
    {
        var doc = CreateAcademicPaperDoc();
        Assert.Equal(doc.GetFootnoteCount(), doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with no footnotes.");
        Assert.Equal(0, doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_AfterAddFootnote_Increases()
    {
        var doc = CreateAcademicPaperDoc();
        var before = doc.GetFootnoteCount();
        doc.AddFootnote(1, "QGP was first predicted by Cabibbo and Parisi in 1975 based on asymptotic freedom.");
        Assert.Equal(before + 1, doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_SaveLoad_Consistent()
    {
        var doc = CreateAcademicPaperDoc();
        doc.AddFootnote(2, "ALICE: A Large Ion Collider Experiment — see ALICE Collaboration, JINST 3 (2008) S08002.");
        var before = doc.GetFootnoteCount();
        var path = TempFile("fnc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFootnoteCount());
    }

    // -------------------------------------------------------------------------
    // AddFootnote
    // -------------------------------------------------------------------------

    [Fact]
    public void AddFootnote_NoThrow()
    {
        var doc = CreateAcademicPaperDoc();
        var ex = Record.Exception(() => doc.AddFootnote(0, "LHC: Large Hadron Collider at CERN, Geneva."));
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Increases_Count()
    {
        var doc = CreateAcademicPaperDoc();
        var before = doc.GetFootnoteCount();
        doc.AddFootnote(3, "TPC: Time Projection Chamber — central tracking detector of ALICE.");
        Assert.Equal(before + 1, doc.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_SaveLoad_Persists()
    {
        var doc = CreateAcademicPaperDoc();
        doc.AddFootnote(4, "V0: forward/backward scintillator arrays used for minimum-bias triggering and centrality.");
        var before = doc.GetFootnoteCount();
        var path = TempFile("af_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_Multiple()
    {
        var doc = CreateAcademicPaperDoc();
        doc.AddFootnote(0, "Note 1: QGP properties reviewed in Blaizot & Zinn-Justin (eds.), Les Houches Lecture Notes.");
        doc.AddFootnote(1, "Note 2: Jet quenching energy loss: ΔE ~ αs L² (Baier-Dokshitzer-Mueller-Peigne-Schiff model).");
        doc.AddFootnote(3, "Note 3: Centrality determination methodology follows ALICE Collaboration, Phys. Rev. C 88 (2013).");
        Assert.Equal(3, doc.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateAcademicPaperDoc();
        doc.AddFootnote(2, "HTML export footnote — QGP lifetime ~5 fm/c before hadronisation.");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateAcademicPaperDoc();
        doc.AddFootnote(1, "Markdown export footnote — collective flow parameter v₂ characterises elliptic flow.");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Then_GetWordCount_Positive()
    {
        var doc = CreateAcademicPaperDoc();
        doc.AddFootnote(0, "Word count footnote — QCD coupling constant αs(MZ) = 0.118 ± 0.001.");
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetFootnoteText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFootnoteText_NoThrow()
    {
        var doc = CreateAcademicPaperDoc();
        doc.AddFootnote(1, "Text retrieval footnote — deconfinement temperature Tc ≈ 155 MeV.");
        var ex = Record.Exception(() => doc.GetFootnoteText(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFootnoteText_NonNull()
    {
        var doc = CreateAcademicPaperDoc();
        doc.AddFootnote(2, "Non-null footnote — J/ψ suppression as QGP signature: Matsui & Satz, PLB 178 (1986).");
        Assert.NotNull(doc.GetFootnoteText(0));
    }

    [Fact]
    public void GetFootnoteText_Consistent()
    {
        var doc = CreateAcademicPaperDoc();
        doc.AddFootnote(0, "Consistency footnote — Bjorken energy density: εBj ~ 5-15 GeV/fm³ at RHIC.");
        Assert.Equal(doc.GetFootnoteText(0), doc.GetFootnoteText(0));
    }

    [Fact]
    public void GetFootnoteText_SaveLoad_Consistent()
    {
        var doc = CreateAcademicPaperDoc();
        doc.AddFootnote(3, "Save-load footnote — Lattice QCD predicts chiral symmetry restoration at Tc.");
        var path = TempFile("fnt_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetFootnoteText(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddFootnote_GetFootnoteCount_GetFootnoteText_SaveToFile_Pipeline()
    {
        // Historical monograph — Victorian railway network development and political economy
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "The Political Economy of Railway Mania: Capital Formation, Parliamentary Promotion and Network Expansion in Britain, 1843–1847", 1);
        doc.AppendParagraph("The Railway Mania of 1845-1847 represented the most concentrated episode of speculative capital formation in nineteenth-century Britain, with Parliament authorising over £240 million in railway projects at the peak.");
        doc.AppendParagraph("George Hudson's empire of interlocking railway companies, centred on the Midland Railway and York and North Midland Railway, exemplified the intersection of political influence, share manipulation, and infrastructure development.");

        doc.InsertHeading(3, "Capital Markets and Share Speculation", 2);
        doc.AppendParagraph("Contemporary analysis by John Stuart Mill in his 1848 Principles of Political Economy identified the railway share market as exhibiting classic speculative dynamics driven by credit expansion under the 1844 Bank Charter Act.");
        doc.AppendParagraph("Subscription lists for new railway schemes attracted deposits from a socially broad investor base including clergymen, tradesmen, and professional classes, many financing their investments through call option structures.");

        doc.InsertHeading(6, "Parliamentary Processes and Select Committee Review", 2);
        doc.AppendParagraph("The 1846 Parliamentary session witnessed 272 railway Acts receiving Royal Assent, requiring Select Committee examination of competing route proposals and financial depositions demonstrating adequate capital subscription.");
        doc.AppendParagraph("Engineer testimony before Parliamentary committees, most notably from Robert Stephenson and Isambard Kingdom Brunel, provided crucial technical arbitration between competing gauge standards and alignment proposals.");

        doc.InsertHeading(9, "Collapse and Aftermath", 1);
        doc.AppendParagraph("The contraction of railway share prices from October 1845 reversed speculative gains and precipitated widespread financial distress among heavily leveraged investors, with many projects abandoned at intermediate construction stages.");
        doc.AppendParagraph("Despite the speculative collapse, completed Victorian railway infrastructure substantially reduced internal transport costs, facilitated regional labour market integration, and accelerated the spatial concentration of manufacturing industries.");

        Assert.Equal(12, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetFootnoteCount());

        // AddFootnote — scholarly citations and clarifications
        doc.AddFootnote(1, "Parliamentary returns of 1846 session: Board of Trade Returns of Railway Companies, PP 1847 (777) lxiii.");
        Assert.Equal(1, doc.GetFootnoteCount());

        doc.AddFootnote(2, "George Hudson (1800-1871): 'Railway King'. His financial irregularities were exposed in 1849 by shareholder committees investigating fraudulent dividend payments from capital.");
        Assert.Equal(2, doc.GetFootnoteCount());

        doc.AddFootnote(3, "J.S. Mill (1848), Principles of Political Economy, Book III, Chapter XII 'Of a Monetized Currency'. Mill's analysis anticipated later Keynesian concepts of speculative demand for money.");
        Assert.Equal(3, doc.GetFootnoteCount());

        doc.AddFootnote(5, "The 1844 Bank Charter Act separated Bank of England note issue from banking departments, providing institutional framework that paradoxically facilitated credit expansion through the bill market.");
        Assert.Equal(4, doc.GetFootnoteCount());

        doc.AddFootnote(6, "House of Commons Standing Order 68 (1845) required deposited plans, sections, and books of reference, together with proof of subscription for 5% of proposed capital before Private Bill presentation.");
        Assert.Equal(5, doc.GetFootnoteCount());

        doc.AddFootnote(7, "The gauge controversy between Stephenson's 4ft 8½in standard gauge and Brunel's 7ft ¼in broad gauge on the Great Western Railway was resolved by the Gauge Act of 1846 mandating standard gauge for new trunk lines.");
        Assert.Equal(6, doc.GetFootnoteCount());

        // Consistent
        Assert.Equal(doc.GetFootnoteCount(), doc.GetFootnoteCount());

        // GetFootnoteText
        var text0 = doc.GetFootnoteText(0);
        Assert.NotNull(text0);
        Assert.Equal(text0, doc.GetFootnoteText(0)); // consistent

        var text3 = doc.GetFootnoteText(3);
        Assert.NotNull(text3);

        var text5 = doc.GetFootnoteText(5);
        Assert.NotNull(text5);

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
        var path = TempFile("dogfood_railway_mania.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetFootnoteCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetFootnoteText(0));
        Assert.NotNull(loaded.GetFootnoteText(5));

        // AddFootnote on loaded
        loaded.AddFootnote(8, "Clapham, J.H. (1938), An Economic History of Modern Britain, Vol. I, Chapter VIII 'Railways and Railway Policy to 1850'. Cambridge University Press.");
        Assert.Equal(7, loaded.GetFootnoteCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: the Railway Mania demonstrates how infrastructure investment cycles combine genuine economic opportunity with speculative excess, ultimately producing durable physical capital at substantial social and private cost.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_railway_mania_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetFootnoteCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetFootnoteText(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddFootnote(0, "Final footnote."));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
