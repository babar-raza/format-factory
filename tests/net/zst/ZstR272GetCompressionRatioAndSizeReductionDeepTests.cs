// Tests for ZstDocument.GetCompressionRatio, GetSizeReductionPercent deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R272

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R272: Tests for ZstDocument.GetCompressionRatio, GetSizeReductionPercent deeper.
/// GetCompressionRatio(): returns decompressed/compressed size ratio; ≥ 1.0 for compressible data.
/// GetSizeReductionPercent(): returns percentage reduction in size; in [0,100] for normal archives.
/// Covers: GetCompressionRatio no-throw; GetCompressionRatio positive;
/// GetCompressionRatio geq one for compressible data; GetCompressionRatio consistent;
/// GetCompressionRatio save-load;
/// GetSizeReductionPercent no-throw; GetSizeReductionPercent in-range;
/// GetSizeReductionPercent consistent; GetSizeReductionPercent save-load;
/// CompressionRatio and SizeReductionPercent are consistent with each other; dogfood pipeline.
/// </summary>
public class ZstR272GetCompressionRatioAndSizeReductionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR272GetCompressionRatioAndSizeReductionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR272_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCompressibleZst(string name, int size = 5000)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        for (int i = 0; i < size / 20; i++)
            sb.Append($"AAAAAABBBBBCCCCC{i:D4}");
        var original = Encoding.UTF8.GetBytes(sb.ToString());
        using var ms = new MemoryStream();
        using (var zs = new ZLibStream(ms, CompressionLevel.Optimal, leaveOpen: true))
            zs.Write(original, 0, original.Length);
        File.WriteAllBytes(path, ms.ToArray());
        return path;
    }

    private string CreateLargeCompressibleZst(string name, int size = 20000)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        for (int i = 0; i < size / 30; i++)
            sb.Append($"structured_record_{i:D6}_field_A_{(i % 10):D2}_field_B_{(i % 7):D2}_end ");
        var original = Encoding.UTF8.GetBytes(sb.ToString());
        using var ms = new MemoryStream();
        using (var zs = new ZLibStream(ms, CompressionLevel.Optimal, leaveOpen: true))
            zs.Write(original, 0, original.Length);
        File.WriteAllBytes(path, ms.ToArray());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetCompressionRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionRatio_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        var ex = Record.Exception(() => doc.GetCompressionRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionRatio_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        Assert.True(doc.GetCompressionRatio() > 0.0);
    }

    [Fact]
    public void GetCompressionRatio_Geq_One_ForCompressibleData()
    {
        var doc = ZstDocument.LoadFile(CreateLargeCompressibleZst("large.zst"));
        Assert.True(doc.GetCompressionRatio() >= 1.0);
    }

    [Fact]
    public void GetCompressionRatio_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        Assert.Equal(doc.GetCompressionRatio(), doc.GetCompressionRatio());
    }

    [Fact]
    public void GetCompressionRatio_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        var before = doc.GetCompressionRatio();
        var path = TempFile("cr_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).GetCompressionRatio(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetSizeReductionPercent
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSizeReductionPercent_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        var ex = Record.Exception(() => doc.GetSizeReductionPercent());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSizeReductionPercent_InRange()
    {
        var doc = ZstDocument.LoadFile(CreateLargeCompressibleZst("large.zst"));
        var pct = doc.GetSizeReductionPercent();
        Assert.True(pct >= 0.0 && pct <= 100.0);
    }

    [Fact]
    public void GetSizeReductionPercent_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        Assert.Equal(doc.GetSizeReductionPercent(), doc.GetSizeReductionPercent());
    }

    [Fact]
    public void GetSizeReductionPercent_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        var before = doc.GetSizeReductionPercent();
        var path = TempFile("sr_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).GetSizeReductionPercent(), precision: 6);
    }

    [Fact]
    public void CompressionRatio_And_SizeReductionPercent_Consistent()
    {
        // ratio r = decompressed/compressed → reduction = (1 - 1/r) * 100
        var doc = ZstDocument.LoadFile(CreateLargeCompressibleZst("large.zst"));
        var ratio = doc.GetCompressionRatio();
        var pct = doc.GetSizeReductionPercent();
        if (ratio > 0)
        {
            double expected = (1.0 - 1.0 / ratio) * 100.0;
            Assert.Equal(expected, pct, precision: 4);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCompressionRatio_GetSizeReductionPercent_Pipeline()
    {
        // Science — STFC / Diamond Light Source: Synchrotron Diffraction Data Archive
        // Compressed crystallographic data files (CIF format) from protein structure determination
        // Compression ratio benchmarks inform storage planning for PB-scale data archives

        var path = TempFile("diamond_lightsource_diffraction.zst");
        {
            var sb = new StringBuilder();
            // Simulate CIF-style crystallographic data
            sb.AppendLine("data_DIAMOND_PROTEIN_STRUCTURE_I24_20240601");
            sb.AppendLine("_cell_length_a                   52.341");
            sb.AppendLine("_cell_length_b                   52.341");
            sb.AppendLine("_cell_length_c                   120.887");
            sb.AppendLine("_cell_angle_alpha                 90.000");
            sb.AppendLine("_cell_angle_beta                  90.000");
            sb.AppendLine("_cell_angle_gamma                120.000");
            sb.AppendLine("_symmetry_space_group_name_H-M   'P 32 2 1'");
            sb.AppendLine("loop_");
            sb.AppendLine("_atom_site_label");
            sb.AppendLine("_atom_site_type_symbol");
            sb.AppendLine("_atom_site_fract_x");
            sb.AppendLine("_atom_site_fract_y");
            sb.AppendLine("_atom_site_fract_z");
            sb.AppendLine("_atom_site_occupancy");
            sb.AppendLine("_atom_site_B_iso_or_equiv");

            var rng = new Random(20240601);
            string[] elements = { "C", "N", "O", "S", "H", "C", "C", "N", "O", "C" };
            for (int i = 0; i < 2000; i++)
            {
                string elem = elements[rng.Next(elements.Length)];
                double x = rng.NextDouble();
                double y = rng.NextDouble();
                double z = rng.NextDouble();
                double occ = 0.95 + rng.NextDouble() * 0.05;
                double bfac = 10 + rng.NextDouble() * 30;
                sb.AppendLine($"{elem}{i:D4}  {elem}  {x:F5}  {y:F5}  {z:F5}  {occ:F3}  {bfac:F2}");
            }

            var original = Encoding.UTF8.GetBytes(sb.ToString());
            using var ms = new MemoryStream();
            using (var zs = new ZLibStream(ms, CompressionLevel.Optimal, leaveOpen: true))
                zs.Write(original, 0, original.Length);
            File.WriteAllBytes(path, ms.ToArray());
        }

        var doc = ZstDocument.LoadFile(path);

        // Compression ratio
        var ratio = doc.GetCompressionRatio();
        Assert.True(ratio > 0.0);
        Assert.True(ratio >= 1.0); // CIF data is text and compresses well
        Assert.Equal(ratio, doc.GetCompressionRatio()); // consistent

        // Size reduction percent
        var pct = doc.GetSizeReductionPercent();
        Assert.True(pct >= 0.0 && pct <= 100.0);
        Assert.Equal(pct, doc.GetSizeReductionPercent()); // consistent

        // Cross-consistency
        if (ratio > 0)
        {
            double expected = (1.0 - 1.0 / ratio) * 100.0;
            Assert.Equal(expected, pct, precision: 4);
        }

        // Sizes must be positive
        Assert.True(doc.GetDecompressedSize() > 0);
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetCompressedSize() <= doc.GetDecompressedSize());

        // SaveToFile
        var outPath = TempFile("diamond_ls_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(ratio, loaded.GetCompressionRatio(), precision: 6);
        Assert.Equal(pct, loaded.GetSizeReductionPercent(), precision: 6);

        // Second archive: log file data (also compressible)
        var logPath = TempFile("beamline_i24_log.zst");
        {
            var sb = new StringBuilder();
            var rng2 = new Random(20240602);
            for (int i = 0; i < 500; i++)
            {
                double flux = 1e12 + rng2.NextDouble() * 1e11;
                double energy = 12.658 + rng2.NextDouble() * 0.01;
                sb.AppendLine($"2024-06-01T{(i / 3600):D2}:{((i % 3600) / 60):D2}:{(i % 60):D2}Z I24 BEAM FLUX={flux:E3} ENERGY={energy:F4} STATUS=OK");
            }
            var orig2 = Encoding.UTF8.GetBytes(sb.ToString());
            using var ms2 = new MemoryStream();
            using (var zs2 = new ZLibStream(ms2, CompressionLevel.Optimal, leaveOpen: true))
                zs2.Write(orig2, 0, orig2.Length);
            File.WriteAllBytes(logPath, ms2.ToArray());
        }
        var logDoc = ZstDocument.LoadFile(logPath);
        Assert.True(logDoc.GetCompressionRatio() > 0.0);
        Assert.True(logDoc.GetSizeReductionPercent() >= 0.0 && logDoc.GetSizeReductionPercent() <= 100.0);

        var ex1 = Record.Exception(() => loaded.GetCompressionRatio());
        var ex2 = Record.Exception(() => loaded.GetSizeReductionPercent());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
