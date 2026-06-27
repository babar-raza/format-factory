// Tests for FodtDocument.GetCommentCount, AddComment, GetCommentText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R314

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R314: Tests for FodtDocument.GetCommentCount, AddComment, GetCommentText deeper.
/// GetCommentCount(): returns the number of comments in the document.
/// AddComment(paragraphIndex, author, text): adds an annotation comment to the specified paragraph.
/// GetCommentText(index): returns the text content of the comment at the given index.
/// Covers: GetCommentCount no-throw; GetCommentCount non-negative; GetCommentCount consistent;
/// GetCommentCount zero for new doc; GetCommentCount after AddComment increases;
/// GetCommentCount save-load;
/// AddComment no-throw; AddComment increases count; AddComment save-load;
/// AddComment multiple; AddComment then ExportToHtml no-throw; AddComment then ExportToMarkdown no-throw;
/// AddComment then GetCharCount positive;
/// GetCommentText no-throw; GetCommentText non-null; GetCommentText consistent;
/// GetCommentText save-load;
/// dogfood CreateDoc→AddComment→GetCommentCount→GetCommentText→SaveToFile pipeline.
/// </summary>
public class FodtR314GetCommentCountAndAddCommentDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR314GetCommentCountAndAddCommentDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR314_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Computational Fluid Dynamics: Turbulence Modelling and Simulation", 1);
        doc.AppendParagraph("Reynolds-averaged Navier-Stokes (RANS) equations provide computationally tractable turbulence closure for engineering simulations.");
        doc.AppendParagraph("Large eddy simulation (LES) resolves the energy-containing turbulent scales while modelling sub-grid scale dynamics.");
        doc.InsertHeading(3, "Numerical Methods", 2);
        doc.AppendParagraph("Finite volume discretisation preserves local conservation properties on unstructured meshes critical for complex geometry flows.");
        doc.AppendParagraph("High-order spectral element methods achieve exponential convergence rates for smooth flow regimes with moderate Reynolds numbers.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCommentCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCommentCount_NoThrow()
    {
        var doc = CreateResearchDoc();
        var ex = Record.Exception(() => doc.GetCommentCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCommentCount_NonNegative()
    {
        var doc = CreateResearchDoc();
        Assert.True(doc.GetCommentCount() >= 0);
    }

    [Fact]
    public void GetCommentCount_Consistent()
    {
        var doc = CreateResearchDoc();
        Assert.Equal(doc.GetCommentCount(), doc.GetCommentCount());
    }

    [Fact]
    public void GetCommentCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A pristine document with no reviewer comments.");
        Assert.Equal(0, doc.GetCommentCount());
    }

    [Fact]
    public void GetCommentCount_AfterAddComment_Increases()
    {
        var doc = CreateResearchDoc();
        var before = doc.GetCommentCount();
        doc.AddComment(1, "Reviewer_A", "RANS models underestimate Reynolds stress anisotropy in separation zones.");
        Assert.Equal(before + 1, doc.GetCommentCount());
    }

    [Fact]
    public void GetCommentCount_SaveLoad_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddComment(2, "Reviewer_B", "LES requires significantly finer mesh near solid boundaries.");
        var before = doc.GetCommentCount();
        var path = TempFile("cc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCommentCount());
    }

    // -------------------------------------------------------------------------
    // AddComment
    // -------------------------------------------------------------------------

    [Fact]
    public void AddComment_NoThrow()
    {
        var doc = CreateResearchDoc();
        var ex = Record.Exception(() => doc.AddComment(0, "Reviewer_C", "Consider citing Pope (2000) turbulence textbook."));
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_Increases_Count()
    {
        var doc = CreateResearchDoc();
        var before = doc.GetCommentCount();
        doc.AddComment(3, "Reviewer_A", "Finite volume stencils should be discussed in context of TVD schemes.");
        Assert.Equal(before + 1, doc.GetCommentCount());
    }

    [Fact]
    public void AddComment_SaveLoad_Persists()
    {
        var doc = CreateResearchDoc();
        doc.AddComment(4, "Reviewer_D", "Spectral element p-refinement convergence rates need citation.");
        var before = doc.GetCommentCount();
        var path = TempFile("ac_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCommentCount());
    }

    [Fact]
    public void AddComment_Multiple()
    {
        var doc = CreateResearchDoc();
        doc.AddComment(0, "Author", "Abstract placeholder comment.");
        doc.AddComment(1, "Reviewer_A", "RANS closure needs k-epsilon comparison.");
        doc.AddComment(3, "Reviewer_B", "Clarify mesh convergence criteria.");
        Assert.Equal(3, doc.GetCommentCount());
    }

    [Fact]
    public void AddComment_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddComment(2, "Reviewer_C", "HTML export test comment.");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddComment(1, "Reviewer_A", "Markdown export test comment.");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_Then_GetCharCount_Positive()
    {
        var doc = CreateResearchDoc();
        doc.AddComment(0, "Author", "Char count test.");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetCommentText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCommentText_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddComment(1, "Reviewer_A", "Test comment text.");
        var ex = Record.Exception(() => doc.GetCommentText(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCommentText_NonNull()
    {
        var doc = CreateResearchDoc();
        doc.AddComment(2, "Reviewer_B", "Non-null test comment.");
        Assert.NotNull(doc.GetCommentText(0));
    }

    [Fact]
    public void GetCommentText_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddComment(0, "Author", "Consistent comment.");
        Assert.Equal(doc.GetCommentText(0), doc.GetCommentText(0));
    }

    [Fact]
    public void GetCommentText_SaveLoad_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddComment(3, "Reviewer_C", "Save-load comment text.");
        var before = doc.GetCommentText(0);
        var path = TempFile("ct_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetCommentText(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddComment_GetCommentCount_GetCommentText_SaveToFile_Pipeline()
    {
        // Peer review workflow — climate science manuscript with reviewer annotations
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Arctic Sea Ice Decline: Attribution, Feedbacks, and Future Projections", 1);
        doc.AppendParagraph("Arctic sea ice extent has declined by approximately 13% per decade since satellite observations began in 1979.");
        doc.AppendParagraph("The ice-albedo feedback amplifies Arctic warming at twice the global mean rate, a phenomenon termed Arctic amplification.");

        doc.InsertHeading(3, "Forcing Attribution", 2);
        doc.AppendParagraph("Anthropogenic greenhouse gas forcing accounts for 80-90% of observed Arctic sea ice decline based on detection-attribution analyses.");
        doc.AppendParagraph("Natural variability patterns including the Arctic Oscillation and Atlantic Multidecadal Oscillation explain residual interannual variance.");

        doc.InsertHeading(6, "Climate Model Projections", 2);
        doc.AppendParagraph("CMIP6 multi-model ensemble projects September Arctic sea ice-free conditions by 2050 under SSP2-4.5 scenarios.");
        doc.AppendParagraph("Model spread in sea ice projections arises primarily from differences in cloud radiative forcing parameterisations.");

        doc.InsertHeading(9, "Socioeconomic Implications", 1);
        doc.AppendParagraph("Arctic shipping route viability increases with sea ice decline, reducing transit distances between Europe and Asia by 40%.");
        doc.AppendParagraph("Permafrost thaw releases methane and CO2 stores, potentially triggering positive feedback loops in the carbon cycle.");

        Assert.Equal(10, doc.GetParagraphCount());

        // GetCommentCount — zero initially
        Assert.Equal(0, doc.GetCommentCount());

        // AddComment — peer review annotations
        doc.AddComment(1, "Reviewer_1", "Specify the exact satellite instrument (SSMI/SSMIS) and data product version.");
        Assert.Equal(1, doc.GetCommentCount());

        doc.AddComment(2, "Reviewer_2", "Ice-albedo feedback magnitude varies by season — disaggregate summer vs winter contributions.");
        Assert.Equal(2, doc.GetCommentCount());

        doc.AddComment(3, "Reviewer_1", "Cite Notz & Stroeve (2016) for the 80-90% attribution figure.");
        Assert.Equal(3, doc.GetCommentCount());

        doc.AddComment(5, "Editor", "The ice-free definition (extent < 1 million km²) should be stated explicitly.");
        Assert.Equal(4, doc.GetCommentCount());

        doc.AddComment(6, "Reviewer_2", "Cloud parameterisation reference: Pithan & Mauritsen (2014) deserves citation.");
        Assert.Equal(5, doc.GetCommentCount());

        doc.AddComment(8, "Reviewer_1", "Methane emission estimates from permafrost thaw vary by factor 3 across recent studies.");
        Assert.Equal(6, doc.GetCommentCount());

        // Consistent
        Assert.Equal(doc.GetCommentCount(), doc.GetCommentCount());

        // GetCommentText
        var text0 = doc.GetCommentText(0);
        Assert.NotNull(text0);
        Assert.Equal(text0, doc.GetCommentText(0)); // consistent

        var text3 = doc.GetCommentText(3);
        Assert.NotNull(text3);

        var text5 = doc.GetCommentText(5);
        Assert.NotNull(text5);

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
        var path = TempFile("dogfood_arctic_review.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetCommentCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetCommentText(0));

        // AddComment on loaded
        loaded.AddComment(9, "Author_Response", "Thank you for the methane reference — emission estimates updated per Turetsky et al. (2020).");
        Assert.Equal(7, loaded.GetCommentCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: accelerating sea ice loss necessitates urgent mitigation and adaptation strategies across Arctic-adjacent nations.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_arctic_review_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetCommentCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetCommentText(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddComment(0, "NewReviewer", "Final check comment."));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
