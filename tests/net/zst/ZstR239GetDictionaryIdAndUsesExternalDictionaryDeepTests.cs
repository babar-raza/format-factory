// Tests for ZstDocument.GetDictionaryId, UsesExternalDictionary, GetDictionarySize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R239

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R239: Tests for ZstDocument.GetDictionaryId, UsesExternalDictionary, GetDictionarySize deeper.
/// GetDictionaryId(): returns the dictionary ID if an external dictionary was used (0 if none).
/// UsesExternalDictionary(): returns true if the frame uses an external compression dictionary.
/// GetDictionarySize(): returns the size in bytes of the attached or referenced dictionary (0 if none).
/// Covers: GetDictionaryId no-throw; GetDictionaryId non-negative; GetDictionaryId consistent;
/// GetDictionaryId zero for standard frame; GetDictionaryId save-load;
/// UsesExternalDictionary no-throw; UsesExternalDictionary false for standard frame; UsesExternalDictionary consistent;
/// UsesExternalDictionary save-load;
/// GetDictionarySize no-throw; GetDictionarySize non-negative; GetDictionarySize consistent;
/// dogfood Compress→GetDictionaryId→UsesExternalDictionary→GetDictionarySize→SaveToFile pipeline.
/// </summary>
public class ZstR239GetDictionaryIdAndUsesExternalDictionaryDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR239GetDictionaryIdAndUsesExternalDictionaryDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR239_" + Guid.NewGuid().ToString("N"));
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
        var content = string.Join("\n", Enumerable.Repeat(
            "DICT_TEST_STANDARD_FRAME_ALPHA_BETA_GAMMA_DELTA_EPSILON_ZETA", 100));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("standard.zst");
        File.WriteAllBytes(path, data);
        return path;
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
        // Standard frames without external dictionaries have dictionary ID = 0
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
    // UsesExternalDictionary
    // -------------------------------------------------------------------------

    [Fact]
    public void UsesExternalDictionary_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.UsesExternalDictionary());
        Assert.Null(ex);
    }

    [Fact]
    public void UsesExternalDictionary_False_ForStandardFrame()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.False(doc.UsesExternalDictionary());
    }

    [Fact]
    public void UsesExternalDictionary_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(doc.UsesExternalDictionary(), doc.UsesExternalDictionary());
    }

    [Fact]
    public void UsesExternalDictionary_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var before = doc.UsesExternalDictionary();
        var path = TempFile("ued_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.UsesExternalDictionary());
    }

    // -------------------------------------------------------------------------
    // GetDictionarySize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDictionarySize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetDictionarySize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDictionarySize_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.True(doc.GetDictionarySize() >= 0);
    }

    [Fact]
    public void GetDictionarySize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(doc.GetDictionarySize(), doc.GetDictionarySize());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDictionaryId_UsesExternalDictionary_GetDictionarySize_SaveToFile_Pipeline()
    {
        // Genomics — VCF variant call format data dictionary-free compression
        var sb = new StringBuilder();
        sb.AppendLine("##fileformat=VCFv4.3");
        sb.AppendLine("##FILTER=<ID=PASS,Description=\"All filters passed\">");
        sb.AppendLine("##INFO=<ID=DP,Number=1,Type=Integer,Description=\"Total Depth\">");
        sb.AppendLine("##INFO=<ID=AF,Number=A,Type=Float,Description=\"Allele Frequency\">");
        sb.AppendLine("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">");
        sb.AppendLine("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE");
        string[] chroms = { "chr1", "chr2", "chr3", "chr4", "chrX", "chrY" };
        string[] refs = { "A", "C", "G", "T" };
        string[] alts = { "T", "A", "C", "G" };
        var rng = new Random(20240701);
        for (int i = 0; i < 400; i++)
        {
            var chrom = chroms[i % 6];
            int pos = 100000 + i * 500 + rng.Next(0, 100);
            var r = refs[i % 4];
            var a = alts[i % 4];
            int dp = rng.Next(10, 200);
            double af = 0.1 + rng.NextDouble() * 0.8;
            string gt = rng.NextDouble() < 0.5 ? "0/1" : "1/1";
            sb.AppendLine($"{chrom}\t{pos}\trs{i + 100000}\t{r}\t{a}\t{255 - i % 50:F1}\tPASS\tDP={dp};AF={af:F3}\tGT\t{gt}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_vcf.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetDictionaryId — standard VCF compression uses no external dictionary
        var dictId = doc.GetDictionaryId();
        Assert.True(dictId >= 0);
        Assert.Equal(0, dictId); // no external dictionary
        Assert.Equal(dictId, doc.GetDictionaryId()); // consistent

        // UsesExternalDictionary — false for standard frame
        Assert.False(doc.UsesExternalDictionary());
        Assert.Equal(doc.UsesExternalDictionary(), doc.UsesExternalDictionary()); // consistent

        // GetDictionarySize
        var dictSize = doc.GetDictionarySize();
        Assert.True(dictSize >= 0);
        Assert.Equal(dictSize, doc.GetDictionarySize()); // consistent

        // Relationship: no external dictionary → dictId=0, dictSize=0
        Assert.True(!doc.UsesExternalDictionary() || dictId > 0);

        // GetMagicNumber (cross-check)
        Assert.Equal(0xFD2FB528u, (uint)doc.GetMagicNumber());

        // SaveToFile
        var out1 = TempFile("dogfood_vcf_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));

        // LoadFile and verify preserved
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(dictId, loaded.GetDictionaryId());
        Assert.Equal(doc.UsesExternalDictionary(), loaded.UsesExternalDictionary());
        Assert.Equal(dictSize, loaded.GetDictionarySize());

        // Round-trip decompression
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        var text = Encoding.UTF8.GetString(decompressed);
        Assert.Contains("VCFv4.3", text);
        Assert.Contains("chr1", text);
        Assert.Contains("rs100000", text);

        // Second compression cycle
        var recompressed = ZstWriter.Compress(decompressed);
        var out2 = TempFile("dogfood_vcf_v2.zst");
        File.WriteAllBytes(out2, recompressed);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.Equal(0, loaded2.GetDictionaryId()); // still no dictionary
        Assert.False(loaded2.UsesExternalDictionary());
        Assert.True(loaded2.GetDictionarySize() >= 0);
        var ex1 = Record.Exception(() => loaded2.GetFrameHeaderSize());
        Assert.Null(ex1);
    }
}
