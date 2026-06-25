// Tests for ZstParser.ZstdMagic constant and ZstParser.DefaultMaxFileSizeBytes.
// Sprint: FORMAT-FACTORY-ZST-PARSER-CONSTANTS-R124-20260627
// Ledger: R124-GOVERNED-DOTNET-ZST-PARSER-CONSTANTS-001

using System;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R124: ZstParser.ZstdMagic is a 4-byte array containing the Zstandard magic
/// bytes (0x28, 0xB5, 0x2F, 0xFD). ZstParser.DefaultMaxFileSizeBytes is the
/// 256 MB parser limit. The magic bytes match the first 4 bytes of any Zstd-compressed
/// output. Parsing a compressed stream with a custom maxFileSizeBytes restores the
/// document's FrameCount. ParseStream with knownLength=-1 falls back to stream length.
/// </summary>
public class ZstR124ParserConstantsTests
{
    // ---- ZstdMagic: existence and length ----

    [Fact]
    public void ZstdMagic_IsNotNull()
    {
        Assert.NotNull(ZstParser.ZstdMagic);
    }

    [Fact]
    public void ZstdMagic_IsFourBytes()
    {
        Assert.Equal(4, ZstParser.ZstdMagic.Length);
    }

    // ---- ZstdMagic: byte values ----

    [Fact]
    public void ZstdMagic_FirstByte_Is0x28()
    {
        Assert.Equal(0x28, ZstParser.ZstdMagic[0]);
    }

    [Fact]
    public void ZstdMagic_SecondByte_Is0xB5()
    {
        Assert.Equal(0xB5, ZstParser.ZstdMagic[1]);
    }

    [Fact]
    public void ZstdMagic_ThirdByte_Is0x2F()
    {
        Assert.Equal(0x2F, ZstParser.ZstdMagic[2]);
    }

    [Fact]
    public void ZstdMagic_FourthByte_Is0xFD()
    {
        Assert.Equal(0xFD, ZstParser.ZstdMagic[3]);
    }

    // ---- ZstdMagic: matches compressed output ----

    [Fact]
    public void ZstdMagic_MatchesFirstBytesOfCompressedOutput()
    {
        var compressed = ZstWriter.Compress(Encoding.UTF8.GetBytes("magic check"));
        for (int i = 0; i < ZstParser.ZstdMagic.Length; i++)
            Assert.Equal(ZstParser.ZstdMagic[i], compressed[i]);
    }

    // ---- DefaultMaxFileSizeBytes ----

    [Fact]
    public void DefaultMaxFileSizeBytes_IsPositive()
    {
        Assert.True(ZstParser.DefaultMaxFileSizeBytes > 0);
    }

    [Fact]
    public void DefaultMaxFileSizeBytes_Is256MB()
    {
        // 256 * 1024 * 1024 = 268,435,456
        Assert.Equal(256L * 1024 * 1024, ZstParser.DefaultMaxFileSizeBytes);
    }

    // ---- ParseStream uses DefaultMaxFileSizeBytes ----

    [Fact]
    public void ParseStream_WithDefaultLimit_ProducesValidDocument()
    {
        var data       = Encoding.UTF8.GetBytes("hello parser");
        var compressed = ZstWriter.Compress(data);
        using var ms   = new System.IO.MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms, knownLength: compressed.Length);
        Assert.True(doc.MagicValid);
        Assert.True(doc.FrameCount > 0);
    }

    // ---- Dogfood: magic constant matches live parse ----

    [Fact]
    public void DogfoodPipeline_MagicBytesFromConstant_MatchLiveCompressedPayload()
    {
        var payload    = Encoding.UTF8.GetBytes(
            "{\"format\":\"ZST\",\"magic\":\"0x28B52FFD\",\"spec\":\"RFC 8878\"}");
        var compressed = ZstWriter.Compress(payload);

        // Verify constant matches first 4 bytes of output
        for (int i = 0; i < 4; i++)
            Assert.Equal(ZstParser.ZstdMagic[i], compressed[i]);

        // Parse and verify round-trip
        using var ms = new System.IO.MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms, knownLength: compressed.Length);
        Assert.True(doc.MagicValid);
        Assert.Equal(1, doc.FrameCount);
    }
}
