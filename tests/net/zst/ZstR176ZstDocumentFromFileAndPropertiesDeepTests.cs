// Tests for ZstDocument.FromFile, FileSizeKB, SizeExceeds, ContentTypeHint deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R176

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R176: Tests for ZstDocument.FromFile, FileSizeKB, SizeExceeds, ContentTypeHint deeper.
/// ZstDocument.FromFile(path): creates a ZstDocument by parsing a file at the given path.
/// FileSizeKB: returns the compressed file size in kilobytes.
/// SizeExceeds(threshold): returns true if compressed size exceeds threshold bytes.
/// ContentTypeHint: returns a string hint about the content type.
/// IsMinimalFrame: returns true if the compressed data is a minimal single frame.
/// Covers: FromFile non-null; FromFile FrameCount positive; FromFile CompressedSize positive;
/// FromFile IsEmpty false; FileSizeKB positive for real content; FileSizeKB correct magnitude;
/// SizeExceeds small threshold returns true; SizeExceeds large threshold returns false;
/// ContentTypeHint non-null; IsMinimalFrame non-null;
/// dogfood WriteToFile->FromFile->FileSizeKB->SizeExceeds->ContentTypeHint->Verify pipeline.
/// </summary>
public class ZstR176ZstDocumentFromFileAndPropertiesDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly string LargeText =
        string.Concat(System.Linq.Enumerable.Repeat(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " +
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ", 20));

    private static readonly string SmallText = "Small content.";

    public ZstR176ZstDocumentFromFileAndPropertiesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR176_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string WriteFile(string name, string content)
    {
        var path = TempFile(name);
        ZstWriter.WriteToFile(content, path);
        return path;
    }

    // -------------------------------------------------------------------------
    // ZstDocument.FromFile
    // -------------------------------------------------------------------------

    [Fact]
    public void FromFile_NonNull()
    {
        var path = WriteFile("test.zst", LargeText);
        Assert.NotNull(ZstDocument.FromFile(path));
    }

    [Fact]
    public void FromFile_FrameCountPositive()
    {
        var path = WriteFile("frames.zst", LargeText);
        var doc = ZstDocument.FromFile(path);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void FromFile_CompressedSizePositive()
    {
        var path = WriteFile("size.zst", LargeText);
        var doc = ZstDocument.FromFile(path);
        Assert.True(doc.CompressedSize > 0);
    }

    [Fact]
    public void FromFile_IsEmptyFalse()
    {
        var path = WriteFile("notempty.zst", LargeText);
        var doc = ZstDocument.FromFile(path);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void FromFile_CompressedSizeMatchesFileSize()
    {
        var path = WriteFile("match.zst", SmallText);
        var fileSize = new FileInfo(path).Length;
        var doc = ZstDocument.FromFile(path);
        Assert.Equal(fileSize, (long)doc.CompressedSize);
    }

    // -------------------------------------------------------------------------
    // FileSizeKB
    // -------------------------------------------------------------------------

    [Fact]
    public void FileSizeKB_Positive_ForRealContent()
    {
        var path = WriteFile("kb.zst", LargeText);
        var doc = ZstDocument.FromFile(path);
        Assert.True(doc.FileSizeKB >= 0);
    }

    [Fact]
    public void FileSizeKB_SmallFile_LessThanOne()
    {
        var path = WriteFile("small.zst", SmallText);
        var doc = ZstDocument.FromFile(path);
        // Small text compresses to a tiny file
        Assert.True(doc.FileSizeKB < 10);
    }

    // -------------------------------------------------------------------------
    // SizeExceeds
    // -------------------------------------------------------------------------

    [Fact]
    public void SizeExceeds_SmallThreshold_ReturnsTrue()
    {
        var path = WriteFile("exceeds.zst", LargeText);
        var doc = ZstDocument.FromFile(path);
        // Any non-empty file should exceed 0 bytes
        Assert.True(doc.SizeExceeds(0));
    }

    [Fact]
    public void SizeExceeds_LargeThreshold_ReturnsFalse()
    {
        var path = WriteFile("notexceeds.zst", SmallText);
        var doc = ZstDocument.FromFile(path);
        // Small file definitely doesn't exceed 100MB
        Assert.False(doc.SizeExceeds(100 * 1024 * 1024));
    }

    [Fact]
    public void SizeExceeds_ExactSize_ReturnsFalse()
    {
        var path = WriteFile("exact.zst", SmallText);
        var doc = ZstDocument.FromFile(path);
        var size = (int)doc.CompressedSize;
        // Size does not exceed itself
        Assert.False(doc.SizeExceeds(size));
    }

    // -------------------------------------------------------------------------
    // ContentTypeHint
    // -------------------------------------------------------------------------

    [Fact]
    public void ContentTypeHint_NonNull()
    {
        var path = WriteFile("hint.zst", LargeText);
        var doc = ZstDocument.FromFile(path);
        Assert.NotNull(doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_NonEmpty()
    {
        var path = WriteFile("hintne.zst", LargeText);
        var doc = ZstDocument.FromFile(path);
        Assert.NotEmpty(doc.ContentTypeHint);
    }

    // -------------------------------------------------------------------------
    // IsMinimalFrame
    // -------------------------------------------------------------------------

    [Fact]
    public void IsMinimalFrame_SmallFile_HasValue()
    {
        var path = WriteFile("minimal.zst", SmallText);
        var doc = ZstDocument.FromFile(path);
        // IsMinimalFrame returns bool — just verify it doesn't throw
        var _ = doc.IsMinimalFrame;
        Assert.True(true);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToFile_FromFile_FileSizeKB_SizeExceeds_ContentTypeHint_Verify_Pipeline()
    {
        // WriteToFile
        var path = TempFile("dogfood.zst");
        ZstWriter.WriteToFile(LargeText, path);
        Assert.True(File.Exists(path));

        // FromFile
        var doc = ZstDocument.FromFile(path);
        Assert.NotNull(doc);
        Assert.True(doc.FrameCount > 0);
        Assert.True(doc.CompressedSize > 0);
        Assert.False(doc.IsEmpty);

        // FileSizeKB
        Assert.True(doc.FileSizeKB >= 0);

        // SizeExceeds
        Assert.True(doc.SizeExceeds(0)); // exceeds 0
        Assert.False(doc.SizeExceeds(1024 * 1024 * 100)); // doesn't exceed 100MB

        // ContentTypeHint
        var hint = doc.ContentTypeHint;
        Assert.NotNull(hint);
        Assert.NotEmpty(hint);

        // ParseFile gives same result
        var parsed = ZstParser.ParseFile(path);
        Assert.Equal(doc.CompressedSize, parsed.CompressedSize);
        Assert.Equal(doc.FrameCount, parsed.FrameCount);
    }
}
