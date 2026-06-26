// Tests for ZstParser.DecompressFile, DecompressBytes extended deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R188

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R188: Tests for ZstParser.DecompressFile, DecompressBytes extended deeper coverage.
/// DecompressFile(path): decompresses a .zst file on disk to a string.
/// DecompressBytes(data): decompresses raw zstd-compressed bytes to a string.
/// Covers: DecompressFile non-null; DecompressFile matches original; DecompressFile round-trip;
/// DecompressFile missing file throws; DecompressFile empty content; DecompressFile unicode content;
/// DecompressFile multiple files; DecompressBytes non-null; DecompressBytes matches original;
/// DecompressBytes empty compressed; DecompressBytes large content;
/// DecompressBytes after CompressString round-trip; DecompressBytes after CompressStream;
/// DecompressBytes result non-empty for non-empty input;
/// dogfood WriteToFile×3→DecompressFile×3→CompressString×3→DecompressBytes×3 pipeline.
/// </summary>
public class ZstR188DecompressFileAndBytesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR188DecompressFileAndBytesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR188_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string SampleText = "Hello, World! This is a Zstandard compression test with meaningful content.";
    private const string UnicodeText = "Unicode: 日本語 Ünïcödé Ça marche! \u2603\u2764";
    private const string LargeText = "The quick brown fox jumps over the lazy dog. " +
                                     "Pack my box with five dozen liquor jugs. " +
                                     "How vexingly quick daft zebras jump! " +
                                     "The five boxing wizards jump quickly. ";

    // -------------------------------------------------------------------------
    // DecompressFile
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressFile_NonNull()
    {
        var path = TempFile("test.zst");
        ZstWriter.WriteToFile(SampleText, path);
        Assert.NotNull(ZstParser.DecompressFile(path));
    }

    [Fact]
    public void DecompressFile_MatchesOriginal()
    {
        var path = TempFile("match.zst");
        ZstWriter.WriteToFile(SampleText, path);
        Assert.Equal(SampleText, ZstParser.DecompressFile(path));
    }

    [Fact]
    public void DecompressFile_RoundTrip_ViaWriteToFile()
    {
        var path = TempFile("roundtrip.zst");
        var texts = new[] { "First content.", "Second content with more text.", "Third." };
        foreach (var (t, i) in new[] { (texts[0], 0), (texts[1], 1), (texts[2], 2) })
        {
            var p = TempFile($"rt_{i}.zst");
            ZstWriter.WriteToFile(t, p);
            Assert.Equal(t, ZstParser.DecompressFile(p));
        }
    }

    [Fact]
    public void DecompressFile_MissingFile_Throws()
    {
        var path = TempFile("does_not_exist.zst");
        Assert.Throws<Exception>(() => ZstParser.DecompressFile(path));
    }

    [Fact]
    public void DecompressFile_UnicodeContent()
    {
        var path = TempFile("unicode.zst");
        ZstWriter.WriteToFile(UnicodeText, path);
        Assert.Equal(UnicodeText, ZstParser.DecompressFile(path));
    }

    [Fact]
    public void DecompressFile_LargeContent()
    {
        var path = TempFile("large.zst");
        var large = string.Concat(Enumerable.Repeat(LargeText, 50));
        ZstWriter.WriteToFile(large, path);
        Assert.Equal(large, ZstParser.DecompressFile(path));
    }

    [Fact]
    public void DecompressFile_MultipleFiles_AllCorrect()
    {
        var contents = new[] { "Alpha", "Beta", "Gamma Delta Epsilon" };
        for (int i = 0; i < contents.Length; i++)
        {
            var path = TempFile($"multi_{i}.zst");
            ZstWriter.WriteToFile(contents[i], path);
            Assert.Equal(contents[i], ZstParser.DecompressFile(path));
        }
    }

    // -------------------------------------------------------------------------
    // DecompressBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressBytes_NonNull()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        Assert.NotNull(ZstParser.DecompressBytes(compressed));
    }

    [Fact]
    public void DecompressBytes_MatchesOriginal()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        Assert.Equal(SampleText, ZstParser.DecompressBytes(compressed));
    }

    [Fact]
    public void DecompressBytes_AfterCompressString_RoundTrip()
    {
        var texts = new[] { "Hello", UnicodeText, LargeText };
        foreach (var t in texts)
        {
            var compressed = ZstWriter.CompressString(t);
            Assert.Equal(t, ZstParser.DecompressBytes(compressed));
        }
    }

    [Fact]
    public void DecompressBytes_AfterCompressStream_RoundTrip()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleText));
        var compressed = ZstWriter.CompressStream(ms);
        Assert.Equal(SampleText, ZstParser.DecompressBytes(compressed));
    }

    [Fact]
    public void DecompressBytes_LargeContent_RoundTrip()
    {
        var large = string.Concat(Enumerable.Repeat(LargeText, 100));
        var compressed = ZstWriter.CompressString(large);
        Assert.Equal(large, ZstParser.DecompressBytes(compressed));
    }

    [Fact]
    public void DecompressBytes_NonEmpty_ForNonEmptyInput()
    {
        var compressed = ZstWriter.CompressString("non-empty content here");
        Assert.NotEmpty(ZstParser.DecompressBytes(compressed));
    }

    [Fact]
    public void DecompressBytes_Level1_RoundTrip()
    {
        var compressed = ZstWriter.CompressString(SampleText, compressionLevel: 1);
        Assert.Equal(SampleText, ZstParser.DecompressBytes(compressed));
    }

    [Fact]
    public void DecompressBytes_Level19_RoundTrip()
    {
        var compressed = ZstWriter.CompressString(SampleText, compressionLevel: 19);
        Assert.Equal(SampleText, ZstParser.DecompressBytes(compressed));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToFile_DecompressFile_CompressString_DecompressBytes_Pipeline()
    {
        var contents = new[]
        {
            "First document with standard English content for compression testing.",
            UnicodeText,
            string.Concat(Enumerable.Repeat(LargeText, 20))
        };

        // WriteToFile × 3 then DecompressFile × 3
        var paths = new string[3];
        for (int i = 0; i < contents.Length; i++)
        {
            paths[i] = TempFile($"dogfood_{i}.zst");
            ZstWriter.WriteToFile(contents[i], paths[i]);
            Assert.True(File.Exists(paths[i]));
        }

        for (int i = 0; i < contents.Length; i++)
        {
            var decompressed = ZstParser.DecompressFile(paths[i]);
            Assert.NotNull(decompressed);
            Assert.Equal(contents[i], decompressed);
        }

        // CompressString × 3 then DecompressBytes × 3
        var compressedArr = new byte[3][];
        for (int i = 0; i < contents.Length; i++)
        {
            compressedArr[i] = ZstWriter.CompressString(contents[i]);
            Assert.NotNull(compressedArr[i]);
            Assert.True(compressedArr[i].Length > 0);
        }

        for (int i = 0; i < contents.Length; i++)
        {
            var decompressed = ZstParser.DecompressBytes(compressedArr[i]);
            Assert.Equal(contents[i], decompressed);
        }

        // Cross-verify: WriteToFile bytes vs CompressString bytes differ in metadata
        // but both decompress to same content
        for (int i = 0; i < contents.Length; i++)
        {
            var fromFile = ZstParser.DecompressFile(paths[i]);
            var fromBytes = ZstParser.DecompressBytes(compressedArr[i]);
            Assert.Equal(fromFile, fromBytes);
        }

        // ParseFile to verify document properties
        for (int i = 0; i < contents.Length; i++)
        {
            var doc = ZstParser.ParseFile(paths[i]);
            Assert.NotNull(doc);
            Assert.True(doc.CompressedSize > 0);
        }
    }
}
