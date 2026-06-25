// Tests for ZstWriter.Decompress(byte[], maxDecompressedBytes) — size limit enforcement.
// Sprint: FORMAT-FACTORY-ZST-R126-20260627
// Ledger: R126-GOVERNED-DOTNET-ZST-DECOMPRESS-LIMIT-001

using System;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R126: Tests for ZstWriter.Decompress(byte[] data, long maxDecompressedBytes) limit parameter.
/// Verifies: normal decompression succeeds, null data throws ArgumentNullException,
/// decompressed output exceeding maxDecompressedBytes throws ZstWriteException,
/// very tight limit blocks even tiny payloads, default limit is very large (permissive).
/// RFC 8878 basis: §3.1.1 decompression security guard.
/// </summary>
public class ZstR126DecompressLimitTests
{
    private static byte[] CompressString(string text) =>
        ZstWriter.Compress(Encoding.UTF8.GetBytes(text));

    // -------------------------------------------------------------------------
    // Normal decompression
    // -------------------------------------------------------------------------

    [Fact]
    public void Decompress_ValidData_ReturnsOriginalBytes()
    {
        const string original = "Hello ZST decompression limit test";
        var compressed = CompressString(original);
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(original, Encoding.UTF8.GetString(decompressed));
    }

    [Fact]
    public void Decompress_WithDefaultLimit_Succeeds()
    {
        const string payload = "Default limit decompression test R126";
        var compressed = CompressString(payload);
        // Should not throw — default limit is 512 MB
        var result = ZstWriter.Decompress(compressed, ZstWriter.DefaultMaxDecompressedBytes);
        Assert.Equal(payload, Encoding.UTF8.GetString(result));
    }

    [Fact]
    public void Decompress_ExplicitLargeLimit_Succeeds()
    {
        const string payload = "Explicit large limit test";
        var compressed = CompressString(payload);
        var result = ZstWriter.Decompress(compressed, 1024 * 1024); // 1 MB limit
        Assert.Equal(payload, Encoding.UTF8.GetString(result));
    }

    // -------------------------------------------------------------------------
    // Limit enforcement
    // -------------------------------------------------------------------------

    [Fact]
    public void Decompress_LimitTooSmall_ThrowsZstWriteException()
    {
        // Payload decompresses to >10 bytes; limit of 1 byte should trigger
        const string payload = "This is more than one byte";
        var compressed = CompressString(payload);
        Assert.Throws<ZstWriteException>(() => ZstWriter.Decompress(compressed, maxDecompressedBytes: 1));
    }

    [Fact]
    public void Decompress_LimitExactlyPayloadSize_Succeeds()
    {
        const string payload = "Exact limit";
        var bytes = Encoding.UTF8.GetBytes(payload);
        var compressed = ZstWriter.Compress(bytes);
        // Limit exactly equals decompressed size → should succeed
        var result = ZstWriter.Decompress(compressed, maxDecompressedBytes: bytes.Length);
        Assert.Equal(payload, Encoding.UTF8.GetString(result));
    }

    [Fact]
    public void Decompress_LimitOneLessThanPayload_ThrowsZstWriteException()
    {
        const string payload = "One less limit";
        var bytes = Encoding.UTF8.GetBytes(payload);
        var compressed = ZstWriter.Compress(bytes);
        // Limit one byte less than decompressed size → should throw
        Assert.Throws<ZstWriteException>(
            () => ZstWriter.Decompress(compressed, maxDecompressedBytes: bytes.Length - 1));
    }

    // -------------------------------------------------------------------------
    // Null guard
    // -------------------------------------------------------------------------

    [Fact]
    public void Decompress_NullData_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => ZstWriter.Decompress(null!));
    }

    // -------------------------------------------------------------------------
    // DefaultMaxDecompressedBytes constant
    // -------------------------------------------------------------------------

    [Fact]
    public void DefaultMaxDecompressedBytes_Is512MB()
    {
        Assert.Equal(512L * 1024 * 1024, ZstWriter.DefaultMaxDecompressedBytes);
    }

    [Fact]
    public void DefaultMaxDecompressedBytes_IsPositive()
    {
        Assert.True(ZstWriter.DefaultMaxDecompressedBytes > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: compress large-ish payload and decompress with various limits
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_JsonPayload_LimitBelowAndAbove()
    {
        const string json =
            """{"sprint":"S116","format":"ZST","test":"decompress_limit","data":"ABCDEFGHIJ"}""";
        var jsonBytes = Encoding.UTF8.GetBytes(json);
        var compressed = ZstWriter.Compress(jsonBytes);

        // Below limit: throws
        Assert.Throws<ZstWriteException>(
            () => ZstWriter.Decompress(compressed, maxDecompressedBytes: 10));

        // Above limit: succeeds
        var result = ZstWriter.Decompress(compressed, maxDecompressedBytes: jsonBytes.Length + 100);
        Assert.Equal(json, Encoding.UTF8.GetString(result));

        // Default limit: always succeeds for small payloads
        var defaultResult = ZstWriter.Decompress(compressed);
        Assert.Equal(json, Encoding.UTF8.GetString(defaultResult));
    }
}
