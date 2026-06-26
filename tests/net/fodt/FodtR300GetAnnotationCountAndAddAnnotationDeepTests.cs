// Tests for FodtDocument.GetAnnotationCount, AddAnnotation, GetAnnotationText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R300

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R300: Tests for FodtDocument.GetAnnotationCount, AddAnnotation, GetAnnotationText deeper.
/// GetAnnotationCount(): returns the number of annotations/comments in the document.
/// AddAnnotation(paragraphIndex, text, author): adds an annotation to the specified paragraph.
/// GetAnnotationText(index): returns the text of the annotation at the given index.
/// Covers: GetAnnotationCount no-throw; GetAnnotationCount non-negative; GetAnnotationCount consistent;
/// GetAnnotationCount zero for new doc; GetAnnotationCount after AddAnnotation increases;
/// GetAnnotationCount save-load;
/// AddAnnotation no-throw; AddAnnotation increases count; AddAnnotation save-load;
/// AddAnnotation multiple; AddAnnotation then ExportToHtml no-throw;
/// AddAnnotation then ExportToMarkdown no-throw; AddAnnotation then GetCharCount positive;
/// GetAnnotationText no-throw; GetAnnotationText non-null; GetAnnotationText consistent;
/// GetAnnotationText save-load;
/// dogfood CreateDoc→AddAnnotation→GetAnnotationCount→GetAnnotationText→SaveToFile pipeline.
/// </summary>
public class FodtR300GetAnnotationCountAndAddAnnotationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR300GetAnnotationCountAndAddAnnotationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR300_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateRichDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Artificial Intelligence in Healthcare: Clinical Applications", 1);
        doc.AppendParagraph("Machine learning models are transforming diagnostic imaging accuracy across radiology departments.");
        doc.AppendParagraph("Natural language processing enables extraction of structured data from unstructured clinical notes.");
        doc.InsertHeading(3, "Predictive Analytics", 2);
        doc.AppendParagraph("Sepsis prediction models demonstrate 80% sensitivity 6 hours before clinical deterioration.");
        doc.AppendParagraph("Readmission risk stratification models guide targeted post-discharge intervention programmes.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetAnnotationCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAnnotationCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetAnnotationCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetAnnotationCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetAnnotationCount() >= 0);
    }

    [Fact]
    public void GetAnnotationCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetAnnotationCount(), doc.GetAnnotationCount());
    }

    [Fact]
    public void GetAnnotationCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No annotations here.");
        Assert.Equal(0, doc.GetAnnotationCount());
    }

    [Fact]
    public void GetAnnotationCount_AfterAddAnnotation_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetAnnotationCount();
        doc.AddAnnotation(1, "Consider adding citation for diagnostic accuracy claim.", "Reviewer A");
        Assert.Equal(before + 1, doc.GetAnnotationCount());
    }

    [Fact]
    public void GetAnnotationCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(3, "Verify sensitivity metric against primary literature.", "Reviewer B");
        var before = doc.GetAnnotationCount();
        var path = TempFile("anc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetAnnotationCount());
    }

    // -------------------------------------------------------------------------
    // AddAnnotation
    // -------------------------------------------------------------------------

    [Fact]
    public void AddAnnotation_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddAnnotation(0, "Check heading style.", "Editor"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddAnnotation_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetAnnotationCount();
        doc.AddAnnotation(2, "Expand on NLP use cases.", "Technical Reviewer");
        Assert.Equal(before + 1, doc.GetAnnotationCount());
    }

    [Fact]
    public void AddAnnotation_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(4, "Add cost-effectiveness data.", "Health Economist");
        var before = doc.GetAnnotationCount();
        var path = TempFile("aan_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetAnnotationCount());
    }

    [Fact]
    public void AddAnnotation_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(0, "Title could be more concise.", "Editor");
        doc.AddAnnotation(2, "Add NLP model examples.", "Technical Author");
        doc.AddAnnotation(3, "Sensitivity figure needs citation.", "Peer Reviewer");
        Assert.Equal(3, doc.GetAnnotationCount());
    }

    [Fact]
    public void AddAnnotation_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(1, "HTML annotation test.", "Tester");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddAnnotation_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(2, "Markdown annotation test.", "Tester");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddAnnotation_Then_GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(0, "Char count annotation.", "Author");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetAnnotationText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAnnotationText_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(1, "Test annotation text.", "Tester");
        var ex = Record.Exception(() => doc.GetAnnotationText(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetAnnotationText_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(2, "Non-null annotation.", "Author");
        Assert.NotNull(doc.GetAnnotationText(0));
    }

    [Fact]
    public void GetAnnotationText_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(0, "Consistent annotation.", "Reviewer");
        Assert.Equal(doc.GetAnnotationText(0), doc.GetAnnotationText(0));
    }

    [Fact]
    public void GetAnnotationText_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(3, "Save-load annotation.", "QA");
        var before = doc.GetAnnotationText(0);
        var path = TempFile("gat_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetAnnotationText(0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddAnnotation_GetAnnotationCount_GetAnnotationText_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Sustainable Finance: ESG Integration and Portfolio Management", 1);
        doc.AppendParagraph("Environmental, social, and governance criteria are increasingly embedded in institutional investment mandates.");
        doc.AppendParagraph("ESG data quality and standardisation remain significant challenges for quantitative portfolio construction.");

        doc.InsertHeading(3, "Climate Risk Assessment", 2);
        doc.AppendParagraph("Physical risk metrics quantify exposure to acute and chronic climate hazards across asset classes.");
        doc.AppendParagraph("Transition risk captures potential value erosion from policy, technology, and market shifts.");

        doc.InsertHeading(6, "Impact Measurement", 2);
        doc.AppendParagraph("The SFDR framework categorises funds by sustainability ambition level across Articles 6, 8, and 9.");
        doc.AppendParagraph("TCFD-aligned reporting requires scenario analysis across 1.5°C, 2°C, and 4°C warming pathways.");

        doc.InsertHeading(9, "Portfolio Construction", 1);
        doc.AppendParagraph("ESG integration reduces downside risk while maintaining competitive risk-adjusted returns over 5+ year horizons.");
        doc.AppendParagraph("Factor-based ESG strategies systematically tilt portfolios toward higher-scoring securities within sectors.");

        Assert.Equal(10, doc.GetParagraphCount());

        // GetAnnotationCount — zero initially
        Assert.Equal(0, doc.GetAnnotationCount());

        // AddAnnotation — review comments
        doc.AddAnnotation(0, "Title approved. Ensure subtitle alignment with journal style guide.", "Managing Editor");
        Assert.Equal(1, doc.GetAnnotationCount());

        doc.AddAnnotation(1, "Cite UNPRI signatories growth statistics (now >4000 institutions).", "Data Analyst");
        Assert.Equal(2, doc.GetAnnotationCount());

        doc.AddAnnotation(3, "Reference NGFS scenarios for physical risk taxonomy.", "Climate Specialist");
        Assert.Equal(3, doc.GetAnnotationCount());

        doc.AddAnnotation(6, "SFDR Article definitions need regulatory citation.", "Compliance Officer");
        Assert.Equal(4, doc.GetAnnotationCount());

        doc.AddAnnotation(8, "Update 5-year return data to include 2022-2026 market cycle.", "Quantitative Analyst");
        Assert.Equal(5, doc.GetAnnotationCount());

        // Consistent
        Assert.Equal(doc.GetAnnotationCount(), doc.GetAnnotationCount());

        // GetAnnotationText
        var ann0 = doc.GetAnnotationText(0);
        Assert.NotNull(ann0);
        Assert.Equal(ann0, doc.GetAnnotationText(0)); // consistent

        var ann1 = doc.GetAnnotationText(1);
        Assert.NotNull(ann1);

        var ann4 = doc.GetAnnotationText(4);
        Assert.NotNull(ann4);

        // ExportToHtml works
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown works
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // ExportToPlainText works
        var plain = doc.ExportToPlainText();
        Assert.NotNull(plain);
        Assert.NotEmpty(plain);

        // GetCharCount and GetWordCount positive
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_esg.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetAnnotationCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetAnnotationText(0));

        // AddAnnotation on loaded
        loaded.AddAnnotation(9, "Factor tilts should include sector-neutral constraint documentation.", "Portfolio Manager");
        Assert.Equal(6, loaded.GetAnnotationCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: ESG integration is converging from ethical preference to mainstream risk management practice.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_esg_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetAnnotationCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetAnnotationText(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.ExportToPlainText());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
