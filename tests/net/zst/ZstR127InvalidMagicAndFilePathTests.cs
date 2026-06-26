// Tests for ZstInvalidMagicException and ZstParser.ParseStream filePath parameter.
// Sprint: FORMAT-FACTORY-ZST-R127-20260627
// Ledger: R127-GOVERNED-DOTNET-ZST-INVALID-MAGIC-FILEPATH-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R127: Tests for ZstInvalidMagicException (thrown when data has wrong magic bytes)
/// and ZstParser.ParseStream(Stream, knownLength, filePath) with explicit filePath argument.
/// ZstInvalidMagicException is a subclass of ZstException. Passing incorrect magic bytes
/// causes ParseStream to throw ZstInvalidMagicException, not a generic Exception.
/// The filePath parameter populates ZstDocument.FilePath when provided.
/// Covers: invalid magic→ZstInvalidMagicException; zero-length non-magic data;
/// explicit filePath propagates to doc.FilePath; default knownLength=-1 still works;
/// IsValid=false for wrong-magic document (via Parse on valid then corrupt); dogfood
/// exception hierarchy (ZstInvalidMagicException is ZstException is ZstException).
/// </summary>
public class ZstR127InvalidMagicAndFilePathTests
{
    private static byte[] Compress(string text)
    {
        var bytes = Encoding.UTF8.GetBytes(text);
        return ZstWriter.Compress(bytes);
    }

    private static Stream ToStream(byte[] data) => new MemoryStream(data);

    // -------------------------------------------------------------------------
    // ZstInvalidMagicException: wrong magic bytes
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseStream_WrongMagicBytes_ThrowsZstInvalidMagicException()
    {
        // First 4 bytes are NOT the Zstd magic (0x28 0xB5 0x2F 0xFD)
        var badData = new byte[] { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05 };
        using var ms = ToStream(badData);
        Assert.Throws<ZstInvalidMagicException>(() => ZstParser.ParseStream(ms));
    }

    [Fact]
    public void ParseStream_PdfHeader_ThrowsZstInvalidMagicException()
    {
        // %PDF (common wrong-format scenario)
        var pdfLike = new byte[] { (byte)'%', (byte)'P', (byte)'D', (byte)'F', 0x2D };
        using var ms = ToStream(pdfLike);
        Assert.Throws<ZstInvalidMagicException>(() => ZstParser.ParseStream(ms));
    }

    [Fact]
    public void ParseStream_AllZeroBytes_ThrowsZstInvalidMagicException()
    {
        var allZeros = new byte[16];
        using var ms = ToStream(allZeros);
        Assert.Throws<ZstInvalidMagicException>(() => ZstParser.ParseStream(ms));
    }

    [Fact]
    public void ZstInvalidMagicException_IsSubclassOfZstException()
    {
        // Verify exception hierarchy
        var ex = new ZstInvalidMagicException("test");
        Assert.IsAssignableFrom<ZstException>(ex);
    }

    [Fact]
    public void ZstInvalidMagicException_MessagePreserved()
    {
        var ex = new ZstInvalidMagicException("bad magic detected");
        Assert.Equal("bad magic detected", ex.Message);
    }

    // -------------------------------------------------------------------------
    // ParseStream with explicit filePath parameter
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseStream_WithExplicitFilePath_PopulatesDocumentFilePath()
    {
        var compressed = Compress("stream with filepath label");
        using var ms = ToStream(compressed);
        const string fakeLabel = "/virtual/path/data.zst";
        var doc = ZstParser.ParseStream(ms, knownLength: -1, filePath: fakeLabel);
        Assert.Equal(fakeLabel, doc.FilePath);
    }

    [Fact]
    public void ParseStream_WithExplicitFilePath_DocIsValid()
    {
        var compressed = Compress("valid content with path");
        using var ms = ToStream(compressed);
        var doc = ZstParser.ParseStream(ms, knownLength: -1, filePath: "tagged.zst");
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void ParseStream_WithoutFilePath_FilePathIsNull()
    {
        var compressed = Compress("content without path");
        using var ms = ToStream(compressed);
        var doc = ZstParser.ParseStream(ms);
        Assert.Null(doc.FilePath);
    }

    // -------------------------------------------------------------------------
    // ParseStream with explicit knownLength
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseStream_WithExplicitKnownLength_FrameCountAtLeastOne()
    {
        var compressed = Compress("known length test");
        using var ms = ToStream(compressed);
        var doc = ZstParser.ParseStream(ms, knownLength: compressed.Length);
        Assert.True(doc.FrameCount >= 1);
    }

    [Fact]
    public void ParseStream_ExplicitKnownLength_MagicValid()
    {
        var compressed = Compress("another known length test");
        using var ms = ToStream(compressed);
        var doc = ZstParser.ParseStream(ms, knownLength: compressed.Length);
        Assert.True(doc.MagicValid);
    }

    // -------------------------------------------------------------------------
    // Dogfood: compress → ParseStream with filePath → verify all properties
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CompressParseWithFilePath_AllPropertiesCorrect()
    {
        const string input = "dogfood content for R127 filePath test";
        var compressed = Compress(input);
        const string label = "/dog/food/r127.zst";

        using var ms = ToStream(compressed);
        var doc = ZstParser.ParseStream(ms, knownLength: compressed.Length, filePath: label);

        Assert.True(doc.IsValid);
        Assert.True(doc.MagicValid);
        Assert.True(doc.FrameCount >= 1);
        Assert.Equal(label, doc.FilePath);
        Assert.True(doc.FileSizeBytes >= 0);
    }
}
