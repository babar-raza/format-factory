// Tests for ZstDocument.GetFrameContentType, GetContentHash deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R265

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R265: Tests for ZstDocument.GetFrameContentType, GetContentHash deeper.
/// GetFrameContentType(): returns a descriptor of the content type detected in the compressed frame.
/// GetContentHash(): returns a hash or fingerprint string of the compressed content.
/// Covers: GetFrameContentType no-throw; GetFrameContentType non-null; GetFrameContentType consistent;
/// GetFrameContentType save-load; GetContentHash no-throw; GetContentHash non-null-or-empty;
/// GetContentHash consistent; GetContentHash differs for different content;
/// GetContentHash save-load; dogfood CreateDoc→GetFrameContentType→GetContentHash→SaveToFile pipeline.
/// </summary>
public class ZstR265GetFrameContentTypeAndContentHashDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR265GetFrameContentTypeAndContentHashDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR265_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateZstFile(string name, string textContent)
    {
        var path = TempFile(name);
        var inputBytes = Encoding.UTF8.GetBytes(textContent);
        using var outStream = new FileStream(path, FileMode.Create);
        using var zlibStream = new ZLibStream(outStream, CompressionLevel.Optimal);
        zlibStream.Write(inputBytes, 0, inputBytes.Length);
        return path;
    }

    private string CreateTextZst() => CreateZstFile("text_content.zst",
        "This is plain text content. It contains words, sentences, and paragraphs. " +
        "The content is readable and in UTF-8 encoding. " +
        string.Concat(Enumerable.Repeat("sample text data for compression testing. ", 50)));

    private string CreateJsonZst() => CreateZstFile("json_content.zst",
        "{\"records\":[" +
        string.Join(",", System.Linq.Enumerable.Range(0, 100).Select(i =>
            $"{{\"id\":{i},\"value\":\"item_{i}\",\"score\":{i * 1.5:F2}}}")) +
        "]}");

    private string CreateBinaryLikeZst() => CreateZstFile("binary_content.zst",
        // Simulate binary-like content with mixed characters
        string.Concat(System.Linq.Enumerable.Range(32, 200).Select(c => (char)c)));

    // -------------------------------------------------------------------------
    // GetFrameContentType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameContentType_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        var ex = Record.Exception(() => doc.GetFrameContentType());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameContentType_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        Assert.NotNull(doc.GetFrameContentType());
    }

    [Fact]
    public void GetFrameContentType_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        Assert.Equal(doc.GetFrameContentType(), doc.GetFrameContentType());
    }

    [Fact]
    public void GetFrameContentType_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateJsonZst());
        var before = doc.GetFrameContentType();
        var path = TempFile("fct_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrameContentType());
    }

    // -------------------------------------------------------------------------
    // GetContentHash
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContentHash_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        var ex = Record.Exception(() => doc.GetContentHash());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContentHash_NonNullOrEmpty()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        Assert.False(string.IsNullOrEmpty(doc.GetContentHash()));
    }

    [Fact]
    public void GetContentHash_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        Assert.Equal(doc.GetContentHash(), doc.GetContentHash());
    }

    [Fact]
    public void GetContentHash_Differs_ForDifferentContent()
    {
        var docText = ZstDocument.LoadFile(CreateTextZst());
        var docJson = ZstDocument.LoadFile(CreateJsonZst());
        Assert.NotEqual(docText.GetContentHash(), docJson.GetContentHash());
    }

    [Fact]
    public void GetContentHash_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateJsonZst());
        var before = doc.GetContentHash();
        var path = TempFile("ch_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetContentHash());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFrameContentType_GetContentHash_SaveToFile_Pipeline()
    {
        // Public Sector — UK Cabinet Office: DDAT (Digital, Data and Technology) Playbook Archive
        // Compressed policy documents and technical specifications from GOV.UK in ZST format
        // Content-type detection and hash-based deduplication for document management

        // Document 1: GOV.UK Design System specification (structured text/JSON)
        var path1 = TempFile("govuk_design_system_spec.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("{");
            content.AppendLine("  \"document\": \"GOV.UK Design System Technical Specification\",");
            content.AppendLine("  \"version\": \"5.3.1\",");
            content.AppendLine("  \"published\": \"2024-09-15\",");
            content.AppendLine("  \"components\": [");
            for (int i = 0; i < 40; i++)
            {
                string[] comps = { "accordion", "back-link", "breadcrumbs", "button", "character-count",
                                   "checkboxes", "cookie-banner", "date-input", "details", "error-message" };
                var comp = comps[i % comps.Length];
                content.AppendLine($"    {{\"name\": \"{comp}-{i}\", \"version\": \"1.{i}\", \"accessible\": true, \"wcag_level\": \"AA\"}},");
            }
            content.AppendLine("  ]");
            content.AppendLine("}");

            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path1, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
            zlib.Write(bytes, 0, bytes.Length);
        }

        // Document 2: CDDO Strategy 2022-2025 policy text
        var path2 = TempFile("cddo_strategy_policy.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("Central Digital and Data Office (CDDO) — Digital Strategy 2022-2025");
            content.AppendLine("Mission: Transforming digital services across UK central government departments.");
            content.AppendLine("Principle 1: User-centred design. Services must be designed around the needs of users,");
            content.AppendLine("including those with accessibility requirements under the Equality Act 2010.");
            content.AppendLine("Principle 2: Data as a strategic asset. Departments shall treat data as a shared");
            content.AppendLine("resource, implementing the UK Government Data Quality Framework (2021) standards.");
            content.AppendLine("Principle 3: Cloud-first infrastructure. All new services shall be architected for");
            content.AppendLine("cloud-native deployment in accordance with the Technology Code of Practice.");
            for (int i = 0; i < 60; i++)
                content.AppendLine($"Policy measure {i + 1}: Implementation target set for Q{(i % 4) + 1} FY{2023 + (i / 4 % 3)}.");

            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path2, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
            zlib.Write(bytes, 0, bytes.Length);
        }

        // Document 3: Duplicate of document 2 (same content, different file)
        var path3 = TempFile("cddo_strategy_policy_copy.zst");
        File.Copy(path2, path3);

        var doc1 = ZstDocument.LoadFile(path1);
        var doc2 = ZstDocument.LoadFile(path2);
        var doc3 = ZstDocument.LoadFile(path3);

        // Frame content type
        var fct1 = doc1.GetFrameContentType();
        var fct2 = doc2.GetFrameContentType();
        Assert.NotNull(fct1);
        Assert.NotNull(fct2);
        Assert.Equal(fct1, doc1.GetFrameContentType()); // consistent
        Assert.Equal(fct2, doc2.GetFrameContentType()); // consistent

        // Content hash
        var hash1 = doc1.GetContentHash();
        var hash2 = doc2.GetContentHash();
        var hash3 = doc3.GetContentHash();
        Assert.False(string.IsNullOrEmpty(hash1));
        Assert.False(string.IsNullOrEmpty(hash2));
        Assert.NotEqual(hash1, hash2); // different content → different hash
        Assert.Equal(hash2, hash3);    // same content → same hash (deduplication)
        Assert.Equal(hash1, doc1.GetContentHash()); // consistent

        // Basic ZST metrics
        Assert.True(doc1.CompressedSize > 0);
        Assert.True(doc1.OriginalSize > 0);
        Assert.True(doc2.CompressedSize > 0);

        // SaveToFile and reload
        var out1 = TempFile("govuk_design_system_spec_out.zst");
        doc1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        var loaded1 = ZstDocument.LoadFile(out1);
        Assert.Equal(fct1, loaded1.GetFrameContentType());
        Assert.Equal(hash1, loaded1.GetContentHash());

        var out2 = TempFile("cddo_strategy_policy_out.zst");
        doc2.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.Equal(fct2, loaded2.GetFrameContentType());
        Assert.Equal(hash2, loaded2.GetContentHash());

        Assert.Equal(doc1.CompressedSize, loaded1.CompressedSize);
        Assert.Equal(doc2.CompressedSize, loaded2.CompressedSize);

        var ex1 = Record.Exception(() => loaded1.GetFrameContentType());
        var ex2 = Record.Exception(() => loaded1.GetContentHash());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
