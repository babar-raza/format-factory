// Tests for ZstDocument.GetBlockOffsetTable, GetRandomAccessOffset, GetBlockCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R247

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R247: Tests for ZstDocument.GetBlockOffsetTable, GetRandomAccessOffset, GetBlockCount deeper.
/// GetBlockOffsetTable(): returns a list of byte offsets for each block within the compressed frame.
/// GetRandomAccessOffset(position): returns the nearest block offset for random access at the given position.
/// GetBlockCount(): returns the number of compressed blocks in the frame.
/// Covers: GetBlockOffsetTable no-throw; GetBlockOffsetTable non-null; GetBlockOffsetTable consistent;
/// GetBlockOffsetTable count equals GetBlockCount;
/// GetRandomAccessOffset no-throw; GetRandomAccessOffset non-negative; GetRandomAccessOffset consistent;
/// GetRandomAccessOffset ≤ CompressedSize;
/// GetBlockCount no-throw; GetBlockCount positive; GetBlockCount consistent;
/// GetBlockCount save-load;
/// dogfood CreateDoc→GetBlockOffsetTable→GetRandomAccessOffset→GetBlockCount pipeline.
/// </summary>
public class ZstR247GetBlockOffsetTableAndRandomAccessDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR247GetBlockOffsetTableAndRandomAccessDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR247_" + Guid.NewGuid().ToString("N"));
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
        var content = System.Text.Encoding.UTF8.GetBytes(
            "city,population,area_km2\nLondon,9000000,1572\nManchester,553000,116\nBirmingham,1145000,267\nLeeds,793000,551\n");
        File.WriteAllBytes(path, ZstWriter.Compress(content));
        return path;
    }

    private string CreateLargerZst()
    {
        var path = TempFile("larger.zst");
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < 80; i++)
            sb.Append($"BLOCK_DATA:{i:D4}|sequence={i * 13 % 97}|payload={'X'.ToString().PadRight(50, 'X')}\n");
        File.WriteAllBytes(path, ZstWriter.Compress(System.Text.Encoding.UTF8.GetBytes(sb.ToString())));
        return path;
    }

    // -------------------------------------------------------------------------
    // GetBlockOffsetTable
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockOffsetTable_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetBlockOffsetTable());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockOffsetTable_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.NotNull(doc.GetBlockOffsetTable());
    }

    [Fact]
    public void GetBlockOffsetTable_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetBlockOffsetTable().Count, doc.GetBlockOffsetTable().Count);
    }

    [Fact]
    public void GetBlockOffsetTable_Count_Equals_BlockCount()
    {
        var doc = ZstDocument.LoadFile(CreateLargerZst());
        Assert.Equal(doc.GetBlockCount(), doc.GetBlockOffsetTable().Count);
    }

    // -------------------------------------------------------------------------
    // GetRandomAccessOffset
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRandomAccessOffset_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetRandomAccessOffset(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRandomAccessOffset_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetRandomAccessOffset(0) >= 0);
    }

    [Fact]
    public void GetRandomAccessOffset_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetRandomAccessOffset(0), doc.GetRandomAccessOffset(0));
    }

    [Fact]
    public void GetRandomAccessOffset_LessOrEqual_CompressedSize()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetRandomAccessOffset(0) <= doc.CompressedSize);
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
        Assert.True(doc.GetBlockCount() > 0);
    }

    [Fact]
    public void GetBlockCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetBlockCount(), doc.GetBlockCount());
    }

    [Fact]
    public void GetBlockCount_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetBlockCount();
        var path = TempFile("bc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetBlockOffsetTable_GetRandomAccessOffset_GetBlockCount_Pipeline()
    {
        // Scientific computing — compressed NetCDF-like ocean model output (SSH, temperature, salinity)
        var path = TempFile("ocean_model.zst");
        var sb = new System.Text.StringBuilder();
        sb.Append("NEMO_OCEAN_MODEL_OUTPUT FORMAT=ASCII GRID=ORCA025 TIMESTEP=3600\n");
        var rng = new Random(20250301);
        // 250 grid points with 4 variables
        for (int lat = 0; lat < 25; lat++)
        {
            for (int lon = 0; lon < 10; lon++)
            {
                double latDeg = -30 + lat * 2.5;
                double lonDeg = -20 + lon * 4.0;
                double ssh = (rng.NextDouble() - 0.5) * 0.8;    // sea surface height (m)
                double temp = 5 + rng.NextDouble() * 25;          // temperature (°C)
                double salinity = 33 + rng.NextDouble() * 5;      // salinity (PSU)
                double currU = (rng.NextDouble() - 0.5) * 0.5;   // zonal current (m/s)
                sb.Append($"LAT={latDeg:F2},LON={lonDeg:F2},SSH={ssh:F4},TEMP={temp:F2},SAL={salinity:F3},U={currU:F4}\n");
            }
        }
        sb.Append("END_OF_RECORD\n");
        var content = System.Text.Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(content);
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetBlockCount
        var blockCount = doc.GetBlockCount();
        Assert.True(blockCount > 0);
        Assert.Equal(blockCount, doc.GetBlockCount()); // consistent

        // GetBlockOffsetTable
        var offsets = doc.GetBlockOffsetTable();
        Assert.NotNull(offsets);
        Assert.Equal(blockCount, offsets.Count);
        Assert.Equal(offsets.Count, doc.GetBlockOffsetTable().Count); // consistent

        // GetRandomAccessOffset
        var offset0 = doc.GetRandomAccessOffset(0);
        Assert.True(offset0 >= 0);
        Assert.True(offset0 <= doc.CompressedSize);
        Assert.Equal(offset0, doc.GetRandomAccessOffset(0)); // consistent

        var offsetMid = doc.GetRandomAccessOffset(doc.DecompressedSize / 2);
        Assert.True(offsetMid >= 0);
        Assert.True(offsetMid <= doc.CompressedSize);

        // VerifyIntegrity
        Assert.True(doc.VerifyIntegrity());

        // GetMagicNumber
        Assert.Equal(0xFD2FB528u, (uint)doc.GetMagicNumber());

        // SaveToFile
        var outPath = TempFile("ocean_model_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(blockCount, loaded.GetBlockCount());
        Assert.Equal(offsets.Count, loaded.GetBlockOffsetTable().Count);
        Assert.Equal(offset0, loaded.GetRandomAccessOffset(0));
        Assert.Equal(doc.CompressedSize, loaded.CompressedSize);

        // Additional stats
        Assert.True(doc.CompressionRatio > 1.0);
        Assert.Equal(0, doc.GetDictionaryId());
    }
}
