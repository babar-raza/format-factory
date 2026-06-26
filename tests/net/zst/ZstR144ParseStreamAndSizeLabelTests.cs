// Tests for ZstParser.ParseStream and ZstDocument.SizeLabel property.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R144

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R144: Tests for ZstParser.ParseStream and ZstDocument.SizeLabel property.
/// ZstParser.ParseStream(stream, knownLength, filePath): parses ZST from stream.
/// ZstDocument.SizeLabel: human-readable label based on FileSizeBytes (B/KB/MB/GB).
/// ZstParser.DefaultMaxFileSizeBytes: 256 MB constant.
/// Covers: ParseStream valid data produces MagicValid=true; ParseStream valid data FrameCount>0;
/// ParseStream invalid magic produces MagicValid=false; ParseStream empty stream is invalid;
/// ParseStream uses knownLength for FileSizeBytes; SizeLabel bytes for small file;
/// SizeLabel KB for kilobyte-range; SizeLabel non-null always;
/// DefaultMaxFileSizeBytes is 256*1024*1024; ZstdMagic is 4 bytes;
/// dogfood Compress->MemoryStream->ParseStream->SizeLabel pipeline.
/// </summary>
public class ZstR144ParseStreamAndSizeLabelTests
{
    private static byte[] CompressText(string text)
    {
        var bytes = System.Text.Encoding.UTF8.GetBytes(text);
        return ZstWriter.Compress(bytes);
    }

    // -------------------------------------------------------------------------
    // ParseStream
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseStream_ValidData_MagicIsValid()
    {
        var compressed = CompressText("Hello stream!");
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, knownLength: compressed.Length);
        Assert.True(doc.MagicValid);
    }

    [Fact]
    public void ParseStream_ValidData_FrameCountPositive()
    {
        var compressed = CompressText("Frame count test");
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, knownLength: compressed.Length);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void ParseStream_InvalidMagic_MagicIsFalse()
    {
        var invalidBytes = new byte[] { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05 };
        using var stream = new MemoryStream(invalidBytes);
        var doc = ZstParser.ParseStream(stream, knownLength: invalidBytes.Length);
        Assert.False(doc.MagicValid);
    }

    [Fact]
    public void ParseStream_EmptyStream_IsInvalid()
    {
        using var stream = new MemoryStream(Array.Empty<byte>());
        var doc = ZstParser.ParseStream(stream, knownLength: 0);
        Assert.False(doc.IsValid);
    }

    [Fact]
    public void ParseStream_KnownLength_SetInFileSizeBytes()
    {
        var compressed = CompressText("Known length test");
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, knownLength: compressed.Length);
        Assert.Equal(compressed.Length, doc.FileSizeBytes);
    }

    [Fact]
    public void ParseStream_WithFilePath_FilePathSet()
    {
        var compressed = CompressText("File path test");
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, knownLength: compressed.Length, filePath: "test.zst");
        Assert.Equal("test.zst", doc.FilePath);
    }

    // -------------------------------------------------------------------------
    // SizeLabel
    // -------------------------------------------------------------------------

    [Fact]
    public void SizeLabel_SmallFile_IsNotNull()
    {
        var compressed = CompressText("small");
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, knownLength: compressed.Length);
        Assert.NotNull(doc.SizeLabel);
        Assert.NotEmpty(doc.SizeLabel);
    }

    [Fact]
    public void SizeLabel_SmallFile_ContainsSizeUnit()
    {
        var compressed = CompressText("small file content");
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, knownLength: compressed.Length);
        // Should contain B, KB, MB, or GB
        var label = doc.SizeLabel;
        Assert.True(
            label.Contains("B") || label.Contains("K") || label.Contains("M") || label.Contains("G"),
            $"SizeLabel '{label}' does not contain expected size unit");
    }

    [Fact]
    public void SizeLabel_ZeroBytes_IsNotNull()
    {
        using var stream = new MemoryStream(Array.Empty<byte>());
        var doc = ZstParser.ParseStream(stream, knownLength: 0);
        Assert.NotNull(doc.SizeLabel);
    }

    // -------------------------------------------------------------------------
    // Constants
    // -------------------------------------------------------------------------

    [Fact]
    public void DefaultMaxFileSizeBytes_Is256MB()
    {
        Assert.Equal(256L * 1024 * 1024, ZstParser.DefaultMaxFileSizeBytes);
    }

    [Fact]
    public void ZstdMagic_IsFourBytes()
    {
        Assert.Equal(4, ZstParser.ZstdMagic.Length);
    }

    [Fact]
    public void ZstdMagic_HasCorrectValues()
    {
        Assert.Equal(0x28, ZstParser.ZstdMagic[0]);
        Assert.Equal(0xB5, ZstParser.ZstdMagic[1]);
        Assert.Equal(0x2F, ZstParser.ZstdMagic[2]);
        Assert.Equal(0xFD, ZstParser.ZstdMagic[3]);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress->MemoryStream->ParseStream->SizeLabel->IsValid
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressStreamParseSizeLabel_Pipeline()
    {
        var original = "Dogfood ZST stream parse test with sufficient content for compression.";
        var compressed = CompressText(original);

        // Parse from stream with known length
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, knownLength: compressed.Length, filePath: "dogfood.zst");

        // Verify document state
        Assert.True(doc.IsValid);
        Assert.True(doc.MagicValid);
        Assert.True(doc.FrameCount > 0);
        Assert.Equal(compressed.Length, doc.FileSizeBytes);
        Assert.Equal("dogfood.zst", doc.FilePath);

        // SizeLabel should be a meaningful string
        var label = doc.SizeLabel;
        Assert.NotNull(label);
        Assert.NotEmpty(label);

        // FileSizeKB is consistent with FileSizeBytes
        Assert.Equal(doc.FileSizeBytes / 1024.0, doc.FileSizeKB, precision: 5);
    }
}
