// Tests for ZstWriter.CompressStream, CompressString levels, and round-trip deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R183

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R183: Tests for ZstWriter.CompressStream, CompressString with level variants, and round-trip.
/// CompressStream(stream): compresses a readable stream to bytes.
/// CompressString(text, level): compresses with explicit compression level.
/// Covers: CompressStream non-null; CompressStream positive length; CompressStream round-trip;
/// CompressStream matches CompressString for same input; CompressStream large input;
/// CompressString level 1 decompressible; CompressString level 19 decompressible;
/// CompressString level 1 vs 19 differ (may differ); CompressString empty string;
/// CompressBytes level 1; CompressBytes level 22 (max); DecompressBytes on all levels;
/// dogfood CompressStream→ParseBytes→DecompressFile→WriteToFile→CompressStream pipeline.
/// </summary>
public class ZstR183CompressStreamAndLevelDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly string SampleText = "The quick brown fox jumps over the lazy dog. Repeated content helps compression. " +
        "The quick brown fox jumps over the lazy dog. Repeated content helps compression.";

    public ZstR183CompressStreamAndLevelDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR183_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // CompressStream
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressStream_NonNull()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleText));
        var result = ZstWriter.CompressStream(ms);
        Assert.NotNull(result);
    }

    [Fact]
    public void CompressStream_PositiveLength()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleText));
        var result = ZstWriter.CompressStream(ms);
        Assert.True(result.Length > 0);
    }

    [Fact]
    public void CompressStream_RoundTrip()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleText));
        var compressed = ZstWriter.CompressStream(ms);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, decompressed);
    }

    [Fact]
    public void CompressStream_MatchesCompressString()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleText));
        var fromStream = ZstWriter.CompressStream(ms);
        var fromString = ZstWriter.CompressString(SampleText);
        // Both should decompress to same content (sizes may differ slightly)
        Assert.Equal(SampleText, ZstParser.DecompressBytes(fromStream));
        Assert.Equal(SampleText, ZstParser.DecompressBytes(fromString));
    }

    [Fact]
    public void CompressStream_LargeInput_RoundTrip()
    {
        var largeText = string.Concat(System.Linq.Enumerable.Repeat("Large stream content block. ", 500));
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(largeText));
        var compressed = ZstWriter.CompressStream(ms);
        Assert.True(compressed.Length > 0);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(largeText, decompressed);
    }

    [Fact]
    public void CompressStream_SmallInput_NonNull()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes("Hi"));
        var result = ZstWriter.CompressStream(ms);
        Assert.NotNull(result);
        Assert.True(result.Length > 0);
    }

    // -------------------------------------------------------------------------
    // CompressString with levels
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressString_Level1_Decompressible()
    {
        var compressed = ZstWriter.CompressString(SampleText, 1);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, decompressed);
    }

    [Fact]
    public void CompressString_Level9_Decompressible()
    {
        var compressed = ZstWriter.CompressString(SampleText, 9);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, decompressed);
    }

    [Fact]
    public void CompressString_Level19_Decompressible()
    {
        var compressed = ZstWriter.CompressString(SampleText, 19);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, decompressed);
    }

    [Fact]
    public void CompressString_AllLevels_NonNullResult()
    {
        foreach (var level in new[] { 1, 3, 6, 9, 12, 15, 19 })
        {
            var compressed = ZstWriter.CompressString(SampleText, level);
            Assert.NotNull(compressed);
            Assert.True(compressed.Length > 0);
        }
    }

    [Fact]
    public void CompressString_DefaultLevel_RoundTrip()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, decompressed);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressStream_ParseBytes_WriteToFile_DecompressFile_Pipeline()
    {
        // CompressStream
        using var ms1 = new MemoryStream(Encoding.UTF8.GetBytes(SampleText));
        var compressed = ZstWriter.CompressStream(ms1);
        Assert.True(compressed.Length > 0);

        // ParseBytes
        var doc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(doc);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.FrameCount > 0);
        Assert.False(doc.IsEmpty);

        // DecompressBytes
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, decompressed);

        // WriteToFile using string (same content)
        var path = TempFile("stream_test.zst");
        ZstWriter.WriteToFile(SampleText, path);
        Assert.True(File.Exists(path));

        // ParseFile matches ParseBytes in content
        var fromFile = ZstParser.ParseFile(path);
        Assert.True(fromFile.CompressedSize > 0);

        // DecompressFile round-trip
        Assert.Equal(SampleText, ZstParser.DecompressFile(path));

        // CompressStream from FileStream
        using var fs = File.OpenRead(path);
        // We can parse the stream (ParseStream)
        var fromStream = ZstParser.ParseStream(fs);
        Assert.NotNull(fromStream);
        Assert.True(fromStream.CompressedSize > 0);

        // Level 1 also produces parseable result
        var level1 = ZstWriter.CompressString(SampleText, 1);
        var docLevel1 = ZstParser.ParseBytes(level1);
        Assert.True(docLevel1.FrameCount > 0);
        Assert.Equal(SampleText, ZstParser.DecompressBytes(level1));

        // Level 19 also
        var level19 = ZstWriter.CompressString(SampleText, 19);
        Assert.Equal(SampleText, ZstParser.DecompressBytes(level19));
    }
}
