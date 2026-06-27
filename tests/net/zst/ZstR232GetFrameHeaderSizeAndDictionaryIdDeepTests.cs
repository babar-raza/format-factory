// Tests for ZstDocument.GetFrameHeaderSize, GetDictionaryId, GetChecksumPresent deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R232

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R232: Tests for ZstDocument.GetFrameHeaderSize, GetDictionaryId, GetChecksumPresent deeper.
/// GetFrameHeaderSize(): returns the size in bytes of the Zstandard frame header.
/// GetDictionaryId(): returns the dictionary ID embedded in the frame (0 if none).
/// GetChecksumPresent(): returns whether the content checksum flag is set in the frame.
/// Covers: GetFrameHeaderSize no-throw; GetFrameHeaderSize positive; GetFrameHeaderSize consistent;
/// GetFrameHeaderSize save-load;
/// GetDictionaryId no-throw; GetDictionaryId non-negative; GetDictionaryId consistent;
/// GetDictionaryId zero for standard frame; GetDictionaryId save-load;
/// GetChecksumPresent no-throw; GetChecksumPresent consistent; GetChecksumPresent save-load;
/// GetChecksumPresent true for checksum frame;
/// dogfood Compress→GetFrameHeaderSize→GetDictionaryId→GetChecksumPresent→SaveToFile pipeline.
/// </summary>
public class ZstR232GetFrameHeaderSizeAndDictionaryIdDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR232GetFrameHeaderSizeAndDictionaryIdDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR232_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateStandardZst()
    {
        var content = "Standard Zstandard frame without dictionary.\n" +
                      string.Join(" ", Enumerable.Repeat("metadata telemetry monitoring infrastructure", 50));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("standard.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    private string CreateChecksumZst()
    {
        var content = string.Join("\n", Enumerable.Repeat(
            "CHECKSUM_TEST_DATA_BLOCK_ALPHA_BETA_GAMMA_DELTA_EPSILON", 100));
        var data = ZstWriter.CompressWithChecksum(Encoding.UTF8.GetBytes(content));
        var path = TempFile("checksum.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFrameHeaderSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameHeaderSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetFrameHeaderSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameHeaderSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.True(doc.GetFrameHeaderSize() > 0);
    }

    [Fact]
    public void GetFrameHeaderSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(doc.GetFrameHeaderSize(), doc.GetFrameHeaderSize());
    }

    [Fact]
    public void GetFrameHeaderSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var before = doc.GetFrameHeaderSize();
        var path = TempFile("fhs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrameHeaderSize());
    }

    // -------------------------------------------------------------------------
    // GetDictionaryId
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDictionaryId_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetDictionaryId());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDictionaryId_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.True(doc.GetDictionaryId() >= 0);
    }

    [Fact]
    public void GetDictionaryId_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(doc.GetDictionaryId(), doc.GetDictionaryId());
    }

    [Fact]
    public void GetDictionaryId_Zero_ForStandardFrame()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(0, doc.GetDictionaryId());
    }

    [Fact]
    public void GetDictionaryId_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var before = doc.GetDictionaryId();
        var path = TempFile("did_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDictionaryId());
    }

    // -------------------------------------------------------------------------
    // GetChecksumPresent
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChecksumPresent_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetChecksumPresent());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChecksumPresent_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(doc.GetChecksumPresent(), doc.GetChecksumPresent());
    }

    [Fact]
    public void GetChecksumPresent_True_ForChecksumFrame()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        Assert.True(doc.GetChecksumPresent());
    }

    [Fact]
    public void GetChecksumPresent_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        var before = doc.GetChecksumPresent();
        var path = TempFile("chk_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetChecksumPresent());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFrameHeaderSize_GetDictionaryId_GetChecksumPresent_SaveToFile_Pipeline()
    {
        // IoT telemetry stream — smart city sensor aggregation log
        var sb = new StringBuilder();
        sb.AppendLine("timestamp,sensor_type,location,value,unit,quality_score,alert");
        string[] types = { "temperature", "humidity", "pressure", "co2", "noise", "particulate" };
        string[] locations = { "downtown", "suburbs", "industrial", "port", "airport", "residential" };
        var rng = new Random(12345);
        for (int i = 0; i < 300; i++)
        {
            double val = types[i % 6] switch
            {
                "temperature" => 18.0 + rng.NextDouble() * 15.0,
                "humidity"    => 40.0 + rng.NextDouble() * 40.0,
                "pressure"    => 1010.0 + rng.NextDouble() * 10.0,
                "co2"         => 400.0 + rng.NextDouble() * 200.0,
                "noise"       => 50.0 + rng.NextDouble() * 40.0,
                _             => rng.NextDouble() * 50.0
            };
            sb.AppendLine($"2026-06-26T{i / 60:D2}:{i % 60:D2}:00Z,{types[i % 6]},{locations[i % 6]},{val:F2},{(i % 6 < 3 ? "celsius" : "ppm")},{0.85 + rng.NextDouble() * 0.15:F2},{(val > 200 ? "true" : "false")}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_iot.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetFrameHeaderSize
        var headerSize = doc.GetFrameHeaderSize();
        Assert.True(headerSize > 0);
        Assert.Equal(headerSize, doc.GetFrameHeaderSize()); // consistent

        // GetDictionaryId — standard frame has no dictionary
        var dictId = doc.GetDictionaryId();
        Assert.True(dictId >= 0);
        Assert.Equal(0, dictId); // no dictionary used
        Assert.Equal(dictId, doc.GetDictionaryId()); // consistent

        // GetChecksumPresent
        var hasChecksum = doc.GetChecksumPresent();
        Assert.Equal(hasChecksum, doc.GetChecksumPresent()); // consistent

        // SaveToFile
        var out1 = TempFile("dogfood_iot_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify frame metadata preserved
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(headerSize, loaded.GetFrameHeaderSize());
        Assert.Equal(dictId, loaded.GetDictionaryId());
        Assert.Equal(hasChecksum, loaded.GetChecksumPresent());

        // Decompression round-trip
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        Assert.True(decompressed.Length > 0);

        // Checksum frame comparison
        var chkDoc = ZstDocument.LoadFile(CreateChecksumZst());
        Assert.True(chkDoc.GetChecksumPresent()); // has checksum
        Assert.True(chkDoc.GetFrameHeaderSize() > 0);
        Assert.Equal(0, chkDoc.GetDictionaryId()); // still no dictionary

        // Recompress decompressed data
        var out2 = TempFile("dogfood_iot_v2.zst");
        var recompressed = ZstWriter.Compress(decompressed);
        File.WriteAllBytes(out2, recompressed);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.True(loaded2.GetFrameHeaderSize() > 0);
        Assert.Equal(0, loaded2.GetDictionaryId());
        var ex1 = Record.Exception(() => loaded2.GetChecksumPresent());
        Assert.Null(ex1);
    }
}
