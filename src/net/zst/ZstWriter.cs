// FormatFactory.Zst -- Zstandard (.zst) file writer.
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
// Spec: IETF RFC 8878 (Zstandard Compression Format, 2021-02-01)

using System;
using System.IO;
using FormatFactory.Zst.Exceptions;
using ZstdSharp;

namespace FormatFactory.Zst;

/// <summary>
/// Writer for Zstandard compressed data (.zst).
///
/// Provides compress and decompress operations using the ZstdSharp managed
/// implementation of the Zstandard algorithm (RFC 8878).
///
/// Security posture:
///   - Compression level clamped to [1, 22]
///   - Decompression output guard (default 512 MB)
///   - Null input rejected at entry point
/// </summary>
public static class ZstWriter
{
    /// <summary>Default compression level (RFC 8878 recommends level 3).</summary>
    public const int DefaultCompressionLevel = 3;

    /// <summary>Minimum compression level (fastest, lowest ratio).</summary>
    public const int MinCompressionLevel = 1;

    /// <summary>Maximum compression level (slowest, highest ratio).</summary>
    public const int MaxCompressionLevel = 22;

    /// <summary>Default maximum decompressed output size (512 MB).</summary>
    public const long DefaultMaxDecompressedBytes = 512L * 1024 * 1024;

    // -------------------------------------------------------------------------
    // Compress
    // -------------------------------------------------------------------------

    /// <summary>
    /// Compress <paramref name="data"/> using Zstandard at the specified level.
    /// </summary>
    /// <param name="data">Input bytes to compress. Must not be null.</param>
    /// <param name="level">
    /// Compression level in [1, 22]. Values outside this range are clamped.
    /// Default: 3 (RFC 8878 recommended).
    /// </param>
    /// <returns>Compressed bytes including the Zstandard frame header and magic number.</returns>
    /// <exception cref="ArgumentNullException">Thrown if <paramref name="data"/> is null.</exception>
    /// <exception cref="ZstWriteException">Thrown if compression fails.</exception>
    public static byte[] Compress(byte[] data, int level = DefaultCompressionLevel)
    {
        if (data is null)
            throw new ArgumentNullException(nameof(data));

        level = Math.Clamp(level, MinCompressionLevel, MaxCompressionLevel);

        try
        {
            using var compressor = new Compressor(level);
            return compressor.Wrap(data).ToArray();
        }
        catch (Exception ex) when (ex is not ZstWriteException)
        {
            throw new ZstWriteException($"Compression failed: {ex.Message}", ex);
        }
    }

    /// <summary>
    /// Compress <paramref name="input"/> stream to <paramref name="output"/> stream.
    /// </summary>
    /// <param name="input">Source stream to compress. Must not be null.</param>
    /// <param name="output">Destination stream. Must not be null.</param>
    /// <param name="level">Compression level in [1, 22].</param>
    /// <exception cref="ArgumentNullException">Thrown if either stream is null.</exception>
    /// <exception cref="ZstWriteException">Thrown if compression fails.</exception>
    public static void Compress(Stream input, Stream output, int level = DefaultCompressionLevel)
    {
        if (input is null)  throw new ArgumentNullException(nameof(input));
        if (output is null) throw new ArgumentNullException(nameof(output));

        byte[] inputBytes;
        using (var ms = new MemoryStream())
        {
            input.CopyTo(ms);
            inputBytes = ms.ToArray();
        }

        byte[] compressed = Compress(inputBytes, level);
        output.Write(compressed, 0, compressed.Length);
    }

    /// <summary>
    /// Compress <paramref name="data"/> and write the result to <paramref name="destPath"/>.
    /// </summary>
    /// <param name="data">Input bytes to compress.</param>
    /// <param name="destPath">Destination file path. Parent directory must exist.</param>
    /// <param name="level">Compression level in [1, 22].</param>
    /// <exception cref="ArgumentNullException">Thrown if <paramref name="destPath"/> is null or empty.</exception>
    /// <exception cref="ZstWriteException">Thrown if compression or file write fails.</exception>
    public static void CompressToFile(byte[] data, string destPath, int level = DefaultCompressionLevel)
    {
        if (string.IsNullOrEmpty(destPath))
            throw new ArgumentNullException(nameof(destPath));

        byte[] compressed = Compress(data, level);

        try
        {
            File.WriteAllBytes(destPath, compressed);
        }
        catch (Exception ex) when (ex is not ZstWriteException)
        {
            throw new ZstWriteException($"Failed to write compressed file '{destPath}': {ex.Message}", ex);
        }
    }

    // -------------------------------------------------------------------------
    // Decompress
    // -------------------------------------------------------------------------

    /// <summary>
    /// Decompress Zstandard-compressed <paramref name="data"/>.
    /// </summary>
    /// <param name="data">Compressed input bytes. Must not be null.</param>
    /// <param name="maxDecompressedBytes">
    /// Maximum allowed decompressed output size in bytes.
    /// Default: 512 MB.
    /// </param>
    /// <returns>Decompressed bytes.</returns>
    /// <exception cref="ArgumentNullException">Thrown if <paramref name="data"/> is null.</exception>
    /// <exception cref="ZstWriteException">Thrown if decompression fails or output exceeds the guard.</exception>
    public static byte[] Decompress(byte[] data, long maxDecompressedBytes = DefaultMaxDecompressedBytes)
    {
        if (data is null)
            throw new ArgumentNullException(nameof(data));

        try
        {
            using var decompressor = new Decompressor();
            byte[] result = decompressor.Unwrap(data).ToArray();

            if (result.Length > maxDecompressedBytes)
                throw new ZstWriteException(
                    $"Decompressed output ({result.Length:N0} bytes) exceeds guard limit " +
                    $"({maxDecompressedBytes:N0} bytes).");

            return result;
        }
        catch (ZstWriteException)
        {
            throw;
        }
        catch (Exception ex)
        {
            throw new ZstWriteException($"Decompression failed: {ex.Message}", ex);
        }
    }

    /// <summary>
    /// Decompress <paramref name="input"/> stream to <paramref name="output"/> stream.
    /// </summary>
    /// <param name="input">Compressed source stream.</param>
    /// <param name="output">Decompressed destination stream.</param>
    /// <param name="maxDecompressedBytes">Maximum allowed decompressed output size.</param>
    /// <exception cref="ArgumentNullException">Thrown if either stream is null.</exception>
    /// <exception cref="ZstWriteException">Thrown if decompression fails.</exception>
    public static void Decompress(Stream input, Stream output,
        long maxDecompressedBytes = DefaultMaxDecompressedBytes)
    {
        if (input is null)  throw new ArgumentNullException(nameof(input));
        if (output is null) throw new ArgumentNullException(nameof(output));

        byte[] inputBytes;
        using (var ms = new MemoryStream())
        {
            input.CopyTo(ms);
            inputBytes = ms.ToArray();
        }

        byte[] decompressed = Decompress(inputBytes, maxDecompressedBytes);
        output.Write(decompressed, 0, decompressed.Length);
    }
}
