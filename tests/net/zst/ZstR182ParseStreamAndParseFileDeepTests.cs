// Tests for ZstParser.ParseStream, ParseFile with various content types deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R182

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R182: Tests for ZstParser.ParseStream, ParseFile with various content types deeper coverage.
/// ParseStream(stream): parses a ZstDocument from a stream.
/// ParseFile(path): parses a ZstDocument from a file path.
/// Covers: ParseStream non-null; ParseStream CompressedSize positive; ParseStream FrameCount positive;
/// ParseStream IsEmpty false; ParseStream matches ParseFile CompressedSize;
/// ParseStream from MemoryStream; ParseStream from FileStream;
/// ParseFile unicode content; ParseFile large content;
/// ParseFile CompressedSize matches file length; ParseFile after WriteToFile;
/// ValidateFile then ParseFile; multiple ParseFile calls consistent;
/// dogfood WriteToFile->ValidateFile->ParseFile->ParseStream->DecompressFile->Verify pipeline.
/// </summary>
public class ZstR182ParseStreamAndParseFileDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly string TextContent = "Stream and file parsing test content for ZST format.";
    private static readonly string UnicodeContent = "Unicode: こんにちは αβγδ Привет!";
    private static readonly string LargeContent = string.Concat(Enumerable.Repeat("Large content block. ", 500));

    public ZstR182ParseStreamAndParseFileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR182_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // ParseStream
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseStream_FromMemoryStream_NonNull()
    {
        var bytes = ZstWriter.CompressString(TextContent);
        using var ms = new MemoryStream(bytes);
        Assert.NotNull(ZstParser.ParseStream(ms));
    }

    [Fact]
    public void ParseStream_CompressedSize_Positive()
    {
        var bytes = ZstWriter.CompressString(TextContent);
        using var ms = new MemoryStream(bytes);
        Assert.True(ZstParser.ParseStream(ms).CompressedSize > 0);
    }

    [Fact]
    public void ParseStream_FrameCount_Positive()
    {
        var bytes = ZstWriter.CompressString(TextContent);
        using var ms = new MemoryStream(bytes);
        Assert.True(ZstParser.ParseStream(ms).FrameCount > 0);
    }

    [Fact]
    public void ParseStream_IsEmpty_False()
    {
        var bytes = ZstWriter.CompressString(TextContent);
        using var ms = new MemoryStream(bytes);
        Assert.False(ZstParser.ParseStream(ms).IsEmpty);
    }

    [Fact]
    public void ParseStream_MatchesParsedFile_CompressedSize()
    {
        var path = TempFile("stream_vs_file.zst");
        ZstWriter.WriteToFile(TextContent, path);
        var fromFile = ZstParser.ParseFile(path);
        using var fs = new FileStream(path, FileMode.Open, FileAccess.Read);
        var fromStream = ZstParser.ParseStream(fs);
        Assert.Equal(fromFile.CompressedSize, fromStream.CompressedSize);
    }

    [Fact]
    public void ParseStream_FromFileStream_NonNull()
    {
        var path = TempFile("filestream.zst");
        ZstWriter.WriteToFile(TextContent, path);
        using var fs = new FileStream(path, FileMode.Open, FileAccess.Read);
        Assert.NotNull(ZstParser.ParseStream(fs));
    }

    [Fact]
    public void ParseStream_MatchesParsedBytes()
    {
        var bytes = ZstWriter.CompressString(TextContent);
        using var ms = new MemoryStream(bytes);
        var fromStream = ZstParser.ParseStream(ms);
        var fromBytes = ZstParser.ParseBytes(bytes);
        Assert.Equal(fromBytes.CompressedSize, fromStream.CompressedSize);
    }

    // -------------------------------------------------------------------------
    // ParseFile various content types
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseFile_UnicodeContent_NonNull()
    {
        var path = TempFile("unicode.zst");
        ZstWriter.WriteToFile(UnicodeContent, path);
        Assert.NotNull(ZstParser.ParseFile(path));
    }

    [Fact]
    public void ParseFile_UnicodeContent_CompressedSizePositive()
    {
        var path = TempFile("unicode2.zst");
        ZstWriter.WriteToFile(UnicodeContent, path);
        Assert.True(ZstParser.ParseFile(path).CompressedSize > 0);
    }

    [Fact]
    public void ParseFile_LargeContent_CompressedSizePositive()
    {
        var path = TempFile("large.zst");
        ZstWriter.WriteToFile(LargeContent, path);
        Assert.True(ZstParser.ParseFile(path).CompressedSize > 0);
    }

    [Fact]
    public void ParseFile_CompressedSize_MatchesFileLength()
    {
        var path = TempFile("size_check.zst");
        ZstWriter.WriteToFile(TextContent, path);
        var doc = ZstParser.ParseFile(path);
        Assert.Equal(new FileInfo(path).Length, (long)doc.CompressedSize);
    }

    [Fact]
    public void ParseFile_MultipleCallsSameFile_Consistent()
    {
        var path = TempFile("multi_call.zst");
        ZstWriter.WriteToFile(TextContent, path);
        var doc1 = ZstParser.ParseFile(path);
        var doc2 = ZstParser.ParseFile(path);
        Assert.Equal(doc1.CompressedSize, doc2.CompressedSize);
        Assert.Equal(doc1.FrameCount, doc2.FrameCount);
    }

    [Fact]
    public void ValidateFile_ThenParseFile_Consistent()
    {
        var path = TempFile("validate_then_parse.zst");
        ZstWriter.WriteToFile(TextContent, path);
        Assert.True(ZstParser.ValidateFile(path));
        var doc = ZstParser.ParseFile(path);
        Assert.NotNull(doc);
        Assert.True(doc.CompressedSize > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToFile_ValidateFile_ParseFile_ParseStream_DecompressFile_Verify_Pipeline()
    {
        // WriteToFile multiple contents
        var path1 = TempFile("p1.zst");
        var path2 = TempFile("p2.zst");
        ZstWriter.WriteToFile(TextContent, path1);
        ZstWriter.WriteToFile(UnicodeContent, path2);

        // ValidateFile
        Assert.True(ZstParser.ValidateFile(path1));
        Assert.True(ZstParser.ValidateFile(path2));

        // ParseFile
        var doc1 = ZstParser.ParseFile(path1);
        var doc2 = ZstParser.ParseFile(path2);
        Assert.True(doc1.CompressedSize > 0);
        Assert.True(doc2.CompressedSize > 0);
        Assert.True(doc1.FrameCount > 0);
        Assert.False(doc1.IsEmpty);
        Assert.False(doc2.IsEmpty);

        // ParseStream for each
        using var fs1 = new FileStream(path1, FileMode.Open, FileAccess.Read);
        var streamDoc1 = ZstParser.ParseStream(fs1);
        Assert.Equal(doc1.CompressedSize, streamDoc1.CompressedSize);

        using var ms2 = new MemoryStream(File.ReadAllBytes(path2));
        var streamDoc2 = ZstParser.ParseStream(ms2);
        Assert.Equal(doc2.CompressedSize, streamDoc2.CompressedSize);

        // DecompressFile round-trips
        Assert.Equal(TextContent, ZstParser.DecompressFile(path1));
        Assert.Equal(UnicodeContent, ZstParser.DecompressFile(path2));
    }
}
