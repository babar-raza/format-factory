// Tests for ZstDocument.GetVersion, GetDictionaryId, GetWindowSize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R211

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R211: Tests for ZstDocument.GetVersion, GetDictionaryId, GetWindowSize deeper.
/// GetVersion(): returns the Zstandard version used for compression.
/// GetDictionaryId(): returns the dictionary ID (0 if no dictionary).
/// GetWindowSize(): returns the window size used during compression.
/// Covers: GetVersion non-null; GetVersion no-throw; GetVersion non-empty;
/// GetVersion consistent; GetVersion is numeric; GetVersion save-load;
/// GetDictionaryId non-negative; GetDictionaryId no-throw; GetDictionaryId consistent;
/// GetDictionaryId zero for no-dictionary; GetDictionaryId save-load;
/// GetDictionaryId same for same file; GetDictionaryId returns int;
/// GetWindowSize positive; GetWindowSize no-throw; GetWindowSize consistent;
/// GetWindowSize reasonable range; GetWindowSize save-load;
/// IsValid true; GetFrameCount positive; GetCompressionStats non-null;
/// GetChecksum non-empty; GetMagicBytes length=4;
/// dogfood CompressFile→GetVersion→GetDictionaryId→GetWindowSize→SaveToFile pipeline.
/// </summary>
public class ZstR211GetVersionAndDictionaryIdDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR211GetVersionAndDictionaryIdDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR211_" + Guid.NewGuid().ToString("N"));
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
        var raw = TempFile($"raw_{tag}.txt");
        var zst = TempFile($"{tag}.zst");
        File.WriteAllText(raw, content);
        ZstWriter.CompressFile(raw, zst, compressionLevel: level);
        return zst;
    }

    private static string BigContent(int lines) =>
        string.Join('\n', System.Linq.Enumerable.Range(0, lines)
            .Select(i => $"Line {i}: The corporate strategy report covers all operational divisions for the year."));

    // -------------------------------------------------------------------------
    // GetVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void GetVersion_NonNull()
    {
        var doc = ZstDocument.LoadFile(MakeZst(BigContent(80), "ver1"));
        Assert.NotNull(doc.GetVersion());
    }

    [Fact]
    public void GetVersion_NoThrow()
    {
        var doc = ZstDocument.LoadFile(MakeZst(BigContent(60), "ver2"));
        var ex = Record.Exception(() => doc.GetVersion());
        Assert.Null(ex);
    }

    [Fact]
    public void GetVersion_NonEmpty()
    {
        var doc = ZstDocument.LoadFile(MakeZst(BigContent(80), "ver3"));
        Assert.NotEmpty(doc.GetVersion());
    }

    [Fact]
    public void GetVersion_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(BigContent(80), "ver4"));
        Assert.Equal(doc.GetVersion(), doc.GetVersion());
    }

    [Fact]
    public void GetVersion_Contains_Digits()
    {
        var doc = ZstDocument.LoadFile(MakeZst(BigContent(80), "ver5"));
        var version = doc.GetVersion();
        Assert.True(version.Any(char.IsDigit));
    }

    [Fact]
    public void GetVersion_SaveLoad_Consistent()
    {
        var path = MakeZst(BigContent(80), "ver6");
        var doc = ZstDocument.LoadFile(path);
        var before = doc.GetVersion();
        var savePath = TempFile("ver_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(before, loaded.GetVersion());
    }

    // -------------------------------------------------------------------------
    // GetDictionaryId
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDictionaryId_NonNegative()
    {
        var doc = ZstDocument.LoadFile(MakeZst(BigContent(80), "dict1"));
        Assert.True(doc.GetDictionaryId() >= 0);
    }

    [Fact]
    public void GetDictionaryId_NoThrow()
    {
        var doc = ZstDocument.LoadFile(MakeZst(BigContent(60), "dict2"));
        var ex = Record.Exception(() => doc.GetDictionaryId());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDictionaryId_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(BigContent(80), "dict3"));
        Assert.Equal(doc.GetDictionaryId(), doc.GetDictionaryId());
    }

    [Fact]
    public void GetDictionaryId_Zero_ForNoDictionary()
    {
        // Standard compression without dictionary → dictionary ID = 0
        var doc = ZstDocument.LoadFile(MakeZst(BigContent(80), "dict4"));
        Assert.Equal(0, doc.GetDictionaryId());
    }

    [Fact]
    public void GetDictionaryId_SameFile_SameId()
    {
        var path = MakeZst(BigContent(80), "dict5");
        var doc1 = ZstDocument.LoadFile(path);
        var doc2 = ZstDocument.LoadFile(path);
        Assert.Equal(doc1.GetDictionaryId(), doc2.GetDictionaryId());
    }

    [Fact]
    public void GetDictionaryId_SaveLoad_Consistent()
    {
        var path = MakeZst(BigContent(80), "dict6");
        var doc = ZstDocument.LoadFile(path);
        var before = doc.GetDictionaryId();
        var savePath = TempFile("dict_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(before, loaded.GetDictionaryId());
    }

    // -------------------------------------------------------------------------
    // GetWindowSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWindowSize_Positive()
    {
        var doc = ZstDocument.LoadFile(MakeZst(BigContent(80), "win1"));
        Assert.True(doc.GetWindowSize() > 0);
    }

    [Fact]
    public void GetWindowSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(MakeZst(BigContent(60), "win2"));
        var ex = Record.Exception(() => doc.GetWindowSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWindowSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(BigContent(80), "win3"));
        Assert.Equal(doc.GetWindowSize(), doc.GetWindowSize());
    }

    [Fact]
    public void GetWindowSize_ReasonableRange()
    {
        var doc = ZstDocument.LoadFile(MakeZst(BigContent(80), "win4"));
        var ws = doc.GetWindowSize();
        // Zstandard window size is typically between 1KB and 128MB
        Assert.True(ws >= 1024 && ws <= 134217728);
    }

    [Fact]
    public void GetWindowSize_SaveLoad_Consistent()
    {
        var path = MakeZst(BigContent(80), "win5");
        var doc = ZstDocument.LoadFile(path);
        var before = doc.GetWindowSize();
        var savePath = TempFile("win_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(before, loaded.GetWindowSize());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressFile_GetVersion_GetDictionaryId_GetWindowSize_SaveToFile_Pipeline()
    {
        var content = BigContent(200);
        var rawPath = TempFile("dogfood_raw.txt");
        File.WriteAllText(rawPath, content);

        // Compress at level 3
        var zstPath = TempFile("dogfood.zst");
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);
        Assert.True(File.Exists(zstPath));

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.True(doc.IsValid);

        // GetVersion
        var version = doc.GetVersion();
        Assert.NotNull(version);
        Assert.NotEmpty(version);
        Assert.True(version.Any(char.IsDigit));
        Assert.Equal(version, doc.GetVersion()); // consistent

        // GetDictionaryId
        var dictId = doc.GetDictionaryId();
        Assert.True(dictId >= 0);
        Assert.Equal(0, dictId); // no dictionary used
        Assert.Equal(dictId, doc.GetDictionaryId()); // consistent

        // GetWindowSize
        var windowSize = doc.GetWindowSize();
        Assert.True(windowSize > 0);
        Assert.True(windowSize >= 1024);
        Assert.Equal(windowSize, doc.GetWindowSize()); // consistent

        // GetCompressionStats
        var stats = doc.GetCompressionStats();
        Assert.True(stats.Ratio > 0);

        // GetChecksum
        var checksum = doc.GetChecksum();
        Assert.NotNull(checksum);
        Assert.NotEmpty(checksum);

        // GetMagicBytes
        var magic = doc.GetMagicBytes();
        Assert.Equal(4, magic.Length);
        Assert.Equal(0x28, magic[0]);

        // GetFrameCount
        Assert.True(doc.GetFrameCount() > 0);

        // Compress at level 9 — same version
        var zst9Path = TempFile("dogfood_level9.zst");
        ZstWriter.CompressFile(rawPath, zst9Path, compressionLevel: 9);
        var doc9 = ZstDocument.LoadFile(zst9Path);
        Assert.Equal(version, doc9.GetVersion()); // same ZST version regardless of level
        Assert.Equal(0, doc9.GetDictionaryId()); // no dictionary

        // SaveToFile
        var savePath = TempFile("dogfood_saved.zst");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile saved and verify all fields
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.True(loaded.IsValid);
        Assert.Equal(version, loaded.GetVersion());
        Assert.Equal(dictId, loaded.GetDictionaryId());
        Assert.Equal(windowSize, loaded.GetWindowSize());
        Assert.Equal(checksum, loaded.GetChecksum());

        // Decompress and verify roundtrip
        var decompPath = TempFile("dogfood_decomp.txt");
        ZstParser.DecompressFile(savePath, decompPath);
        Assert.Equal(content, File.ReadAllText(decompPath));

        // Final save
        var finalPath = TempFile("dogfood_final.zst");
        loaded.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = ZstDocument.LoadFile(finalPath);
        Assert.Equal(version, final.GetVersion());
        Assert.Equal(0, final.GetDictionaryId());
        Assert.True(final.GetWindowSize() > 0);
    }
}
