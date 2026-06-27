// Tests for ZstDocument.GetDictionaryId, GetDictionaryData deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R252

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R252: Tests for ZstDocument.GetDictionaryId, GetDictionaryData deeper.
/// GetDictionaryId(): returns the dictionary ID embedded in the frame header (0 if none).
/// GetDictionaryData(): returns the raw bytes of the embedded dictionary reference, or empty if none.
/// Covers: GetDictionaryId no-throw; GetDictionaryId non-negative; GetDictionaryId consistent;
/// GetDictionaryId save-load; GetDictionaryData no-throw; GetDictionaryData non-null;
/// GetDictionaryData consistent; GetDictionaryData save-load;
/// GetDictionaryId zero for standard frame; GetDictionaryData empty for standard frame;
/// dogfood CreateDoc→GetDictionaryId→GetDictionaryData→SaveToFile pipeline.
/// </summary>
public class ZstR252GetDictionaryIdAndDictionaryDataDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR252GetDictionaryIdAndDictionaryDataDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR252_" + Guid.NewGuid().ToString("N"));
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
        // Standard zstd frame without dictionary
        var content = "Standard zstd frame without dictionary. " +
                      string.Join(" ", System.Linq.Enumerable.Repeat("Regulatory submission document content.", 80));
        var path = TempFile("standard.zst");
        var writer = new ZstWriter();
        writer.CompressToFile(System.Text.Encoding.UTF8.GetBytes(content), path);
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
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        // Standard frames without dictionary have ID = 0
        Assert.Equal(0, doc.GetDictionaryId());
    }

    [Fact]
    public void GetDictionaryId_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var before = doc.GetDictionaryId();
        var path = TempFile("dict_id_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDictionaryId());
    }

    // -------------------------------------------------------------------------
    // GetDictionaryData
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDictionaryData_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetDictionaryData());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDictionaryData_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.NotNull(doc.GetDictionaryData());
    }

    [Fact]
    public void GetDictionaryData_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var d1 = doc.GetDictionaryData();
        var d2 = doc.GetDictionaryData();
        Assert.Equal(d1.Length, d2.Length);
    }

    [Fact]
    public void GetDictionaryData_Empty_ForStandardFrame()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        // No embedded dictionary in a standard frame
        Assert.Empty(doc.GetDictionaryData());
    }

    [Fact]
    public void GetDictionaryData_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var before = doc.GetDictionaryData();
        var path = TempFile("dict_data_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before.Length, loaded.GetDictionaryData().Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDictionaryId_GetDictionaryData_Pipeline()
    {
        // Bioinformatics archival — GenBank flat file batch compression for INSDC submission
        // Simulating compression of nucleotide sequence records for EMBL-EBI data exchange
        var rng = new Random(20241001);
        char[] bases = { 'A', 'T', 'G', 'C' };

        var recordBuilder = new System.Text.StringBuilder();
        recordBuilder.AppendLine("LOCUS       SYNTHETIC_OPERON_001     6847 bp    DNA     linear   SYN 01-OCT-2024");
        recordBuilder.AppendLine("DEFINITION  Synthetic operon construct for metabolic engineering of Corynebacterium");
        recordBuilder.AppendLine("            glutamicum ATCC 13032 — L-lysine biosynthesis pathway optimisation.");
        recordBuilder.AppendLine("ACCESSION   SY000001");
        recordBuilder.AppendLine("VERSION     SY000001.1");
        recordBuilder.AppendLine("KEYWORDS    synthetic biology; metabolic engineering; L-lysine; flux optimisation.");
        recordBuilder.AppendLine("SOURCE      synthetic construct");
        recordBuilder.AppendLine("  ORGANISM  synthetic construct");
        recordBuilder.AppendLine("            other sequences; artificial sequences; vectors.");
        recordBuilder.AppendLine("FEATURES             Location/Qualifiers");
        recordBuilder.AppendLine("     gene            1..6847");
        recordBuilder.AppendLine("                     /gene=\"lys_operon_v3\"");
        recordBuilder.AppendLine("                     /note=\"codon-optimised for C. glutamicum expression\"");
        recordBuilder.AppendLine("     CDS             1..1245");
        recordBuilder.AppendLine("                     /gene=\"asd\"");
        recordBuilder.AppendLine("                     /product=\"aspartate-semialdehyde dehydrogenase\"");
        recordBuilder.AppendLine("                     /EC_number=\"1.2.1.11\"");
        recordBuilder.AppendLine("     CDS             1252..2487");
        recordBuilder.AppendLine("                     /gene=\"dapA\"");
        recordBuilder.AppendLine("                     /product=\"4-hydroxy-tetrahydrodipicolinate synthase\"");
        recordBuilder.AppendLine("                     /EC_number=\"4.3.3.7\"");
        recordBuilder.AppendLine("     CDS             2490..3734");
        recordBuilder.AppendLine("                     /gene=\"dapB\"");
        recordBuilder.AppendLine("                     /product=\"4-hydroxy-tetrahydrodipicolinate reductase\"");
        recordBuilder.AppendLine("                     /EC_number=\"1.17.1.8\"");
        recordBuilder.AppendLine("     CDS             3740..5014");
        recordBuilder.AppendLine("                     /gene=\"lysC\"");
        recordBuilder.AppendLine("                     /product=\"aspartate kinase\"");
        recordBuilder.AppendLine("                     /note=\"feedback-resistant variant T311I/S301F\"");
        recordBuilder.AppendLine("     CDS             5021..6847");
        recordBuilder.AppendLine("                     /gene=\"lysA\"");
        recordBuilder.AppendLine("                     /product=\"diaminopimelate decarboxylase\"");
        recordBuilder.AppendLine("                     /EC_number=\"4.1.1.20\"");
        recordBuilder.AppendLine("ORIGIN");
        // Generate synthetic sequence
        var seqChars = new char[6847];
        for (int i = 0; i < seqChars.Length; i++)
            seqChars[i] = bases[rng.Next(4)];
        var seq = new string(seqChars);
        // Format as GenBank 60-char lines
        for (int pos = 0; pos < seq.Length; pos += 60)
        {
            int len = Math.Min(60, seq.Length - pos);
            recordBuilder.AppendLine($"       {pos + 1,6} {seq.Substring(pos, len)}");
        }
        recordBuilder.AppendLine("//");

        var payload = System.Text.Encoding.UTF8.GetBytes(recordBuilder.ToString());

        // Compress
        var path = TempFile("genbank_lys_operon.zst");
        var writer = new ZstWriter();
        writer.CompressToFile(payload, path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > doc.GetCompressedSize());

        // GetDictionaryId
        var dictId = doc.GetDictionaryId();
        Assert.True(dictId >= 0);
        Assert.Equal(0, dictId); // standard frame, no dict
        Assert.Equal(dictId, doc.GetDictionaryId()); // consistent

        // GetDictionaryData
        var dictData = doc.GetDictionaryData();
        Assert.NotNull(dictData);
        Assert.Empty(dictData); // no embedded dictionary
        Assert.Equal(dictData.Length, doc.GetDictionaryData().Length); // consistent

        // Decompression round-trip
        var decompressed = doc.Decompress();
        Assert.NotNull(decompressed);
        Assert.Equal(payload.Length, decompressed.Length);

        // Frame metadata
        Assert.True(doc.GetFrameCount() >= 1);
        Assert.Equal(doc.GetDictionaryId(), doc.GetDictionaryId()); // idempotent

        // SaveToFile
        var path2 = TempFile("genbank_lys_operon_copy.zst");
        doc.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        Assert.True(new FileInfo(path2).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(path2);
        Assert.Equal(dictId, loaded.GetDictionaryId());
        Assert.Equal(dictData.Length, loaded.GetDictionaryData().Length);
        Assert.Equal(doc.GetCompressedSize(), loaded.GetCompressedSize());
        Assert.Equal(doc.GetDecompressedSize(), loaded.GetDecompressedSize());

        // Additional records — simulate batch compression of 5 sequence records
        for (int rec = 0; rec < 5; rec++)
        {
            var miniSeq = new char[500 + rec * 100];
            for (int i = 0; i < miniSeq.Length; i++) miniSeq[i] = bases[rng.Next(4)];
            var miniPayload = System.Text.Encoding.UTF8.GetBytes($"LOCUS SEQ_{rec:D3}\n" + new string(miniSeq));
            var miniPath = TempFile($"seq_{rec:D3}.zst");
            writer.CompressToFile(miniPayload, miniPath);
            var miniDoc = ZstDocument.LoadFile(miniPath);
            Assert.Equal(0, miniDoc.GetDictionaryId());
            Assert.Empty(miniDoc.GetDictionaryData());
            Assert.True(miniDoc.GetCompressedSize() > 0);
        }
    }
}
