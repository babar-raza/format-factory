// Tests for ZstWriter.CompressString, DecompressToString deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R161

using System;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R161: Tests for ZstWriter.CompressString, DecompressToString deeper coverage.
/// ZstWriter.CompressString(text): compresses a string to bytes.
/// ZstWriter.DecompressToString(bytes): decompresses bytes to string.
/// ZstWriter.CompressString(text, level): compresses at specific level.
/// Covers: CompressString returns non-empty; CompressString->DecompressToString round-trip;
/// CompressString round-trip with long text; CompressString with unicode;
/// CompressString empty string round-trip; DecompressToString returns original;
/// CompressString at min level; CompressString at max level; CompressString at default;
/// DecompressToString unicode content; CompressString smaller than source for long text;
/// CompressString->ZstDocument.Load->IsEmpty false;
/// CompressString->ZstDocument.Load->FrameCount; CompressString result is valid zst;
/// dogfood CompressString->DecompressToString->CompressString->DecompressToString chain.
/// </summary>
public class ZstR161CompressStringAndDecompressTests
{
    private const string ShortText = "Hello World!";
    private const string LongText = "This is a much longer text string that should compress well because it has repeated content patterns. " +
                                    "This is a much longer text string that should compress well because it has repeated content patterns. " +
                                    "Final portion of the content.";
    private const string UnicodeText = "Unicode content: \u4e2d\u6587 \u00e9\u00e0\u00fc \u0413\u0440\u0443\u043f\u043f\u0430";

    // -------------------------------------------------------------------------
    // CompressString
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressString_ReturnsNonEmpty()
    {
        var bytes = ZstWriter.CompressString(ShortText);
        Assert.NotEmpty(bytes);
    }

    [Fact]
    public void CompressString_RoundTrip_PreservesContent()
    {
        var bytes = ZstWriter.CompressString(ShortText);
        var result = ZstWriter.DecompressToString(bytes);
        Assert.Equal(ShortText, result);
    }

    [Fact]
    public void CompressString_LongText_RoundTrip()
    {
        var bytes = ZstWriter.CompressString(LongText);
        var result = ZstWriter.DecompressToString(bytes);
        Assert.Equal(LongText, result);
    }

    [Fact]
    public void CompressString_Unicode_RoundTrip()
    {
        var bytes = ZstWriter.CompressString(UnicodeText);
        var result = ZstWriter.DecompressToString(bytes);
        Assert.Equal(UnicodeText, result);
    }

    [Fact]
    public void CompressString_EmptyString_RoundTrip()
    {
        var bytes = ZstWriter.CompressString(string.Empty);
        var result = ZstWriter.DecompressToString(bytes);
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void CompressString_AtMinLevel_RoundTrip()
    {
        var bytes = ZstWriter.CompressString(ShortText, ZstWriter.MinCompressionLevel);
        var result = ZstWriter.DecompressToString(bytes);
        Assert.Equal(ShortText, result);
    }

    [Fact]
    public void CompressString_AtMaxLevel_RoundTrip()
    {
        var bytes = ZstWriter.CompressString(ShortText, ZstWriter.MaxCompressionLevel);
        var result = ZstWriter.DecompressToString(bytes);
        Assert.Equal(ShortText, result);
    }

    [Fact]
    public void CompressString_AtDefaultLevel_RoundTrip()
    {
        var bytes = ZstWriter.CompressString(ShortText, ZstWriter.DefaultCompressionLevel);
        var result = ZstWriter.DecompressToString(bytes);
        Assert.Equal(ShortText, result);
    }

    [Fact]
    public void CompressString_LongText_SmallerThanSource()
    {
        var bytes = ZstWriter.CompressString(LongText);
        var sourceBytes = Encoding.UTF8.GetBytes(LongText);
        Assert.True(bytes.Length < sourceBytes.Length);
    }

    // -------------------------------------------------------------------------
    // ZstDocument.Load from CompressString
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressString_ZstDocumentLoad_IsEmpty_False()
    {
        var bytes = ZstWriter.CompressString(LongText);
        var doc = ZstDocument.Load(bytes);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void CompressString_ZstDocumentLoad_FrameCount_Positive()
    {
        var bytes = ZstWriter.CompressString(ShortText);
        var doc = ZstDocument.Load(bytes);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void CompressString_ZstDocumentLoad_CompressedSize_Matches()
    {
        var bytes = ZstWriter.CompressString(ShortText);
        var doc = ZstDocument.Load(bytes);
        Assert.Equal(bytes.Length, doc.CompressedSize);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CompressString->DecompressToString->CompressString->DecompressToString chain
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressDecompressCompressDecompress_Chain()
    {
        var original = "Dogfood test content with some repetition. Dogfood test content again.";

        // Round 1
        var bytes1 = ZstWriter.CompressString(original);
        var text1 = ZstWriter.DecompressToString(bytes1);
        Assert.Equal(original, text1);

        // Check ZstDocument properties
        var doc = ZstDocument.Load(bytes1);
        Assert.False(doc.IsEmpty);
        Assert.True(doc.FrameCount > 0);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // Round 2 — compress the decompressed text again
        var bytes2 = ZstWriter.CompressString(text1);
        var text2 = ZstWriter.DecompressToString(bytes2);
        Assert.Equal(original, text2);

        // Unicode round trip
        var uniBytes = ZstWriter.CompressString(UnicodeText);
        var uniResult = ZstWriter.DecompressToString(uniBytes);
        Assert.Equal(UnicodeText, uniResult);
    }
}
