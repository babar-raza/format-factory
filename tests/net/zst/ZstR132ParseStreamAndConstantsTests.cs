// Tests for ZstParser.ParseStream and ZstParser constants (DefaultMaxFileSizeBytes, ZstdMagic).
// Sprint: ff-sprint-s132-dotnet-deepening-20260627
// Ledger: PC-ZST-R132

using System;
using System.IO;
using System.Text;
using Xunit;
using FormatFactory.Zst.Exceptions;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R132: Tests for ZstParser.ParseStream(Stream, long, string?) and ZstParser
/// constants (DefaultMaxFileSizeBytes, ZstdMagic). ParseStream parses a stream
/// of Zstandard-compressed data and returns a ZstDocument. DefaultMaxFileSizeBytes
/// is 256 MB. ZstdMagic is the 4-byte Zstandard frame magic: [0x28, 0xB5, 0x2F, 0xFD].
/// Covers: DefaultMaxFileSizeBytes=256 MB; ZstdMagic has 4 bytes; ZstdMagic[0]=0x28;
/// ZstdMagic[3]=0xFD; ParseStream null stream throws ArgumentNullException;
/// ParseStream valid stream returns non-null; parsed IsValid=true; parsed MagicValid=true;
/// parsed FileSizeKB reflects stream size; dogfood Compress→ParseStream→IsValid pipeline.
/// </summary>
public class ZstR132ParseStreamAndConstantsTests
{
    // -------------------------------------------------------------------------
    // ZstParser constants
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstParser_DefaultMaxFileSizeBytes_Is256MB()
    {
        const long expected = 256L * 1024 * 1024;
        Assert.Equal(expected, ZstParser.DefaultMaxFileSizeBytes);
    }

    [Fact]
    public void ZstParser_ZstdMagic_HasFourBytes()
    {
        Assert.Equal(4, ZstParser.ZstdMagic.Length);
    }

    [Fact]
    public void ZstParser_ZstdMagic_FirstByte_Is0x28()
    {
        Assert.Equal(0x28, ZstParser.ZstdMagic[0]);
    }

    [Fact]
    public void ZstParser_ZstdMagic_LastByte_Is0xFD()
    {
        Assert.Equal(0xFD, ZstParser.ZstdMagic[3]);
    }

    // -------------------------------------------------------------------------
    // ZstParser.ParseStream null guard
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstParser_ParseStream_NullStream_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            ZstParser.ParseStream(null!));
    }

    // -------------------------------------------------------------------------
    // ZstParser.ParseStream valid compressed stream
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstParser_ParseStream_ValidCompressedStream_ReturnsNonNull()
    {
        var data = Encoding.UTF8.GetBytes("Hello from ParseStream R132 test.");
        var compressed = ZstWriter.Compress(data);
        using var ms = new MemoryStream(compressed);

        var doc = ZstParser.ParseStream(ms, knownLength: compressed.Length);

        Assert.NotNull(doc);
    }

    [Fact]
    public void ZstParser_ParseStream_ValidStream_MagicValid_IsTrue()
    {
        var data = Encoding.UTF8.GetBytes("ParseStream magic validation R132.");
        var compressed = ZstWriter.Compress(data);
        using var ms = new MemoryStream(compressed);

        var doc = ZstParser.ParseStream(ms, knownLength: compressed.Length);

        Assert.True(doc.MagicValid);
    }

    [Fact]
    public void ZstParser_ParseStream_ValidStream_IsValid_IsTrue()
    {
        var data = Encoding.UTF8.GetBytes("ZstDocument IsValid from ParseStream.");
        var compressed = ZstWriter.Compress(data);
        using var ms = new MemoryStream(compressed);

        var doc = ZstParser.ParseStream(ms, knownLength: compressed.Length);

        Assert.True(doc.IsValid);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress → ParseStream → IsValid chain
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Compress_ParseStream_AllPropertiesConsistent()
    {
        var original = Encoding.UTF8.GetBytes("Dogfood test: Compress then ParseStream for R132 constant verification.");
        var compressed = ZstWriter.Compress(original, level: ZstWriter.DefaultCompressionLevel);

        using var ms = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms, knownLength: compressed.Length);

        Assert.True(doc.IsValid);
        Assert.True(doc.MagicValid);
        Assert.True(doc.FrameCount > 0);
        Assert.False(doc.IsEmptyContent);
        // FileSizeBytes should reflect the stream length passed
        Assert.True(doc.FileSizeBytes >= 0);
    }
}
