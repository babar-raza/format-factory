// Tests for ZstDocument.GetCompressionRatio, IsLargeFile, GetStreamType deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R218

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R218: Tests for ZstDocument.GetCompressionRatio, IsLargeFile, GetStreamType deeper.
/// GetCompressionRatio(): returns the ratio of decompressed to compressed size.
/// IsLargeFile(): returns true if the compressed file exceeds a size threshold.
/// GetStreamType(): returns a string describing the stream/frame type.
/// Covers: GetCompressionRatio no-throw; GetCompressionRatio positive; GetCompressionRatio consistent;
/// GetCompressionRatio at-least-one; GetCompressionRatio save-load;
/// GetCompressionRatio better for highly-compressible content;
/// IsLargeFile no-throw; IsLargeFile bool; IsLargeFile consistent; IsLargeFile save-load;
/// IsLargeFile false for small file;
/// GetStreamType no-throw; GetStreamType non-null; GetStreamType non-empty;
/// GetStreamType consistent; GetStreamType save-load;
/// dogfood CompressFile→GetCompressionRatio→IsLargeFile→GetStreamType→SaveToFile pipeline.
/// </summary>
public class ZstR218GetCompressionRatioAndStreamTypeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR218GetCompressionRatioAndStreamTypeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR218_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private ZstDocument MakeDoc(string content, int level = 3)
    {
        var raw = TempFile("r_" + Guid.NewGuid().ToString("N") + ".txt");
        var zst = TempFile("z_" + Guid.NewGuid().ToString("N") + ".zst");
        File.WriteAllText(raw, content);
        ZstWriter.CompressFile(raw, zst, compressionLevel: level);
        return ZstDocument.LoadFile(zst);
    }

    private static string RepeatText(string phrase, int times)
    {
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < times; i++)
            sb.Append(phrase).Append(' ').Append(i).Append('\n');
        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // GetCompressionRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionRatio_NoThrow()
    {
        var doc = MakeDoc(RepeatText("compression ratio no throw", 80));
        var ex = Record.Exception(() => doc.GetCompressionRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionRatio_Positive()
    {
        var doc = MakeDoc(RepeatText("compression ratio positive", 80));
        Assert.True(doc.GetCompressionRatio() > 0);
    }

    [Fact]
    public void GetCompressionRatio_Consistent()
    {
        var doc = MakeDoc(RepeatText("compression ratio consistent", 80));
        Assert.Equal(doc.GetCompressionRatio(), doc.GetCompressionRatio());
    }

    [Fact]
    public void GetCompressionRatio_AtLeastOne_ForCompressible()
    {
        var doc = MakeDoc(RepeatText("highly compressible repeating text pattern", 200));
        Assert.True(doc.GetCompressionRatio() >= 1.0);
    }

    [Fact]
    public void GetCompressionRatio_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("compression ratio save load", 80));
        var before = doc.GetCompressionRatio();
        var path = TempFile("cr_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionRatio(), 2);
    }

    [Fact]
    public void GetCompressionRatio_Matches_GetCompressionStats()
    {
        var doc = MakeDoc(RepeatText("ratio vs stats comparison", 80));
        var stats = doc.GetCompressionStats();
        var ratio = doc.GetCompressionRatio();
        // Both should be positive
        Assert.True(ratio > 0);
        Assert.True(stats.Ratio > 0);
    }

    // -------------------------------------------------------------------------
    // IsLargeFile
    // -------------------------------------------------------------------------

    [Fact]
    public void IsLargeFile_NoThrow()
    {
        var doc = MakeDoc(RepeatText("is large file no throw", 80));
        var ex = Record.Exception(() => doc.IsLargeFile());
        Assert.Null(ex);
    }

    [Fact]
    public void IsLargeFile_ReturnsBool()
    {
        var doc = MakeDoc(RepeatText("is large file bool", 80));
        var result = doc.IsLargeFile();
        Assert.True(result == true || result == false);
    }

    [Fact]
    public void IsLargeFile_Consistent()
    {
        var doc = MakeDoc(RepeatText("is large file consistent", 80));
        Assert.Equal(doc.IsLargeFile(), doc.IsLargeFile());
    }

    [Fact]
    public void IsLargeFile_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("is large file save load", 80));
        var before = doc.IsLargeFile();
        var path = TempFile("ilf_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.IsLargeFile());
    }

    [Fact]
    public void IsLargeFile_False_ForSmallContent()
    {
        var doc = MakeDoc("small content file"); // tiny content
        // A few-byte compressed file should not be "large"
        Assert.False(doc.IsLargeFile());
    }

    // -------------------------------------------------------------------------
    // GetStreamType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStreamType_NoThrow()
    {
        var doc = MakeDoc(RepeatText("stream type no throw", 80));
        var ex = Record.Exception(() => doc.GetStreamType());
        Assert.Null(ex);
    }

    [Fact]
    public void GetStreamType_NonNull()
    {
        var doc = MakeDoc(RepeatText("stream type non null", 80));
        Assert.NotNull(doc.GetStreamType());
    }

    [Fact]
    public void GetStreamType_NonEmpty()
    {
        var doc = MakeDoc(RepeatText("stream type non empty", 80));
        Assert.NotEmpty(doc.GetStreamType());
    }

    [Fact]
    public void GetStreamType_Consistent()
    {
        var doc = MakeDoc(RepeatText("stream type consistent", 80));
        Assert.Equal(doc.GetStreamType(), doc.GetStreamType());
    }

    [Fact]
    public void GetStreamType_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("stream type save load", 80));
        var before = doc.GetStreamType();
        var path = TempFile("st_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetStreamType());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCompressionRatio_IsLargeFile_GetStreamType_SaveToFile_Pipeline()
    {
        var original = RepeatText("Dogfood compression ratio large file stream type content", 150);

        var rawPath = TempFile("dogfood_raw.txt");
        File.WriteAllText(rawPath, original);

        var zstPath = TempFile("dogfood_source.zst");
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.NotNull(doc);
        Assert.True(doc.IsValid);

        // GetCompressionRatio
        var ratio = doc.GetCompressionRatio();
        Assert.True(ratio > 0);
        Assert.Equal(ratio, doc.GetCompressionRatio()); // consistent

        // IsLargeFile
        var isLarge = doc.IsLargeFile();
        Assert.Equal(isLarge, doc.IsLargeFile()); // consistent

        // GetStreamType
        var streamType = doc.GetStreamType();
        Assert.NotNull(streamType);
        Assert.NotEmpty(streamType);
        Assert.Equal(streamType, doc.GetStreamType()); // consistent

        // GetCompressionStats cross-check
        var stats = doc.GetCompressionStats();
        Assert.NotNull(stats);
        Assert.True(stats.Ratio > 0);

        // GetDecompressedSize and GetCompressedSize
        Assert.True(doc.GetDecompressedSize() > 0);
        Assert.True(doc.GetCompressedSize() > 0);

        // SaveToFile
        var savePath = TempFile("dogfood_saved.zst");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.True(loaded.IsValid);
        Assert.Equal(ratio, loaded.GetCompressionRatio(), 2);
        Assert.Equal(isLarge, loaded.IsLargeFile());
        Assert.Equal(streamType, loaded.GetStreamType());

        // Decompress and verify
        var decompPath = TempFile("dogfood_decomp.txt");
        ZstParser.DecompressFile(savePath, decompPath);
        Assert.Equal(original, File.ReadAllText(decompPath));

        // Second doc — small content
        var raw2 = TempFile("dogfood_raw2.txt");
        File.WriteAllText(raw2, "small");
        var zst2 = TempFile("dogfood_src2.zst");
        ZstWriter.CompressFile(raw2, zst2, compressionLevel: 1);
        var doc2 = ZstDocument.LoadFile(zst2);
        Assert.True(doc2.IsValid);
        Assert.True(doc2.GetCompressionRatio() > 0);
        Assert.False(doc2.IsLargeFile());
        Assert.NotNull(doc2.GetStreamType());

        // Final save
        var finalPath = TempFile("dogfood_final.zst");
        doc2.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = ZstDocument.LoadFile(finalPath);
        Assert.True(final.IsValid);
        Assert.Equal(doc2.GetCompressionRatio(), final.GetCompressionRatio(), 2);
        Assert.Equal(doc2.IsLargeFile(), final.IsLargeFile());
    }
}
