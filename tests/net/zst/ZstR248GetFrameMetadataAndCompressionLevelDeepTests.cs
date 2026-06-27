// Tests for ZstDocument.GetFrameMetadata, GetCompressionLevel, GetWindowSize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R248

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R248: Tests for ZstDocument.GetFrameMetadata, GetCompressionLevel, GetWindowSize deeper.
/// GetFrameMetadata(): returns metadata about the Zstandard frame header.
/// GetCompressionLevel(): returns the compression level hint stored in the frame (or 0 if absent).
/// GetWindowSize(): returns the window size (log) used during compression.
/// Covers: GetFrameMetadata no-throw; GetFrameMetadata non-null; GetFrameMetadata consistent;
/// GetCompressionLevel no-throw; GetCompressionLevel non-negative; GetCompressionLevel consistent;
/// GetWindowSize no-throw; GetWindowSize positive; GetWindowSize consistent; GetWindowSize save-load;
/// dogfood CreateDoc→GetFrameMetadata→GetCompressionLevel→GetWindowSize pipeline.
/// </summary>
public class ZstR248GetFrameMetadataAndCompressionLevelDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR248GetFrameMetadataAndCompressionLevelDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR248_" + Guid.NewGuid().ToString("N"));
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
            "id,type,value\n1,alpha,100\n2,beta,200\n3,gamma,300\n");
        var compressed = ZstWriter.Compress(content);
        File.WriteAllBytes(path, compressed);
        return path;
    }

    private string CreateLargerZst()
    {
        var path = TempFile("larger.zst");
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < 50; i++)
            sb.Append($"RECORD:{i:D4}|payload={i * 13}|active=true|ts=2024-06-{(i % 30 + 1):D2}T12:00:00Z\n");
        var compressed = ZstWriter.Compress(System.Text.Encoding.UTF8.GetBytes(sb.ToString()));
        File.WriteAllBytes(path, compressed);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFrameMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameMetadata_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetFrameMetadata());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameMetadata_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.NotNull(doc.GetFrameMetadata());
    }

    [Fact]
    public void GetFrameMetadata_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var m1 = doc.GetFrameMetadata();
        var m2 = doc.GetFrameMetadata();
        Assert.Equal(m1, m2);
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
    public void GetCompressionLevel_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetCompressionLevel() >= 0);
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
    // GetWindowSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWindowSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetWindowSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWindowSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetWindowSize() > 0);
    }

    [Fact]
    public void GetWindowSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetWindowSize(), doc.GetWindowSize());
    }

    [Fact]
    public void GetWindowSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetWindowSize();
        var path = TempFile("ws_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetWindowSize());
    }

    [Fact]
    public void GetWindowSize_LargerFile_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateLargerZst());
        Assert.True(doc.GetWindowSize() > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFrameMetadata_GetCompressionLevel_GetWindowSize_Pipeline()
    {
        // Proteomics — LC-MS/MS mass spectrometry peptide identification results
        var path = TempFile("lcmsms_peptides.zst");
        var sb = new System.Text.StringBuilder();
        sb.Append("HEADER:LCMSMS_PEPTIDE_IDENTIFICATION FORMAT=TSV INSTRUMENT=ORBITRAP VERSION=2.1\n");
        sb.Append("scan_id\tpeptide_sequence\tcharge\tm_z_observed\tm_z_theoretical\tdelta_mass_ppm\tscore\tq_value\tprotein_accession\n");
        var rng = new Random(20240601);
        string[] proteins = { "P04637", "P38936", "Q13148", "O15350", "P10636", "Q16665", "P00533", "P42345" };
        string[] bases_aa = { "A", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "Y" };
        for (int i = 0; i < 300; i++)
        {
            var pepLen = rng.Next(7, 25);
            var pep = new System.Text.StringBuilder();
            for (int j = 0; j < pepLen; j++) pep.Append(bases_aa[rng.Next(bases_aa.Length)]);
            var charge = rng.Next(1, 5);
            var mz_obs = 400.0 + rng.NextDouble() * 1200.0;
            var delta_ppm = (rng.NextDouble() - 0.5) * 10.0;
            var mz_theo = mz_obs * (1 - delta_ppm / 1e6);
            var score = 20.0 + rng.NextDouble() * 80.0;
            var q_val = rng.NextDouble() * 0.05;
            sb.Append($"{1000 + i}\t{pep}\t{charge}\t{mz_obs:F4}\t{mz_theo:F4}\t{delta_ppm:F3}\t{score:F2}\t{q_val:F4}\t{proteins[rng.Next(proteins.Length)]}\n");
        }
        sb.Append("FOOTER:TOTAL_PEPTIDES=300 INSTRUMENT_ID=OT-QExactive-001\n");

        var content = System.Text.Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(content);
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > doc.CompressedSize);

        // GetFrameMetadata
        var meta = doc.GetFrameMetadata();
        Assert.NotNull(meta);
        Assert.Equal(meta, doc.GetFrameMetadata()); // consistent

        // GetCompressionLevel
        var level = doc.GetCompressionLevel();
        Assert.True(level >= 0);
        Assert.Equal(level, doc.GetCompressionLevel()); // consistent

        // GetWindowSize
        var windowSize = doc.GetWindowSize();
        Assert.True(windowSize > 0);
        Assert.Equal(windowSize, doc.GetWindowSize()); // consistent

        // Additional frame properties
        var magic = doc.GetMagicNumber();
        Assert.Equal(0xFD2FB528u, (uint)magic);

        var dictId = doc.GetDictionaryId();
        Assert.True(dictId >= 0);

        // SearchForBytes
        var headerPattern = System.Text.Encoding.ASCII.GetBytes("HEADER:LCMSMS");
        Assert.True(doc.SearchForBytes(headerPattern) >= 0);

        var peptidePattern = System.Text.Encoding.ASCII.GetBytes("scan_id");
        Assert.True(doc.SearchForBytes(peptidePattern) >= 0);

        var absentPattern = new byte[] { 0xDE, 0xAD, 0xBE, 0xEF };
        Assert.True(doc.SearchForBytes(absentPattern) < 0);

        // SaveToFile
        var outPath = TempFile("lcmsms_peptides_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(meta, loaded.GetFrameMetadata());
        Assert.Equal(level, loaded.GetCompressionLevel());
        Assert.Equal(windowSize, loaded.GetWindowSize());
        Assert.Equal(doc.CompressedSize, loaded.CompressedSize);
        Assert.Equal(magic, loaded.GetMagicNumber());
        Assert.True(loaded.SearchForBytes(headerPattern) >= 0);

        // Ratio and frame count
        Assert.True(doc.CompressionRatio > 1.0);
        Assert.True(doc.FrameCount >= 1);
    }
}
