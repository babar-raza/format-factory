// Tests for ZstDocument.GetBlockSize, GetBlockCount, GetBlockOffset deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R251

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R251: Tests for ZstDocument.GetBlockSize, GetBlockCount, GetBlockOffset deeper.
/// GetBlockSize(blockIndex): returns the compressed size of the block at the given index.
/// GetBlockCount(): returns the total number of blocks in the Zstandard frame.
/// GetBlockOffset(blockIndex): returns the byte offset of the block within the compressed file.
/// Covers: GetBlockCount no-throw; GetBlockCount positive; GetBlockCount consistent;
/// GetBlockSize no-throw; GetBlockSize positive; GetBlockSize consistent;
/// GetBlockSize save-load;
/// GetBlockOffset no-throw; GetBlockOffset non-negative; GetBlockOffset consistent;
/// GetBlockOffset increases with index; GetBlockOffset save-load;
/// dogfood CreateDoc→GetBlockCount→GetBlockSize→GetBlockOffset pipeline.
/// </summary>
public class ZstR251GetBlockSizeAndBlockCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR251GetBlockSizeAndBlockCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR251_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleZst()
    {
        var path = TempFile("sample.zst");
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < 30; i++)
            sb.Append($"RECORD:{i:D4}|data=payload_{i * 11}|tag=ALPHA\n");
        var compressed = ZstWriter.Compress(System.Text.Encoding.UTF8.GetBytes(sb.ToString()));
        File.WriteAllBytes(path, compressed);
        return path;
    }

    private string CreateLargerZst()
    {
        var path = TempFile("larger.zst");
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < 200; i++)
            sb.Append($"LINE:{i:D6}|content=data_block_{i}|ts=2024-01-{(i % 28 + 1):D2}\n");
        var compressed = ZstWriter.Compress(System.Text.Encoding.UTF8.GetBytes(sb.ToString()));
        File.WriteAllBytes(path, compressed);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetBlockCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetBlockCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockCount_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetBlockCount() >= 1);
    }

    [Fact]
    public void GetBlockCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetBlockCount(), doc.GetBlockCount());
    }

    [Fact]
    public void GetBlockCount_LargerFile_AtLeastOne()
    {
        var doc = ZstDocument.LoadFile(CreateLargerZst());
        Assert.True(doc.GetBlockCount() >= 1);
    }

    // -------------------------------------------------------------------------
    // GetBlockSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetBlockSize(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetBlockSize(0) > 0);
    }

    [Fact]
    public void GetBlockSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetBlockSize(0), doc.GetBlockSize(0));
    }

    [Fact]
    public void GetBlockSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetBlockSize(0);
        var path = TempFile("bs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockSize(0));
    }

    // -------------------------------------------------------------------------
    // GetBlockOffset
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockOffset_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetBlockOffset(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockOffset_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetBlockOffset(0) >= 0);
    }

    [Fact]
    public void GetBlockOffset_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetBlockOffset(0), doc.GetBlockOffset(0));
    }

    [Fact]
    public void GetBlockOffset_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetBlockOffset(0);
        var path = TempFile("bo_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockOffset(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetBlockCount_GetBlockSize_GetBlockOffset_Pipeline()
    {
        // Seismology — broadband seismogram data from IRIS/FDSN network (SAC-format compressed archive)
        var path = TempFile("seismogram_network.zst");
        var sb = new System.Text.StringBuilder();
        sb.Append("SAC_ARCHIVE FORMAT=MINISEED_EQUIVALENT VERSION=2.0 NETWORK=IC STATION=BJT\n");
        sb.Append("channel\tnpts\tdelta_seconds\tbegin_time_utc\tstla\tstlo\tstel_m\tevla\tevlo\tevdp_km\tmag\tphase\tazimuth\tgcarc\n");

        var rng = new Random(20250901);
        string[] channels = { "BHZ", "BHE", "BHN", "HHZ", "HHE", "HHN" };
        string[] phases = { "P", "S", "PP", "SS", "PcP", "ScS", "SKS", "PKIKP" };
        for (int i = 0; i < 180; i++)
        {
            var ch = channels[i % channels.Length];
            int npts = 8000 + rng.Next(8000);
            double delta = ch.StartsWith("B") ? 0.025 : 0.01;
            double stla = 40.0 + rng.NextDouble() * 10.0;
            double stlo = 110.0 + rng.NextDouble() * 15.0;
            double stel = 100 + rng.NextDouble() * 900;
            double evla = -30 + rng.NextDouble() * 80;
            double evlo = -100 + rng.NextDouble() * 200;
            double evdp = 5 + rng.NextDouble() * 690;
            double mag = 4.0 + rng.NextDouble() * 5.0;
            var phase = phases[rng.Next(phases.Length)];
            double az = rng.NextDouble() * 360;
            double gcarc = 5 + rng.NextDouble() * 150;
            sb.Append($"{ch}\t{npts}\t{delta:F4}\t2024-{(rng.Next(12) + 1):D2}-{(rng.Next(28) + 1):D2}T{rng.Next(24):D2}:{rng.Next(60):D2}:{rng.NextDouble() * 60:F3}Z\t{stla:F6}\t{stlo:F6}\t{stel:F1}\t{evla:F6}\t{evlo:F6}\t{evdp:F1}\t{mag:F2}\t{phase}\t{az:F2}\t{gcarc:F3}\n");
        }
        sb.Append("ARCHIVE_FOOTER: TOTAL_CHANNELS=180 NETWORK_CODE=IC SENSOR_TYPE=BROADBAND\n");

        var content = System.Text.Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(content);
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetBlockCount
        var blockCount = doc.GetBlockCount();
        Assert.True(blockCount >= 1);
        Assert.Equal(blockCount, doc.GetBlockCount()); // consistent

        // GetBlockSize
        var blockSize0 = doc.GetBlockSize(0);
        Assert.True(blockSize0 > 0);
        Assert.Equal(blockSize0, doc.GetBlockSize(0)); // consistent

        // GetBlockOffset
        var offset0 = doc.GetBlockOffset(0);
        Assert.True(offset0 >= 0);
        Assert.Equal(offset0, doc.GetBlockOffset(0)); // consistent

        // Multiple blocks: offsets increase
        if (blockCount > 1)
        {
            var offset1 = doc.GetBlockOffset(1);
            Assert.True(offset1 > offset0);
        }

        // Frame-level properties
        Assert.Equal(0xFD2FB528u, (uint)doc.GetMagicNumber());
        Assert.True(doc.FrameCount >= 1);
        Assert.Equal(0, doc.GetSkipFrameCount());
        Assert.True(doc.GetTotalFrameSize() >= doc.CompressedSize);
        Assert.True(doc.VerifyDecompressedIntegrity());

        // SearchForBytes
        var sacHeader = System.Text.Encoding.ASCII.GetBytes("SAC_ARCHIVE");
        Assert.True(doc.SearchForBytes(sacHeader) >= 0);
        var channelPattern = System.Text.Encoding.ASCII.GetBytes("BHZ");
        Assert.True(doc.SearchForBytes(channelPattern) >= 0);

        // SaveToFile
        var outPath = TempFile("seismogram_network_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(blockCount, loaded.GetBlockCount());
        Assert.Equal(blockSize0, loaded.GetBlockSize(0));
        Assert.Equal(offset0, loaded.GetBlockOffset(0));
        Assert.Equal(doc.CompressedSize, loaded.CompressedSize);
        Assert.True(loaded.VerifyDecompressedIntegrity());

        // CompressionRatio
        Assert.True(doc.CompressionRatio > 1.0);
    }
}
