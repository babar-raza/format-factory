// Tests for TsvDocument.GetCumulativeSum, GetMovingAverage, GetPercentileRank deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R231

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R231: Tests for TsvDocument.GetCumulativeSum, GetMovingAverage, GetPercentileRank deeper.
/// GetCumulativeSum(columnName): returns an array of cumulative sums for the column.
/// GetMovingAverage(columnName, windowSize): returns moving averages with the given window.
/// GetPercentileRank(columnName, value): returns the percentile rank (0-100) of the given value.
/// Covers: GetCumulativeSum no-throw; GetCumulativeSum count equals row count; GetCumulativeSum consistent;
/// GetCumulativeSum last equals column sum; GetCumulativeSum save-load;
/// GetMovingAverage no-throw; GetMovingAverage count leq row count; GetMovingAverage consistent;
/// GetMovingAverage save-load;
/// GetPercentileRank no-throw; GetPercentileRank in range; GetPercentileRank consistent;
/// GetPercentileRank 100 for max; GetPercentileRank save-load;
/// dogfood CreateDoc→GetCumulativeSum→GetMovingAverage→GetPercentileRank→SaveToFile pipeline.
/// </summary>
public class TsvR231GetCumulativeSumAndMovingAverageDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR231GetCumulativeSumAndMovingAverageDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR231_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSalesTsv()
    {
        var path = TempFile("sales.tsv");
        File.WriteAllText(path,
            "month\trevenue\tunits\tavg_order\tcustomers\n" +
            "Jan\t142500\t2850\t50.0\t1200\n" +
            "Feb\t128400\t2568\t50.0\t1080\n" +
            "Mar\t165200\t3304\t50.0\t1380\n" +
            "Apr\t178900\t3578\t50.0\t1490\n" +
            "May\t195600\t3912\t50.0\t1620\n" +
            "Jun\t212400\t4248\t50.0\t1750\n" +
            "Jul\t198800\t3976\t50.0\t1640\n" +
            "Aug\t205200\t4104\t50.0\t1700\n" +
            "Sep\t222500\t4450\t50.0\t1820\n" +
            "Oct\t248700\t4974\t50.0\t2030\n" +
            "Nov\t285400\t5708\t50.0\t2320\n" +
            "Dec\t315800\t6316\t50.0\t2580\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetCumulativeSum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCumulativeSum_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var ex = Record.Exception(() => doc.GetCumulativeSum("revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCumulativeSum_Count_EqualsRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        Assert.Equal(doc.GetRowCount(), doc.GetCumulativeSum("revenue").Length);
    }

    [Fact]
    public void GetCumulativeSum_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var c1 = doc.GetCumulativeSum("revenue");
        var c2 = doc.GetCumulativeSum("revenue");
        Assert.Equal(c1.Length, c2.Length);
        for (int i = 0; i < c1.Length; i++)
            Assert.Equal(c1[i], c2[i]);
    }

    [Fact]
    public void GetCumulativeSum_LastEqualsColumnSum()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var cumSum = doc.GetCumulativeSum("revenue");
        var colSum = doc.GetColumnSum("revenue");
        Assert.Equal(colSum, cumSum[cumSum.Length - 1], precision: 6);
    }

    [Fact]
    public void GetCumulativeSum_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var before = doc.GetCumulativeSum("units");
        var path = TempFile("cs_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetCumulativeSum("units");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetMovingAverage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMovingAverage_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var ex = Record.Exception(() => doc.GetMovingAverage("revenue", 3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMovingAverage_Count_LeqRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        Assert.True(doc.GetMovingAverage("revenue", 3).Length <= doc.GetRowCount());
    }

    [Fact]
    public void GetMovingAverage_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var m1 = doc.GetMovingAverage("units", 3);
        var m2 = doc.GetMovingAverage("units", 3);
        Assert.Equal(m1.Length, m2.Length);
    }

    [Fact]
    public void GetMovingAverage_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var before = doc.GetMovingAverage("revenue", 3);
        var path = TempFile("ma_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetMovingAverage("revenue", 3);
        Assert.Equal(before.Length, after.Length);
    }

    // -------------------------------------------------------------------------
    // GetPercentileRank
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPercentileRank_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var ex = Record.Exception(() => doc.GetPercentileRank("revenue", 195600));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPercentileRank_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var rank = doc.GetPercentileRank("revenue", 195600);
        Assert.True(rank >= 0.0);
        Assert.True(rank <= 100.0);
    }

    [Fact]
    public void GetPercentileRank_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        Assert.Equal(doc.GetPercentileRank("revenue", 150000), doc.GetPercentileRank("revenue", 150000));
    }

    [Fact]
    public void GetPercentileRank_100_ForMax()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var maxVal = doc.GetColumnMax("revenue");
        var rank = doc.GetPercentileRank("revenue", maxVal);
        Assert.True(rank >= 99.0); // at or near 100
    }

    [Fact]
    public void GetPercentileRank_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var before = doc.GetPercentileRank("units", 3000);
        var path = TempFile("pr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPercentileRank("units", 3000), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCumulativeSum_GetMovingAverage_GetPercentileRank_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_energy_demand.tsv");
        File.WriteAllText(path,
            "week\tgas_demand_gwh\telectricity_gwh\trenewable_gwh\tpeak_load_gw\tco2_intensity\n" +
            "W01\t85200\t42800\t18500\t58.2\t0.185\n" +
            "W02\t88400\t44200\t19200\t60.1\t0.182\n" +
            "W03\t91200\t45800\t20100\t62.4\t0.178\n" +
            "W04\t86800\t43500\t18800\t59.8\t0.183\n" +
            "W05\t78500\t40200\t17200\t55.4\t0.192\n" +
            "W06\t75200\t38800\t16500\t52.8\t0.196\n" +
            "W07\t72800\t37500\t15800\t51.2\t0.201\n" +
            "W08\t69400\t36200\t15200\t49.8\t0.208\n" +
            "W09\t71200\t37100\t15600\t50.9\t0.204\n" +
            "W10\t74800\t38800\t16800\t53.2\t0.198\n" +
            "W11\t79200\t41200\t18000\t56.8\t0.190\n" +
            "W12\t83500\t43500\t19500\t59.2\t0.186\n");

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());
        Assert.Equal(6, doc.GetColumnCount());

        // GetCumulativeSum — gas_demand_gwh
        var cumGas = doc.GetCumulativeSum("gas_demand_gwh");
        Assert.NotNull(cumGas);
        Assert.Equal(12, cumGas.Length);
        // Verify monotone increasing (all values positive)
        for (int i = 1; i < cumGas.Length; i++)
            Assert.True(cumGas[i] >= cumGas[i - 1]);
        // Last value = total sum
        Assert.Equal(doc.GetColumnSum("gas_demand_gwh"), cumGas[11], precision: 6);

        // GetCumulativeSum — electricity_gwh
        var cumElec = doc.GetCumulativeSum("electricity_gwh");
        Assert.Equal(12, cumElec.Length);
        Assert.Equal(doc.GetColumnSum("electricity_gwh"), cumElec[11], precision: 6);

        // Consistent
        var cumGas2 = doc.GetCumulativeSum("gas_demand_gwh");
        for (int i = 0; i < cumGas.Length; i++)
            Assert.Equal(cumGas[i], cumGas2[i], precision: 6);

        // GetMovingAverage — 3-week moving average
        var ma3Gas = doc.GetMovingAverage("gas_demand_gwh", 3);
        Assert.True(ma3Gas.Length <= 12);
        Assert.True(ma3Gas.Length > 0);

        var ma3Elec = doc.GetMovingAverage("electricity_gwh", 3);
        Assert.True(ma3Elec.Length <= 12);

        // 4-week moving average
        var ma4Peak = doc.GetMovingAverage("peak_load_gw", 4);
        Assert.True(ma4Peak.Length <= 12);

        // GetPercentileRank — rank of median gas demand
        var medGas = doc.GetColumnMean("gas_demand_gwh");
        var rankMed = doc.GetPercentileRank("gas_demand_gwh", medGas);
        Assert.True(rankMed >= 0.0);
        Assert.True(rankMed <= 100.0);

        // Max value is at 100th percentile
        var maxGas = doc.GetColumnMax("gas_demand_gwh");
        var rankMax = doc.GetPercentileRank("gas_demand_gwh", maxGas);
        Assert.True(rankMax >= 99.0);

        // Consistent
        Assert.Equal(doc.GetPercentileRank("electricity_gwh", 40000), doc.GetPercentileRank("electricity_gwh", 40000));

        // SaveToFile
        var out1 = TempFile("dogfood_energy_out.tsv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        var loadedCum = loaded.GetCumulativeSum("gas_demand_gwh");
        Assert.Equal(cumGas.Length, loadedCum.Length);
        for (int i = 0; i < cumGas.Length; i++)
            Assert.Equal(cumGas[i], loadedCum[i], precision: 6);

        // AddRow and recompute
        loaded.AddRow(new[] { "W13", "86200", "44500", "19800", "60.2", "0.184" });
        Assert.Equal(13, loaded.GetRowCount());
        var updatedCum = loaded.GetCumulativeSum("gas_demand_gwh");
        Assert.Equal(13, updatedCum.Length);

        // Final save
        var out2 = TempFile("dogfood_energy_v2.tsv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = TsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.Equal(13, loaded2.GetCumulativeSum("gas_demand_gwh").Length);
        Assert.True(loaded2.GetMovingAverage("electricity_gwh", 3).Length <= 13);
        Assert.True(loaded2.GetPercentileRank("gas_demand_gwh", 80000) >= 0.0);
    }
}
