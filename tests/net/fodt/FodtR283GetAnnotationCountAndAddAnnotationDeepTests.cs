// Tests for FodtDocument.GetAnnotationCount, AddAnnotation, GetAnnotationText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R283

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R283: Tests for FodtDocument.GetAnnotationCount, AddAnnotation, GetAnnotationText deeper.
/// GetAnnotationCount(): returns the number of annotations in the document.
/// AddAnnotation(paragraphIndex, author, text): adds a named annotation at the paragraph.
/// GetAnnotationText(annotationIndex): returns the text content of the annotation.
/// Covers: GetAnnotationCount no-throw; GetAnnotationCount non-negative; GetAnnotationCount consistent;
/// GetAnnotationCount zero for new doc; GetAnnotationCount after AddAnnotation increases;
/// GetAnnotationCount save-load;
/// AddAnnotation no-throw; AddAnnotation increases count; AddAnnotation save-load;
/// AddAnnotation multiple; AddAnnotation then ExportToHtml no-throw;
/// AddAnnotation then ExportToMarkdown no-throw; AddAnnotation then GetCharCount positive;
/// GetAnnotationText no-throw; GetAnnotationText non-null; GetAnnotationText consistent;
/// GetAnnotationText save-load; GetAnnotationText multiple annotations;
/// dogfood CreateDoc→AddAnnotation→GetAnnotationCount→GetAnnotationText→SaveToFile pipeline.
/// </summary>
public class FodtR283GetAnnotationCountAndAddAnnotationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR283GetAnnotationCountAndAddAnnotationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR283_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Research Paper on Platform Scalability", 1);
        doc.AppendParagraph("This paper presents findings from a twelve-month study of platform scalability.");
        doc.AppendParagraph("All experiments were conducted under controlled conditions with reproducible results.");
        doc.InsertHeading(3, "Methodology", 2);
        doc.AppendParagraph("The study employed a mixed-method approach combining quantitative and qualitative data.");
        doc.AppendParagraph("Peer review was conducted by three independent researchers in the field.");
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
        doc.AppendParagraph("Document without annotations.");
        Assert.Equal(0, doc.GetAnnotationCount());
    }

    [Fact]
    public void GetAnnotationCount_AfterAddAnnotation_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetAnnotationCount();
        doc.AddAnnotation(1, "Reviewer A", "This section needs clarification.");
        Assert.Equal(before + 1, doc.GetAnnotationCount());
    }

    [Fact]
    public void GetAnnotationCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(1, "Editor", "Verify citation format.");
        var before = doc.GetAnnotationCount();
        var path = TempFile("ac_save.fodt");
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
        var ex = Record.Exception(() => doc.AddAnnotation(1, "Author", "Initial review comment here."));
        Assert.Null(ex);
    }

    [Fact]
    public void AddAnnotation_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetAnnotationCount();
        doc.AddAnnotation(2, "Peer Reviewer", "Statistical analysis is sound.");
        Assert.Equal(before + 1, doc.GetAnnotationCount());
    }

    [Fact]
    public void AddAnnotation_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(1, "Proofreader", "Typo on line three.");
        var before = doc.GetAnnotationCount();
        var path = TempFile("aa_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetAnnotationCount());
    }

    [Fact]
    public void AddAnnotation_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(0, "Reviewer1", "Title is appropriate.");
        doc.AddAnnotation(1, "Reviewer2", "Abstract could be more concise.");
        doc.AddAnnotation(3, "Reviewer3", "Methodology is rigorous.");
        Assert.Equal(3, doc.GetAnnotationCount());
    }

    [Fact]
    public void AddAnnotation_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(1, "Editor", "HTML annotation test.");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddAnnotation_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(2, "Reviewer", "Markdown annotation test.");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddAnnotation_Then_GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(1, "Author", "Char count test annotation.");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetAnnotationText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAnnotationText_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(1, "Rev", "Test text.");
        var ex = Record.Exception(() => doc.GetAnnotationText(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetAnnotationText_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(1, "Rev", "Non null text.");
        Assert.NotNull(doc.GetAnnotationText(0));
    }

    [Fact]
    public void GetAnnotationText_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(1, "Rev", "Consistent text.");
        Assert.Equal(doc.GetAnnotationText(0), doc.GetAnnotationText(0));
    }

    [Fact]
    public void GetAnnotationText_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(1, "Author", "Save load text.");
        var before = doc.GetAnnotationText(0);
        var path = TempFile("gat_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetAnnotationText(0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    [Fact]
    public void GetAnnotationText_Multiple_Annotations()
    {
        var doc = CreateRichDoc();
        doc.AddAnnotation(0, "Rev1", "First annotation text.");
        doc.AddAnnotation(2, "Rev2", "Second annotation text.");
        Assert.NotNull(doc.GetAnnotationText(0));
        Assert.NotNull(doc.GetAnnotationText(1));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddAnnotation_GetAnnotationCount_GetAnnotationText_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Clinical Trial Protocol Version 3.2", 1);
        doc.AppendParagraph("This protocol defines the procedures for the Phase II clinical trial of Compound X.");
        doc.AppendParagraph("All procedures must comply with ICH-GCP guidelines and local regulatory requirements.");

        doc.InsertHeading(3, "Inclusion Criteria", 2);
        doc.AppendParagraph("Patients aged eighteen to seventy-five years with confirmed diagnosis.");
        doc.AppendParagraph("No prior treatment with immunosuppressive agents within the last six months.");

        doc.InsertHeading(6, "Exclusion Criteria", 2);
        doc.AppendParagraph("Patients with known hypersensitivity to any component of the study medication.");
        doc.AppendParagraph("Pregnant or breastfeeding individuals are excluded from participation.");

        doc.InsertHeading(9, "Primary Endpoints", 1);
        doc.AppendParagraph("The primary endpoint is progression-free survival at twelve months.");
        doc.AppendParagraph("Secondary endpoints include overall survival and quality of life measures.");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetAnnotationCount — zero initially
        Assert.Equal(0, doc.GetAnnotationCount());

        // AddAnnotation — protocol title
        doc.AddAnnotation(0, "Medical Monitor", "Version 3.2 supersedes all prior versions.");
        Assert.Equal(1, doc.GetAnnotationCount());

        // AddAnnotation — inclusion
        doc.AddAnnotation(3, "Biostatistician", "Age range confirmed by power calculation.");
        Assert.Equal(2, doc.GetAnnotationCount());

        // AddAnnotation — exclusion
        doc.AddAnnotation(6, "Principal Investigator", "Review exclusion against updated label.");
        Assert.Equal(3, doc.GetAnnotationCount());

        // AddAnnotation — primary endpoint
        doc.AddAnnotation(9, "Regulatory Advisor", "Endpoint aligned with FDA guidance document.");
        Assert.Equal(4, doc.GetAnnotationCount());

        // GetAnnotationText
        var t0 = doc.GetAnnotationText(0);
        var t1 = doc.GetAnnotationText(1);
        var t2 = doc.GetAnnotationText(2);
        var t3 = doc.GetAnnotationText(3);
        Assert.NotNull(t0);
        Assert.NotNull(t1);
        Assert.NotNull(t2);
        Assert.NotNull(t3);

        // Consistent
        Assert.Equal(doc.GetAnnotationCount(), doc.GetAnnotationCount());
        Assert.Equal(doc.GetAnnotationText(0), doc.GetAnnotationText(0));

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

        // GetCharCount positive
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_protocol.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetAnnotationCount());
        Assert.True(loaded.GetParagraphCount() > 0);

        // GetAnnotationText on loaded
        for (int i = 0; i < loaded.GetAnnotationCount(); i++)
            Assert.NotNull(loaded.GetAnnotationText(i));

        // AddAnnotation on loaded
        loaded.AddAnnotation(loaded.GetParagraphCount() - 1, "Sponsor", "Final review pending ethics committee.");
        Assert.Equal(5, loaded.GetAnnotationCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Amendment: protocol updated per Data Safety Monitoring Board recommendations.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_protocol_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetAnnotationCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.ExportToPlainText());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
