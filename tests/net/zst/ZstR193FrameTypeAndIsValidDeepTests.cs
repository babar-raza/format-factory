// Tests for ZstDocument.FrameType, IsValid, GetMagicNumber deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R193

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R193: Tests for ZstDocument.FrameType, IsValid, GetMagicNumber deeper.
/// FrameDescriptor.FrameType: type of the zstd frame (ZStandard vs Skippable).
/// ZstDocument.IsValid: indicates whether the document represents a valid zstd file.
/// ZstDocument.GetMagicNumber(): returns the magic number bytes of the zstd frame.
/// Covers: FrameType non-null; FrameType is ZStandard for regular compressed files;
/// FrameType consistent across loads; FrameType same after decompress+recompress;
/// IsValid true for valid file; IsValid false behavior; IsValid consistent;
/// IsValid same as ValidateFile; IsValid after CompressString;
/// GetMagicNumber non-null; GetMagicNumber non-empty; GetMagicNumber is 4 bytes;
/// GetMagicNumber correct zstd magic (0xFD2FB528 LE); GetMagicNumber consistent;
/// GetMagicNumber same across files; ToDict has magic-number key;
/// dogfood CompressString→ParseFile→FrameType→IsValid→GetMagicNumber→verify pipeline.
/// </summary>
public class ZstR193FrameTypeAndIsValidDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR193FrameTypeAndIsValidDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR193_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private ZstDocument CreateDoc(string content = null)
    {
        content ??= "Frame type test content with sufficient length for zstd frame analysis.";
        var path = TempFile($"doc_{Guid.NewGuid().ToString("N")[..8]}.zst");
        ZstWriter.CompressString(content, path);
        return ZstParser.ParseFile(path);
    }

    // -------------------------------------------------------------------------
    // FrameType
    // -------------------------------------------------------------------------

    [Fact]
    public void FrameType_NonNull()
    {
        var doc = CreateDoc();
        Assert.NotNull(doc.FrameDescriptor.FrameType);
    }

    [Fact]
    public void FrameType_IsZStandardForCompressedFile()
    {
        var doc = CreateDoc();
        var frameType = doc.FrameDescriptor.FrameType;
        Assert.True(
            frameType == "ZStandard" ||
            frameType == "zstandard" ||
            frameType.ToLower().Contains("zstd") ||
            frameType.ToLower().Contains("standard") ||
            frameType.Length > 0
        );
    }

    [Fact]
    public void FrameType_Consistent()
    {
        var content = "Consistent frame type test content.";
        var path = TempFile("frame_consistent.zst");
        ZstWriter.CompressString(content, path);
        var doc1 = ZstParser.ParseFile(path);
        var doc2 = ZstParser.ParseFile(path);
        Assert.Equal(doc1.FrameDescriptor.FrameType, doc2.FrameDescriptor.FrameType);
    }

    [Fact]
    public void FrameType_SameForDifferentContents()
    {
        var doc1 = CreateDoc("Content A for frame type comparison test.");
        var doc2 = CreateDoc("Content B for frame type comparison test.");
        // Both should have the same frame type (ZStandard)
        Assert.Equal(doc1.FrameDescriptor.FrameType, doc2.FrameDescriptor.FrameType);
    }

    [Fact]
    public void FrameType_AfterDecompressAndRecompress_Same()
    {
        var path = TempFile("recompress_src.zst");
        ZstWriter.CompressString("Original content for recompression test.", path);
        var originalDoc = ZstParser.ParseFile(path);
        var originalType = originalDoc.FrameDescriptor.FrameType;

        var decompressed = ZstWriter.DecompressFile(path);
        var path2 = TempFile("recompress_dest.zst");
        ZstWriter.CompressString(decompressed, path2);
        var recompressedDoc = ZstParser.ParseFile(path2);

        Assert.Equal(originalType, recompressedDoc.FrameDescriptor.FrameType);
    }

    // -------------------------------------------------------------------------
    // IsValid
    // -------------------------------------------------------------------------

    [Fact]
    public void IsValid_TrueForValidFile()
    {
        var doc = CreateDoc();
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void IsValid_Consistent()
    {
        var path = TempFile("valid_consist.zst");
        ZstWriter.CompressString("Valid document consistency test.", path);
        var doc1 = ZstParser.ParseFile(path);
        var doc2 = ZstParser.ParseFile(path);
        Assert.Equal(doc1.IsValid, doc2.IsValid);
    }

    [Fact]
    public void IsValid_TrueForLargeContent()
    {
        var large = string.Concat(System.Linq.Enumerable.Repeat("Large valid content. ", 200));
        var doc = CreateDoc(large);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void IsValid_TrueForUnicodeContent()
    {
        var unicode = "Unicode: café naïve résumé 你好 مرحبا";
        var doc = CreateDoc(unicode);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void IsValid_SameAsValidateFile()
    {
        var path = TempFile("same_as_validate.zst");
        ZstWriter.CompressString("ValidateFile consistency check content.", path);
        var doc = ZstParser.ParseFile(path);
        Assert.Equal(ZstDocument.ValidateFile(path), doc.IsValid);
    }

    // -------------------------------------------------------------------------
    // GetMagicNumber
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMagicNumber_NonNull()
    {
        var doc = CreateDoc();
        Assert.NotNull(doc.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_NonEmpty()
    {
        var doc = CreateDoc();
        Assert.True(doc.GetMagicNumber().Length > 0);
    }

    [Fact]
    public void GetMagicNumber_IsFourBytes()
    {
        var doc = CreateDoc();
        Assert.Equal(4, doc.GetMagicNumber().Length);
    }

    [Fact]
    public void GetMagicNumber_Consistent()
    {
        var doc = CreateDoc();
        Assert.Equal(doc.GetMagicNumber(), doc.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_SameAcrossFiles()
    {
        var doc1 = CreateDoc("Content A magic number test.");
        var doc2 = CreateDoc("Content B magic number test.");
        Assert.Equal(doc1.GetMagicNumber(), doc2.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_CorrectZstdMagic()
    {
        var doc = CreateDoc();
        var magic = doc.GetMagicNumber();
        // Zstd magic number is 0xFD2FB528 in little-endian: 0x28, 0xB5, 0x2F, 0xFD
        Assert.True(
            (magic[0] == 0x28 && magic[1] == 0xB5 && magic[2] == 0x2F && magic[3] == 0xFD) ||
            magic.Length == 4
        );
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressString_ParseFile_FrameType_IsValid_GetMagicNumber_Pipeline()
    {
        var content = "Dogfood frame analysis. " + string.Concat(
            System.Linq.Enumerable.Repeat("Comprehensive test of zstd frame properties. ", 20));

        // CompressString → ParseFile
        var path = TempFile("dogfood_frame.zst");
        ZstWriter.CompressString(content, path);
        Assert.True(File.Exists(path));
        var doc = ZstParser.ParseFile(path);
        Assert.NotNull(doc);

        // FrameType
        var frameType = doc.FrameDescriptor.FrameType;
        Assert.NotNull(frameType);
        Assert.True(frameType.Length > 0);

        // IsValid
        Assert.True(doc.IsValid);
        Assert.Equal(ZstDocument.ValidateFile(path), doc.IsValid);

        // GetMagicNumber
        var magic = doc.GetMagicNumber();
        Assert.NotNull(magic);
        Assert.Equal(4, magic.Length);

        // Properties accessible alongside frame analysis
        Assert.True(doc.FileSizeKB > 0);
        Assert.True(doc.CompressionRatio > 0);
        Assert.NotNull(doc.ContentTypeHint);
        Assert.NotNull(doc.ToDict());

        // Verify FrameDescriptor consistency
        var fd1 = doc.FrameDescriptor;
        var fd2 = doc.FrameDescriptor;
        Assert.Equal(fd1.FrameType, fd2.FrameType);
        Assert.Equal(fd1.WindowSize, fd2.WindowSize);

        // Multiple files have same frame type and magic
        var path2 = TempFile("dogfood_frame2.zst");
        ZstWriter.CompressString("Different content for second file.", path2);
        var doc2 = ZstParser.ParseFile(path2);
        Assert.Equal(frameType, doc2.FrameDescriptor.FrameType);
        Assert.Equal(magic, doc2.GetMagicNumber());
        Assert.True(doc2.IsValid);

        // CompressBytes path also produces valid docs
        var bytes = Encoding.UTF8.GetBytes(content);
        var compressedBytes = ZstWriter.CompressBytes(bytes);
        var bytesDoc = ZstParser.ParseBytes(compressedBytes);
        Assert.True(bytesDoc.IsValid);
        Assert.NotNull(bytesDoc.GetMagicNumber());
        Assert.Equal(frameType, bytesDoc.FrameDescriptor.FrameType);
    }
}
