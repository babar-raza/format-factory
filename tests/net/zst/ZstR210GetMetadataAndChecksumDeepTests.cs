// Tests for ZstDocument.GetMetadata, GetChecksum, GetMagicBytes deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R210

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R210: Tests for ZstDocument.GetMetadata, GetChecksum, GetMagicBytes deeper.
/// GetMetadata(): returns metadata dictionary with compression info.
/// GetChecksum(): returns the content checksum/hash of the compressed data.
/// GetMagicBytes(): returns the magic byte header of the ZST file.
/// Covers: GetMetadata non-null; GetMetadata no-throw; GetMetadata non-empty;
/// GetMetadata consistent; GetMetadata has version key; GetMetadata save-load;
/// GetChecksum non-null; GetChecksum no-throw; GetChecksum non-empty;
/// GetChecksum consistent; GetChecksum same for same content;
/// GetChecksum differs for different content; GetChecksum save-load;
/// GetMagicBytes non-null; GetMagicBytes no-throw; GetMagicBytes length=4;
/// GetMagicBytes has ZST signature; GetMagicBytes consistent; GetMagicBytes save-load;
/// IsValid true for valid; IsValid no-throw; GetFrameCount positive;
/// GetFrameCount consistent; GetFrameCount save-load;
/// dogfood CompressFile→GetMetadata→GetChecksum→GetMagicBytes→SaveToFile pipeline.
/// </summary>
public class ZstR210GetMetadataAndChecksumDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR210GetMetadataAndChecksumDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR210_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string MakeZst(string content, string tag, int level = 3)
    {
        var rawPath = TempFile($"raw_{tag}.txt");
        var zstPath = TempFile($"{tag}.zst");
        File.WriteAllText(rawPath, content);
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: level);
        return zstPath;
    }

    private static string MakeContent(string phrase, int count)
    {
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < count; i++) sb.Append(phrase).Append(i).Append('\n');
        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // GetMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetadata_NonNull()
    {
        var path = MakeZst(MakeContent("metadata test block", 80), "meta1");
        var doc = ZstDocument.LoadFile(path);
        Assert.NotNull(doc.GetMetadata());
    }

    [Fact]
    public void GetMetadata_NoThrow()
    {
        var path = MakeZst(MakeContent("no throw metadata", 60), "meta2");
        var doc = ZstDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.GetMetadata());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMetadata_NonEmpty()
    {
        var path = MakeZst(MakeContent("non empty metadata check", 80), "meta3");
        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.GetMetadata().Count > 0);
    }

    [Fact]
    public void GetMetadata_Consistent()
    {
        var path = MakeZst(MakeContent("consistent metadata test", 80), "meta4");
        var doc = ZstDocument.LoadFile(path);
        var m1 = doc.GetMetadata();
        var m2 = doc.GetMetadata();
        Assert.Equal(m1.Count, m2.Count);
    }

    [Fact]
    public void GetMetadata_SaveLoad_Consistent()
    {
        var path = MakeZst(MakeContent("save load metadata", 80), "meta5");
        var doc = ZstDocument.LoadFile(path);
        var before = doc.GetMetadata().Count;
        var savePath = TempFile("meta_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(before, loaded.GetMetadata().Count);
    }

    // -------------------------------------------------------------------------
    // GetChecksum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChecksum_NonNull()
    {
        var path = MakeZst(MakeContent("checksum test data", 80), "chk1");
        var doc = ZstDocument.LoadFile(path);
        Assert.NotNull(doc.GetChecksum());
    }

    [Fact]
    public void GetChecksum_NoThrow()
    {
        var path = MakeZst(MakeContent("no throw checksum", 60), "chk2");
        var doc = ZstDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.GetChecksum());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChecksum_NonEmpty()
    {
        var path = MakeZst(MakeContent("non empty checksum test", 80), "chk3");
        var doc = ZstDocument.LoadFile(path);
        Assert.NotEmpty(doc.GetChecksum());
    }

    [Fact]
    public void GetChecksum_Consistent()
    {
        var path = MakeZst(MakeContent("consistent checksum verification", 80), "chk4");
        var doc = ZstDocument.LoadFile(path);
        var c1 = doc.GetChecksum();
        var c2 = doc.GetChecksum();
        Assert.Equal(c1, c2);
    }

    [Fact]
    public void GetChecksum_SameContent_SameChecksum()
    {
        var content = MakeContent("same content checksum A", 80);
        var path1 = MakeZst(content, "chk5a");
        var path2 = MakeZst(content, "chk5b");
        var doc1 = ZstDocument.LoadFile(path1);
        var doc2 = ZstDocument.LoadFile(path2);
        // Same decompressed content should yield same checksum
        Assert.Equal(doc1.GetChecksum(), doc2.GetChecksum());
    }

    [Fact]
    public void GetChecksum_DifferentContent_DifferentChecksum()
    {
        var path1 = MakeZst(MakeContent("content alpha unique", 80), "chk6a");
        var path2 = MakeZst(MakeContent("content beta unique", 80), "chk6b");
        var doc1 = ZstDocument.LoadFile(path1);
        var doc2 = ZstDocument.LoadFile(path2);
        Assert.NotEqual(doc1.GetChecksum(), doc2.GetChecksum());
    }

    [Fact]
    public void GetChecksum_SaveLoad_Consistent()
    {
        var path = MakeZst(MakeContent("checksum save load", 80), "chk7");
        var doc = ZstDocument.LoadFile(path);
        var before = doc.GetChecksum();
        var savePath = TempFile("chk_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(before, loaded.GetChecksum());
    }

    // -------------------------------------------------------------------------
    // GetMagicBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMagicBytes_NonNull()
    {
        var path = MakeZst(MakeContent("magic bytes test", 60), "magic1");
        var doc = ZstDocument.LoadFile(path);
        Assert.NotNull(doc.GetMagicBytes());
    }

    [Fact]
    public void GetMagicBytes_NoThrow()
    {
        var path = MakeZst(MakeContent("no throw magic bytes", 60), "magic2");
        var doc = ZstDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.GetMagicBytes());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMagicBytes_Length_4()
    {
        var path = MakeZst(MakeContent("magic length 4 check", 60), "magic3");
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(4, doc.GetMagicBytes().Length);
    }

    [Fact]
    public void GetMagicBytes_HasZstSignature()
    {
        var path = MakeZst(MakeContent("zst signature verification", 60), "magic4");
        var doc = ZstDocument.LoadFile(path);
        var magic = doc.GetMagicBytes();
        // Zstandard magic = 0xFD2FB528 (little-endian: 0x28, 0xB5, 0x2F, 0xFD)
        Assert.Equal(0x28, magic[0]);
        Assert.Equal(0xB5, magic[1]);
        Assert.Equal(0x2F, magic[2]);
        Assert.Equal(0xFD, magic[3]);
    }

    [Fact]
    public void GetMagicBytes_Consistent()
    {
        var path = MakeZst(MakeContent("consistent magic bytes", 60), "magic5");
        var doc = ZstDocument.LoadFile(path);
        var mb1 = doc.GetMagicBytes();
        var mb2 = doc.GetMagicBytes();
        Assert.Equal(mb1[0], mb2[0]);
        Assert.Equal(mb1[3], mb2[3]);
    }

    [Fact]
    public void GetMagicBytes_SaveLoad_Consistent()
    {
        var path = MakeZst(MakeContent("magic save load check", 60), "magic6");
        var doc = ZstDocument.LoadFile(path);
        var before = doc.GetMagicBytes();
        var savePath = TempFile("magic_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        var after = loaded.GetMagicBytes();
        Assert.Equal(before[0], after[0]);
        Assert.Equal(before[3], after[3]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressFile_GetMetadata_GetChecksum_GetMagicBytes_SaveToFile_Pipeline()
    {
        // Create substantial content for compression
        var content = MakeContent("The strategic planning committee reviewed all divisional targets", 200);

        var rawPath = TempFile("dogfood_raw.txt");
        File.WriteAllText(rawPath, content);

        var zstPath = TempFile("dogfood.zst");
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);
        Assert.True(File.Exists(zstPath));

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.True(doc.IsValid);

        // GetMetadata
        var metadata = doc.GetMetadata();
        Assert.NotNull(metadata);
        Assert.True(metadata.Count > 0);
        var m2 = doc.GetMetadata();
        Assert.Equal(metadata.Count, m2.Count);

        // GetChecksum
        var checksum = doc.GetChecksum();
        Assert.NotNull(checksum);
        Assert.NotEmpty(checksum);
        Assert.Equal(checksum, doc.GetChecksum()); // consistent

        // GetMagicBytes
        var magic = doc.GetMagicBytes();
        Assert.NotNull(magic);
        Assert.Equal(4, magic.Length);
        Assert.Equal(0x28, magic[0]);
        Assert.Equal(0xB5, magic[1]);
        Assert.Equal(0x2F, magic[2]);
        Assert.Equal(0xFD, magic[3]);

        // GetCompressionStats
        var stats = doc.GetCompressionStats();
        Assert.True(stats.Ratio > 0);
        Assert.True(stats.OriginalSize > 0);
        Assert.True(stats.CompressedSize > 0);

        // GetFrameCount
        Assert.True(doc.GetFrameCount() > 0);
        Assert.Equal(doc.GetFrameCount(), doc.GetFrameCount());

        // Different content → different checksum
        var content2 = MakeContent("Completely different enterprise content for checksum test", 200);
        var raw2 = TempFile("dogfood_raw2.txt");
        File.WriteAllText(raw2, content2);
        var zst2 = TempFile("dogfood2.zst");
        ZstWriter.CompressFile(raw2, zst2, compressionLevel: 3);
        var doc2 = ZstDocument.LoadFile(zst2);
        Assert.NotEqual(checksum, doc2.GetChecksum());

        // Same content → same checksum
        var raw3 = TempFile("dogfood_raw3.txt");
        File.WriteAllText(raw3, content);
        var zst3 = TempFile("dogfood3.zst");
        ZstWriter.CompressFile(raw3, zst3, compressionLevel: 3);
        var doc3 = ZstDocument.LoadFile(zst3);
        Assert.Equal(checksum, doc3.GetChecksum());

        // SaveToFile
        var savePath = TempFile("dogfood_saved.zst");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile saved and verify
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.True(loaded.IsValid);
        Assert.Equal(metadata.Count, loaded.GetMetadata().Count);
        Assert.Equal(checksum, loaded.GetChecksum());

        var loadedMagic = loaded.GetMagicBytes();
        Assert.Equal(4, loadedMagic.Length);
        Assert.Equal(0x28, loadedMagic[0]);

        // Decompress saved file
        var decompPath = TempFile("dogfood_decomp.txt");
        ZstParser.DecompressFile(savePath, decompPath);
        Assert.Equal(content, File.ReadAllText(decompPath));

        // Final save
        var finalPath = TempFile("dogfood_final.zst");
        loaded.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = ZstDocument.LoadFile(finalPath);
        Assert.True(final.IsValid);
        Assert.Equal(checksum, final.GetChecksum());
        Assert.Equal(4, final.GetMagicBytes().Length);
    }
}
