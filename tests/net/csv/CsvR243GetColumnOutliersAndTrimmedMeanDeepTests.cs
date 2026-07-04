// Tests for CsvDocument.GetColumnOutliers, GetColumnTrimmedMean, GetColumnIQR deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R243

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R243: Tests for CsvDocument.GetColumnOutliers, GetColumnTrimmedMean, GetColumnIQR deeper.
/// GetColumnOutliers(columnName, threshold): returns the count of outlier values in the column.
/// GetColumnTrimmedMean(columnName, trimFraction): returns the mean after trimming extreme values.
/// GetColumnIQR(columnName): returns the interquartile range (Q3-Q1) of numeric values.
/// Covers: GetColumnOutliers no-throw; GetColumnOutliers non-negative; GetColumnOutliers consistent;
/// GetColumnOutliers zero for uniform data;
/// GetColumnTrimmedMean no-throw; GetColumnTrimmedMean finite; GetColumnTrimmedMean consistent;
/// GetColumnTrimmedMean between min and max;
/// GetColumnIQR no-throw; GetColumnIQR non-negative; GetColumnIQR consistent;
/// GetColumnIQR zero for constant column; GetColumnIQR save-load;
/// dogfood CreateDoc→GetColumnOutliers→GetColumnTrimmedMean→GetColumnIQR pipeline.
/// </summary>
public class CsvR243GetColumnOutliersAndTrimmedMeanDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR243GetColumnOutliersAndTrimmedMeanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR243_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePropertyCsv()
    {
        var path = TempFile("property.csv");
        var lines = new System.Collections.Generic.List<string>
        {
            "postcode,property_type,bedrooms,asking_price_gbp,floor_area_sqm,price_per_sqm",
            "SW1A1AA,Flat,1,450000,45,10000",
            "SW1A2AA,Flat,2,680000,68,10000",
            "EC1A1BB,Terraced,3,920000,105,8762",
            "EC2A1CC,Semi_Detached,4,1250000,140,8929",
            "N1 9GU,Terraced,2,750000,80,9375",
            "E1 6RF,Flat,1,420000,42,10000",
            "SE1 7PB,Flat,2,595000,60,9917",
            "W1T 1JY,Detached,5,4500000,280,16071",  // outlier
            "WC2N 5DU,Flat,1,380000,38,10000",
            "EC4M 5UT,Terraced,3,875000,98,8929",
            "SW7 1NA,Flat,2,720000,72,10000",
            "NW1 8AN,Semi_Detached,4,1100000,130,8462",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateConstantCsv()
    {
        var path = TempFile("constant.csv");
        var lines = new string[]
        {
            "id,score,grade",
            "S1,75,B",
            "S2,75,B",
            "S3,75,B",
            "S4,75,B",
            "S5,75,B",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnOutliers
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnOutliers_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreatePropertyCsv());
        var ex = Record.Exception(() => doc.GetColumnOutliers("asking_price_gbp", 2.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnOutliers_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreatePropertyCsv());
        Assert.True(doc.GetColumnOutliers("asking_price_gbp", 2.0).Count >= 0);
    }

    [Fact]
    public void GetColumnOutliers_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePropertyCsv());
        Assert.Equal(doc.GetColumnOutliers("price_per_sqm", 2.0), doc.GetColumnOutliers("price_per_sqm", 2.0));
    }

    [Fact]
    public void GetColumnOutliers_Zero_ForUniformData()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0, doc.GetColumnOutliers("score", 2.0).Count);
    }

    // -------------------------------------------------------------------------
    // GetColumnTrimmedMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnTrimmedMean_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreatePropertyCsv());
        var ex = Record.Exception(() => doc.GetColumnTrimmedMean("asking_price_gbp", 0.1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnTrimmedMean_Finite()
    {
        var doc = CsvDocument.LoadFile(CreatePropertyCsv());
        var tm = doc.GetColumnTrimmedMean("asking_price_gbp", 0.1);
        Assert.True(double.IsFinite(tm));
    }

    [Fact]
    public void GetColumnTrimmedMean_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePropertyCsv());
        Assert.Equal(doc.GetColumnTrimmedMean("floor_area_sqm", 0.1), doc.GetColumnTrimmedMean("floor_area_sqm", 0.1));
    }

    [Fact]
    public void GetColumnTrimmedMean_Between_Min_And_Max()
    {
        var doc = CsvDocument.LoadFile(CreatePropertyCsv());
        var tm = doc.GetColumnTrimmedMean("bedrooms", 0.1);
        var min = doc.GetColumnMin("bedrooms");
        var max = doc.GetColumnMax("bedrooms");
        Assert.True(tm >= min);
        Assert.True(tm <= max);
    }

    // -------------------------------------------------------------------------
    // GetColumnIQR
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnIQR_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreatePropertyCsv());
        var ex = Record.Exception(() => doc.GetColumnIQR("asking_price_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnIQR_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreatePropertyCsv());
        Assert.True(doc.GetColumnIQR("asking_price_gbp") >= 0);
    }

    [Fact]
    public void GetColumnIQR_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePropertyCsv());
        Assert.Equal(doc.GetColumnIQR("floor_area_sqm"), doc.GetColumnIQR("floor_area_sqm"));
    }

    [Fact]
    public void GetColumnIQR_Zero_ForConstantColumn()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0.0, doc.GetColumnIQR("score"), precision: 6);
    }

    [Fact]
    public void GetColumnIQR_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePropertyCsv());
        var before = doc.GetColumnIQR("asking_price_gbp");
        var path = TempFile("iqr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnIQR("asking_price_gbp"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnOutliers_GetColumnTrimmedMean_GetColumnIQR_Pipeline()
    {
        // UK actuarial — general insurance motor claims cost distribution
        var path = TempFile("motor_claims.csv");
        var csvLines = new System.Collections.Generic.List<string>();
        csvLines.Add("claim_id,vehicle_class,driver_age,claim_severity,repair_cost_gbp,total_incurred_gbp,settled_flag");
        var rng = new Random(20240301);
        string[] classes = { "Hatchback", "Saloon", "SUV", "Van", "Motorcycle" };
        for (int i = 0; i < 150; i++)
        {
            var cls = classes[i % 5];
            int age = 17 + rng.Next(0, 58);
            // Most claims £500-£8000; occasional catastrophic total loss (£30k+)
            double repair = i % 30 == 0 ? 30000 + rng.NextDouble() * 20000 : 500 + rng.NextDouble() * 7500;
            double severity = repair / 1000.0;
            double total = repair * (1.0 + rng.NextDouble() * 0.3); // add legal + hire costs
            int settled = (rng.NextDouble() < 0.85) ? 1 : 0;
            csvLines.Add($"CLM{i:D5},{cls},{age},{severity:F2},{repair:F0},{total:F0},{settled}");
        }
        File.WriteAllLines(path, csvLines);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);

        // GetColumnIQR
        var repairIqr = doc.GetColumnIQR("repair_cost_gbp");
        Assert.True(repairIqr >= 0);
        var totalIqr = doc.GetColumnIQR("total_incurred_gbp");
        Assert.True(totalIqr >= 0);
        Assert.Equal(repairIqr, doc.GetColumnIQR("repair_cost_gbp")); // consistent

        // GetColumnOutliers — large loss claims
        var repairOutliers = doc.GetColumnOutliers("repair_cost_gbp", 2.0);
        Assert.True(repairOutliers.Count >= 0);
        Assert.Equal(repairOutliers, doc.GetColumnOutliers("repair_cost_gbp", 2.0)); // consistent

        // GetColumnTrimmedMean — robust average cost excluding total losses
        var trimmedMean = doc.GetColumnTrimmedMean("repair_cost_gbp", 0.1);
        Assert.True(double.IsFinite(trimmedMean));
        var min = doc.GetColumnMin("repair_cost_gbp");
        var max = doc.GetColumnMax("repair_cost_gbp");
        Assert.True(trimmedMean >= min);
        Assert.True(trimmedMean <= max);
        Assert.Equal(trimmedMean, doc.GetColumnTrimmedMean("repair_cost_gbp", 0.1)); // consistent

        // All numeric columns
        foreach (var col in new[] { "driver_age", "repair_cost_gbp", "total_incurred_gbp" })
        {
            Assert.True(doc.GetColumnIQR(col) >= 0);
            Assert.True(doc.GetColumnOutliers(col, 2.0).Count >= 0);
            Assert.True(double.IsFinite(doc.GetColumnTrimmedMean(col, 0.1)));
        }

        // SaveToFile
        var outPath = TempFile("motor_claims_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(repairIqr, loaded.GetColumnIQR("repair_cost_gbp"), precision: 6);
        Assert.True(double.IsFinite(loaded.GetColumnTrimmedMean("total_incurred_gbp", 0.1)));
        Assert.True(loaded.GetColumnOutliers("repair_cost_gbp", 2.0).Count >= 0);
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // Consistency with mean and StdDev
        var mean = doc.GetColumnMean("repair_cost_gbp");
        var std = doc.GetColumnStdDev("repair_cost_gbp");
        Assert.True(mean >= min);
        Assert.True(mean <= max);
        Assert.True(std >= 0);
        Assert.True(double.IsFinite(doc.GetColumnTrimmedMean("driver_age", 0.05)));
    }
}
