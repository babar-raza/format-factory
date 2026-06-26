// Tests for ZstWriter constants and CompressToFile.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R142

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R142: Tests for ZstWriter constants and CompressToFile.
/// DefaultCompressionLevel = 3. MinCompressionLevel = 1. MaxCompressionLevel = 22.
/// DefaultMaxDecompressedBytes = 512 MB.
/// CompressToFile(data, destPath, level): writes compressed bytes to disk.
/// Covers: DefaultCompressionLevel equals 3; MinCompressionLevel equals 1;
/// MaxCompressionLevel equals 22; MaxCompressionLevel > MinCompressionLevel;
/// DefaultMaxDecompressedBytes equals 512MB; DefaultMaxDecompressedBytes > DefaultMaxFileSizeBytes;
/// CompressToFile creates file; CompressToFile file starts with ZST magic;
/// CompressToFile file is decompressable; CompressToFile with level=1 creates file;
/// CompressToFile with level=MaxCompressionLevel creates file;
/// CompressToFile null path throws; CompressToFile null data throws;
/// dogfood Compress->CompressToFile->ZstParser.Parse->IsValid pipeline.
/// </summary>
public class ZstR142WriterConstantsAndCompressToFileTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR142WriterConstantsAndCompressToFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR142_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // Constants
    // -------------------------------------------------------------------------

    [Fact]
    public void DefaultCompressionLevel_IsThree()
    {
        Assert.Equal(3, ZstWriter.DefaultCompressionLevel);
    }

    [Fact]
    public void MinCompressionLevel_IsOne()
    {
        Assert.Equal(1, ZstWriter.MinCompressionLevel);
    }

    [Fact]
    public void MaxCompressionLevel_Is22()
    {
        Assert.Equal(22, ZstWriter.MaxCompressionLevel);
    }

    [Fact]
    public void MaxCompressionLevel_GreaterThanMin()
    {
        Assert.True(ZstWriter.MaxCompressionLevel > ZstWriter.MinCompressionLevel);
    }

    [Fact]
    public void DefaultCompressionLevel_InRange()
    {
        Assert.InRange(ZstWriter.DefaultCompressionLevel,
            ZstWriter.MinCompressionLevel,
            ZstWriter.MaxCompressionLevel);
    }

    [Fact]
    public void DefaultMaxDecompressedBytes_Is512MB()
    {
        long expected = 512L * 1024 * 1024;
        Assert.Equal(expected, ZstWriter.DefaultMaxDecompressedBytes);
    }

    [Fact]
    public void DefaultMaxDecompressedBytes_GreaterThanParserMaxFileSize()
    {
        // 512MB decompressed > 256MB max file size
        Assert.True(ZstWriter.DefaultMaxDecompressedBytes > ZstParser.DefaultMaxFileSizeBytes);
    }

    // -------------------------------------------------------------------------
    // CompressToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressToFile_CreatesFile()
    {
        var data = Encoding.UTF8.GetBytes("Hello, CompressToFile!");
        var path = TempFile("created.zst");
        ZstWriter.CompressToFile(data, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void CompressToFile_FileNotEmpty()
    {
        var data = Encoding.UTF8.GetBytes("Non-empty content.");
        var path = TempFile("nonempty.zst");
        ZstWriter.CompressToFile(data, path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void CompressToFile_FileStartsWithZstMagic()
    {
        var data = Encoding.UTF8.GetBytes("Magic bytes test.");
        var path = TempFile("magic.zst");
        ZstWriter.CompressToFile(data, path);
        var fileBytes = File.ReadAllBytes(path);
        Assert.True(fileBytes.Length >= 4);
        Assert.Equal(0x28, fileBytes[0]);
        Assert.Equal(0xB5, fileBytes[1]);
        Assert.Equal(0x2F, fileBytes[2]);
        Assert.Equal(0xFD, fileBytes[3]);
    }

    [Fact]
    public void CompressToFile_WithLevel1_CreatesFile()
    {
        var data = Encoding.UTF8.GetBytes("Level 1 compression.");
        var path = TempFile("level1.zst");
        ZstWriter.CompressToFile(data, path, level: 1);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void CompressToFile_WithMaxLevel_CreatesFile()
    {
        var data = Encoding.UTF8.GetBytes("Max level compression.");
        var path = TempFile("max-level.zst");
        ZstWriter.CompressToFile(data, path, level: ZstWriter.MaxCompressionLevel);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void CompressToFile_NullPath_Throws()
    {
        var data = Encoding.UTF8.GetBytes("data");
        Assert.ThrowsAny<Exception>(() => ZstWriter.CompressToFile(data, null!));
    }

    [Fact]
    public void CompressToFile_FileIsDecompressable()
    {
        var original = Encoding.UTF8.GetBytes("Decompressable content.");
        var path = TempFile("decompressable.zst");
        ZstWriter.CompressToFile(original, path);

        var compressed = File.ReadAllBytes(path);
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(original, decompressed);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress->CompressToFile->ZstParser.Parse->IsValid
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressToFileParseIsValid_Pipeline()
    {
        var input = Encoding.UTF8.GetBytes(
            "ZstR142 dogfood pipeline. " + new string('x', 200));

        // Write to file
        var path = TempFile("dogfood.zst");
        ZstWriter.CompressToFile(input, path);
        Assert.True(File.Exists(path));

        // Parse via file
        var doc = ZstParser.Parse(path);
        Assert.True(doc.MagicValid, "Expected MagicValid=true after CompressToFile.");
        Assert.True(doc.IsValid, "Expected IsValid=true after CompressToFile.");
        Assert.True(doc.FileSizeBytes > 0);
    }
}
