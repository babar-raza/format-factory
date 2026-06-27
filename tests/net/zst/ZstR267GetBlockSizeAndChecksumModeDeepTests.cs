// Tests for ZstDocument.GetBlockSize, GetChecksumMode deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R267

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R267: Tests for ZstDocument.GetBlockSize, GetChecksumMode deeper.
/// GetBlockSize(): returns the block size used in compression (in bytes), or 0 if not applicable.
/// GetChecksumMode(): returns the checksum mode string (e.g. "none", "xxhash", "crc32") or "none".
/// Covers: GetBlockSize no-throw; GetBlockSize non-negative; GetBlockSize consistent;
/// GetBlockSize save-load; GetChecksumMode no-throw; GetChecksumMode non-null;
/// GetChecksumMode consistent; GetChecksumMode save-load;
/// dogfood CreateDoc→GetBlockSize→GetChecksumMode→SaveToFile pipeline.
/// </summary>
public class ZstR267GetBlockSizeAndChecksumModeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR267GetBlockSizeAndChecksumModeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR267_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateZst(string name, string content)
    {
        var path = TempFile(name);
        var bytes = Encoding.UTF8.GetBytes(content);
        using var outStream = new FileStream(path, FileMode.Create);
        using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
        zlib.Write(bytes, 0, bytes.Length);
        return path;
    }

    private string CreateLargeZst()
    {
        var sb = new StringBuilder();
        for (int i = 0; i < 300; i++)
            sb.AppendLine($"Record {i}: value={i * 1.23:F4} status={(i % 3 == 0 ? "active" : "inactive")} tag=block_{i / 10}");
        return CreateZst("large.zst", sb.ToString());
    }

    private string CreateSmallZst() => CreateZst("small.zst",
        "Small payload for block size and checksum mode tests. " + string.Concat(Enumerable.Repeat("filler ", 30)));

    // -------------------------------------------------------------------------
    // GetBlockSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var ex = Record.Exception(() => doc.GetBlockSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockSize_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.True(doc.GetBlockSize() >= 0);
    }

    [Fact]
    public void GetBlockSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.Equal(doc.GetBlockSize(), doc.GetBlockSize());
    }

    [Fact]
    public void GetBlockSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var before = doc.GetBlockSize();
        var path = TempFile("bs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockSize());
    }

    // -------------------------------------------------------------------------
    // GetChecksumMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChecksumMode_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSmallZst());
        var ex = Record.Exception(() => doc.GetChecksumMode());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChecksumMode_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateSmallZst());
        Assert.NotNull(doc.GetChecksumMode());
    }

    [Fact]
    public void GetChecksumMode_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSmallZst());
        Assert.Equal(doc.GetChecksumMode(), doc.GetChecksumMode());
    }

    [Fact]
    public void GetChecksumMode_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var before = doc.GetChecksumMode();
        var path = TempFile("cm_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetChecksumMode());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetBlockSize_GetChecksumMode_SaveToFile_Pipeline()
    {
        // Science — STFC: ISIS Neutron and Muon Source Data Archive
        // Compressed raw neutron scattering detector event data
        // Block size and checksum validation for long-term data integrity assurance

        // File 1: Small detector calibration run
        var path1 = TempFile("isis_calibration_run_001.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("ISIS Neutron Source — Detector Calibration Run");
            content.AppendLine("Instrument: WISH (Wide-angle In-Situ and Texture diffractometer)");
            content.AppendLine("Run number: CAL-2024-001");
            content.AppendLine("Date: 2024-10-15");
            content.AppendLine("Beam power: 160 kW");
            content.AppendLine("Sample: Vanadium rod (reference standard)");
            for (int i = 0; i < 80; i++)
                content.AppendLine($"Detector {i:D3}: counts={1200 + i * 3} efficiency={0.85 + i * 0.001:F4} dead_time_us={2.1 + i * 0.01:F3}");
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path1, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
            zlib.Write(bytes, 0, bytes.Length);
        }

        // File 2: Large science run (muon spectroscopy)
        var path2 = TempFile("isis_musr_run_2024_045.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("MuSR Spectrometer — Science Run");
            content.AppendLine("Experiment: RB2410001 — Quantum Spin Liquid in Frustrated Magnets");
            content.AppendLine("Principal Investigator: Dr A.K. Sinha, University of Edinburgh");
            content.AppendLine("Temperature: 1.5 K");
            content.AppendLine("Magnetic field: 0.0 mT (zero-field)");
            for (int i = 0; i < 200; i++)
            {
                double time_us = i * 0.016; // 16 ns time bins
                int positrons = (int)(8000 * Math.Exp(-time_us / 2.197) * (1 + 0.25 * Math.Cos(2 * Math.PI * 0.5 * time_us)));
                content.AppendLine($"Bin {i:D4}: t_us={time_us:F4} N_positrons={positrons} asymmetry={0.25 * Math.Cos(2 * Math.PI * 0.5 * time_us):F6}");
            }
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path2, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
            zlib.Write(bytes, 0, bytes.Length);
        }

        // File 3: Archive manifest (small metadata file)
        var path3 = TempFile("isis_archive_manifest_2024.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("{");
            content.AppendLine("  \"archive\": \"ISIS_2024_Q4\",");
            content.AppendLine("  \"instrument\": \"WISH\",");
            content.AppendLine("  \"total_runs\": 4821,");
            content.AppendLine("  \"total_bytes\": 2847291648,");
            content.AppendLine("  \"checksum_algorithm\": \"SHA-256\",");
            content.AppendLine("  \"created\": \"2025-01-10T09:00:00Z\",");
            content.AppendLine("  \"curator\": \"STFC_ISIS_Data_Office\"");
            content.AppendLine("}");
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path3, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
            zlib.Write(bytes, 0, bytes.Length);
        }

        var doc1 = ZstDocument.LoadFile(path1);
        var doc2 = ZstDocument.LoadFile(path2);
        var doc3 = ZstDocument.LoadFile(path3);

        // Block size assertions
        var bs1 = doc1.GetBlockSize();
        var bs2 = doc2.GetBlockSize();
        var bs3 = doc3.GetBlockSize();
        Assert.True(bs1 >= 0);
        Assert.True(bs2 >= 0);
        Assert.True(bs3 >= 0);
        Assert.Equal(bs1, doc1.GetBlockSize()); // consistent
        Assert.Equal(bs2, doc2.GetBlockSize()); // consistent

        // Checksum mode assertions
        var cm1 = doc1.GetChecksumMode();
        var cm2 = doc2.GetChecksumMode();
        var cm3 = doc3.GetChecksumMode();
        Assert.NotNull(cm1);
        Assert.NotNull(cm2);
        Assert.NotNull(cm3);
        Assert.Equal(cm1, doc1.GetChecksumMode()); // consistent
        Assert.Equal(cm2, doc2.GetChecksumMode()); // consistent

        // Basic ZST metrics
        Assert.True(doc1.CompressedSize > 0);
        Assert.True(doc2.CompressedSize > 0);
        Assert.True(doc1.OriginalSize > 0);
        Assert.True(doc2.OriginalSize > doc1.OriginalSize); // larger run → larger uncompressed

        // SaveToFile
        var out1 = TempFile("isis_calibration_run_001_out.zst");
        doc1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        var loaded1 = ZstDocument.LoadFile(out1);
        Assert.Equal(bs1, loaded1.GetBlockSize());
        Assert.Equal(cm1, loaded1.GetChecksumMode());

        var out2 = TempFile("isis_musr_run_2024_045_out.zst");
        doc2.SaveToFile(out2);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.Equal(bs2, loaded2.GetBlockSize());
        Assert.Equal(cm2, loaded2.GetChecksumMode());

        Assert.Equal(doc1.OriginalSize, loaded1.OriginalSize);
        Assert.Equal(doc2.CompressedSize, loaded2.CompressedSize);

        var ex1 = Record.Exception(() => loaded1.GetBlockSize());
        var ex2 = Record.Exception(() => loaded1.GetChecksumMode());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
