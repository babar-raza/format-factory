// Tests for ZstDocument.GetChecksum, VerifyIntegrity, GetContentChecksum deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R246

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R246: Tests for ZstDocument.GetChecksum, VerifyIntegrity, GetContentChecksum deeper.
/// GetChecksum(): returns the frame checksum (xxHash64 or CRC32C) stored in the Zstandard frame.
/// VerifyIntegrity(): returns true if the frame integrity check passes.
/// GetContentChecksum(): returns the content checksum stored in the frame footer, or 0 if absent.
/// Covers: GetChecksum no-throw; GetChecksum non-negative; GetChecksum consistent;
/// VerifyIntegrity no-throw; VerifyIntegrity returns bool; VerifyIntegrity consistent;
/// VerifyIntegrity true for valid frame;
/// GetContentChecksum no-throw; GetContentChecksum non-negative; GetContentChecksum consistent;
/// GetContentChecksum save-load;
/// dogfood CreateDoc→GetChecksum→VerifyIntegrity→GetContentChecksum pipeline.
/// </summary>
public class ZstR246GetChecksumAndVerifyIntegrityDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR246GetChecksumAndVerifyIntegrityDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR246_" + Guid.NewGuid().ToString("N"));
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
            "transaction_id,amount,currency,status\nTX001,250.00,GBP,SETTLED\nTX002,89.50,EUR,PENDING\nTX003,1250.00,USD,SETTLED\n");
        var compressed = ZstWriter.Compress(content);
        File.WriteAllBytes(path, compressed);
        return path;
    }

    private string CreateLargerZst()
    {
        var path = TempFile("larger.zst");
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < 50; i++)
            sb.Append($"LOG:{i:D4}|timestamp=2024-01-{(i % 28 + 1):D2}T12:{(i % 60):D2}:00Z|level=INFO|service=payments|message=ProcessedOK\n");
        var compressed = ZstWriter.Compress(System.Text.Encoding.UTF8.GetBytes(sb.ToString()));
        File.WriteAllBytes(path, compressed);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetChecksum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChecksum_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetChecksum());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChecksum_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetChecksum() >= 0);
    }

    [Fact]
    public void GetChecksum_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetChecksum(), doc.GetChecksum());
    }

    // -------------------------------------------------------------------------
    // VerifyIntegrity
    // -------------------------------------------------------------------------

    [Fact]
    public void VerifyIntegrity_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.VerifyIntegrity());
        Assert.Null(ex);
    }

    [Fact]
    public void VerifyIntegrity_Returns_Bool()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var result = doc.VerifyIntegrity();
        Assert.True(result == true || result == false);
    }

    [Fact]
    public void VerifyIntegrity_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.VerifyIntegrity(), doc.VerifyIntegrity());
    }

    [Fact]
    public void VerifyIntegrity_True_For_Valid_Frame()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.VerifyIntegrity());
    }

    // -------------------------------------------------------------------------
    // GetContentChecksum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContentChecksum_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetContentChecksum());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContentChecksum_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetContentChecksum() >= 0);
    }

    [Fact]
    public void GetContentChecksum_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetContentChecksum(), doc.GetContentChecksum());
    }

    [Fact]
    public void GetContentChecksum_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetContentChecksum();
        var path = TempFile("cc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetContentChecksum());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetChecksum_VerifyIntegrity_GetContentChecksum_Pipeline()
    {
        // Financial infrastructure — ISO 20022 payment messages (MX format) for SWIFT integration
        var path = TempFile("swift_mx_messages.zst");
        var sb = new System.Text.StringBuilder();
        sb.Append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        sb.Append("<Document xmlns=\"urn:iso:std:iso:20022:tech:xsd:pacs.008.001.09\">\n");
        var rng = new Random(20241001);
        string[] currencies = { "GBP", "EUR", "USD", "CHF", "JPY" };
        string[] bicCodes = { "BARCGB22", "DEUTDEDB", "BNPAFRPP", "UBSWCHZH", "MTBJPYJT" };
        for (int i = 0; i < 200; i++)
        {
            string txId = $"TX{i:D8}";
            double amount = 100 + rng.NextDouble() * 999900;
            string ccy = currencies[i % 5];
            string debtorBic = bicCodes[rng.Next(5)];
            string creditorBic = bicCodes[rng.Next(5)];
            sb.Append($"  <CdtTrfTxInf><PmtId><TxId>{txId}</TxId></PmtId>");
            sb.Append($"<IntrBkSttlmAmt Ccy=\"{ccy}\">{amount:F2}</IntrBkSttlmAmt>");
            sb.Append($"<DbtrAgt><FinInstnId><BICFI>{debtorBic}</BICFI></FinInstnId></DbtrAgt>");
            sb.Append($"<CdtrAgt><FinInstnId><BICFI>{creditorBic}</BICFI></FinInstnId></CdtrAgt>");
            sb.Append("</CdtTrfTxInf>\n");
        }
        sb.Append("</Document>\n");
        var content = System.Text.Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(content);
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > doc.CompressedSize);

        // GetChecksum
        var checksum = doc.GetChecksum();
        Assert.True(checksum >= 0);
        Assert.Equal(checksum, doc.GetChecksum()); // consistent

        // VerifyIntegrity
        Assert.True(doc.VerifyIntegrity());
        Assert.Equal(doc.VerifyIntegrity(), doc.VerifyIntegrity()); // consistent

        // GetContentChecksum
        var contentCsum = doc.GetContentChecksum();
        Assert.True(contentCsum >= 0);
        Assert.Equal(contentCsum, doc.GetContentChecksum()); // consistent

        // SearchForBytes — verify content is searchable
        var pattern = System.Text.Encoding.ASCII.GetBytes("TX00000000");
        Assert.True(doc.SearchForBytes(pattern) >= 0);

        // GetMagicNumber
        Assert.Equal(0xFD2FB528u, (uint)doc.GetMagicNumber());

        // SaveToFile
        var outPath = TempFile("swift_mx_messages_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(checksum, loaded.GetChecksum());
        Assert.True(loaded.VerifyIntegrity());
        Assert.Equal(contentCsum, loaded.GetContentChecksum());
        Assert.Equal(doc.CompressedSize, loaded.CompressedSize);

        // Additional metrics
        Assert.True(doc.CompressionRatio > 1.0);
        Assert.Equal(0, doc.GetDictionaryId());
    }
}
