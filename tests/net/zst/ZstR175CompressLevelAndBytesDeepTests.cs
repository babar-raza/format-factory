// Tests for ZstWriter.CompressString at various levels, CompressBytes, WriteToFile levels.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R175

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R175: Tests for ZstWriter compression levels and CompressBytes coverage.
/// CompressString(content, level): compresses a string at the given compression level.
/// CompressBytes(data, level): compresses a byte array at the given level.
/// WriteToFile(content, path, level): writes compressed content to file at the given level.
/// Covers: CompressString level 1 non-null; CompressString level 9 non-null;
/// CompressString level 19 non-null; higher level produces smaller or equal output;
/// CompressBytes non-null; CompressBytes length positive; CompressBytes round-trip matches;
/// DecompressBytes restores original; CompressBytes level 1 vs 19 both valid;
/// WriteToFile level 1 creates file; WriteToFile level 9 creates file;
/// dogfood CompressString->CompressBytes->WriteToFile->Decompress->Verify pipeline at multiple levels.
/// </summary>
public class ZstR175CompressLevelAndBytesDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly string SampleText =
        "The quick brown fox jumps over the lazy dog. " +
        "Pack my box with five dozen liquor jugs. " +
        "How vexingly quick daft zebras jump!";

    public ZstR175CompressLevelAndBytesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR175_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // CompressString at various levels
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressString_Level1_NonNull()
    {
        var result = ZstWriter.CompressString(SampleText, 1);
        Assert.NotNull(result);
    }

    [Fact]
    public void CompressString_Level1_LengthPositive()
    {
        var result = ZstWriter.CompressString(SampleText, 1);
        Assert.True(result.Length > 0);
    }

    [Fact]
    public void CompressString_Level9_NonNull()
    {
        var result = ZstWriter.CompressString(SampleText, 9);
        Assert.NotNull(result);
    }

    [Fact]
    public void CompressString_Level19_NonNull()
    {
        var result = ZstWriter.CompressString(SampleText, 19);
        Assert.NotNull(result);
    }

    [Fact]
    public void CompressString_AllLevels_Decompressible()
    {
        foreach (var level in new[] { 1, 3, 9, 15, 19 })
        {
            var compressed = ZstWriter.CompressString(SampleText, level);
            var decompressed = ZstParser.DecompressBytes(compressed);
            Assert.Equal(SampleText, decompressed);
        }
    }

    [Fact]
    public void CompressString_HigherLevel_SmallerOrEqual()
    {
        var low = ZstWriter.CompressString(new string('X', 1000), 1);
        var high = ZstWriter.CompressString(new string('X', 1000), 19);
        // Higher compression level should produce same or smaller output for repetitive data
        Assert.True(high.Length <= low.Length);
    }

    // -------------------------------------------------------------------------
    // CompressBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressBytes_NonNull()
    {
        var data = System.Text.Encoding.UTF8.GetBytes(SampleText);
        var result = ZstWriter.CompressBytes(data);
        Assert.NotNull(result);
    }

    [Fact]
    public void CompressBytes_LengthPositive()
    {
        var data = System.Text.Encoding.UTF8.GetBytes(SampleText);
        var result = ZstWriter.CompressBytes(data);
        Assert.True(result.Length > 0);
    }

    [Fact]
    public void CompressBytes_RoundTrip_MatchesOriginal()
    {
        var data = System.Text.Encoding.UTF8.GetBytes(SampleText);
        var compressed = ZstWriter.CompressBytes(data);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, decompressed);
    }

    [Fact]
    public void CompressBytes_Level1_Valid()
    {
        var data = System.Text.Encoding.UTF8.GetBytes(SampleText);
        var compressed = ZstWriter.CompressBytes(data, 1);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, decompressed);
    }

    [Fact]
    public void CompressBytes_Level19_Valid()
    {
        var data = System.Text.Encoding.UTF8.GetBytes(SampleText);
        var compressed = ZstWriter.CompressBytes(data, 19);
        var decompressed = ZstParser.DecompressBytes(compressed);
        Assert.Equal(SampleText, decompressed);
    }

    // -------------------------------------------------------------------------
    // WriteToFile at various levels
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_Level1_CreatesFile()
    {
        var path = TempFile("level1.zst");
        ZstWriter.WriteToFile(SampleText, path, 1);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_Level9_CreatesFile()
    {
        var path = TempFile("level9.zst");
        ZstWriter.WriteToFile(SampleText, path, 9);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_Level19_ContentDecompressible()
    {
        var path = TempFile("level19.zst");
        ZstWriter.WriteToFile(SampleText, path, 19);
        var decompressed = ZstParser.DecompressFile(path);
        Assert.Equal(SampleText, decompressed);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressString_CompressBytes_WriteToFile_Decompress_Verify_MultiLevel_Pipeline()
    {
        // CompressString at levels 1, 3, 19
        var c1 = ZstWriter.CompressString(SampleText, 1);
        var c3 = ZstWriter.CompressString(SampleText, 3);
        var c19 = ZstWriter.CompressString(SampleText, 19);
        Assert.NotNull(c1);
        Assert.NotNull(c3);
        Assert.NotNull(c19);

        // All decompress to original
        Assert.Equal(SampleText, ZstParser.DecompressBytes(c1));
        Assert.Equal(SampleText, ZstParser.DecompressBytes(c3));
        Assert.Equal(SampleText, ZstParser.DecompressBytes(c19));

        // CompressBytes round-trip
        var raw = System.Text.Encoding.UTF8.GetBytes(SampleText);
        var cb = ZstWriter.CompressBytes(raw, 3);
        Assert.Equal(SampleText, ZstParser.DecompressBytes(cb));

        // WriteToFile at level 3
        var path = TempFile("dogfood.zst");
        ZstWriter.WriteToFile(SampleText, path, 3);
        Assert.True(File.Exists(path));
        var decompressed = ZstParser.DecompressFile(path);
        Assert.Equal(SampleText, decompressed);

        // Validate file
        Assert.True(ZstParser.ValidateFile(path));

        // ParseFile
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.False(doc.IsEmpty);
    }
}
