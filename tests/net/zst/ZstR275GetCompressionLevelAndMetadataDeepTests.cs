// Tests for ZstDocument.GetCompressionLevel, GetMetadata deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R275

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R275: Tests for ZstDocument.GetCompressionLevel, GetMetadata deeper.
/// GetCompressionLevel(): returns a string or integer representing the compression level used.
/// GetMetadata(): returns a metadata dictionary or string with archive properties.
/// Covers: GetCompressionLevel no-throw; GetCompressionLevel non-null;
/// GetCompressionLevel consistent; GetCompressionLevel save-load;
/// GetMetadata no-throw; GetMetadata non-null; GetMetadata non-empty;
/// GetMetadata consistent; GetMetadata save-load; dogfood pipeline.
/// </summary>
public class ZstR275GetCompressionLevelAndMetadataDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR275GetCompressionLevelAndMetadataDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR275_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateOptimalZst(string name = "optimal.zst")
    {
        var path = TempFile(name);
        var src = Encoding.UTF8.GetBytes(
            string.Concat(Enumerable.Repeat("Optimal compression test data payload. ", 100)));
        using var fs = File.Create(path);
        using var zs = new ZLibStream(fs, CompressionLevel.Optimal, leaveOpen: true);
        zs.Write(src, 0, src.Length);
        return path;
    }

    private string CreateFastestZst(string name = "fastest.zst")
    {
        var path = TempFile(name);
        var src = Encoding.UTF8.GetBytes(
            string.Concat(Enumerable.Repeat("Fastest compression test data payload. ", 100)));
        using var fs = File.Create(path);
        using var zs = new ZLibStream(fs, CompressionLevel.Fastest, leaveOpen: true);
        zs.Write(src, 0, src.Length);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetCompressionLevel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionLevel_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateOptimalZst());
        var ex = Record.Exception(() => doc.GetCompressionLevel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionLevel_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateOptimalZst());
        Assert.NotNull(doc.GetCompressionLevel());
    }

    [Fact]
    public void GetCompressionLevel_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateOptimalZst());
        Assert.Equal(doc.GetCompressionLevel(), doc.GetCompressionLevel());
    }

    [Fact]
    public void GetCompressionLevel_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateOptimalZst());
        var before = doc.GetCompressionLevel();
        var path = TempFile("cl_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).GetCompressionLevel());
    }

    // -------------------------------------------------------------------------
    // GetMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetadata_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateOptimalZst());
        var ex = Record.Exception(() => doc.GetMetadata());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMetadata_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateOptimalZst());
        Assert.NotNull(doc.GetMetadata());
    }

    [Fact]
    public void GetMetadata_NonEmpty()
    {
        var doc = ZstDocument.LoadFile(CreateOptimalZst());
        Assert.NotEmpty(doc.GetMetadata());
    }

    [Fact]
    public void GetMetadata_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateOptimalZst());
        Assert.Equal(doc.GetMetadata(), doc.GetMetadata());
    }

    [Fact]
    public void GetMetadata_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateOptimalZst());
        var before = doc.GetMetadata();
        var path = TempFile("md_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).GetMetadata());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCompressionLevel_GetMetadata_Pipeline()
    {
        // Legal — HMCTS / MoJ: Court Proceedings Data Archive
        // Compressed case record exports from Crown Court Digital case management system
        // Compression level and metadata validate archive provenance for subject access requests

        // Scenario 1: Crown Court case registry (optimal compression)
        var path1 = TempFile("hmcts_crown_court_registry_2024.zst");
        {
            var sb = new StringBuilder();
            sb.AppendLine("# HMCTS Crown Court Digital Case Registry — Q3 2024");
            sb.AppendLine("# Export Date: 2024-10-01 | Classification: OFFICIAL-SENSITIVE");
            sb.AppendLine("# System: Common Platform | Jurisdiction: England and Wales");
            sb.AppendLine("case_id,defendant_ref,offence_code,plea,verdict,sentence_category,sentence_length_months,court_centre,sitting_date,judge_ref");
            var rng = new Random(20240701);
            string[] pleas = { "Guilty", "Not_Guilty", "Not_Guilty", "Guilty", "Guilty" };
            string[] verdicts = { "Convicted", "Acquitted", "Convicted", "Convicted", "Acquitted" };
            string[] offCodes = { "THEFT01", "FRAUD02", "ASSAULT03", "DRUG04", "CYBER05", "FRAUD06" };
            string[] courts = { "CCRC_Leeds", "CCRC_Manchester", "CCRC_Birmingham", "CCRC_Bristol", "CCRC_London_SE" };
            for (int i = 0; i < 150; i++)
            {
                string plea = pleas[rng.Next(pleas.Length)];
                string verdict = plea == "Guilty" ? "Convicted" : verdicts[rng.Next(verdicts.Length)];
                int sentence = verdict == "Convicted" ? rng.Next(3, 120) : 0;
                sb.AppendLine($"CC{2024000 + i},{rng.Next(100000, 999999)},{offCodes[rng.Next(offCodes.Length)]},{plea},{verdict},Custodial,{sentence},{courts[rng.Next(courts.Length)]},2024-{rng.Next(1, 10):D2}-{rng.Next(1, 28):D2},J{rng.Next(1000, 9999)}");
            }
            var raw = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(path1);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal, leaveOpen: true);
            zs.Write(raw, 0, raw.Length);
        }

        // Scenario 2: Magistrates' Court fixed penalty registry (fastest compression)
        var path2 = TempFile("hmcts_mags_fp_registry_2024.zst");
        {
            var sb = new StringBuilder();
            sb.AppendLine("# HMCTS Magistrates Fixed Penalty Registry — Q3 2024");
            sb.AppendLine("penalty_ref,offence_type,penalty_amount_gbp,payment_status,payment_date,enforcement_status");
            var rng = new Random(20240702);
            string[] offenceTypes = { "Speed_Camera_NIP", "Red_Light_Camera", "Bus_Lane_PCN", "ANPR_NoInsurance", "Littering" };
            string[] paymentStatuses = { "Paid", "Paid", "Paid", "Outstanding", "Enforcement" };
            for (int i = 0; i < 200; i++)
            {
                string pStatus = paymentStatuses[rng.Next(paymentStatuses.Length)];
                string pDate = pStatus == "Paid" ? $"2024-{rng.Next(1, 10):D2}-{rng.Next(1, 28):D2}" : "";
                double amount = new[] { 100.0, 200.0, 130.0, 300.0, 150.0 }[rng.Next(5)];
                sb.AppendLine($"FP{2024000000 + i},{offenceTypes[rng.Next(offenceTypes.Length)]},{amount:F2},{pStatus},{pDate},{(pStatus == "Enforcement" ? "Warrant_Issued" : "None")}");
            }
            var raw = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(path2);
            using var zs = new ZLibStream(fs, CompressionLevel.Fastest, leaveOpen: true);
            zs.Write(raw, 0, raw.Length);
        }

        var doc1 = ZstDocument.LoadFile(path1);
        var doc2 = ZstDocument.LoadFile(path2);

        // Compression levels
        var cl1 = doc1.GetCompressionLevel();
        var cl2 = doc2.GetCompressionLevel();
        Assert.NotNull(cl1);
        Assert.NotNull(cl2);
        Assert.Equal(cl1, doc1.GetCompressionLevel()); // consistent
        Assert.Equal(cl2, doc2.GetCompressionLevel()); // consistent

        // Metadata
        var md1 = doc1.GetMetadata();
        var md2 = doc2.GetMetadata();
        Assert.NotNull(md1);
        Assert.NotNull(md2);
        Assert.NotEmpty(md1);
        Assert.NotEmpty(md2);
        Assert.Equal(md1, doc1.GetMetadata()); // consistent
        Assert.Equal(md2, doc2.GetMetadata()); // consistent

        // Compressed sizes are positive
        Assert.True(doc1.GetCompressedSize() > 0);
        Assert.True(doc2.GetCompressedSize() > 0);

        // Compression ratios
        Assert.True(doc1.GetCompressionRatio() >= 1.0);
        Assert.True(doc2.GetCompressionRatio() >= 1.0);

        // SaveToFile
        var out1 = TempFile("hmcts_crown_out.zst");
        doc1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loaded1 = ZstDocument.LoadFile(out1);
        Assert.Equal(cl1, loaded1.GetCompressionLevel());
        Assert.Equal(md1, loaded1.GetMetadata());

        var out2 = TempFile("hmcts_mags_out.zst");
        doc2.SaveToFile(out2);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.Equal(cl2, loaded2.GetCompressionLevel());
        Assert.Equal(md2, loaded2.GetMetadata());

        var ex1 = Record.Exception(() => loaded1.GetCompressionLevel());
        var ex2 = Record.Exception(() => loaded2.GetMetadata());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
