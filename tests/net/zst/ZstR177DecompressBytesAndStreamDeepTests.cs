// Tests for ZstParser.DecompressBytes, DecompressStream, ZstDocument.ToBytes deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R177

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R177: Tests for ZstParser.DecompressBytes, DecompressStream, ZstDocument.ToBytes deeper.
/// DecompressBytes(data): decompresses a byte array and returns the original string.
/// DecompressStream(stream): decompresses from a stream and returns the original string.
/// ZstDocument.ToBytes(): returns the compressed data as a byte array.
/// Covers: DecompressBytes correct string; DecompressBytes unicode correct;
/// DecompressBytes level1 correct; DecompressBytes level19 correct;
/// DecompressStream non-null; DecompressStream correct string;
/// DecompressStream from MemoryStream correct; ZstDocument.ToBytes non-null;
/// ZstDocument.ToBytes length positive; ZstDocument.ToBytes matches ParseFile CompressedSize;
/// dogfood CompressString->ToBytes->DecompressBytes->DecompressStream->Verify pipeline.
/// </summary>
public class ZstR177DecompressBytesAndStreamDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly string SampleText =
        "The compressed content with all sorts of characters: 1234567890 !@#$%^&*()";

    private static readonly string UnicodeText =
        "Unicode: こんにちは 世界 Ñoño résumé naïve café";

    public ZstR177DecompressBytesAndStreamDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR177_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // DecompressBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressBytes_CorrectString()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        var result = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, result);
    }

    [Fact]
    public void DecompressBytes_Unicode_CorrectString()
    {
        var compressed = ZstWriter.CompressString(UnicodeText);
        var result = ZstParser.DecompressBytes(compressed);
        Assert.Equal(UnicodeText, result);
    }

    [Fact]
    public void DecompressBytes_Level1_CorrectString()
    {
        var compressed = ZstWriter.CompressString(SampleText, 1);
        var result = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, result);
    }

    [Fact]
    public void DecompressBytes_Level19_CorrectString()
    {
        var compressed = ZstWriter.CompressString(SampleText, 19);
        var result = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, result);
    }

    [Fact]
    public void DecompressBytes_LongRepetitive_CorrectString()
    {
        var longText = new string('A', 5000);
        var compressed = ZstWriter.CompressString(longText);
        var result = ZstParser.DecompressBytes(compressed);
        Assert.Equal(longText, result);
    }

    // -------------------------------------------------------------------------
    // DecompressStream
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressStream_NonNull()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        using var ms = new MemoryStream(compressed);
        var result = ZstParser.DecompressStream(ms);
        Assert.NotNull(result);
    }

    [Fact]
    public void DecompressStream_CorrectString()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        using var ms = new MemoryStream(compressed);
        var result = ZstParser.DecompressStream(ms);
        Assert.Equal(SampleText, result);
    }

    [Fact]
    public void DecompressStream_Unicode_CorrectString()
    {
        var compressed = ZstWriter.CompressString(UnicodeText);
        using var ms = new MemoryStream(compressed);
        var result = ZstParser.DecompressStream(ms);
        Assert.Equal(UnicodeText, result);
    }

    [Fact]
    public void DecompressStream_FromFileStream_CorrectString()
    {
        var path = TempFile("stream.zst");
        ZstWriter.WriteToFile(SampleText, path);
        using var fs = File.OpenRead(path);
        var result = ZstParser.DecompressStream(fs);
        Assert.Equal(SampleText, result);
    }

    // -------------------------------------------------------------------------
    // ZstDocument.ToBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void ToBytes_NonNull()
    {
        var path = TempFile("tobytes.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var doc = ZstDocument.FromFile(path);
        Assert.NotNull(doc.ToBytes());
    }

    [Fact]
    public void ToBytes_LengthPositive()
    {
        var path = TempFile("tobytes2.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var doc = ZstDocument.FromFile(path);
        Assert.True(doc.ToBytes().Length > 0);
    }

    [Fact]
    public void ToBytes_LengthMatchesCompressedSize()
    {
        var path = TempFile("tobytes3.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var doc = ZstDocument.FromFile(path);
        Assert.Equal((int)doc.CompressedSize, doc.ToBytes().Length);
    }

    [Fact]
    public void ToBytes_Decompressible()
    {
        var path = TempFile("tobytes4.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var doc = ZstDocument.FromFile(path);
        var bytes = doc.ToBytes();
        var decompressed = ZstParser.DecompressBytes(bytes);
        Assert.Equal(SampleText, decompressed);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressString_ToBytes_DecompressBytes_DecompressStream_Verify_Pipeline()
    {
        // CompressString
        var compressed = ZstWriter.CompressString(SampleText);

        // DecompressBytes
        var text1 = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, text1);

        // DecompressStream
        using var ms = new MemoryStream(compressed);
        var text2 = ZstParser.DecompressStream(ms);
        Assert.Equal(SampleText, text2);

        // WriteToFile -> FromFile -> ToBytes -> DecompressBytes
        var path = TempFile("dogfood.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var doc = ZstDocument.FromFile(path);
        var bytes = doc.ToBytes();
        Assert.NotNull(bytes);
        var text3 = ZstParser.DecompressBytes(bytes);
        Assert.Equal(SampleText, text3);

        // DecompressStream from file
        using var fs = File.OpenRead(path);
        var text4 = ZstParser.DecompressStream(fs);
        Assert.Equal(SampleText, text4);

        // All four decompression paths agree
        Assert.Equal(text1, text2);
        Assert.Equal(text2, text3);
        Assert.Equal(text3, text4);
    }
}
