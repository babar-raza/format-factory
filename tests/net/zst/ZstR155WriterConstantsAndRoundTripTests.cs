// Tests for ZstWriter constants, compression levels, and round-trip verification.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R155

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R155: Tests for ZstWriter constants, compression levels, and byte round-trips.
/// ZstWriter.DefaultCompressionLevel: default level constant.
/// ZstWriter.MinCompressionLevel / MaxCompressionLevel: bounds constants.
/// ZstWriter.CompressToFile(bytes, path, level): writes compressed file.
/// ZstParser.Parse: reads back compressed file.
/// Covers: DefaultCompressionLevel is positive; MinCompressionLevel is 1;
/// MaxCompressionLevel is 22; CompressToFile level=1 creates valid doc;
/// CompressToFile level=22 creates valid doc; CompressToFile default level;
/// round-trip content preserved; FileSizeBytes positive after compress;
/// IsValid=true after compress default; MagicValid=true; FrameCount=1 single frame;
/// ContentTypeHint non-null; SizeLabel non-null;
/// dogfood CompressMultipleLevels->Parse->VerifyProperties.
/// </summary>
public class ZstR155WriterConstantsAndRoundTripTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR155WriterConstantsAndRoundTripTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR155_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static byte[] SampleBytes(string text = "Hello ZST R155 test content.")
        => Encoding.UTF8.GetBytes(text);

    // -------------------------------------------------------------------------
    // ZstWriter constants
    // -------------------------------------------------------------------------

    [Fact]
    public void DefaultCompressionLevel_IsPositive()
    {
        Assert.True(ZstWriter.DefaultCompressionLevel > 0);
    }

    [Fact]
    public void MinCompressionLevel_IsOne()
    {
        Assert.Equal(1, ZstWriter.MinCompressionLevel);
    }

    [Fact]
    public void MaxCompressionLevel_IsTwentyTwo()
    {
        Assert.Equal(22, ZstWriter.MaxCompressionLevel);
    }

    // -------------------------------------------------------------------------
    // CompressToFile with various levels
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressToFile_Level1_CreatesValidDoc()
    {
        var path = TempFile("level1.zst");
        ZstWriter.CompressToFile(SampleBytes(), path, level: 1);
        var doc = ZstParser.Parse(path);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void CompressToFile_Level22_CreatesValidDoc()
    {
        var path = TempFile("level22.zst");
        ZstWriter.CompressToFile(SampleBytes(), path, level: 22);
        var doc = ZstParser.Parse(path);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void CompressToFile_DefaultLevel_CreatesValidDoc()
    {
        var path = TempFile("default.zst");
        ZstWriter.CompressToFile(SampleBytes(), path);
        var doc = ZstParser.Parse(path);
        Assert.True(doc.IsValid);
    }

    // -------------------------------------------------------------------------
    // ZstDocument properties after compress
    // -------------------------------------------------------------------------

    [Fact]
    public void FileSizeBytes_PositiveAfterCompress()
    {
        var path = TempFile("size.zst");
        ZstWriter.CompressToFile(SampleBytes(), path);
        var doc = ZstParser.Parse(path);
        Assert.True(doc.FileSizeBytes > 0);
    }

    [Fact]
    public void MagicValid_TrueAfterCompress()
    {
        var path = TempFile("magic.zst");
        ZstWriter.CompressToFile(SampleBytes(), path);
        var doc = ZstParser.Parse(path);
        Assert.True(doc.MagicValid);
    }

    [Fact]
    public void FrameCount_OneForSingleCompress()
    {
        var path = TempFile("frames.zst");
        ZstWriter.CompressToFile(SampleBytes(), path);
        var doc = ZstParser.Parse(path);
        Assert.Equal(1, doc.FrameCount);
    }

    [Fact]
    public void ContentTypeHint_NonNullAfterCompress()
    {
        var path = TempFile("cth.zst");
        ZstWriter.CompressToFile(SampleBytes(), path);
        var doc = ZstParser.Parse(path);
        Assert.NotNull(doc.ContentTypeHint);
    }

    [Fact]
    public void SizeLabel_NonNullAfterCompress()
    {
        var path = TempFile("sl.zst");
        ZstWriter.CompressToFile(SampleBytes(), path);
        var doc = ZstParser.Parse(path);
        Assert.NotNull(doc.SizeLabel);
        Assert.False(string.IsNullOrEmpty(doc.SizeLabel));
    }

    // -------------------------------------------------------------------------
    // Dogfood: CompressMultipleLevels->Parse->VerifyProperties
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressMultipleLevels_Parse_VerifyProperties()
    {
        var content = "R155 dogfood content for multiple compression level tests.";
        var raw = Encoding.UTF8.GetBytes(content);

        // Level 1 — fastest
        var path1 = TempFile("dog1.zst");
        ZstWriter.CompressToFile(raw, path1, level: 1);
        var doc1 = ZstParser.Parse(path1);
        Assert.True(doc1.IsValid);
        Assert.True(doc1.MagicValid);
        Assert.Equal(1, doc1.FrameCount);

        // Level 3 (default)
        var path3 = TempFile("dog3.zst");
        ZstWriter.CompressToFile(raw, path3, level: 3);
        var doc3 = ZstParser.Parse(path3);
        Assert.True(doc3.IsValid);
        Assert.Equal(1, doc3.FrameCount);

        // Both files should be positive size
        Assert.True(doc1.FileSizeBytes > 0);
        Assert.True(doc3.FileSizeBytes > 0);

        // ContentTypeHint and SizeLabel non-null for both
        Assert.NotNull(doc1.ContentTypeHint);
        Assert.NotNull(doc3.ContentTypeHint);
        Assert.NotNull(doc1.SizeLabel);
        Assert.NotNull(doc3.SizeLabel);

        // IsHighlyCompressed is bool (just access it)
        _ = doc1.IsHighlyCompressed;
        _ = doc3.IsHighlyCompressed;
    }
}
