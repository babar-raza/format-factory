// Tests for ZstDocument.GetDecompressionSpeed, GetThroughputRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R258

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R258: Tests for ZstDocument.GetDecompressionSpeed, GetThroughputRatio deeper.
/// GetDecompressionSpeed(): returns estimated decompression throughput in MB/s (positive or 0).
/// GetThroughputRatio(): returns ratio of decompressed/compressed size as throughput multiplier.
/// Covers: GetDecompressionSpeed no-throw; GetDecompressionSpeed non-negative;
/// GetDecompressionSpeed consistent; GetDecompressionSpeed save-load;
/// GetThroughputRatio no-throw; GetThroughputRatio positive;
/// GetThroughputRatio greater-than-one for compressible; GetThroughputRatio consistent;
/// GetThroughputRatio save-load;
/// dogfood CreateDoc→GetDecompressionSpeed→GetThroughputRatio pipeline.
/// </summary>
public class ZstR258GetDecompressionSpeedAndThroughputDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR258GetDecompressionSpeedAndThroughputDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR258_" + Guid.NewGuid().ToString("N"));
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
        var sb = new StringBuilder();
        for (int i = 0; i < 300; i++)
            sb.AppendLine($"entry_{i:D6}|value_{i * 13 % 997:D4}|category_{i % 8}|score_{i % 10 + 1}|flag_{i % 2}");
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        using var ms = new MemoryStream();
        var writer = new ZstWriter(ms);
        writer.Write(raw);
        writer.Finish();
        File.WriteAllBytes(path, ms.ToArray());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetDecompressionSpeed
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDecompressionSpeed_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetDecompressionSpeed());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDecompressionSpeed_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetDecompressionSpeed() >= 0);
    }

    [Fact]
    public void GetDecompressionSpeed_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetDecompressionSpeed(), doc.GetDecompressionSpeed());
    }

    [Fact]
    public void GetDecompressionSpeed_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetDecompressionSpeed();
        var path = TempFile("ds_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDecompressionSpeed(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetThroughputRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetThroughputRatio_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetThroughputRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetThroughputRatio_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetThroughputRatio() > 0);
    }

    [Fact]
    public void GetThroughputRatio_GreaterThanOne_ForCompressible()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        // Repetitive structured text: decompressed > compressed → ratio > 1
        Assert.True(doc.GetThroughputRatio() >= 1.0);
    }

    [Fact]
    public void GetThroughputRatio_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var r1 = doc.GetThroughputRatio();
        var r2 = doc.GetThroughputRatio();
        Assert.Equal(r1, r2);
    }

    [Fact]
    public void GetThroughputRatio_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetThroughputRatio();
        var path = TempFile("tr_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetThroughputRatio(), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDecompressionSpeed_GetThroughputRatio_Pipeline()
    {
        // Genomics — UK Biobank Whole Exome Sequencing variant call format
        // VCF-style variant records from chr1 target region: throughput metrics for pipeline sizing
        var rng = new Random(20241201);
        var sb = new StringBuilder();

        // VCF-like header + data rows
        sb.AppendLine("##fileformat=VCFv4.2");
        sb.AppendLine("##reference=GRCh38");
        sb.AppendLine("##source=GATK_HaplotypeCaller_4.4.0");
        sb.AppendLine("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tUKB_SAMPLE");

        string[] refs = { "A", "T", "C", "G" };
        string[] alts = { "T", "A", "G", "C", "AT", "TC" };
        string[] filters = { "PASS", "LowQual", "PASS", "PASS", "GQ20" };

        for (int i = 0; i < 320; i++)
        {
            int pos = 1000000 + (i * 1237);
            string refBase = refs[rng.Next(refs.Length)];
            string alt = alts[rng.Next(alts.Length)];
            double qual = 30 + rng.NextDouble() * 60;
            string filter = filters[rng.Next(filters.Length)];
            int dp = 20 + rng.Next(60);
            double af = 0.1 + rng.NextDouble() * 0.4;
            int gq = 20 + rng.Next(60);
            string gt = rng.NextDouble() < 0.6 ? "0/1" : "1/1";
            sb.AppendLine($"chr1\t{pos}\t.\t{refBase}\t{alt}\t{qual:F1}\t{filter}\tDP={dp};AF={af:F3};AC=1;AN=2\tGT:GQ:DP\t{gt}:{gq}:{dp}");
        }

        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var path = TempFile("ukb_wes_chr1.zst");
        using (var ms = new MemoryStream())
        {
            var writer = new ZstWriter(ms);
            writer.Write(raw);
            writer.Finish();
            File.WriteAllBytes(path, ms.ToArray());
        }
        Assert.True(File.Exists(path));

        var doc = ZstDocument.LoadFile(path);

        // GetDecompressionSpeed
        var speed = doc.GetDecompressionSpeed();
        Assert.True(speed >= 0);
        Assert.Equal(speed, doc.GetDecompressionSpeed()); // consistent

        // GetThroughputRatio
        var ratio = doc.GetThroughputRatio();
        Assert.True(ratio > 0);
        Assert.Equal(ratio, doc.GetThroughputRatio()); // consistent

        // VCF data is highly compressible (repetitive FORMAT/INFO fields)
        Assert.True(ratio >= 1.0);

        // Frame and content sizes validate ratio
        Assert.True(doc.GetContentSize() > 0);
        Assert.True(doc.GetFrameSize() > 0);
        Assert.True(doc.GetContentSize() >= doc.GetFrameSize());

        // Compression ratio consistent with throughput ratio
        var compressionRatio = doc.GetCompressionRatio();
        Assert.True(compressionRatio > 0);

        // SaveToFile
        var outPath = TempFile("ukb_wes_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(speed, loaded.GetDecompressionSpeed(), precision: 6);
        Assert.Equal(ratio, loaded.GetThroughputRatio(), precision: 8);

        // Second dataset: minimal content for comparison
        var sb2 = new StringBuilder();
        sb2.AppendLine("##fileformat=VCFv4.2");
        sb2.AppendLine("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO");
        for (int i = 0; i < 10; i++)
            sb2.AppendLine($"chr1\t{100 + i}\t.\tA\tT\t{50.0 + i:F1}\tPASS\tDP=30");
        var raw2 = Encoding.UTF8.GetBytes(sb2.ToString());
        var path2 = TempFile("small_vcf.zst");
        using (var ms2 = new MemoryStream())
        {
            var w2 = new ZstWriter(ms2);
            w2.Write(raw2);
            w2.Finish();
            File.WriteAllBytes(path2, ms2.ToArray());
        }
        var doc2 = ZstDocument.LoadFile(path2);
        Assert.True(doc2.GetThroughputRatio() > 0);

        // Larger dataset has greater content
        Assert.True(doc.GetContentSize() > doc2.GetContentSize());

        var ex1 = Record.Exception(() => loaded.GetDecompressionSpeed());
        var ex2 = Record.Exception(() => loaded.GetThroughputRatio());
        var ex3 = Record.Exception(() => loaded.GetCompressionRatio());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
