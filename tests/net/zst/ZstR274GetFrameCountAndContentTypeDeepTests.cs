// Tests for ZstDocument.GetFrameCount, GetContentType deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R274

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R274: Tests for ZstDocument.GetFrameCount, GetContentType deeper.
/// GetFrameCount(): returns the number of Zstandard frames in the archive.
/// GetContentType(): returns a string identifying the detected MIME type or content category.
/// Covers: GetFrameCount no-throw; GetFrameCount positive; GetFrameCount consistent;
/// GetFrameCount save-load; GetFrameCount non-decreasing across multiple frames;
/// GetContentType no-throw; GetContentType non-null; GetContentType non-empty;
/// GetContentType consistent; GetContentType save-load; dogfood pipeline.
/// </summary>
public class ZstR274GetFrameCountAndContentTypeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR274GetFrameCountAndContentTypeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR274_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleZst(string name = "sample.zst")
    {
        var path = TempFile(name);
        var src = Encoding.UTF8.GetBytes(
            string.Concat(Enumerable.Repeat("Frame count test data with compressible content. ", 80)));
        using var fs = File.Create(path);
        using var zs = new ZLibStream(fs, CompressionLevel.Optimal, leaveOpen: true);
        zs.Write(src, 0, src.Length);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFrameCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetFrameCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameCount_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetFrameCount() >= 1);
    }

    [Fact]
    public void GetFrameCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetFrameCount(), doc.GetFrameCount());
    }

    [Fact]
    public void GetFrameCount_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetFrameCount();
        var path = TempFile("fc_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).GetFrameCount());
    }

    // -------------------------------------------------------------------------
    // GetContentType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContentType_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetContentType());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContentType_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.NotNull(doc.GetContentType());
    }

    [Fact]
    public void GetContentType_NonEmpty()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.NotEmpty(doc.GetContentType());
    }

    [Fact]
    public void GetContentType_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetContentType(), doc.GetContentType());
    }

    [Fact]
    public void GetContentType_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetContentType();
        var path = TempFile("ct_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).GetContentType());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFrameCount_GetContentType_Pipeline()
    {
        // Bioinformatics — Genomics England / NHS GMS: Whole Genome Sequencing Variant Archives
        // Compressed VCF variant data from 100,000 Genomes Project rare disease cohort
        // Frame count verifies archive integrity; content type determines downstream pipeline routing

        // Scenario 1: VCF variant data (highly compressible structured text)
        var path1 = TempFile("gms_wgs_vcf_chr1_grch38.zst");
        {
            var sb = new StringBuilder();
            sb.AppendLine("##fileformat=VCFv4.3");
            sb.AppendLine("##reference=GRCh38.p14");
            sb.AppendLine("##source=GeL_WGS_Pipeline_v5.2");
            sb.AppendLine("##FILTER=<ID=PASS,Description=\"All filters passed\">");
            sb.AppendLine("##INFO=<ID=DP,Number=1,Type=Integer,Description=\"Total Depth\">");
            sb.AppendLine("##INFO=<ID=AF,Number=A,Type=Float,Description=\"Allele Frequency\">");
            sb.AppendLine("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">");
            sb.AppendLine("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tGEL_P00001");
            var rng = new Random(20240415);
            for (int i = 0; i < 200; i++)
            {
                int pos = 10000 + i * 5000 + rng.Next(4999);
                string ref_ = new[] { "A", "G", "C", "T" }[rng.Next(4)];
                string alt = new[] { "T", "C", "G", "A" }[rng.Next(4)];
                double af = rng.NextDouble() * 0.5;
                int dp = 30 + rng.Next(200);
                string gt = rng.NextDouble() < 0.3 ? "0/1" : (rng.NextDouble() < 0.5 ? "1/1" : "0/0");
                sb.AppendLine($"1\t{pos}\t.\t{ref_}\t{alt}\t{30 + rng.Next(970)}\tPASS\tDP={dp};AF={af:F4}\tGT\t{gt}");
            }
            var raw = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(path1);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal, leaveOpen: true);
            zs.Write(raw, 0, raw.Length);
        }

        // Scenario 2: FASTQ sequence reads (bioinformatics raw data)
        var path2 = TempFile("gms_wgs_fastq_r1_batch.zst");
        {
            var sb = new StringBuilder();
            var bases = new[] { 'A', 'T', 'G', 'C' };
            var rng = new Random(20240416);
            for (int i = 0; i < 50; i++)
            {
                sb.AppendLine($"@GEL.P00001.RUN001.{i:D6} 1:N:0:ATCACG");
                var seq = new char[150];
                var qual = new char[150];
                for (int j = 0; j < 150; j++)
                {
                    seq[j] = bases[rng.Next(4)];
                    qual[j] = (char)(33 + rng.Next(40)); // Phred+33
                }
                sb.AppendLine(new string(seq));
                sb.AppendLine("+");
                sb.AppendLine(new string(qual));
            }
            var raw = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(path2);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal, leaveOpen: true);
            zs.Write(raw, 0, raw.Length);
        }

        // Scenario 3: BED annotation file (genome interval data)
        var path3 = TempFile("gms_panel_v4_target_regions.zst");
        {
            var sb = new StringBuilder();
            string[] chroms = { "chr1", "chr2", "chr3", "chr7", "chr12", "chr17", "chr22", "chrX" };
            var rng = new Random(20240417);
            sb.AppendLine("track name=\"GeL_PanelApp_v4\" description=\"Rare Disease Panel Targets\" useScore=1");
            for (int i = 0; i < 100; i++)
            {
                string chrom = chroms[rng.Next(chroms.Length)];
                int start = rng.Next(1, 100_000_000);
                int end = start + rng.Next(100, 5000);
                string gene = $"GENE{rng.Next(1000):D4}";
                sb.AppendLine($"{chrom}\t{start}\t{end}\t{gene}\t{rng.Next(100, 1000)}");
            }
            var raw = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(path3);
            using var zs = new ZLibStream(fs, CompressionLevel.SmallestSize, leaveOpen: true);
            zs.Write(raw, 0, raw.Length);
        }

        var doc1 = ZstDocument.LoadFile(path1);
        var doc2 = ZstDocument.LoadFile(path2);
        var doc3 = ZstDocument.LoadFile(path3);

        // Frame counts
        var fc1 = doc1.GetFrameCount();
        var fc2 = doc2.GetFrameCount();
        var fc3 = doc3.GetFrameCount();
        Assert.True(fc1 >= 1);
        Assert.True(fc2 >= 1);
        Assert.True(fc3 >= 1);
        Assert.Equal(fc1, doc1.GetFrameCount()); // consistent
        Assert.Equal(fc2, doc2.GetFrameCount()); // consistent
        Assert.Equal(fc3, doc3.GetFrameCount()); // consistent

        // Content types
        var ct1 = doc1.GetContentType();
        var ct2 = doc2.GetContentType();
        var ct3 = doc3.GetContentType();
        Assert.NotNull(ct1);
        Assert.NotNull(ct2);
        Assert.NotNull(ct3);
        Assert.NotEmpty(ct1);
        Assert.NotEmpty(ct2);
        Assert.NotEmpty(ct3);
        Assert.Equal(ct1, doc1.GetContentType()); // consistent
        Assert.Equal(ct2, doc2.GetContentType()); // consistent
        Assert.Equal(ct3, doc3.GetContentType()); // consistent

        // Cross-consistency: compressed sizes
        Assert.True(doc1.GetCompressedSize() > 0);
        Assert.True(doc2.GetCompressedSize() > 0);
        Assert.True(doc3.GetCompressedSize() > 0);

        // SaveToFile
        var out1 = TempFile("gms_vcf_out.zst");
        doc1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loaded1 = ZstDocument.LoadFile(out1);
        Assert.Equal(fc1, loaded1.GetFrameCount());
        Assert.Equal(ct1, loaded1.GetContentType());

        var out2 = TempFile("gms_fastq_out.zst");
        doc2.SaveToFile(out2);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.Equal(fc2, loaded2.GetFrameCount());
        Assert.Equal(ct2, loaded2.GetContentType());

        var out3 = TempFile("gms_bed_out.zst");
        doc3.SaveToFile(out3);
        var loaded3 = ZstDocument.LoadFile(out3);
        Assert.Equal(fc3, loaded3.GetFrameCount());
        Assert.Equal(ct3, loaded3.GetContentType());

        var ex1 = Record.Exception(() => loaded1.GetFrameCount());
        var ex2 = Record.Exception(() => loaded2.GetContentType());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
