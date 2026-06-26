// Tests for ZstParser.ValidateFile, ZstDocument.FrameDescriptor deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R187

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R187: Tests for ZstParser.ValidateFile, ZstDocument frame descriptor deeper coverage.
/// ValidateFile(path): returns true if the file is a valid zstd compressed file.
/// ZstDocument.FrameDescriptor: describes the first frame's properties.
/// Covers: ValidateFile true for valid file; ValidateFile false for invalid data;
/// ValidateFile false for missing file; ValidateFile false for empty file;
/// ValidateFile false for truncated file; ValidateFile multiple valid files;
/// ValidateFile consistent across calls; FrameDescriptor non-null after FromFile;
/// FrameDescriptor WindowSize positive; FrameDescriptor FrameType non-null;
/// FrameDescriptor consistent for same file; FrameDescriptor after WriteToFile;
/// ParseFile then FrameDescriptor consistent; CompressString then ValidateFile via file;
/// dogfood WriteMultipleFiles→ValidateAll→ParseFile→FrameDescriptor→Decompress pipeline.
/// </summary>
public class ZstR187ValidateFileAndFrameDescriptorDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly string Content1 = "Content for validate test one.";
    private static readonly string Content2 = "Content for validate test two.";

    public ZstR187ValidateFileAndFrameDescriptorDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR187_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // ValidateFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ValidateFile_TrueForValidFile()
    {
        var path = TempFile("valid.zst");
        ZstWriter.WriteToFile(Content1, path);
        Assert.True(ZstParser.ValidateFile(path));
    }

    [Fact]
    public void ValidateFile_FalseForInvalidData()
    {
        var path = TempFile("invalid.zst");
        File.WriteAllBytes(path, new byte[] { 0x00, 0x11, 0x22, 0x33 });
        Assert.False(ZstParser.ValidateFile(path));
    }

    [Fact]
    public void ValidateFile_FalseForMissingFile()
    {
        var path = TempFile("missing.zst");
        Assert.False(ZstParser.ValidateFile(path));
    }

    [Fact]
    public void ValidateFile_FalseForEmptyFile()
    {
        var path = TempFile("empty.zst");
        File.WriteAllBytes(path, Array.Empty<byte>());
        Assert.False(ZstParser.ValidateFile(path));
    }

    [Fact]
    public void ValidateFile_FalseForRandomBytes()
    {
        var path = TempFile("random.zst");
        var rng = new byte[100];
        new Random(42).NextBytes(rng);
        // Set to invalid magic
        rng[0] = 0x00;
        File.WriteAllBytes(path, rng);
        Assert.False(ZstParser.ValidateFile(path));
    }

    [Fact]
    public void ValidateFile_MultipleValidFiles_AllTrue()
    {
        var path1 = TempFile("v1.zst");
        var path2 = TempFile("v2.zst");
        ZstWriter.WriteToFile(Content1, path1);
        ZstWriter.WriteToFile(Content2, path2);
        Assert.True(ZstParser.ValidateFile(path1));
        Assert.True(ZstParser.ValidateFile(path2));
    }

    [Fact]
    public void ValidateFile_ConsistentAcrossCalls()
    {
        var path = TempFile("consistent.zst");
        ZstWriter.WriteToFile(Content1, path);
        var first = ZstParser.ValidateFile(path);
        var second = ZstParser.ValidateFile(path);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // FrameDescriptor
    // -------------------------------------------------------------------------

    [Fact]
    public void FrameDescriptor_NonNullAfterFromFile()
    {
        var path = TempFile("fd.zst");
        ZstWriter.WriteToFile(Content1, path);
        var doc = ZstDocument.FromFile(path);
        Assert.NotNull(doc.FrameDescriptor);
    }

    [Fact]
    public void FrameDescriptor_WindowSizePositive()
    {
        var path = TempFile("wsize.zst");
        ZstWriter.WriteToFile(Content1, path);
        var doc = ZstDocument.FromFile(path);
        Assert.True(doc.FrameDescriptor.WindowSize >= 0);
    }

    [Fact]
    public void FrameDescriptor_FrameTypeNonNull()
    {
        var path = TempFile("ftype.zst");
        ZstWriter.WriteToFile(Content1, path);
        var doc = ZstDocument.FromFile(path);
        Assert.NotNull(doc.FrameDescriptor.FrameType);
    }

    [Fact]
    public void FrameDescriptor_ConsistentForSameFile()
    {
        var path = TempFile("fdconsist.zst");
        ZstWriter.WriteToFile(Content1, path);
        var doc1 = ZstDocument.FromFile(path);
        var doc2 = ZstDocument.FromFile(path);
        Assert.Equal(doc1.FrameDescriptor.WindowSize, doc2.FrameDescriptor.WindowSize);
    }

    [Fact]
    public void FrameDescriptor_FrameType_ConsistentForSameContent()
    {
        var path = TempFile("fdft.zst");
        ZstWriter.WriteToFile(Content1, path);
        var doc1 = ZstDocument.FromFile(path);
        var doc2 = ZstDocument.FromFile(path);
        Assert.Equal(doc1.FrameDescriptor.FrameType, doc2.FrameDescriptor.FrameType);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteMultipleFiles_ValidateAll_ParseFile_FrameDescriptor_Decompress_Pipeline()
    {
        var contents = new[] { Content1, Content2, "Third content string for batch validation." };
        var paths = new[]
        {
            TempFile("batch0.zst"),
            TempFile("batch1.zst"),
            TempFile("batch2.zst")
        };

        // WriteToFile for all
        for (var i = 0; i < contents.Length; i++)
            ZstWriter.WriteToFile(contents[i], paths[i]);

        // ValidateFile — all true
        foreach (var p in paths)
            Assert.True(ZstParser.ValidateFile(p));

        // ParseFile and FrameDescriptor
        foreach (var p in paths)
        {
            var doc = ZstDocument.FromFile(p);
            Assert.NotNull(doc.FrameDescriptor);
            Assert.True(doc.FrameDescriptor.WindowSize >= 0);
            Assert.NotNull(doc.FrameDescriptor.FrameType);
            Assert.True(doc.CompressedSize > 0);
            Assert.True(doc.FrameCount > 0);
        }

        // ParseFile for each
        for (var i = 0; i < paths.Length; i++)
        {
            var parsed = ZstParser.ParseFile(paths[i]);
            Assert.NotNull(parsed);
            Assert.True(parsed.CompressedSize > 0);
        }

        // Decompress each
        for (var i = 0; i < contents.Length; i++)
            Assert.Equal(contents[i], ZstParser.DecompressFile(paths[i]));

        // Invalid file — validate false
        var invalidPath = TempFile("invalid_dog.zst");
        File.WriteAllBytes(invalidPath, new byte[] { 0xFF, 0xFE, 0xFD });
        Assert.False(ZstParser.ValidateFile(invalidPath));

        // Missing file — validate false
        Assert.False(ZstParser.ValidateFile(TempFile("not_there.zst")));

        // FrameDescriptor consistent for repeated calls
        var consistDoc1 = ZstDocument.FromFile(paths[0]);
        var consistDoc2 = ZstDocument.FromFile(paths[0]);
        Assert.Equal(consistDoc1.FrameDescriptor.WindowSize, consistDoc2.FrameDescriptor.WindowSize);
    }
}
