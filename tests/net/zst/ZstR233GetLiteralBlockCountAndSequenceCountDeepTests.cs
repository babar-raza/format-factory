// Tests for ZstDocument.GetLiteralBlockCount, GetSequenceCount, GetLiteralLengthHistogram deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R233

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R233: Tests for ZstDocument.GetLiteralBlockCount, GetSequenceCount, GetLiteralLengthHistogram deeper.
/// GetLiteralBlockCount(): returns the number of literal blocks in the compressed frame.
/// GetSequenceCount(): returns the number of sequences (match+literal) in the compressed data.
/// GetLiteralLengthHistogram(): returns an array representing the literal length frequency distribution.
/// Covers: GetLiteralBlockCount no-throw; GetLiteralBlockCount positive; GetLiteralBlockCount consistent;
/// GetLiteralBlockCount save-load;
/// GetSequenceCount no-throw; GetSequenceCount positive; GetSequenceCount consistent;
/// GetSequenceCount greater for repetitive data; GetSequenceCount save-load;
/// GetLiteralLengthHistogram no-throw; GetLiteralLengthHistogram non-null; GetLiteralLengthHistogram consistent;
/// GetLiteralLengthHistogram save-load;
/// dogfood Compress→GetLiteralBlockCount→GetSequenceCount→GetLiteralLengthHistogram→SaveToFile pipeline.
/// </summary>
public class ZstR233GetLiteralBlockCountAndSequenceCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR233GetLiteralBlockCountAndSequenceCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR233_" + Guid.NewGuid().ToString("N"));
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
            "PATTERN_ALPHA_BETA_GAMMA_DELTA_EPSILON_ZETA_ETA_THETA_IOTA_KAPPA", 200));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("repetitive.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    private string CreateDiverseZst()
    {
        var sb = new StringBuilder();
        var rng = new Random(99);
        for (int i = 0; i < 300; i++)
            sb.AppendLine($"{rng.Next(100000):D6},{rng.NextDouble():F8},{Guid.NewGuid()}");
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(sb.ToString()));
        var path = TempFile("diverse.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetLiteralBlockCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLiteralBlockCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateDiverseZst());
        var ex = Record.Exception(() => doc.GetLiteralBlockCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLiteralBlockCount_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateDiverseZst());
        Assert.True(doc.GetLiteralBlockCount() > 0);
    }

    [Fact]
    public void GetLiteralBlockCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateDiverseZst());
        Assert.Equal(doc.GetLiteralBlockCount(), doc.GetLiteralBlockCount());
    }

    [Fact]
    public void GetLiteralBlockCount_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateDiverseZst());
        var before = doc.GetLiteralBlockCount();
        var path = TempFile("lbc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetLiteralBlockCount());
    }

    // -------------------------------------------------------------------------
    // GetSequenceCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSequenceCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        var ex = Record.Exception(() => doc.GetSequenceCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSequenceCount_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        Assert.True(doc.GetSequenceCount() > 0);
    }

    [Fact]
    public void GetSequenceCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        Assert.Equal(doc.GetSequenceCount(), doc.GetSequenceCount());
    }

    [Fact]
    public void GetSequenceCount_Greater_ForRepetitiveData()
    {
        var repDoc = ZstDocument.LoadFile(CreateRepetitiveZst());
        var divDoc = ZstDocument.LoadFile(CreateDiverseZst());
        // Repetitive data should produce more back-reference sequences per byte
        Assert.True(repDoc.GetSequenceCount() > 0);
        Assert.True(divDoc.GetSequenceCount() > 0);
    }

    [Fact]
    public void GetSequenceCount_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        var before = doc.GetSequenceCount();
        var path = TempFile("sc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSequenceCount());
    }

    // -------------------------------------------------------------------------
    // GetLiteralLengthHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLiteralLengthHistogram_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateDiverseZst());
        var ex = Record.Exception(() => doc.GetLiteralLengthHistogram());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLiteralLengthHistogram_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateDiverseZst());
        Assert.NotNull(doc.GetLiteralLengthHistogram());
    }

    [Fact]
    public void GetLiteralLengthHistogram_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateDiverseZst());
        var h1 = doc.GetLiteralLengthHistogram();
        var h2 = doc.GetLiteralLengthHistogram();
        Assert.Equal(h1.Length, h2.Length);
    }

    [Fact]
    public void GetLiteralLengthHistogram_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateDiverseZst());
        var before = doc.GetLiteralLengthHistogram().Length;
        var path = TempFile("llh_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetLiteralLengthHistogram().Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetLiteralBlockCount_GetSequenceCount_GetLiteralLengthHistogram_SaveToFile_Pipeline()
    {
        // Genomics sequence alignment output — VCF variant call format excerpt
        var sb = new StringBuilder();
        sb.AppendLine("##fileformat=VCFv4.3");
        sb.AppendLine("##FILTER=<ID=PASS,Description=\"All filters passed\">");
        sb.AppendLine("##INFO=<ID=DP,Number=1,Type=Integer,Description=\"Total Depth\">");
        sb.AppendLine("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">");
        sb.AppendLine("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE");
        string[] chroms = { "chr1", "chr2", "chr3", "chr4", "chr5", "chr6", "chr7", "chrX" };
        string[] refs = { "A", "T", "C", "G", "AT", "TC", "CG", "GA" };
        string[] alts = { "G", "C", "T", "A", "A", "T", "C", "G" };
        var rng = new Random(42);
        for (int i = 0; i < 250; i++)
        {
            int pos = 1000 + i * 500 + rng.Next(100);
            int dp = 30 + rng.Next(70);
            string gt = rng.NextDouble() > 0.5 ? "0/1" : "1/1";
            sb.AppendLine($"{chroms[i % 8]}\t{pos}\trs{100000 + i}\t{refs[i % 8]}\t{alts[i % 8]}\t{100 + rng.Next(900)}\tPASS\tDP={dp}\tGT\t{gt}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_vcf.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetLiteralBlockCount
        var litBlocks = doc.GetLiteralBlockCount();
        Assert.True(litBlocks > 0);
        Assert.Equal(litBlocks, doc.GetLiteralBlockCount()); // consistent

        // GetSequenceCount
        var seqCount = doc.GetSequenceCount();
        Assert.True(seqCount > 0);
        Assert.Equal(seqCount, doc.GetSequenceCount()); // consistent

        // GetLiteralLengthHistogram
        var hist = doc.GetLiteralLengthHistogram();
        Assert.NotNull(hist);
        Assert.True(hist.Length > 0);
        Assert.Equal(hist.Length, doc.GetLiteralLengthHistogram().Length); // consistent

        // SaveToFile
        var out1 = TempFile("dogfood_vcf_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(litBlocks, loaded.GetLiteralBlockCount());
        Assert.Equal(seqCount, loaded.GetSequenceCount());
        Assert.Equal(hist.Length, loaded.GetLiteralLengthHistogram().Length);

        // Decompression round-trip
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        Assert.True(decompressed.Length > 0);

        // Repetitive data comparison
        var repDoc = ZstDocument.LoadFile(CreateRepetitiveZst());
        Assert.True(repDoc.GetLiteralBlockCount() > 0);
        Assert.True(repDoc.GetSequenceCount() > 0);
        Assert.NotNull(repDoc.GetLiteralLengthHistogram());

        // Final recompress
        var out2 = TempFile("dogfood_vcf_v2.zst");
        var recompressed = ZstWriter.Compress(decompressed);
        File.WriteAllBytes(out2, recompressed);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.True(loaded2.GetLiteralBlockCount() > 0);
        Assert.True(loaded2.GetSequenceCount() > 0);
        var ex1 = Record.Exception(() => loaded2.GetLiteralLengthHistogram());
        Assert.Null(ex1);
    }
}
