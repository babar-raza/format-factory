// Tests for ZstDocument.GetOriginalSize, GetCompressionRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R264

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R264: Tests for ZstDocument.GetOriginalSize, GetCompressionRatio deeper.
/// GetOriginalSize(): returns the decompressed/original data size in bytes.
/// GetCompressionRatio(): returns OriginalSize / CompressedSize (ratio ≥ 1 for compressible data).
/// Covers: GetOriginalSize no-throw; GetOriginalSize positive; GetOriginalSize consistent;
/// GetOriginalSize save-load; GetCompressionRatio no-throw; GetCompressionRatio positive;
/// GetCompressionRatio consistent; GetCompressionRatio save-load;
/// GetCompressionRatio ge one for compressible; GetOriginalSize ge CompressedSize for compressible;
/// dogfood CreateDoc→GetOriginalSize→GetCompressionRatio→SaveToFile pipeline.
/// </summary>
public class ZstR264GetOriginalSizeAndCompressionRatioDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR264GetOriginalSizeAndCompressionRatioDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR264_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateRepetitivZst(string tag = "a")
    {
        var path = TempFile($"repetitive_{tag}.zst");
        var text = "AAAA BBBB CCCC DDDD EEEE 12345 67890 ";
        var source = Encoding.UTF8.GetBytes(string.Concat(Enumerable.Repeat(text, 200)));
        using var fs = File.Create(path);
        using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
        zs.Write(source, 0, source.Length);
        return path;
    }

    private string CreateSampleZst()
    {
        var path = TempFile("sample.zst");
        var text = "The Judicial Appointments Commission selects candidates for judicial office in courts and tribunals in England and Wales. ";
        var source = Encoding.UTF8.GetBytes(string.Concat(Enumerable.Repeat(text, 50)));
        using var fs = File.Create(path);
        using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
        zs.Write(source, 0, source.Length);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetOriginalSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOriginalSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetOriginalSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetOriginalSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetOriginalSize() > 0);
    }

    [Fact]
    public void GetOriginalSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetOriginalSize(), doc.GetOriginalSize());
    }

    [Fact]
    public void GetOriginalSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetOriginalSize();
        var path = TempFile("os_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetOriginalSize());
    }

    [Fact]
    public void GetOriginalSize_Ge_CompressedSize_ForCompressible()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitivZst());
        Assert.True(doc.GetOriginalSize() >= doc.CompressedSize);
    }

    // -------------------------------------------------------------------------
    // GetCompressionRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionRatio_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetCompressionRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionRatio_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetCompressionRatio() > 0.0);
    }

    [Fact]
    public void GetCompressionRatio_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetCompressionRatio(), doc.GetCompressionRatio());
    }

    [Fact]
    public void GetCompressionRatio_Ge_One_ForCompressible()
    {
        var doc = ZstDocument.LoadFile(CreateRepetitivZst());
        Assert.True(doc.GetCompressionRatio() >= 1.0);
    }

    [Fact]
    public void GetCompressionRatio_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetCompressionRatio();
        var path = TempFile("cr_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionRatio(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetOriginalSize_GetCompressionRatio_SaveToFile_Pipeline()
    {
        // Judiciary — Courts and Tribunals Service: Case Management System Export
        // Compressed bundles of case records for long-term archival — compression ratio audit
        var rng = new Random(20240901);

        // File 1: Structured case records (text, highly compressible)
        var pathCases = TempFile("hmcts_case_records.zst");
        {
            var sb = new StringBuilder();
            sb.AppendLine("case_ref,court,judge,claimant,defendant,issue_date,hearing_date,status,claim_value_gbp,outcome");
            string[] courts = { "Royal Courts of Justice", "Manchester Civil Justice Centre",
                                "Birmingham Civil Justice Centre", "Leeds Combined Court Centre" };
            string[] statuses = { "Filed", "Listed", "Adjourned", "Settled", "Judgment" };
            string[] outcomes = { "Pending", "Claimant Wins", "Defendant Wins", "Settled", "Discontinued" };
            for (int i = 0; i < 400; i++)
            {
                string caseRef = $"QB-2024-{i:D6}";
                string court = courts[rng.Next(courts.Length)];
                string judge = $"HHJ {(char)('A' + rng.Next(26))}. {(char)('A' + rng.Next(26))}. Smith";
                double claimVal = Math.Round(5000 + rng.NextDouble() * 995000, 2);
                string status = statuses[rng.Next(statuses.Length)];
                string outcome = outcomes[rng.Next(outcomes.Length)];
                sb.AppendLine($"{caseRef},{court},{judge},Claimant {i},Defendant {i},2024-01-{(i % 28) + 1:D2},2025-03-{(i % 28) + 1:D2},{status},{claimVal},{outcome}");
            }
            var source = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(pathCases);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
            zs.Write(source, 0, source.Length);
        }

        // File 2: Judgment text corpus (prose, moderately compressible)
        var pathJudgments = TempFile("hmcts_judgment_extracts.zst");
        {
            var sb = new StringBuilder();
            string[] openings = {
                "This is a claim for damages arising from an alleged breach of contract.",
                "The Claimant seeks summary judgment pursuant to CPR Part 24.",
                "This matter comes before the court on the Defendant's application to strike out.",
                "The parties have been unable to agree the terms of the consent order.",
                "The court is required to determine the preliminary issue of limitation."
            };
            for (int i = 0; i < 300; i++)
            {
                sb.AppendLine($"[{2024000 + i}] EWCA Civ {i + 100}");
                sb.AppendLine($"IN THE COURT OF APPEAL (CIVIL DIVISION)");
                sb.AppendLine(openings[i % openings.Length]);
                sb.AppendLine("Having considered the submissions of counsel for both parties, and having read the trial judge's detailed findings of fact, this court is of the view that the appeal must be dismissed for the following reasons.");
                sb.AppendLine();
            }
            var source = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(pathJudgments);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
            zs.Write(source, 0, source.Length);
        }

        var docCases = ZstDocument.LoadFile(pathCases);
        var docJudgments = ZstDocument.LoadFile(pathJudgments);

        // GetOriginalSize
        var osCases = docCases.GetOriginalSize();
        var osJudgments = docJudgments.GetOriginalSize();
        Assert.True(osCases > 0);
        Assert.True(osJudgments > 0);
        Assert.Equal(osCases, docCases.GetOriginalSize()); // consistent
        Assert.Equal(osJudgments, docJudgments.GetOriginalSize()); // consistent

        // Original size >= compressed size for structured text
        Assert.True(osCases >= docCases.CompressedSize);
        Assert.True(osJudgments >= docJudgments.CompressedSize);

        // GetCompressionRatio
        var crCases = docCases.GetCompressionRatio();
        var crJudgments = docJudgments.GetCompressionRatio();
        Assert.True(crCases > 0);
        Assert.True(crJudgments > 0);
        Assert.True(crCases >= 1.0); // structured text compresses well
        Assert.True(crJudgments >= 1.0);
        Assert.Equal(crCases, docCases.GetCompressionRatio()); // consistent
        Assert.Equal(crJudgments, docJudgments.GetCompressionRatio());

        // SaveToFile
        var outCases = TempFile("hmcts_cases_out.zst");
        docCases.SaveToFile(outCases);
        Assert.True(File.Exists(outCases));
        var loadedCases = ZstDocument.LoadFile(outCases);
        Assert.Equal(osCases, loadedCases.GetOriginalSize());
        Assert.Equal(crCases, loadedCases.GetCompressionRatio(), precision: 6);

        var outJudgments = TempFile("hmcts_judgments_out.zst");
        docJudgments.SaveToFile(outJudgments);
        var loadedJudgments = ZstDocument.LoadFile(outJudgments);
        Assert.Equal(osJudgments, loadedJudgments.GetOriginalSize());
        Assert.Equal(crJudgments, loadedJudgments.GetCompressionRatio(), precision: 6);

        var ex1 = Record.Exception(() => loadedCases.GetOriginalSize());
        var ex2 = Record.Exception(() => loadedCases.GetCompressionRatio());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
