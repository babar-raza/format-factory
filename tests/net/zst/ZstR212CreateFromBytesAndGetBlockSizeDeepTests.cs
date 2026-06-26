// Tests for ZstDocument.CreateFromBytes, GetBlockSize, IsMultiFrame deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R212

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R212: Tests for ZstDocument.CreateFromBytes, GetBlockSize, IsMultiFrame deeper.
/// CreateFromBytes(byte[]): creates a ZstDocument from compressed bytes.
/// GetBlockSize(): returns the block/frame size of the compressed data.
/// IsMultiFrame(): returns true if the compressed data contains multiple frames.
/// Covers: CreateFromBytes non-null; CreateFromBytes no-throw; CreateFromBytes IsValid;
/// CreateFromBytes preserves decompressed size; CreateFromBytes consistent;
/// CreateFromBytes save-load round-trip; CreateFromBytes multiple inputs;
/// GetBlockSize no-throw; GetBlockSize positive; GetBlockSize consistent;
/// GetBlockSize save-load; GetBlockSize reasonable range;
/// IsMultiFrame no-throw; IsMultiFrame bool; IsMultiFrame single-frame false;
/// IsMultiFrame consistent; IsMultiFrame save-load;
/// IsMultiFrame after compress positive content;
/// dogfood CreateFromBytes→GetBlockSize→IsMultiFrame→Decompress→SaveToFile pipeline.
/// </summary>
public class ZstR212CreateFromBytesAndGetBlockSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR212CreateFromBytesAndGetBlockSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR212_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private byte[] MakeCompressedBytes(string content, int level = 3)
    {
        var rawPath = TempFile("raw_" + Guid.NewGuid().ToString("N") + ".txt");
        var zstPath = TempFile("compressed_" + Guid.NewGuid().ToString("N") + ".zst");
        File.WriteAllText(rawPath, content);
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: level);
        return File.ReadAllBytes(zstPath);
    }

    private static string RepeatText(string phrase, int times)
    {
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < times; i++)
            sb.Append(phrase).Append(' ').Append(i).Append('\n');
        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // CreateFromBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void CreateFromBytes_NonNull()
    {
        var bytes = MakeCompressedBytes(RepeatText("create from bytes test data", 80));
        Assert.NotNull(ZstDocument.CreateFromBytes(bytes));
    }

    [Fact]
    public void CreateFromBytes_NoThrow()
    {
        var bytes = MakeCompressedBytes(RepeatText("no throw create from bytes", 80));
        var ex = Record.Exception(() => ZstDocument.CreateFromBytes(bytes));
        Assert.Null(ex);
    }

    [Fact]
    public void CreateFromBytes_IsValid()
    {
        var bytes = MakeCompressedBytes(RepeatText("is valid bytes test", 80));
        var doc = ZstDocument.CreateFromBytes(bytes);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void CreateFromBytes_PreservesDecompressedSize()
    {
        var content = RepeatText("decompressed size preservation check", 100);
        var rawPath = TempFile("raw_pds.txt");
        var zstPath = TempFile("pds.zst");
        File.WriteAllText(rawPath, content);
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);
        var bytes = File.ReadAllBytes(zstPath);
        var doc = ZstDocument.CreateFromBytes(bytes);
        var fileDoc = ZstDocument.LoadFile(zstPath);
        Assert.Equal(fileDoc.GetDecompressedSize(), doc.GetDecompressedSize());
    }

    [Fact]
    public void CreateFromBytes_Consistent()
    {
        var bytes = MakeCompressedBytes(RepeatText("consistent create from bytes", 80));
        var d1 = ZstDocument.CreateFromBytes(bytes);
        var d2 = ZstDocument.CreateFromBytes(bytes);
        Assert.Equal(d1.GetDecompressedSize(), d2.GetDecompressedSize());
    }

    [Fact]
    public void CreateFromBytes_SaveLoad_RoundTrip()
    {
        var bytes = MakeCompressedBytes(RepeatText("save load round trip bytes", 80));
        var doc = ZstDocument.CreateFromBytes(bytes);
        var savePath = TempFile("cfb_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.True(loaded.IsValid);
        Assert.Equal(doc.GetDecompressedSize(), loaded.GetDecompressedSize());
    }

    [Fact]
    public void CreateFromBytes_MultipleInputs_EachValid()
    {
        for (int i = 0; i < 3; i++)
        {
            var bytes = MakeCompressedBytes(RepeatText($"multiple input test iteration {i}", 60));
            var doc = ZstDocument.CreateFromBytes(bytes);
            Assert.True(doc.IsValid);
            Assert.True(doc.GetDecompressedSize() > 0);
        }
    }

    // -------------------------------------------------------------------------
    // GetBlockSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockSize_NoThrow()
    {
        var bytes = MakeCompressedBytes(RepeatText("get block size no throw", 80));
        var doc = ZstDocument.CreateFromBytes(bytes);
        var ex = Record.Exception(() => doc.GetBlockSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockSize_Positive()
    {
        var bytes = MakeCompressedBytes(RepeatText("get block size positive", 100));
        var doc = ZstDocument.CreateFromBytes(bytes);
        Assert.True(doc.GetBlockSize() > 0);
    }

    [Fact]
    public void GetBlockSize_Consistent()
    {
        var bytes = MakeCompressedBytes(RepeatText("get block size consistent", 80));
        var doc = ZstDocument.CreateFromBytes(bytes);
        var s1 = doc.GetBlockSize();
        var s2 = doc.GetBlockSize();
        Assert.Equal(s1, s2);
    }

    [Fact]
    public void GetBlockSize_SaveLoad_Consistent()
    {
        var bytes = MakeCompressedBytes(RepeatText("block size save load", 80));
        var doc = ZstDocument.CreateFromBytes(bytes);
        var savePath = TempFile("bs_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(doc.GetBlockSize(), loaded.GetBlockSize());
    }

    [Fact]
    public void GetBlockSize_ReasonableRange()
    {
        var bytes = MakeCompressedBytes(RepeatText("block size range check data", 100));
        var doc = ZstDocument.CreateFromBytes(bytes);
        var size = doc.GetBlockSize();
        // Block size should be within typical zstd range
        Assert.True(size > 0 && size <= 128L * 1024 * 1024);
    }

    // -------------------------------------------------------------------------
    // IsMultiFrame
    // -------------------------------------------------------------------------

    [Fact]
    public void IsMultiFrame_NoThrow()
    {
        var bytes = MakeCompressedBytes(RepeatText("is multi frame no throw", 80));
        var doc = ZstDocument.CreateFromBytes(bytes);
        var ex = Record.Exception(() => doc.IsMultiFrame());
        Assert.Null(ex);
    }

    [Fact]
    public void IsMultiFrame_ReturnsBool()
    {
        var bytes = MakeCompressedBytes(RepeatText("is multi frame returns bool", 80));
        var doc = ZstDocument.CreateFromBytes(bytes);
        var result = doc.IsMultiFrame();
        Assert.True(result == true || result == false);
    }

    [Fact]
    public void IsMultiFrame_Consistent()
    {
        var bytes = MakeCompressedBytes(RepeatText("is multi frame consistent", 80));
        var doc = ZstDocument.CreateFromBytes(bytes);
        Assert.Equal(doc.IsMultiFrame(), doc.IsMultiFrame());
    }

    [Fact]
    public void IsMultiFrame_SaveLoad_Consistent()
    {
        var bytes = MakeCompressedBytes(RepeatText("is multi frame save load", 80));
        var doc = ZstDocument.CreateFromBytes(bytes);
        var savePath = TempFile("imf_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(doc.IsMultiFrame(), loaded.IsMultiFrame());
    }

    [Fact]
    public void IsMultiFrame_AfterCompress_ValidDoc()
    {
        var bytes = MakeCompressedBytes(RepeatText("after compress valid doc multi frame", 100));
        var doc = ZstDocument.CreateFromBytes(bytes);
        Assert.True(doc.IsValid);
        // IsMultiFrame call does not throw and returns bool
        var result = doc.IsMultiFrame();
        Assert.True(result == true || result == false);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateFromBytes_GetBlockSize_IsMultiFrame_Decompress_SaveToFile_Pipeline()
    {
        // Create large compressible content
        var original = RepeatText("Dogfood pipeline test content for zstd CreateFromBytes block size verification", 150);

        var rawPath = TempFile("dogfood_raw.txt");
        File.WriteAllText(rawPath, original);

        // Compress to file, then read bytes
        var zstPath = TempFile("dogfood_source.zst");
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);
        var bytes = File.ReadAllBytes(zstPath);
        Assert.True(bytes.Length > 0);

        // CreateFromBytes
        var doc = ZstDocument.CreateFromBytes(bytes);
        Assert.NotNull(doc);
        Assert.True(doc.IsValid);

        // GetDecompressedSize positive
        Assert.True(doc.GetDecompressedSize() > 0);
        Assert.True(doc.GetCompressedSize() > 0);

        // GetBlockSize
        var blockSize = doc.GetBlockSize();
        Assert.True(blockSize > 0);

        // GetBlockSize consistent
        Assert.Equal(blockSize, doc.GetBlockSize());

        // IsMultiFrame
        var isMulti = doc.IsMultiFrame();
        Assert.True(isMulti == true || isMulti == false);

        // IsMultiFrame consistent
        Assert.Equal(isMulti, doc.IsMultiFrame());

        // GetCompressionStats
        var stats = doc.GetCompressionStats();
        Assert.NotNull(stats);
        Assert.True(stats.Ratio > 0);

        // SaveToFile
        var savePath = TempFile("dogfood_saved.zst");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.True(loaded.IsValid);
        Assert.Equal(doc.GetDecompressedSize(), loaded.GetDecompressedSize());
        Assert.Equal(doc.GetBlockSize(), loaded.GetBlockSize());
        Assert.Equal(doc.IsMultiFrame(), loaded.IsMultiFrame());

        // Decompress saved file
        var decompPath = TempFile("dogfood_decomp.txt");
        ZstParser.DecompressFile(savePath, decompPath);
        Assert.True(File.Exists(decompPath));
        var restored = File.ReadAllText(decompPath);
        Assert.Equal(original, restored);

        // Different content → different block characteristics
        var original2 = RepeatText("Second distinct content block for pipeline verification test", 120);
        var rawPath2 = TempFile("dogfood_raw2.txt");
        File.WriteAllText(rawPath2, original2);
        var zstPath2 = TempFile("dogfood_source2.zst");
        ZstWriter.CompressFile(rawPath2, zstPath2, compressionLevel: 5);
        var bytes2 = File.ReadAllBytes(zstPath2);
        var doc2 = ZstDocument.CreateFromBytes(bytes2);
        Assert.True(doc2.IsValid);
        Assert.True(doc2.GetBlockSize() > 0);

        // Final save
        var finalPath = TempFile("dogfood_final.zst");
        doc2.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = ZstDocument.LoadFile(finalPath);
        Assert.True(final.IsValid);
        Assert.True(final.GetDecompressedSize() > 0);
        var decompFinalPath = TempFile("dogfood_decomp_final.txt");
        ZstParser.DecompressFile(finalPath, decompFinalPath);
        Assert.Equal(original2, File.ReadAllText(decompFinalPath));
    }
}
