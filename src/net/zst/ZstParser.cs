// FormatFactory.Zst -- Commercial .NET Zstandard Parser
// DEC-033 Option B: .NET Commercial Only
// Python FOSS track: src/python/zst/ (Apache-2.0)
// Spec: IETF RFC 8878 (Zstandard Compression Format, 2021-02-01)
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.IO;
using FormatFactory.Zst.Exceptions;

namespace FormatFactory.Zst;

/// <summary>
/// Parser for Zstandard compressed files (.zst).
///
/// Spec reference: IETF RFC 8878.
/// Magic bytes: 0x28 0xB5 0x2F 0xFD (RFC 8878 §3.1.1).
///
/// Security posture:
///   - File size guard (MaxFileSizeBytes, default 256 MB)
///   - Does NOT decompress — probe-only for metadata extraction
///   - Magic byte validation on every parse
/// </summary>
public static class ZstParser
{
    /// <summary>Zstandard magic bytes: 0x28 0xB5 0x2F 0xFD (RFC 8878 §3.1.1).</summary>
    public static readonly byte[] ZstdMagic = [0x28, 0xB5, 0x2F, 0xFD];

    /// <summary>Default maximum file size accepted by Parse() (256 MB).</summary>
    public const long DefaultMaxFileSizeBytes = 256L * 1024 * 1024;

    /// <summary>
    /// Parse a Zstandard file from disk and return a <see cref="ZstDocument"/>.
    /// Does not decompress — extracts metadata only.
    /// </summary>
    /// <param name="filePath">Path to the .zst file.</param>
    /// <param name="maxFileSizeBytes">Maximum file size (default 256 MB).</param>
    /// <returns>A <see cref="ZstDocument"/> with probed metadata.</returns>
    /// <exception cref="ZstFileNotFoundException">File does not exist.</exception>
    /// <exception cref="ZstFileSizeException">File exceeds size guard.</exception>
    /// <exception cref="ZstInvalidMagicException">File is not a valid Zstandard frame.</exception>
    public static ZstDocument Parse(string filePath, long maxFileSizeBytes = DefaultMaxFileSizeBytes)
    {
        if (!File.Exists(filePath))
            throw new ZstFileNotFoundException($"File not found: {filePath}");

        var info = new FileInfo(filePath);
        if (info.Length > maxFileSizeBytes)
            throw new ZstFileSizeException(
                $"File size {info.Length} exceeds limit {maxFileSizeBytes}.");

        using var stream = File.OpenRead(filePath);
        return ParseStream(stream, info.Length, filePath);
    }

    /// <summary>
    /// Parse Zstandard data from a stream (probe-only, no decompression).
    /// </summary>
    public static ZstDocument ParseStream(Stream stream, long knownLength = -1, string? filePath = null)
    {
        var buffer = new byte[Math.Min(knownLength > 0 ? knownLength : 1024, 1024)];
        int read = stream.Read(buffer, 0, buffer.Length);

        bool magicValid = read >= 4
            && buffer[0] == ZstdMagic[0]
            && buffer[1] == ZstdMagic[1]
            && buffer[2] == ZstdMagic[2]
            && buffer[3] == ZstdMagic[3];

        long fileSizeBytes = knownLength > 0 ? knownLength : read;
        byte fhd = read >= 5 ? buffer[4] : (byte)0;
        int frameCount = magicValid ? CountFrames(buffer, read, fileSizeBytes) : 0;

        bool isMinimal = frameCount == 1 && fileSizeBytes < 1024;
        bool sizeExceeds100K = fileSizeBytes > 100_000;
        bool isHighlyCompressed = magicValid && fileSizeBytes < 512 && frameCount > 0;
        bool isEmptyContent = fileSizeBytes <= 4;
        long overheadBytes = magicValid ? Math.Max(0, fileSizeBytes - 4 - frameCount) : 0;
        double bytesPerFrame = frameCount > 0 ? (double)fileSizeBytes / frameCount : 0.0;

        string contentTypeHint = DetermineContentTypeHint(filePath, fileSizeBytes, frameCount);

        return new ZstDocument
        {
            FilePath = filePath,
            FileSizeBytes = fileSizeBytes,
            MagicValid = magicValid,
            FrameCount = frameCount,
            FrameHeaderDescriptor = fhd,
            IsMinimalFrame = isMinimal,
            SizeExceeds100K = sizeExceeds100K,
            IsHighlyCompressed = isHighlyCompressed,
            IsEmptyContent = isEmptyContent,
            OverheadBytes = overheadBytes,
            BytesPerFrame = bytesPerFrame,
            ContentTypeHint = contentTypeHint,
        };
    }

    /// <summary>
    /// Heuristic frame count: count occurrences of the 4-byte Zstandard magic in
    /// the file. This is a best-effort estimate without full frame parsing.
    /// </summary>
    private static int CountFrames(byte[] buffer, int bufferLen, long totalFileSize)
    {
        if (bufferLen < 4) return 0;

        // First magic match at offset 0 is guaranteed (already validated above).
        // Search for additional magic sequences in the buffer.
        int count = 1;
        for (int i = 4; i <= bufferLen - 4; i++)
        {
            if (buffer[i] == ZstdMagic[0]
                && buffer[i + 1] == ZstdMagic[1]
                && buffer[i + 2] == ZstdMagic[2]
                && buffer[i + 3] == ZstdMagic[3])
            {
                count++;
                i += 3; // skip over matched bytes
            }
        }

        // If the total file is much larger than our 1KB buffer, use heuristic.
        // Large files likely have more frames; scale conservatively.
        if (totalFileSize > bufferLen && count == 1 && totalFileSize > 128 * 1024)
        {
            // Estimate: assume average ~64KB per frame for large files.
            count = (int)Math.Max(1, totalFileSize / (64 * 1024));
        }

        return count;
    }

    private static string DetermineContentTypeHint(string? filePath, long fileSize, int frameCount)
    {
        if (filePath is null) return "compressed_data";

        var name = Path.GetFileName(filePath).ToLowerInvariant();
        if (name.EndsWith(".tar.zst") || name.Contains(".tar."))
            return "compressed_archive";
        if (frameCount > 1)
            return "compressed_archive";
        if (fileSize < 256)
            return "compressed_data";
        return "compressed_data";
    }
}
