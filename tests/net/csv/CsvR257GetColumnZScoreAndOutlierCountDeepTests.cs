// Tests for CsvDocument.GetColumnZScore, GetColumnOutlierCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R257

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R257: Tests for CsvDocument.GetColumnZScore, GetColumnOutlierCount deeper.
/// GetColumnZScore(colName, row): returns the z-score of the value in the given row.
/// GetColumnOutlierCount(colName, threshold): returns count of rows where |z-score| > threshold.
/// Covers: GetColumnZScore no-throw; GetColumnZScore finite; GetColumnZScore consistent;
/// GetColumnZScore save-load; GetColumnOutlierCount no-throw;
/// GetColumnOutlierCount non-negative; GetColumnOutlierCount zero for constant;
/// GetColumnOutlierCount less-than-RowCount; GetColumnOutlierCount consistent;
/// GetColumnOutlierCount save-load;
/// dogfood CreateDoc→GetColumnZScore→GetColumnOutlierCount pipeline.
/// </summary>
public class CsvR257GetColumnZScoreAndOutlierCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR257GetColumnZScoreAndOutlierCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR257_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleCsv()
    {
        var path = TempFile("sample.csv");
        var sb = new StringBuilder();
        sb.AppendLine("trial_id,treatment,response_rate,adverse_events,dropout_pct,sample_size");
        var rng = new Random(20240801);
        for (int i = 0; i < 80; i++)
        {
            string trt = i % 3 == 0 ? "A" : (i % 3 == 1 ? "B" : "Placebo");
            double rr = 30 + rng.NextDouble() * 40;
            int ae = rng.Next(5, 25);
            double drop = 5 + rng.NextDouble() * 20;
            int n = 50 + rng.Next(150);
            if (i == 10) rr = 98.5;  // outlier
            if (i == 40) ae = 120;    // outlier
            sb.AppendLine($"T{i:D4},{trt},{rr:F1},{ae},{drop:F1},{n}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantCsv()
    {
        var path = TempFile("constant.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,fixed_dose");
        for (int i = 0; i < 40; i++)
            sb.AppendLine($"{i},100.0");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnZScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnZScore_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnZScore("response_rate", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnZScore_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var z = doc.GetColumnZScore("response_rate", 0);
        Assert.True(double.IsFinite(z));
    }

    [Fact]
    public void GetColumnZScore_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnZScore("dropout_pct", 5), doc.GetColumnZScore("dropout_pct", 5));
    }

    [Fact]
    public void GetColumnZScore_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnZScore("sample_size", 2);
        var path = TempFile("zs_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnZScore("sample_size", 2), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnOutlierCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnOutlierCount_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnOutlierCount("response_rate", 2.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnOutlierCount_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnOutlierCount("adverse_events", 2.0) >= 0);
    }

    [Fact]
    public void GetColumnOutlierCount_Zero_ForConstant()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0, doc.GetColumnOutlierCount("fixed_dose", 2.0));
    }

    [Fact]
    public void GetColumnOutlierCount_LessThanRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnOutlierCount("dropout_pct", 1.5) < doc.RowCount);
    }

    [Fact]
    public void GetColumnOutlierCount_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var v1 = doc.GetColumnOutlierCount("response_rate", 3.0);
        var v2 = doc.GetColumnOutlierCount("response_rate", 3.0);
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnOutlierCount_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnOutlierCount("adverse_events", 2.5);
        var path = TempFile("oc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnOutlierCount("adverse_events", 2.5));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnZScore_GetColumnOutlierCount_Pipeline()
    {
        // Financial crime — FCA Suspicious Activity Reports (SARs) analytics
        // Transaction monitoring: z-score based outlier detection for AML screening
        var path = TempFile("sar_transactions.csv");
        var sb = new StringBuilder();
        sb.AppendLine("transaction_id,customer_segment,amount_gbp,counterparty_country_risk,velocity_30d,structuring_indicator,amount_threshold_pct,prior_sars,account_age_days");
        var rng = new Random(20240701);

        string[] segments = { "retail", "sme", "corporate", "private_banking", "wealth" };
        string[] countries = { "UK", "EU", "US", "HK", "AE", "CH" };
        double[] countryRisk = { 1.0, 1.5, 1.2, 3.5, 4.2, 2.8 };

        for (int i = 0; i < 200; i++)
        {
            string seg = segments[i % segments.Length];
            int cIdx = rng.Next(countries.Length);
            double amount = seg == "retail" ? (500 + rng.NextDouble() * 4500) :
                           seg == "sme" ? (5000 + rng.NextDouble() * 45000) :
                           seg == "corporate" ? (50000 + rng.NextDouble() * 450000) :
                           (10000 + rng.NextDouble() * 90000);
            double risk = countryRisk[cIdx] + rng.NextDouble() * 0.5;
            int velocity = rng.Next(1, 50);
            int structuring = rng.NextDouble() < 0.08 ? 1 : 0;
            double threshold = amount / (seg == "retail" ? 10000 : 250000) * 100;
            int priorSars = rng.NextDouble() < 0.05 ? rng.Next(1, 5) : 0;
            int acctAge = 30 + rng.Next(3650);

            // Inject high-value suspicious transactions
            if (i == 15) { amount = 98500; structuring = 1; velocity = 85; }  // structuring outlier
            if (i == 88) { amount = 1250000; risk = 6.8; }  // large high-risk payment
            if (i == 155) { velocity = 230; priorSars = 8; }  // velocity outlier

            sb.AppendLine($"TXN{1000000 + i},{seg},{amount:F2},{risk:F2},{velocity},{structuring},{threshold:F1},{priorSars},{acctAge}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(9, doc.ColumnCount);

        // GetColumnZScore — individual anomalous transactions
        var zsAmount88 = doc.GetColumnZScore("amount_gbp", 88);
        Assert.True(double.IsFinite(zsAmount88));
        Assert.True(zsAmount88 > 2.0); // large payment is outlier

        var zsVelocity155 = doc.GetColumnZScore("velocity_30d", 155);
        Assert.True(double.IsFinite(zsVelocity155));
        Assert.True(zsVelocity155 > 2.0); // velocity spike

        // Normal transaction z-scores should be moderate
        var zsAmount0 = doc.GetColumnZScore("amount_gbp", 0);
        Assert.True(double.IsFinite(zsAmount0));
        Assert.Equal(doc.GetColumnZScore("amount_gbp", 0), doc.GetColumnZScore("amount_gbp", 0)); // consistent

        // GetColumnOutlierCount — AML screening
        var outliersAmount = doc.GetColumnOutlierCount("amount_gbp", 3.0);
        Assert.True(outliersAmount >= 1); // large payment outlier
        Assert.True(outliersAmount < doc.RowCount);

        var outliersVelocity = doc.GetColumnOutlierCount("velocity_30d", 3.0);
        Assert.True(outliersVelocity >= 1);

        var outliersRisk = doc.GetColumnOutlierCount("counterparty_country_risk", 2.5);
        Assert.True(outliersRisk >= 0);

        // More sensitive threshold catches more
        var outliersAmountSensitive = doc.GetColumnOutlierCount("amount_gbp", 1.5);
        Assert.True(outliersAmountSensitive >= outliersAmount);

        // Consistent
        Assert.Equal(outliersAmount, doc.GetColumnOutlierCount("amount_gbp", 3.0));

        // Basic stats
        Assert.True(doc.GetColumnMean("amount_gbp") > 0);
        Assert.True(doc.GetColumnStdDev("amount_gbp") > 0);
        Assert.True(doc.GetColumnMin("velocity_30d") <= doc.GetColumnMax("velocity_30d"));

        // SaveToFile
        var outPath = TempFile("sar_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(zsAmount88, loaded.GetColumnZScore("amount_gbp", 88), precision: 8);
        Assert.Equal(outliersAmount, loaded.GetColumnOutlierCount("amount_gbp", 3.0));

        // Constant column
        var path2 = TempFile("constant_sar.csv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("id,flat_fee");
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"{i},25.00");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = CsvDocument.LoadFile(path2);
        Assert.Equal(0, doc2.GetColumnOutlierCount("flat_fee", 2.0));
    }
}
