// Tests for CsvDocument.GetColumnMean, GetColumnMedian deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R277

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R277: Tests for CsvDocument.GetColumnMean, GetColumnMedian deeper.
/// GetColumnMean(colName): returns the arithmetic mean of numeric values in the column.
/// GetColumnMedian(colName): returns the median numeric value in the column.
/// Covers: GetColumnMean no-throw; GetColumnMean in-range; GetColumnMean exact for uniform;
/// GetColumnMean consistent; GetColumnMean save-load;
/// GetColumnMedian no-throw; GetColumnMedian in-range; GetColumnMedian exact for uniform;
/// GetColumnMedian consistent; GetColumnMedian save-load;
/// GetColumnMean equals GetColumnMedian for uniform; dogfood pipeline.
/// </summary>
public class CsvR277GetColumnMeanAndMedianDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR277GetColumnMeanAndMedianDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR277_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id,score");
        // scores 0..90 step 10 → mean=45, median=45
        for (int i = 0; i < 10; i++)
            sb.AppendLine($"{i},{i * 10.0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,measure");
        for (int i = 0; i < 20; i++)
            sb.AppendLine($"{i},12.5");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMean_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnMean("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMean_InRange_BetweenMinAndMax()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var mean = doc.GetColumnMean("score");
        Assert.True(mean >= doc.GetColumnMin("score") && mean <= doc.GetColumnMax("score"));
    }

    [Fact]
    public void GetColumnMean_Exact_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(12.5, doc.GetColumnMean("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnMean_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnMean("score"), doc.GetColumnMean("score"));
    }

    [Fact]
    public void GetColumnMean_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnMean("score");
        var path = TempFile("mean_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnMean("score"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnMedian
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMedian_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnMedian("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMedian_InRange_BetweenMinAndMax()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var median = doc.GetColumnMedian("score");
        Assert.True(median >= doc.GetColumnMin("score") && median <= doc.GetColumnMax("score"));
    }

    [Fact]
    public void GetColumnMedian_Exact_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(12.5, doc.GetColumnMedian("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnMedian_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnMedian("score"), doc.GetColumnMedian("score"));
    }

    [Fact]
    public void GetColumnMedian_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnMedian("score");
        var path = TempFile("median_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnMedian("score"), precision: 6);
    }

    [Fact]
    public void GetColumnMean_Equals_Median_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(doc.GetColumnMean("measure"), doc.GetColumnMedian("measure"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMean_GetColumnMedian_Pipeline()
    {
        // Housing — DLUHC / Homes England: Affordable Housing Completions 2024
        // Local authority-level data on affordable housing delivery under Section 106 agreements
        // Mean and median distinguish average delivery from typical authority performance in skewed distributions

        var path = TempFile("dluhc_affordable_housing_2024.csv");
        var sb = new StringBuilder();
        sb.AppendLine("la_code,la_name,region,s106_completions,affordable_rent_units,shared_ownership_units,social_rent_units,total_completions,delivery_rate_pct,grant_per_unit_gbp,land_cost_per_unit_gbp");

        var rng = new Random(20241001);
        string[] regions = { "London", "South_East", "East_of_England", "South_West",
                              "West_Midlands", "East_Midlands", "Yorkshire", "North_West",
                              "North_East", "Wales" };
        string[] laNames = {
            "Tower_Hamlets", "Southwark", "Hackney", "Newham", "Wandsworth",
            "Birmingham", "Manchester", "Leeds", "Sheffield", "Liverpool",
            "Bristol", "Leicester", "Nottingham", "Newcastle", "Sunderland",
            "Cardiff", "Swansea", "Oxford", "Cambridge", "Brighton_and_Hove",
            "Plymouth", "Exeter", "Reading", "Slough", "Luton",
            "Coventry", "Wolverhampton", "Derby", "Bradford", "Salford"
        };

        for (int i = 0; i < 30; i++)
        {
            string region = regions[i % regions.Length];
            int s106 = 20 + rng.Next(480);
            int affordRent = (int)(s106 * (0.4 + rng.NextDouble() * 0.3));
            int sharedOwn = (int)(s106 * (0.2 + rng.NextDouble() * 0.2));
            int socRent = s106 - affordRent - sharedOwn;
            if (socRent < 0) socRent = 0;
            int total = s106 + rng.Next(50);
            double rate = 60 + rng.NextDouble() * 35;
            double grant = 30000 + rng.NextDouble() * 70000;
            double land = 15000 + rng.NextDouble() * 85000;
            // London LAs have much higher land costs
            if (region == "London") land *= 3.0;
            sb.AppendLine($"E0900{i:D4},{laNames[i]},{region},{s106},{affordRent},{sharedOwn},{socRent},{total},{rate:F1},{grant:F0},{land:F0}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(30, doc.RowCount);
        Assert.Equal(11, doc.ColumnCount);

        // S106 completions mean and median
        var s106Mean = doc.GetColumnMean("s106_completions");
        var s106Median = doc.GetColumnMedian("s106_completions");
        var s106Min = doc.GetColumnMin("s106_completions");
        var s106Max = doc.GetColumnMax("s106_completions");

        Assert.True(s106Mean >= s106Min && s106Mean <= s106Max);
        Assert.True(s106Median >= s106Min && s106Median <= s106Max);
        Assert.True(s106Mean > 0.0);
        Assert.Equal(s106Mean, doc.GetColumnMean("s106_completions")); // consistent
        Assert.Equal(s106Median, doc.GetColumnMedian("s106_completions")); // consistent

        // Delivery rate mean and median (should be in [60, 100])
        var rateMean = doc.GetColumnMean("delivery_rate_pct");
        var rateMedian = doc.GetColumnMedian("delivery_rate_pct");
        Assert.True(rateMean > 0.0 && rateMean <= 100.0);
        Assert.True(rateMedian > 0.0 && rateMedian <= 100.0);

        // Grant per unit mean and median
        var grantMean = doc.GetColumnMean("grant_per_unit_gbp");
        var grantMedian = doc.GetColumnMedian("grant_per_unit_gbp");
        Assert.True(grantMean > 0.0);
        Assert.True(grantMedian > 0.0);
        Assert.True(grantMean >= doc.GetColumnMin("grant_per_unit_gbp"));
        Assert.True(grantMean <= doc.GetColumnMax("grant_per_unit_gbp"));

        // Land cost: London premium means mean >> median (right-skewed)
        var landMean = doc.GetColumnMean("land_cost_per_unit_gbp");
        var landMedian = doc.GetColumnMedian("land_cost_per_unit_gbp");
        Assert.True(landMean > 0.0);
        Assert.True(landMedian > 0.0);
        // Mean not wildly below median (basic sanity)
        Assert.True(landMean >= landMedian * 0.5);

        // SaveToFile
        var outPath = TempFile("dluhc_affordable_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(s106Mean, loaded.GetColumnMean("s106_completions"), precision: 6);
        Assert.Equal(s106Median, loaded.GetColumnMedian("s106_completions"), precision: 6);
        Assert.Equal(rateMean, loaded.GetColumnMean("delivery_rate_pct"), precision: 6);
        Assert.Equal(grantMedian, loaded.GetColumnMedian("grant_per_unit_gbp"), precision: 6);
        Assert.Equal(landMean, loaded.GetColumnMean("land_cost_per_unit_gbp"), precision: 6);
    }
}
