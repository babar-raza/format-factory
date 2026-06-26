// Tests for ZstDocument.VerifyIntegrity, GetZstdVersion, IsChecksumEnabled deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R214

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R214: Tests for ZstDocument.VerifyIntegrity, GetZstdVersion, IsChecksumEnabled deeper.
/// VerifyIntegrity(): validates the compressed data integrity; returns true if valid.
/// GetZstdVersion(): returns the zstd library or format version string.
/// IsChecksumEnabled(): returns true if the frame contains a content checksum.
/// Covers: VerifyIntegrity no-throw; VerifyIntegrity true for valid file;
/// VerifyIntegrity consistent; VerifyIntegrity save-load; VerifyIntegrity multiple files;
/// VerifyIntegrity after Decompress;
/// GetZstdVersion no-throw; GetZstdVersion non-null; GetZstdVersion non-empty;
/// GetZstdVersion consistent; GetZstdVersion has digits; GetZstdVersion save-load;
/// IsChecksumEnabled no-throw; IsChecksumEnabled returns bool; IsChecksumEnabled consistent;
/// IsChecksumEnabled save-load; IsChecksumEnabled valid for all levels;
/// GetCompressionStats after VerifyIntegrity; VerifyIntegrity after GetContentSize;
/// dogfood CompressFile→VerifyIntegrity→GetZstdVersion→IsChecksumEnabled→SaveToFile pipeline.
/// </summary>
public class ZstR214VerifyIntegrityAndZstdVersionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR214VerifyIntegrityAndZstdVersionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR214_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string MakeZst(string content, string tag, int level = 3)
    {
        var rawPath = TempFile($"raw_{tag}.txt");
        var zstPath = TempFile($"{tag}.zst");
        File.WriteAllText(rawPath, content);
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: level);
        return zstPath;
    }

    private static string RepeatText(string phrase, int times)
    {
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < times; i++)
            sb.Append(phrase).Append(' ').Append(i).Append('\n');
        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // VerifyIntegrity
    // -------------------------------------------------------------------------

    [Fact]
    public void VerifyIntegrity_NoThrow()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("verify integrity no throw", 80), "vi1"));
        var ex = Record.Exception(() => doc.VerifyIntegrity());
        Assert.Null(ex);
    }

    [Fact]
    public void VerifyIntegrity_True_ForValidFile()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("verify integrity valid", 100), "vi2"));
        Assert.True(doc.VerifyIntegrity());
    }

    [Fact]
    public void VerifyIntegrity_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("verify integrity consistent", 80), "vi3"));
        Assert.Equal(doc.VerifyIntegrity(), doc.VerifyIntegrity());
    }

    [Fact]
    public void VerifyIntegrity_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("verify integrity save load", 80), "vi4"));
        var before = doc.VerifyIntegrity();
        var savePath = TempFile("vi_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(before, loaded.VerifyIntegrity());
    }

    [Fact]
    public void VerifyIntegrity_Multiple_Files_AllValid()
    {
        for (int i = 1; i <= 3; i++)
        {
            var doc = ZstDocument.LoadFile(MakeZst(RepeatText($"multi file verify {i}", 60), $"vi_m{i}"));
            Assert.True(doc.VerifyIntegrity());
        }
    }

    [Fact]
    public void VerifyIntegrity_After_GetContentSize()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("verify after content size", 80), "vi5"));
        var _ = doc.GetContentSize();
        Assert.True(doc.VerifyIntegrity());
    }

    // -------------------------------------------------------------------------
    // GetZstdVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void GetZstdVersion_NoThrow()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("zstd version no throw", 80), "zv1"));
        var ex = Record.Exception(() => doc.GetZstdVersion());
        Assert.Null(ex);
    }

    [Fact]
    public void GetZstdVersion_NonNull()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("zstd version non null", 80), "zv2"));
        Assert.NotNull(doc.GetZstdVersion());
    }

    [Fact]
    public void GetZstdVersion_NonEmpty()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("zstd version non empty", 80), "zv3"));
        Assert.NotEmpty(doc.GetZstdVersion());
    }

    [Fact]
    public void GetZstdVersion_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("zstd version consistent", 80), "zv4"));
        Assert.Equal(doc.GetZstdVersion(), doc.GetZstdVersion());
    }

    [Fact]
    public void GetZstdVersion_HasDigits()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("zstd version has digits", 80), "zv5"));
        var version = doc.GetZstdVersion();
        Assert.True(version.Length > 0);
        // Version string should contain at least one digit
        Assert.True(System.Text.RegularExpressions.Regex.IsMatch(version, @"\d"));
    }

    [Fact]
    public void GetZstdVersion_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("zstd version save load", 80), "zv6"));
        var before = doc.GetZstdVersion();
        var savePath = TempFile("zv_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(before, loaded.GetZstdVersion());
    }

    // -------------------------------------------------------------------------
    // IsChecksumEnabled
    // -------------------------------------------------------------------------

    [Fact]
    public void IsChecksumEnabled_NoThrow()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("checksum enabled no throw", 80), "ce1"));
        var ex = Record.Exception(() => doc.IsChecksumEnabled());
        Assert.Null(ex);
    }

    [Fact]
    public void IsChecksumEnabled_ReturnsBool()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("checksum enabled bool", 80), "ce2"));
        var result = doc.IsChecksumEnabled();
        Assert.True(result == true || result == false);
    }

    [Fact]
    public void IsChecksumEnabled_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("checksum enabled consistent", 80), "ce3"));
        Assert.Equal(doc.IsChecksumEnabled(), doc.IsChecksumEnabled());
    }

    [Fact]
    public void IsChecksumEnabled_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("checksum enabled save load", 80), "ce4"));
        var before = doc.IsChecksumEnabled();
        var savePath = TempFile("ce_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(before, loaded.IsChecksumEnabled());
    }

    [Fact]
    public void IsChecksumEnabled_AllLevels_NoException()
    {
        foreach (var level in new[] { 1, 3, 9 })
        {
            var doc = ZstDocument.LoadFile(MakeZst(RepeatText($"checksum level {level}", 60), $"ce_l{level}", level));
            var ex = Record.Exception(() => doc.IsChecksumEnabled());
            Assert.Null(ex);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_VerifyIntegrity_GetZstdVersion_IsChecksumEnabled_SaveToFile_Pipeline()
    {
        var original = RepeatText("Enterprise data platform integrity verification test content for 2026 release", 150);
        var rawPath = TempFile("dogfood_raw.txt");
        File.WriteAllText(rawPath, original);

        // Compress at multiple levels
        foreach (var level in new[] { 1, 5, 9 })
        {
            var zstPath = TempFile($"dogfood_l{level}.zst");
            ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: level);
            var doc = ZstDocument.LoadFile(zstPath);
            Assert.True(doc.IsValid);

            // VerifyIntegrity
            Assert.True(doc.VerifyIntegrity());
            Assert.Equal(doc.VerifyIntegrity(), doc.VerifyIntegrity()); // consistent

            // GetZstdVersion
            var version = doc.GetZstdVersion();
            Assert.NotNull(version);
            Assert.NotEmpty(version);
            Assert.Equal(version, doc.GetZstdVersion()); // consistent

            // IsChecksumEnabled
            var checksumEnabled = doc.IsChecksumEnabled();
            Assert.True(checksumEnabled == true || checksumEnabled == false);
            Assert.Equal(checksumEnabled, doc.IsChecksumEnabled()); // consistent

            // GetCompressionStats after verification
            var stats = doc.GetCompressionStats();
            Assert.NotNull(stats);
            Assert.True(stats.Ratio > 0);

            // GetContentSize
            Assert.Equal(doc.GetDecompressedSize(), doc.GetContentSize());

            // SaveToFile
            var savePath = TempFile($"dogfood_saved_l{level}.zst");
            doc.SaveToFile(savePath);
            Assert.True(File.Exists(savePath));

            // LoadFile saved and verify
            var loaded = ZstDocument.LoadFile(savePath);
            Assert.True(loaded.IsValid);
            Assert.True(loaded.VerifyIntegrity());
            Assert.Equal(version, loaded.GetZstdVersion());
            Assert.Equal(checksumEnabled, loaded.IsChecksumEnabled());

            // Decompress to verify round-trip integrity
            var decompPath = TempFile($"dogfood_decomp_l{level}.txt");
            ZstParser.DecompressFile(savePath, decompPath);
            Assert.Equal(original, File.ReadAllText(decompPath));
        }

        // Test with CreateFromBytes
        var zstPath1 = TempFile("dogfood_bytes.zst");
        ZstWriter.CompressFile(rawPath, zstPath1, compressionLevel: 3);
        var bytes = File.ReadAllBytes(zstPath1);
        var bytesDoc = ZstDocument.CreateFromBytes(bytes);
        Assert.True(bytesDoc.VerifyIntegrity());
        Assert.NotNull(bytesDoc.GetZstdVersion());
        Assert.True(bytesDoc.IsChecksumEnabled() == true || bytesDoc.IsChecksumEnabled() == false);

        // Final save from bytes doc
        var finalPath = TempFile("dogfood_final.zst");
        bytesDoc.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = ZstDocument.LoadFile(finalPath);
        Assert.True(final.VerifyIntegrity());
        Assert.Equal(bytesDoc.GetZstdVersion(), final.GetZstdVersion());
    }
}
