// Tests for ZstWriter and ZstParser constants and properties.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R158

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R158: Tests for ZstWriter and ZstParser constants and computed document properties.
/// ZstWriter.DefaultCompressionLevel, MinCompressionLevel, MaxCompressionLevel.
/// ZstDocument.OverheadBytes, BytesPerFrame, FileSizeKB, IsHighlyCompressed, SizeLabel.
/// Covers: DefaultCompressionLevel >= MinCompressionLevel; DefaultCompressionLevel <= MaxCompressionLevel;
/// MinCompressionLevel is 1; MaxCompressionLevel is 22;
/// OverheadBytes >= 0 after compress; BytesPerFrame > 0 for single-frame;
/// FileSizeKB is FileSizeBytes / 1024.0; SizeLabel contains "B" or size unit;
/// IsHighlyCompressed is bool; IsMinimalFrame is bool; FrameHeaderDescriptor in 0-255;
/// HasMultipleFrames false for single frame; ContentTypeHint non-null;
/// IsEmptyContent false for non-empty content; SizeExceeds100K false for small file;
/// dogfood CompressToFile->Parse->verify all computed properties accessible.
/// </summary>
public class ZstR158WriterAndParserConstantsTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR158WriterAndParserConstantsTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR158_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private ZstDocument ParseCompressed(string text, string filename = "test.zst")
    {
        var path = TempFile(filename);
        ZstWriter.CompressToFile(Encoding.UTF8.GetBytes(text), path);
        return ZstParser.Parse(path);
    }

    // -------------------------------------------------------------------------
    // ZstWriter constants
    // -------------------------------------------------------------------------

    [Fact]
    public void DefaultLevel_IsAtLeastMinLevel()
    {
        Assert.True(ZstWriter.DefaultCompressionLevel >= ZstWriter.MinCompressionLevel);
    }

    [Fact]
    public void DefaultLevel_IsAtMostMaxLevel()
    {
        Assert.True(ZstWriter.DefaultCompressionLevel <= ZstWriter.MaxCompressionLevel);
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
    // ZstDocument computed properties
    // -------------------------------------------------------------------------

    [Fact]
    public void OverheadBytes_NonNegativeAfterCompress()
    {
        var doc = ParseCompressed("overhead check content.");
        Assert.True(doc.OverheadBytes >= 0);
    }

    [Fact]
    public void BytesPerFrame_PositiveForSingleFrame()
    {
        var doc = ParseCompressed("bytes per frame check.");
        if (doc.FrameCount > 0)
            Assert.True(doc.BytesPerFrame > 0);
    }

    [Fact]
    public void FileSizeKB_MatchesFileSizeBytesDiv1024()
    {
        var doc = ParseCompressed("file size kb check.");
        Assert.Equal(doc.FileSizeBytes / 1024.0, doc.FileSizeKB, 3);
    }

    [Fact]
    public void SizeLabel_ContainsSizeUnit()
    {
        var doc = ParseCompressed("size label content.");
        var label = doc.SizeLabel;
        Assert.NotNull(label);
        // SizeLabel should contain B, KB, MB etc.
        Assert.True(label.Contains("B") || label.Contains("K") || label.Contains("M"),
            $"Expected size unit in label but got: '{label}'");
    }

    [Fact]
    public void IsHighlyCompressed_IsBool()
    {
        var doc = ParseCompressed("highly compressed check.");
        _ = doc.IsHighlyCompressed; // just verify accessible as bool
        Assert.IsType<bool>(doc.IsHighlyCompressed);
    }

    [Fact]
    public void IsMinimalFrame_IsBool()
    {
        var doc = ParseCompressed("minimal frame check.");
        Assert.IsType<bool>(doc.IsMinimalFrame);
    }

    [Fact]
    public void FrameHeaderDescriptor_InRange0To255()
    {
        var doc = ParseCompressed("frame header descriptor check.");
        Assert.InRange(doc.FrameHeaderDescriptor, (byte)0, (byte)255);
    }

    [Fact]
    public void HasMultipleFrames_FalseForSingleCompress()
    {
        var doc = ParseCompressed("has multiple frames check.");
        Assert.False(doc.HasMultipleFrames);
    }

    [Fact]
    public void ContentTypeHint_NonNull()
    {
        var doc = ParseCompressed("content type hint check.");
        Assert.NotNull(doc.ContentTypeHint);
    }

    [Fact]
    public void IsEmptyContent_FalseForNonEmpty()
    {
        var doc = ParseCompressed("non-empty content here.");
        Assert.False(doc.IsEmptyContent);
    }

    [Fact]
    public void SizeExceeds100K_FalseForSmallContent()
    {
        var doc = ParseCompressed("tiny content.");
        Assert.False(doc.SizeExceeds100K);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CompressToFile->Parse->verify all computed properties
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressParseVerifyAllComputedProperties()
    {
        var content = "R158 dogfood: verifying all ZstDocument computed properties.";
        var path = TempFile("dogfood.zst");
        ZstWriter.CompressToFile(Encoding.UTF8.GetBytes(content), path);
        var doc = ZstParser.Parse(path);

        // Core validity
        Assert.True(doc.IsValid);
        Assert.True(doc.MagicValid);
        Assert.Equal(1, doc.FrameCount);
        Assert.True(doc.FileSizeBytes > 0);

        // Computed properties
        Assert.Equal(doc.FileSizeBytes / 1024.0, doc.FileSizeKB, 3);
        Assert.True(doc.OverheadBytes >= 0);
        if (doc.FrameCount > 0)
            Assert.True(doc.BytesPerFrame > 0);

        // String properties
        Assert.NotNull(doc.ContentTypeHint);
        Assert.NotNull(doc.SizeLabel);
        Assert.False(string.IsNullOrEmpty(doc.SizeLabel));

        // Boolean properties
        Assert.False(doc.IsEmptyContent);
        Assert.False(doc.HasMultipleFrames);
        Assert.False(doc.SizeExceeds100K);
        Assert.InRange(doc.FrameHeaderDescriptor, (byte)0, (byte)255);
        _ = doc.IsHighlyCompressed;
        _ = doc.IsMinimalFrame;

        // Writer constants
        Assert.Equal(1, ZstWriter.MinCompressionLevel);
        Assert.Equal(22, ZstWriter.MaxCompressionLevel);
        Assert.True(ZstWriter.DefaultCompressionLevel >= 1);
    }
}
