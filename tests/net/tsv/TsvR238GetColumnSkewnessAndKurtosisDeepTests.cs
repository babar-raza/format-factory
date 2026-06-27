// Tests for TsvDocument.GetColumnSkewness, GetColumnKurtosis, GetColumnStdDev deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R238

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R238: Tests for TsvDocument.GetColumnSkewness, GetColumnKurtosis, GetColumnStdDev deeper.
/// GetColumnSkewness(columnName): returns the skewness of numeric values in the column.
/// GetColumnKurtosis(columnName): returns the excess kurtosis of numeric values in the column.
/// GetColumnStdDev(columnName): returns the standard deviation of numeric values in the column.
/// Covers: GetColumnSkewness no-throw; GetColumnSkewness finite; GetColumnSkewness consistent;
/// GetColumnSkewness zero for symmetric data;
/// GetColumnKurtosis no-throw; GetColumnKurtosis finite; GetColumnKurtosis consistent;
/// GetColumnStdDev no-throw; GetColumnStdDev non-negative; GetColumnStdDev consistent;
/// GetColumnStdDev zero for constant column; GetColumnStdDev save-load;
/// dogfood CreateDoc→GetColumnSkewness→GetColumnKurtosis→GetColumnStdDev pipeline.
/// </summary>
public class TsvR238GetColumnSkewnessAndKurtosisDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR238GetColumnSkewnessAndKurtosisDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR238_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateFinancialReturnsTsv()
    {
        var path = TempFile("returns.tsv");
        var lines = new System.Collections.Generic.List<string>
        {
            "fund\treturn_pct\tvolatility\tsharpe\tbeta",
            "GBP_Bond_A\t3.2\t2.1\t1.52\t0.12",
            "GBP_Bond_B\t2.8\t1.8\t1.56\t0.09",
            "UK_Equity_A\t12.4\t15.3\t0.81\t0.98",
            "UK_Equity_B\t-3.1\t18.7\t-0.17\t1.21",
            "Global_Equity\t9.7\t14.2\t0.68\t0.87",
            "EM_Equity\t-8.4\t22.6\t-0.37\t1.35",
            "Property_REIT\t7.3\t8.9\t0.82\t0.45",
            "Infrastructure\t6.8\t6.2\t1.10\t0.31",
            "Absolute_Return\t4.1\t3.8\t1.08\t0.18",
            "High_Yield_Bond\t5.6\t6.7\t0.84\t0.38",
            "IG_Credit\t3.9\t3.2\t1.22\t0.21",
            "Cash_MM\t4.5\t0.3\t15.00\t0.01",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateConstantTsv()
    {
        var path = TempFile("constant.tsv");
        var lines = new string[]
        {
            "id\tvalue\tcategory",
            "R1\t42\tX",
            "R2\t42\tY",
            "R3\t42\tX",
            "R4\t42\tZ",
            "R5\t42\tX",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnSkewness_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateFinancialReturnsTsv());
        var ex = Record.Exception(() => doc.GetColumnSkewness("return_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnSkewness_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateFinancialReturnsTsv());
        var skew = doc.GetColumnSkewness("return_pct");
        Assert.True(double.IsFinite(skew));
    }

    [Fact]
    public void GetColumnSkewness_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateFinancialReturnsTsv());
        Assert.Equal(doc.GetColumnSkewness("volatility"), doc.GetColumnSkewness("volatility"));
    }

    [Fact]
    public void GetColumnSkewness_NearZero_ForSymmetricData()
    {
        var path = TempFile("symmetric.tsv");
        File.WriteAllLines(path, new[]
        {
            "id\tvalue",
            "A\t-3",
            "B\t-2",
            "C\t-1",
            "D\t0",
            "E\t1",
            "F\t2",
            "G\t3",
        });
        var doc = TsvDocument.LoadFile(path);
        var skew = doc.GetColumnSkewness("value");
        Assert.True(Math.Abs(skew) < 0.5);
    }

    // -------------------------------------------------------------------------
    // GetColumnKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnKurtosis_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateFinancialReturnsTsv());
        var ex = Record.Exception(() => doc.GetColumnKurtosis("return_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnKurtosis_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateFinancialReturnsTsv());
        var kurt = doc.GetColumnKurtosis("return_pct");
        Assert.True(double.IsFinite(kurt));
    }

    [Fact]
    public void GetColumnKurtosis_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateFinancialReturnsTsv());
        Assert.Equal(doc.GetColumnKurtosis("sharpe"), doc.GetColumnKurtosis("sharpe"));
    }

    // -------------------------------------------------------------------------
    // GetColumnStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStdDev_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateFinancialReturnsTsv());
        var ex = Record.Exception(() => doc.GetColumnStdDev("return_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnStdDev_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateFinancialReturnsTsv());
        Assert.True(doc.GetColumnStdDev("return_pct") >= 0);
    }

    [Fact]
    public void GetColumnStdDev_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateFinancialReturnsTsv());
        Assert.Equal(doc.GetColumnStdDev("volatility"), doc.GetColumnStdDev("volatility"));
    }

    [Fact]
    public void GetColumnStdDev_Zero_ForConstantColumn()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0.0, doc.GetColumnStdDev("value"), precision: 6);
    }

    [Fact]
    public void GetColumnStdDev_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateFinancialReturnsTsv());
        var before = doc.GetColumnStdDev("beta");
        var path = TempFile("sd_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnStdDev("beta"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnSkewness_GetColumnKurtosis_GetColumnStdDev_Pipeline()
    {
        // Asset management — multi-asset portfolio return distribution analysis
        var path = TempFile("portfolio_returns.tsv");
        var lines = new System.Collections.Generic.List<string>();
        lines.Add("date\tequity_return\tbond_return\tcommodity_return\talternative_return\tportfolio_return");
        var rng = new Random(20240101);
        for (int i = 0; i < 120; i++) // 10 years of monthly returns
        {
            double eq = (rng.NextDouble() - 0.45) * 12.0;
            double bd = (rng.NextDouble() - 0.42) * 4.0;
            double cm = (rng.NextDouble() - 0.50) * 8.0;
            double alt = (rng.NextDouble() - 0.44) * 6.0;
            double port = 0.4 * eq + 0.3 * bd + 0.15 * cm + 0.15 * alt;
            lines.Add($"2014-{(i % 12 + 1):D2}-01\t{eq:F3}\t{bd:F3}\t{cm:F3}\t{alt:F3}\t{port:F3}");
        }
        File.WriteAllLines(path, lines);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(120, doc.RowCount);

        // GetColumnStdDev
        var eqStd = doc.GetColumnStdDev("equity_return");
        Assert.True(eqStd > 0);
        var bdStd = doc.GetColumnStdDev("bond_return");
        Assert.True(bdStd > 0);
        Assert.True(eqStd > bdStd); // equities more volatile than bonds
        Assert.Equal(eqStd, doc.GetColumnStdDev("equity_return")); // consistent

        // GetColumnSkewness
        var eqSkew = doc.GetColumnSkewness("equity_return");
        Assert.True(double.IsFinite(eqSkew));
        var portSkew = doc.GetColumnSkewness("portfolio_return");
        Assert.True(double.IsFinite(portSkew));
        Assert.Equal(eqSkew, doc.GetColumnSkewness("equity_return")); // consistent

        // GetColumnKurtosis
        var eqKurt = doc.GetColumnKurtosis("equity_return");
        Assert.True(double.IsFinite(eqKurt));
        var bdKurt = doc.GetColumnKurtosis("bond_return");
        Assert.True(double.IsFinite(bdKurt));
        Assert.Equal(eqKurt, doc.GetColumnKurtosis("equity_return")); // consistent

        // All columns
        foreach (var col in new[] { "equity_return", "bond_return", "commodity_return", "alternative_return", "portfolio_return" })
        {
            Assert.True(doc.GetColumnStdDev(col) >= 0);
            Assert.True(double.IsFinite(doc.GetColumnSkewness(col)));
            Assert.True(double.IsFinite(doc.GetColumnKurtosis(col)));
        }

        // SaveToFile
        var outPath = TempFile("portfolio_returns_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(eqStd, loaded.GetColumnStdDev("equity_return"), precision: 6);
        Assert.True(double.IsFinite(loaded.GetColumnSkewness("portfolio_return")));
        Assert.True(double.IsFinite(loaded.GetColumnKurtosis("bond_return")));
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // GetColumnMean / GetColumnMin / GetColumnMax consistency with StdDev
        var mean = doc.GetColumnMean("portfolio_return");
        var min = doc.GetColumnMin("portfolio_return");
        var max = doc.GetColumnMax("portfolio_return");
        var std = doc.GetColumnStdDev("portfolio_return");
        Assert.True(mean >= min);
        Assert.True(mean <= max);
        Assert.True(std <= (max - min));
    }
}
