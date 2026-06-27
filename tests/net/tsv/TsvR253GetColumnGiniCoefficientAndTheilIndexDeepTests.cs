// Tests for TsvDocument.GetColumnGiniCoefficient, GetColumnTheilIndex deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R253

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R253: Tests for TsvDocument.GetColumnGiniCoefficient, GetColumnTheilIndex deeper.
/// GetColumnGiniCoefficient(colName): returns Gini coefficient [0,1] for a numeric column.
/// GetColumnTheilIndex(colName): returns Theil T entropy-based inequality measure.
/// Covers: GetColumnGiniCoefficient no-throw; GetColumnGiniCoefficient in [0,1];
/// GetColumnGiniCoefficient zero for equal; GetColumnGiniCoefficient consistent;
/// GetColumnGiniCoefficient save-load;
/// GetColumnTheilIndex no-throw; GetColumnTheilIndex non-negative; GetColumnTheilIndex consistent;
/// GetColumnTheilIndex save-load;
/// dogfood CreateDoc→GetColumnGiniCoefficient→GetColumnTheilIndex pipeline.
/// </summary>
public class TsvR253GetColumnGiniCoefficientAndTheilIndexDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR253GetColumnGiniCoefficientAndTheilIndexDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR253_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("household_id\tincome_gbp\texpenditure_gbp\tsavings_gbp");
        var rng = new Random(20240901);
        // Lognormal income distribution (realistic)
        for (int i = 0; i < 100; i++)
        {
            double logInc = rng.NextGaussian2(10.5, 0.6);
            double income = Math.Exp(logInc);
            double expenditure = income * (0.7 + rng.NextDouble() * 0.25);
            double savings = income - expenditure;
            sb.AppendLine($"HH{i:D5}\t{income:F0}\t{expenditure:F0}\t{savings:F0}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateEqualTsv()
    {
        var path = TempFile("equal.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tincome");
        for (int i = 0; i < 20; i++)
            sb.AppendLine($"{i}\t50000");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnGiniCoefficient
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnGiniCoefficient_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnGiniCoefficient("income_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnGiniCoefficient_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var gini = doc.GetColumnGiniCoefficient("income_gbp");
        Assert.True(gini >= 0.0 && gini <= 1.0);
    }

    [Fact]
    public void GetColumnGiniCoefficient_Zero_ForEqual()
    {
        var doc = TsvDocument.LoadFile(CreateEqualTsv());
        Assert.Equal(0.0, doc.GetColumnGiniCoefficient("income"), precision: 6);
    }

    [Fact]
    public void GetColumnGiniCoefficient_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnGiniCoefficient("income_gbp"), doc.GetColumnGiniCoefficient("income_gbp"));
    }

    [Fact]
    public void GetColumnGiniCoefficient_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnGiniCoefficient("income_gbp");
        var path = TempFile("gini_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnGiniCoefficient("income_gbp"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnTheilIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnTheilIndex_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnTheilIndex("income_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnTheilIndex_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnTheilIndex("income_gbp") >= 0.0);
    }

    [Fact]
    public void GetColumnTheilIndex_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnTheilIndex("income_gbp"), doc.GetColumnTheilIndex("income_gbp"));
    }

    [Fact]
    public void GetColumnTheilIndex_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnTheilIndex("expenditure_gbp");
        var path = TempFile("theil_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnTheilIndex("expenditure_gbp"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnGini_GetColumnTheil_Pipeline()
    {
        // ONS Wealth and Assets Survey — household wealth distribution analysis
        // Gini coefficient and Theil index for total wealth, financial wealth, property wealth
        var path = TempFile("wealth_assets_survey.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("household_id\tregion\ttotal_wealth_gbp\tfinancial_wealth_gbp\tproperty_wealth_gbp\tpension_wealth_gbp\tphysical_wealth_gbp\tnum_persons\ttenure_type");
        var rng = new Random(20240115);
        string[] regions = { "London", "South_East", "East_of_England", "West_Midlands", "North_West", "Yorkshire", "Scotland", "Wales" };
        string[] tenures = { "Owner_occupied_outright", "Owner_occupied_mortgage", "Private_rented", "Social_rented" };
        for (int i = 0; i < 200; i++)
        {
            var region = regions[i % regions.Length];
            var tenure = tenures[i % tenures.Length];
            // Pareto-distributed wealth (more realistic than lognormal for top tail)
            double u = rng.NextDouble();
            double totalWealth = u < 0.7 ?
                (5000 + rng.NextDouble() * 195000) : // lower 70%
                (200000 + rng.NextDouble() * 2800000); // upper 30%
            // London premium
            if (region == "London") totalWealth *= 1.4;
            // Renters have lower wealth
            if (tenure.Contains("rented")) totalWealth *= 0.4;
            double financial = totalWealth * (0.1 + rng.NextDouble() * 0.2);
            double property = tenure.StartsWith("Owner") ? totalWealth * (0.3 + rng.NextDouble() * 0.4) : 0;
            double pension = totalWealth * (0.2 + rng.NextDouble() * 0.25);
            double physical = totalWealth * (0.05 + rng.NextDouble() * 0.1);
            int persons = 1 + rng.Next(4);
            sb.AppendLine($"HH{i:D6}\t{region}\t{totalWealth:F0}\t{financial:F0}\t{property:F0}\t{pension:F0}\t{physical:F0}\t{persons}\t{tenure}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(9, doc.ColumnCount);

        // GetColumnGiniCoefficient — wealth Gini (UK ≈ 0.6-0.7)
        var giniTotal = doc.GetColumnGiniCoefficient("total_wealth_gbp");
        Assert.True(giniTotal >= 0.0 && giniTotal <= 1.0);
        Assert.Equal(giniTotal, doc.GetColumnGiniCoefficient("total_wealth_gbp")); // consistent

        var giniFinancial = doc.GetColumnGiniCoefficient("financial_wealth_gbp");
        Assert.True(giniFinancial >= 0.0 && giniFinancial <= 1.0);

        var giniProperty = doc.GetColumnGiniCoefficient("property_wealth_gbp");
        Assert.True(giniProperty >= 0.0 && giniProperty <= 1.0);

        var giniPension = doc.GetColumnGiniCoefficient("pension_wealth_gbp");
        Assert.True(giniPension >= 0.0 && giniPension <= 1.0);

        // GetColumnTheilIndex
        var theilTotal = doc.GetColumnTheilIndex("total_wealth_gbp");
        Assert.True(theilTotal >= 0.0);
        Assert.Equal(theilTotal, doc.GetColumnTheilIndex("total_wealth_gbp")); // consistent

        var theilFinancial = doc.GetColumnTheilIndex("financial_wealth_gbp");
        Assert.True(theilFinancial >= 0.0);

        var theilPension = doc.GetColumnTheilIndex("pension_wealth_gbp");
        Assert.True(theilPension >= 0.0);

        // Basic stats
        Assert.True(doc.GetColumnMin("total_wealth_gbp") <= doc.GetColumnMax("total_wealth_gbp"));
        Assert.True(doc.GetColumnMean("total_wealth_gbp") > 0.0);

        // IQR and MAD
        var iqrWealth = doc.GetColumnInterquartileRange("total_wealth_gbp");
        Assert.True(iqrWealth >= 0.0);

        // SaveToFile
        var outPath = TempFile("wealth_assets_survey_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(giniTotal, loaded.GetColumnGiniCoefficient("total_wealth_gbp"), precision: 8);
        Assert.Equal(giniFinancial, loaded.GetColumnGiniCoefficient("financial_wealth_gbp"), precision: 8);
        Assert.Equal(theilTotal, loaded.GetColumnTheilIndex("total_wealth_gbp"), precision: 8);
        Assert.Equal(theilFinancial, loaded.GetColumnTheilIndex("financial_wealth_gbp"), precision: 8);

        // Equal distribution test
        var pathEqual = TempFile("equal_wealth.tsv");
        var sbEqual = new StringBuilder();
        sbEqual.AppendLine("hh\twealth");
        for (int i = 0; i < 50; i++)
            sbEqual.AppendLine($"HH{i:D4}\t100000");
        File.WriteAllText(pathEqual, sbEqual.ToString());
        var docEqual = TsvDocument.LoadFile(pathEqual);
        Assert.Equal(0.0, docEqual.GetColumnGiniCoefficient("wealth"), precision: 6);
    }
}

internal static class TsvR253RandomExtensions
{
    internal static double NextGaussian2(this Random rng, double mean, double stdDev)
    {
        double u1 = 1.0 - rng.NextDouble();
        double u2 = 1.0 - rng.NextDouble();
        double z = Math.Sqrt(-2.0 * Math.Log(u1)) * Math.Sin(2.0 * Math.PI * u2);
        return mean + stdDev * z;
    }
}
