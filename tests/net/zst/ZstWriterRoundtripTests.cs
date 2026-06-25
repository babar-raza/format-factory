// FormatFactory.Zst.Tests -- ZstWriter roundtrip and compress/decompress tests.
// QF-1-001: Verifies ZstWriter compress→decompress produces identical output.

using System;
using System.IO;
using System.Text;
using FormatFactory.Zst;
using FormatFactory.Zst.Exceptions;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>Roundtrip and unit tests for ZstWriter compress/decompress.</summary>
public class ZstWriterRoundtripTests
{
    // -------------------------------------------------------------------------
    // Compress → Decompress roundtrip
    // -------------------------------------------------------------------------

    [Fact]
    public void Compress_ThenDecompress_ProducesOriginalBytes()
    {
        byte[] original = Encoding.UTF8.GetBytes("Hello, Zstandard! Format Factory ZST roundtrip test.");
        byte[] compressed = ZstWriter.Compress(original);
        byte[] roundtripped = ZstWriter.Decompress(compressed);
        Assert.Equal(original, roundtripped);
    }

    [Fact]
    public void Compress_ThenDecompress_EmptyInput_RoundtripIsEmpty()
    {
        byte[] original = [];
        byte[] compressed = ZstWriter.Compress(original);
        byte[] roundtripped = ZstWriter.Decompress(compressed);
        Assert.Equal(original, roundtripped);
    }

    [Fact]
    public void Compress_ThenDecompress_BinaryData_RoundtripIdentical()
    {
        byte[] original = new byte[1024];
        for (int i = 0; i < original.Length; i++)
            original[i] = (byte)(i & 0xFF);
        byte[] compressed = ZstWriter.Compress(original);
        byte[] roundtripped = ZstWriter.Decompress(compressed);
        Assert.Equal(original, roundtripped);
    }

    [Fact]
    public void Compress_ThenDecompress_LargeRepetitiveInput_IsSmaller()
    {
        byte[] original = new byte[65536];
        for (int i = 0; i < original.Length; i++)
            original[i] = 0x42; // highly compressible
        byte[] compressed = ZstWriter.Compress(original);
        byte[] roundtripped = ZstWriter.Decompress(compressed);
        Assert.Equal(original, roundtripped);
        Assert.True(compressed.Length < original.Length, "Compressed output should be smaller for repetitive data");
    }

    // -------------------------------------------------------------------------
    // Compress() output contains valid Zstandard magic
    // -------------------------------------------------------------------------

    [Fact]
    public void Compress_Output_StartsWithZstMagicBytes()
    {
        byte[] original = Encoding.UTF8.GetBytes("test content for magic check");
        byte[] compressed = ZstWriter.Compress(original);
        Assert.True(compressed.Length >= 4);
        Assert.Equal(0x28, compressed[0]);
        Assert.Equal(0xB5, compressed[1]);
        Assert.Equal(0x2F, compressed[2]);
        Assert.Equal(0xFD, compressed[3]);
    }

    [Fact]
    public void Compress_WithParsedOutput_ZstParserRecognisesResult()
    {
        byte[] original = Encoding.UTF8.GetBytes("parseable compressed content");
        byte[] compressed = ZstWriter.Compress(original);
        string tmpPath = Path.GetTempFileName() + ".zst";
        try
        {
            File.WriteAllBytes(tmpPath, compressed);
            var doc = ZstParser.Parse(tmpPath);
            Assert.True(doc.MagicValid);
            Assert.True(doc.FrameCount >= 1);
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    // -------------------------------------------------------------------------
    // Stream overloads
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressStream_ThenDecompressStream_RoundtripProducesOriginal()
    {
        byte[] original = Encoding.UTF8.GetBytes("Stream overload roundtrip test content.");
        using var inStream = new MemoryStream(original);
        using var compressedStream = new MemoryStream();
        ZstWriter.Compress(inStream, compressedStream);

        compressedStream.Seek(0, SeekOrigin.Begin);
        using var decompressedStream = new MemoryStream();
        ZstWriter.Decompress(compressedStream, decompressedStream);
        Assert.Equal(original, decompressedStream.ToArray());
    }

    // -------------------------------------------------------------------------
    // CompressToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressToFile_ProducesReadableZstFile()
    {
        byte[] original = Encoding.UTF8.GetBytes("Content compressed to file.");
        string tmpPath = Path.GetTempFileName() + ".zst";
        try
        {
            ZstWriter.CompressToFile(original, tmpPath);
            Assert.True(File.Exists(tmpPath));
            byte[] fromFile = File.ReadAllBytes(tmpPath);
            byte[] roundtripped = ZstWriter.Decompress(fromFile);
            Assert.Equal(original, roundtripped);
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    // -------------------------------------------------------------------------
    // Compression levels
    // -------------------------------------------------------------------------

    [Theory]
    [InlineData(1)]
    [InlineData(3)]
    [InlineData(10)]
    [InlineData(22)]
    public void Compress_AtLevel_DecompressProducesOriginal(int level)
    {
        byte[] original = Encoding.UTF8.GetBytes($"Level {level} compression test.");
        byte[] compressed = ZstWriter.Compress(original, level);
        byte[] roundtripped = ZstWriter.Decompress(compressed);
        Assert.Equal(original, roundtripped);
    }

    [Fact]
    public void Compress_LevelBelowMin_ClampsToMin_StillWorks()
    {
        byte[] original = Encoding.UTF8.GetBytes("level clamping test");
        byte[] compressed = ZstWriter.Compress(original, level: -99);
        byte[] roundtripped = ZstWriter.Decompress(compressed);
        Assert.Equal(original, roundtripped);
    }

    [Fact]
    public void Compress_LevelAboveMax_ClampsToMax_StillWorks()
    {
        byte[] original = Encoding.UTF8.GetBytes("level clamping test high");
        byte[] compressed = ZstWriter.Compress(original, level: 9999);
        byte[] roundtripped = ZstWriter.Decompress(compressed);
        Assert.Equal(original, roundtripped);
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Compress_NullInput_Throws_ArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => ZstWriter.Compress(null!));
    }

    [Fact]
    public void Decompress_NullInput_Throws_ArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => ZstWriter.Decompress(null!));
    }

    [Fact]
    public void Decompress_RandomBytes_Throws_ZstWriteException()
    {
        byte[] garbage = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07];
        Assert.Throws<ZstWriteException>(() => ZstWriter.Decompress(garbage));
    }

    [Fact]
    public void CompressToFile_NullPath_Throws_ArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => ZstWriter.CompressToFile([], null!));
    }

    [Fact]
    public void CompressStream_NullInput_Throws_ArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => ZstWriter.Compress(null!, new MemoryStream()));
    }

    [Fact]
    public void CompressStream_NullOutput_Throws_ArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => ZstWriter.Compress(new MemoryStream(), null!));
    }
}
