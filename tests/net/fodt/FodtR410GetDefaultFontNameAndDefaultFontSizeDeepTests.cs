// Tests for FodtDocument.GetDefaultFontName, GetDefaultFontSize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R410

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R410: Tests for FodtDocument.GetDefaultFontName, GetDefaultFontSize deeper.
/// GetDefaultFontName(): returns the name of the default body font configured for the document.
/// GetDefaultFontSize(): returns the default body font size (in points) configured for the document.
/// Covers: GetDefaultFontName no-throw; GetDefaultFontName non-null/non-empty;
/// GetDefaultFontName consistent; GetDefaultFontName save-load;
/// GetDefaultFontSize no-throw; GetDefaultFontSize positive;
/// GetDefaultFontSize consistent; GetDefaultFontSize save-load; dogfood pipeline.
/// </summary>
public class FodtR410GetDefaultFontNameAndDefaultFontSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR410GetDefaultFontNameAndDefaultFontSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR410_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // GetDefaultFontName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDefaultFontName_NoThrow()
    {
        var doc = new FodtDocument();
        var ex = Record.Exception(() => doc.GetDefaultFontName());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDefaultFontName_NonNullAndNonEmpty()
    {
        var doc = new FodtDocument();
        var name = doc.GetDefaultFontName();
        Assert.NotNull(name);
        Assert.NotEmpty(name);
    }

    [Fact]
    public void GetDefaultFontName_Consistent()
    {
        var doc = new FodtDocument();
        Assert.Equal(doc.GetDefaultFontName(), doc.GetDefaultFontName());
    }

    [Fact]
    public void GetDefaultFontName_SaveLoad_Consistent()
    {
        var doc = new FodtDocument();
        var before = doc.GetDefaultFontName();
        var path = TempFile("fn_save.fodt");
        doc.SaveToFile(path);
        Assert.Equal(before, FodtDocument.LoadFile(path).GetDefaultFontName());
    }

    // -------------------------------------------------------------------------
    // GetDefaultFontSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDefaultFontSize_NoThrow()
    {
        var doc = new FodtDocument();
        var ex = Record.Exception(() => doc.GetDefaultFontSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDefaultFontSize_Positive()
    {
        var doc = new FodtDocument();
        Assert.True(doc.GetDefaultFontSize() > 0);
    }

    [Fact]
    public void GetDefaultFontSize_Consistent()
    {
        var doc = new FodtDocument();
        Assert.Equal(doc.GetDefaultFontSize(), doc.GetDefaultFontSize());
    }

    [Fact]
    public void GetDefaultFontSize_SaveLoad_Consistent()
    {
        var doc = new FodtDocument();
        var before = doc.GetDefaultFontSize();
        var path = TempFile("fs_save.fodt");
        doc.SaveToFile(path);
        Assert.Equal(before, FodtDocument.LoadFile(path).GetDefaultFontSize(), precision: 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDefaultFontName_GetDefaultFontSize_Pipeline()
    {
        // Education — Ofqual / DfE: National Reference Test 2024 Technical Report
        // Document-level font defaults drive ADA accessibility compliance for DfE-mandated
        // published specifications; font name and size checked against WCAG 2.1 typography guidance

        var doc = new FodtDocument();

        // Add front matter
        doc.AddParagraph("National Reference Test 2024 — Technical Report");
        doc.AddParagraph("Ofqual / Standards and Testing Agency / Department for Education");
        doc.AddParagraph("Reference: Ofqual/24/6842");
        doc.AddParagraph("Publication date: March 2024");
        doc.AddParagraph(string.Empty);

        // Executive Summary
        doc.AddParagraph("Executive Summary");
        doc.AddParagraph(
            "The National Reference Test (NRT) 2024 provides nationally representative data on the " +
            "attainment of Year 11 students in English and mathematics. The NRT is designed to enable " +
            "stable year-on-year comparisons of student performance independent of GCSE grade boundaries.");

        // Section 1: Background
        doc.AddParagraph("1. Background and Policy Context");
        doc.AddParagraph(
            "The NRT was established following the Ofqual consultation on maintaining standards " +
            "in GCSE reformed qualifications (2015-16). The test administers items previously used " +
            "in PISA/TIMSS frameworks, adapted for the English national curriculum at KS4.");

        // Section 2: Sample Design
        doc.AddParagraph("2. Sample Design");
        doc.AddParagraph(
            "The 2024 administration recruited a stratified random sample of 300 schools across " +
            "England, yielding a pupil sample of approximately 15,000 Year 11 students. Schools " +
            "were stratified by region, school type (academy/maintained), and prior attainment band.");
        doc.AddParagraph(
            "Response rate: 94.7% at school level; 91.2% at pupil level (within-school). " +
            "Weighting applied using trimmed Horvitz-Thompson estimators to correct for differential " +
            "non-response by Ofsted inspection rating and FSM eligibility.");

        // Section 3: Results
        doc.AddParagraph("3. Headline Results");
        doc.AddParagraph(
            "English reading: mean scaled score 493.2 (SE 1.8), 95% CI [489.7, 496.7]. " +
            "Year-on-year change: +2.1 points (not statistically significant at p<0.05). " +
            "Mathematics: mean scaled score 501.4 (SE 2.1), 95% CI [497.3, 505.5]. " +
            "Year-on-year change: +3.7 points (p=0.032, significant at 5% level).");

        // Section 4: Equalities Analysis
        doc.AddParagraph("4. Equalities Analysis");
        doc.AddParagraph(
            "Attainment gap by FSM eligibility: English 41.2 scaled score points (down from 43.8 in 2023). " +
            "Mathematics: 38.7 points (down from 41.2 in 2023). " +
            "Gender gap: Females outperform males in English by 18.4 points; males outperform females " +
            "in mathematics by 6.2 points. Both trends consistent with GCSE data.");

        // Section 5: Measurement Properties
        doc.AddParagraph("5. Measurement Properties and IRT Calibration");
        doc.AddParagraph(
            "Item parameters estimated using a 2-parameter logistic IRT model (2PL) via marginal " +
            "maximum likelihood (MML). Person ability estimates obtained via EAP (Expected A Posteriori) " +
            "with 40-point quadrature approximation. Test information peak at theta=0.2 (English) and " +
            "theta=-0.1 (mathematics), consistent with national ability distribution.");

        // Verify document structure
        Assert.True(doc.ParagraphCount > 0);

        // --- Core tests ---
        var fontName = doc.GetDefaultFontName();
        Assert.NotNull(fontName);
        Assert.NotEmpty(fontName);
        Assert.Equal(fontName, doc.GetDefaultFontName()); // consistent

        var fontSize = doc.GetDefaultFontSize();
        Assert.True(fontSize > 0);
        Assert.Equal(fontSize, doc.GetDefaultFontSize()); // consistent

        // SaveToFile
        var outPath = TempFile("ofqual_nrt_2024_technical_report.fodt");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(outPath);
        Assert.Equal(doc.ParagraphCount, loaded.ParagraphCount);

        var loadedFontName = loaded.GetDefaultFontName();
        Assert.NotNull(loadedFontName);
        Assert.NotEmpty(loadedFontName);
        Assert.Equal(fontName, loadedFontName);

        var loadedFontSize = loaded.GetDefaultFontSize();
        Assert.True(loadedFontSize > 0);
        Assert.Equal(fontSize, loadedFontSize, precision: 5);

        var ex1 = Record.Exception(() => loaded.GetDefaultFontName());
        var ex2 = Record.Exception(() => loaded.GetDefaultFontSize());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
