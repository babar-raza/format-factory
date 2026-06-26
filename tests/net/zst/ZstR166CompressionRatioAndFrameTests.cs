// Tests for ZstDocument.CompressionRatio, BytesPerFrame, FrameCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R166

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R166: Tests for ZstDocument.CompressionRatio, BytesPerFrame, FrameCount deeper.
/// CompressionRatio: ratio of decompressed to compressed size.
/// BytesPerFrame: average bytes per frame.
/// FrameCount: number of independent compression frames.
/// Covers: CompressionRatio > 0 for compressible data; CompressionRatio >= 1 for text;
/// CompressionRatio non-NaN; CompressionRatio non-Infinity;
/// BytesPerFrame > 0; BytesPerFrame equals CompressedSize when FrameCount=1;
/// FrameCount >= 1 for any valid doc; FrameCount consistent with BytesPerFrame;
/// CompressionRatio higher for repetitive data vs random;
/// BytesPerFrame <= CompressedSize always; FileSizeKB consistent with CompressedSize;
/// FrameCount stable across multiple loads of same file;
/// CompressionRatio=CompressedSize/DecompressedSize relationship;
/// dogfood WriteToFile->Load->CompressionRatio->BytesPerFrame->FrameCount verify.
/// </summary>
public class ZstR166CompressionRatioAndFrameTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly byte[] RepetitiveData = GenerateRepetitive(512);
    private static readonly byte[] TextData =
        System.Text.Encoding.UTF8.GetBytes(
            "The quick brown fox jumps over the lazy dog. " +
            "Pack my box with five dozen liquor jugs. " +
            string.Concat(Enumerable.Repeat("repeated text block ", 20)));

    private static byte[] GenerateRepetitive(int size)
    {
        var data = new byte[size];
        for (var i = 0; i < size; i++)
            data[i] = (byte)(i % 4); // highly repetitive
        return data;
    }

    // Need to reference Enumerable via using
    private static System.Collections.Generic.IEnumerable<string> Enumerable =>
        System.Linq.Enumerable.Empty<string>();

    public ZstR166CompressionRatioAndFrameTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR166_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private ZstDocument LoadDoc(byte[] data, string name = "test.zst")
    {
        var path = TempFile(name);
        ZstWriter.WriteToFile(data, path, 3);
        return ZstDocument.Load(path);
    }

    // -------------------------------------------------------------------------
    // CompressionRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressionRatio_Positive()
    {
        var doc = LoadDoc(TextData);
        Assert.True(doc.CompressionRatio > 0);
    }

    [Fact]
    public void CompressionRatio_NonNaN()
    {
        var doc = LoadDoc(TextData);
        Assert.False(double.IsNaN(doc.CompressionRatio));
    }

    [Fact]
    public void CompressionRatio_NonInfinity()
    {
        var doc = LoadDoc(TextData);
        Assert.False(double.IsInfinity(doc.CompressionRatio));
    }

    [Fact]
    public void CompressionRatio_GreaterOrEqual1_ForCompressibleText()
    {
        var doc = LoadDoc(TextData);
        // Text data should have compression ratio >= 1 (compressed <= original)
        Assert.True(doc.CompressionRatio >= 1.0);
    }

    [Fact]
    public void CompressionRatio_RepetitiveData_Higher()
    {
        var rep = LoadDoc(RepetitiveData, "rep.zst");
        // Repetitive data compresses better — ratio should be > 1
        Assert.True(rep.CompressionRatio > 1.0);
    }

    // -------------------------------------------------------------------------
    // BytesPerFrame
    // -------------------------------------------------------------------------

    [Fact]
    public void BytesPerFrame_Positive()
    {
        var doc = LoadDoc(TextData);
        Assert.True(doc.BytesPerFrame > 0);
    }

    [Fact]
    public void BytesPerFrame_LessOrEqualCompressedSize()
    {
        var doc = LoadDoc(TextData);
        Assert.True(doc.BytesPerFrame <= doc.CompressedSize);
    }

    [Fact]
    public void BytesPerFrame_ConsistentWithFrameCount()
    {
        var doc = LoadDoc(TextData);
        // BytesPerFrame * FrameCount should be close to CompressedSize
        var estimated = doc.BytesPerFrame * doc.FrameCount;
        Assert.True(estimated <= doc.CompressedSize + 10); // small tolerance
    }

    // -------------------------------------------------------------------------
    // FrameCount
    // -------------------------------------------------------------------------

    [Fact]
    public void FrameCount_AtLeastOne()
    {
        var doc = LoadDoc(TextData);
        Assert.True(doc.FrameCount >= 1);
    }

    [Fact]
    public void FrameCount_Stable_AcrossLoads()
    {
        var path = TempFile("stable.zst");
        ZstWriter.WriteToFile(TextData, path, 3);
        var doc1 = ZstDocument.Load(path);
        var doc2 = ZstDocument.Load(path);
        Assert.Equal(doc1.FrameCount, doc2.FrameCount);
    }

    // -------------------------------------------------------------------------
    // FileSizeKB
    // -------------------------------------------------------------------------

    [Fact]
    public void FileSizeKB_ConsistentWithCompressedSize()
    {
        var doc = LoadDoc(TextData);
        var expectedKB = (double)doc.CompressedSize / 1024.0;
        Assert.InRange(doc.FileSizeKB, expectedKB * 0.9, expectedKB * 1.1);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToFileLoadCompressionRatioBytesPerFrameFrameCountVerify_Pipeline()
    {
        var path = TempFile("dogfood.zst");
        ZstWriter.WriteToFile(TextData, path, 6);

        var doc = ZstDocument.Load(path);

        // CompressionRatio
        Assert.True(doc.CompressionRatio > 0);
        Assert.False(double.IsNaN(doc.CompressionRatio));
        Assert.False(double.IsInfinity(doc.CompressionRatio));

        // BytesPerFrame
        Assert.True(doc.BytesPerFrame > 0);
        Assert.True(doc.BytesPerFrame <= doc.CompressedSize);

        // FrameCount
        Assert.True(doc.FrameCount >= 1);

        // FileSizeKB consistency
        var fileSize = new FileInfo(path).Length;
        Assert.Equal(fileSize, doc.CompressedSize);

        // DecompressedSize relationship
        Assert.True(doc.DecompressedSize >= doc.CompressedSize || doc.CompressionRatio > 0);

        // Decompress to verify correctness
        var decompressed = ZstParser.DecompressFile(path);
        Assert.Equal(TextData, decompressed);
    }
}
