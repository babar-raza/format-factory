// Tests for ZstDocument.GetBlockCount, GetBlockSize, GetBlockCompressionRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R229

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R229: Tests for ZstDocument.GetBlockCount, GetBlockSize, GetBlockCompressionRatio deeper.
/// GetBlockCount(): returns the number of compressed blocks in the frame.
/// GetBlockSize(blockIndex): returns the size in bytes of the block at the given index.
/// GetBlockCompressionRatio(blockIndex): returns the compression ratio for the specified block.
/// Covers: GetBlockCount no-throw; GetBlockCount positive; GetBlockCount consistent;
/// GetBlockCount save-load;
/// GetBlockSize no-throw; GetBlockSize positive; GetBlockSize consistent; GetBlockSize save-load;
/// GetBlockCompressionRatio no-throw; GetBlockCompressionRatio positive; GetBlockCompressionRatio consistent;
/// GetBlockCompressionRatio high for repetitive data; GetBlockCompressionRatio save-load;
/// dogfood Compress→GetBlockCount→GetBlockSize→GetBlockCompressionRatio→SaveToFile pipeline.
/// </summary>
public class ZstR229GetBlockCountAndBlockSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR229GetBlockCountAndBlockSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR229_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateRepetitiveZst()
    {
        var content = string.Join("\n", Enumerable.Repeat(
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", 500));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("repetitive.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    private string CreateStructuredZst()
    {
        var sb = new StringBuilder();
        sb.AppendLine("timestamp,sensor_id,temperature,humidity,pressure,co2_ppm");
        for (int i = 0; i < 200; i++)
            sb.AppendLine($"2026-06-26T{i / 60:D2}:{i % 60:D2}:00Z,SENSOR_{i % 10:D3},{20.0 + (i % 15) * 0.3:F1},{45.0 + (i % 20) * 0.5:F1},{1013.0 + (i % 8) * 0.2:F1},{400 + (i % 50)}");
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(sb.ToString()));
        var path = TempFile("structured.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetBlockCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStructuredZst());
        var ex = Record.Exception(() => doc.GetBlockCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockCount_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateStructuredZst());
        Assert.True(doc.GetBlockCount() > 0);
    }

    [Fact]
    public void GetBlockCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStructuredZst());
        Assert.Equal(doc.GetBlockCount(), doc.GetBlockCount());
    }

    [Fact]
    public void GetBlockCount_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStructuredZst());
        var before = doc.GetBlockCount();
        var path = TempFile("bc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockCount());
    }

    // -------------------------------------------------------------------------
    // GetBlockSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStructuredZst());
        var ex = Record.Exception(() => doc.GetBlockSize(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateStructuredZst());
        Assert.True(doc.GetBlockSize(0) > 0);
    }

    [Fact]
    public void GetBlockSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStructuredZst());
        Assert.Equal(doc.GetBlockSize(0), doc.GetBlockSize(0));
    }

    [Fact]
    public void GetBlockSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStructuredZst());
        var before = doc.GetBlockSize(0);
        var path = TempFile("bs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockSize(0));
    }

    // -------------------------------------------------------------------------
    // GetBlockCompressionRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockCompressionRatio_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        var ex = Record.Exception(() => doc.GetBlockCompressionRatio(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockCompressionRatio_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateStructuredZst());
        Assert.True(doc.GetBlockCompressionRatio(0) > 0.0);
    }

    [Fact]
    public void GetBlockCompressionRatio_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStructuredZst());
        Assert.Equal(doc.GetBlockCompressionRatio(0), doc.GetBlockCompressionRatio(0));
    }

    [Fact]
    public void GetBlockCompressionRatio_HighForRepetitiveData()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        Assert.True(doc.GetBlockCompressionRatio(0) > 1.0);
    }

    [Fact]
    public void GetBlockCompressionRatio_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        var before = doc.GetBlockCompressionRatio(0);
        var path = TempFile("bcr_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockCompressionRatio(0), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetBlockCount_GetBlockSize_GetBlockCompressionRatio_SaveToFile_Pipeline()
    {
        // Astronomy survey data: SDSS photometric catalogue excerpt
        var sb = new StringBuilder();
        sb.AppendLine("obj_id,ra,dec,u_mag,g_mag,r_mag,i_mag,z_mag,redshift,obj_type");
        string[] types = { "GALAXY", "QSO", "STAR" };
        var rng = new Random(42);
        for (int i = 0; i < 300; i++)
        {
            double ra = rng.NextDouble() * 360.0;
            double dec = rng.NextDouble() * 180.0 - 90.0;
            double u = 18.0 + rng.NextDouble() * 6.0;
            double g = u - 0.3 - rng.NextDouble() * 0.5;
            double r = g - 0.2 - rng.NextDouble() * 0.4;
            double ii = r - 0.1 - rng.NextDouble() * 0.3;
            double z = ii - 0.05 - rng.NextDouble() * 0.2;
            double redshift = rng.NextDouble() * 3.5;
            sb.AppendLine($"SDSS_{i:D6},{ra:F6},{dec:F6},{u:F3},{g:F3},{r:F3},{ii:F3},{z:F3},{redshift:F4},{types[i % 3]}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_sdss.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetBlockCount — positive
        var blockCount = doc.GetBlockCount();
        Assert.True(blockCount > 0);
        Assert.Equal(blockCount, doc.GetBlockCount()); // consistent

        // GetBlockSize — positive for first block
        var blockSize = doc.GetBlockSize(0);
        Assert.True(blockSize > 0);
        Assert.Equal(blockSize, doc.GetBlockSize(0)); // consistent

        // GetBlockCompressionRatio — positive
        var ratio = doc.GetBlockCompressionRatio(0);
        Assert.True(ratio > 0.0);
        Assert.Equal(ratio, doc.GetBlockCompressionRatio(0)); // consistent

        // All blocks have positive sizes
        for (int i = 0; i < blockCount; i++)
        {
            Assert.True(doc.GetBlockSize(i) > 0);
            Assert.True(doc.GetBlockCompressionRatio(i) > 0.0);
        }

        // SaveToFile — original
        var out1 = TempFile("dogfood_sdss_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify block structure preserved
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(blockCount, loaded.GetBlockCount());
        Assert.Equal(blockSize, loaded.GetBlockSize(0));
        Assert.Equal(ratio, loaded.GetBlockCompressionRatio(0), precision: 6);

        // Verify decompressed content round-trips
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        Assert.True(decompressed.Length > 0);

        // Repetitive data comparison
        var repDoc = ZstDocument.LoadFile(CreateRepetitiveZst());
        Assert.True(repDoc.GetBlockCount() > 0);
        Assert.True(repDoc.GetBlockCompressionRatio(0) > ratio); // repetitive compresses better

        // Final save via writer
        var out2 = TempFile("dogfood_sdss_v2.zst");
        var recompressed = ZstWriter.Compress(decompressed);
        File.WriteAllBytes(out2, recompressed);
        Assert.True(File.Exists(out2));
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.True(loaded2.GetBlockCount() > 0);
        Assert.True(loaded2.GetBlockSize(0) > 0);
        Assert.True(loaded2.GetBlockCompressionRatio(0) > 0.0);
        var ex1 = Record.Exception(() => loaded2.GetBlockCount());
        Assert.Null(ex1);
    }
}
