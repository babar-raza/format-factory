// Tests for ZstDocument.GetCompressionLevel, GetCompressionSpeed deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R268

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R268: Tests for ZstDocument.GetCompressionLevel, GetCompressionSpeed deeper.
/// GetCompressionLevel(): returns the estimated compression level used (1–22 for zstd, or 0 if unknown).
/// GetCompressionSpeed(): returns a string descriptor of compression speed ("fast", "normal", "slow", or "unknown").
/// Covers: GetCompressionLevel no-throw; GetCompressionLevel non-negative; GetCompressionLevel consistent;
/// GetCompressionLevel save-load; GetCompressionSpeed no-throw; GetCompressionSpeed non-null;
/// GetCompressionSpeed consistent; GetCompressionSpeed save-load;
/// dogfood CreateDoc→GetCompressionLevel→GetCompressionSpeed→SaveToFile pipeline.
/// </summary>
public class ZstR268GetCompressionLevelAndCompressionSpeedDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR268GetCompressionLevelAndCompressionSpeedDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR268_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateZst(string name, string content, CompressionLevel level = CompressionLevel.Optimal)
    {
        var path = TempFile(name);
        var bytes = Encoding.UTF8.GetBytes(content);
        using var outStream = new FileStream(path, FileMode.Create);
        using var zlib = new ZLibStream(outStream, level);
        zlib.Write(bytes, 0, bytes.Length);
        return path;
    }

    private string CreateLargeZst()
    {
        var sb = new StringBuilder();
        for (int i = 0; i < 500; i++)
            sb.AppendLine($"Line {i:D4}: data_field_a={i * 1.41:F3} data_field_b={i * 3.14:F4} tag=batch_{i / 50}");
        return CreateZst("large.zst", sb.ToString());
    }

    private string CreateSmallZst() =>
        CreateZst("small.zst", "Compact payload for compression level and speed tests. " +
                  string.Concat(Enumerable.Repeat("padding ", 20)));

    private string CreateFastZst() =>
        CreateZst("fast.zst", new string('A', 2000) + new string('B', 2000), CompressionLevel.Fastest);

    // -------------------------------------------------------------------------
    // GetCompressionLevel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionLevel_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var ex = Record.Exception(() => doc.GetCompressionLevel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionLevel_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.True(doc.GetCompressionLevel() >= 0);
    }

    [Fact]
    public void GetCompressionLevel_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.Equal(doc.GetCompressionLevel(), doc.GetCompressionLevel());
    }

    [Fact]
    public void GetCompressionLevel_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var before = doc.GetCompressionLevel();
        var path = TempFile("cl_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionLevel());
    }

    // -------------------------------------------------------------------------
    // GetCompressionSpeed
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionSpeed_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSmallZst());
        var ex = Record.Exception(() => doc.GetCompressionSpeed());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionSpeed_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateSmallZst());
        Assert.NotNull(doc.GetCompressionSpeed());
    }

    [Fact]
    public void GetCompressionSpeed_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSmallZst());
        Assert.Equal(doc.GetCompressionSpeed(), doc.GetCompressionSpeed());
    }

    [Fact]
    public void GetCompressionSpeed_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var before = doc.GetCompressionSpeed();
        var path = TempFile("cs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionSpeed());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCompressionLevel_GetCompressionSpeed_SaveToFile_Pipeline()
    {
        // Technology — GOV.UK Notify: Bulk Notification Archive
        // Compressed notification payloads from the GOV.UK Notify service
        // Compression level and speed profiling for archive storage optimisation

        // Archive 1: High-volume bulk SMS notifications (optimal compression for long-term archive)
        var path1 = TempFile("govuk_notify_sms_archive_2024_q3.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("GOV.UK Notify — Bulk SMS Archive Q3 2024");
            content.AppendLine("Service: HMRC Tax Self-Assessment Reminders");
            content.AppendLine("Reference: SA_BULK_2024_Q3");
            for (int i = 0; i < 200; i++)
            {
                string phone = $"+447{700000000 + i}";
                string status = i % 10 == 0 ? "failed" : i % 3 == 0 ? "pending" : "delivered";
                content.AppendLine($"MSG{i:D6}|{phone}|Your Self Assessment tax return is due by 31 January 2025. You owe £{(i * 47 + 150):F2}. Reference: SA{2024000000 + i}.|{status}|2024-10-{(i % 30 + 1):D2}");
            }
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path1, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
            zlib.Write(bytes, 0, bytes.Length);
        }

        // Archive 2: Real-time email notifications (fastest compression for low-latency delivery)
        var path2 = TempFile("govuk_notify_email_realtime_2024_q3.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("GOV.UK Notify — Real-time Email Archive Q3 2024");
            content.AppendLine("Service: DWP Universal Credit Claimant Updates");
            for (int i = 0; i < 150; i++)
            {
                content.AppendLine($"EMAIL{i:D6}|claimant{i}@example.gov.uk|Your Universal Credit payment of £{(658 + i % 200):F2} has been processed and will be credited to your account on {2024 + i / 366}-{(i % 12 + 1):D2}-{(i % 28 + 1):D2}.|delivered");
            }
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path2, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Fastest);
            zlib.Write(bytes, 0, bytes.Length);
        }

        // Archive 3: Letter PDF metadata (small, mixed records)
        var path3 = TempFile("govuk_notify_letter_metadata_2024_q3.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("{");
            content.AppendLine("  \"archive\": \"GOV.UK Notify Letter Metadata Q3 2024\",");
            content.AppendLine("  \"service\": \"DWP Pension Credit Annual Uprating Letters\",");
            content.AppendLine("  \"count\": 12483,");
            content.AppendLine("  \"total_pages\": 24966,");
            content.AppendLine("  \"print_provider\": \"DVLA_Swansea_Print\",");
            content.AppendLine("  \"dispatch_date\": \"2024-09-30\",");
            content.AppendLine("  \"cost_pence\": 38721.00");
            content.AppendLine("}");
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path3, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.SmallestSize);
            zlib.Write(bytes, 0, bytes.Length);
        }

        var doc1 = ZstDocument.LoadFile(path1);
        var doc2 = ZstDocument.LoadFile(path2);
        var doc3 = ZstDocument.LoadFile(path3);

        // Compression level
        var cl1 = doc1.GetCompressionLevel();
        var cl2 = doc2.GetCompressionLevel();
        var cl3 = doc3.GetCompressionLevel();
        Assert.True(cl1 >= 0);
        Assert.True(cl2 >= 0);
        Assert.True(cl3 >= 0);
        Assert.Equal(cl1, doc1.GetCompressionLevel()); // consistent
        Assert.Equal(cl2, doc2.GetCompressionLevel()); // consistent

        // Compression speed
        var cs1 = doc1.GetCompressionSpeed();
        var cs2 = doc2.GetCompressionSpeed();
        var cs3 = doc3.GetCompressionSpeed();
        Assert.NotNull(cs1);
        Assert.NotNull(cs2);
        Assert.NotNull(cs3);
        Assert.Equal(cs1, doc1.GetCompressionSpeed()); // consistent
        Assert.Equal(cs2, doc2.GetCompressionSpeed()); // consistent
        Assert.Equal(cs3, doc3.GetCompressionSpeed()); // consistent

        // Basic ZST metrics
        Assert.True(doc1.CompressedSize > 0);
        Assert.True(doc2.CompressedSize > 0);
        Assert.True(doc1.OriginalSize > 0);
        Assert.True(doc2.OriginalSize > 0);

        // SaveToFile
        var out1 = TempFile("govuk_notify_sms_out.zst");
        doc1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        var loaded1 = ZstDocument.LoadFile(out1);
        Assert.Equal(cl1, loaded1.GetCompressionLevel());
        Assert.Equal(cs1, loaded1.GetCompressionSpeed());

        var out2 = TempFile("govuk_notify_email_out.zst");
        doc2.SaveToFile(out2);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.Equal(cl2, loaded2.GetCompressionLevel());
        Assert.Equal(cs2, loaded2.GetCompressionSpeed());

        Assert.Equal(doc1.CompressedSize, loaded1.CompressedSize);
        Assert.Equal(doc2.OriginalSize, loaded2.OriginalSize);

        var ex1 = Record.Exception(() => loaded1.GetCompressionLevel());
        var ex2 = Record.Exception(() => loaded1.GetCompressionSpeed());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
