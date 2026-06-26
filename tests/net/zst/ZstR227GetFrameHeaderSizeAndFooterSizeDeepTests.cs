// Tests for ZstDocument.GetFrameHeaderSize, GetFrameFooterSize, GetFrameDataSize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R227

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R227: Tests for ZstDocument.GetFrameHeaderSize, GetFrameFooterSize, GetFrameDataSize deeper.
/// GetFrameHeaderSize(): returns the size in bytes of the Zstandard frame header.
/// GetFrameFooterSize(): returns the size in bytes of the Zstandard frame footer/checksum area.
/// GetFrameDataSize(): returns the size in bytes of compressed data blocks in the frame.
/// Covers: GetFrameHeaderSize no-throw; GetFrameHeaderSize positive; GetFrameHeaderSize consistent;
/// GetFrameHeaderSize save-load; GetFrameHeaderSize leq compressedSize;
/// GetFrameFooterSize no-throw; GetFrameFooterSize non-negative; GetFrameFooterSize consistent;
/// GetFrameFooterSize save-load;
/// GetFrameDataSize no-throw; GetFrameDataSize positive; GetFrameDataSize consistent;
/// GetFrameDataSize save-load; GetFrameDataSize leq compressedSize;
/// dogfood Compress→GetFrameHeaderSize→GetFrameFooterSize→GetFrameDataSize→SaveToFile pipeline.
/// </summary>
public class ZstR227GetFrameHeaderSizeAndFooterSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR227GetFrameHeaderSizeAndFooterSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR227_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateZstFile(string text = "The quick brown fox jumps over the lazy dog. " +
        "Jived fox nymph grabs quick waltz. Glib jocks quiz nymph to vex dwarf!")
    {
        var raw = TempFile("src.txt");
        File.WriteAllText(raw, text);
        var zst = TempFile("src.zst");
        var writer = new ZstWriter();
        writer.CompressFile(raw, zst);
        return zst;
    }

    // -------------------------------------------------------------------------
    // GetFrameHeaderSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameHeaderSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetFrameHeaderSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameHeaderSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetFrameHeaderSize() > 0);
    }

    [Fact]
    public void GetFrameHeaderSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetFrameHeaderSize(), doc.GetFrameHeaderSize());
    }

    [Fact]
    public void GetFrameHeaderSize_LeqCompressedSize()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetFrameHeaderSize() <= doc.GetCompressedSize());
    }

    [Fact]
    public void GetFrameHeaderSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetFrameHeaderSize();
        var path = TempFile("fhs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrameHeaderSize());
    }

    // -------------------------------------------------------------------------
    // GetFrameFooterSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameFooterSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetFrameFooterSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameFooterSize_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetFrameFooterSize() >= 0);
    }

    [Fact]
    public void GetFrameFooterSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetFrameFooterSize(), doc.GetFrameFooterSize());
    }

    [Fact]
    public void GetFrameFooterSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetFrameFooterSize();
        var path = TempFile("ffs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrameFooterSize());
    }

    // -------------------------------------------------------------------------
    // GetFrameDataSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameDataSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetFrameDataSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameDataSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetFrameDataSize() > 0);
    }

    [Fact]
    public void GetFrameDataSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetFrameDataSize(), doc.GetFrameDataSize());
    }

    [Fact]
    public void GetFrameDataSize_LeqCompressedSize()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetFrameDataSize() <= doc.GetCompressedSize());
    }

    [Fact]
    public void GetFrameDataSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetFrameDataSize();
        var path = TempFile("fds_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrameDataSize());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFrameHeaderSize_GetFrameFooterSize_GetFrameDataSize_SaveToFile_Pipeline()
    {
        var content = string.Join("\n", new[]
        {
            "GENOMICS PIPELINE LOG — Batch 20260626",
            "sample_id=GEN001,chromosome=chr1,start=12345,end=12890,depth=42,quality=38.5,variant=SNP",
            "sample_id=GEN002,chromosome=chr3,start=88200,end=88650,depth=37,quality=41.2,variant=INDEL",
            "sample_id=GEN001,chromosome=chr7,start=145000,end=145200,depth=55,quality=44.1,variant=SNP",
            "sample_id=GEN003,chromosome=chrX,start=45600,end=45800,depth=29,quality=35.8,variant=SV",
            "sample_id=GEN002,chromosome=chr12,start=220000,end=220500,depth=48,quality=40.3,variant=SNP",
            "sample_id=GEN004,chromosome=chr2,start=67890,end=68100,depth=61,quality=47.6,variant=CNV",
            "sample_id=GEN003,chromosome=chr15,start=98000,end=98250,depth=33,quality=36.9,variant=SNP",
            "sample_id=GEN001,chromosome=chr19,start=12000,end=12180,depth=52,quality=43.2,variant=INDEL",
            "END_BATCH"
        });

        var raw = TempFile("genomics.txt");
        File.WriteAllText(raw, content);
        var zstPath = TempFile("genomics.zst");
        var writer = new ZstWriter();
        writer.CompressFile(raw, zstPath);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > 0);

        // GetFrameHeaderSize — positive, leq compressed size
        var headerSize = doc.GetFrameHeaderSize();
        Assert.True(headerSize > 0);
        Assert.True(headerSize <= doc.GetCompressedSize());
        Assert.Equal(headerSize, doc.GetFrameHeaderSize()); // consistent

        // GetFrameFooterSize — non-negative
        var footerSize = doc.GetFrameFooterSize();
        Assert.True(footerSize >= 0);
        Assert.Equal(footerSize, doc.GetFrameFooterSize()); // consistent

        // GetFrameDataSize — positive, leq compressed size
        var dataSize = doc.GetFrameDataSize();
        Assert.True(dataSize > 0);
        Assert.True(dataSize <= doc.GetCompressedSize());
        Assert.Equal(dataSize, doc.GetFrameDataSize()); // consistent

        // Cross-checks
        var level = doc.GetCompressionLevel();
        Assert.True(level >= 0);

        var frameCount = doc.GetFrameCount();
        Assert.True(frameCount >= 1);

        // SaveToFile
        var path = TempFile("dogfood_genomics_out.zst");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(headerSize, loaded.GetFrameHeaderSize());
        Assert.Equal(footerSize, loaded.GetFrameFooterSize());
        Assert.Equal(dataSize, loaded.GetFrameDataSize());
        Assert.Equal(doc.GetCompressedSize(), loaded.GetCompressedSize());

        // Compress larger file to verify sizes change
        var largeContent = string.Join("\n", System.Linq.Enumerable.Repeat(content, 10));
        var rawLarge = TempFile("genomics_large.txt");
        File.WriteAllText(rawLarge, largeContent);
        var zstLarge = TempFile("genomics_large.zst");
        writer.CompressFile(rawLarge, zstLarge);
        var docLarge = ZstDocument.LoadFile(zstLarge);
        Assert.True(docLarge.GetCompressedSize() > doc.GetCompressedSize());
        Assert.True(docLarge.GetFrameDataSize() > 0);
        Assert.True(docLarge.GetFrameHeaderSize() > 0);

        // Final save
        var path2 = TempFile("dogfood_genomics_v2.zst");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = ZstDocument.LoadFile(path2);
        Assert.Equal(loaded.GetFrameHeaderSize(), loaded2.GetFrameHeaderSize());
        Assert.Equal(loaded.GetFrameFooterSize(), loaded2.GetFrameFooterSize());
        Assert.Equal(loaded.GetFrameDataSize(), loaded2.GetFrameDataSize());
    }
}
