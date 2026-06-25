// FormatFactory.Zst -- Zstandard (.zst) file domain model.
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
// Spec: IETF RFC 8878 (Zstandard Compression Format, 2021-02-01)

namespace FormatFactory.Zst;

/// <summary>
/// Domain model for a Zstandard compressed file.
///
/// Spec reference: IETF RFC 8878 §3.1.1 (magic number), §3.1.2 (frame header).
/// </summary>
public sealed class ZstDocument
{
    /// <summary>Absolute path to the source file, or null if created from bytes.</summary>
    public string? FilePath { get; init; }

    /// <summary>File size in bytes.</summary>
    public long FileSizeBytes { get; init; }

    /// <summary>True if the file begins with the Zstandard magic bytes (0x28 0xB5 0x2F 0xFD).</summary>
    public bool MagicValid { get; init; }

    /// <summary>Number of Zstandard frames detected in the file.</summary>
    public int FrameCount { get; init; }

    /// <summary>Frame header descriptor byte from the first frame (RFC 8878 §3.1.2).</summary>
    public byte FrameHeaderDescriptor { get; init; }

    /// <summary>
    /// True if the file is a minimal single-frame Zstandard archive
    /// (FrameCount == 1 and FileSizeBytes &lt; 1024).
    /// </summary>
    public bool IsMinimalFrame { get; init; }

    /// <summary>
    /// True if the file size exceeds 100,000 bytes (100 KB).
    /// </summary>
    public bool SizeExceeds100K { get; init; }

    /// <summary>
    /// True if the file appears to have high compression (FileSizeBytes &lt; 512 bytes
    /// but FrameCount &gt; 0, suggesting highly compressible content).
    /// Heuristic only — does not decompress.
    /// </summary>
    public bool IsHighlyCompressed { get; init; }

    /// <summary>Estimated overhead bytes (file size minus 4-byte magic minus 1-byte FHD per frame).</summary>
    public long OverheadBytes { get; init; }

    /// <summary>Bytes per frame (FileSizeBytes / FrameCount), or 0 if no frames detected.</summary>
    public double BytesPerFrame { get; init; }

    /// <summary>
    /// Content type hint based on file path extension or embedded data.
    /// Returns "compressed_archive", "compressed_data", or "unknown".
    /// </summary>
    public string ContentTypeHint { get; init; } = "unknown";

    /// <summary>True if FileSizeBytes is 0 after skipping magic bytes.</summary>
    public bool IsEmptyContent { get; init; }

    // ---- Computed convenience properties ----

    /// <summary>True if FrameCount is greater than 1 (multi-frame archive).</summary>
    public bool HasMultipleFrames => FrameCount > 1;

    /// <summary>File size in kilobytes (FileSizeBytes / 1024.0).</summary>
    public double FileSizeKB => FileSizeBytes / 1024.0;

    /// <summary>
    /// True if the document appears structurally valid:
    /// magic bytes are present and at least one frame was detected.
    /// </summary>
    public bool IsValid => MagicValid && FrameCount > 0;

    /// <summary>
    /// Human-readable size label based on FileSizeBytes:
    /// "empty" (0), "tiny" (&lt;512 B), "small" (&lt;10 KB), "medium" (&lt;1 MB), "large" (>=1 MB).
    /// </summary>
    public string SizeLabel =>
        FileSizeBytes == 0 ? "empty" :
        FileSizeBytes < 512 ? "tiny" :
        FileSizeBytes < 10_240 ? "small" :
        FileSizeBytes < 1_048_576 ? "medium" :
        "large";
}
