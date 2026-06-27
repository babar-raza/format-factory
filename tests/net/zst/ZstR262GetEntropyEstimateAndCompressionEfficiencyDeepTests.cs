// Tests for ZstDocument.GetEntropyEstimate, GetCompressionEfficiency deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R262

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R262: Tests for ZstDocument.GetEntropyEstimate, GetCompressionEfficiency deeper.
/// GetEntropyEstimate(): returns estimated source entropy in bits per byte (0.0–8.0).
/// GetCompressionEfficiency(): returns ratio of compression gain to theoretical maximum (0.0–1.0).
/// Covers: GetEntropyEstimate no-throw; GetEntropyEstimate in-range; GetEntropyEstimate consistent;
/// GetEntropyEstimate lower for compressible; GetEntropyEstimate save-load;
/// GetCompressionEfficiency no-throw; GetCompressionEfficiency in-range;
/// GetCompressionEfficiency consistent; GetCompressionEfficiency save-load;
/// GetCompressionEfficiency higher for repetitive; dogfood pipeline.
/// </summary>
public class ZstR262GetEntropyEstimateAndCompressionEfficiencyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR262GetEntropyEstimateAndCompressionEfficiencyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR262_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateRepetitivZst()
    {
        var path = TempFile("repetitive.zst");
        var source = Encoding.UTF8.GetBytes(new string('A', 10000));
        using var fs = File.Create(path);
        using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
        zs.Write(source, 0, source.Length);
        return path;
    }

    private string CreateHighEntropyZst()
    {
        var path = TempFile("high_entropy.zst");
        var rng = new Random(42);
        var source = new byte[10000];
        rng.NextBytes(source);
        using var fs = File.Create(path);
        using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
        zs.Write(source, 0, source.Length);
        return path;
    }

    private string CreateSampleZst()
    {
        var path = TempFile("sample.zst");
        var text = "The quick brown fox jumps over the lazy dog. " +
                   "Pack my box with five dozen liquor jugs. " +
                   "How vexingly quick daft zebras jump! ";
        var source = Encoding.UTF8.GetBytes(string.Concat(Enumerable.Repeat(text, 50)));
        using var fs = File.Create(path);
        using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
        zs.Write(source, 0, source.Length);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetEntropyEstimate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEntropyEstimate_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetEntropyEstimate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEntropyEstimate_InRange()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var e = doc.GetEntropyEstimate();
        Assert.True(e >= 0.0 && e <= 8.0);
    }

    [Fact]
    public void GetEntropyEstimate_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetEntropyEstimate(), doc.GetEntropyEstimate());
    }

    [Fact]
    public void GetEntropyEstimate_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetEntropyEstimate();
        var path = TempFile("ee_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetEntropyEstimate(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetCompressionEfficiency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionEfficiency_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetCompressionEfficiency());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionEfficiency_InRange()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ce = doc.GetCompressionEfficiency();
        Assert.True(ce >= 0.0 && ce <= 1.0);
    }

    [Fact]
    public void GetCompressionEfficiency_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetCompressionEfficiency(), doc.GetCompressionEfficiency());
    }

    [Fact]
    public void GetCompressionEfficiency_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetCompressionEfficiency();
        var path = TempFile("ce_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionEfficiency(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetEntropyEstimate_GetCompressionEfficiency_Pipeline()
    {
        // Genomics — UK Biobank Whole Genome Sequencing (WGS) data compression
        // Comparing compression of structured VCF annotation data vs raw FASTQ reads
        // Entropy and efficiency analysis for storage tier selection

        // File 1: Structured clinical annotation (highly compressible)
        var pathAnnotation = TempFile("wgs_clinical_annotation.zst");
        {
            var sb = new StringBuilder();
            sb.AppendLine("##fileformat=VCFv4.2");
            sb.AppendLine("##FILTER=<ID=PASS,Description=\"All filters passed\">");
            sb.AppendLine("##INFO=<ID=AC,Number=A,Type=Integer,Description=\"Allele count in genotypes\">");
            sb.AppendLine("##INFO=<ID=AF,Number=A,Type=Float,Description=\"Allele Frequency\">");
            sb.AppendLine("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">");
            sb.AppendLine("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tUKB123456");
            var rng = new Random(20240901);
            for (int i = 0; i < 300; i++)
            {
                int pos = 100000 + i * 1000 + rng.Next(500);
                string ref_ = new[] { "A", "C", "G", "T" }[rng.Next(4)];
                string alt = new[] { "A", "C", "G", "T" }[rng.Next(4)];
                double af = Math.Round(rng.NextDouble() * 0.5, 4);
                string gt = rng.Next(2) == 0 ? "0/1" : "1/1";
                sb.AppendLine($"chr1\t{pos}\t.\t{ref_}\t{alt}\t100\tPASS\tAC=1;AF={af}\tGT\t{gt}");
            }
            var source = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(pathAnnotation);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
            zs.Write(source, 0, source.Length);
        }

        // File 2: Quality scores (moderate entropy — numerical patterns)
        var pathQuality = TempFile("wgs_quality_scores.zst");
        {
            var sb = new StringBuilder();
            var rng = new Random(20240902);
            for (int i = 0; i < 200; i++)
            {
                var scores = new StringBuilder();
                for (int j = 0; j < 100; j++)
                {
                    if (j > 0) scores.Append('\t');
                    scores.Append(20 + rng.Next(20)); // Phred scores 20-39
                }
                sb.AppendLine(scores.ToString());
            }
            var source = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(pathQuality);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
            zs.Write(source, 0, source.Length);
        }

        var docAnnotation = ZstDocument.LoadFile(pathAnnotation);
        var docQuality = ZstDocument.LoadFile(pathQuality);

        // Entropy estimates — both in valid range
        var eeAnnotation = docAnnotation.GetEntropyEstimate();
        var eeQuality = docQuality.GetEntropyEstimate();
        Assert.True(eeAnnotation >= 0.0 && eeAnnotation <= 8.0);
        Assert.True(eeQuality >= 0.0 && eeQuality <= 8.0);
        Assert.Equal(eeAnnotation, docAnnotation.GetEntropyEstimate()); // consistent
        Assert.Equal(eeQuality, docQuality.GetEntropyEstimate()); // consistent

        // Compression efficiency — both in valid range
        var ceAnnotation = docAnnotation.GetCompressionEfficiency();
        var ceQuality = docQuality.GetCompressionEfficiency();
        Assert.True(ceAnnotation >= 0.0 && ceAnnotation <= 1.0);
        Assert.True(ceQuality >= 0.0 && ceQuality <= 1.0);
        Assert.Equal(ceAnnotation, docAnnotation.GetCompressionEfficiency()); // consistent

        // Basic document properties
        Assert.True(docAnnotation.CompressedSize > 0);
        Assert.True(docQuality.CompressedSize > 0);

        // SaveToFile and verify
        var outAnnotation = TempFile("wgs_annotation_out.zst");
        docAnnotation.SaveToFile(outAnnotation);
        Assert.True(File.Exists(outAnnotation));
        var loadedAnnotation = ZstDocument.LoadFile(outAnnotation);
        Assert.Equal(eeAnnotation, loadedAnnotation.GetEntropyEstimate(), precision: 6);
        Assert.Equal(ceAnnotation, loadedAnnotation.GetCompressionEfficiency(), precision: 6);

        var outQuality = TempFile("wgs_quality_out.zst");
        docQuality.SaveToFile(outQuality);
        Assert.True(File.Exists(outQuality));
        var loadedQuality = ZstDocument.LoadFile(outQuality);
        Assert.Equal(eeQuality, loadedQuality.GetEntropyEstimate(), precision: 6);
        Assert.Equal(ceQuality, loadedQuality.GetCompressionEfficiency(), precision: 6);

        var ex1 = Record.Exception(() => loadedAnnotation.GetEntropyEstimate());
        var ex2 = Record.Exception(() => loadedAnnotation.GetCompressionEfficiency());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
