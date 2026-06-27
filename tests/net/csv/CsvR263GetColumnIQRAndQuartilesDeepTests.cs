// Tests for CsvDocument.GetColumnIQR, GetColumnQuartiles deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R263

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R263: Tests for CsvDocument.GetColumnIQR, GetColumnQuartiles deeper.
/// GetColumnIQR(colName): returns the interquartile range (Q3-Q1) of numeric values in the column.
/// GetColumnQuartiles(colName): returns Q1, Q2 (median), Q3 as a tuple/struct.
/// Covers: GetColumnIQR no-throw; GetColumnIQR non-negative; GetColumnIQR consistent;
/// GetColumnIQR zero for constant; GetColumnIQR save-load;
/// GetColumnQuartiles no-throw; GetColumnQuartiles Q1 le Q2 le Q3;
/// GetColumnQuartiles consistent; GetColumnQuartiles save-load;
/// GetColumnIQR equals Q3 minus Q1; dogfood CreateDoc→GetColumnIQR→GetColumnQuartiles pipeline.
/// </summary>
public class CsvR263GetColumnIQRAndQuartilesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR263GetColumnIQRAndQuartilesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR263_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("policy_id,premium_gbp,claims_count,loss_ratio_pct,years_on_risk");
        var rng = new Random(20240815);
        for (int i = 0; i < 80; i++)
        {
            int premium = 500 + rng.Next(9500);
            int claims = rng.Next(8);
            int lr = 20 + rng.Next(120);
            int yrs = 1 + rng.Next(20);
            sb.AppendLine($"POL{i:D5},{premium},{claims},{lr},{yrs}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantCsv()
    {
        var path = TempFile("constant.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,value");
        for (int i = 0; i < 40; i++)
            sb.AppendLine($"{i},100");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnIQR
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnIQR_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnIQR("premium_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnIQR_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnIQR("premium_gbp") >= 0.0);
    }

    [Fact]
    public void GetColumnIQR_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnIQR("premium_gbp"), doc.GetColumnIQR("premium_gbp"));
    }

    [Fact]
    public void GetColumnIQR_Zero_ForConstant()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0.0, doc.GetColumnIQR("value"), precision: 8);
    }

    [Fact]
    public void GetColumnIQR_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnIQR("premium_gbp");
        var path = TempFile("iqr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnIQR("premium_gbp"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnQuartiles
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnQuartiles_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnQuartiles("premium_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnQuartiles_Q1_Le_Q2_Le_Q3()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var q = doc.GetColumnQuartiles("premium_gbp");
        Assert.True(q.Q1 <= q.Q2);
        Assert.True(q.Q2 <= q.Q3);
    }

    [Fact]
    public void GetColumnQuartiles_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var q1 = doc.GetColumnQuartiles("loss_ratio_pct");
        var q2 = doc.GetColumnQuartiles("loss_ratio_pct");
        Assert.Equal(q1.Q1, q2.Q1);
        Assert.Equal(q1.Q2, q2.Q2);
        Assert.Equal(q1.Q3, q2.Q3);
    }

    [Fact]
    public void GetColumnQuartiles_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnQuartiles("years_on_risk");
        var path = TempFile("q_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetColumnQuartiles("years_on_risk");
        Assert.Equal(before.Q1, after.Q1, precision: 8);
        Assert.Equal(before.Q2, after.Q2, precision: 8);
        Assert.Equal(before.Q3, after.Q3, precision: 8);
    }

    [Fact]
    public void GetColumnIQR_Equals_Q3_Minus_Q1()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var q = doc.GetColumnQuartiles("loss_ratio_pct");
        var iqr = doc.GetColumnIQR("loss_ratio_pct");
        Assert.Equal(q.Q3 - q.Q1, iqr, precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnIQR_GetColumnQuartiles_Pipeline()
    {
        // Insurance — Lloyd's of London Syndicate Performance Analysis
        // Combined ratio, expense ratio, premium data for syndicates across classes of business
        // IQR analysis to detect outlier syndicates and class-of-business concentration
        var path = TempFile("lloyds_syndicate_data.csv");
        var sb = new StringBuilder();
        sb.AppendLine("syndicate_id,class_of_business,gwp_gbpm,nep_gbpm,net_claims_gbpm,expense_ratio_pct,combined_ratio_pct,roe_pct,years_operating");

        var rng = new Random(20240901);
        string[] classes = { "Property Cat", "Marine Cargo", "Aviation", "Casualty", "Cyber",
                              "Energy", "Motor", "Life Re", "Political Risk", "Credit" };
        int[] classMeans = { 145, 95, 78, 118, 162, 104, 88, 92, 135, 108 }; // combined ratio baseline

        for (int i = 0; i < 200; i++)
        {
            int classIdx = i % classes.Length;
            string cls = classes[classIdx];
            double gwp = Math.Round(10 + rng.NextDouble() * 490, 1);
            double nep = Math.Round(gwp * (0.7 + rng.NextDouble() * 0.2), 1);
            double claims = Math.Round(nep * (0.4 + rng.NextDouble() * 0.5), 1);
            int expRatio = 25 + rng.Next(20);
            int baseRatio = classMeans[classIdx];
            int combRatio = Math.Max(60, Math.Min(200, baseRatio + rng.Next(-30, 31)));
            double roe = Math.Round(-5 + rng.NextDouble() * 25, 1);
            int yrs = 3 + rng.Next(35);
            sb.AppendLine($"S{1000 + i},{cls},{gwp},{nep},{claims},{expRatio},{combRatio},{roe},{yrs}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(9, doc.ColumnCount);

        // IQR of combined ratio
        var iqrCombined = doc.GetColumnIQR("combined_ratio_pct");
        Assert.True(iqrCombined >= 0);
        Assert.Equal(iqrCombined, doc.GetColumnIQR("combined_ratio_pct")); // consistent

        // Quartiles of combined ratio
        var qCombined = doc.GetColumnQuartiles("combined_ratio_pct");
        Assert.True(qCombined.Q1 <= qCombined.Q2);
        Assert.True(qCombined.Q2 <= qCombined.Q3);
        Assert.True(qCombined.Q1 >= 60);
        Assert.True(qCombined.Q3 <= 200);
        Assert.Equal(qCombined.Q3 - qCombined.Q1, iqrCombined, precision: 6);

        // IQR of GWP — wide spread expected
        var iqrGwp = doc.GetColumnIQR("gwp_gbpm");
        Assert.True(iqrGwp >= 0);
        var qGwp = doc.GetColumnQuartiles("gwp_gbpm");
        Assert.True(qGwp.Q1 <= qGwp.Q2);
        Assert.True(qGwp.Q2 <= qGwp.Q3);
        Assert.Equal(qGwp.Q3 - qGwp.Q1, iqrGwp, precision: 6);

        // IQR of expense ratio — narrower (25-44 range)
        var iqrExp = doc.GetColumnIQR("expense_ratio_pct");
        Assert.True(iqrExp >= 0);
        Assert.True(iqrExp <= 19); // max range is 19
        var qExp = doc.GetColumnQuartiles("expense_ratio_pct");
        Assert.True(qExp.Q1 >= 25);
        Assert.True(qExp.Q3 <= 44);

        // IQR of years_operating
        var iqrYrs = doc.GetColumnIQR("years_operating");
        Assert.True(iqrYrs >= 0);
        var qYrs = doc.GetColumnQuartiles("years_operating");
        Assert.True(qYrs.Q1 <= qYrs.Q2);
        Assert.True(qYrs.Q2 <= qYrs.Q3);

        // IQR of ROE
        var iqrRoe = doc.GetColumnIQR("roe_pct");
        Assert.True(iqrRoe >= 0);
        var qRoe = doc.GetColumnQuartiles("roe_pct");
        Assert.True(qRoe.Q1 <= qRoe.Q2);
        Assert.True(qRoe.Q2 <= qRoe.Q3);

        // Basic column stats
        Assert.True(doc.GetColumnMean("combined_ratio_pct") > 0);
        Assert.True(doc.GetColumnStdDev("gwp_gbpm") > 0);

        // SaveToFile
        var outPath = TempFile("lloyds_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(iqrCombined, loaded.GetColumnIQR("combined_ratio_pct"), precision: 8);
        var qLoaded = loaded.GetColumnQuartiles("combined_ratio_pct");
        Assert.Equal(qCombined.Q1, qLoaded.Q1, precision: 8);
        Assert.Equal(qCombined.Q2, qLoaded.Q2, precision: 8);
        Assert.Equal(qCombined.Q3, qLoaded.Q3, precision: 8);

        // Constant IQR sub-test
        var path2 = TempFile("constant_lloyds.csv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("id,combined_ratio");
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"{i},100");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = CsvDocument.LoadFile(path2);
        Assert.Equal(0.0, doc2.GetColumnIQR("combined_ratio"), precision: 8);
        var qConst = doc2.GetColumnQuartiles("combined_ratio");
        Assert.Equal(100.0, qConst.Q1, precision: 6);
        Assert.Equal(100.0, qConst.Q2, precision: 6);
        Assert.Equal(100.0, qConst.Q3, precision: 6);
    }
}
