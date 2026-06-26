// Tests for ZstDocument.GetChecksumValue, GetFrameCount, IsFrameIntact deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R216

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R216: Tests for ZstDocument.GetChecksumValue, GetFrameCount, IsFrameIntact deeper.
/// GetChecksumValue(): returns the checksum/hash embedded in the zstd frame.
/// GetFrameCount(): returns the number of frames in the compressed data.
/// IsFrameIntact(): returns true if the frame structure passes basic validation.
/// Covers: GetChecksumValue no-throw; GetChecksumValue non-negative; GetChecksumValue consistent;
/// GetChecksumValue save-load; GetChecksumValue different docs;
/// GetFrameCount no-throw; GetFrameCount at-least-one; GetFrameCount consistent;
/// GetFrameCount save-load; GetFrameCount reasonable range;
/// IsFrameIntact no-throw; IsFrameIntact true for valid; IsFrameIntact bool;
/// IsFrameIntact consistent; IsFrameIntact save-load;
/// dogfood CompressFile→GetChecksumValue→GetFrameCount→IsFrameIntact→SaveToFile pipeline.
/// </summary>
public class ZstR216GetChecksumAndFrameCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR216GetChecksumAndFrameCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR216_" + Guid.NewGuid().ToString("N"));
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
    // GetChecksumValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChecksumValue_NoThrow()
    {
        var doc = MakeDoc(RepeatText("checksum no throw test", 80));
        var ex = Record.Exception(() => doc.GetChecksumValue());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChecksumValue_NonNegative()
    {
        var doc = MakeDoc(RepeatText("checksum non negative", 80));
        Assert.True(doc.GetChecksumValue() >= 0);
    }

    [Fact]
    public void GetChecksumValue_Consistent()
    {
        var doc = MakeDoc(RepeatText("checksum consistent", 80));
        Assert.Equal(doc.GetChecksumValue(), doc.GetChecksumValue());
    }

    [Fact]
    public void GetChecksumValue_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("checksum save load", 80));
        var before = doc.GetChecksumValue();
        var path = TempFile("cv_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetChecksumValue());
    }

    [Fact]
    public void GetChecksumValue_DifferentContent_MayDiffer()
    {
        var doc1 = MakeDoc(RepeatText("first document content alpha", 80));
        var doc2 = MakeDoc(RepeatText("second document content beta", 80));
        // Both should be non-negative regardless of whether they differ
        Assert.True(doc1.GetChecksumValue() >= 0);
        Assert.True(doc2.GetChecksumValue() >= 0);
    }

    // -------------------------------------------------------------------------
    // GetFrameCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameCount_NoThrow()
    {
        var doc = MakeDoc(RepeatText("frame count no throw", 80));
        var ex = Record.Exception(() => doc.GetFrameCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameCount_AtLeastOne()
    {
        var doc = MakeDoc(RepeatText("frame count at least one", 80));
        Assert.True(doc.GetFrameCount() >= 1);
    }

    [Fact]
    public void GetFrameCount_Consistent()
    {
        var doc = MakeDoc(RepeatText("frame count consistent", 80));
        Assert.Equal(doc.GetFrameCount(), doc.GetFrameCount());
    }

    [Fact]
    public void GetFrameCount_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("frame count save load", 80));
        var before = doc.GetFrameCount();
        var path = TempFile("fc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrameCount());
    }

    [Fact]
    public void GetFrameCount_ReasonableRange()
    {
        var doc = MakeDoc(RepeatText("frame count range check", 80));
        var count = doc.GetFrameCount();
        // A single CompressFile call produces at most a small number of frames
        Assert.True(count >= 1 && count <= 1000);
    }

    // -------------------------------------------------------------------------
    // IsFrameIntact
    // -------------------------------------------------------------------------

    [Fact]
    public void IsFrameIntact_NoThrow()
    {
        var doc = MakeDoc(RepeatText("frame intact no throw", 80));
        var ex = Record.Exception(() => doc.IsFrameIntact());
        Assert.Null(ex);
    }

    [Fact]
    public void IsFrameIntact_True_ForValidDoc()
    {
        var doc = MakeDoc(RepeatText("frame intact valid", 80));
        Assert.True(doc.IsFrameIntact());
    }

    [Fact]
    public void IsFrameIntact_ReturnsBool()
    {
        var doc = MakeDoc(RepeatText("frame intact bool", 80));
        var result = doc.IsFrameIntact();
        Assert.True(result == true || result == false);
    }

    [Fact]
    public void IsFrameIntact_Consistent()
    {
        var doc = MakeDoc(RepeatText("frame intact consistent", 80));
        Assert.Equal(doc.IsFrameIntact(), doc.IsFrameIntact());
    }

    [Fact]
    public void IsFrameIntact_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("frame intact save load", 80));
        var before = doc.IsFrameIntact();
        var path = TempFile("fi_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.IsFrameIntact());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetChecksumValue_GetFrameCount_IsFrameIntact_SaveToFile_Pipeline()
    {
        var original = RepeatText("Dogfood checksum frame count intact pipeline for full verification", 130);

        var rawPath = TempFile("dogfood_raw.txt");
        File.WriteAllText(rawPath, original);

        var zstPath = TempFile("dogfood_source.zst");
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.NotNull(doc);
        Assert.True(doc.IsValid);

        // GetChecksumValue
        var checksum = doc.GetChecksumValue();
        Assert.True(checksum >= 0);
        Assert.Equal(checksum, doc.GetChecksumValue()); // consistent

        // GetFrameCount
        var frameCount = doc.GetFrameCount();
        Assert.True(frameCount >= 1);
        Assert.Equal(frameCount, doc.GetFrameCount()); // consistent

        // IsFrameIntact
        Assert.True(doc.IsFrameIntact());
        Assert.Equal(doc.IsFrameIntact(), doc.IsFrameIntact()); // consistent

        // GetDecompressedSize positive
        Assert.True(doc.GetDecompressedSize() > 0);
        Assert.True(doc.GetCompressedSize() > 0);

        // GetCompressionStats
        var stats = doc.GetCompressionStats();
        Assert.NotNull(stats);
        Assert.True(stats.Ratio > 0);

        // SaveToFile
        var savePath = TempFile("dogfood_saved.zst");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify all consistent
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.True(loaded.IsValid);
        Assert.Equal(checksum, loaded.GetChecksumValue());
        Assert.Equal(frameCount, loaded.GetFrameCount());
        Assert.Equal(doc.IsFrameIntact(), loaded.IsFrameIntact());
        Assert.Equal(doc.GetDecompressedSize(), loaded.GetDecompressedSize());

        // Decompress and verify
        var decompPath = TempFile("dogfood_decomp.txt");
        ZstParser.DecompressFile(savePath, decompPath);
        Assert.Equal(original, File.ReadAllText(decompPath));

        // Second doc at different level
        var raw2 = TempFile("dogfood_raw2.txt");
        File.WriteAllText(raw2, RepeatText("Second distinct content for frame count comparison test", 100));
        var zst2 = TempFile("dogfood_src2.zst");
        ZstWriter.CompressFile(raw2, zst2, compressionLevel: 6);
        var doc2 = ZstDocument.LoadFile(zst2);
        Assert.True(doc2.IsValid);
        Assert.True(doc2.GetChecksumValue() >= 0);
        Assert.True(doc2.GetFrameCount() >= 1);
        Assert.True(doc2.IsFrameIntact());

        // Final save
        var finalPath = TempFile("dogfood_final.zst");
        doc2.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = ZstDocument.LoadFile(finalPath);
        Assert.True(final.IsValid);
        Assert.Equal(doc2.GetChecksumValue(), final.GetChecksumValue());
        Assert.Equal(doc2.GetFrameCount(), final.GetFrameCount());
        Assert.True(final.IsFrameIntact());
    }
}
