// Tests for ZstDocument.GetHeaderSize, GetContentOffset, GetMagicNumber deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R215

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R215: Tests for ZstDocument.GetHeaderSize, GetContentOffset, GetMagicNumber deeper.
/// GetHeaderSize(): returns the size of the zstd frame header in bytes.
/// GetContentOffset(): returns the byte offset where content begins in the frame.
/// GetMagicNumber(): returns the zstd magic number (0xFD2FB528) as a string or long.
/// Covers: GetHeaderSize no-throw; GetHeaderSize positive; GetHeaderSize consistent;
/// GetHeaderSize save-load; GetHeaderSize reasonable range;
/// GetContentOffset no-throw; GetContentOffset positive; GetContentOffset consistent;
/// GetContentOffset save-load; GetContentOffset after GetHeaderSize;
/// GetMagicNumber no-throw; GetMagicNumber non-null; GetMagicNumber consistent;
/// GetMagicNumber save-load; GetMagicNumber same for all valid zst;
/// dogfood CompressFile→GetHeaderSize→GetContentOffset→GetMagicNumber→SaveToFile pipeline.
/// </summary>
public class ZstR215GetHeaderSizeAndContentOffsetDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR215GetHeaderSizeAndContentOffsetDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR215_" + Guid.NewGuid().ToString("N"));
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
    // GetHeaderSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaderSize_NoThrow()
    {
        var doc = MakeDoc(RepeatText("header size no throw", 80));
        var ex = Record.Exception(() => doc.GetHeaderSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHeaderSize_Positive()
    {
        var doc = MakeDoc(RepeatText("header size positive check", 80));
        Assert.True(doc.GetHeaderSize() > 0);
    }

    [Fact]
    public void GetHeaderSize_Consistent()
    {
        var doc = MakeDoc(RepeatText("header size consistent", 80));
        Assert.Equal(doc.GetHeaderSize(), doc.GetHeaderSize());
    }

    [Fact]
    public void GetHeaderSize_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("header size save load", 80));
        var before = doc.GetHeaderSize();
        var path = TempFile("hs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHeaderSize());
    }

    [Fact]
    public void GetHeaderSize_ReasonableRange()
    {
        var doc = MakeDoc(RepeatText("header size range", 80));
        var size = doc.GetHeaderSize();
        // zstd frame header is at least 6 bytes; cap at 18 bytes for practical single-frame
        Assert.True(size >= 6 && size <= 18);
    }

    // -------------------------------------------------------------------------
    // GetContentOffset
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContentOffset_NoThrow()
    {
        var doc = MakeDoc(RepeatText("content offset no throw", 80));
        var ex = Record.Exception(() => doc.GetContentOffset());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContentOffset_Positive()
    {
        var doc = MakeDoc(RepeatText("content offset positive", 80));
        Assert.True(doc.GetContentOffset() > 0);
    }

    [Fact]
    public void GetContentOffset_Consistent()
    {
        var doc = MakeDoc(RepeatText("content offset consistent", 80));
        Assert.Equal(doc.GetContentOffset(), doc.GetContentOffset());
    }

    [Fact]
    public void GetContentOffset_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("content offset save load", 80));
        var before = doc.GetContentOffset();
        var path = TempFile("co_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetContentOffset());
    }

    [Fact]
    public void GetContentOffset_AtLeast_HeaderSize()
    {
        var doc = MakeDoc(RepeatText("content offset vs header", 80));
        Assert.True(doc.GetContentOffset() >= doc.GetHeaderSize());
    }

    // -------------------------------------------------------------------------
    // GetMagicNumber
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMagicNumber_NoThrow()
    {
        var doc = MakeDoc(RepeatText("magic number no throw", 80));
        var ex = Record.Exception(() => doc.GetMagicNumber());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMagicNumber_NonNull()
    {
        var doc = MakeDoc(RepeatText("magic number non null", 80));
        Assert.NotNull(doc.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_Consistent()
    {
        var doc = MakeDoc(RepeatText("magic number consistent", 80));
        Assert.Equal(doc.GetMagicNumber(), doc.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("magic number save load", 80));
        var before = doc.GetMagicNumber();
        var path = TempFile("mn_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_SameForAllValidZst()
    {
        var doc1 = MakeDoc(RepeatText("magic number first doc", 60));
        var doc2 = MakeDoc(RepeatText("magic number second doc", 80));
        Assert.Equal(doc1.GetMagicNumber(), doc2.GetMagicNumber());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetHeaderSize_GetContentOffset_GetMagicNumber_SaveToFile_Pipeline()
    {
        var original = RepeatText("Dogfood header offset magic pipeline content for verification", 140);

        var rawPath = TempFile("dogfood_raw.txt");
        File.WriteAllText(rawPath, original);

        var zstPath = TempFile("dogfood_source.zst");
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.NotNull(doc);
        Assert.True(doc.IsValid);

        // GetHeaderSize
        var headerSize = doc.GetHeaderSize();
        Assert.True(headerSize > 0);
        Assert.Equal(headerSize, doc.GetHeaderSize()); // consistent

        // GetContentOffset
        var contentOffset = doc.GetContentOffset();
        Assert.True(contentOffset > 0);
        Assert.True(contentOffset >= headerSize);
        Assert.Equal(contentOffset, doc.GetContentOffset()); // consistent

        // GetMagicNumber
        var magic = doc.GetMagicNumber();
        Assert.NotNull(magic);
        Assert.Equal(magic, doc.GetMagicNumber()); // consistent

        // GetDecompressedSize positive
        Assert.True(doc.GetDecompressedSize() > 0);
        Assert.True(doc.GetCompressedSize() > 0);

        // IsValid
        Assert.True(doc.IsValid);

        // GetCompressionStats
        var stats = doc.GetCompressionStats();
        Assert.NotNull(stats);
        Assert.True(stats.Ratio > 0);

        // SaveToFile
        var savePath = TempFile("dogfood_saved.zst");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify all fields consistent
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.True(loaded.IsValid);
        Assert.Equal(doc.GetHeaderSize(), loaded.GetHeaderSize());
        Assert.Equal(doc.GetContentOffset(), loaded.GetContentOffset());
        Assert.Equal(doc.GetMagicNumber(), loaded.GetMagicNumber());
        Assert.Equal(doc.GetDecompressedSize(), loaded.GetDecompressedSize());

        // Decompress and verify round-trip
        var decompPath = TempFile("dogfood_decomp.txt");
        ZstParser.DecompressFile(savePath, decompPath);
        Assert.True(File.Exists(decompPath));
        Assert.Equal(original, File.ReadAllText(decompPath));

        // Second doc with different level
        var raw2 = TempFile("dogfood_raw2.txt");
        File.WriteAllText(raw2, RepeatText("Second pipeline content block for header offset comparison", 100));
        var zst2 = TempFile("dogfood_source2.zst");
        ZstWriter.CompressFile(raw2, zst2, compressionLevel: 6);
        var doc2 = ZstDocument.LoadFile(zst2);
        Assert.True(doc2.IsValid);
        Assert.True(doc2.GetHeaderSize() > 0);
        Assert.True(doc2.GetContentOffset() > 0);
        Assert.Equal(magic, doc2.GetMagicNumber()); // magic number same for all valid zst

        // Final save
        var finalPath = TempFile("dogfood_final.zst");
        doc2.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = ZstDocument.LoadFile(finalPath);
        Assert.True(final.IsValid);
        Assert.Equal(doc2.GetHeaderSize(), final.GetHeaderSize());
        Assert.Equal(doc2.GetContentOffset(), final.GetContentOffset());
        Assert.Equal(doc2.GetMagicNumber(), final.GetMagicNumber());
    }
}
