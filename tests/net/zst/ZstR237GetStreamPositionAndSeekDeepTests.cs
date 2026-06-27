// Tests for ZstDocument.GetStreamPosition, SeekToBlock, GetCurrentBlockIndex deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R237

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R237: Tests for ZstDocument.GetStreamPosition, SeekToBlock, GetCurrentBlockIndex deeper.
/// GetStreamPosition(): returns the current byte offset within the compressed stream.
/// SeekToBlock(blockIndex): positions the stream to the start of the specified block.
/// GetCurrentBlockIndex(): returns the index of the currently active block.
/// Covers: GetStreamPosition no-throw; GetStreamPosition non-negative; GetStreamPosition consistent;
/// GetStreamPosition save-load;
/// SeekToBlock no-throw; SeekToBlock zero positions to start; SeekToBlock consistent;
/// SeekToBlock save-load;
/// GetCurrentBlockIndex no-throw; GetCurrentBlockIndex non-negative; GetCurrentBlockIndex consistent;
/// GetCurrentBlockIndex save-load; GetCurrentBlockIndex after SeekToBlock;
/// dogfood Compress→GetStreamPosition→SeekToBlock→GetCurrentBlockIndex→SaveToFile pipeline.
/// </summary>
public class ZstR237GetStreamPositionAndSeekDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR237GetStreamPositionAndSeekDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR237_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateMultiBlockZst()
    {
        // Large content to force multiple blocks
        var sb = new StringBuilder();
        for (int i = 0; i < 1000; i++)
            sb.AppendLine($"BLOCK_DATA_{i:D6}_ALPHA_BETA_GAMMA_DELTA_EPSILON_{(i * 17) % 1000:D3}_PADDING_CONTENT");
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(sb.ToString()));
        var path = TempFile("multiblock.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    private string CreateSmallZst()
    {
        var content = "SMALL_ZST_CONTENT_FOR_STREAM_POSITION_TESTING";
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("small.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetStreamPosition
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStreamPosition_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateMultiBlockZst());
        var ex = Record.Exception(() => doc.GetStreamPosition());
        Assert.Null(ex);
    }

    [Fact]
    public void GetStreamPosition_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateMultiBlockZst());
        Assert.True(doc.GetStreamPosition() >= 0);
    }

    [Fact]
    public void GetStreamPosition_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateMultiBlockZst());
        Assert.Equal(doc.GetStreamPosition(), doc.GetStreamPosition());
    }

    [Fact]
    public void GetStreamPosition_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateMultiBlockZst());
        var before = doc.GetStreamPosition();
        var path = TempFile("sp_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetStreamPosition());
    }

    // -------------------------------------------------------------------------
    // SeekToBlock
    // -------------------------------------------------------------------------

    [Fact]
    public void SeekToBlock_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateMultiBlockZst());
        var ex = Record.Exception(() => doc.SeekToBlock(0));
        Assert.Null(ex);
    }

    [Fact]
    public void SeekToBlock_Zero_PositionsToStart()
    {
        var doc = ZstDocument.LoadFile(CreateMultiBlockZst());
        doc.SeekToBlock(0);
        Assert.Equal(0, doc.GetStreamPosition());
    }

    [Fact]
    public void SeekToBlock_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateMultiBlockZst());
        doc.SeekToBlock(0);
        var pos1 = doc.GetStreamPosition();
        doc.SeekToBlock(0);
        var pos2 = doc.GetStreamPosition();
        Assert.Equal(pos1, pos2);
    }

    [Fact]
    public void SeekToBlock_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateMultiBlockZst());
        doc.SeekToBlock(0);
        var before = doc.GetCurrentBlockIndex();
        var path = TempFile("stb_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        loaded.SeekToBlock(0);
        Assert.Equal(before, loaded.GetCurrentBlockIndex());
    }

    // -------------------------------------------------------------------------
    // GetCurrentBlockIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCurrentBlockIndex_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateMultiBlockZst());
        var ex = Record.Exception(() => doc.GetCurrentBlockIndex());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCurrentBlockIndex_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateMultiBlockZst());
        Assert.True(doc.GetCurrentBlockIndex() >= 0);
    }

    [Fact]
    public void GetCurrentBlockIndex_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateMultiBlockZst());
        Assert.Equal(doc.GetCurrentBlockIndex(), doc.GetCurrentBlockIndex());
    }

    [Fact]
    public void GetCurrentBlockIndex_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateMultiBlockZst());
        var before = doc.GetCurrentBlockIndex();
        var path = TempFile("cbi_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCurrentBlockIndex());
    }

    [Fact]
    public void GetCurrentBlockIndex_AfterSeekToBlock()
    {
        var doc = ZstDocument.LoadFile(CreateMultiBlockZst());
        doc.SeekToBlock(0);
        Assert.Equal(0, doc.GetCurrentBlockIndex());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetStreamPosition_SeekToBlock_GetCurrentBlockIndex_SaveToFile_Pipeline()
    {
        // Scientific computing — numerical simulation checkpoint data stream
        var sb = new StringBuilder();
        sb.AppendLine("# Finite Element Analysis — Structural Simulation Checkpoint Log");
        sb.AppendLine("# Simulation: Offshore Wind Turbine Foundation Stress Analysis");
        sb.AppendLine("# Version: FEA-2026, Solver: OpenFOAM-v2312");
        for (int step = 0; step < 500; step++)
        {
            double time = step * 0.01;
            double stress = 125.4 + 42.3 * Math.Sin(time * 2 * Math.PI / 10.0);
            double displacement = 0.0024 + 0.0008 * Math.Cos(time * Math.PI / 5.0);
            double vonMises = stress * (1.0 + 0.1 * (step % 7));
            sb.AppendLine($"STEP={step:D6},T={time:F4}s,SX={stress:F4}MPa,SY={stress * 0.8:F4}MPa,SZ={stress * 0.6:F4}MPa,U={displacement:F6}m,VM={vonMises:F4}MPa,STATUS={(vonMises < 250 ? "SAFE" : "WARN")}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_fea.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetStreamPosition — initial position
        var initPos = doc.GetStreamPosition();
        Assert.True(initPos >= 0);
        Assert.Equal(initPos, doc.GetStreamPosition()); // consistent

        // GetCurrentBlockIndex — initial block
        var initBlock = doc.GetCurrentBlockIndex();
        Assert.True(initBlock >= 0);
        Assert.Equal(initBlock, doc.GetCurrentBlockIndex()); // consistent

        // SeekToBlock(0) — reset to beginning
        doc.SeekToBlock(0);
        Assert.Equal(0, doc.GetStreamPosition());
        Assert.Equal(0, doc.GetCurrentBlockIndex());

        // SeekToBlock(0) is idempotent
        doc.SeekToBlock(0);
        Assert.Equal(0, doc.GetStreamPosition());
        Assert.Equal(0, doc.GetCurrentBlockIndex());

        // SaveToFile
        var out1 = TempFile("dogfood_fea_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify stream state
        var loaded = ZstDocument.LoadFile(out1);
        Assert.True(loaded.GetStreamPosition() >= 0);
        Assert.True(loaded.GetCurrentBlockIndex() >= 0);

        // SeekToBlock on loaded
        loaded.SeekToBlock(0);
        Assert.Equal(0, loaded.GetStreamPosition());
        Assert.Equal(0, loaded.GetCurrentBlockIndex());

        // Decompression after seek
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        Assert.True(decompressed.Length > 0);
        var text = Encoding.UTF8.GetString(decompressed);
        Assert.Contains("FEA-2026", text);
        Assert.Contains("STEP=000000", text);

        // Larger content to ensure multiple blocks
        var bigSb = new StringBuilder();
        for (int i = 0; i < 2000; i++)
            bigSb.AppendLine($"NODE_{i:D8},{i * 0.001:F6},{i * 0.002:F6},{i * 0.003:F6},DISP={i * 0.000001:F9},STRESS={100.0 + i * 0.01:F4}");
        var bigData = ZstWriter.Compress(Encoding.UTF8.GetBytes(bigSb.ToString()));
        var bigPath = TempFile("dogfood_big.zst");
        File.WriteAllBytes(bigPath, bigData);
        var bigDoc = ZstDocument.LoadFile(bigPath);
        Assert.True(bigDoc.GetStreamPosition() >= 0);
        bigDoc.SeekToBlock(0);
        Assert.Equal(0, bigDoc.GetCurrentBlockIndex());
        Assert.True(bigDoc.GetBlockCount() >= 1);

        // Recompress and verify
        var out2 = TempFile("dogfood_fea_v2.zst");
        File.WriteAllBytes(out2, ZstWriter.Compress(decompressed));
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.True(loaded2.GetStreamPosition() >= 0);
        loaded2.SeekToBlock(0);
        Assert.Equal(0, loaded2.GetCurrentBlockIndex());
        var ex1 = Record.Exception(() => loaded2.GetStreamPosition());
        var ex2 = Record.Exception(() => loaded2.SeekToBlock(0));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
