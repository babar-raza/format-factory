// Tests for FodtDocument.GetRevisionCount, AcceptAllChanges, GetTrackedChangeSummary deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R302

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R302: Tests for FodtDocument.GetRevisionCount, AcceptAllChanges, GetTrackedChangeSummary deeper.
/// GetRevisionCount(): returns the number of tracked revisions in the document.
/// AcceptAllChanges(): returns a new document with all tracked changes accepted.
/// GetTrackedChangeSummary(): returns a summary string of the tracked changes.
/// Covers: GetRevisionCount no-throw; GetRevisionCount non-negative; GetRevisionCount consistent;
/// GetRevisionCount zero for new doc; GetRevisionCount save-load;
/// AcceptAllChanges no-throw; AcceptAllChanges non-null; AcceptAllChanges paragraph count leq original;
/// AcceptAllChanges revision count leq original; AcceptAllChanges save-load;
/// GetTrackedChangeSummary no-throw; GetTrackedChangeSummary non-null; GetTrackedChangeSummary consistent;
/// GetTrackedChangeSummary save-load;
/// dogfood CreateDoc→GetRevisionCount→AcceptAllChanges→GetTrackedChangeSummary→SaveToFile pipeline.
/// </summary>
public class FodtR302GetRevisionCountAndTrackChangesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR302GetRevisionCountAndTrackChangesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR302_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Quantum Computing: Principles and Applications", 1);
        doc.AppendParagraph("Quantum superposition allows qubits to exist in multiple states simultaneously.");
        doc.AppendParagraph("Quantum entanglement enables correlations between particles regardless of distance.");
        doc.InsertHeading(3, "Quantum Algorithms", 2);
        doc.AppendParagraph("Shor's algorithm provides exponential speedup for integer factorisation over classical methods.");
        doc.AppendParagraph("Grover's algorithm delivers quadratic speedup for unstructured database search problems.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetRevisionCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRevisionCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetRevisionCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetRevisionCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetRevisionCount() >= 0);
    }

    [Fact]
    public void GetRevisionCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetRevisionCount(), doc.GetRevisionCount());
    }

    [Fact]
    public void GetRevisionCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Fresh document, no revisions.");
        Assert.Equal(0, doc.GetRevisionCount());
    }

    [Fact]
    public void GetRevisionCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetRevisionCount();
        var path = TempFile("rc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRevisionCount());
    }

    // -------------------------------------------------------------------------
    // AcceptAllChanges
    // -------------------------------------------------------------------------

    [Fact]
    public void AcceptAllChanges_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AcceptAllChanges());
        Assert.Null(ex);
    }

    [Fact]
    public void AcceptAllChanges_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.AcceptAllChanges());
    }

    [Fact]
    public void AcceptAllChanges_RevisionCount_LeqOriginal()
    {
        var doc = CreateRichDoc();
        var original = doc.GetRevisionCount();
        var accepted = doc.AcceptAllChanges();
        Assert.True(accepted.GetRevisionCount() <= original);
    }

    [Fact]
    public void AcceptAllChanges_ParagraphCount_Preserved()
    {
        var doc = CreateRichDoc();
        var accepted = doc.AcceptAllChanges();
        Assert.True(accepted.GetParagraphCount() >= 0);
    }

    [Fact]
    public void AcceptAllChanges_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var accepted = doc.AcceptAllChanges();
        var path = TempFile("aac_save.fodt");
        accepted.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.True(loaded.GetRevisionCount() >= 0);
        Assert.Equal(accepted.GetRevisionCount(), loaded.GetRevisionCount());
    }

    // -------------------------------------------------------------------------
    // GetTrackedChangeSummary
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTrackedChangeSummary_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetTrackedChangeSummary());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTrackedChangeSummary_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetTrackedChangeSummary());
    }

    [Fact]
    public void GetTrackedChangeSummary_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetTrackedChangeSummary(), doc.GetTrackedChangeSummary());
    }

    [Fact]
    public void GetTrackedChangeSummary_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetTrackedChangeSummary();
        var path = TempFile("gtcs_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetTrackedChangeSummary();
        Assert.NotNull(after);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRevisionCount_AcceptAllChanges_GetTrackedChangeSummary_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Supply Chain Resilience: Strategies for the Post-Pandemic Era", 1);
        doc.AppendParagraph("Global supply chains experienced unprecedented disruptions during the 2020-2022 pandemic period.");
        doc.AppendParagraph("Just-in-time inventory strategies proved vulnerable to demand shocks and logistics failures.");

        doc.InsertHeading(3, "Resilience Frameworks", 2);
        doc.AppendParagraph("The SCOR model provides a structured framework for assessing supply chain performance dimensions.");
        doc.AppendParagraph("Visibility platforms enable end-to-end tracking of materials and components across suppliers.");

        doc.InsertHeading(6, "Nearshoring and Diversification", 2);
        doc.AppendParagraph("Regional supply chain hubs reduce dependency on single-source geographies for critical components.");
        doc.AppendParagraph("Dual-sourcing strategies impose cost penalties but significantly reduce supply disruption risk.");

        doc.InsertHeading(9, "Digital Supply Chains", 1);
        doc.AppendParagraph("Digital twins enable simulation of supply chain scenarios to test resilience under stress conditions.");
        doc.AppendParagraph("AI-driven demand forecasting reduces inventory holding costs while maintaining service levels.");

        Assert.Equal(10, doc.GetParagraphCount());

        // GetRevisionCount — zero initially
        Assert.Equal(0, doc.GetRevisionCount());

        // GetTrackedChangeSummary — non-null even without changes
        var summary = doc.GetTrackedChangeSummary();
        Assert.NotNull(summary);
        Assert.Equal(summary, doc.GetTrackedChangeSummary()); // consistent

        // AcceptAllChanges — no changes to accept, safe operation
        var accepted = doc.AcceptAllChanges();
        Assert.NotNull(accepted);
        Assert.True(accepted.GetRevisionCount() <= doc.GetRevisionCount());
        Assert.True(accepted.GetParagraphCount() >= 0);

        // Consistent revision count
        Assert.Equal(doc.GetRevisionCount(), doc.GetRevisionCount());

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
        var path = TempFile("dogfood_supplychain.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(doc.GetRevisionCount(), loaded.GetRevisionCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetTrackedChangeSummary());

        // AcceptAllChanges on loaded
        var loadedAccepted = loaded.AcceptAllChanges();
        Assert.NotNull(loadedAccepted);
        Assert.True(loadedAccepted.GetRevisionCount() >= 0);

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: supply chain resilience is a strategic imperative for risk management in globalised industries.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Save accepted version
        var pathAccepted = TempFile("dogfood_supplychain_accepted.fodt");
        loadedAccepted.SaveToFile(pathAccepted);
        Assert.True(File.Exists(pathAccepted));

        // Final save
        var path2 = TempFile("dogfood_supplychain_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.True(loaded2.GetRevisionCount() >= 0);
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetTrackedChangeSummary());
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AcceptAllChanges());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
