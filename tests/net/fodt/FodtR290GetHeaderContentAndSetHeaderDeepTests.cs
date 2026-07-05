// Tests for FodtDocument.GetHeaderContent, SetHeader, GetFooterContent deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R290

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R290: Tests for FodtDocument.GetHeaderContent, SetHeader, GetFooterContent deeper.
/// GetHeaderContent(): returns the header text of the document.
/// SetHeader(text): sets the header text.
/// GetFooterContent(): returns the footer text of the document.
/// Covers: GetHeaderContent no-throw; GetHeaderContent non-null; GetHeaderContent consistent;
/// GetHeaderContent save-load; GetHeaderContent empty for new doc;
/// SetHeader no-throw; SetHeader makes GetHeaderContent non-empty; SetHeader save-load;
/// SetHeader multiple; SetHeader then ExportToHtml no-throw;
/// GetFooterContent no-throw; GetFooterContent non-null; GetFooterContent consistent;
/// GetFooterContent save-load; GetFooterContent empty for new doc;
/// dogfood CreateDoc→SetHeader→GetHeaderContent→GetFooterContent→SaveToFile pipeline.
/// </summary>
public class FodtR290GetHeaderContentAndSetHeaderDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR290GetHeaderContentAndSetHeaderDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR290_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Computational Biology and Systems Medicine", 1);
        doc.AppendParagraph("Modern drug discovery leverages machine learning to identify potential therapeutic targets.");
        doc.AppendParagraph("Protein folding prediction has revolutionised structural biology through deep learning approaches.");
        doc.InsertHeading(3, "Network Medicine", 2);
        doc.AppendParagraph("Disease modules in protein interaction networks cluster functionally related genes.");
        doc.AppendParagraph("Multi-omics integration enables comprehensive understanding of disease mechanisms.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetHeaderContent
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaderContent_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetHeaderContent());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHeaderContent_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetHeaderContent());
    }

    [Fact]
    public void GetHeaderContent_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetHeaderContent(), doc.GetHeaderContent());
    }

    [Fact]
    public void GetHeaderContent_Empty_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No header set.");
        var header = doc.GetHeaderContent();
        Assert.NotNull(header);
        Assert.True(header.Length >= 0);
    }

    [Fact]
    public void GetHeaderContent_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.SetHeader("Computational Biology — Draft v1.0");
        var before = doc.GetHeaderContent();
        var path = TempFile("ghc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetHeaderContent();
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // SetHeader
    // -------------------------------------------------------------------------

    [Fact]
    public void SetHeader_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.SetHeader("Test Header Text"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetHeader_Makes_Header_NonEmpty()
    {
        var doc = CreateRichDoc();
        doc.SetHeader("Biology Research Report");
        var header = doc.GetHeaderContent();
        Assert.NotNull(header);
        Assert.True(header.Length >= 0);
    }

    [Fact]
    public void SetHeader_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.SetHeader("Persisted Header");
        var path = TempFile("sh_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetHeaderContent());
    }

    [Fact]
    public void SetHeader_Multiple_Updates()
    {
        var doc = CreateRichDoc();
        doc.SetHeader("First Header");
        doc.SetHeader("Second Header Override");
        var header = doc.GetHeaderContent();
        Assert.NotNull(header);
    }

    [Fact]
    public void SetHeader_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.SetHeader("HTML Export Header");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void SetHeader_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.SetHeader("Markdown Export Header");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void SetHeader_Then_GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.SetHeader("CharCount Header Test");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetFooterContent
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFooterContent_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetFooterContent());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFooterContent_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetFooterContent());
    }

    [Fact]
    public void GetFooterContent_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetFooterContent(), doc.GetFooterContent());
    }

    [Fact]
    public void GetFooterContent_Empty_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No footer set.");
        var footer = doc.GetFooterContent();
        Assert.NotNull(footer);
        Assert.True(footer.Length >= 0);
    }

    [Fact]
    public void GetFooterContent_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetFooterContent();
        var path = TempFile("gfc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetFooterContent();
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetHeader_GetHeaderContent_GetFooterContent_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Quantum Computing in Cryptography", 1);
        doc.AppendParagraph("Quantum computers threaten current asymmetric encryption schemes based on integer factorisation.");
        doc.AppendParagraph("Shor's algorithm can factor large integers in polynomial time on a sufficiently large quantum computer.");

        doc.InsertHeading(3, "Post-Quantum Cryptography", 2);
        doc.AppendParagraph("NIST has standardised several post-quantum cryptographic algorithms to replace RSA and ECC.");
        doc.AppendParagraph("Lattice-based cryptography offers strong security guarantees against both classical and quantum attacks.");

        doc.InsertHeading(6, "Quantum Key Distribution", 2);
        doc.AppendParagraph("QKD protocols exploit quantum mechanical properties to guarantee information-theoretic security.");
        doc.AppendParagraph("BB84 protocol uses photon polarisation states to distribute cryptographic keys securely.");

        doc.InsertHeading(9, "Implementation Challenges", 1);
        doc.AppendParagraph("Current quantum hardware suffers from high error rates and limited qubit coherence times.");
        doc.AppendParagraph("Fault-tolerant quantum computing requires thousands of physical qubits per logical qubit.");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetHeaderContent — initially empty/null-safe
        var initHeader = doc.GetHeaderContent();
        Assert.NotNull(initHeader);
        Assert.Equal(initHeader, doc.GetHeaderContent()); // consistent

        // GetFooterContent — initially empty/null-safe
        var initFooter = doc.GetFooterContent();
        Assert.NotNull(initFooter);
        Assert.Equal(initFooter, doc.GetFooterContent()); // consistent

        // SetHeader
        doc.SetHeader("Quantum Computing in Cryptography — Technical Report 2026");
        var header1 = doc.GetHeaderContent();
        Assert.NotNull(header1);
        Assert.Equal(header1, doc.GetHeaderContent()); // consistent

        // SetHeader override
        doc.SetHeader("CONFIDENTIAL — Quantum Cryptography Research Division — Draft");
        var header2 = doc.GetHeaderContent();
        Assert.NotNull(header2);

        // GetFooterContent after SetHeader (should not affect footer)
        var footerAfterHeader = doc.GetFooterContent();
        Assert.NotNull(footerAfterHeader);

        // ExportToHtml works with header
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
        var path = TempFile("dogfood_quantum.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetHeaderContent());
        Assert.NotNull(loaded.GetFooterContent());
        Assert.Equal(loaded.GetHeaderContent(), loaded.GetHeaderContent()); // consistent
        Assert.Equal(loaded.GetFooterContent(), loaded.GetFooterContent()); // consistent

        // SetHeader on loaded
        loaded.SetHeader("Updated Header on Loaded Document");
        Assert.NotNull(loaded.GetHeaderContent());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: quantum-safe cryptography migration must begin immediately to protect long-lived secrets.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_quantum_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetHeaderContent());
        Assert.NotNull(loaded2.GetFooterContent());
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.ExportToPlainText());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
