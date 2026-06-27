// Tests for CsvDocument.GetColumnNormalizedValues, GetColumnRobustScaledValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R252

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R252: Tests for CsvDocument.GetColumnNormalizedValues, GetColumnRobustScaledValues deeper.
/// GetColumnNormalizedValues(colName): returns (value - min) / (max - min) for each row.
/// GetColumnRobustScaledValues(colName): returns (value - median) / IQR for each row.
/// Covers: GetColumnNormalizedValues no-throw; GetColumnNormalizedValues non-null;
/// GetColumnNormalizedValues count equals row count; GetColumnNormalizedValues all in [0,1];
/// GetColumnNormalizedValues save-load;
/// GetColumnRobustScaledValues no-throw; GetColumnRobustScaledValues non-null;
/// GetColumnRobustScaledValues count equals row count; GetColumnRobustScaledValues median near zero;
/// GetColumnRobustScaledValues save-load;
/// dogfood CreateDoc→GetColumnNormalizedValues→GetColumnRobustScaledValues pipeline.
/// </summary>
public class CsvR252GetColumnNormalizedValuesAndRobustScaledValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR252GetColumnNormalizedValuesAndRobustScaledValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR252_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("customer_id,age,income_gbp,credit_score,debt_to_income,account_tenure_months");
        var rng = new Random(54321);
        for (int i = 0; i < 60; i++)
        {
            int age = 22 + rng.Next(60);
            int income = 18000 + rng.Next(130000);
            int score = 300 + rng.Next(550);
            double dti = 0.05 + rng.NextDouble() * 0.55;
            int tenure = rng.Next(240);
            sb.AppendLine($"CUS{i:D5},{age},{income},{score},{dti:F3},{tenure}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnNormalizedValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnNormalizedValues_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnNormalizedValues("income_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnNormalizedValues_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.GetColumnNormalizedValues("income_gbp"));
    }

    [Fact]
    public void GetColumnNormalizedValues_Count_Equals_RowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.RowCount, doc.GetColumnNormalizedValues("income_gbp").Length);
    }

    [Fact]
    public void GetColumnNormalizedValues_All_In_01()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        foreach (var v in doc.GetColumnNormalizedValues("credit_score"))
            Assert.True(v >= 0.0 && v <= 1.0);
    }

    [Fact]
    public void GetColumnNormalizedValues_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnNormalizedValues("age");
        var path = TempFile("nv_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetColumnNormalizedValues("age");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnRobustScaledValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRobustScaledValues_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnRobustScaledValues("income_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRobustScaledValues_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.GetColumnRobustScaledValues("income_gbp"));
    }

    [Fact]
    public void GetColumnRobustScaledValues_Count_Equals_RowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.RowCount, doc.GetColumnRobustScaledValues("credit_score").Length);
    }

    [Fact]
    public void GetColumnRobustScaledValues_Median_Near_Zero()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var vals = doc.GetColumnRobustScaledValues("income_gbp");
        var sorted = (double[])vals.Clone();
        Array.Sort(sorted);
        double median = sorted.Length % 2 == 0
            ? (sorted[sorted.Length / 2 - 1] + sorted[sorted.Length / 2]) / 2.0
            : sorted[sorted.Length / 2];
        Assert.Equal(0.0, median, precision: 3);
    }

    [Fact]
    public void GetColumnRobustScaledValues_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnRobustScaledValues("credit_score");
        var path = TempFile("rsv_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetColumnRobustScaledValues("credit_score");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnNormalizedValues_GetColumnRobustScaledValues_Pipeline()
    {
        // Machine learning — fraud detection feature engineering for payment card transactions
        var path = TempFile("fraud_detection_features.csv");
        var sb = new StringBuilder();
        sb.AppendLine("txn_id,amount_gbp,merchant_category_code,time_since_last_txn_seconds,distance_from_home_km,velocity_24h,card_age_days,is_international,is_contactless,fraud_label");
        var rng = new Random(20250601);
        for (int i = 0; i < 150; i++)
        {
            bool isFraud = rng.Next(20) == 0; // 5% fraud rate
            double amount = isFraud ? 200 + rng.NextDouble() * 3800 : 5 + rng.NextDouble() * 295;
            // Add outliers for outlier robustness test
            if (rng.Next(25) == 0) amount = 5000 + rng.NextDouble() * 10000;
            int mcc = 1000 + rng.Next(8999);
            double timeSinceLast = isFraud ? rng.NextDouble() * 30 : 300 + rng.NextDouble() * 86000;
            double distFromHome = isFraud ? 50 + rng.NextDouble() * 500 : rng.NextDouble() * 30;
            int velocity = isFraud ? 5 + rng.Next(30) : rng.Next(8);
            int cardAge = 30 + rng.Next(3000);
            int isIntl = isFraud && rng.Next(3) == 0 ? 1 : 0;
            int isContactless = rng.Next(3) == 0 ? 1 : 0;
            sb.AppendLine($"T{i:D6},{amount:F2},{mcc},{timeSinceLast:F0},{distFromHome:F2},{velocity},{cardAge},{isIntl},{isContactless},{(isFraud ? 1 : 0)}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);
        Assert.Equal(10, doc.ColumnCount);

        // GetColumnNormalizedValues
        var normAmount = doc.GetColumnNormalizedValues("amount_gbp");
        Assert.NotNull(normAmount);
        Assert.Equal(150, normAmount.Length);
        foreach (var v in normAmount)
            Assert.True(v >= 0.0 && v <= 1.0);

        var normTime = doc.GetColumnNormalizedValues("time_since_last_txn_seconds");
        Assert.Equal(150, normTime.Length);
        foreach (var v in normTime)
            Assert.True(v >= 0.0 && v <= 1.0);

        var normDist = doc.GetColumnNormalizedValues("distance_from_home_km");
        Assert.Equal(150, normDist.Length);
        foreach (var v in normDist)
            Assert.True(v >= 0.0 && v <= 1.0);

        // GetColumnRobustScaledValues — handles outlier amounts well
        var robAmount = doc.GetColumnRobustScaledValues("amount_gbp");
        Assert.NotNull(robAmount);
        Assert.Equal(150, robAmount.Length);

        // Median of robust-scaled should be 0
        var sortedRob = (double[])robAmount.Clone();
        Array.Sort(sortedRob);
        double medianRob = sortedRob.Length % 2 == 0
            ? (sortedRob[sortedRob.Length / 2 - 1] + sortedRob[sortedRob.Length / 2]) / 2.0
            : sortedRob[sortedRob.Length / 2];
        Assert.Equal(0.0, medianRob, precision: 2);

        var robVelocity = doc.GetColumnRobustScaledValues("velocity_24h");
        Assert.Equal(150, robVelocity.Length);

        var robCardAge = doc.GetColumnRobustScaledValues("card_age_days");
        Assert.Equal(150, robCardAge.Length);

        // Consistent
        var norm2 = doc.GetColumnNormalizedValues("amount_gbp");
        for (int i = 0; i < 5; i++)
            Assert.Equal(normAmount[i], norm2[i]);

        var rob2 = doc.GetColumnRobustScaledValues("amount_gbp");
        for (int i = 0; i < 5; i++)
            Assert.Equal(robAmount[i], rob2[i]);

        // Basic stats
        Assert.True(doc.GetColumnMin("amount_gbp") > 0.0);
        Assert.True(doc.GetColumnMean("velocity_24h") >= 0.0);

        // SaveToFile
        var outPath = TempFile("fraud_detection_features_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        var loadedNorm = loaded.GetColumnNormalizedValues("amount_gbp");
        Assert.Equal(normAmount.Length, loadedNorm.Length);
        for (int i = 0; i < 5; i++)
            Assert.Equal(normAmount[i], loadedNorm[i], precision: 8);
        var loadedRob = loaded.GetColumnRobustScaledValues("amount_gbp");
        Assert.Equal(robAmount.Length, loadedRob.Length);
        for (int i = 0; i < 5; i++)
            Assert.Equal(robAmount[i], loadedRob[i], precision: 8);
    }
}
