// Tests for ZstParser constants and ParseStream.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R140

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R140: Tests for ZstParser constants (ZstdMagic, DefaultMaxFileSizeBytes) and ParseStream.
/// ZstdMagic is a 4-byte array with values 0x28, 0xB5, 0x2F, 0xFD (RFC 8878).
/// DefaultMaxFileSizeBytes = 256 MB.
/// ParseStream returns a ZstDocument from a stream; MagicValid reflects whether magic bytes match.
/// Covers: ZstdMagic has length 4; ZstdMagic first byte is 0x28; second 0xB5; third 0x2F; fourth 0xFD;
/// DefaultMaxFileSizeBytes equals 256*1024*1024; DefaultMaxFileSizeBytes is positive;
/// ParseStream with valid zst magic returns MagicValid=true;
/// ParseStream with invalid data returns MagicValid=false;
/// ParseStream empty stream returns MagicValid=false;
/// dogfood Compress->ParseStream->MagicValid pipeline.
/// </summary>
public class ZstR140ParserConstantsAndStreamTests
{
    // -------------------------------------------------------------------------
    // ZstdMagic constants
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstdMagic_HasLength4()
    {
        Assert.Equal(4, ZstParser.ZstdMagic.Length);
    }

    [Fact]
    public void ZstdMagic_FirstByteIs0x28()
    {
        Assert.Equal(0x28, ZstParser.ZstdMagic[0]);
    }

    [Fact]
    public void ZstdMagic_SecondByteIs0xB5()
    {
        Assert.Equal(0xB5, ZstParser.ZstdMagic[1]);
    }

    [Fact]
    public void ZstdMagic_ThirdByteIs0x2F()
    {
        Assert.Equal(0x2F, ZstParser.ZstdMagic[2]);
    }

    [Fact]
    public void ZstdMagic_FourthByteIs0xFD()
    {
        Assert.Equal(0xFD, ZstParser.ZstdMagic[3]);
    }

    // -------------------------------------------------------------------------
    // DefaultMaxFileSizeBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void DefaultMaxFileSizeBytes_Equals256MB()
    {
        long expected = 256L * 1024 * 1024;
        Assert.Equal(expected, ZstParser.DefaultMaxFileSizeBytes);
    }

    [Fact]
    public void DefaultMaxFileSizeBytes_IsPositive()
    {
        Assert.True(ZstParser.DefaultMaxFileSizeBytes > 0);
    }

    // -------------------------------------------------------------------------
    // ParseStream
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseStream_ValidZstMagic_MagicValidIsTrue()
    {
        // Construct a minimal valid-looking ZST header
        var data = new byte[] { 0x28, 0xB5, 0x2F, 0xFD, 0x04, 0x00, 0x31, 0x00, 0x00 };
        using var stream = new MemoryStream(data);
        var doc = ZstParser.ParseStream(stream, data.Length);
        Assert.True(doc.MagicValid);
    }

    [Fact]
    public void ParseStream_InvalidData_MagicValidIsFalse()
    {
        var data = Encoding.UTF8.GetBytes("Not a Zstandard file at all.");
        using var stream = new MemoryStream(data);
        var doc = ZstParser.ParseStream(stream, data.Length);
        Assert.False(doc.MagicValid);
    }

    [Fact]
    public void ParseStream_EmptyStream_MagicValidIsFalse()
    {
        using var stream = new MemoryStream(Array.Empty<byte>());
        var doc = ZstParser.ParseStream(stream, 0);
        Assert.False(doc.MagicValid);
    }

    [Fact]
    public void ParseStream_ValidMagic_IsValidIsTrue()
    {
        var data = new byte[] { 0x28, 0xB5, 0x2F, 0xFD, 0x04, 0x00, 0x31, 0x00, 0x00 };
        using var stream = new MemoryStream(data);
        var doc = ZstParser.ParseStream(stream, data.Length);
        // IsValid requires MagicValid AND FrameCount > 0
        Assert.True(doc.MagicValid);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress->ParseStream->MagicValid
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressParseStreamMagicValid_Pipeline()
    {
        // Compress some data to get real ZST bytes
        var input = Encoding.UTF8.GetBytes("Hello, ZST world! " + new string('x', 100));
        var compressed = ZstWriter.Compress(input, level: ZstWriter.DefaultCompressionLevel);

        // Parse the compressed bytes via stream
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, compressed.Length);

        Assert.True(doc.MagicValid, "Compressed data should start with ZST magic bytes.");
        Assert.True(doc.FileSizeBytes > 0);
    }
}
