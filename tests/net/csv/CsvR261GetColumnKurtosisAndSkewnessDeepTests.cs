// Tests for CsvDocument.GetColumnKurtosis, GetColumnSkewness deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R261

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R261: Tests for CsvDocument.GetColumnKurtosis, GetColumnSkewness deeper.
/// GetColumnKurtosis(colName): returns excess kurtosis of the column's numeric distribution.
/// GetColumnSkewness(colName): returns skewness (third standardised moment) of the column.
/// Covers: GetColumnKurtosis no-throw; GetColumnKurtosis finite; GetColumnKurtosis consistent;
/// GetColumnKurtosis save-load; GetColumnSkewness no-throw; GetColumnSkewness finite;
/// GetColumnSkewness consistent; GetColumnSkewness near-zero for symmetric;
/// GetColumnSkewness positive for right-skew; GetColumnSkewness save-load;
/// dogfood CreateDoc→GetColumnKurtosis→GetColumnSkewness pipeline.
/// </summary>
public class CsvR261GetColumnKurtosisAndSkewnessDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR261GetColumnKurtosisAndSkewnessDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR261_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("loan_id,amount_gbp,term_months,interest_rate,credit_score,default_flag");
        var rng = new Random(20240901);
        for (int i = 0; i < 120; i++)
        {
            double amount = 1000 + rng.NextDouble() * 49000;
            int term = 12 + rng.Next(60);
            double rate = 3.5 + rng.NextDouble() * 20;
            int creditScore = 300 + rng.Next(600);
            int def = rng.NextDouble() < 0.1 ? 1 : 0;
            sb.AppendLine($"LN{i:D5},{amount:F2},{term},{rate:F2},{creditScore},{def}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateSymmetricCsv()
    {
        var path = TempFile("symmetric.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,val");
        for (int i = -5; i <= 5; i++)
            for (int j = 0; j < 10; j++)
                sb.AppendLine($"{(i + 5) * 10 + j},{i}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateRightSkewCsv()
    {
        var path = TempFile("rightskew.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,claim_gbp");
        var rng = new Random(99);
        for (int i = 0; i < 100; i++)
        {
            double v = -Math.Log(1.0 - rng.NextDouble()) * 5000 + 500;
            sb.AppendLine($"{i},{v:F2}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnKurtosis_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnKurtosis("amount_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnKurtosis_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(double.IsFinite(doc.GetColumnKurtosis("amount_gbp")));
    }

    [Fact]
    public void GetColumnKurtosis_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnKurtosis("credit_score"), doc.GetColumnKurtosis("credit_score"));
    }

    [Fact]
    public void GetColumnKurtosis_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnKurtosis("amount_gbp");
        var path = TempFile("kurt_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnKurtosis("amount_gbp"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnSkewness_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnSkewness("amount_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnSkewness_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(double.IsFinite(doc.GetColumnSkewness("amount_gbp")));
    }

    [Fact]
    public void GetColumnSkewness_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnSkewness("interest_rate"), doc.GetColumnSkewness("interest_rate"));
    }

    [Fact]
    public void GetColumnSkewness_Near_Zero_ForSymmetric()
    {
        var doc = CsvDocument.LoadFile(CreateSymmetricCsv());
        Assert.True(Math.Abs(doc.GetColumnSkewness("val")) < 0.5);
    }

    [Fact]
    public void GetColumnSkewness_Positive_ForRightSkew()
    {
        var doc = CsvDocument.LoadFile(CreateRightSkewCsv());
        Assert.True(doc.GetColumnSkewness("claim_gbp") > 0);
    }

    [Fact]
    public void GetColumnSkewness_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnSkewness("credit_score");
        var path = TempFile("skew_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnSkewness("credit_score"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnKurtosis_GetColumnSkewness_Pipeline()
    {
        // Insurance — Lloyd's of London Catastrophe Loss Modelling
        // Historic Cat event loss data: distribution shape for reinsurance pricing
        var path = TempFile("lloyds_cat_losses.csv");
        var sb = new StringBuilder();
        sb.AppendLine("event_id,event_year,peril,territory,insured_loss_musd,market_loss_musd,event_type,return_period_yrs");

        var rng = new Random(20241101);
        string[] perils = { "Windstorm", "Flood", "Earthquake", "Wildfire", "Surge" };
        string[] territories = { "US East Coast", "UK & Ireland", "Japan", "Australia", "Caribbean" };
        string[] eventTypes = { "Cat A", "Cat B", "Cat C" };

        for (int i = 0; i < 200; i++)
        {
            string eventId = $"EVT{i + 1:D5}";
            int year = 1990 + rng.Next(35);
            string peril = perils[rng.Next(perils.Length)];
            string territory = territories[rng.Next(territories.Length)];
            // Losses: highly right-skewed (most small, few catastrophic)
            double insuredLoss = rng.NextDouble() < 0.8
                ? 10 + rng.NextDouble() * 490      // most events: $10m-$500m
                : 500 + rng.NextDouble() * 9500;   // cat events: $500m-$10bn
            double marketLoss = insuredLoss * (1.5 + rng.NextDouble() * 0.5);
            string eventType = eventTypes[rng.Next(eventTypes.Length)];
            // Return period: right-skewed (many low-period events, few extreme)
            double returnPeriod = rng.NextDouble() < 0.7
                ? 1 + rng.NextDouble() * 49        // AEP 1-50 years
                : 50 + rng.NextDouble() * 950;     // rare events: 50-1000 years
            sb.AppendLine($"{eventId},{year},{peril},{territory},{insuredLoss:F1},{marketLoss:F1},{eventType},{returnPeriod:F0}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // GetColumnKurtosis — loss data: heavy tails → positive excess kurtosis
        var kurtInsuredLoss = doc.GetColumnKurtosis("insured_loss_musd");
        Assert.True(double.IsFinite(kurtInsuredLoss));
        Assert.Equal(kurtInsuredLoss, doc.GetColumnKurtosis("insured_loss_musd")); // consistent

        var kurtReturnPeriod = doc.GetColumnKurtosis("return_period_yrs");
        Assert.True(double.IsFinite(kurtReturnPeriod));

        var kurtYear = doc.GetColumnKurtosis("event_year");
        Assert.True(double.IsFinite(kurtYear));

        // GetColumnSkewness — loss data: right-skewed (heavy upper tail)
        var skewInsuredLoss = doc.GetColumnSkewness("insured_loss_musd");
        Assert.True(double.IsFinite(skewInsuredLoss));
        Assert.True(skewInsuredLoss > 0); // catastrophe losses are right-skewed
        Assert.Equal(skewInsuredLoss, doc.GetColumnSkewness("insured_loss_musd")); // consistent

        var skewMarketLoss = doc.GetColumnSkewness("market_loss_musd");
        Assert.True(double.IsFinite(skewMarketLoss));
        Assert.True(skewMarketLoss > 0); // market losses also right-skewed

        var skewReturnPeriod = doc.GetColumnSkewness("return_period_yrs");
        Assert.True(double.IsFinite(skewReturnPeriod));
        Assert.True(skewReturnPeriod > 0); // return periods right-skewed

        // Column stats
        Assert.True(doc.GetColumnMean("insured_loss_musd") > 0);
        Assert.True(doc.GetColumnStdDev("insured_loss_musd") > 0);
        Assert.True(doc.GetColumnMax("insured_loss_musd") > doc.GetColumnMin("insured_loss_musd"));

        // SaveToFile
        var outPath = TempFile("lloyds_cat_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(kurtInsuredLoss, loaded.GetColumnKurtosis("insured_loss_musd"), precision: 6);
        Assert.Equal(skewInsuredLoss, loaded.GetColumnSkewness("insured_loss_musd"), precision: 6);
        Assert.Equal(skewReturnPeriod, loaded.GetColumnSkewness("return_period_yrs"), precision: 6);

        // Symmetric test
        var symPath = TempFile("symmetric_loss.csv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("id,val");
        for (int i = -5; i <= 5; i++)
            for (int j = 0; j < 10; j++)
                sb2.AppendLine($"{(i + 5) * 10 + j},{i}");
        File.WriteAllText(symPath, sb2.ToString());
        var symDoc = CsvDocument.LoadFile(symPath);
        Assert.True(Math.Abs(symDoc.GetColumnSkewness("val")) < 0.5);
    }
}
