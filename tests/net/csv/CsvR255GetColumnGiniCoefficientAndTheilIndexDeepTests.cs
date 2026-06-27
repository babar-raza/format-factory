// Tests for CsvDocument.GetColumnGiniCoefficient, GetColumnTheilIndex deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R255

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R255: Tests for CsvDocument.GetColumnGiniCoefficient, GetColumnTheilIndex deeper.
/// GetColumnGiniCoefficient(colName): returns Gini coefficient [0,1] for a numeric column.
/// GetColumnTheilIndex(colName): returns Theil T entropy-based inequality measure.
/// Covers: GetColumnGiniCoefficient no-throw; GetColumnGiniCoefficient in [0,1];
/// GetColumnGiniCoefficient zero for equal; GetColumnGiniCoefficient consistent;
/// GetColumnGiniCoefficient save-load;
/// GetColumnTheilIndex no-throw; GetColumnTheilIndex non-negative; GetColumnTheilIndex consistent;
/// GetColumnTheilIndex save-load;
/// dogfood CreateDoc→GetColumnGiniCoefficient→GetColumnTheilIndex pipeline.
/// </summary>
public class CsvR255GetColumnGiniCoefficientAndTheilIndexDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR255GetColumnGiniCoefficientAndTheilIndexDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR255_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("company_id,revenue_gbpm,employees,market_cap_gbpm,rd_spend_gbpm");
        var rng = new Random(20241001);
        for (int i = 0; i < 100; i++)
        {
            double revenue = Math.Exp(3 + rng.NextDouble() * 4); // lognormal
            int employees = (int)(revenue * (5 + rng.NextDouble() * 15));
            double marketCap = revenue * (0.8 + rng.NextDouble() * 3.0);
            double rd = revenue * rng.NextDouble() * 0.15;
            sb.AppendLine($"CO{i:D5},{revenue:F2},{employees},{marketCap:F2},{rd:F2}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateEqualCsv()
    {
        var path = TempFile("equal.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,revenue");
        for (int i = 0; i < 20; i++)
            sb.AppendLine($"{i},1000");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnGiniCoefficient
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnGiniCoefficient_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnGiniCoefficient("revenue_gbpm"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnGiniCoefficient_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var gini = doc.GetColumnGiniCoefficient("revenue_gbpm");
        Assert.True(gini >= 0.0 && gini <= 1.0);
    }

    [Fact]
    public void GetColumnGiniCoefficient_Zero_ForEqual()
    {
        var doc = CsvDocument.LoadFile(CreateEqualCsv());
        Assert.Equal(0.0, doc.GetColumnGiniCoefficient("revenue"), precision: 6);
    }

    [Fact]
    public void GetColumnGiniCoefficient_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnGiniCoefficient("revenue_gbpm"), doc.GetColumnGiniCoefficient("revenue_gbpm"));
    }

    [Fact]
    public void GetColumnGiniCoefficient_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnGiniCoefficient("market_cap_gbpm");
        var path = TempFile("gini_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnGiniCoefficient("market_cap_gbpm"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnTheilIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnTheilIndex_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnTheilIndex("revenue_gbpm"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnTheilIndex_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnTheilIndex("revenue_gbpm") >= 0.0);
    }

    [Fact]
    public void GetColumnTheilIndex_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnTheilIndex("market_cap_gbpm"), doc.GetColumnTheilIndex("market_cap_gbpm"));
    }

    [Fact]
    public void GetColumnTheilIndex_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnTheilIndex("rd_spend_gbpm");
        var path = TempFile("theil_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnTheilIndex("rd_spend_gbpm"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnGini_GetColumnTheil_Pipeline()
    {
        // Competition economics — CMA (Competition and Markets Authority) market concentration analysis
        // Pharmaceutical sector: revenue inequality across ATC3 therapeutic classes for UK market
        var path = TempFile("cma_pharma_market_concentration.csv");
        var sb = new StringBuilder();
        sb.AppendLine("company_id,atc3_class,company_name,branded_revenue_gbpm,generic_revenue_gbpm,total_revenue_gbpm,market_share_pct,hhi_contribution,r_and_d_spend_gbpm,employees_uk,patent_portfolio_count");
        var rng = new Random(20241101);

        string[] atcClasses = { "C10A", "A10B", "L01X", "N06A", "R03A", "M01A", "B01A", "J01C", "C09A", "V04C" };
        string[] companies = {
            "AstraZeneca", "GSK", "Pfizer_UK", "Novartis_UK", "Roche_UK", "Eli_Lilly", "MSD_UK",
            "Bristol_Myers", "AbbVie_UK", "Novo_Nordisk_UK", "Sanofi_UK", "Bayer_UK",
            "Boehringer", "Astellas", "Takeda_UK", "Daiichi_Sankyo", "Servier",
            "Almirall", "Ipsen", "Recordati"
        };

        for (int i = 0; i < 200; i++)
        {
            var company = companies[i % companies.Length];
            var atc = atcClasses[i % atcClasses.Length];
            // Power law revenue distribution (market leaders dominate)
            double branded = i < 5 ? (500 + rng.NextDouble() * 1500) :
                            i < 20 ? (50 + rng.NextDouble() * 450) :
                            (1 + rng.NextDouble() * 49);
            double generic = branded * (rng.NextDouble() * 0.5);
            double total = branded + generic;
            double share = total / (branded * 50) * 100; // approximate
            double hhiContrib = share * share;
            double rd = total * (0.08 + rng.NextDouble() * 0.15);
            int employees = (int)(total * (3 + rng.NextDouble() * 8));
            int patents = (int)(rd * (2 + rng.NextDouble() * 5));
            sb.AppendLine($"CO{i:D4},{atc},{company},{branded:F2},{generic:F2},{total:F2},{share:F4},{hhiContrib:F4},{rd:F2},{employees},{patents}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(11, doc.ColumnCount);

        // GetColumnGiniCoefficient — revenue concentration (CMA uses for competition assessment)
        var giniTotal = doc.GetColumnGiniCoefficient("total_revenue_gbpm");
        Assert.True(giniTotal >= 0.0 && giniTotal <= 1.0);
        Assert.Equal(giniTotal, doc.GetColumnGiniCoefficient("total_revenue_gbpm")); // consistent

        var giniBranded = doc.GetColumnGiniCoefficient("branded_revenue_gbpm");
        Assert.True(giniBranded >= 0.0 && giniBranded <= 1.0);

        var giniRd = doc.GetColumnGiniCoefficient("r_and_d_spend_gbpm");
        Assert.True(giniRd >= 0.0 && giniRd <= 1.0);

        var giniPatents = doc.GetColumnGiniCoefficient("patent_portfolio_count");
        Assert.True(giniPatents >= 0.0 && giniPatents <= 1.0);

        // GetColumnTheilIndex — information-theoretic inequality (Theil T)
        var theilTotal = doc.GetColumnTheilIndex("total_revenue_gbpm");
        Assert.True(theilTotal >= 0.0);
        Assert.Equal(theilTotal, doc.GetColumnTheilIndex("total_revenue_gbpm")); // consistent

        var theilBranded = doc.GetColumnTheilIndex("branded_revenue_gbpm");
        Assert.True(theilBranded >= 0.0);

        var theilRd = doc.GetColumnTheilIndex("r_and_d_spend_gbpm");
        Assert.True(theilRd >= 0.0);

        // Basic stats
        Assert.True(doc.GetColumnMin("total_revenue_gbpm") <= doc.GetColumnMax("total_revenue_gbpm"));
        Assert.True(doc.GetColumnMean("total_revenue_gbpm") > 0.0);
        Assert.True(doc.GetColumnStdDev("total_revenue_gbpm") >= 0.0);

        // IQR for comparison
        var iqr = doc.GetColumnInterquartileRange("total_revenue_gbpm");
        Assert.True(iqr >= 0.0);

        // SaveToFile
        var outPath = TempFile("cma_pharma_market_concentration_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(giniTotal, loaded.GetColumnGiniCoefficient("total_revenue_gbpm"), precision: 8);
        Assert.Equal(giniBranded, loaded.GetColumnGiniCoefficient("branded_revenue_gbpm"), precision: 8);
        Assert.Equal(theilTotal, loaded.GetColumnTheilIndex("total_revenue_gbpm"), precision: 8);
        Assert.Equal(theilRd, loaded.GetColumnTheilIndex("r_and_d_spend_gbpm"), precision: 8);

        // Equal distribution
        var pathEqual = TempFile("equal_revenue.csv");
        var sbEqual = new StringBuilder();
        sbEqual.AppendLine("company,revenue");
        for (int i = 0; i < 40; i++)
            sbEqual.AppendLine($"CO{i:D3},5000");
        File.WriteAllText(pathEqual, sbEqual.ToString());
        var docEqual = CsvDocument.LoadFile(pathEqual);
        Assert.Equal(0.0, docEqual.GetColumnGiniCoefficient("revenue"), precision: 6);
    }
}
