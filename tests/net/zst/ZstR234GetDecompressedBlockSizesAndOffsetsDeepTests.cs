// Tests for ZstDocument.GetDecompressedBlockSizes, GetBlockOffsets, GetTotalBlocksSize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R234

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R234: Tests for ZstDocument.GetDecompressedBlockSizes, GetBlockOffsets, GetTotalBlocksSize deeper.
/// GetDecompressedBlockSizes(): returns an array of decompressed sizes for each block.
/// GetBlockOffsets(): returns an array of byte offsets for each block within the frame.
/// GetTotalBlocksSize(): returns the total compressed size of all blocks combined.
/// Covers: GetDecompressedBlockSizes no-throw; GetDecompressedBlockSizes non-null; GetDecompressedBlockSizes count matches block count;
/// GetDecompressedBlockSizes consistent; GetDecompressedBlockSizes save-load;
/// GetBlockOffsets no-throw; GetBlockOffsets non-null; GetBlockOffsets count matches block count;
/// GetBlockOffsets consistent; GetBlockOffsets first is zero or positive; GetBlockOffsets save-load;
/// GetTotalBlocksSize no-throw; GetTotalBlocksSize positive; GetTotalBlocksSize consistent;
/// GetTotalBlocksSize leq compressed size; GetTotalBlocksSize save-load;
/// dogfood Compress→GetDecompressedBlockSizes→GetBlockOffsets→GetTotalBlocksSize→SaveToFile pipeline.
/// </summary>
public class ZstR234GetDecompressedBlockSizesAndOffsetsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR234GetDecompressedBlockSizesAndOffsetsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR234_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateLargeZst()
    {
        var sb = new StringBuilder();
        sb.AppendLine("record_id,timestamp,source,event_type,payload,checksum");
        for (int i = 0; i < 400; i++)
            sb.AppendLine($"REC{i:D6},2026-06-26T{i / 3600:D2}:{(i % 3600) / 60:D2}:{i % 60:D2}Z,srv{i % 8:D2},AUDIT_LOG,payload_{i % 50}_{i * 17 % 97},{i * 1234567 % 999983}");
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(sb.ToString()));
        var path = TempFile("large.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    private string CreateSmallZst()
    {
        var content = "Small test payload for block offset testing.\nLine two.\nLine three.";
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("small.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetDecompressedBlockSizes
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDecompressedBlockSizes_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var ex = Record.Exception(() => doc.GetDecompressedBlockSizes());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDecompressedBlockSizes_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.NotNull(doc.GetDecompressedBlockSizes());
    }

    [Fact]
    public void GetDecompressedBlockSizes_CountMatchesBlockCount()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.Equal(doc.GetBlockCount(), doc.GetDecompressedBlockSizes().Length);
    }

    [Fact]
    public void GetDecompressedBlockSizes_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var s1 = doc.GetDecompressedBlockSizes();
        var s2 = doc.GetDecompressedBlockSizes();
        Assert.Equal(s1.Length, s2.Length);
    }

    [Fact]
    public void GetDecompressedBlockSizes_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var before = doc.GetDecompressedBlockSizes().Length;
        var path = TempFile("dbs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDecompressedBlockSizes().Length);
    }

    // -------------------------------------------------------------------------
    // GetBlockOffsets
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockOffsets_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var ex = Record.Exception(() => doc.GetBlockOffsets());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockOffsets_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.NotNull(doc.GetBlockOffsets());
    }

    [Fact]
    public void GetBlockOffsets_CountMatchesBlockCount()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.Equal(doc.GetBlockCount(), doc.GetBlockOffsets().Length);
    }

    [Fact]
    public void GetBlockOffsets_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var o1 = doc.GetBlockOffsets();
        var o2 = doc.GetBlockOffsets();
        Assert.Equal(o1.Length, o2.Length);
        if (o1.Length > 0) Assert.Equal(o1[0], o2[0]);
    }

    [Fact]
    public void GetBlockOffsets_FirstOffset_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var offsets = doc.GetBlockOffsets();
        if (offsets.Length > 0)
            Assert.True(offsets[0] >= 0);
    }

    [Fact]
    public void GetBlockOffsets_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var before = doc.GetBlockOffsets().Length;
        var path = TempFile("bo_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockOffsets().Length);
    }

    // -------------------------------------------------------------------------
    // GetTotalBlocksSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTotalBlocksSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var ex = Record.Exception(() => doc.GetTotalBlocksSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTotalBlocksSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.True(doc.GetTotalBlocksSize() > 0);
    }

    [Fact]
    public void GetTotalBlocksSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.Equal(doc.GetTotalBlocksSize(), doc.GetTotalBlocksSize());
    }

    [Fact]
    public void GetTotalBlocksSize_LeqCompressedSize()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.True(doc.GetTotalBlocksSize() <= doc.CompressedSize);
    }

    [Fact]
    public void GetTotalBlocksSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var before = doc.GetTotalBlocksSize();
        var path = TempFile("tbs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTotalBlocksSize());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDecompressedBlockSizes_GetBlockOffsets_GetTotalBlocksSize_SaveToFile_Pipeline()
    {
        // Machine learning training log — experiment metrics over 350 epochs
        var sb = new StringBuilder();
        sb.AppendLine("epoch,train_loss,val_loss,train_acc,val_acc,lr,batch_size,grad_norm,elapsed_s");
        var rng = new Random(2026);
        double trainLoss = 2.5, valLoss = 2.6, trainAcc = 0.15, valAcc = 0.14;
        for (int i = 1; i <= 350; i++)
        {
            trainLoss = Math.Max(0.01, trainLoss * (0.985 + rng.NextDouble() * 0.01));
            valLoss = Math.Max(0.02, valLoss * (0.987 + rng.NextDouble() * 0.01));
            trainAcc = Math.Min(0.998, trainAcc + 0.002 + rng.NextDouble() * 0.001);
            valAcc = Math.Min(0.995, valAcc + 0.0018 + rng.NextDouble() * 0.001);
            double lr = 0.001 * Math.Pow(0.98, i / 10.0);
            sb.AppendLine($"{i},{trainLoss:F6},{valLoss:F6},{trainAcc:F6},{valAcc:F6},{lr:F8},128,{1.5 + rng.NextDouble() * 0.5:F4},{i * 2.4:F1}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_training.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetDecompressedBlockSizes
        var blockSizes = doc.GetDecompressedBlockSizes();
        Assert.NotNull(blockSizes);
        Assert.True(blockSizes.Length > 0);
        Assert.Equal(doc.GetBlockCount(), blockSizes.Length);
        Assert.Equal(blockSizes.Length, doc.GetDecompressedBlockSizes().Length); // consistent

        // GetBlockOffsets
        var offsets = doc.GetBlockOffsets();
        Assert.NotNull(offsets);
        Assert.Equal(doc.GetBlockCount(), offsets.Length);
        if (offsets.Length > 0) Assert.True(offsets[0] >= 0);
        Assert.Equal(offsets.Length, doc.GetBlockOffsets().Length); // consistent

        // GetTotalBlocksSize
        var totalSize = doc.GetTotalBlocksSize();
        Assert.True(totalSize > 0);
        Assert.True(totalSize <= doc.CompressedSize);
        Assert.Equal(totalSize, doc.GetTotalBlocksSize()); // consistent

        // SaveToFile
        var out1 = TempFile("dogfood_training_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(blockSizes.Length, loaded.GetDecompressedBlockSizes().Length);
        Assert.Equal(offsets.Length, loaded.GetBlockOffsets().Length);
        Assert.Equal(totalSize, loaded.GetTotalBlocksSize());

        // Decompression round-trip
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        Assert.True(decompressed.Length > 0);

        // Small file comparison
        var smallDoc = ZstDocument.LoadFile(CreateSmallZst());
        Assert.NotNull(smallDoc.GetDecompressedBlockSizes());
        Assert.NotNull(smallDoc.GetBlockOffsets());
        Assert.True(smallDoc.GetTotalBlocksSize() > 0);

        // Final recompress
        var out2 = TempFile("dogfood_training_v2.zst");
        File.WriteAllBytes(out2, ZstWriter.Compress(decompressed));
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.NotNull(loaded2.GetDecompressedBlockSizes());
        Assert.True(loaded2.GetTotalBlocksSize() > 0);
        var ex1 = Record.Exception(() => loaded2.GetBlockOffsets());
        Assert.Null(ex1);
    }
}
