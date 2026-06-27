// Tests for ZstDocument.GetContentHash, VerifyIntegrity, GetCompressionRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R236

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R236: Tests for ZstDocument.GetContentHash, VerifyIntegrity, GetCompressionRatio deeper.
/// GetContentHash(): returns a hash string of the decompressed content for integrity verification.
/// VerifyIntegrity(): returns true if the compressed data is structurally valid.
/// GetCompressionRatio(): returns the ratio of decompressed to compressed size.
/// Covers: GetContentHash no-throw; GetContentHash non-null; GetContentHash consistent;
/// GetContentHash stable across save-load;
/// VerifyIntegrity no-throw; VerifyIntegrity true for valid frame; VerifyIntegrity consistent;
/// VerifyIntegrity save-load;
/// GetCompressionRatio no-throw; GetCompressionRatio geq 1; GetCompressionRatio consistent;
/// GetCompressionRatio higher for repetitive content; GetCompressionRatio save-load;
/// dogfood Compress→GetContentHash→VerifyIntegrity→GetCompressionRatio→SaveToFile pipeline.
/// </summary>
public class ZstR236GetContentHashAndVerifyIntegrityDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR236GetContentHashAndVerifyIntegrityDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR236_" + Guid.NewGuid().ToString("N"));
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
            "REPETITIVE_DATA_BLOCK_AAA_BBB_CCC_DDD_EEE_FFF_GGG_HHH_III_JJJ", 200));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("repetitive.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    private string CreateRandomishZst()
    {
        var sb = new StringBuilder();
        var rng = new Random(99999);
        for (int i = 0; i < 300; i++)
            sb.AppendLine($"{Guid.NewGuid():N},{rng.Next(0, 1000000)},{rng.NextDouble():F8},{rng.Next(0, 256):X2}");
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(sb.ToString()));
        var path = TempFile("randomish.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetContentHash
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContentHash_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        var ex = Record.Exception(() => doc.GetContentHash());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContentHash_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        Assert.NotNull(doc.GetContentHash());
    }

    [Fact]
    public void GetContentHash_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        Assert.Equal(doc.GetContentHash(), doc.GetContentHash());
    }

    [Fact]
    public void GetContentHash_Stable_SaveLoad()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        var before = doc.GetContentHash();
        var path = TempFile("hash_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetContentHash());
    }

    // -------------------------------------------------------------------------
    // VerifyIntegrity
    // -------------------------------------------------------------------------

    [Fact]
    public void VerifyIntegrity_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        var ex = Record.Exception(() => doc.VerifyIntegrity());
        Assert.Null(ex);
    }

    [Fact]
    public void VerifyIntegrity_True_ForValidFrame()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        Assert.True(doc.VerifyIntegrity());
    }

    [Fact]
    public void VerifyIntegrity_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        Assert.Equal(doc.VerifyIntegrity(), doc.VerifyIntegrity());
    }

    [Fact]
    public void VerifyIntegrity_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        var before = doc.VerifyIntegrity();
        var path = TempFile("vi_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.VerifyIntegrity());
    }

    // -------------------------------------------------------------------------
    // GetCompressionRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionRatio_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        var ex = Record.Exception(() => doc.GetCompressionRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionRatio_Geq_One()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        Assert.True(doc.GetCompressionRatio() >= 1.0);
    }

    [Fact]
    public void GetCompressionRatio_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        Assert.Equal(doc.GetCompressionRatio(), doc.GetCompressionRatio(), precision: 4);
    }

    [Fact]
    public void GetCompressionRatio_Higher_ForRepetitive()
    {
        var repDoc = ZstDocument.LoadFile(CreateRepetitiveZst());
        var rndDoc = ZstDocument.LoadFile(CreateRandomishZst());
        // Repetitive content compresses better than pseudo-random
        Assert.True(repDoc.GetCompressionRatio() > rndDoc.GetCompressionRatio());
    }

    [Fact]
    public void GetCompressionRatio_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitiveZst());
        var before = doc.GetCompressionRatio();
        var path = TempFile("cr_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionRatio(), precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetContentHash_VerifyIntegrity_GetCompressionRatio_SaveToFile_Pipeline()
    {
        // Bioinformatics — whole genome sequencing FASTQ quality score stream compression
        var sb = new StringBuilder();
        sb.AppendLine("@HEADER_FORMAT_LINE_WGS_HG38_REFERENCE_GENOME_SEQUENCING_RUN_2026");
        string[] bases = { "A", "T", "G", "C" };
        string qualChars = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJ";
        var rng = new Random(77777);
        for (int i = 0; i < 200; i++)
        {
            // Read ID
            sb.AppendLine($"@READ_{i:D6}_{(i % 3 == 0 ? "FORWARD" : "REVERSE")}_STRAND_CHR{(i % 22) + 1}:{i * 150}-{i * 150 + 149}");
            // Sequence — mostly repetitive patterns with mutations
            var seq = new StringBuilder(150);
            for (int j = 0; j < 150; j++)
                seq.Append(bases[(j % 4 + (rng.Next(0, 10) == 0 ? rng.Next(0, 4) : 0)) % 4]);
            sb.AppendLine(seq.ToString());
            sb.AppendLine("+");
            // Quality scores — mostly high quality (IIIII) with some low spots
            var qual = new StringBuilder(150);
            for (int j = 0; j < 150; j++)
                qual.Append(qualChars[rng.Next(30, qualChars.Length)]);
            sb.AppendLine(qual.ToString());
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_wgs.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetContentHash
        var hash = doc.GetContentHash();
        Assert.NotNull(hash);
        Assert.NotEmpty(hash);
        Assert.Equal(hash, doc.GetContentHash()); // consistent

        // VerifyIntegrity
        Assert.True(doc.VerifyIntegrity());
        Assert.Equal(doc.VerifyIntegrity(), doc.VerifyIntegrity()); // consistent

        // GetCompressionRatio
        var ratio = doc.GetCompressionRatio();
        Assert.True(ratio >= 1.0);
        Assert.Equal(ratio, doc.GetCompressionRatio(), precision: 4); // consistent

        // Highly repetitive content should compress well
        var repContent = Encoding.UTF8.GetBytes(string.Join("", Enumerable.Repeat("ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC", 1000)));
        var repCompressed = ZstWriter.Compress(repContent);
        var repPath = TempFile("dogfood_repetitive.zst");
        File.WriteAllBytes(repPath, repCompressed);
        var repDoc = ZstDocument.LoadFile(repPath);
        Assert.True(repDoc.GetCompressionRatio() > ratio); // DNA repeat compresses better

        // SaveToFile
        var out1 = TempFile("dogfood_wgs_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify preservation
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(hash, loaded.GetContentHash());
        Assert.True(loaded.VerifyIntegrity());
        Assert.Equal(ratio, loaded.GetCompressionRatio(), precision: 4);

        // Decompression round-trip integrity
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        Assert.Equal(raw.Length, decompressed.Length);
        var reText = Encoding.UTF8.GetString(decompressed);
        Assert.Contains("READ_000000", reText);
        Assert.Contains("WGS_HG38", reText);

        // Recompress and verify
        var out2 = TempFile("dogfood_wgs_v2.zst");
        File.WriteAllBytes(out2, ZstWriter.Compress(decompressed));
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.True(loaded2.VerifyIntegrity());
        Assert.True(loaded2.GetCompressionRatio() >= 1.0);
        var ex1 = Record.Exception(() => loaded2.GetContentHash());
        var ex2 = Record.Exception(() => loaded2.GetCompressionRatio());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
