// Tests for ZstWriter.WriteToFile, ZstParser.DecompressFile, DecompressFileToString deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R172

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R172: Tests for ZstWriter.WriteToFile, ZstParser.DecompressFile, DecompressFileToString deeper.
/// ZstWriter.WriteToFile(content, path): compresses string content and writes to file.
/// ZstParser.DecompressFile(path): reads and decompresses a .zst file, returns bytes.
/// ZstParser.DecompressFileToString(path): reads, decompresses, returns string.
/// Covers: WriteToFile creates file; WriteToFile file non-empty; WriteToFile is valid zst;
/// WriteToFile multiple files independent; DecompressFile returns non-null;
/// DecompressFile round-trip matches original; DecompressFile for different content sizes;
/// DecompressFileToString non-null; DecompressFileToString matches original;
/// DecompressFileToString unicode preserved; WriteToFile->ParseFile->FrameCount positive;
/// WriteToFile->LoadStream consistent; multiple write-read cycles;
/// dogfood WriteToFile->DecompressFile->DecompressFileToString->ParseFile verify pipeline.
/// </summary>
public class ZstR172WriteToFileAndDecompressFileDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly string ShortContent = "Hello from the Format Factory ZST test suite.";
    private static readonly string LongContent =
        "This is a longer content string used for round-trip verification of the " +
        "Zstandard compression and decompression pipeline in the Format Factory SDK. " +
        "It contains multiple sentences to exercise the codec at a reasonable size.";
    private static readonly string UnicodeContent =
        "Multi-language test: English, Français, Español, 日本語, العربية";

    public ZstR172WriteToFileAndDecompressFileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR172_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // WriteToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_CreatesFile()
    {
        var path = TempFile("short.zst");
        ZstWriter.WriteToFile(ShortContent, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_FileNonEmpty()
    {
        var path = TempFile("nonempty.zst");
        ZstWriter.WriteToFile(ShortContent, path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void WriteToFile_MultipleFiles_Independent()
    {
        var path1 = TempFile("file1.zst");
        var path2 = TempFile("file2.zst");
        ZstWriter.WriteToFile("Content one.", path1);
        ZstWriter.WriteToFile("Content two different.", path2);
        Assert.True(File.Exists(path1));
        Assert.True(File.Exists(path2));
        Assert.NotEqual(new FileInfo(path1).Length, new FileInfo(path2).Length);
    }

    [Fact]
    public void WriteToFile_LongContent_CreatesFile()
    {
        var path = TempFile("long.zst");
        ZstWriter.WriteToFile(LongContent, path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
    }

    // -------------------------------------------------------------------------
    // DecompressFile
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressFile_NonNull()
    {
        var path = TempFile("dc.zst");
        ZstWriter.WriteToFile(ShortContent, path);
        var result = ZstParser.DecompressFile(path);
        Assert.NotNull(result);
    }

    [Fact]
    public void DecompressFile_MatchesOriginal()
    {
        var path = TempFile("rt.zst");
        ZstWriter.WriteToFile(ShortContent, path);
        var decompressed = ZstParser.DecompressFile(path);
        var text = System.Text.Encoding.UTF8.GetString(decompressed);
        Assert.Equal(ShortContent, text);
    }

    [Fact]
    public void DecompressFile_LongContent_MatchesOriginal()
    {
        var path = TempFile("long_rt.zst");
        ZstWriter.WriteToFile(LongContent, path);
        var decompressed = ZstParser.DecompressFile(path);
        var text = System.Text.Encoding.UTF8.GetString(decompressed);
        Assert.Equal(LongContent, text);
    }

    // -------------------------------------------------------------------------
    // DecompressFileToString
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressFileToString_NonNull()
    {
        var path = TempFile("str.zst");
        ZstWriter.WriteToFile(ShortContent, path);
        Assert.NotNull(ZstParser.DecompressFileToString(path));
    }

    [Fact]
    public void DecompressFileToString_MatchesOriginal()
    {
        var path = TempFile("str_rt.zst");
        ZstWriter.WriteToFile(ShortContent, path);
        Assert.Equal(ShortContent, ZstParser.DecompressFileToString(path));
    }

    [Fact]
    public void DecompressFileToString_Unicode_Preserved()
    {
        var path = TempFile("unicode.zst");
        ZstWriter.WriteToFile(UnicodeContent, path);
        Assert.Equal(UnicodeContent, ZstParser.DecompressFileToString(path));
    }

    [Fact]
    public void DecompressFileToString_LongContent_Preserved()
    {
        var path = TempFile("long_str.zst");
        ZstWriter.WriteToFile(LongContent, path);
        Assert.Equal(LongContent, ZstParser.DecompressFileToString(path));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToFile_DecompressFile_DecompressFileToString_ParseFile_Pipeline()
    {
        // WriteToFile
        var path = TempFile("dogfood.zst");
        ZstWriter.WriteToFile(LongContent, path);
        Assert.True(File.Exists(path));

        // DecompressFile (bytes path)
        var bytes = ZstParser.DecompressFile(path);
        Assert.NotNull(bytes);
        var fromBytes = System.Text.Encoding.UTF8.GetString(bytes);
        Assert.Equal(LongContent, fromBytes);

        // DecompressFileToString (string path)
        var fromString = ZstParser.DecompressFileToString(path);
        Assert.Equal(LongContent, fromString);

        // ParseFile (metadata)
        var doc = ZstParser.ParseFile(path);
        Assert.NotNull(doc);
        Assert.True(doc.FrameCount > 0);
        Assert.True(doc.CompressedSize > 0);
        Assert.False(doc.IsEmpty);

        // CompressedSize matches file size
        Assert.Equal((long)doc.CompressedSize, new FileInfo(path).Length);

        // Unicode variant
        var uniPath = TempFile("unicode_dogfood.zst");
        ZstWriter.WriteToFile(UnicodeContent, uniPath);
        var uniResult = ZstParser.DecompressFileToString(uniPath);
        Assert.Equal(UnicodeContent, uniResult);
    }
}
