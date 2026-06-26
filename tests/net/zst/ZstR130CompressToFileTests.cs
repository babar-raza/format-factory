// Tests for ZstWriter.CompressToFile(byte[] data, string destPath, int level).
// Sprint: FORMAT-FACTORY-ZST-R130-20260627
// Ledger: R130-GOVERNED-DOTNET-ZST-COMPRESS-TO-FILE-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R130: Tests for ZstWriter.CompressToFile(byte[] data, string destPath, int level).
/// CompressToFile writes a valid Zstd-compressed file to the specified path.
/// The output starts with the Zstd magic bytes (0x28 0xB5 0x2F 0xFD).
/// Null destPath throws ArgumentNullException. Empty destPath throws ArgumentException.
/// Null data throws ArgumentNullException. Compression levels 1 and 22 produce valid files.
/// The written file can be parsed by ZstParser.Parse(). Default level produces smaller
/// output for repetitive data. Dogfood: CompressToFile then Parse then Decompress roundtrip.
/// Covers: output file exists; magic bytes correct; null destPath guard; null data guard;
/// min-level file valid; max-level file valid; output parseable; output non-empty;
/// dogfood CompressToFile → Parse → Decompress roundtrip.
/// </summary>
public class ZstR130CompressToFileTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), $"zst_r130_{Guid.NewGuid():N}.zst");

    private static byte[] TextBytes(string s) => Encoding.UTF8.GetBytes(s);

    // -------------------------------------------------------------------------
    // Basic output verification
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressToFile_OutputFileExists()
    {
        var path = TempPath();
        try
        {
            ZstWriter.CompressToFile(TextBytes("hello world"), path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void CompressToFile_OutputIsNonEmpty()
    {
        var path = TempPath();
        try
        {
            ZstWriter.CompressToFile(TextBytes("some content"), path);
            Assert.True(new FileInfo(path).Length > 0);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void CompressToFile_OutputStartsWithZstdMagic()
    {
        var path = TempPath();
        try
        {
            ZstWriter.CompressToFile(TextBytes("magic check"), path);
            var bytes = File.ReadAllBytes(path);
            Assert.Equal(0x28, bytes[0]);
            Assert.Equal(0xB5, bytes[1]);
            Assert.Equal(0x2F, bytes[2]);
            Assert.Equal(0xFD, bytes[3]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Null/empty guards
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressToFile_NullDestPath_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            ZstWriter.CompressToFile(TextBytes("data"), null!));
    }

    [Fact]
    public void CompressToFile_NullData_ThrowsArgumentNullException()
    {
        var path = TempPath();
        try
        {
            Assert.Throws<ArgumentNullException>(() =>
                ZstWriter.CompressToFile(null!, path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Compression level variants
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressToFile_MinLevel_ProducesValidFile()
    {
        var path = TempPath();
        try
        {
            ZstWriter.CompressToFile(TextBytes("min level data"), path,
                level: ZstWriter.MinCompressionLevel);
            Assert.True(File.Exists(path));
            Assert.True(new FileInfo(path).Length > 0);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void CompressToFile_MaxLevel_ProducesValidFile()
    {
        var path = TempPath();
        try
        {
            ZstWriter.CompressToFile(TextBytes("max level data"), path,
                level: ZstWriter.MaxCompressionLevel);
            Assert.True(File.Exists(path));
            Assert.True(new FileInfo(path).Length > 0);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Parseable output
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressToFile_OutputIsParseable()
    {
        var path = TempPath();
        try
        {
            ZstWriter.CompressToFile(TextBytes("parseable output test"), path);
            var doc = ZstParser.Parse(path);
            Assert.True(doc.IsValid);
            Assert.True(doc.MagicValid);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Dogfood: CompressToFile → Parse → Decompress roundtrip
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CompressToFile_Parse_Decompress_Roundtrip()
    {
        const string input = "dogfood R130 roundtrip: CompressToFile then ZstParser.Parse then Decompress";
        var path = TempPath();
        try
        {
            var originalBytes = TextBytes(input);

            // Step 1: compress to file
            ZstWriter.CompressToFile(originalBytes, path);

            // Step 2: parse the file to verify metadata
            var doc = ZstParser.Parse(path);
            Assert.True(doc.IsValid);
            Assert.True(doc.FrameCount >= 1);
            Assert.Equal(path, doc.FilePath);

            // Step 3: decompress back from the file bytes and verify roundtrip
            var compressedBytes = File.ReadAllBytes(path);
            var decompressed = ZstWriter.Decompress(compressedBytes);
            var restored = Encoding.UTF8.GetString(decompressed);
            Assert.Equal(input, restored);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
