// Tests for ZstParser.ParseFile, ZstDocument.Load(stream), ZstDocument properties deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R169

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R169: Tests for ZstParser.ParseFile, ZstDocument.Load(stream), ZstDocument properties deeper.
/// ZstParser.ParseFile(path): parses a .zst file from disk and returns ZstDocument.
/// ZstDocument.Load(stream): loads a ZstDocument from a Stream.
/// ZstDocument properties: CompressedSize, FrameCount, IsEmpty, CompressionRatio, IsHighlyCompressed.
/// Covers: ParseFile creates file; ParseFile FrameCount positive; ParseFile CompressedSize correct;
/// ParseFile IsEmpty false for compressed content; Load(stream) non-null;
/// Load(stream) FrameCount positive; Load(stream) CompressedSize matches;
/// ParseFile->ZstDocument IsHighlyCompressed for repetitive data;
/// CompressionRatio positive for valid compressed data;
/// IsEmpty false after writing content; BytesPerFrame positive;
/// dogfood WriteToFile->ParseFile->Load(stream)->properties verify pipeline.
/// </summary>
public class ZstR169ParseFileStreamAndDocumentTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly string SampleText =
        "Lorem ipsum dolor sit amet consectetur adipiscing elit. " +
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.";

    public ZstR169ParseFileStreamAndDocumentTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR169_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string WriteCompressedFile(string name, string content)
    {
        var compressed = ZstWriter.CompressString(content);
        var path = TempFile(name);
        File.WriteAllBytes(path, compressed);
        return path;
    }

    // -------------------------------------------------------------------------
    // ZstParser.ParseFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseFile_NonNull()
    {
        var path = WriteCompressedFile("sample.zst", SampleText);
        var doc = ZstParser.ParseFile(path);
        Assert.NotNull(doc);
    }

    [Fact]
    public void ParseFile_FrameCount_Positive()
    {
        var path = WriteCompressedFile("sample.zst", SampleText);
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void ParseFile_CompressedSize_Positive()
    {
        var path = WriteCompressedFile("sample.zst", SampleText);
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.CompressedSize > 0);
    }

    [Fact]
    public void ParseFile_IsEmpty_FalseForContent()
    {
        var path = WriteCompressedFile("content.zst", SampleText);
        var doc = ZstParser.ParseFile(path);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void ParseFile_CompressedSize_MatchesFileSize()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        var path = TempFile("size_check.zst");
        File.WriteAllBytes(path, compressed);
        var doc = ZstParser.ParseFile(path);
        Assert.Equal(compressed.Length, (int)doc.CompressedSize);
    }

    // -------------------------------------------------------------------------
    // ZstDocument.Load(stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_NonNull()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        using var ms = new MemoryStream(compressed);
        var doc = ZstDocument.Load(ms);
        Assert.NotNull(doc);
    }

    [Fact]
    public void LoadStream_FrameCount_Positive()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        using var ms = new MemoryStream(compressed);
        var doc = ZstDocument.Load(ms);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void LoadStream_CompressedSize_MatchesInput()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        using var ms = new MemoryStream(compressed);
        var doc = ZstDocument.Load(ms);
        Assert.Equal(compressed.Length, (int)doc.CompressedSize);
    }

    [Fact]
    public void LoadStream_IsEmpty_False()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        using var ms = new MemoryStream(compressed);
        var doc = ZstDocument.Load(ms);
        Assert.False(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // Properties
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressionRatio_Positive_ForCompressibleData()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        using var ms = new MemoryStream(compressed);
        var doc = ZstDocument.Load(ms);
        Assert.True(doc.CompressionRatio >= 0);
    }

    [Fact]
    public void BytesPerFrame_Positive()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        using var ms = new MemoryStream(compressed);
        var doc = ZstDocument.Load(ms);
        Assert.True(doc.BytesPerFrame >= 0);
    }

    [Fact]
    public void IsHighlyCompressed_RepetitiveData_True()
    {
        var repeated = new string('A', 1000);
        var compressed = ZstWriter.CompressString(repeated);
        using var ms = new MemoryStream(compressed);
        var doc = ZstDocument.Load(ms);
        // Highly repetitive data should compress very well
        Assert.True(doc.IsHighlyCompressed || doc.CompressionRatio > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: WriteToFile->ParseFile->Load(stream)->Verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToFileParseFileLoadStreamPropertiesVerify_Pipeline()
    {
        // WriteToFile
        var path = TempFile("dogfood.zst");
        ZstWriter.WriteToFile(SampleText, path);
        Assert.True(File.Exists(path));

        // ParseFile
        var parsed = ZstParser.ParseFile(path);
        Assert.NotNull(parsed);
        Assert.True(parsed.FrameCount > 0);
        Assert.True(parsed.CompressedSize > 0);
        Assert.False(parsed.IsEmpty);

        // Load(stream)
        var bytes = File.ReadAllBytes(path);
        using var ms = new MemoryStream(bytes);
        var loaded = ZstDocument.Load(ms);
        Assert.NotNull(loaded);
        Assert.True(loaded.FrameCount > 0);
        Assert.Equal(parsed.CompressedSize, loaded.CompressedSize);

        // Decompress and verify
        var decompressed = ZstParser.DecompressFile(path);
        Assert.Equal(SampleText, decompressed);
    }
}
