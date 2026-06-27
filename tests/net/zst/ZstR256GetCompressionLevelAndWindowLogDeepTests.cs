// Tests for ZstDocument.GetCompressionLevel, GetWindowLog deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R256

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R256: Tests for ZstDocument.GetCompressionLevel, GetWindowLog deeper.
/// GetCompressionLevel(): returns the compression level used (1-22, or -1 if not stored).
/// GetWindowLog(): returns the window size log2 value used for compression.
/// Covers: GetCompressionLevel no-throw; GetCompressionLevel in valid range;
/// GetCompressionLevel consistent; GetCompressionLevel save-load;
/// GetWindowLog no-throw; GetWindowLog non-negative; GetWindowLog consistent;
/// GetWindowLog save-load; GetWindowLog reasonable upper bound;
/// dogfood CreateDoc→GetCompressionLevel→GetWindowLog pipeline.
/// </summary>
public class ZstR256GetCompressionLevelAndWindowLogDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR256GetCompressionLevelAndWindowLogDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR256_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleZst(int level = 3)
    {
        var path = TempFile($"sample_l{level}.zst");
        var sb = new StringBuilder();
        for (int i = 0; i < 300; i++)
            sb.AppendLine($"sample_record_{i:D6}|data_{i * 13 % 1000}|category_{i % 8}");
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        using var ms = new MemoryStream();
        var writer = new ZstWriter(ms, compressionLevel: level);
        writer.Write(raw);
        writer.Finish();
        File.WriteAllBytes(path, ms.ToArray());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetCompressionLevel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionLevel_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetCompressionLevel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionLevel_InValidRange()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var level = doc.GetCompressionLevel();
        // Valid range: -1 (unknown) or 1-22
        Assert.True(level == -1 || (level >= 1 && level <= 22));
    }

    [Fact]
    public void GetCompressionLevel_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetCompressionLevel(), doc.GetCompressionLevel());
    }

    [Fact]
    public void GetCompressionLevel_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetCompressionLevel();
        var path = TempFile("cl_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionLevel());
    }

    // -------------------------------------------------------------------------
    // GetWindowLog
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWindowLog_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetWindowLog());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWindowLog_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetWindowLog() >= 0);
    }

    [Fact]
    public void GetWindowLog_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetWindowLog(), doc.GetWindowLog());
    }

    [Fact]
    public void GetWindowLog_ReasonableUpperBound()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        // Window log should be ≤ 31 (maximum 2GB window in Zstandard spec)
        Assert.True(doc.GetWindowLog() <= 31);
    }

    [Fact]
    public void GetWindowLog_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetWindowLog();
        var path = TempFile("wl_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetWindowLog());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCompressionLevel_GetWindowLog_Pipeline()
    {
        // Scientific — UK Biobank Whole Exome Sequencing (WES) variant call pipeline
        // VCF-format variant data compressed at different levels for archival vs streaming
        var rng = new Random(20241101);
        string[] chromosomes = { "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "X" };
        string[] refBases = { "A", "T", "C", "G" };
        string[] altBases = { "T", "A", "G", "C", "AT", "TC", "AGT" };
        string[] filters = { "PASS", "LowQual", "LowDP", "PASS", "PASS" };
        string[] gts = { "0/1", "1/1", "0/1", "0/0", "1/2" };

        var vcfSb = new StringBuilder();
        vcfSb.AppendLine("##fileformat=VCFv4.2");
        vcfSb.AppendLine("##source=UKBiobankWES_OQFE_pipeline_v3.1");
        vcfSb.AppendLine("##reference=GRCh38/hg38");
        vcfSb.AppendLine("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE");
        for (int i = 0; i < 250; i++)
        {
            string chrom = chromosomes[rng.Next(chromosomes.Length)];
            int pos = 1000000 + rng.Next(240000000);
            string rsId = rng.NextDouble() < 0.6 ? $"rs{rng.Next(100000000)}" : ".";
            string rf = refBases[rng.Next(refBases.Length)];
            string alt = altBases[rng.Next(altBases.Length)];
            double qual = 20 + rng.NextDouble() * 980;
            string filter = filters[rng.Next(filters.Length)];
            int dp = 15 + rng.Next(200);
            int af = rng.Next(1, 100);
            string gt = gts[rng.Next(gts.Length)];
            int gq = 10 + rng.Next(90);
            vcfSb.AppendLine($"{chrom}\t{pos}\t{rsId}\t{rf}\t{alt}\t{qual:F1}\t{filter}\tDP={dp};AF={af / 100.0:F3}\tGT:GQ\t{gt}:{gq}");
        }

        // Compress at streaming level (fast)
        var rawBytes = Encoding.UTF8.GetBytes(vcfSb.ToString());
        var pathL1 = TempFile("ukbiobank_variants_l1.zst");
        using (var ms1 = new MemoryStream())
        {
            var w1 = new ZstWriter(ms1, compressionLevel: 1);
            w1.Write(rawBytes);
            w1.Finish();
            File.WriteAllBytes(pathL1, ms1.ToArray());
        }

        // Compress at archival level (high compression)
        var pathL9 = TempFile("ukbiobank_variants_l9.zst");
        using (var ms9 = new MemoryStream())
        {
            var w9 = new ZstWriter(ms9, compressionLevel: 9);
            w9.Write(rawBytes);
            w9.Finish();
            File.WriteAllBytes(pathL9, ms9.ToArray());
        }

        var docL1 = ZstDocument.LoadFile(pathL1);
        var docL9 = ZstDocument.LoadFile(pathL9);

        // GetCompressionLevel
        var levelL1 = docL1.GetCompressionLevel();
        var levelL9 = docL9.GetCompressionLevel();
        Assert.True(levelL1 == -1 || (levelL1 >= 1 && levelL1 <= 22));
        Assert.True(levelL9 == -1 || (levelL9 >= 1 && levelL9 <= 22));
        Assert.Equal(levelL1, docL1.GetCompressionLevel()); // consistent
        Assert.Equal(levelL9, docL9.GetCompressionLevel()); // consistent

        // GetWindowLog
        var wlL1 = docL1.GetWindowLog();
        var wlL9 = docL9.GetWindowLog();
        Assert.True(wlL1 >= 0 && wlL1 <= 31);
        Assert.True(wlL9 >= 0 && wlL9 <= 31);
        Assert.Equal(wlL1, docL1.GetWindowLog()); // consistent
        Assert.Equal(wlL9, docL9.GetWindowLog()); // consistent

        // Higher compression should produce smaller file
        Assert.True(new FileInfo(pathL9).Length <= new FileInfo(pathL1).Length);

        // Content size should be same (same input)
        Assert.Equal(docL1.GetContentSize(), docL9.GetContentSize());

        // Basic frame properties
        Assert.True(docL1.FrameCount > 0);
        Assert.True(docL9.FrameCount > 0);
        Assert.True(docL1.CompressedSize > 0);
        Assert.True(docL9.CompressedSize > 0);

        // SaveToFile
        var outL1 = TempFile("ukbiobank_out_l1.zst");
        docL1.SaveToFile(outL1);
        Assert.True(File.Exists(outL1));

        var outL9 = TempFile("ukbiobank_out_l9.zst");
        docL9.SaveToFile(outL9);
        Assert.True(File.Exists(outL9));

        // LoadFile and verify
        var loadedL1 = ZstDocument.LoadFile(outL1);
        Assert.Equal(levelL1, loadedL1.GetCompressionLevel());
        Assert.Equal(wlL1, loadedL1.GetWindowLog());

        var loadedL9 = ZstDocument.LoadFile(outL9);
        Assert.Equal(levelL9, loadedL9.GetCompressionLevel());
        Assert.Equal(wlL9, loadedL9.GetWindowLog());

        // No-throw
        var ex1 = Record.Exception(() => loadedL1.GetFrameSize());
        var ex2 = Record.Exception(() => loadedL9.GetCompressionRatio());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
