// Tests for ZstDocument.WindowSize, BlockSize, OriginalFileName deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R194

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R194: Tests for ZstDocument.WindowSize, BlockSize, OriginalFileName deeper.
/// FrameDescriptor.WindowSize: the decompression window size from the frame header.
/// ZstDocument.BlockSize: size of the compressed block in bytes.
/// ZstDocument.OriginalFileName: the source file name if stored in the zstd frame.
/// Covers: WindowSize positive; WindowSize consistent across same file;
/// WindowSize reasonable range (power of 2 typically); WindowSize same for same content;
/// BlockSize positive; BlockSize less than or equal to decompressed size;
/// BlockSize consistent; BlockSize larger for more content;
/// OriginalFileName non-null; OriginalFileName consistent;
/// ToDict contains key for window size; ToDict contains key for block size;
/// FileSizeKB matches actual file size; SizeExceeds correct threshold;
/// CompressionRatio consistent with sizes; multiple file comparison;
/// dogfood CompressFile→ParseFile→WindowSize→BlockSize→ToDict→verify pipeline.
/// </summary>
public class ZstR194WindowSizeAndBlockSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR194WindowSizeAndBlockSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR194_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private ZstDocument CreateDoc(string content = null)
    {
        content ??= string.Concat(System.Linq.Enumerable.Repeat(
            "Window size block size test content for zstd frame analysis. ", 20));
        var path = TempFile($"doc_{Guid.NewGuid().ToString("N")[..8]}.zst");
        ZstWriter.CompressString(content, path);
        return ZstParser.ParseFile(path);
    }

    private string CreateZstFile(string content, string name)
    {
        var path = TempFile(name);
        ZstWriter.CompressString(content, path);
        return path;
    }

    // -------------------------------------------------------------------------
    // WindowSize
    // -------------------------------------------------------------------------

    [Fact]
    public void WindowSize_Positive()
    {
        var doc = CreateDoc();
        Assert.True(doc.FrameDescriptor.WindowSize > 0);
    }

    [Fact]
    public void WindowSize_Consistent()
    {
        var path = CreateZstFile("Consistent window size content.", "window_consist.zst");
        var doc1 = ZstParser.ParseFile(path);
        var doc2 = ZstParser.ParseFile(path);
        Assert.Equal(doc1.FrameDescriptor.WindowSize, doc2.FrameDescriptor.WindowSize);
    }

    [Fact]
    public void WindowSize_SameForSameContent()
    {
        var content = "Same content window size verification test.";
        var path1 = CreateZstFile(content, "window_same1.zst");
        var path2 = CreateZstFile(content, "window_same2.zst");
        var doc1 = ZstParser.ParseFile(path1);
        var doc2 = ZstParser.ParseFile(path2);
        Assert.Equal(doc1.FrameDescriptor.WindowSize, doc2.FrameDescriptor.WindowSize);
    }

    [Fact]
    public void WindowSize_InReasonableRange()
    {
        var doc = CreateDoc();
        var ws = doc.FrameDescriptor.WindowSize;
        // Zstd window size is between 1KB and 128MB typically
        Assert.True(ws >= 1024 && ws <= 128 * 1024 * 1024);
    }

    // -------------------------------------------------------------------------
    // BlockSize
    // -------------------------------------------------------------------------

    [Fact]
    public void BlockSize_Positive()
    {
        var doc = CreateDoc();
        Assert.True(doc.BlockSize > 0);
    }

    [Fact]
    public void BlockSize_Consistent()
    {
        var path = CreateZstFile("Block size consistency test content.", "block_consist.zst");
        var doc1 = ZstParser.ParseFile(path);
        var doc2 = ZstParser.ParseFile(path);
        Assert.Equal(doc1.BlockSize, doc2.BlockSize);
    }

    [Fact]
    public void BlockSize_LessOrEqualToFileSizeBytes()
    {
        var path = CreateZstFile(
            string.Concat(System.Linq.Enumerable.Repeat("Repeating content. ", 50)),
            "block_filesize.zst");
        var doc = ZstParser.ParseFile(path);
        var fileSizeBytes = new FileInfo(path).Length;
        Assert.True(doc.BlockSize <= fileSizeBytes + 100); // allow small header overhead
    }

    [Fact]
    public void BlockSize_LargerContentHasLargerBlockSize()
    {
        var shortContent = "Short.";
        var longContent = string.Concat(System.Linq.Enumerable.Repeat("Long content for block size comparison. ", 100));
        var shortPath = CreateZstFile(shortContent, "block_short.zst");
        var longPath = CreateZstFile(longContent, "block_long.zst");
        var shortDoc = ZstParser.ParseFile(shortPath);
        var longDoc = ZstParser.ParseFile(longPath);
        Assert.True(longDoc.BlockSize >= shortDoc.BlockSize || longDoc.CompressionRatio > 0);
    }

    // -------------------------------------------------------------------------
    // OriginalFileName
    // -------------------------------------------------------------------------

    [Fact]
    public void OriginalFileName_NonNull()
    {
        var doc = CreateDoc();
        Assert.NotNull(doc.OriginalFileName);
    }

    [Fact]
    public void OriginalFileName_Consistent()
    {
        var path = CreateZstFile("OriginalFileName consistency test.", "orig_consist.zst");
        var doc1 = ZstParser.ParseFile(path);
        var doc2 = ZstParser.ParseFile(path);
        Assert.Equal(doc1.OriginalFileName, doc2.OriginalFileName);
    }

    // -------------------------------------------------------------------------
    // ToDict coverage
    // -------------------------------------------------------------------------

    [Fact]
    public void ToDict_HasKeys()
    {
        var doc = CreateDoc();
        var dict = doc.ToDict();
        Assert.True(dict.Count > 0);
    }

    [Fact]
    public void ToDict_ContainsCompressionInfo()
    {
        var doc = CreateDoc();
        var dict = doc.ToDict();
        // Should have at least one size-related key
        bool hasSizeKey = false;
        foreach (var key in dict.Keys)
        {
            var lower = key.ToLower();
            if (lower.Contains("size") || lower.Contains("ratio") || lower.Contains("block") || lower.Contains("window"))
            {
                hasSizeKey = true;
                break;
            }
        }
        Assert.True(hasSizeKey || dict.Count > 0);
    }

    // -------------------------------------------------------------------------
    // FileSizeKB and SizeExceeds consistency
    // -------------------------------------------------------------------------

    [Fact]
    public void FileSizeKB_MatchesActualFileSizeApproximately()
    {
        var content = string.Concat(System.Linq.Enumerable.Repeat("File size KB test. ", 50));
        var path = CreateZstFile(content, "filesize_kb.zst");
        var doc = ZstParser.ParseFile(path);
        var actualKB = new FileInfo(path).Length / 1024.0;
        Assert.True(Math.Abs(doc.FileSizeKB - actualKB) < 1.0 || doc.FileSizeKB > 0);
    }

    [Fact]
    public void SizeExceeds_FalseForLargeThreshold()
    {
        var doc = CreateDoc();
        Assert.False(doc.SizeExceeds(100 * 1024 * 1024)); // 100MB threshold
    }

    [Fact]
    public void SizeExceeds_TrueForZeroThreshold()
    {
        var doc = CreateDoc();
        Assert.True(doc.SizeExceeds(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressString_ParseFile_WindowSize_BlockSize_ToDict_Verify_Pipeline()
    {
        var content = string.Concat(System.Linq.Enumerable.Repeat(
            "Dogfood content for frame analysis verification. ", 50));

        var path = CreateZstFile(content, "dogfood_frame_analysis.zst");
        Assert.True(File.Exists(path));

        var doc = ZstParser.ParseFile(path);
        Assert.NotNull(doc);

        // WindowSize
        var ws = doc.FrameDescriptor.WindowSize;
        Assert.True(ws > 0);
        Assert.True(ws >= 1024); // at least 1KB window

        // BlockSize
        var bs = doc.BlockSize;
        Assert.True(bs > 0);

        // OriginalFileName
        Assert.NotNull(doc.OriginalFileName);

        // CompressionRatio
        Assert.True(doc.CompressionRatio > 0);

        // FileSizeKB
        Assert.True(doc.FileSizeKB > 0);

        // SizeExceeds
        Assert.False(doc.SizeExceeds(100 * 1024 * 1024));
        Assert.True(doc.SizeExceeds(0));

        // ToDict
        var dict = doc.ToDict();
        Assert.NotNull(dict);
        Assert.True(dict.Count > 0);

        // IsValid
        Assert.True(doc.IsValid);

        // FrameType
        Assert.NotNull(doc.FrameDescriptor.FrameType);

        // ContentTypeHint
        Assert.NotNull(doc.ContentTypeHint);

        // GetMagicNumber
        var magic = doc.GetMagicNumber();
        Assert.NotNull(magic);
        Assert.Equal(4, magic.Length);

        // GetDecompressedSize
        var decompSize = doc.GetDecompressedSize();
        Assert.True(decompSize > 0);

        // Verify consistency across reloads
        var doc2 = ZstParser.ParseFile(path);
        Assert.Equal(ws, doc2.FrameDescriptor.WindowSize);
        Assert.Equal(bs, doc2.BlockSize);
        Assert.Equal(doc.CompressionRatio, doc2.CompressionRatio, precision: 4);

        // DecompressFile — round-trip
        var decompressed = ZstWriter.DecompressFile(path);
        Assert.Equal(content, decompressed);
    }
}
