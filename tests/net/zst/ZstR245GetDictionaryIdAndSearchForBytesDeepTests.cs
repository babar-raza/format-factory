// Tests for ZstDocument.GetDictionaryId, SearchForBytes, GetMagicNumber deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R245

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R245: Tests for ZstDocument.GetDictionaryId, SearchForBytes, GetMagicNumber deeper.
/// GetDictionaryId(): returns the dictionary ID used for compression, or 0 if none.
/// SearchForBytes(pattern): returns the position of the first occurrence in decompressed data.
/// GetMagicNumber(): returns the Zstandard frame magic number (0xFD2FB528).
/// Covers: GetDictionaryId no-throw; GetDictionaryId non-negative; GetDictionaryId consistent;
/// GetDictionaryId zero for standard frame;
/// SearchForBytes no-throw; SearchForBytes returns -1 for absent pattern; SearchForBytes consistent;
/// SearchForBytes non-negative for present pattern;
/// GetMagicNumber no-throw; GetMagicNumber equals expected constant; GetMagicNumber consistent;
/// GetMagicNumber save-load;
/// dogfood CreateDoc→GetDictionaryId→SearchForBytes→GetMagicNumber pipeline.
/// </summary>
public class ZstR245GetDictionaryIdAndSearchForBytesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR245GetDictionaryIdAndSearchForBytesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR245_" + Guid.NewGuid().ToString("N"));
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
        var content = System.Text.Encoding.UTF8.GetBytes(
            "name,value,category\nAlpha,100,A\nBeta,200,B\nGamma,300,C\nDelta,400,D\n");
        var compressed = ZstWriter.Compress(content);
        File.WriteAllBytes(path, compressed);
        return path;
    }

    private string CreateLargerZst()
    {
        var path = TempFile("larger.zst");
        var sb = new System.Text.StringBuilder();
        sb.Append("HEADER:START\n");
        for (int i = 0; i < 40; i++)
            sb.Append($"RECORD:{i:D4}|value={i * 7}|status=ACTIVE|timestamp=2024-01-{(i % 28 + 1):D2}\n");
        sb.Append("FOOTER:END\n");
        var content = System.Text.Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(content);
        File.WriteAllBytes(path, compressed);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetDictionaryId
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDictionaryId_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetDictionaryId());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDictionaryId_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetDictionaryId() >= 0);
    }

    [Fact]
    public void GetDictionaryId_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetDictionaryId(), doc.GetDictionaryId());
    }

    [Fact]
    public void GetDictionaryId_Zero_For_Standard_Frame()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        // Standard frames without explicit dictionary should return 0
        Assert.Equal(0, doc.GetDictionaryId());
    }

    // -------------------------------------------------------------------------
    // SearchForBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchForBytes_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.SearchForBytes(new byte[] { 0x41, 0x6C, 0x70 })); // "Alp"
        Assert.Null(ex);
    }

    [Fact]
    public void SearchForBytes_Returns_Negative_For_Absent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var result = doc.SearchForBytes(new byte[] { 0xFF, 0xFE, 0xFD, 0xFC });
        Assert.True(result < 0);
    }

    [Fact]
    public void SearchForBytes_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var pattern = new byte[] { 0x42 }; // 'B'
        Assert.Equal(doc.SearchForBytes(pattern), doc.SearchForBytes(pattern));
    }

    [Fact]
    public void SearchForBytes_NonNegative_For_Present()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        // "name" is in the header
        var pattern = System.Text.Encoding.ASCII.GetBytes("name");
        Assert.True(doc.SearchForBytes(pattern) >= 0);
    }

    // -------------------------------------------------------------------------
    // GetMagicNumber
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMagicNumber_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetMagicNumber());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMagicNumber_Equals_Expected()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        // Zstandard magic number is 0xFD2FB528 = 4247762216
        Assert.Equal(0xFD2FB528u, (uint)doc.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetMagicNumber(), doc.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetMagicNumber();
        var path = TempFile("mn_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMagicNumber());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDictionaryId_SearchForBytes_GetMagicNumber_Pipeline()
    {
        // Genomics — FASTQ read quality score compression for WGS sequencing pipeline
        var path = TempFile("fastq_reads.zst");
        var sb = new System.Text.StringBuilder();
        sb.Append("@READ_HEADER FORMAT=FASTQ INSTRUMENT=NOVASEQ VERSION=1.4\n");
        var rng = new Random(20240401);
        string[] bases = { "A", "C", "G", "T" };
        for (int i = 0; i < 200; i++)
        {
            // Sequence read ID
            sb.Append($"@SEQ_READ_{i:D6} lane=1 tile={(i % 20 + 1):D4} x={(rng.Next(1000, 9999))} y={(rng.Next(1000, 9999))}\n");
            // Sequence (100 bases)
            var seq = new System.Text.StringBuilder();
            for (int b = 0; b < 100; b++) seq.Append(bases[rng.Next(4)]);
            sb.Append(seq.ToString() + "\n");
            sb.Append("+\n");
            // Quality scores (Phred+33, ASCII 33-73)
            var qual = new System.Text.StringBuilder();
            for (int b = 0; b < 100; b++) qual.Append((char)(rng.Next(33, 74)));
            sb.Append(qual.ToString() + "\n");
        }
        sb.Append("@FOOTER TOTAL_READS=200 GENOME=GRCh38\n");
        var content = System.Text.Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(content);
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > doc.CompressedSize);

        // GetDictionaryId
        var dictId = doc.GetDictionaryId();
        Assert.True(dictId >= 0);
        Assert.Equal(dictId, doc.GetDictionaryId()); // consistent

        // GetMagicNumber
        var magic = doc.GetMagicNumber();
        Assert.Equal(0xFD2FB528u, (uint)magic);
        Assert.Equal(magic, doc.GetMagicNumber()); // consistent

        // SearchForBytes — known header pattern
        var headerPattern = System.Text.Encoding.ASCII.GetBytes("@READ_HEADER");
        var headerPos = doc.SearchForBytes(headerPattern);
        Assert.True(headerPos >= 0);
        Assert.Equal(headerPos, doc.SearchForBytes(headerPattern)); // consistent

        // SearchForBytes — SEQ_READ pattern
        var readPattern = System.Text.Encoding.ASCII.GetBytes("@SEQ_READ_");
        Assert.True(doc.SearchForBytes(readPattern) >= 0);

        // SearchForBytes — absent pattern
        var absentPattern = new byte[] { 0xFF, 0xEE, 0xDD, 0xCC };
        Assert.True(doc.SearchForBytes(absentPattern) < 0);

        // SaveToFile
        var outPath = TempFile("fastq_reads_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(dictId, loaded.GetDictionaryId());
        Assert.Equal(magic, loaded.GetMagicNumber());
        Assert.True(loaded.SearchForBytes(headerPattern) >= 0);
        Assert.Equal(doc.CompressedSize, loaded.CompressedSize);

        // Additional stats
        var ratio = doc.CompressionRatio;
        Assert.True(ratio > 1.0);
        var frameCount = doc.FrameCount;
        Assert.True(frameCount >= 1);
    }
}
