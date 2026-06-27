// Tests for FodtDocument.GetCrossReferenceCount, AddCrossReference, GetCrossReferenceTarget deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R322

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R322: Tests for FodtDocument.GetCrossReferenceCount, AddCrossReference, GetCrossReferenceTarget deeper.
/// GetCrossReferenceCount(): returns the number of cross-references in the document.
/// AddCrossReference(paragraphIndex, targetId, displayText): adds a cross-reference to a target.
/// GetCrossReferenceTarget(index): returns the target ID of the cross-reference at the given index.
/// Covers: GetCrossReferenceCount no-throw; GetCrossReferenceCount non-negative; GetCrossReferenceCount consistent;
/// GetCrossReferenceCount zero for new doc; GetCrossReferenceCount after AddCrossReference increases;
/// GetCrossReferenceCount save-load;
/// AddCrossReference no-throw; AddCrossReference increases count; AddCrossReference save-load;
/// AddCrossReference multiple; AddCrossReference then ExportToHtml no-throw;
/// AddCrossReference then ExportToMarkdown no-throw; AddCrossReference then GetCharCount positive;
/// GetCrossReferenceTarget no-throw; GetCrossReferenceTarget non-null; GetCrossReferenceTarget consistent;
/// GetCrossReferenceTarget save-load;
/// dogfood CreateDoc→AddCrossReference→GetCrossReferenceCount→GetCrossReferenceTarget→SaveToFile pipeline.
/// </summary>
public class FodtR322GetCrossReferenceCountAndAddCrossReferenceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR322GetCrossReferenceCountAndAddCrossReferenceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR322_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateTechnicalDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Software Architecture Patterns in Distributed Microservices", 1);
        doc.AppendParagraph("Event-driven architecture decouples service producers and consumers through asynchronous message passing via broker intermediaries.");
        doc.AppendParagraph("The saga pattern coordinates distributed transactions across microservices using compensating transactions for rollback scenarios.");
        doc.InsertHeading(3, "Service Mesh Implementation", 2);
        doc.AppendParagraph("Istio service mesh provides observability, traffic management, and mutual TLS security without application code modifications.");
        doc.AppendParagraph("Circuit breaker patterns prevent cascading failures by failing fast when upstream services exceed error rate or latency thresholds.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCrossReferenceCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCrossReferenceCount_NoThrow()
    {
        var doc = CreateTechnicalDoc();
        var ex = Record.Exception(() => doc.GetCrossReferenceCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCrossReferenceCount_NonNegative()
    {
        var doc = CreateTechnicalDoc();
        Assert.True(doc.GetCrossReferenceCount() >= 0);
    }

    [Fact]
    public void GetCrossReferenceCount_Consistent()
    {
        var doc = CreateTechnicalDoc();
        Assert.Equal(doc.GetCrossReferenceCount(), doc.GetCrossReferenceCount());
    }

    [Fact]
    public void GetCrossReferenceCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with no cross-references.");
        Assert.Equal(0, doc.GetCrossReferenceCount());
    }

    [Fact]
    public void GetCrossReferenceCount_AfterAddCrossReference_Increases()
    {
        var doc = CreateTechnicalDoc();
        var before = doc.GetCrossReferenceCount();
        doc.AddCrossReference(1, "sec:event-driven", "Section 2");
        Assert.Equal(before + 1, doc.GetCrossReferenceCount());
    }

    [Fact]
    public void GetCrossReferenceCount_SaveLoad_Consistent()
    {
        var doc = CreateTechnicalDoc();
        doc.AddCrossReference(2, "sec:saga-pattern", "Section 3");
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
        var doc = CreateTechnicalDoc();
        var ex = Record.Exception(() => doc.AddCrossReference(0, "sec:intro", "Introduction"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddCrossReference_Increases_Count()
    {
        var doc = CreateTechnicalDoc();
        var before = doc.GetCrossReferenceCount();
        doc.AddCrossReference(3, "sec:istio", "see Istio section");
        Assert.Equal(before + 1, doc.GetCrossReferenceCount());
    }

    [Fact]
    public void AddCrossReference_SaveLoad_Persists()
    {
        var doc = CreateTechnicalDoc();
        doc.AddCrossReference(4, "sec:circuit-breaker", "Circuit Breaker Pattern");
        var before = doc.GetCrossReferenceCount();
        var path = TempFile("acr_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCrossReferenceCount());
    }

    [Fact]
    public void AddCrossReference_Multiple()
    {
        var doc = CreateTechnicalDoc();
        doc.AddCrossReference(0, "ref:fig1", "Figure 1");
        doc.AddCrossReference(1, "ref:table2", "Table 2");
        doc.AddCrossReference(3, "ref:appendixA", "Appendix A");
        Assert.Equal(3, doc.GetCrossReferenceCount());
    }

    [Fact]
    public void AddCrossReference_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateTechnicalDoc();
        doc.AddCrossReference(2, "sec:html-test", "HTML test reference");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddCrossReference_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateTechnicalDoc();
        doc.AddCrossReference(1, "sec:md-test", "Markdown test reference");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddCrossReference_Then_GetCharCount_Positive()
    {
        var doc = CreateTechnicalDoc();
        doc.AddCrossReference(0, "sec:char-test", "Char count reference");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetCrossReferenceTarget
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCrossReferenceTarget_NoThrow()
    {
        var doc = CreateTechnicalDoc();
        doc.AddCrossReference(1, "target-001", "See section");
        var ex = Record.Exception(() => doc.GetCrossReferenceTarget(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCrossReferenceTarget_NonNull()
    {
        var doc = CreateTechnicalDoc();
        doc.AddCrossReference(2, "target-002", "See Figure 3");
        Assert.NotNull(doc.GetCrossReferenceTarget(0));
    }

    [Fact]
    public void GetCrossReferenceTarget_Consistent()
    {
        var doc = CreateTechnicalDoc();
        doc.AddCrossReference(0, "target-003", "Consistent reference");
        Assert.Equal(doc.GetCrossReferenceTarget(0), doc.GetCrossReferenceTarget(0));
    }

    [Fact]
    public void GetCrossReferenceTarget_SaveLoad_Consistent()
    {
        var doc = CreateTechnicalDoc();
        doc.AddCrossReference(3, "target-save", "Save-load reference");
        var path = TempFile("crt_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetCrossReferenceTarget(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddCrossReference_GetCrossReferenceCount_GetCrossReferenceTarget_SaveToFile_Pipeline()
    {
        // Technical specification — quantum computing hardware architecture document
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Quantum Computing Hardware Architecture: Superconducting Qubits and Error Correction", 1);
        doc.AppendParagraph("Superconducting transmon qubits achieve coherence times of 100-300 microseconds at operating temperatures of 15 millikelvin.");
        doc.AppendParagraph("Two-qubit gate fidelities exceeding 99.5% are required to achieve fault-tolerant quantum computation with surface code error correction.");

        doc.InsertHeading(3, "Surface Code Implementation", 2);
        doc.AppendParagraph("The surface code requires approximately 1000 physical qubits per logical qubit for error rates of 0.1% per gate operation.");
        doc.AppendParagraph("Syndrome measurement circuits execute stabiliser measurements without disturbing logical qubit state through ancilla qubit coupling.");

        doc.InsertHeading(6, "Qubit Connectivity", 2);
        doc.AppendParagraph("Heavy-hex lattice topology balances qubit connectivity requirements against crosstalk suppression in superconducting architectures.");
        doc.AppendParagraph("Microwave control lines require individual 50Ω coaxial cables per qubit, posing significant scalability challenges beyond 1000 qubits.");

        doc.InsertHeading(9, "Classical Control Stack", 1);
        doc.AppendParagraph("Field-programmable gate arrays execute real-time decoder algorithms processing syndrome measurement data within qubit coherence windows.");
        doc.AppendParagraph("Cryogenic CMOS electronics operating at 4K stage reduce wiring requirements by multiplexing control signals for qubit arrays.");

        Assert.Equal(10, doc.GetParagraphCount());

        // GetCrossReferenceCount — zero initially
        Assert.Equal(0, doc.GetCrossReferenceCount());

        // AddCrossReference — within-document references
        doc.AddCrossReference(1, "sec:coherence", "see coherence time discussion");
        Assert.Equal(1, doc.GetCrossReferenceCount());

        doc.AddCrossReference(2, "sec:surface-code", "see Section 2: Surface Code Implementation");
        Assert.Equal(2, doc.GetCrossReferenceCount());

        doc.AddCrossReference(3, "fig:qubit-overhead", "Figure 3: Physical qubit overhead vs error rate");
        Assert.Equal(3, doc.GetCrossReferenceCount());

        doc.AddCrossReference(5, "sec:connectivity", "see Qubit Connectivity section");
        Assert.Equal(4, doc.GetCrossReferenceCount());

        doc.AddCrossReference(7, "table:latency", "Table 4: Decoder latency requirements");
        Assert.Equal(5, doc.GetCrossReferenceCount());

        doc.AddCrossReference(8, "fig:cryo-stack", "Figure 6: Cryogenic electronics architecture");
        Assert.Equal(6, doc.GetCrossReferenceCount());

        // Consistent
        Assert.Equal(doc.GetCrossReferenceCount(), doc.GetCrossReferenceCount());

        // GetCrossReferenceTarget
        var target0 = doc.GetCrossReferenceTarget(0);
        Assert.NotNull(target0);
        Assert.Equal(target0, doc.GetCrossReferenceTarget(0)); // consistent

        var target3 = doc.GetCrossReferenceTarget(3);
        Assert.NotNull(target3);

        var target5 = doc.GetCrossReferenceTarget(5);
        Assert.NotNull(target5);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // ExportToPlainText
        var plain = doc.ExportToPlainText();
        Assert.NotNull(plain);
        Assert.NotEmpty(plain);

        // GetCharCount and GetWordCount positive
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_quantum_arch.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetCrossReferenceCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetCrossReferenceTarget(0));
        Assert.NotNull(loaded.GetCrossReferenceTarget(5));

        // AddCrossReference on loaded
        loaded.AddCrossReference(9, "app:benchmark-data", "Appendix A: Benchmark Results");
        Assert.Equal(7, loaded.GetCrossReferenceCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: fault-tolerant quantum computing requires co-design of physical qubits, error correction codes, and classical control systems.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_quantum_arch_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetCrossReferenceCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetCrossReferenceTarget(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddCrossReference(0, "ref:final", "Final cross-reference"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
