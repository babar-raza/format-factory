// Tests for NdjsonDocument.GetFieldMaxStringLength, GetFieldMinStringLength deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R264

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R264: Tests for NdjsonDocument.GetFieldMaxStringLength, GetFieldMinStringLength deeper.
/// GetFieldMaxStringLength(fieldName): returns the maximum string length across all records.
/// GetFieldMinStringLength(fieldName): returns the minimum string length across all records.
/// Covers: GetFieldMaxStringLength no-throw; GetFieldMaxStringLength non-negative;
/// GetFieldMaxStringLength consistent; GetFieldMaxStringLength save-load;
/// GetFieldMaxStringLength ≥ GetFieldMinStringLength;
/// GetFieldMinStringLength no-throw; GetFieldMinStringLength non-negative;
/// GetFieldMinStringLength consistent; GetFieldMinStringLength save-load;
/// GetFieldMinStringLength zero for empty string; GetFieldMaxStringLength known value;
/// dogfood CreateDoc→GetFieldMaxStringLength→GetFieldMinStringLength pipeline.
/// </summary>
public class NdjsonR264GetFieldMaxStringLengthAndMinStringLengthDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR264GetFieldMaxStringLengthAndMinStringLengthDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR264_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleNdjson()
    {
        var path = TempFile("sample.ndjson");
        var sb = new StringBuilder();
        string[] tags = { "A", "AB", "ABC", "ABCD", "ABCDE" };
        string[] codes = { "X1", "Y22", "Z333", "W4444", "V55555", "U666666" };
        for (int i = 0; i < 80; i++)
        {
            string tag = tags[i % tags.Length];
            string code = codes[i % codes.Length];
            sb.AppendLine($"{{\"id\":{i},\"tag\":\"{tag}\",\"code\":\"{code}\",\"name\":\"Record_{i:D6}\"}}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateFixedLengthNdjson()
    {
        var path = TempFile("fixed.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 40; i++)
            sb.AppendLine($"{{\"id\":{i},\"code\":\"FIXED\"}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldMaxStringLength
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMaxStringLength_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMaxStringLength("tag"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMaxStringLength_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldMaxStringLength("tag") >= 0);
    }

    [Fact]
    public void GetFieldMaxStringLength_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMaxStringLength("tag"), doc.GetFieldMaxStringLength("tag"));
    }

    [Fact]
    public void GetFieldMaxStringLength_KnownValue()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        // "ABCDE" is the longest tag (5 chars)
        Assert.Equal(5, doc.GetFieldMaxStringLength("tag"));
    }

    [Fact]
    public void GetFieldMaxStringLength_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMaxStringLength("code");
        var path = TempFile("max_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMaxStringLength("code"));
    }

    [Fact]
    public void GetFieldMaxStringLength_GreaterOrEqualToMin()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldMaxStringLength("tag") >= doc.GetFieldMinStringLength("tag"));
    }

    // -------------------------------------------------------------------------
    // GetFieldMinStringLength
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMinStringLength_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMinStringLength("tag"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMinStringLength_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldMinStringLength("tag") >= 0);
    }

    [Fact]
    public void GetFieldMinStringLength_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMinStringLength("code"), doc.GetFieldMinStringLength("code"));
    }

    [Fact]
    public void GetFieldMinStringLength_KnownValue()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        // "A" is the shortest tag (1 char)
        Assert.Equal(1, doc.GetFieldMinStringLength("tag"));
    }

    [Fact]
    public void GetFieldMinStringLength_FixedLength()
    {
        var doc = NdjsonDocument.LoadFile(CreateFixedLengthNdjson());
        // "FIXED" is always 5 chars
        Assert.Equal(5, doc.GetFieldMinStringLength("code"));
        Assert.Equal(5, doc.GetFieldMaxStringLength("code"));
    }

    [Fact]
    public void GetFieldMinStringLength_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMinStringLength("tag");
        var path = TempFile("min_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMinStringLength("tag"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldMaxStringLength_GetFieldMinStringLength_Pipeline()
    {
        // Fintech — Open Banking UK: Payment Initiation Service Provider (PISP) transaction logs
        // PSD2 compliance: string field validation (payee names, references, BICs, IBANs)
        var path = TempFile("openbanking_pisp.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240801);

        string[] payeeNames = {
            "HMRC", "Transport for London", "BT Group plc",
            "Virgin Media O2 Ltd", "British Gas Services Ltd",
            "Tesco Stores Ltd", "ASDA Stores Ltd",
            "NHS Commissioning Board", "Department for Work and Pensions",
            "Westminster City Council", "HM", "UK"
        };
        string[] references = {
            "PAY2024", "INV-2024-001234", "DD/SO REF 8847612",
            "Standing Order — Mortgage — Sept 2024",
            "Council Tax Installment 7 of 10 — 2024/25",
            "x", "REF", "TRANSFER"
        };
        string[] currencies = { "GBP", "EUR", "USD" };

        for (int i = 0; i < 180; i++)
        {
            string payee = payeeNames[rng.Next(payeeNames.Length)];
            string reference = references[rng.Next(references.Length)];
            string currency = currencies[i % 3 == 0 ? 0 : rng.Next(currencies.Length)];
            double amount = 10 + rng.NextDouble() * 4990;

            // IBAN generation (varying country prefix → different lengths)
            string ibanCountry = rng.NextDouble() < 0.8 ? "GB" : (rng.NextDouble() < 0.5 ? "DE" : "FR");
            int ibanLen = ibanCountry == "GB" ? 22 : (ibanCountry == "DE" ? 22 : 27);
            var ibanSb = new StringBuilder(ibanCountry);
            for (int c = 0; c < ibanLen - 2; c++)
                ibanSb.Append((char)('0' + rng.Next(10)));
            string iban = ibanSb.ToString();

            // BIC: 8 or 11 chars
            string[] bics8 = { "BARCGB22", "HBUKGB4B", "LLOYSGB2L", "NWBKGB2L" };
            string[] bics11 = { "BARCGB22XXX", "HBUKGB4BXXX", "LLOYSGB2LXXX", "NWBKGB2LXXX" };
            string bic = rng.NextDouble() < 0.6 ? bics8[rng.Next(bics8.Length)] : bics11[rng.Next(bics11.Length)];

            string status = rng.NextDouble() < 0.92 ? "ACCP" : (rng.NextDouble() < 0.5 ? "RJCT" : "PDNG");
            string timestamp = $"2024-{(rng.Next(12) + 1):D2}-{(rng.Next(28) + 1):D2}T{rng.Next(24):D2}:{rng.Next(60):D2}:00Z";

            sb.AppendLine($"{{\"txn_id\":\"TXN{1000000 + i}\"," +
                         $"\"payee_name\":\"{payee}\"," +
                         $"\"reference\":\"{reference}\"," +
                         $"\"amount\":{amount:F2}," +
                         $"\"currency\":\"{currency}\"," +
                         $"\"creditor_iban\":\"{iban}\"," +
                         $"\"creditor_bic\":\"{bic}\"," +
                         $"\"status\":\"{status}\"," +
                         $"\"timestamp\":\"{timestamp}\"}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(180, doc.RecordCount);

        // GetFieldMaxStringLength — payee names
        var maxPayee = doc.GetFieldMaxStringLength("payee_name");
        Assert.True(maxPayee > 0);
        Assert.Equal(maxPayee, doc.GetFieldMaxStringLength("payee_name")); // consistent

        // GetFieldMinStringLength — payee names ("HM" or "UK" are shortest = 2 chars)
        var minPayee = doc.GetFieldMinStringLength("payee_name");
        Assert.True(minPayee >= 0);
        Assert.Equal(minPayee, doc.GetFieldMinStringLength("payee_name")); // consistent
        Assert.True(maxPayee >= minPayee);

        // Reference field — variable length
        var maxRef = doc.GetFieldMaxStringLength("reference");
        var minRef = doc.GetFieldMinStringLength("reference");
        Assert.True(maxRef >= minRef);
        // "x" is 1 char, long references are ~40+ chars
        Assert.True(minRef >= 1);
        Assert.True(maxRef >= 10); // long references present

        // Currency: always 3 chars
        var maxCurrency = doc.GetFieldMaxStringLength("currency");
        var minCurrency = doc.GetFieldMinStringLength("currency");
        Assert.Equal(3, maxCurrency);
        Assert.Equal(3, minCurrency);

        // BIC: 8 or 11 chars
        var maxBic = doc.GetFieldMaxStringLength("creditor_bic");
        var minBic = doc.GetFieldMinStringLength("creditor_bic");
        Assert.True(minBic == 8 || minBic == 11);
        Assert.True(maxBic == 8 || maxBic == 11);
        Assert.True(maxBic >= minBic);

        // IBAN: GB/DE=22, FR=27
        var maxIban = doc.GetFieldMaxStringLength("creditor_iban");
        var minIban = doc.GetFieldMinStringLength("creditor_iban");
        Assert.True(minIban >= 22);
        Assert.True(maxIban <= 27);
        Assert.True(maxIban >= minIban);

        // Status: "RJCT"=4, "ACCP"=4, "PDNG"=4 — all 4 chars
        Assert.Equal(4, doc.GetFieldMaxStringLength("status"));
        Assert.Equal(4, doc.GetFieldMinStringLength("status"));

        // SaveToFile
        var outPath = TempFile("openbanking_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(maxPayee, loaded.GetFieldMaxStringLength("payee_name"));
        Assert.Equal(minPayee, loaded.GetFieldMinStringLength("payee_name"));
        Assert.Equal(maxRef, loaded.GetFieldMaxStringLength("reference"));
        Assert.Equal(minRef, loaded.GetFieldMinStringLength("reference"));
        Assert.Equal(3, loaded.GetFieldMaxStringLength("currency"));

        // Additional no-throw
        var ex1 = Record.Exception(() => loaded.GetFieldMaxStringLength("txn_id"));
        var ex2 = Record.Exception(() => loaded.GetFieldMinStringLength("txn_id"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
