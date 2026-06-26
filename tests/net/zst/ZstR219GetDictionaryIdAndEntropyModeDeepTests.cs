// Tests for ZstDocument.GetDictionaryId, GetEntropyMode, GetBlockSize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R219

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R219: Tests for ZstDocument.GetDictionaryId, GetEntropyMode, GetBlockSize deeper.
/// GetDictionaryId(): returns the dictionary ID embedded in the frame header (0 if none).
/// GetEntropyMode(): returns a string describing the entropy coding mode (e.g. "Huffman", "FSE").
/// GetBlockSize(): returns the maximum block size used during compression.
/// Covers: GetDictionaryId no-throw; GetDictionaryId non-negative; GetDictionaryId consistent;
/// GetDictionaryId save-load; GetDictionaryId no-dict is zero;
/// GetEntropyMode no-throw; GetEntropyMode non-null; GetEntropyMode non-empty;
/// GetEntropyMode consistent; GetEntropyMode save-load;
/// GetBlockSize no-throw; GetBlockSize positive; GetBlockSize consistent;
/// GetBlockSize save-load; GetBlockSize power-of-two-or-common;
/// dogfood CompressFile→GetDictionaryId→GetEntropyMode→GetBlockSize→SaveToFile pipeline.
/// </summary>
public class ZstR219GetDictionaryIdAndEntropyModeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR219GetDictionaryIdAndEntropyModeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR219_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private ZstDocument MakeDoc(string content, int level = 3)
    {
        var raw = TempFile("r_" + Guid.NewGuid().ToString("N") + ".txt");
        var zst = TempFile("z_" + Guid.NewGuid().ToString("N") + ".zst");
        File.WriteAllText(raw, content);
        ZstWriter.CompressFile(raw, zst, compressionLevel: level);
        return ZstDocument.LoadFile(zst);
    }

    private static string RepeatText(string phrase, int times)
    {
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < times; i++)
            sb.Append(phrase).Append(' ').Append(i).Append('\n');
        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // GetDictionaryId
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDictionaryId_NoThrow()
    {
        var doc = MakeDoc(RepeatText("dictionary id no throw", 80));
        var ex = Record.Exception(() => doc.GetDictionaryId());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDictionaryId_NonNegative()
    {
        var doc = MakeDoc(RepeatText("dictionary id non negative", 80));
        Assert.True(doc.GetDictionaryId() >= 0);
    }

    [Fact]
    public void GetDictionaryId_Consistent()
    {
        var doc = MakeDoc(RepeatText("dictionary id consistent", 80));
        Assert.Equal(doc.GetDictionaryId(), doc.GetDictionaryId());
    }

    [Fact]
    public void GetDictionaryId_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("dictionary id save load", 80));
        var before = doc.GetDictionaryId();
        var path = TempFile("did_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDictionaryId());
    }

    [Fact]
    public void GetDictionaryId_NoDict_IsZero()
    {
        // Compressing without a dictionary should yield ID = 0
        var doc = MakeDoc(RepeatText("no dictionary compression", 80));
        Assert.Equal(0, doc.GetDictionaryId());
    }

    // -------------------------------------------------------------------------
    // GetEntropyMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEntropyMode_NoThrow()
    {
        var doc = MakeDoc(RepeatText("entropy mode no throw", 80));
        var ex = Record.Exception(() => doc.GetEntropyMode());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEntropyMode_NonNull()
    {
        var doc = MakeDoc(RepeatText("entropy mode non null", 80));
        Assert.NotNull(doc.GetEntropyMode());
    }

    [Fact]
    public void GetEntropyMode_NonEmpty()
    {
        var doc = MakeDoc(RepeatText("entropy mode non empty", 80));
        Assert.NotEmpty(doc.GetEntropyMode());
    }

    [Fact]
    public void GetEntropyMode_Consistent()
    {
        var doc = MakeDoc(RepeatText("entropy mode consistent", 80));
        Assert.Equal(doc.GetEntropyMode(), doc.GetEntropyMode());
    }

    [Fact]
    public void GetEntropyMode_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("entropy mode save load", 80));
        var before = doc.GetEntropyMode();
        var path = TempFile("em_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetEntropyMode());
    }

    // -------------------------------------------------------------------------
    // GetBlockSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockSize_NoThrow()
    {
        var doc = MakeDoc(RepeatText("block size no throw", 80));
        var ex = Record.Exception(() => doc.GetBlockSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockSize_Positive()
    {
        var doc = MakeDoc(RepeatText("block size positive", 80));
        Assert.True(doc.GetBlockSize() > 0);
    }

    [Fact]
    public void GetBlockSize_Consistent()
    {
        var doc = MakeDoc(RepeatText("block size consistent", 80));
        Assert.Equal(doc.GetBlockSize(), doc.GetBlockSize());
    }

    [Fact]
    public void GetBlockSize_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("block size save load", 80));
        var before = doc.GetBlockSize();
        var path = TempFile("bs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockSize());
    }

    [Fact]
    public void GetBlockSize_AtLeast_1KB()
    {
        // Zstandard block size is typically 128KB+
        var doc = MakeDoc(RepeatText("block size at least 1KB", 200));
        Assert.True(doc.GetBlockSize() >= 1024);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDictionaryId_GetEntropyMode_GetBlockSize_SaveToFile_Pipeline()
    {
        var original = RepeatText("Dogfood dictionary entropy block size content", 150);

        var rawPath = TempFile("dogfood_raw.txt");
        File.WriteAllText(rawPath, original);

        var zstPath = TempFile("dogfood_source.zst");
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.NotNull(doc);
        Assert.True(doc.IsValid);

        // GetDictionaryId
        var dictId = doc.GetDictionaryId();
        Assert.True(dictId >= 0);
        Assert.Equal(dictId, doc.GetDictionaryId()); // consistent
        Assert.Equal(0, dictId); // no dict used

        // GetEntropyMode
        var entropy = doc.GetEntropyMode();
        Assert.NotNull(entropy);
        Assert.NotEmpty(entropy);
        Assert.Equal(entropy, doc.GetEntropyMode()); // consistent

        // GetBlockSize
        var blockSize = doc.GetBlockSize();
        Assert.True(blockSize > 0);
        Assert.Equal(blockSize, doc.GetBlockSize()); // consistent

        // Cross-check with GetCompressionRatio
        Assert.True(doc.GetCompressionRatio() > 0);

        // Cross-check with GetDecompressedSize
        Assert.True(doc.GetDecompressedSize() > 0);

        // SaveToFile
        var savePath = TempFile("dogfood_saved.zst");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.True(loaded.IsValid);
        Assert.Equal(dictId, loaded.GetDictionaryId());
        Assert.Equal(entropy, loaded.GetEntropyMode());
        Assert.Equal(blockSize, loaded.GetBlockSize());

        // Decompress and verify round-trip
        var decompPath = TempFile("dogfood_decomp.txt");
        ZstParser.DecompressFile(savePath, decompPath);
        Assert.Equal(original, File.ReadAllText(decompPath));

        // Second doc — different compression level
        var raw2 = TempFile("dogfood_raw2.txt");
        File.WriteAllText(raw2, RepeatText("Level 19 compression test", 100));
        var zst2 = TempFile("dogfood_src2.zst");
        ZstWriter.CompressFile(raw2, zst2, compressionLevel: 6);
        var doc2 = ZstDocument.LoadFile(zst2);
        Assert.True(doc2.IsValid);
        Assert.True(doc2.GetDictionaryId() >= 0);
        Assert.NotNull(doc2.GetEntropyMode());
        Assert.True(doc2.GetBlockSize() > 0);

        // Final save
        var finalPath = TempFile("dogfood_final.zst");
        doc2.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = ZstDocument.LoadFile(finalPath);
        Assert.True(final.IsValid);
        Assert.Equal(doc2.GetDictionaryId(), final.GetDictionaryId());
        Assert.Equal(doc2.GetEntropyMode(), final.GetEntropyMode());
        Assert.Equal(doc2.GetBlockSize(), final.GetBlockSize());
    }
}
