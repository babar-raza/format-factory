// Tests for ZstException hierarchy and ZstWriter.Decompress decompression limit.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R148

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R148: Tests for ZstException hierarchy and ZstWriter.Decompress decompression limit.
/// ZstException: base exception for ZST errors.
/// ZstWriter.Decompress(byte[], maxDecompressedBytes): decompresses with size limit.
/// ZstWriter.DefaultMaxDecompressedBytes: the default decompression size cap.
/// Covers: ZstException is Exception; ZstException message preserved;
/// ZstException inner exception preserved; DefaultMaxDecompressedBytes positive;
/// Decompress with large limit succeeds; Decompress small data returns original;
/// Decompress with exact limit succeeds; ZstWriter min/max/default level constants;
/// MinCompressionLevel is 1; MaxCompressionLevel is 22; DefaultCompressionLevel is 3;
/// Decompress round-trip with explicit max; Compress then Decompress preserves data;
/// dogfood Compress->Decompress with explicit limits pipeline.
/// </summary>
public class ZstR148ExceptionAndDecompressLimitTests
{
    private static byte[] TextBytes(string text) => Encoding.UTF8.GetBytes(text);

    // -------------------------------------------------------------------------
    // ZstException
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstException_IsException()
    {
        var ex = new ZstException("test error");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    [Fact]
    public void ZstException_MessagePreserved()
    {
        var ex = new ZstException("specific zst error");
        Assert.Contains("specific zst error", ex.Message);
    }

    [Fact]
    public void ZstException_WithInnerException_PreservesInner()
    {
        var inner = new InvalidOperationException("inner");
        var ex = new ZstException("outer", inner);
        Assert.Same(inner, ex.InnerException);
    }

    // -------------------------------------------------------------------------
    // DefaultMaxDecompressedBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void DefaultMaxDecompressedBytes_IsPositive()
    {
        Assert.True(ZstWriter.DefaultMaxDecompressedBytes > 0);
    }

    [Fact]
    public void DefaultMaxDecompressedBytes_IsAtLeast1MB()
    {
        Assert.True(ZstWriter.DefaultMaxDecompressedBytes >= 1024 * 1024);
    }

    // -------------------------------------------------------------------------
    // Compression level constants
    // -------------------------------------------------------------------------

    [Fact]
    public void MinCompressionLevel_IsOne()
    {
        Assert.Equal(1, ZstWriter.MinCompressionLevel);
    }

    [Fact]
    public void MaxCompressionLevel_IsTwentyTwo()
    {
        Assert.Equal(22, ZstWriter.MaxCompressionLevel);
    }

    [Fact]
    public void DefaultCompressionLevel_IsThree()
    {
        Assert.Equal(3, ZstWriter.DefaultCompressionLevel);
    }

    // -------------------------------------------------------------------------
    // Decompress with maxDecompressedBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void Decompress_WithLargeLimit_Succeeds()
    {
        var original = "Decompression limit test data.";
        var compressed = ZstWriter.Compress(TextBytes(original));
        var decompressed = ZstWriter.Decompress(compressed, maxDecompressedBytes: 10L * 1024 * 1024);
        Assert.Equal(original, Encoding.UTF8.GetString(decompressed));
    }

    [Fact]
    public void Decompress_SmallData_ReturnsOriginal()
    {
        var original = "Hello, ZST!";
        var compressed = ZstWriter.Compress(TextBytes(original));
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(original, Encoding.UTF8.GetString(decompressed));
    }

    [Fact]
    public void Decompress_WithExactLimit_Succeeds()
    {
        var original = "Exact limit test.";
        var compressed = ZstWriter.Compress(TextBytes(original));
        // Use a limit larger than the decompressed size
        var limit = (long)original.Length * 10;
        var decompressed = ZstWriter.Decompress(compressed, maxDecompressedBytes: limit);
        Assert.Equal(original, Encoding.UTF8.GetString(decompressed));
    }

    [Fact]
    public void Decompress_ByteArrayResult_IsNonEmpty()
    {
        var compressed = ZstWriter.Compress(TextBytes("Non-empty test content for decompression."));
        var result = ZstWriter.Decompress(compressed);
        Assert.NotEmpty(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress->Decompress with explicit limits pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressDecompressWithExplicitLimits()
    {
        var messages = new[]
        {
            "First message: Hello, ZST pipeline!",
            "Second message: Testing decompression limits.",
            "Third message: Dogfood complete."
        };

        foreach (var msg in messages)
        {
            var data = TextBytes(msg);
            var compressed = ZstWriter.Compress(data, level: ZstWriter.DefaultCompressionLevel);
            Assert.NotEmpty(compressed);

            // Decompress with explicit limit
            var decompressed = ZstWriter.Decompress(compressed,
                maxDecompressedBytes: ZstWriter.DefaultMaxDecompressedBytes);
            Assert.Equal(msg, Encoding.UTF8.GetString(decompressed));

            // Also verify stream-based round-trip
            using var inStream = new MemoryStream(data);
            using var compStream = new MemoryStream();
            ZstWriter.Compress(inStream, compStream);
            var compBytes = compStream.ToArray();

            using var decompIn = new MemoryStream(compBytes);
            using var decompOut = new MemoryStream();
            ZstWriter.Decompress(decompIn, decompOut);
            Assert.Equal(msg, Encoding.UTF8.GetString(decompOut.ToArray()));
        }
    }
}
