// Tests for ZstWriter round-trip via Compress/Decompress and CompressToFile.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R150

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R150: Tests for ZstWriter full round-trip and file-based operations.
/// Compress(byte[])->Decompress(byte[]): byte array round-trip.
/// Compress(Stream, Stream)->Decompress(Stream, Stream): stream round-trip.
/// CompressToFile(data, path): writes compressed to disk.
/// ZstParser.Parse(filePath): parses from actual file.
/// Covers: Byte round-trip exact match; Stream round-trip exact match;
/// CompressToFile file exists; CompressToFile Decompress exact match;
/// ZstParser.Parse on CompressToFile output IsValid; FilePath set after Parse;
/// FrameCount positive after Parse; MagicValid after Parse;
/// Compress preserves all UTF-8 characters; Compress empty array then Decompress;
/// Multiple round-trips consistent; large string round-trip;
/// dogfood Compress->CompressToFile->Parse->Decompress pipeline.
/// </summary>
public class ZstR150WriterRoundTripTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR150WriterRoundTripTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR150_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private static byte[] Utf8(string s) => Encoding.UTF8.GetBytes(s);
    private static string FromUtf8(byte[] b) => Encoding.UTF8.GetString(b);

    // -------------------------------------------------------------------------
    // Byte array round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void ByteRoundTrip_ExactMatch()
    {
        var original = "Exact byte round-trip test.";
        var compressed = ZstWriter.Compress(Utf8(original));
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(original, FromUtf8(decompressed));
    }

    [Fact]
    public void ByteRoundTrip_AllAsciiChars()
    {
        var sb = new StringBuilder();
        for (var c = 32; c < 127; c++) sb.Append((char)c);
        var original = sb.ToString();
        var compressed = ZstWriter.Compress(Utf8(original));
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(original, FromUtf8(decompressed));
    }

    [Fact]
    public void ByteRoundTrip_LargeString_ExactMatch()
    {
        var original = string.Concat(Enumerable.Repeat("Large string round-trip. ", 100));
        var compressed = ZstWriter.Compress(Utf8(original));
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(original, FromUtf8(decompressed));
    }

    [Fact]
    public void ByteRoundTrip_EmptyArray_Succeeds()
    {
        var compressed = ZstWriter.Compress(Array.Empty<byte>());
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Empty(decompressed);
    }

    [Fact]
    public void ByteRoundTrip_MultipleRoundsConsistent()
    {
        var original = "Consistent multiple round-trips.";
        for (var i = 0; i < 5; i++)
        {
            var compressed = ZstWriter.Compress(Utf8(original));
            var decompressed = ZstWriter.Decompress(compressed);
            Assert.Equal(original, FromUtf8(decompressed));
        }
    }

    // -------------------------------------------------------------------------
    // Stream round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void StreamRoundTrip_ExactMatch()
    {
        var original = "Stream exact round-trip test.";
        using var inputStream = new MemoryStream(Utf8(original));
        using var compressedStream = new MemoryStream();
        ZstWriter.Compress(inputStream, compressedStream);

        var compressed = compressedStream.ToArray();
        using var decompressInput = new MemoryStream(compressed);
        using var decompressOutput = new MemoryStream();
        ZstWriter.Decompress(decompressInput, decompressOutput);

        Assert.Equal(original, FromUtf8(decompressOutput.ToArray()));
    }

    // -------------------------------------------------------------------------
    // CompressToFile + ZstParser.Parse
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressToFile_FileExists()
    {
        var path = TempFile("exists.zst");
        ZstWriter.CompressToFile(Utf8("File exists test."), path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void CompressToFile_DecompressExactMatch()
    {
        var original = "CompressToFile round-trip.";
        var path = TempFile("rt.zst");
        ZstWriter.CompressToFile(Utf8(original), path);
        var fileBytes = File.ReadAllBytes(path);
        var decompressed = ZstWriter.Decompress(fileBytes);
        Assert.Equal(original, FromUtf8(decompressed));
    }

    [Fact]
    public void CompressToFile_ParseIsValid()
    {
        var path = TempFile("valid.zst");
        ZstWriter.CompressToFile(Utf8("Parse validity test."), path);
        var doc = ZstParser.Parse(path);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void CompressToFile_ParseFilePath_IsSet()
    {
        var path = TempFile("filepath.zst");
        ZstWriter.CompressToFile(Utf8("File path test."), path);
        var doc = ZstParser.Parse(path);
        Assert.Equal(path, doc.FilePath);
    }

    [Fact]
    public void CompressToFile_ParseFrameCount_Positive()
    {
        var path = TempFile("frames.zst");
        ZstWriter.CompressToFile(Utf8("Frame count test."), path);
        var doc = ZstParser.Parse(path);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void CompressToFile_ParseMagicValid_IsTrue()
    {
        var path = TempFile("magic.zst");
        ZstWriter.CompressToFile(Utf8("Magic valid test."), path);
        var doc = ZstParser.Parse(path);
        Assert.True(doc.MagicValid);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress->CompressToFile->Parse->Decompress pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressCompressToFileParseDecompressPipeline()
    {
        var original = "Dogfood: full ZST pipeline from byte[] to file to parse to decompress.";

        // Byte compress
        var compressedBytes = ZstWriter.Compress(Utf8(original));
        Assert.True(compressedBytes.Length > 0);

        // Verify byte decompression
        Assert.Equal(original, FromUtf8(ZstWriter.Decompress(compressedBytes)));

        // Write to file
        var path = TempFile("dogfood.zst");
        ZstWriter.CompressToFile(Utf8(original), path);
        Assert.True(File.Exists(path));

        // Parse
        var doc = ZstParser.Parse(path);
        Assert.True(doc.IsValid);
        Assert.True(doc.MagicValid);
        Assert.Equal(path, doc.FilePath);

        // Decompress file
        var fileBytes = File.ReadAllBytes(path);
        var decompressed = ZstWriter.Decompress(fileBytes);
        Assert.Equal(original, FromUtf8(decompressed));
    }
}
