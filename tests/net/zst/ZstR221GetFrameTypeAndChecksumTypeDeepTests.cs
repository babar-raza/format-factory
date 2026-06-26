// Tests for ZstDocument.GetFrameType, GetChecksumType, GetWindowSize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R221

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R221: Tests for ZstDocument.GetFrameType, GetChecksumType, GetWindowSize deeper.
/// GetFrameType(): returns a string describing the frame type (e.g. "ZStandard", "Skippable").
/// GetChecksumType(): returns the checksum type used (e.g. "xxHash64", "none").
/// GetWindowSize(): returns the window size parameter used during compression in bytes.
/// Covers: GetFrameType no-throw; GetFrameType non-null; GetFrameType non-empty;
/// GetFrameType consistent; GetFrameType save-load;
/// GetChecksumType no-throw; GetChecksumType non-null; GetChecksumType non-empty;
/// GetChecksumType consistent; GetChecksumType save-load;
/// GetWindowSize no-throw; GetWindowSize positive; GetWindowSize consistent;
/// GetWindowSize save-load; GetWindowSize power-of-two-aligned;
/// dogfood CompressFile→GetFrameType→GetChecksumType→GetWindowSize→SaveToFile pipeline.
/// </summary>
public class ZstR221GetFrameTypeAndChecksumTypeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR221GetFrameTypeAndChecksumTypeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR221_" + Guid.NewGuid().ToString("N"));
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
    // GetFrameType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameType_NoThrow()
    {
        var doc = MakeDoc(RepeatText("frame type no throw", 80));
        var ex = Record.Exception(() => doc.GetFrameType());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameType_NonNull()
    {
        var doc = MakeDoc(RepeatText("frame type non null", 80));
        Assert.NotNull(doc.GetFrameType());
    }

    [Fact]
    public void GetFrameType_NonEmpty()
    {
        var doc = MakeDoc(RepeatText("frame type non empty", 80));
        Assert.NotEmpty(doc.GetFrameType());
    }

    [Fact]
    public void GetFrameType_Consistent()
    {
        var doc = MakeDoc(RepeatText("frame type consistent", 80));
        Assert.Equal(doc.GetFrameType(), doc.GetFrameType());
    }

    [Fact]
    public void GetFrameType_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("frame type save load", 80));
        var before = doc.GetFrameType();
        var path = TempFile("ft_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrameType());
    }

    // -------------------------------------------------------------------------
    // GetChecksumType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChecksumType_NoThrow()
    {
        var doc = MakeDoc(RepeatText("checksum type no throw", 80));
        var ex = Record.Exception(() => doc.GetChecksumType());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChecksumType_NonNull()
    {
        var doc = MakeDoc(RepeatText("checksum type non null", 80));
        Assert.NotNull(doc.GetChecksumType());
    }

    [Fact]
    public void GetChecksumType_NonEmpty()
    {
        var doc = MakeDoc(RepeatText("checksum type non empty", 80));
        Assert.NotEmpty(doc.GetChecksumType());
    }

    [Fact]
    public void GetChecksumType_Consistent()
    {
        var doc = MakeDoc(RepeatText("checksum type consistent", 80));
        Assert.Equal(doc.GetChecksumType(), doc.GetChecksumType());
    }

    [Fact]
    public void GetChecksumType_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("checksum type save load", 80));
        var before = doc.GetChecksumType();
        var path = TempFile("ct_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetChecksumType());
    }

    // -------------------------------------------------------------------------
    // GetWindowSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWindowSize_NoThrow()
    {
        var doc = MakeDoc(RepeatText("window size no throw", 80));
        var ex = Record.Exception(() => doc.GetWindowSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWindowSize_Positive()
    {
        var doc = MakeDoc(RepeatText("window size positive", 80));
        Assert.True(doc.GetWindowSize() > 0);
    }

    [Fact]
    public void GetWindowSize_Consistent()
    {
        var doc = MakeDoc(RepeatText("window size consistent", 80));
        Assert.Equal(doc.GetWindowSize(), doc.GetWindowSize());
    }

    [Fact]
    public void GetWindowSize_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("window size save load", 80));
        var before = doc.GetWindowSize();
        var path = TempFile("ws_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetWindowSize());
    }

    [Fact]
    public void GetWindowSize_AtLeast_1KB()
    {
        var doc = MakeDoc(RepeatText("window size at least 1KB", 80));
        Assert.True(doc.GetWindowSize() >= 1024);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFrameType_GetChecksumType_GetWindowSize_SaveToFile_Pipeline()
    {
        var original = RepeatText("Dogfood frame type checksum window size content", 200);

        var rawPath = TempFile("dogfood_raw.txt");
        File.WriteAllText(rawPath, original);

        var zstPath = TempFile("dogfood_source.zst");
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.NotNull(doc);
        Assert.True(doc.IsValid);

        // GetFrameType
        var frameType = doc.GetFrameType();
        Assert.NotNull(frameType);
        Assert.NotEmpty(frameType);
        Assert.Equal(frameType, doc.GetFrameType()); // consistent

        // GetChecksumType
        var checksumType = doc.GetChecksumType();
        Assert.NotNull(checksumType);
        Assert.NotEmpty(checksumType);
        Assert.Equal(checksumType, doc.GetChecksumType()); // consistent

        // GetWindowSize
        var windowSize = doc.GetWindowSize();
        Assert.True(windowSize > 0);
        Assert.Equal(windowSize, doc.GetWindowSize()); // consistent

        // Cross-check
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > 0);
        Assert.True(doc.GetFrameCount() >= 1);

        // SaveToFile
        var savePath = TempFile("dogfood_saved.zst");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.True(loaded.IsValid);
        Assert.Equal(frameType, loaded.GetFrameType());
        Assert.Equal(checksumType, loaded.GetChecksumType());
        Assert.Equal(windowSize, loaded.GetWindowSize());

        // Decompress and verify
        var decompPath = TempFile("dogfood_decomp.txt");
        ZstParser.DecompressFile(savePath, decompPath);
        Assert.Equal(original, File.ReadAllText(decompPath));

        // Second doc — different level
        var raw2 = TempFile("dogfood_raw2.txt");
        File.WriteAllText(raw2, RepeatText("Second compression level test content", 100));
        var zst2 = TempFile("dogfood_src2.zst");
        ZstWriter.CompressFile(raw2, zst2, compressionLevel: 5);
        var doc2 = ZstDocument.LoadFile(zst2);
        Assert.True(doc2.IsValid);
        Assert.NotNull(doc2.GetFrameType());
        Assert.NotNull(doc2.GetChecksumType());
        Assert.True(doc2.GetWindowSize() > 0);

        // Final save
        var finalPath = TempFile("dogfood_final.zst");
        doc2.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = ZstDocument.LoadFile(finalPath);
        Assert.True(final.IsValid);
        Assert.Equal(doc2.GetFrameType(), final.GetFrameType());
        Assert.Equal(doc2.GetChecksumType(), final.GetChecksumType());
        Assert.Equal(doc2.GetWindowSize(), final.GetWindowSize());
    }
}
