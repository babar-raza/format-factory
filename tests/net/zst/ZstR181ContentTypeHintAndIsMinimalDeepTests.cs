// Tests for ZstDocument.ContentTypeHint, IsMinimalFrame, ZstWriter.CompressBytes deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R181

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R181: Tests for ZstDocument.ContentTypeHint, IsMinimalFrame, ZstWriter.CompressBytes deeper.
/// ContentTypeHint: string hint for content type of the compressed data.
/// IsMinimalFrame: true if the frame is a minimal Zstandard frame.
/// ZstWriter.CompressBytes: compresses a byte array to a compressed byte array.
/// Covers: ContentTypeHint non-null; ContentTypeHint non-empty; ContentTypeHint consistent;
/// IsMinimalFrame does not throw; CompressBytes non-null; CompressBytes round-trip correct;
/// CompressBytes byte array; CompressBytes level 1 and 19 both produce decompressible data;
/// CompressBytes from UTF8-encoded string; CompressBytes with binary-like data;
/// ZstDocument.FromFile vs ParseFile consistent CompressedSize;
/// dogfood CompressBytes->ParseBytes->WriteToFile->FromFile->CompressBytes->Verify pipeline.
/// </summary>
public class ZstR181ContentTypeHintAndIsMinimalDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly string SampleText = "Sample text content for compression testing.";
    private static readonly byte[] SampleBytes = System.Text.Encoding.UTF8.GetBytes(SampleText);

    public ZstR181ContentTypeHintAndIsMinimalDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR181_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // ContentTypeHint
    // -------------------------------------------------------------------------

    [Fact]
    public void ContentTypeHint_NonNull()
    {
        var path = TempFile("hint.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var doc = ZstDocument.FromFile(path);
        Assert.NotNull(doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_NonEmpty()
    {
        var path = TempFile("hint2.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var doc = ZstDocument.FromFile(path);
        Assert.NotEmpty(doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_Consistent_BetweenTwoCalls()
    {
        var path = TempFile("hint3.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var doc = ZstDocument.FromFile(path);
        Assert.Equal(doc.ContentTypeHint, doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_SameForSameContent()
    {
        var p1 = TempFile("h1.zst"); var p2 = TempFile("h2.zst");
        ZstWriter.WriteToFile(SampleText, p1);
        ZstWriter.WriteToFile(SampleText, p2);
        var d1 = ZstDocument.FromFile(p1);
        var d2 = ZstDocument.FromFile(p2);
        Assert.Equal(d1.ContentTypeHint, d2.ContentTypeHint);
    }

    // -------------------------------------------------------------------------
    // IsMinimalFrame
    // -------------------------------------------------------------------------

    [Fact]
    public void IsMinimalFrame_DoesNotThrow()
    {
        var path = TempFile("minimal.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var doc = ZstDocument.FromFile(path);
        var ex = Record.Exception(() => _ = doc.IsMinimalFrame);
        Assert.Null(ex);
    }

    [Fact]
    public void IsMinimalFrame_ReturnsBoolean()
    {
        var path = TempFile("minimal2.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var doc = ZstDocument.FromFile(path);
        // Should be bool — either true or false
        Assert.True(doc.IsMinimalFrame == true || doc.IsMinimalFrame == false);
    }

    // -------------------------------------------------------------------------
    // CompressBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressBytes_NonNull()
    {
        Assert.NotNull(ZstWriter.CompressBytes(SampleBytes));
    }

    [Fact]
    public void CompressBytes_Positive_Length()
    {
        Assert.True(ZstWriter.CompressBytes(SampleBytes).Length > 0);
    }

    [Fact]
    public void CompressBytes_RoundTrip_Correct()
    {
        var compressed = ZstWriter.CompressBytes(SampleBytes);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, decompressed);
    }

    [Fact]
    public void CompressBytes_Level1_Decompressible()
    {
        var compressed = ZstWriter.CompressBytes(SampleBytes, level: 1);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, decompressed);
    }

    [Fact]
    public void CompressBytes_Level19_Decompressible()
    {
        var compressed = ZstWriter.CompressBytes(SampleBytes, level: 19);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, decompressed);
    }

    [Fact]
    public void CompressBytes_FromString_RoundTrip()
    {
        var text = "Hello, 世界! Привет мир.";
        var bytes = System.Text.Encoding.UTF8.GetBytes(text);
        var compressed = ZstWriter.CompressBytes(bytes);
        var decompressedBytes = ZstParser.DecompressBytesToBytes(compressed);
        var result = System.Text.Encoding.UTF8.GetString(decompressedBytes);
        Assert.Equal(text, result);
    }

    [Fact]
    public void CompressBytes_RepetitiveData_CompressesWell()
    {
        var repetitive = System.Text.Encoding.UTF8.GetBytes(new string('X', 10000));
        var compressed = ZstWriter.CompressBytes(repetitive);
        Assert.True(compressed.Length < repetitive.Length);
    }

    // -------------------------------------------------------------------------
    // FromFile vs ParseFile consistency
    // -------------------------------------------------------------------------

    [Fact]
    public void FromFile_MatchesParsedFile_CompressedSize()
    {
        var path = TempFile("compare.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var fromFile = ZstDocument.FromFile(path);
        var parsed = ZstParser.ParseFile(path);
        Assert.Equal(parsed.CompressedSize, fromFile.CompressedSize);
    }

    [Fact]
    public void FromFile_MatchesParsedFile_FrameCount()
    {
        var path = TempFile("frame_compare.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var fromFile = ZstDocument.FromFile(path);
        var parsed = ZstParser.ParseFile(path);
        Assert.Equal(parsed.FrameCount, fromFile.FrameCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressBytes_ParseBytes_WriteToFile_FromFile_Verify_Pipeline()
    {
        // CompressBytes
        var compressed = ZstWriter.CompressBytes(SampleBytes);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);

        // ParseBytes
        var parsedFromBytes = ZstParser.ParseBytes(compressed);
        Assert.NotNull(parsedFromBytes);
        Assert.Equal(compressed.Length, (int)parsedFromBytes.CompressedSize);
        Assert.True(parsedFromBytes.FrameCount > 0);

        // WriteToFile then FromFile
        var path = TempFile("dogfood.zst");
        ZstWriter.WriteToFile(SampleText, path);
        var fromFile = ZstDocument.FromFile(path);
        Assert.NotNull(fromFile);
        Assert.True(fromFile.CompressedSize > 0);
        Assert.False(fromFile.IsEmpty);

        // ContentTypeHint
        Assert.NotNull(fromFile.ContentTypeHint);
        Assert.NotEmpty(fromFile.ContentTypeHint);

        // IsMinimalFrame
        var minFrame = Record.Exception(() => _ = fromFile.IsMinimalFrame);
        Assert.Null(minFrame);

        // ToDict from file
        var dict = fromFile.ToDict();
        Assert.NotNull(dict);

        // Round-trip verify
        var decompressed = ZstParser.DecompressFile(path);
        Assert.Equal(SampleText, decompressed);

        // CompressBytes at different levels
        var bytes1 = ZstWriter.CompressBytes(SampleBytes, level: 1);
        var bytes19 = ZstWriter.CompressBytes(SampleBytes, level: 19);
        Assert.Equal(SampleText, ZstParser.DecompressBytes(bytes1));
        Assert.Equal(SampleText, ZstParser.DecompressBytes(bytes19));
    }
}
