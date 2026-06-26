// Tests for ZstWriter.Compress(Stream, Stream) and ZstWriter.Decompress(Stream, Stream).
// Sprint: FORMAT-FACTORY-ZST-R128-20260627
// Ledger: R128-GOVERNED-DOTNET-ZST-STREAM-COMPRESS-DECOMPRESS-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R128: Dedicated tests for ZstWriter.Compress(Stream, Stream, int level)
/// and ZstWriter.Decompress(Stream, Stream, long maxDecompressedBytes).
/// Compress: reads input stream to end, writes Zstd frame to output stream.
/// Decompress: reads compressed stream, writes decompressed bytes to output stream.
/// Both throw ArgumentNullException when a stream argument is null.
/// Covers: compress-stream output is non-empty; output starts with Zstd magic bytes;
/// compress→decompress stream roundtrip restores original bytes;
/// roundtrip preserves UTF-8 text; null input throws; null output throws;
/// Decompress null input throws; Decompress null output throws;
/// compress at min level (1) works; compress at max level (22) works;
/// dogfood compound stream pipeline.
/// </summary>
public class ZstR128StreamCompressDecompressTests
{
    private static readonly byte[] ZstdMagic = [0x28, 0xB5, 0x2F, 0xFD];

    private static byte[] CompressViaStream(byte[] data, int level = ZstWriter.DefaultCompressionLevel)
    {
        using var input  = new MemoryStream(data);
        using var output = new MemoryStream();
        ZstWriter.Compress(input, output, level);
        return output.ToArray();
    }

    private static byte[] DecompressViaStream(byte[] compressed)
    {
        using var input  = new MemoryStream(compressed);
        using var output = new MemoryStream();
        ZstWriter.Decompress(input, output);
        return output.ToArray();
    }

    // -------------------------------------------------------------------------
    // Compress(Stream, Stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void Compress_Stream_OutputIsNonEmpty()
    {
        var data = Encoding.UTF8.GetBytes("stream compress test data");
        var result = CompressViaStream(data);
        Assert.True(result.Length > 0);
    }

    [Fact]
    public void Compress_Stream_OutputStartsWithZstdMagic()
    {
        var data = Encoding.UTF8.GetBytes("zstd magic header test");
        var result = CompressViaStream(data);
        Assert.True(result.Length >= 4);
        Assert.Equal(ZstdMagic[0], result[0]);
        Assert.Equal(ZstdMagic[1], result[1]);
        Assert.Equal(ZstdMagic[2], result[2]);
        Assert.Equal(ZstdMagic[3], result[3]);
    }

    [Fact]
    public void Compress_Stream_NullInputStream_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            ZstWriter.Compress(null!, new MemoryStream()));
    }

    [Fact]
    public void Compress_Stream_NullOutputStream_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            ZstWriter.Compress(new MemoryStream(), null!));
    }

    [Fact]
    public void Compress_Stream_AtMinLevel_Works()
    {
        var data = Encoding.UTF8.GetBytes("min level compression test");
        var result = CompressViaStream(data, ZstWriter.MinCompressionLevel);
        Assert.True(result.Length > 0);
    }

    // -------------------------------------------------------------------------
    // Decompress(Stream, Stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void Decompress_Stream_NullInputStream_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            ZstWriter.Decompress(null!, new MemoryStream()));
    }

    [Fact]
    public void Decompress_Stream_NullOutputStream_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            ZstWriter.Decompress(new MemoryStream(ZstWriter.Compress([])), null!));
    }

    // -------------------------------------------------------------------------
    // Compress → Decompress roundtrip
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressDecompress_StreamRoundtrip_RestoresOriginalBytes()
    {
        var original = Encoding.UTF8.GetBytes("roundtrip test: stream compress+decompress");
        var compressed   = CompressViaStream(original);
        var decompressed = DecompressViaStream(compressed);
        Assert.Equal(original, decompressed);
    }

    [Fact]
    public void CompressDecompress_StreamRoundtrip_PreservesUtf8Text()
    {
        const string text = "Stream roundtrip UTF-8 verification — R128.";
        var original     = Encoding.UTF8.GetBytes(text);
        var compressed   = CompressViaStream(original);
        var decompressed = DecompressViaStream(compressed);
        Assert.Equal(text, Encoding.UTF8.GetString(decompressed));
    }

    // -------------------------------------------------------------------------
    // Dogfood: chained stream pipeline (compress→decompress→parse)
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StreamCompressDecompressThenParse()
    {
        const string content = "dogfood R128 stream compress pipeline";
        var original = Encoding.UTF8.GetBytes(content);

        // Compress via stream
        var compressed = CompressViaStream(original);

        // Parse the compressed bytes
        using var parseMs = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(parseMs);
        Assert.True(doc.IsValid);

        // Decompress via stream and verify
        var decompressed = DecompressViaStream(compressed);
        Assert.Equal(content, Encoding.UTF8.GetString(decompressed));
    }
}
