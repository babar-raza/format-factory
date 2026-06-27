// Tests for CsvDocument.GetColumnZScore, GetColumnStandardizedValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R251

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R251: Tests for CsvDocument.GetColumnZScore, GetColumnStandardizedValues deeper.
/// GetColumnZScore(colName, value): returns (value - mean) / stddev for the named column.
/// GetColumnStandardizedValues(colName): returns the array of z-scores for all rows in the column.
/// Covers: GetColumnZScore no-throw; GetColumnZScore zero at mean; GetColumnZScore consistent;
/// GetColumnZScore positive above mean; GetColumnZScore negative below mean;
/// GetColumnStandardizedValues no-throw; GetColumnStandardizedValues non-null;
/// GetColumnStandardizedValues count equals row count; GetColumnStandardizedValues mean near zero;
/// GetColumnStandardizedValues save-load;
/// dogfood CreateDoc→GetColumnZScore→GetColumnStandardizedValues pipeline.
/// </summary>
public class CsvR251GetColumnZScoreAndStandardizedValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR251GetColumnZScoreAndStandardizedValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR251_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("property_id,price_gbp,sqft,bedrooms,age_years,epc_rating_numeric");
        var rng = new Random(12345);
        for (int i = 0; i < 60; i++)
        {
            int price = 150000 + rng.Next(850000);
            int sqft = 500 + rng.Next(3000);
            int beds = 1 + rng.Next(6);
            int age = rng.Next(150);
            int epc = 20 + rng.Next(80);
            sb.AppendLine($"PROP{i:D4},{price},{sqft},{beds},{age},{epc}");
        }
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
        var mean = doc.GetColumnMean("price_gbp");
        var ex = Record.Exception(() => doc.GetColumnZScore("price_gbp", mean));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnZScore_Zero_AtMean()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var mean = doc.GetColumnMean("price_gbp");
        Assert.Equal(0.0, doc.GetColumnZScore("price_gbp", mean), precision: 6);
    }

    [Fact]
    public void GetColumnZScore_Positive_AboveMean()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var mean = doc.GetColumnMean("sqft");
        var stddev = doc.GetColumnStdDev("sqft");
        Assert.True(doc.GetColumnZScore("sqft", mean + stddev) > 0.0);
    }

    [Fact]
    public void GetColumnZScore_Negative_BelowMean()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var mean = doc.GetColumnMean("sqft");
        var stddev = doc.GetColumnStdDev("sqft");
        Assert.True(doc.GetColumnZScore("sqft", mean - stddev) < 0.0);
    }

    [Fact]
    public void GetColumnZScore_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var z1 = doc.GetColumnZScore("age_years", 50.0);
        var z2 = doc.GetColumnZScore("age_years", 50.0);
        Assert.Equal(z1, z2);
    }

    // -------------------------------------------------------------------------
    // GetColumnStandardizedValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStandardizedValues_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnStandardizedValues("price_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnStandardizedValues_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.GetColumnStandardizedValues("price_gbp"));
    }

    [Fact]
    public void GetColumnStandardizedValues_Count_Equals_RowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var vals = doc.GetColumnStandardizedValues("price_gbp");
        Assert.Equal(doc.RowCount, vals.Length);
    }

    [Fact]
    public void GetColumnStandardizedValues_Mean_Near_Zero()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var vals = doc.GetColumnStandardizedValues("price_gbp");
        double sum = 0;
        foreach (var v in vals) sum += v;
        Assert.Equal(0.0, sum / vals.Length, precision: 6);
    }

    [Fact]
    public void GetColumnStandardizedValues_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnStandardizedValues("sqft");
        var path = TempFile("zsv_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetColumnStandardizedValues("sqft");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnZScore_GetColumnStandardizedValues_Pipeline()
    {
        // Epidemiology — UK Biobank cardiovascular risk factor distribution study
        var path = TempFile("cvd_risk_factors.csv");
        var sb = new StringBuilder();
        sb.AppendLine("eid,age,bmi,sbp_mmhg,total_cholesterol_mmol,hdl_mmol,ldl_mmol,triglycerides_mmol,hba1c_mmol_mol,crp_mg_l");
        var rng = new Random(20250101);
        for (int i = 0; i < 150; i++)
        {
            int age = 40 + rng.Next(40);
            double bmi = 18.5 + rng.NextDouble() * 22.0;
            int sbp = 100 + rng.Next(80);
            double tc = 3.5 + rng.NextDouble() * 4.0;
            double hdl = 0.8 + rng.NextDouble() * 2.0;
            double ldl = 1.5 + rng.NextDouble() * 4.0;
            double tg = 0.5 + rng.NextDouble() * 3.5;
            double hba1c = 31 + rng.NextDouble() * 50;
            double crp = 0.1 + rng.NextDouble() * 15.0;
            sb.AppendLine($"{1000000 + i},{age},{bmi:F1},{sbp},{tc:F2},{hdl:F2},{ldl:F2},{tg:F2},{hba1c:F1},{crp:F2}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);
        Assert.Equal(10, doc.ColumnCount);

        // GetColumnZScore
        var meanBmi = doc.GetColumnMean("bmi");
        var stddevBmi = doc.GetColumnStdDev("bmi");

        var zAtMean = doc.GetColumnZScore("bmi", meanBmi);
        Assert.Equal(0.0, zAtMean, precision: 6);

        var zAbove = doc.GetColumnZScore("bmi", meanBmi + stddevBmi);
        Assert.True(zAbove > 0.0);
        Assert.Equal(1.0, zAbove, precision: 4);

        var zBelow = doc.GetColumnZScore("bmi", meanBmi - stddevBmi);
        Assert.True(zBelow < 0.0);
        Assert.Equal(-1.0, zBelow, precision: 4);

        // Consistent
        Assert.Equal(doc.GetColumnZScore("sbp_mmhg", 120.0), doc.GetColumnZScore("sbp_mmhg", 120.0));
        Assert.Equal(doc.GetColumnZScore("total_cholesterol_mmol", 5.0), doc.GetColumnZScore("total_cholesterol_mmol", 5.0));

        // GetColumnStandardizedValues
        var zValsBmi = doc.GetColumnStandardizedValues("bmi");
        Assert.NotNull(zValsBmi);
        Assert.Equal(150, zValsBmi.Length);

        // Mean near 0
        double sumBmi = 0;
        foreach (var v in zValsBmi) sumBmi += v;
        Assert.Equal(0.0, sumBmi / zValsBmi.Length, precision: 6);

        var zValsSbp = doc.GetColumnStandardizedValues("sbp_mmhg");
        Assert.Equal(150, zValsSbp.Length);
        double sumSbp = 0;
        foreach (var v in zValsSbp) sumSbp += v;
        Assert.Equal(0.0, sumSbp / zValsSbp.Length, precision: 6);

        // Std dev of z-scores should be ~1.0
        double sumSqBmi = 0;
        foreach (var v in zValsBmi) sumSqBmi += v * v;
        double stdZ = Math.Sqrt(sumSqBmi / zValsBmi.Length);
        Assert.True(stdZ > 0.9 && stdZ < 1.1);

        // Consistent
        var z2 = doc.GetColumnStandardizedValues("bmi");
        for (int i = 0; i < 5; i++)
            Assert.Equal(zValsBmi[i], z2[i]);

        // Basic stats
        Assert.True(doc.GetColumnMean("age") > 0.0);
        Assert.True(doc.GetColumnMin("hdl_mmol") > 0.0);
        Assert.True(doc.GetColumnMax("crp_mg_l") > doc.GetColumnMean("crp_mg_l"));

        // SaveToFile
        var outPath = TempFile("cvd_risk_factors_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(zAtMean, loaded.GetColumnZScore("bmi", meanBmi), precision: 8);
        var loadedZVals = loaded.GetColumnStandardizedValues("bmi");
        Assert.Equal(zValsBmi.Length, loadedZVals.Length);
        for (int i = 0; i < 5; i++)
            Assert.Equal(zValsBmi[i], loadedZVals[i], precision: 8);
    }
}
