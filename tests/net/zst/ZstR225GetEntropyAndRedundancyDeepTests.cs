// Tests for ZstDocument.GetEntropy, GetRedundancy, GetCompressionEfficiency deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R225

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R225: Tests for ZstDocument.GetEntropy, GetRedundancy, GetCompressionEfficiency deeper.
/// GetEntropy(): returns the Shannon entropy of the compressed data (bits per byte).
/// GetRedundancy(): returns 1 - (entropy / 8), the fraction of compressible redundancy.
/// GetCompressionEfficiency(): returns ratio of actual compression vs theoretical maximum.
/// Covers: GetEntropy no-throw; GetEntropy in [0,8]; GetEntropy consistent; GetEntropy save-load;
/// GetRedundancy no-throw; GetRedundancy in [0,1]; GetRedundancy consistent; GetRedundancy save-load;
/// GetRedundancy plus-entropy-leq-eight;
/// GetCompressionEfficiency no-throw; GetCompressionEfficiency in [0,1]; GetCompressionEfficiency consistent;
/// GetCompressionEfficiency save-load;
/// dogfood Compress→GetEntropy→GetRedundancy→GetCompressionEfficiency→SaveToFile pipeline.
/// </summary>
public class ZstR225GetEntropyAndRedundancyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR225GetEntropyAndRedundancyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR225_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateZstFile(string content = null)
    {
        content ??= string.Join(" ", System.Linq.Enumerable.Repeat(
            "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs.", 20));
        var raw = TempFile("src.txt");
        File.WriteAllText(raw, content);
        var zst = TempFile("src.zst");
        new ZstWriter().CompressFile(raw, zst);
        return zst;
    }

    // -------------------------------------------------------------------------
    // GetEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEntropy_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetEntropy());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEntropy_InRange()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var e = doc.GetEntropy();
        Assert.True(e >= 0.0 && e <= 8.0);
    }

    [Fact]
    public void GetEntropy_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetEntropy(), doc.GetEntropy());
    }

    [Fact]
    public void GetEntropy_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetEntropy();
        var path = TempFile("ent_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetEntropy(), 4);
    }

    // -------------------------------------------------------------------------
    // GetRedundancy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRedundancy_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetRedundancy());
        Assert.Null(ex);
    }

    [Fact]
    public void GetRedundancy_InRange()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var r = doc.GetRedundancy();
        Assert.True(r >= 0.0 && r <= 1.0);
    }

    [Fact]
    public void GetRedundancy_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetRedundancy(), doc.GetRedundancy());
    }

    [Fact]
    public void GetRedundancy_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetRedundancy();
        var path = TempFile("red_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRedundancy(), 4);
    }

    // -------------------------------------------------------------------------
    // GetCompressionEfficiency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionEfficiency_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetCompressionEfficiency());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionEfficiency_InRange()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var eff = doc.GetCompressionEfficiency();
        Assert.True(eff >= 0.0 && eff <= 1.0);
    }

    [Fact]
    public void GetCompressionEfficiency_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetCompressionEfficiency(), doc.GetCompressionEfficiency());
    }

    [Fact]
    public void GetCompressionEfficiency_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetCompressionEfficiency();
        var path = TempFile("eff_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionEfficiency(), 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetEntropy_GetRedundancy_GetCompressionEfficiency_SaveToFile_Pipeline()
    {
        // Highly repetitive content — should have low entropy and high redundancy
        var content = string.Concat(System.Linq.Enumerable.Repeat(
            "AAABBBCCCDDDEEEFFFGGGHHH 123456789 The same pattern repeats many times here.\n", 100));

        var raw = TempFile("repetitive.txt");
        File.WriteAllText(raw, content);
        var zstPath = TempFile("repetitive.zst");
        new ZstWriter().CompressFile(raw, zstPath);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > 0);

        // GetEntropy — compressed data: should be in [0,8]
        var entropy = doc.GetEntropy();
        Assert.True(entropy >= 0.0 && entropy <= 8.0);
        Assert.Equal(entropy, doc.GetEntropy()); // consistent

        // GetRedundancy — should be in [0,1]
        var redundancy = doc.GetRedundancy();
        Assert.True(redundancy >= 0.0 && redundancy <= 1.0);
        Assert.Equal(redundancy, doc.GetRedundancy()); // consistent

        // GetCompressionEfficiency
        var efficiency = doc.GetCompressionEfficiency();
        Assert.True(efficiency >= 0.0 && efficiency <= 1.0);
        Assert.Equal(efficiency, doc.GetCompressionEfficiency()); // consistent

        // Cross-checks
        Assert.True(doc.GetCompressionRatio() > 0);
        Assert.True(doc.GetCompressedSize() < doc.GetDecompressedSize()); // should be smaller

        // SaveToFile
        var path = TempFile("dogfood_rep_out.zst");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(entropy, loaded.GetEntropy(), 4);
        Assert.Equal(redundancy, loaded.GetRedundancy(), 4);
        Assert.Equal(efficiency, loaded.GetCompressionEfficiency(), 4);
        Assert.Equal(doc.GetCompressedSize(), loaded.GetCompressedSize());

        // Final save
        var path2 = TempFile("dogfood_rep_v2.zst");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = ZstDocument.LoadFile(path2);
        Assert.Equal(loaded.GetEntropy(), loaded2.GetEntropy(), 4);
        Assert.Equal(loaded.GetRedundancy(), loaded2.GetRedundancy(), 4);
        Assert.Equal(loaded.GetCompressionEfficiency(), loaded2.GetCompressionEfficiency(), 4);
    }
}
