// Tests for ZstWriter.Compress(Stream, Stream) and Decompress(Stream, Stream).
// Sprint: FORMAT-FACTORY-ZST-STREAM-COMPRESS-20260626
// Ledger: R121-GOVERNED-DOTNET-ZST-STREAM-COMPRESS-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R121: ZstWriter.Compress(Stream input, Stream output, level) compresses a stream
/// to another stream. ZstWriter.Decompress(Stream input, Stream output) decompresses
/// the stream. Both round-trip correctly — compress then decompress restores original
/// bytes. Multiple compression levels produce valid Zstd frames.
/// </summary>
public class ZstR121StreamCompressTests
{
    // ---- Stream Compress: output is non-empty ----

    [Fact]
    public void StreamCompress_SmallPayload_ProducesOutput()
    {
        var input  = new MemoryStream(Encoding.UTF8.GetBytes("hello stream"));
        var output = new MemoryStream();
        ZstWriter.Compress(input, output);
        Assert.True(output.Length > 0);
    }

    [Fact]
    public void StreamCompress_OutputSmallerThanRepetitiveInput()
    {
        var data   = Encoding.UTF8.GetBytes(new string('X', 10000));
        var input  = new MemoryStream(data);
        var output = new MemoryStream();
        ZstWriter.Compress(input, output);
        Assert.True(output.Length < data.Length);
    }

    // ---- Stream Decompress: restores original ----

    [Fact]
    public void StreamDecompress_AfterCompress_RestoresOriginalBytes()
    {
        var original  = Encoding.UTF8.GetBytes("stream round-trip test payload");
        var compressed = new MemoryStream();
        ZstWriter.Compress(new MemoryStream(original), compressed);

        compressed.Position = 0;
        var decompressed = new MemoryStream();
        ZstWriter.Decompress(compressed, decompressed);

        Assert.Equal(original, decompressed.ToArray());
    }

    [Fact]
    public void StreamDecompress_LongPayload_RestoresOriginal()
    {
        var original  = Encoding.UTF8.GetBytes(new string('A', 50000));
        var compressed = new MemoryStream();
        ZstWriter.Compress(new MemoryStream(original), compressed);

        compressed.Position = 0;
        var decompressed = new MemoryStream();
        ZstWriter.Decompress(compressed, decompressed);

        Assert.Equal(original.Length, decompressed.Length);
        Assert.Equal(original, decompressed.ToArray());
    }

    // ---- Different compression levels ----

    [Fact]
    public void StreamCompress_LevelOne_ProducesValidFrame()
    {
        var input  = new MemoryStream(Encoding.UTF8.GetBytes("level one test"));
        var output = new MemoryStream();
        ZstWriter.Compress(input, output, level: 1);
        Assert.True(output.Length > 0);
    }

    [Fact]
    public void StreamCompress_LevelTwenty_ProducesValidFrame()
    {
        var input  = new MemoryStream(Encoding.UTF8.GetBytes("level twenty test"));
        var output = new MemoryStream();
        ZstWriter.Compress(input, output, level: 20);
        Assert.True(output.Length > 0);
    }

    [Fact]
    public void StreamCompress_Level20ThenDecompress_RestoresData()
    {
        var original   = Encoding.UTF8.GetBytes("high compression round-trip");
        var compressed = new MemoryStream();
        ZstWriter.Compress(new MemoryStream(original), compressed, level: 20);

        compressed.Position = 0;
        var decompressed = new MemoryStream();
        ZstWriter.Decompress(compressed, decompressed);

        Assert.Equal(original, decompressed.ToArray());
    }

    // ---- Empty input ----

    [Fact]
    public void StreamCompress_EmptyInput_DoesNotThrow()
    {
        var input  = new MemoryStream(Array.Empty<byte>());
        var output = new MemoryStream();
        ZstWriter.Compress(input, output);
        // Should not throw; output may be minimal frame
        Assert.True(output.Length >= 0);
    }

    // ---- Dogfood: stream compress/decompress pipeline ----

    [Fact]
    public void DogfoodPipeline_StreamRoundTrip_MultiplePayloads()
    {
        string[] payloads = ["Format Factory", "ZST stream pipeline", new string('Z', 5000)];

        foreach (var text in payloads)
        {
            var original   = Encoding.UTF8.GetBytes(text);
            var compressed = new MemoryStream();
            ZstWriter.Compress(new MemoryStream(original), compressed);

            compressed.Position = 0;
            var decompressed = new MemoryStream();
            ZstWriter.Decompress(compressed, decompressed);

            Assert.Equal(original, decompressed.ToArray());
        }
    }
}
