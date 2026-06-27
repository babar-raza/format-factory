// Tests for ZstDocument.GetCompressedBlockCount, GetFrameMetadata, GetBlockSize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R241

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R241: Tests for ZstDocument.GetCompressedBlockCount, GetFrameMetadata, GetBlockSize deeper.
/// GetCompressedBlockCount(): returns the number of compressed blocks in the Zstandard frame.
/// GetFrameMetadata(): returns a string describing the frame-level metadata fields.
/// GetBlockSize(blockIndex): returns the byte size of the compressed block at the given index.
/// Covers: GetCompressedBlockCount no-throw; GetCompressedBlockCount non-negative;
/// GetCompressedBlockCount consistent; GetCompressedBlockCount save-load;
/// GetFrameMetadata no-throw; GetFrameMetadata non-null; GetFrameMetadata consistent;
/// GetBlockSize no-throw; GetBlockSize non-negative; GetBlockSize consistent;
/// GetBlockSize save-load;
/// dogfood Compress→GetCompressedBlockCount→GetFrameMetadata→GetBlockSize→SaveToFile pipeline.
/// </summary>
public class ZstR241GetCompressedBlocksAndFrameMetadataDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR241GetCompressedBlocksAndFrameMetadataDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR241_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateBlockMetaZst()
    {
        var content = string.Join("\n", System.Linq.Enumerable.Repeat(
            "BLOCK_META_FRAME_ALPHA_BETA_GAMMA_DELTA_EPSILON_ZETA_ETA_THETA_IOTA_KAPPA_LAMBDA", 120));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("blockmeta.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetCompressedBlockCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressedBlockCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateBlockMetaZst());
        var ex = Record.Exception(() => doc.GetCompressedBlockCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressedBlockCount_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateBlockMetaZst());
        Assert.True(doc.GetCompressedBlockCount() >= 0);
    }

    [Fact]
    public void GetCompressedBlockCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateBlockMetaZst());
        Assert.Equal(doc.GetCompressedBlockCount(), doc.GetCompressedBlockCount());
    }

    [Fact]
    public void GetCompressedBlockCount_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateBlockMetaZst());
        var before = doc.GetCompressedBlockCount();
        var path = TempFile("bc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressedBlockCount());
    }

    // -------------------------------------------------------------------------
    // GetFrameMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameMetadata_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateBlockMetaZst());
        var ex = Record.Exception(() => doc.GetFrameMetadata());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameMetadata_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateBlockMetaZst());
        Assert.NotNull(doc.GetFrameMetadata());
    }

    [Fact]
    public void GetFrameMetadata_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateBlockMetaZst());
        Assert.Equal(doc.GetFrameMetadata(), doc.GetFrameMetadata());
    }

    // -------------------------------------------------------------------------
    // GetBlockSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateBlockMetaZst());
        var ex = Record.Exception(() => doc.GetBlockSize(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockSize_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateBlockMetaZst());
        Assert.True(doc.GetBlockSize(0) >= 0);
    }

    [Fact]
    public void GetBlockSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateBlockMetaZst());
        Assert.Equal(doc.GetBlockSize(0), doc.GetBlockSize(0));
    }

    [Fact]
    public void GetBlockSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateBlockMetaZst());
        var before = doc.GetBlockSize(0);
        var path = TempFile("bs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockSize(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCompressedBlockCount_GetFrameMetadata_GetBlockSize_SaveToFile_Pipeline()
    {
        // Telecommunications — LTE/5G network event log compression and metadata inspection
        var sb = new StringBuilder();
        sb.AppendLine("timestamp,cell_id,imsi_suffix,event_type,rsrp_dbm,sinr_db,throughput_mbps,handover_target,drop_flag");
        string[] events = { "RRC_SETUP", "ATTACH_REQUEST", "HANDOVER_CMD", "MEASUREMENT_REPORT", "DETACH", "PAGING", "BEARER_SETUP", "BEARER_RELEASE" };
        string[] cells = { "eNB_001_C1", "eNB_001_C2", "eNB_002_C1", "eNB_002_C3", "eNB_003_C1", "eNB_003_C2" };
        var rng = new Random(20240601);
        for (int i = 0; i < 500; i++)
        {
            int ts = 1717200000 + i * 60;
            var cell = cells[i % 6];
            var evt = events[i % 8];
            double rsrp = -130 + rng.NextDouble() * 50.0;
            double sinr = -5 + rng.NextDouble() * 30.0;
            double tput = rng.NextDouble() * 100.0;
            var target = (evt == "HANDOVER_CMD") ? cells[(i + 1) % 6] : "";
            int drop = (rng.NextDouble() < 0.02) ? 1 : 0;
            sb.AppendLine($"{ts},{cell},{(1000000 + i):D10},{evt},{rsrp:F1},{sinr:F1},{tput:F1},{target},{drop}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_lte_events.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetCompressedBlockCount
        var blockCount = doc.GetCompressedBlockCount();
        Assert.True(blockCount >= 0);
        Assert.Equal(blockCount, doc.GetCompressedBlockCount()); // consistent

        // GetFrameMetadata
        var meta = doc.GetFrameMetadata();
        Assert.NotNull(meta);
        Assert.Equal(meta, doc.GetFrameMetadata()); // consistent

        // GetBlockSize
        var blockSize = doc.GetBlockSize(0);
        Assert.True(blockSize >= 0);
        Assert.Equal(blockSize, doc.GetBlockSize(0)); // consistent

        // SaveToFile
        var out1 = TempFile("dogfood_lte_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));

        // LoadFile — verify block metadata preserved
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(blockCount, loaded.GetCompressedBlockCount());
        Assert.NotNull(loaded.GetFrameMetadata());
        Assert.Equal(blockSize, loaded.GetBlockSize(0));

        // Decompression round-trip
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        var text = Encoding.UTF8.GetString(decompressed);
        Assert.Contains("RRC_SETUP", text);
        Assert.Contains("HANDOVER_CMD", text);
        Assert.Contains("eNB_001_C1", text);

        // ValidateChecksum
        Assert.True(doc.ValidateChecksum());

        // Second compression
        var recompressed = ZstWriter.Compress(decompressed);
        var out2 = TempFile("dogfood_lte_v2.zst");
        File.WriteAllBytes(out2, recompressed);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.True(loaded2.GetCompressedBlockCount() >= 0);
        Assert.NotNull(loaded2.GetFrameMetadata());
        Assert.Equal(0xFD2FB528u, (uint)loaded2.GetMagicNumber());
        var ex1 = Record.Exception(() => loaded2.GetBlockSize(0));
        Assert.Null(ex1);
    }
}
