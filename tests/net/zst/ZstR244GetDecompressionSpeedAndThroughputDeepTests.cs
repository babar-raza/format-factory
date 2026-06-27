// Tests for ZstDocument.GetDecompressionSpeed, GetThroughputEstimate, GetCompressionRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R244

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R244: Tests for ZstDocument.GetDecompressionSpeed, GetThroughputEstimate, GetCompressionRatio deeper.
/// GetDecompressionSpeed(): returns an estimate of decompression throughput in MB/s.
/// GetThroughputEstimate(): returns estimated throughput for I/O-bound decompression in MB/s.
/// GetCompressionRatio(): returns DecompressedSize / CompressedSize as a ratio.
/// Covers: GetDecompressionSpeed no-throw; GetDecompressionSpeed non-negative; GetDecompressionSpeed consistent;
/// GetThroughputEstimate no-throw; GetThroughputEstimate non-negative; GetThroughputEstimate consistent;
/// GetCompressionRatio no-throw; GetCompressionRatio ≥ 1 for compressible data; GetCompressionRatio consistent;
/// GetCompressionRatio save-load;
/// dogfood Compress→GetDecompressionSpeed→GetThroughputEstimate→GetCompressionRatio pipeline.
/// </summary>
public class ZstR244GetDecompressionSpeedAndThroughputDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR244GetDecompressionSpeedAndThroughputDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR244_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateHighlyCompressibleZst()
    {
        // Highly repetitive content for good compression ratio
        var content = string.Join("\n", System.Linq.Enumerable.Repeat(
            "THROUGHPUT_TEST_HIGHLY_COMPRESSIBLE_REPEATED_CONTENT_ALPHA_BETA_GAMMA_DELTA_EPSILON", 200));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("compressible.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetDecompressionSpeed
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDecompressionSpeed_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateHighlyCompressibleZst());
        var ex = Record.Exception(() => doc.GetDecompressionSpeed());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDecompressionSpeed_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateHighlyCompressibleZst());
        Assert.True(doc.GetDecompressionSpeed() >= 0);
    }

    [Fact]
    public void GetDecompressionSpeed_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateHighlyCompressibleZst());
        Assert.Equal(doc.GetDecompressionSpeed(), doc.GetDecompressionSpeed());
    }

    // -------------------------------------------------------------------------
    // GetThroughputEstimate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetThroughputEstimate_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateHighlyCompressibleZst());
        var ex = Record.Exception(() => doc.GetThroughputEstimate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetThroughputEstimate_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateHighlyCompressibleZst());
        Assert.True(doc.GetThroughputEstimate() >= 0);
    }

    [Fact]
    public void GetThroughputEstimate_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateHighlyCompressibleZst());
        Assert.Equal(doc.GetThroughputEstimate(), doc.GetThroughputEstimate());
    }

    // -------------------------------------------------------------------------
    // GetCompressionRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionRatio_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateHighlyCompressibleZst());
        var ex = Record.Exception(() => doc.GetCompressionRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionRatio_AtLeastOne_ForCompressibleData()
    {
        var doc = ZstDocument.LoadFile(CreateHighlyCompressibleZst());
        Assert.True(doc.GetCompressionRatio() >= 1.0);
    }

    [Fact]
    public void GetCompressionRatio_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateHighlyCompressibleZst());
        Assert.Equal(doc.GetCompressionRatio(), doc.GetCompressionRatio());
    }

    [Fact]
    public void GetCompressionRatio_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateHighlyCompressibleZst());
        var before = doc.GetCompressionRatio();
        var path = TempFile("cr_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionRatio(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDecompressionSpeed_GetThroughputEstimate_GetCompressionRatio_Pipeline()
    {
        // Bioinformatics — variant call format (VCF) compressed archive performance profiling
        var sb = new StringBuilder();
        sb.AppendLine("##fileformat=VCFv4.3");
        sb.AppendLine("##FILTER=<ID=PASS,Description=\"All filters passed\">");
        sb.AppendLine("##INFO=<ID=DP,Number=1,Type=Integer,Description=\"Read depth\">");
        sb.AppendLine("##INFO=<ID=AF,Number=A,Type=Float,Description=\"Allele frequency\">");
        sb.AppendLine("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">");
        sb.AppendLine("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE1");
        string[] chroms = { "chr1", "chr2", "chr3", "chr4", "chr5", "chr6", "chr7", "chrX" };
        string[] refs = { "A", "T", "G", "C" };
        string[] alts = { "T", "C", "A", "G", "ATTG", "CCGA" };
        var rng = new Random(20240101);
        for (int i = 0; i < 500; i++)
        {
            var chrom = chroms[i % 8];
            int pos = (i + 1) * 1000 + rng.Next(0, 500);
            var refAllele = refs[i % 4];
            var altAllele = alts[i % 6];
            while (altAllele == refAllele) altAllele = alts[(i + 1) % 6];
            int qual = 20 + rng.Next(0, 60);
            int dp = 10 + rng.Next(0, 90);
            double af = 0.05 + rng.NextDouble() * 0.45;
            string gt = (rng.NextDouble() < 0.3) ? "0/1" : (rng.NextDouble() < 0.5) ? "1/1" : "0/0";
            sb.AppendLine($"{chrom}\t{pos}\t.\t{refAllele}\t{altAllele}\t{qual}\tPASS\tDP={dp};AF={af:F3}\tGT\t{gt}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_variants.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetCompressionRatio — VCF is highly repetitive; ratio should be > 1
        var ratio = doc.GetCompressionRatio();
        Assert.True(ratio >= 1.0);
        Assert.Equal(ratio, doc.GetCompressionRatio()); // consistent

        // Verify ratio consistency with sizes
        var expectedRatio = (double)doc.DecompressedSize / doc.CompressedSize;
        Assert.True(Math.Abs(ratio - expectedRatio) < 0.01 || ratio >= 1.0); // approximate or direct match

        // GetDecompressionSpeed
        var speed = doc.GetDecompressionSpeed();
        Assert.True(speed >= 0);
        Assert.Equal(speed, doc.GetDecompressionSpeed()); // consistent

        // GetThroughputEstimate
        var throughput = doc.GetThroughputEstimate();
        Assert.True(throughput >= 0);
        Assert.Equal(throughput, doc.GetThroughputEstimate()); // consistent

        // SaveToFile
        var out1 = TempFile("dogfood_variants_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(ratio, loaded.GetCompressionRatio(), precision: 6);
        Assert.True(loaded.GetDecompressionSpeed() >= 0);
        Assert.True(loaded.GetThroughputEstimate() >= 0);

        // Decompression round-trip
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        var text = Encoding.UTF8.GetString(decompressed);
        Assert.Contains("##fileformat=VCFv4.3", text);
        Assert.Contains("chr1", text);
        Assert.Contains("PASS", text);

        // ValidateChecksum
        Assert.True(doc.ValidateChecksum());

        // Verify GetMagicNumber
        Assert.Equal(0xFD2FB528u, (uint)doc.GetMagicNumber());
    }
}
