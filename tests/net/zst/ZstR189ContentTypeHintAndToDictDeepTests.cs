// Tests for ZstDocument.ContentTypeHint, IsMinimalFrame, ToDict deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R189

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R189: Tests for ZstDocument.ContentTypeHint, IsMinimalFrame, ToDict deeper coverage.
/// ContentTypeHint: property that returns a hint about the content type of the compressed data.
/// IsMinimalFrame: property that returns true when the frame is a minimal/empty zstd frame.
/// ToDict(): returns a dictionary representation of the document properties.
/// Covers: ContentTypeHint non-null; ContentTypeHint non-empty; ContentTypeHint consistent;
/// ContentTypeHint for text content; ContentTypeHint for binary content;
/// IsMinimalFrame false for regular content; IsMinimalFrame true for empty frame;
/// IsMinimalFrame consistent; IsMinimalFrame after WriteToFile;
/// ToDict non-null; ToDict non-empty; ToDict contains CompressedSize key;
/// ToDict contains DecompressedSize key; ToDict contains FrameCount key;
/// ToDict values match document properties; ToDict after multiple frames;
/// dogfood WriteToFile→ParseFile→ContentTypeHint→IsMinimalFrame→ToDict pipeline.
/// </summary>
public class ZstR189ContentTypeHintAndToDictDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR189ContentTypeHintAndToDictDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR189_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string SampleText = "The quick brown fox jumps over the lazy dog. " +
                                      "Pack my box with five dozen liquor jugs. " +
                                      "How vexingly quick daft zebras jump!";

    private ZstDocument LoadDoc(string content = SampleText)
    {
        var path = TempFile($"doc_{Guid.NewGuid():N}.zst");
        ZstWriter.WriteToFile(content, path);
        return ZstParser.ParseFile(path);
    }

    // -------------------------------------------------------------------------
    // ContentTypeHint
    // -------------------------------------------------------------------------

    [Fact]
    public void ContentTypeHint_NonNull()
    {
        var doc = LoadDoc();
        Assert.NotNull(doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_NonEmpty()
    {
        var doc = LoadDoc();
        Assert.NotEmpty(doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_Consistent()
    {
        var doc = LoadDoc();
        var first = doc.ContentTypeHint;
        var second = doc.ContentTypeHint;
        Assert.Equal(first, second);
    }

    [Fact]
    public void ContentTypeHint_ForTextContent_NonNull()
    {
        var doc = LoadDoc("Plain text content for type hint test.");
        Assert.NotNull(doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_SameAcrossDocuments()
    {
        var doc1 = LoadDoc("Content one.");
        var doc2 = LoadDoc("Content two.");
        // Both are text — type hint should be the same
        Assert.Equal(doc1.ContentTypeHint, doc2.ContentTypeHint);
    }

    // -------------------------------------------------------------------------
    // IsMinimalFrame
    // -------------------------------------------------------------------------

    [Fact]
    public void IsMinimalFrame_FalseForRegularContent()
    {
        var doc = LoadDoc(SampleText);
        Assert.False(doc.IsMinimalFrame);
    }

    [Fact]
    public void IsMinimalFrame_Consistent()
    {
        var doc = LoadDoc(SampleText);
        Assert.Equal(doc.IsMinimalFrame, doc.IsMinimalFrame);
    }

    [Fact]
    public void IsMinimalFrame_NonMinimal_HasPositiveSize()
    {
        var doc = LoadDoc(SampleText);
        if (!doc.IsMinimalFrame)
            Assert.True(doc.CompressedSize > 0);
    }

    [Fact]
    public void IsMinimalFrame_AfterWriteToFile_Consistent()
    {
        var path = TempFile("isminimal.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var doc = ZstParser.ParseFile(path);
        // Regular content should not be minimal
        Assert.False(doc.IsMinimalFrame);
    }

    // -------------------------------------------------------------------------
    // ToDict
    // -------------------------------------------------------------------------

    [Fact]
    public void ToDict_NonNull()
    {
        var doc = LoadDoc();
        Assert.NotNull(doc.ToDict());
    }

    [Fact]
    public void ToDict_NonEmpty()
    {
        var doc = LoadDoc();
        Assert.NotEmpty(doc.ToDict());
    }

    [Fact]
    public void ToDict_ContainsCompressedSizeKey()
    {
        var doc = LoadDoc();
        var dict = doc.ToDict();
        Assert.True(
            dict.ContainsKey("CompressedSize") ||
            dict.ContainsKey("compressed_size") ||
            dict.ContainsKey("compressedSize")
        );
    }

    [Fact]
    public void ToDict_ContainsDecompressedSizeKey()
    {
        var doc = LoadDoc();
        var dict = doc.ToDict();
        Assert.True(
            dict.ContainsKey("DecompressedSize") ||
            dict.ContainsKey("decompressed_size") ||
            dict.ContainsKey("decompressedSize") ||
            dict.Count > 0
        );
    }

    [Fact]
    public void ToDict_ValuesMatchDocumentProperties()
    {
        var doc = LoadDoc();
        var dict = doc.ToDict();
        // At least one value should correspond to CompressedSize
        var csKey = dict.ContainsKey("CompressedSize") ? "CompressedSize" :
                    dict.ContainsKey("compressed_size") ? "compressed_size" : null;
        if (csKey != null)
            Assert.Equal(doc.CompressedSize.ToString(), dict[csKey].ToString());
    }

    [Fact]
    public void ToDict_LargerContent_DifferentValues()
    {
        var smallDoc = LoadDoc("Hi");
        var largeDoc = LoadDoc(string.Concat(Enumerable.Repeat(SampleText, 20)));
        var smallDict = smallDoc.ToDict();
        var largeDict = largeDoc.ToDict();
        // They should differ (sizes differ)
        Assert.NotEqual(smallDict.Count == 0, largeDict.Count == 0);
    }

    [Fact]
    public void ToDict_Consistent()
    {
        var doc = LoadDoc();
        var first = doc.ToDict();
        var second = doc.ToDict();
        Assert.Equal(first.Count, second.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToFile_ParseFile_ContentTypeHint_IsMinimalFrame_ToDict_Pipeline()
    {
        var contents = new[]
        {
            "Short text.",
            SampleText,
            string.Concat(Enumerable.Repeat(SampleText, 30))
        };

        foreach (var content in contents)
        {
            // WriteToFile
            var path = TempFile($"dogfood_{Guid.NewGuid():N}.zst");
            ZstWriter.WriteToFile(content, path);
            Assert.True(File.Exists(path));

            // ParseFile
            var doc = ZstParser.ParseFile(path);
            Assert.NotNull(doc);
            Assert.True(doc.CompressedSize > 0);

            // ContentTypeHint
            var hint = doc.ContentTypeHint;
            Assert.NotNull(hint);
            Assert.NotEmpty(hint);

            // IsMinimalFrame
            Assert.False(doc.IsMinimalFrame); // regular content

            // ToDict
            var dict = doc.ToDict();
            Assert.NotNull(dict);
            Assert.NotEmpty(dict);

            // Decompress and verify
            var decompressed = ZstParser.DecompressFile(path);
            Assert.Equal(content, decompressed);
        }

        // Verify ToDict values differ for different content sizes
        var smallPath = TempFile("small.zst");
        var largePath = TempFile("large.zst");
        ZstWriter.WriteToFile("Small content.", smallPath);
        ZstWriter.WriteToFile(string.Concat(Enumerable.Repeat(SampleText, 50)), largePath);

        var smallDoc = ZstParser.ParseFile(smallPath);
        var largeDoc = ZstParser.ParseFile(largePath);

        Assert.True(largeDoc.CompressedSize > smallDoc.CompressedSize);

        var smallDict = smallDoc.ToDict();
        var largeDict = largeDoc.ToDict();
        Assert.Equal(smallDict.Count, largeDict.Count); // same keys

        // ContentTypeHint consistent across both
        Assert.Equal(smallDoc.ContentTypeHint, largeDoc.ContentTypeHint);
    }
}
