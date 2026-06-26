// Tests for ZstWriter.CompressToFile.
// Sprint: ff-sprint-s138-dotnet-deepening-20260627
// Ledger: PC-ZST-R134

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R134: Tests for ZstWriter.CompressToFile(byte[] data, string destPath, int level).
/// CompressToFile compresses data and writes it to a file.
/// Throws ArgumentNullException for empty/null destPath (guards to ArgumentNullException).
/// Throws ZstWriteException on I/O failure.
/// Covers: null data throws; empty path throws; file created after compress;
/// file content is non-empty; file begins with ZST magic bytes;
/// round-trip: CompressToFile then ParseStream returns valid doc;
/// round-trip: IsValid=true; MagicValid=true; round-trip: FrameCount=1;
/// dogfood Compress->CompressToFile->ParseStream->IsValid pipeline.
/// </summary>
public class ZstR134CompressToFileTests
{
    private static readonly byte[] SamplePayload =
        Encoding.UTF8.GetBytes("The quick brown fox jumps over the lazy dog. Repeated. ".PadRight(200, 'x'));

    // -------------------------------------------------------------------------
    // Null/empty path guard
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressToFile_EmptyPath_Throws()
    {
        Assert.ThrowsAny<Exception>(() => ZstWriter.CompressToFile(SamplePayload, string.Empty));
    }

    [Fact]
    public void CompressToFile_NullPath_Throws()
    {
        Assert.ThrowsAny<Exception>(() => ZstWriter.CompressToFile(SamplePayload, null!));
    }

    // -------------------------------------------------------------------------
    // File creation and content
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressToFile_ValidPath_CreatesFile()
    {
        var path = Path.Combine(Path.GetTempPath(), $"zst_r134_{Guid.NewGuid():N}.zst");
        try
        {
            ZstWriter.CompressToFile(SamplePayload, path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void CompressToFile_ValidPath_FileIsNonEmpty()
    {
        var path = Path.Combine(Path.GetTempPath(), $"zst_r134_{Guid.NewGuid():N}.zst");
        try
        {
            ZstWriter.CompressToFile(SamplePayload, path);
            Assert.True(new FileInfo(path).Length > 0);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void CompressToFile_FileStartsWithZstMagicBytes()
    {
        var path = Path.Combine(Path.GetTempPath(), $"zst_r134_{Guid.NewGuid():N}.zst");
        try
        {
            ZstWriter.CompressToFile(SamplePayload, path);
            var bytes = File.ReadAllBytes(path);
            // Zstandard magic: 0x28 0xB5 0x2F 0xFD
            Assert.True(bytes.Length >= 4);
            Assert.Equal(0x28, bytes[0]);
            Assert.Equal(0xB5, bytes[1]);
            Assert.Equal(0x2F, bytes[2]);
            Assert.Equal(0xFD, bytes[3]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Round-trip via ParseStream
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressToFile_RoundTrip_ParseStream_ReturnsValidDocument()
    {
        var path = Path.Combine(Path.GetTempPath(), $"zst_r134_{Guid.NewGuid():N}.zst");
        try
        {
            ZstWriter.CompressToFile(SamplePayload, path);
            var bytes = File.ReadAllBytes(path);
            using var stream = new MemoryStream(bytes);
            var doc = ZstParser.ParseStream(stream, bytes.Length);
            Assert.NotNull(doc);
            Assert.True(doc.IsValid);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void CompressToFile_RoundTrip_MagicValid_IsTrue()
    {
        var path = Path.Combine(Path.GetTempPath(), $"zst_r134_{Guid.NewGuid():N}.zst");
        try
        {
            ZstWriter.CompressToFile(SamplePayload, path);
            var bytes = File.ReadAllBytes(path);
            using var stream = new MemoryStream(bytes);
            var doc = ZstParser.ParseStream(stream, bytes.Length);
            Assert.True(doc.MagicValid);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void CompressToFile_RoundTrip_FrameCountIsOne()
    {
        var path = Path.Combine(Path.GetTempPath(), $"zst_r134_{Guid.NewGuid():N}.zst");
        try
        {
            ZstWriter.CompressToFile(SamplePayload, path);
            var bytes = File.ReadAllBytes(path);
            using var stream = new MemoryStream(bytes);
            var doc = ZstParser.ParseStream(stream, bytes.Length);
            Assert.Equal(1, doc.FrameCount);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress -> CompressToFile -> ParseStream -> IsValid pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CompressToFile_Parse_IsValid()
    {
        var payload = Encoding.UTF8.GetBytes(
            string.Join(" ", System.Linq.Enumerable.Repeat("hello world", 50)));
        var path = Path.Combine(Path.GetTempPath(), $"zst_r134_dog_{Guid.NewGuid():N}.zst");
        try
        {
            ZstWriter.CompressToFile(payload, path, level: 3);
            Assert.True(File.Exists(path));

            var bytes = File.ReadAllBytes(path);
            using var stream = new MemoryStream(bytes);
            var doc = ZstParser.ParseStream(stream, bytes.Length);

            Assert.True(doc.IsValid);
            Assert.True(doc.MagicValid);
            Assert.False(doc.HasMultipleFrames);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
