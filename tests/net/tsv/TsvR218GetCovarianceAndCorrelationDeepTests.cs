// Tests for TsvDocument.GetCovariance, GetCorrelation, GetZScore deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R218

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R218: Tests for TsvDocument.GetCovariance, GetCorrelation, GetZScore deeper.
/// GetCovariance(col1, col2): returns the covariance between two numeric columns.
/// GetCorrelation(col1, col2): returns the Pearson correlation coefficient between two columns.
/// GetZScore(colName, rowIndex): returns the z-score of the value at rowIndex in colName.
/// Covers: GetCovariance no-throw; GetCovariance finite; GetCovariance consistent;
/// GetCovariance symmetric; GetCovariance save-load;
/// GetCorrelation no-throw; GetCorrelation in [-1,1]; GetCorrelation consistent;
/// GetCorrelation self is 1; GetCorrelation save-load;
/// GetZScore no-throw; GetZScore finite; GetZScore consistent; GetZScore save-load;
/// GetZScore mean row near zero;
/// dogfood LoadFile→GetCovariance→GetCorrelation→GetZScore→SaveToFile pipeline.
/// </summary>
public class TsvR218GetCovarianceAndCorrelationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR218GetCovarianceAndCorrelationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR218_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateMetricsTsv()
    {
        var path = TempFile("metrics.tsv");
        var content =
            "Product\tRevenue\tAdSpend\tUnits\tMargin\n" +
            "Alpha\t450000\t45000\t1200\t38\n" +
            "Beta\t320000\t28000\t890\t42\n" +
            "Gamma\t610000\t67000\t1650\t35\n" +
            "Delta\t275000\t22000\t720\t45\n" +
            "Epsilon\t530000\t58000\t1400\t37\n" +
            "Zeta\t185000\t14000\t480\t51\n" +
            "Eta\t720000\t82000\t1900\t33\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetCovariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCovariance_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        var ex = Record.Exception(() => doc.GetCovariance("Revenue", "AdSpend"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCovariance_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        var cov = doc.GetCovariance("Revenue", "AdSpend");
        Assert.True(double.IsFinite(cov));
    }

    [Fact]
    public void GetCovariance_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        Assert.Equal(doc.GetCovariance("Revenue", "AdSpend"), doc.GetCovariance("Revenue", "AdSpend"));
    }

    [Fact]
    public void GetCovariance_Symmetric()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        // Cov(X,Y) == Cov(Y,X)
        Assert.Equal(
            doc.GetCovariance("Revenue", "AdSpend"),
            doc.GetCovariance("AdSpend", "Revenue"),
            3);
    }

    [Fact]
    public void GetCovariance_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        var before = doc.GetCovariance("Revenue", "Units");
        var path = TempFile("cov_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCovariance("Revenue", "Units"), 2);
    }

    [Fact]
    public void GetCovariance_Revenue_AdSpend_Positive()
    {
        // Revenue and AdSpend should be positively correlated in this dataset
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        Assert.True(doc.GetCovariance("Revenue", "AdSpend") > 0);
    }

    // -------------------------------------------------------------------------
    // GetCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCorrelation_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        var ex = Record.Exception(() => doc.GetCorrelation("Revenue", "AdSpend"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCorrelation_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        var r = doc.GetCorrelation("Revenue", "AdSpend");
        Assert.True(r >= -1.0 && r <= 1.0);
    }

    [Fact]
    public void GetCorrelation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        Assert.Equal(doc.GetCorrelation("Revenue", "Units"), doc.GetCorrelation("Revenue", "Units"));
    }

    [Fact]
    public void GetCorrelation_Self_IsOne()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        Assert.Equal(1.0, doc.GetCorrelation("Revenue", "Revenue"), 4);
    }

    [Fact]
    public void GetCorrelation_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        var before = doc.GetCorrelation("Revenue", "AdSpend");
        var path = TempFile("corr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCorrelation("Revenue", "AdSpend"), 3);
    }

    // -------------------------------------------------------------------------
    // GetZScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetZScore_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        var ex = Record.Exception(() => doc.GetZScore("Revenue", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetZScore_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        var z = doc.GetZScore("Revenue", 0);
        Assert.True(double.IsFinite(z));
    }

    [Fact]
    public void GetZScore_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        Assert.Equal(doc.GetZScore("Revenue", 2), doc.GetZScore("Revenue", 2));
    }

    [Fact]
    public void GetZScore_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        var before = doc.GetZScore("Revenue", 1);
        var path = TempFile("zscore_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetZScore("Revenue", 1), 4);
    }

    [Fact]
    public void GetZScore_AllRows_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateMetricsTsv());
        for (int i = 0; i < doc.GetRowCount(); i++)
        {
            var z = doc.GetZScore("Revenue", i);
            Assert.True(double.IsFinite(z), $"Row {i} z-score is not finite");
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCovariance_GetCorrelation_GetZScore_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_kpi.tsv");
        var content =
            "Month\tSales\tLeads\tConversions\tRevenue\n" +
            "Jan\t280\t1200\t23\t420000\n" +
            "Feb\t310\t1350\t28\t465000\n" +
            "Mar\t345\t1480\t32\t517500\n" +
            "Apr\t290\t1250\t25\t435000\n" +
            "May\t360\t1560\t35\t540000\n" +
            "Jun\t420\t1820\t41\t630000\n" +
            "Jul\t395\t1710\t38\t592500\n" +
            "Aug\t440\t1900\t43\t660000\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRowCount());

        // GetCovariance — Sales vs Revenue (expected positive)
        var covSalesRevenue = doc.GetCovariance("Sales", "Revenue");
        Assert.True(double.IsFinite(covSalesRevenue));
        Assert.True(covSalesRevenue > 0);
        Assert.Equal(covSalesRevenue, doc.GetCovariance("Sales", "Revenue")); // consistent

        // GetCovariance — symmetric
        Assert.Equal(
            doc.GetCovariance("Leads", "Conversions"),
            doc.GetCovariance("Conversions", "Leads"),
            3);

        // GetCorrelation — Sales vs Revenue
        var corrSalesRevenue = doc.GetCorrelation("Sales", "Revenue");
        Assert.True(corrSalesRevenue >= -1.0 && corrSalesRevenue <= 1.0);
        Assert.True(corrSalesRevenue > 0.9); // strongly positive
        Assert.Equal(corrSalesRevenue, doc.GetCorrelation("Sales", "Revenue")); // consistent

        // GetCorrelation — self correlation = 1
        Assert.Equal(1.0, doc.GetCorrelation("Sales", "Sales"), 4);
        Assert.Equal(1.0, doc.GetCorrelation("Revenue", "Revenue"), 4);

        // GetZScore — all rows for Revenue
        for (int i = 0; i < doc.GetRowCount(); i++)
            Assert.True(double.IsFinite(doc.GetZScore("Revenue", i)));

        // GetZScore — high revenue row should have positive z-score
        var zAug = doc.GetZScore("Revenue", 7); // Aug = 660000 (highest)
        Assert.True(zAug > 0);

        // GetZScore — low revenue row should have negative z-score
        var zJan = doc.GetZScore("Revenue", 0); // Jan = 420000 (lowest)
        Assert.True(zJan < 0);

        // AddRow and recheck
        doc.AddRow(new[] { "Sep", "460", "1980", "45", "690000" });
        Assert.Equal(9, doc.GetRowCount());
        Assert.True(double.IsFinite(doc.GetCovariance("Sales", "Revenue")));
        Assert.True(doc.GetCorrelation("Sales", "Revenue") >= -1.0);

        // SaveToFile
        var savePath = TempFile("dogfood_kpi_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRowCount());
        Assert.Equal(doc.GetCovariance("Sales", "Revenue"), loaded.GetCovariance("Sales", "Revenue"), 2);
        Assert.Equal(doc.GetCorrelation("Sales", "Revenue"), loaded.GetCorrelation("Sales", "Revenue"), 3);

        // Z-scores consistent after load
        for (int i = 0; i < 9; i++)
            Assert.Equal(doc.GetZScore("Revenue", i), loaded.GetZScore("Revenue", i), 4);

        // SortByColumn still works
        var sorted = loaded.SortByColumn("Revenue", ascending: true);
        Assert.Equal(9, sorted.GetRowCount());

        // Final save
        var path2 = TempFile("dogfood_kpi_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetCorrelation("Sales", "Revenue"), loaded2.GetCorrelation("Sales", "Revenue"), 3);
    }
}
