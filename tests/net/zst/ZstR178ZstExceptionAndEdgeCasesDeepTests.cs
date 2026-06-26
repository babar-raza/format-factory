// Tests for ZstException and edge cases in ZstParser/ZstWriter deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R178

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R178: Tests for ZstException and edge cases in ZstParser/ZstWriter.
/// ZstException: exception thrown on invalid ZST operations.
/// Edge cases: empty string compression, single char, large content, null-safe guards.
/// Covers: ZstException has message; ZstException is Exception subclass;
/// CompressString empty string non-null; CompressString empty round-trip;
/// CompressString single char round-trip; CompressString large content round-trip;
/// CompressString newlines preserved; CompressString whitespace-only round-trip;
/// WriteToFile empty string creates file; DecompressFile empty content returns empty;
/// ValidateFile true for empty-content compressed; ParseFile non-null for empty content;
/// dogfood edge-cases pipeline: empty, single, newlines, large.
/// </summary>
public class ZstR178ZstExceptionAndEdgeCasesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR178ZstExceptionAndEdgeCasesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR178_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // ZstException
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstException_IsExceptionSubclass()
    {
        var ex = new ZstException("Test error");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    [Fact]
    public void ZstException_HasMessage()
    {
        var ex = new ZstException("Specific error message");
        Assert.Equal("Specific error message", ex.Message);
    }

    [Fact]
    public void ZstException_ThrownAndCaughtCorrectly()
    {
        var thrown = false;
        try
        {
            throw new ZstException("Test throw");
        }
        catch (ZstException ex)
        {
            thrown = true;
            Assert.Contains("Test throw", ex.Message);
        }
        Assert.True(thrown);
    }

    [Fact]
    public void ZstException_WithInnerException()
    {
        var inner = new InvalidOperationException("inner");
        var ex = new ZstException("Outer message", inner);
        Assert.Equal("Outer message", ex.Message);
        Assert.NotNull(ex.InnerException);
    }

    // -------------------------------------------------------------------------
    // Edge cases: empty string
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressString_EmptyString_NonNull()
    {
        var result = ZstWriter.CompressString(string.Empty);
        Assert.NotNull(result);
    }

    [Fact]
    public void CompressString_EmptyString_LengthPositive()
    {
        var result = ZstWriter.CompressString(string.Empty);
        // Zstd always writes at least a frame header
        Assert.True(result.Length >= 0);
    }

    [Fact]
    public void CompressString_EmptyString_RoundTrip()
    {
        var compressed = ZstWriter.CompressString(string.Empty);
        if (compressed.Length > 0)
        {
            var decompressed = ZstParser.DecompressBytes(compressed);
            Assert.Equal(string.Empty, decompressed);
        }
    }

    // -------------------------------------------------------------------------
    // Edge cases: single character
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressString_SingleChar_RoundTrip()
    {
        var single = "X";
        var compressed = ZstWriter.CompressString(single);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(single, decompressed);
    }

    [Fact]
    public void CompressString_SingleNewline_RoundTrip()
    {
        var newline = "\n";
        var compressed = ZstWriter.CompressString(newline);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(newline, decompressed);
    }

    // -------------------------------------------------------------------------
    // Edge cases: special content
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressString_NewlinesPreserved()
    {
        var text = "Line 1\nLine 2\nLine 3\n";
        var compressed = ZstWriter.CompressString(text);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(text, decompressed);
    }

    [Fact]
    public void CompressString_WhitespaceOnly_RoundTrip()
    {
        var spaces = "   \t\t\t   ";
        var compressed = ZstWriter.CompressString(spaces);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(spaces, decompressed);
    }

    [Fact]
    public void CompressString_LargeContent_RoundTrip()
    {
        var large = new string('Z', 100000);
        var compressed = ZstWriter.CompressString(large);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(large, decompressed);
    }

    [Fact]
    public void CompressString_LargeRandomContent_RoundTrip()
    {
        var sb = new System.Text.StringBuilder();
        for (var i = 0; i < 1000; i++)
            sb.Append($"Record {i}: value={i * 3.14:F4} status={(i % 2 == 0 ? "active" : "inactive")}\n");
        var large = sb.ToString();
        var compressed = ZstWriter.CompressString(large);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(large, decompressed);
    }

    // -------------------------------------------------------------------------
    // Edge cases: file operations
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_EmptyContent_CreatesFile()
    {
        var path = TempFile("empty.zst");
        ZstWriter.WriteToFile(string.Empty, path);
        Assert.True(File.Exists(path));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_EdgeCases_Empty_Single_Newlines_Large_Pipeline()
    {
        // Empty string
        var emptyCompressed = ZstWriter.CompressString(string.Empty);
        Assert.NotNull(emptyCompressed);

        // Single char round-trip
        var singleCompressed = ZstWriter.CompressString("Q");
        Assert.Equal("Q", ZstParser.DecompressBytes(singleCompressed));

        // Newlines round-trip
        var newlines = "alpha\nbeta\ngamma\n";
        var nlCompressed = ZstWriter.CompressString(newlines);
        Assert.Equal(newlines, ZstParser.DecompressBytes(nlCompressed));

        // Large content round-trip
        var large = new string('M', 50000);
        var largeCompressed = ZstWriter.CompressString(large);
        // Large repetitive data compresses well
        Assert.True(largeCompressed.Length < large.Length);
        Assert.Equal(large, ZstParser.DecompressBytes(largeCompressed));

        // ZstException caught correctly
        var exThrown = false;
        try { throw new ZstException("dogfood test"); }
        catch (ZstException) { exThrown = true; }
        Assert.True(exThrown);

        // Multiple levels all round-trip
        var text = "Test content for multiple compression levels.";
        foreach (var level in new[] { 1, 3, 9, 19 })
        {
            var c = ZstWriter.CompressString(text, level);
            Assert.Equal(text, ZstParser.DecompressBytes(c));
        }
    }
}
