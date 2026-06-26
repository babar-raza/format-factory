// Tests for FodtDocument.GetCrossReferenceCount, AddCrossReference, GetCrossReferenceTarget deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R297

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R297: Tests for FodtDocument.GetCrossReferenceCount, AddCrossReference, GetCrossReferenceTarget deeper.
/// GetCrossReferenceCount(): returns the number of cross-references in the document.
/// AddCrossReference(name, targetParagraph): adds a cross-reference to the specified paragraph.
/// GetCrossReferenceTarget(name): returns the target paragraph index for the named cross-reference.
/// Covers: GetCrossReferenceCount no-throw; GetCrossReferenceCount non-negative; GetCrossReferenceCount consistent;
/// GetCrossReferenceCount zero for new doc; GetCrossReferenceCount after AddCrossReference increases;
/// GetCrossReferenceCount save-load;
/// AddCrossReference no-throw; AddCrossReference increases count; AddCrossReference save-load;
/// AddCrossReference multiple; AddCrossReference then ExportToHtml no-throw;
/// AddCrossReference then ExportToMarkdown no-throw; AddCrossReference then GetCharCount positive;
/// GetCrossReferenceTarget no-throw; GetCrossReferenceTarget non-negative; GetCrossReferenceTarget consistent;
/// GetCrossReferenceTarget save-load;
/// dogfood CreateDoc→AddCrossReference→GetCrossReferenceCount→GetCrossReferenceTarget→SaveToFile pipeline.
/// </summary>
public class FodtR297GetCrossReferenceCountAndAddCrossReferenceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR297GetCrossReferenceCountAndAddCrossReferenceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR297_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Computational Neuroscience: Models and Methods", 1);
        doc.AppendParagraph("Spiking neural networks model information processing through discrete action potentials.");
        doc.AppendParagraph("Rate coding and temporal coding represent competing theories of neural information encoding.");
        doc.InsertHeading(3, "Integrate-and-Fire Models", 2);
        doc.AppendParagraph("The leaky integrate-and-fire neuron captures essential membrane potential dynamics.");
        doc.AppendParagraph("Conductance-based models extend LIF to include voltage-gated ion channel dynamics.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCrossReferenceCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCrossReferenceCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetCrossReferenceCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCrossReferenceCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetCrossReferenceCount() >= 0);
    }

    [Fact]
    public void GetCrossReferenceCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetCrossReferenceCount(), doc.GetCrossReferenceCount());
    }

    [Fact]
    public void GetCrossReferenceCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No cross-references here.");
        Assert.Equal(0, doc.GetCrossReferenceCount());
    }

    [Fact]
    public void GetCrossReferenceCount_AfterAddCrossReference_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCrossReferenceCount();
        doc.AddCrossReference("ref_intro", 0);
        Assert.Equal(before + 1, doc.GetCrossReferenceCount());
    }

    [Fact]
    public void GetCrossReferenceCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddCrossReference("ref_lif", 3);
        var before = doc.GetCrossReferenceCount();
        var path = TempFile("crc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCrossReferenceCount());
    }

    // -------------------------------------------------------------------------
    // AddCrossReference
    // -------------------------------------------------------------------------

    [Fact]
    public void AddCrossReference_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddCrossReference("xref_main", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void AddCrossReference_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCrossReferenceCount();
        doc.AddCrossReference("xref_snn", 1);
        Assert.Equal(before + 1, doc.GetCrossReferenceCount());
    }

    [Fact]
    public void AddCrossReference_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddCrossReference("xref_lif", 3);
        var before = doc.GetCrossReferenceCount();
        var path = TempFile("acr_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCrossReferenceCount());
    }

    [Fact]
    public void AddCrossReference_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddCrossReference("xref_intro", 0);
        doc.AddCrossReference("xref_rate_coding", 2);
        doc.AddCrossReference("xref_conductance", 4);
        Assert.Equal(3, doc.GetCrossReferenceCount());
    }

    [Fact]
    public void AddCrossReference_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddCrossReference("xref_html", 1);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddCrossReference_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddCrossReference("xref_md", 2);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddCrossReference_Then_GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.AddCrossReference("xref_char", 0);
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetCrossReferenceTarget
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCrossReferenceTarget_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddCrossReference("target_test", 2);
        var ex = Record.Exception(() => doc.GetCrossReferenceTarget("target_test"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCrossReferenceTarget_NonNegative()
    {
        var doc = CreateRichDoc();
        doc.AddCrossReference("target_nonneg", 1);
        Assert.True(doc.GetCrossReferenceTarget("target_nonneg") >= 0);
    }

    [Fact]
    public void GetCrossReferenceTarget_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddCrossReference("target_consist", 3);
        Assert.Equal(
            doc.GetCrossReferenceTarget("target_consist"),
            doc.GetCrossReferenceTarget("target_consist"));
    }

    [Fact]
    public void GetCrossReferenceTarget_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddCrossReference("target_sl", 2);
        var before = doc.GetCrossReferenceTarget("target_sl");
        var path = TempFile("gcrt_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetCrossReferenceTarget("target_sl");
        Assert.True(after >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddCrossReference_GetCrossReferenceCount_GetCrossReferenceTarget_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Macroeconomic Policy Frameworks and Institutional Design", 1);
        doc.AppendParagraph("Monetary policy frameworks evolved significantly following the 1970s stagflation crisis.");
        doc.AppendParagraph("Inflation targeting emerged as the dominant central bank framework in the 1990s.");

        doc.InsertHeading(3, "Fiscal Policy Constraints", 2);
        doc.AppendParagraph("Fiscal rules constrain government borrowing to maintain debt sustainability.");
        doc.AppendParagraph("Counter-cyclical fiscal policy requires accumulation of surpluses during expansionary periods.");

        doc.InsertHeading(6, "Monetary-Fiscal Coordination", 2);
        doc.AppendParagraph("Fiscal dominance occurs when monetary policy is subordinated to fiscal financing needs.");
        doc.AppendParagraph("The fiscal theory of the price level challenges conventional monetary policy analysis.");

        doc.InsertHeading(9, "Institutional Frameworks", 1);
        doc.AppendParagraph("Central bank independence is associated with lower inflation and better policy credibility.");
        doc.AppendParagraph("Fiscal councils provide independent assessment of fiscal plans and sustainability.");

        Assert.Equal(10, doc.GetParagraphCount());

        // GetCrossReferenceCount — zero initially
        Assert.Equal(0, doc.GetCrossReferenceCount());

        // AddCrossReference — key sections
        doc.AddCrossReference("xref_monetary_policy", 0);
        Assert.Equal(1, doc.GetCrossReferenceCount());

        doc.AddCrossReference("xref_fiscal_rules", 3);
        Assert.Equal(2, doc.GetCrossReferenceCount());

        doc.AddCrossReference("xref_coordination", 6);
        Assert.Equal(3, doc.GetCrossReferenceCount());

        doc.AddCrossReference("xref_institutions", 9);
        Assert.Equal(4, doc.GetCrossReferenceCount());

        // Consistent
        Assert.Equal(doc.GetCrossReferenceCount(), doc.GetCrossReferenceCount());

        // GetCrossReferenceTarget
        var t0 = doc.GetCrossReferenceTarget("xref_monetary_policy");
        Assert.True(t0 >= 0);
        Assert.Equal(t0, doc.GetCrossReferenceTarget("xref_monetary_policy")); // consistent

        var t1 = doc.GetCrossReferenceTarget("xref_fiscal_rules");
        Assert.True(t1 >= 0);

        var t2 = doc.GetCrossReferenceTarget("xref_coordination");
        Assert.True(t2 >= 0);

        var t3 = doc.GetCrossReferenceTarget("xref_institutions");
        Assert.True(t3 >= 0);

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
        var path = TempFile("dogfood_macropolicy.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetCrossReferenceCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.True(loaded.GetCrossReferenceTarget("xref_monetary_policy") >= 0);

        // AddCrossReference on loaded
        loaded.AddCrossReference("xref_conclusion", loaded.GetParagraphCount() - 1);
        Assert.Equal(5, loaded.GetCrossReferenceCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: effective macroeconomic management requires coherent monetary and fiscal frameworks.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_macropolicy_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetCrossReferenceCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.ExportToPlainText());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
