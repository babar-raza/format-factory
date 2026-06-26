// Tests for ZstDocument.GetBlockSize, GetWindowSize, GetBlockCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R223

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R223: Tests for ZstDocument.GetBlockSize, GetWindowSize, GetBlockCount deeper.
/// GetBlockSize(): returns the size of Zstandard blocks in bytes.
/// GetWindowSize(): returns the Zstandard window size.
/// GetBlockCount(): returns the number of Zstandard blocks in the frame.
/// Covers: GetBlockSize no-throw; GetBlockSize positive; GetBlockSize consistent;
/// GetBlockSize save-load; GetBlockSize leq decompressed size;
/// GetWindowSize no-throw; GetWindowSize positive; GetWindowSize consistent;
/// GetWindowSize save-load; GetWindowSize geq block size;
/// GetBlockCount no-throw; GetBlockCount positive; GetBlockCount consistent;
/// GetBlockCount save-load; GetBlockCount >= 1;
/// dogfood Compress→GetBlockSize→GetWindowSize→GetBlockCount→SaveToFile pipeline.
/// </summary>
public class ZstR223GetBlockSizeAndWindowSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR223GetBlockSizeAndWindowSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR223_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateZstFile(int repeatCount = 50)
    {
        var raw = TempFile("src.txt");
        var line = "The quick brown fox jumps over the lazy dog. 1234567890 ABCDEFGHIJKLMNOPQRSTUVWXYZ\n";
        File.WriteAllText(raw, string.Concat(System.Linq.Enumerable.Repeat(line, repeatCount)));
        var zst = TempFile("src.zst");
        new ZstWriter().CompressFile(raw, zst);
        return zst;
    }

    // -------------------------------------------------------------------------
    // GetBlockSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetBlockSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetBlockSize() > 0);
    }

    [Fact]
    public void GetBlockSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetBlockSize(), doc.GetBlockSize());
    }

    [Fact]
    public void GetBlockSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetBlockSize();
        var path = TempFile("bs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockSize());
    }

    [Fact]
    public void GetBlockSize_Leq_DecompressedSize()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetBlockSize() <= doc.GetDecompressedSize() + 1);
    }

    // -------------------------------------------------------------------------
    // GetWindowSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWindowSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetWindowSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWindowSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetWindowSize() > 0);
    }

    [Fact]
    public void GetWindowSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetWindowSize(), doc.GetWindowSize());
    }

    [Fact]
    public void GetWindowSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetWindowSize();
        var path = TempFile("ws_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetWindowSize());
    }

    [Fact]
    public void GetWindowSize_Geq_BlockSize()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetWindowSize() >= doc.GetBlockSize());
    }

    // -------------------------------------------------------------------------
    // GetBlockCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetBlockCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockCount_AtLeastOne()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetBlockCount() >= 1);
    }

    [Fact]
    public void GetBlockCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetBlockCount(), doc.GetBlockCount());
    }

    [Fact]
    public void GetBlockCount_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetBlockCount();
        var path = TempFile("bc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetBlockSize_GetWindowSize_GetBlockCount_SaveToFile_Pipeline()
    {
        // Large-ish content to ensure non-trivial block structure
        var lines = new System.Text.StringBuilder();
        for (int i = 0; i < 200; i++)
            lines.AppendLine($"LOG[{i:D4}] timestamp={1719360000 + i} level=INFO component=processor msg=\"Processing batch {i} of 200\" items={i * 100} elapsed_ms={i * 12}");

        var raw = TempFile("logstream.txt");
        File.WriteAllText(raw, lines.ToString());
        var zstPath = TempFile("logstream.zst");
        new ZstWriter().CompressFile(raw, zstPath);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > 0);

        // GetBlockSize
        var blockSize = doc.GetBlockSize();
        Assert.True(blockSize > 0);
        Assert.Equal(blockSize, doc.GetBlockSize()); // consistent

        // GetWindowSize
        var windowSize = doc.GetWindowSize();
        Assert.True(windowSize > 0);
        Assert.True(windowSize >= blockSize);
        Assert.Equal(windowSize, doc.GetWindowSize()); // consistent

        // GetBlockCount
        var blockCount = doc.GetBlockCount();
        Assert.True(blockCount >= 1);
        Assert.Equal(blockCount, doc.GetBlockCount()); // consistent

        // Cross-checks
        Assert.True(doc.GetCompressionRatio() > 0);
        Assert.True(doc.GetFrameCount() >= 1);

        // SaveToFile
        var path = TempFile("dogfood_logstream_out.zst");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(blockSize, loaded.GetBlockSize());
        Assert.Equal(windowSize, loaded.GetWindowSize());
        Assert.Equal(blockCount, loaded.GetBlockCount());
        Assert.Equal(doc.GetCompressedSize(), loaded.GetCompressedSize());

        // Final save
        var path2 = TempFile("dogfood_logstream_v2.zst");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = ZstDocument.LoadFile(path2);
        Assert.Equal(loaded.GetBlockSize(), loaded2.GetBlockSize());
        Assert.Equal(loaded.GetWindowSize(), loaded2.GetWindowSize());
        Assert.Equal(loaded.GetBlockCount(), loaded2.GetBlockCount());
    }
}
