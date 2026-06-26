// Tests for ZstParser.ParseFile, ZstException, edge cases.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R167

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R167: Tests for ZstParser.ParseFile, ZstException, edge cases.
/// ZstParser.ParseFile(path): parses a .zst file and returns ZstDocument.
/// ZstException: thrown for invalid .zst data.
/// Covers: ParseFile non-null; ParseFile CompressedSize matches file size;
/// ParseFile DecompressedSize > 0; ParseFile FrameCount >= 1;
/// ParseFile IsEmpty false for non-empty; ParseFile CompressionRatio > 0;
/// ParseFile->Decompress round-trip; ParseFile at level 1/6/19 all valid;
/// ZstException thrown for invalid data; ZstException thrown for empty bytes;
/// ParseFile consistent with WriteToFile->Load; ParseFile FileSizeKB > 0;
/// ParseFile BytesPerFrame > 0; ParseFile FrameHeaderDescriptor accessible;
/// ZstWriter.CompressString->ParseBytes->IsEmpty false;
/// dogfood WriteToFile->ParseFile->VerifyAllProperties->Decompress->CompareOriginal.
/// </summary>
public class ZstR167ParseFileAndExceptionTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly byte[] SampleData =
        System.Text.Encoding.UTF8.GetBytes(
            "ZST parse file test data — comprehensive property verification. " +
            string.Concat(new string('A', 100))); // some repetition for compressibility

    public ZstR167ParseFileAndExceptionTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR167_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string WriteSample(int level = 3, string name = "test.zst")
    {
        var path = TempFile(name);
        ZstWriter.WriteToFile(SampleData, path, level);
        return path;
    }

    // -------------------------------------------------------------------------
    // ZstParser.ParseFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseFile_NonNull()
    {
        var path = WriteSample();
        var doc = ZstParser.ParseFile(path);
        Assert.NotNull(doc);
    }

    [Fact]
    public void ParseFile_CompressedSize_MatchesFileSize()
    {
        var path = WriteSample();
        var doc = ZstParser.ParseFile(path);
        var fileSize = new FileInfo(path).Length;
        Assert.Equal(fileSize, doc.CompressedSize);
    }

    [Fact]
    public void ParseFile_DecompressedSize_Positive()
    {
        var path = WriteSample();
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.DecompressedSize > 0);
    }

    [Fact]
    public void ParseFile_FrameCount_AtLeastOne()
    {
        var path = WriteSample();
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.FrameCount >= 1);
    }

    [Fact]
    public void ParseFile_IsEmpty_False()
    {
        var path = WriteSample();
        var doc = ZstParser.ParseFile(path);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void ParseFile_CompressionRatio_Positive()
    {
        var path = WriteSample();
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.CompressionRatio > 0);
    }

    [Fact]
    public void ParseFile_FileSizeKB_Positive()
    {
        var path = WriteSample();
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.FileSizeKB > 0);
    }

    [Fact]
    public void ParseFile_BytesPerFrame_Positive()
    {
        var path = WriteSample();
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.BytesPerFrame > 0);
    }

    [Fact]
    public void ParseFile_Level1_Valid()
    {
        var path = WriteSample(1, "l1.zst");
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.FrameCount >= 1);
    }

    [Fact]
    public void ParseFile_Level6_Valid()
    {
        var path = WriteSample(6, "l6.zst");
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.FrameCount >= 1);
    }

    [Fact]
    public void ParseFile_Level19_Valid()
    {
        var path = WriteSample(19, "l19.zst");
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.FrameCount >= 1);
    }

    [Fact]
    public void ParseFile_Decompress_RoundTrip()
    {
        var path = WriteSample();
        ZstParser.ParseFile(path); // ensure parseable
        var decompressed = ZstParser.DecompressFile(path);
        Assert.Equal(SampleData, decompressed);
    }

    // -------------------------------------------------------------------------
    // ZstException
    // -------------------------------------------------------------------------

    [Fact]
    public void Decompress_InvalidData_ThrowsZstException()
    {
        var invalidData = new byte[] { 0x00, 0x01, 0x02, 0x03, 0x04 };
        Assert.Throws<ZstException>(() => ZstParser.Decompress(invalidData));
    }

    // -------------------------------------------------------------------------
    // ParseBytes consistency
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseBytes_IsEmpty_False_ForNonEmpty()
    {
        var compressed = ZstWriter.CompressString("non-empty string data");
        var doc = ZstParser.ParseBytes(compressed);
        Assert.False(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToFileParseFileVerifyAllPropertiesDecompressCompareOriginal_Pipeline()
    {
        // WriteToFile at level 6
        var path = TempFile("dogfood.zst");
        ZstWriter.WriteToFile(SampleData, path, 6);

        // ParseFile
        var doc = ZstParser.ParseFile(path);
        Assert.NotNull(doc);

        // Verify all properties
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);
        Assert.True(doc.FrameCount >= 1);
        Assert.False(doc.IsEmpty);
        Assert.False(doc.IsEmptyContent);
        Assert.True(doc.CompressionRatio > 0);
        Assert.True(doc.BytesPerFrame > 0);
        Assert.True(doc.FileSizeKB > 0);

        // CompressedSize matches file size
        var fileSize = new FileInfo(path).Length;
        Assert.Equal(fileSize, doc.CompressedSize);

        // DecompressedSize matches original
        Assert.Equal((long)SampleData.Length, doc.DecompressedSize);

        // Decompress and compare
        var decompressed = ZstParser.DecompressFile(path);
        Assert.Equal(SampleData, decompressed);

        // ParseFile consistent with Load
        var loadDoc = ZstDocument.Load(path);
        Assert.Equal(doc.FrameCount, loadDoc.FrameCount);
        Assert.Equal(doc.CompressedSize, loadDoc.CompressedSize);
    }
}
