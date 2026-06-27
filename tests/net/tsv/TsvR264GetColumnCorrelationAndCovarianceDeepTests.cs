// Tests for TsvDocument.GetColumnCorrelation, GetColumnCovariance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R264

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R264: Tests for TsvDocument.GetColumnCorrelation, GetColumnCovariance deeper.
/// GetColumnCorrelation(colA, colB): returns Pearson correlation coefficient (-1 to +1).
/// GetColumnCovariance(colA, colB): returns population covariance between two columns.
/// Covers: GetColumnCorrelation no-throw; GetColumnCorrelation in-range; GetColumnCorrelation consistent;
/// GetColumnCorrelation one for identical; GetColumnCorrelation save-load;
/// GetColumnCovariance no-throw; GetColumnCovariance consistent;
/// GetColumnCovariance zero for independent; GetColumnCovariance save-load;
/// GetColumnCovariance positive for positively correlated;
/// dogfood CreateDoc→GetColumnCorrelation→GetColumnCovariance pipeline.
/// </summary>
public class TsvR264GetColumnCorrelationAndCovarianceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR264GetColumnCorrelationAndCovarianceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR264_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleTsv()
    {
        var path = TempFile("sample.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tx\ty_pos\ty_neg\tz_const");
        var rng = new Random(20240815);
        for (int i = 0; i < 100; i++)
        {
            double x = rng.NextDouble() * 100;
            double yPos = x * 2 + rng.NextDouble() * 5; // strong positive corr
            double yNeg = -x + rng.NextDouble() * 10;   // negative corr
            double z = 50.0;                              // constant
            sb.AppendLine($"{i}\t{x:F4}\t{yPos:F4}\t{yNeg:F4}\t{z:F4}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateIdenticalTsv()
    {
        var path = TempFile("identical.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\ta\tb");
        var rng = new Random(42);
        for (int i = 0; i < 50; i++)
        {
            double v = rng.NextDouble() * 100;
            sb.AppendLine($"{i}\t{v:F4}\t{v:F4}"); // a == b
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCorrelation_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnCorrelation("x", "y_pos"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCorrelation_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var r = doc.GetColumnCorrelation("x", "y_pos");
        Assert.True(r >= -1.0 && r <= 1.0);
    }

    [Fact]
    public void GetColumnCorrelation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnCorrelation("x", "y_pos"),
                     doc.GetColumnCorrelation("x", "y_pos"));
    }

    [Fact]
    public void GetColumnCorrelation_One_ForIdentical()
    {
        var doc = TsvDocument.LoadFile(CreateIdenticalTsv());
        Assert.Equal(1.0, doc.GetColumnCorrelation("a", "b"), precision: 6);
    }

    [Fact]
    public void GetColumnCorrelation_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnCorrelation("x", "y_pos");
        var path = TempFile("corr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCorrelation("x", "y_pos"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnCovariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCovariance_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnCovariance("x", "y_pos"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCovariance_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnCovariance("x", "y_pos"),
                     doc.GetColumnCovariance("x", "y_pos"));
    }

    [Fact]
    public void GetColumnCovariance_Positive_ForPositivelyCorrelated()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnCovariance("x", "y_pos") > 0);
    }

    [Fact]
    public void GetColumnCovariance_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnCovariance("x", "y_neg");
        var path = TempFile("cov_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCovariance("x", "y_neg"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnCorrelation_GetColumnCovariance_Pipeline()
    {
        // Economics — ONS Labour Force Survey: Employment Indicators
        // Correlation analysis between economic activity rate, wages, hours, and vacancies
        var path = TempFile("ons_lfs_indicators.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("quarter\tregion\tactivity_rate_pct\tunemployment_rate_pct\tmedian_weekly_pay_gbp\tavg_hours\tvacancy_rate_per_100");

        var rng = new Random(20240901);
        string[] regions = { "London", "South East", "East", "Midlands", "North West", "North East", "Scotland", "Wales" };
        string[] quarters = { "2023 Q1", "2023 Q2", "2023 Q3", "2023 Q4", "2024 Q1", "2024 Q2", "2024 Q3", "2024 Q4" };

        for (int i = 0; i < 200; i++)
        {
            string quarter = quarters[i % quarters.Length];
            string region = regions[i % regions.Length];
            // Activity rate and unemployment are negatively correlated
            double actRate = Math.Round(72 + rng.NextDouble() * 8, 1);
            double uRate = Math.Round(Math.Max(2.0, 10 - actRate / 10 + rng.NextDouble() * 1.5), 1);
            // Pay and activity rate are positively correlated
            double pay = Math.Round(450 + actRate * 8 + rng.NextDouble() * 50, 0);
            double hours = Math.Round(31 + rng.NextDouble() * 5, 1);
            double vacRate = Math.Round(2 + rng.NextDouble() * 4, 2);
            sb.AppendLine($"{quarter}\t{region}\t{actRate}\t{uRate}\t{pay}\t{hours}\t{vacRate}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(7, doc.ColumnCount);

        // Correlation: activity_rate vs median_pay — expect positive
        var corrActPay = doc.GetColumnCorrelation("activity_rate_pct", "median_weekly_pay_gbp");
        Assert.True(corrActPay >= -1.0 && corrActPay <= 1.0);
        Assert.Equal(corrActPay, doc.GetColumnCorrelation("activity_rate_pct", "median_weekly_pay_gbp")); // consistent
        Assert.True(corrActPay > 0); // positive correlation by construction

        // Correlation: activity_rate vs unemployment — expect negative
        var corrActUnemp = doc.GetColumnCorrelation("activity_rate_pct", "unemployment_rate_pct");
        Assert.True(corrActUnemp >= -1.0 && corrActUnemp <= 1.0);
        Assert.True(corrActUnemp < 0); // negative correlation by construction

        // Correlation: symmetric — corr(A,B) == corr(B,A)
        Assert.Equal(corrActPay,
                     doc.GetColumnCorrelation("median_weekly_pay_gbp", "activity_rate_pct"),
                     precision: 6);

        // Covariance: activity_rate vs median_pay — positive
        var covActPay = doc.GetColumnCovariance("activity_rate_pct", "median_weekly_pay_gbp");
        Assert.True(covActPay > 0);
        Assert.Equal(covActPay, doc.GetColumnCovariance("activity_rate_pct", "median_weekly_pay_gbp")); // consistent

        // Covariance: activity_rate vs unemployment — negative
        var covActUnemp = doc.GetColumnCovariance("activity_rate_pct", "unemployment_rate_pct");
        Assert.True(covActUnemp < 0);

        // Hours worked — moderate positive correlation with pay
        var corrHoursPay = doc.GetColumnCorrelation("avg_hours", "median_weekly_pay_gbp");
        Assert.True(corrHoursPay >= -1.0 && corrHoursPay <= 1.0);

        // SaveToFile
        var outPath = TempFile("ons_lfs_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(corrActPay, loaded.GetColumnCorrelation("activity_rate_pct", "median_weekly_pay_gbp"), precision: 6);
        Assert.Equal(covActPay, loaded.GetColumnCovariance("activity_rate_pct", "median_weekly_pay_gbp"), precision: 4);

        // Identical column → correlation = 1
        var corrSelf = doc.GetColumnCorrelation("activity_rate_pct", "activity_rate_pct");
        Assert.Equal(1.0, corrSelf, precision: 6);
    }
}
