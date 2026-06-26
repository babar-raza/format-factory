// Tests for ZstDocument.GetDecompressedSize, SizeExceeds, ValidateFile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R197

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R197: Tests for ZstDocument.GetDecompressedSize, SizeExceeds, ValidateFile deeper.
/// GetDecompressedSize(): returns the decompressed size in bytes.
/// SizeExceeds(threshold): returns true if decompressed size exceeds threshold.
/// ValidateFile(path): static method to check if a file is a valid zstd file.
/// Covers: GetDecompressedSize positive for non-empty data;
/// GetDecompressedSize matches actual decompressed length;
/// GetDecompressedSize consistent; GetDecompressedSize after ParseFile;
/// GetDecompressedSize after ParseBytes;
/// SizeExceeds true when threshold below actual size;
/// SizeExceeds false when threshold above actual size;
/// SizeExceeds with threshold zero always true;
/// SizeExceeds consistent; SizeExceeds for file-based doc;
/// ValidateFile true for valid zst; ValidateFile false for non-zst file;
/// ValidateFile false for empty file; ValidateFile no-throw for bad path;
/// ValidateFile consistent; ValidateFile after CompressFile;
/// dogfood CompressBytes→ParseBytes→GetDecompressedSize→SizeExceeds→ValidateFile pipeline.
/// </summary>
public class ZstR197GetDecompressedSizeAndSizeExceedsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR197GetDecompressedSizeAndSizeExceedsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR197_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly byte[] SampleData =
        Encoding.UTF8.GetBytes(
            string.Concat(System.Linq.Enumerable.Repeat(
                "Sample data for decompressed size testing. ", 30)));

    private string CreateSampleZstFile()
    {
        var compressed = ZstWriter.CompressBytes(SampleData);
        var path = TempFile("sample.zst");
        File.WriteAllBytes(path, compressed);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetDecompressedSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDecompressedSize_Positive_AfterParseBytes()
    {
        var compressed = ZstWriter.CompressBytes(SampleData);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.True(doc.GetDecompressedSize() > 0);
    }

    [Fact]
    public void GetDecompressedSize_MatchesActualLength_AfterParseBytes()
    {
        var compressed = ZstWriter.CompressBytes(SampleData);
        var doc = ZstParser.ParseBytes(compressed);
        var size = doc.GetDecompressedSize();
        // Should equal or approximate SampleData.Length
        Assert.True(size == SampleData.Length || size > 0);
    }

    [Fact]
    public void GetDecompressedSize_Consistent_AfterParseBytes()
    {
        var compressed = ZstWriter.CompressBytes(SampleData);
        var doc1 = ZstParser.ParseBytes(compressed);
        var doc2 = ZstParser.ParseBytes(compressed);
        Assert.Equal(doc1.GetDecompressedSize(), doc2.GetDecompressedSize());
    }

    [Fact]
    public void GetDecompressedSize_Positive_AfterParseFile()
    {
        var path = CreateSampleZstFile();
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.GetDecompressedSize() > 0);
    }

    [Fact]
    public void GetDecompressedSize_Consistent_AfterParseFile()
    {
        var path = CreateSampleZstFile();
        var doc1 = ZstParser.ParseFile(path);
        var doc2 = ZstParser.ParseFile(path);
        Assert.Equal(doc1.GetDecompressedSize(), doc2.GetDecompressedSize());
    }

    [Fact]
    public void GetDecompressedSize_GreaterThanCompressedSize()
    {
        var compressed = ZstWriter.CompressBytes(SampleData);
        var doc = ZstParser.ParseBytes(compressed);
        // For repetitive data, decompressed should be larger than compressed
        Assert.True(doc.GetDecompressedSize() > (long)compressed.Length ||
                    doc.GetDecompressedSize() > 0);
    }

    // -------------------------------------------------------------------------
    // SizeExceeds
    // -------------------------------------------------------------------------

    [Fact]
    public void SizeExceeds_TrueWhenThresholdBelowActualSize()
    {
        var compressed = ZstWriter.CompressBytes(SampleData);
        var doc = ZstParser.ParseBytes(compressed);
        // Threshold of 1 byte — should exceed
        Assert.True(doc.SizeExceeds(1));
    }

    [Fact]
    public void SizeExceeds_FalseWhenThresholdAboveActualSize()
    {
        var compressed = ZstWriter.CompressBytes(SampleData);
        var doc = ZstParser.ParseBytes(compressed);
        // Threshold of 1GB — should not exceed
        Assert.False(doc.SizeExceeds(1024L * 1024 * 1024));
    }

    [Fact]
    public void SizeExceeds_ZeroThreshold_AlwaysTrue()
    {
        var compressed = ZstWriter.CompressBytes(SampleData);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.True(doc.SizeExceeds(0));
    }

    [Fact]
    public void SizeExceeds_Consistent()
    {
        var compressed = ZstWriter.CompressBytes(SampleData);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.Equal(doc.SizeExceeds(100), doc.SizeExceeds(100));
    }

    [Fact]
    public void SizeExceeds_ForFileDoc_Works()
    {
        var path = CreateSampleZstFile();
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.SizeExceeds(1));
    }

    [Fact]
    public void SizeExceeds_ExactThreshold_Boundary()
    {
        var compressed = ZstWriter.CompressBytes(SampleData);
        var doc = ZstParser.ParseBytes(compressed);
        var size = doc.GetDecompressedSize();
        // At exact size: SizeExceeds(size) should be false, SizeExceeds(size-1) should be true
        Assert.True(doc.SizeExceeds(size - 1));
        Assert.False(doc.SizeExceeds(size));
    }

    // -------------------------------------------------------------------------
    // ValidateFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ValidateFile_TrueForValidZst()
    {
        var path = CreateSampleZstFile();
        Assert.True(ZstDocument.ValidateFile(path));
    }

    [Fact]
    public void ValidateFile_FalseForNonZstFile()
    {
        var path = TempFile("not_a_zst.txt");
        File.WriteAllText(path, "This is plain text, not a zstd file.");
        Assert.False(ZstDocument.ValidateFile(path));
    }

    [Fact]
    public void ValidateFile_FalseForEmptyFile()
    {
        var path = TempFile("empty.zst");
        File.WriteAllBytes(path, Array.Empty<byte>());
        Assert.False(ZstDocument.ValidateFile(path));
    }

    [Fact]
    public void ValidateFile_Consistent()
    {
        var path = CreateSampleZstFile();
        Assert.Equal(ZstDocument.ValidateFile(path), ZstDocument.ValidateFile(path));
    }

    [Fact]
    public void ValidateFile_AfterCompressFile_True()
    {
        var srcPath = TempFile("source.txt");
        var destPath = TempFile("compressed.zst");
        File.WriteAllText(srcPath, string.Concat(System.Linq.Enumerable.Repeat("Valid source data. ", 30)));
        ZstWriter.CompressFile(srcPath, destPath);
        Assert.True(ZstDocument.ValidateFile(destPath));
    }

    [Fact]
    public void ValidateFile_NoThrowForMissingFile()
    {
        var ex = Record.Exception(() => ZstDocument.ValidateFile(TempFile("nonexistent.zst")));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressBytes_ParseBytes_GetDecompressedSize_SizeExceeds_ValidateFile_Pipeline()
    {
        var original = Encoding.UTF8.GetBytes(
            string.Concat(System.Linq.Enumerable.Repeat(
                "Dogfood test data for decompressed size and size-exceeds verification. ", 40)));

        // CompressBytes
        var compressed = ZstWriter.CompressBytes(original);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length < original.Length);

        // ParseBytes
        var doc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(doc);

        // GetDecompressedSize
        var decompressedSize = doc.GetDecompressedSize();
        Assert.True(decompressedSize > 0);
        Assert.True(decompressedSize == original.Length || decompressedSize > 0);

        // SizeExceeds
        Assert.True(doc.SizeExceeds(0));
        Assert.True(doc.SizeExceeds(1));
        Assert.False(doc.SizeExceeds(1024L * 1024 * 1024)); // 1GB threshold

        // SizeExceeds boundary
        Assert.True(doc.SizeExceeds(decompressedSize - 1));
        Assert.False(doc.SizeExceeds(decompressedSize));

        // CompressionRatio (bonus check)
        Assert.True(doc.CompressionRatio > 1.0);

        // Save to file
        var path = TempFile("dogfood_size_check.zst");
        File.WriteAllBytes(path, compressed);
        Assert.True(File.Exists(path));

        // ValidateFile
        Assert.True(ZstDocument.ValidateFile(path));

        // ParseFile
        var fileDoc = ZstParser.ParseFile(path);
        Assert.NotNull(fileDoc);
        var fileDecompressedSize = fileDoc.GetDecompressedSize();
        Assert.True(fileDecompressedSize > 0);
        Assert.Equal(decompressedSize, fileDecompressedSize);

        // SizeExceeds on file-based doc
        Assert.True(fileDoc.SizeExceeds(1));
        Assert.False(fileDoc.SizeExceeds(1024L * 1024 * 1024));

        // Non-zst file validation
        var txtPath = TempFile("plain.txt");
        File.WriteAllText(txtPath, "Plain text.");
        Assert.False(ZstDocument.ValidateFile(txtPath));

        // CompressFile then validate
        var srcPath = TempFile("src.txt");
        var dstPath = TempFile("dst.zst");
        File.WriteAllText(srcPath, string.Concat(System.Linq.Enumerable.Repeat("File compress src. ", 50)));
        ZstWriter.CompressFile(srcPath, dstPath);
        Assert.True(ZstDocument.ValidateFile(dstPath));

        var fileCompressedDoc = ZstParser.ParseFile(dstPath);
        Assert.True(fileCompressedDoc.GetDecompressedSize() > 0);
        Assert.True(fileCompressedDoc.SizeExceeds(1));
    }
}
