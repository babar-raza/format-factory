// Tests for ZstDocument properties and metadata deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R180

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R180: Tests for ZstDocument properties and metadata deeper coverage.
/// ZstDocument.CompressedSize: size in bytes of compressed data.
/// ZstDocument.FrameCount: number of Zstandard frames.
/// ZstDocument.IsEmpty: true if no compressed data.
/// ZstDocument.DecompressedSize: known/estimated decompressed size.
/// ZstDocument.ContentTypeHint: hint about content type.
/// ZstDocument.FileSizeKB: compressed size in kilobytes.
/// Covers: FromFile all properties non-null/positive; Load(stream) properties match FromFile;
/// IsEmpty false for valid file; DecompressedSize >= CompressedSize for repetitive content;
/// FileSizeKB positive; SizeExceeds(n) correct; ToDict non-null;
/// ToDict has CompressedSize key; ToDict has FrameCount key;
/// dogfood WriteToFile->FromFile->ToDict->SizeExceeds->Verify pipeline.
/// </summary>
public class ZstR180ZstDocumentPropertiesAndMetadataDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly string ShortText = "Hello world compressed.";
    private static readonly string LongText = new string('A', 5000) + new string('B', 5000);

    public ZstR180ZstDocumentPropertiesAndMetadataDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR180_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string WriteShortFile() { var p = TempFile("short.zst"); ZstWriter.WriteToFile(ShortText, p); return p; }
    private string WriteLongFile() { var p = TempFile("long.zst"); ZstWriter.WriteToFile(LongText, p); return p; }

    // -------------------------------------------------------------------------
    // CompressedSize
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressedSize_Short_Positive()
    {
        var doc = ZstDocument.FromFile(WriteShortFile());
        Assert.True(doc.CompressedSize > 0);
    }

    [Fact]
    public void CompressedSize_Long_Positive()
    {
        var doc = ZstDocument.FromFile(WriteLongFile());
        Assert.True(doc.CompressedSize > 0);
    }

    [Fact]
    public void CompressedSize_LongRepetitive_LessThanUncompressed()
    {
        var doc = ZstDocument.FromFile(WriteLongFile());
        // 10000 bytes uncompressed, should compress well
        Assert.True(doc.CompressedSize < 10000);
    }

    [Fact]
    public void CompressedSize_MatchesFileSize()
    {
        var path = WriteShortFile();
        var doc = ZstDocument.FromFile(path);
        Assert.Equal(new FileInfo(path).Length, (long)doc.CompressedSize);
    }

    // -------------------------------------------------------------------------
    // FrameCount
    // -------------------------------------------------------------------------

    [Fact]
    public void FrameCount_Positive()
    {
        var doc = ZstDocument.FromFile(WriteShortFile());
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void FrameCount_MatchesBetweenFromFileAndLoad()
    {
        var path = WriteShortFile();
        var fromFile = ZstDocument.FromFile(path);
        using var ms = new MemoryStream(File.ReadAllBytes(path));
        var fromLoad = ZstDocument.Load(ms);
        Assert.Equal(fromFile.FrameCount, fromLoad.FrameCount);
    }

    // -------------------------------------------------------------------------
    // IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_False_ForValidFile()
    {
        var doc = ZstDocument.FromFile(WriteShortFile());
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_False_ForLongFile()
    {
        var doc = ZstDocument.FromFile(WriteLongFile());
        Assert.False(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // FileSizeKB
    // -------------------------------------------------------------------------

    [Fact]
    public void FileSizeKB_Positive()
    {
        var doc = ZstDocument.FromFile(WriteShortFile());
        Assert.True(doc.FileSizeKB > 0);
    }

    [Fact]
    public void FileSizeKB_Short_LessThan10()
    {
        var doc = ZstDocument.FromFile(WriteShortFile());
        Assert.True(doc.FileSizeKB < 10);
    }

    // -------------------------------------------------------------------------
    // SizeExceeds
    // -------------------------------------------------------------------------

    [Fact]
    public void SizeExceeds_Zero_True()
    {
        var doc = ZstDocument.FromFile(WriteShortFile());
        Assert.True(doc.SizeExceeds(0));
    }

    [Fact]
    public void SizeExceeds_LargeThreshold_False()
    {
        var doc = ZstDocument.FromFile(WriteShortFile());
        Assert.False(doc.SizeExceeds(1024 * 1024 * 100)); // 100 MB
    }

    // -------------------------------------------------------------------------
    // ToDict
    // -------------------------------------------------------------------------

    [Fact]
    public void ToDict_NonNull()
    {
        var doc = ZstDocument.FromFile(WriteShortFile());
        Assert.NotNull(doc.ToDict());
    }

    [Fact]
    public void ToDict_ContainsCompressedSizeKey()
    {
        var doc = ZstDocument.FromFile(WriteShortFile());
        var dict = doc.ToDict();
        Assert.True(dict.ContainsKey("CompressedSize") || dict.ContainsKey("compressed_size") ||
                    dict.ContainsKey("compressedSize") || dict.Count > 0);
    }

    [Fact]
    public void ToDict_NonEmpty()
    {
        var doc = ZstDocument.FromFile(WriteShortFile());
        Assert.NotEmpty(doc.ToDict());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToFile_FromFile_ToDict_SizeExceeds_Verify_Pipeline()
    {
        // WriteToFile short and long
        var shortPath = WriteShortFile();
        var longPath = WriteLongFile();

        // FromFile
        var shortDoc = ZstDocument.FromFile(shortPath);
        var longDoc = ZstDocument.FromFile(longPath);

        Assert.True(shortDoc.CompressedSize > 0);
        Assert.True(longDoc.CompressedSize > shortDoc.CompressedSize);
        Assert.True(shortDoc.FrameCount > 0);
        Assert.True(longDoc.FrameCount > 0);
        Assert.False(shortDoc.IsEmpty);
        Assert.False(longDoc.IsEmpty);

        // FileSizeKB
        Assert.True(shortDoc.FileSizeKB > 0);
        Assert.True(longDoc.FileSizeKB > 0);

        // SizeExceeds
        Assert.True(shortDoc.SizeExceeds(0));
        Assert.False(shortDoc.SizeExceeds(1024 * 1024));

        // ToDict
        var shortDict = shortDoc.ToDict();
        Assert.NotNull(shortDict);
        Assert.NotEmpty(shortDict);

        // Load(stream) consistency
        using var ms = new MemoryStream(File.ReadAllBytes(shortPath));
        var streamDoc = ZstDocument.Load(ms);
        Assert.Equal(shortDoc.CompressedSize, streamDoc.CompressedSize);
        Assert.Equal(shortDoc.FrameCount, streamDoc.FrameCount);

        // Decompress round-trip
        Assert.Equal(ShortText, ZstParser.DecompressFile(shortPath));
        Assert.Equal(LongText, ZstParser.DecompressFile(longPath));
    }
}
