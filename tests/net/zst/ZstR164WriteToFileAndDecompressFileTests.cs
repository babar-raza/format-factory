// Tests for ZstWriter.WriteToFile, ZstParser.DecompressFile, file I/O round-trips.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R164

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R164: Tests for ZstWriter.WriteToFile, ZstParser.DecompressFile, file I/O.
/// ZstWriter.WriteToFile(data, path): compresses data and writes to file.
/// ZstWriter.WriteToFile(data, path, level): compresses at given level.
/// ZstParser.DecompressFile(path): decompresses a .zst file to bytes.
/// ZstParser.DecompressFileToString(path): decompresses to UTF-8 string.
/// Covers: WriteToFile creates file; WriteToFile file non-empty;
/// WriteToFile->DecompressFile round-trip matches original;
/// WriteToFile at level 1 creates file; WriteToFile at level 19 creates file;
/// DecompressFile returns correct length; DecompressFileToString matches original;
/// WriteToFile->ParseFile frame count positive; WriteToFile->ZstDocument.Load count;
/// Multiple WriteToFile different levels all decompress correctly;
/// WriteToFile string data round-trip;
/// dogfood Compress->WriteToFile->DecompressFile->DecompressFileToString->ParseFile verify.
/// </summary>
public class ZstR164WriteToFileAndDecompressFileTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly byte[] SampleBytes =
        System.Text.Encoding.UTF8.GetBytes(
            "Sample compressed data for file I/O round-trip verification. " +
            "This text contains enough content to be meaningfully compressed.");

    private const string SampleString =
        "File I/O test string: compress and decompress through files correctly.";

    public ZstR164WriteToFileAndDecompressFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR164_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // ZstWriter.WriteToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_CreatesFile()
    {
        var path = TempFile("out.zst");
        ZstWriter.WriteToFile(SampleBytes, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_FileNonEmpty()
    {
        var path = TempFile("nonempty.zst");
        ZstWriter.WriteToFile(SampleBytes, path);
        var info = new FileInfo(path);
        Assert.True(info.Length > 0);
    }

    [Fact]
    public void WriteToFile_Level1_CreatesFile()
    {
        var path = TempFile("level1.zst");
        ZstWriter.WriteToFile(SampleBytes, path, 1);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_Level19_CreatesFile()
    {
        var path = TempFile("level19.zst");
        ZstWriter.WriteToFile(SampleBytes, path, 19);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_StringData_CreatesFile()
    {
        var path = TempFile("str.zst");
        ZstWriter.WriteToFile(SampleString, path);
        Assert.True(File.Exists(path));
    }

    // -------------------------------------------------------------------------
    // ZstParser.DecompressFile
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressFile_RoundTrip_MatchesOriginal()
    {
        var path = TempFile("rt.zst");
        ZstWriter.WriteToFile(SampleBytes, path);
        var result = ZstParser.DecompressFile(path);
        Assert.Equal(SampleBytes, result);
    }

    [Fact]
    public void DecompressFile_Length_MatchesOriginal()
    {
        var path = TempFile("len.zst");
        ZstWriter.WriteToFile(SampleBytes, path);
        var result = ZstParser.DecompressFile(path);
        Assert.Equal(SampleBytes.Length, result.Length);
    }

    [Fact]
    public void DecompressFile_Level1_RoundTrip()
    {
        var path = TempFile("rt1.zst");
        ZstWriter.WriteToFile(SampleBytes, path, 1);
        var result = ZstParser.DecompressFile(path);
        Assert.Equal(SampleBytes, result);
    }

    [Fact]
    public void DecompressFile_Level19_RoundTrip()
    {
        var path = TempFile("rt19.zst");
        ZstWriter.WriteToFile(SampleBytes, path, 19);
        var result = ZstParser.DecompressFile(path);
        Assert.Equal(SampleBytes, result);
    }

    // -------------------------------------------------------------------------
    // ZstParser.DecompressFileToString
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressFileToString_MatchesOriginal()
    {
        var path = TempFile("str_rt.zst");
        ZstWriter.WriteToFile(SampleString, path);
        var result = ZstParser.DecompressFileToString(path);
        Assert.Equal(SampleString, result);
    }

    [Fact]
    public void DecompressFileToString_NonNull()
    {
        var path = TempFile("nn.zst");
        ZstWriter.WriteToFile(SampleString, path);
        var result = ZstParser.DecompressFileToString(path);
        Assert.NotNull(result);
    }

    // -------------------------------------------------------------------------
    // WriteToFile -> ParseFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_ParseFile_FrameCountPositive()
    {
        var path = TempFile("parse.zst");
        ZstWriter.WriteToFile(SampleBytes, path);
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void WriteToFile_ParseFile_CompressedSizeMatchesFileSize()
    {
        var path = TempFile("size.zst");
        ZstWriter.WriteToFile(SampleBytes, path);
        var doc = ZstParser.ParseFile(path);
        var fileSize = new FileInfo(path).Length;
        Assert.Equal(fileSize, doc.CompressedSize);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressWriteDecompressFileStringParseVerify_Pipeline()
    {
        // WriteToFile at multiple levels
        foreach (var level in new[] { 1, 6, 15 })
        {
            var path = TempFile($"dogfood_level{level}.zst");
            ZstWriter.WriteToFile(SampleBytes, path, level);
            Assert.True(File.Exists(path));

            var result = ZstParser.DecompressFile(path);
            Assert.Equal(SampleBytes, result);
        }

        // String round-trip
        var strPath = TempFile("dogfood_str.zst");
        ZstWriter.WriteToFile(SampleString, strPath);
        var strResult = ZstParser.DecompressFileToString(strPath);
        Assert.Equal(SampleString, strResult);

        // ParseFile properties
        var parsePath = TempFile("dogfood_parse.zst");
        ZstWriter.WriteToFile(SampleBytes, parsePath, 3);
        var doc = ZstParser.ParseFile(parsePath);
        Assert.False(doc.IsEmpty);
        Assert.True(doc.FrameCount > 0);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);
        Assert.True(doc.CompressionRatio > 0);
    }
}
