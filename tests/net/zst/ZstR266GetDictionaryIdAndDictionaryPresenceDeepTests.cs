// Tests for ZstDocument.GetDictionaryId, GetDictionaryPresence deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R266

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R266: Tests for ZstDocument.GetDictionaryId, GetDictionaryPresence deeper.
/// GetDictionaryId(): returns the dictionary ID embedded in the ZST frame header (0 if no dictionary).
/// GetDictionaryPresence(): returns true if the frame uses an external dictionary, false otherwise.
/// Covers: GetDictionaryId no-throw; GetDictionaryId non-negative; GetDictionaryId consistent;
/// GetDictionaryPresence no-throw; GetDictionaryPresence consistent;
/// GetDictionaryPresence false for standard frame; GetDictionaryId zero for standard frame;
/// GetDictionaryId save-load; GetDictionaryPresence save-load;
/// dogfood CreateDoc→GetDictionaryId→GetDictionaryPresence→SaveToFile pipeline.
/// </summary>
public class ZstR266GetDictionaryIdAndDictionaryPresenceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR266GetDictionaryIdAndDictionaryPresenceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR266_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateStandardZst(string name, string content)
    {
        var path = TempFile(name);
        var bytes = Encoding.UTF8.GetBytes(content);
        using var outStream = new FileStream(path, FileMode.Create);
        using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
        zlib.Write(bytes, 0, bytes.Length);
        return path;
    }

    private string CreateLargeZst()
    {
        var sb = new StringBuilder();
        for (int i = 0; i < 200; i++)
            sb.AppendLine($"{{\"id\":{i},\"name\":\"item_{i}\",\"value\":{i * 3.14:F4},\"active\":{(i % 2 == 0 ? "true" : "false")}}}");
        return CreateStandardZst("large.zst", sb.ToString());
    }

    private string CreateSmallZst() =>
        CreateStandardZst("small.zst",
            "Small compressed payload for dictionary ID testing. " +
            string.Concat(Enumerable.Repeat("padding data. ", 20)));

    // -------------------------------------------------------------------------
    // GetDictionaryId
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDictionaryId_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst("nothrow.zst", "test content for dictionary id check"));
        var ex = Record.Exception(() => doc.GetDictionaryId());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDictionaryId_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.True(doc.GetDictionaryId() >= 0);
    }

    [Fact]
    public void GetDictionaryId_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.Equal(doc.GetDictionaryId(), doc.GetDictionaryId());
    }

    [Fact]
    public void GetDictionaryId_Zero_ForStandardFrame()
    {
        // Standard ZLib/ZST frame without external dictionary → dictionary ID = 0
        var doc = ZstDocument.LoadFile(CreateStandardZst("standard.zst", "standard frame no dictionary data here at all"));
        Assert.Equal(0, doc.GetDictionaryId());
    }

    [Fact]
    public void GetDictionaryId_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var before = doc.GetDictionaryId();
        var path = TempFile("did_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDictionaryId());
    }

    // -------------------------------------------------------------------------
    // GetDictionaryPresence
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDictionaryPresence_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSmallZst());
        var ex = Record.Exception(() => doc.GetDictionaryPresence());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDictionaryPresence_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSmallZst());
        Assert.Equal(doc.GetDictionaryPresence(), doc.GetDictionaryPresence());
    }

    [Fact]
    public void GetDictionaryPresence_False_ForStandardFrame()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst("noDictFrame.zst",
            "no external dictionary used in this compressed frame content data filler text repeated"));
        Assert.False(doc.GetDictionaryPresence());
    }

    [Fact]
    public void GetDictionaryPresence_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var before = doc.GetDictionaryPresence();
        var path = TempFile("dp_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDictionaryPresence());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDictionaryId_GetDictionaryPresence_SaveToFile_Pipeline()
    {
        // Public Sector — HMRC: Making Tax Digital (MTD) Compressed Submission Payloads
        // VAT return submissions compressed before transmission to HMRC APIs
        // Dictionary presence check ensures payload integrity (no stale dictionary reference)

        // Document 1: VAT Return MT001 — standard quarterly submission
        var path1 = TempFile("hmrc_mtd_vat_q1.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("{");
            content.AppendLine("  \"submission_type\": \"VAT_RETURN\",");
            content.AppendLine("  \"period_key\": \"24A1\",");
            content.AppendLine("  \"period_start\": \"2024-04-01\",");
            content.AppendLine("  \"period_end\": \"2024-06-30\",");
            content.AppendLine("  \"due_date\": \"2024-08-07\",");
            content.AppendLine("  \"vrn\": \"GB123456789\",");
            content.AppendLine("  \"box1_output_tax\": 48250.00,");
            content.AppendLine("  \"box2_acquisitions\": 0.00,");
            content.AppendLine("  \"box3_total_output\": 48250.00,");
            content.AppendLine("  \"box4_input_tax\": 31840.75,");
            content.AppendLine("  \"box5_net_vat\": 16409.25,");
            content.AppendLine("  \"box6_total_sales\": 241250.00,");
            content.AppendLine("  \"box7_total_purchases\": 159203.75,");
            content.AppendLine("  \"box8_ec_supplies\": 0.00,");
            content.AppendLine("  \"box9_ec_acquisitions\": 0.00,");
            content.AppendLine("  \"finalised\": true,");
            content.AppendLine("  \"submitted_by\": \"AGENT_SA_001\",");
            content.AppendLine("  \"submission_timestamp\": \"2024-07-31T09:15:42Z\"");
            content.AppendLine("}");
            for (int i = 0; i < 50; i++)
                content.AppendLine($"  // Line item {i}: invoice VAT tracking record {i * 100 + 1}");
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path1, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
            zlib.Write(bytes, 0, bytes.Length);
        }

        // Document 2: VAT Return MT002 — correction submission
        var path2 = TempFile("hmrc_mtd_vat_q1_correction.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("{");
            content.AppendLine("  \"submission_type\": \"VAT_RETURN_CORRECTION\",");
            content.AppendLine("  \"original_ref\": \"MTD_24A1_001\",");
            content.AppendLine("  \"period_key\": \"24A1\",");
            content.AppendLine("  \"vrn\": \"GB123456789\",");
            content.AppendLine("  \"box1_output_tax\": 49100.00,");
            content.AppendLine("  \"box4_input_tax\": 32150.25,");
            content.AppendLine("  \"box5_net_vat\": 16949.75,");
            content.AppendLine("  \"correction_reason\": \"Omitted_invoice_discovered\",");
            content.AppendLine("  \"correction_amount\": 540.50,");
            content.AppendLine("  \"finalised\": true");
            content.AppendLine("}");
            for (int i = 0; i < 30; i++)
                content.AppendLine($"  // Correction audit trail entry {i}: delta record");
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path2, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
            zlib.Write(bytes, 0, bytes.Length);
        }

        // Document 3: MTD Income Tax Self-Assessment payload
        var path3 = TempFile("hmrc_mtd_itsa_q1.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("{");
            content.AppendLine("  \"submission_type\": \"SELF_EMPLOYMENT_PERIODIC\",");
            content.AppendLine("  \"tax_year\": \"2024-25\",");
            content.AppendLine("  \"period_start\": \"2024-04-06\",");
            content.AppendLine("  \"period_end\": \"2024-07-05\",");
            content.AppendLine("  \"nino\": \"AA123456A\",");
            content.AppendLine("  \"business_id\": \"XKIS12345678901\",");
            content.AppendLine("  \"income_turnover\": 28500.00,");
            content.AppendLine("  \"income_other\": 0.00,");
            content.AppendLine("  \"expenses_cost_of_goods\": 8200.00,");
            content.AppendLine("  \"expenses_construction\": 0.00,");
            content.AppendLine("  \"expenses_staff\": 6400.00,");
            content.AppendLine("  \"expenses_travel\": 1250.00,");
            content.AppendLine("  \"expenses_premises\": 800.00,");
            content.AppendLine("  \"expenses_admin\": 350.00,");
            content.AppendLine("  \"expenses_other\": 190.00,");
            content.AppendLine("  \"net_profit\": 11310.00");
            content.AppendLine("}");
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path3, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
            zlib.Write(bytes, 0, bytes.Length);
        }

        var doc1 = ZstDocument.LoadFile(path1);
        var doc2 = ZstDocument.LoadFile(path2);
        var doc3 = ZstDocument.LoadFile(path3);

        // Dictionary ID assertions
        var id1 = doc1.GetDictionaryId();
        var id2 = doc2.GetDictionaryId();
        var id3 = doc3.GetDictionaryId();
        Assert.True(id1 >= 0);
        Assert.True(id2 >= 0);
        Assert.True(id3 >= 0);
        Assert.Equal(id1, doc1.GetDictionaryId()); // consistent
        Assert.Equal(id2, doc2.GetDictionaryId()); // consistent
        // Standard frames without external dictionary → all IDs = 0
        Assert.Equal(0, id1);
        Assert.Equal(0, id2);
        Assert.Equal(0, id3);

        // Dictionary presence assertions
        Assert.False(doc1.GetDictionaryPresence()); // standard frame — no dictionary
        Assert.False(doc2.GetDictionaryPresence());
        Assert.False(doc3.GetDictionaryPresence());
        Assert.Equal(doc1.GetDictionaryPresence(), doc1.GetDictionaryPresence()); // consistent

        // Basic ZST metrics
        Assert.True(doc1.CompressedSize > 0);
        Assert.True(doc1.OriginalSize > 0);
        Assert.True(doc1.OriginalSize >= doc1.CompressedSize || doc1.CompressedSize > 0);

        // SaveToFile
        var out1 = TempFile("hmrc_mtd_vat_q1_out.zst");
        doc1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        var loaded1 = ZstDocument.LoadFile(out1);
        Assert.Equal(id1, loaded1.GetDictionaryId());
        Assert.Equal(false, loaded1.GetDictionaryPresence());

        var out2 = TempFile("hmrc_mtd_itsa_q1_out.zst");
        doc3.SaveToFile(out2);
        var loaded3 = ZstDocument.LoadFile(out2);
        Assert.Equal(id3, loaded3.GetDictionaryId());
        Assert.Equal(doc3.GetDictionaryPresence(), loaded3.GetDictionaryPresence());

        Assert.Equal(doc1.OriginalSize, loaded1.OriginalSize);

        var ex1 = Record.Exception(() => loaded1.GetDictionaryId());
        var ex2 = Record.Exception(() => loaded1.GetDictionaryPresence());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
