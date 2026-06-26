// Tests for TsvDocument.GetKurtosis, GetEntropy, GetVarianceCoefficient deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R224

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R224: Tests for TsvDocument.GetKurtosis, GetEntropy, GetVarianceCoefficient deeper.
/// GetKurtosis(colName): returns the kurtosis statistic for a numeric column.
/// GetEntropy(colName): returns the Shannon entropy of the column's value distribution.
/// GetVarianceCoefficient(colName): returns StdDev/Mean (coefficient of variation).
/// Covers: GetKurtosis no-throw; GetKurtosis finite; GetKurtosis consistent; GetKurtosis save-load;
/// GetEntropy no-throw; GetEntropy non-negative; GetEntropy consistent; GetEntropy save-load;
/// GetVarianceCoefficient no-throw; GetVarianceCoefficient non-negative; GetVarianceCoefficient consistent;
/// GetVarianceCoefficient save-load; GetVarianceCoefficient approx-stddev-over-mean;
/// dogfood LoadFile→GetKurtosis→GetEntropy→GetVarianceCoefficient→SaveToFile pipeline.
/// </summary>
public class TsvR224GetKurtosisAndEntropyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR224GetKurtosisAndEntropyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR224_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCityTsv()
    {
        var path = TempFile("cities.tsv");
        var content =
            "City\tPopulation\tAreaKm2\tDensity\tMedianAge\tGDPBillions\n" +
            "CityA\t2850000\t1472\t1936\t38.2\t185.4\n" +
            "CityB\t4120000\t2058\t2002\t35.6\t312.8\n" +
            "CityC\t980000\t890\t1101\t41.3\t98.2\n" +
            "CityD\t7650000\t3094\t2472\t32.8\t620.5\n" +
            "CityE\t1540000\t1120\t1375\t39.7\t145.9\n" +
            "CityF\t3280000\t1785\t1837\t36.4\t251.3\n" +
            "CityG\t620000\t650\t954\t44.1\t72.6\n" +
            "CityH\t9200000\t4850\t1897\t31.5\t812.4\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetKurtosis_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateCityTsv());
        var ex = Record.Exception(() => doc.GetKurtosis("Population"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetKurtosis_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateCityTsv());
        Assert.True(double.IsFinite(doc.GetKurtosis("Population")));
    }

    [Fact]
    public void GetKurtosis_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCityTsv());
        Assert.Equal(doc.GetKurtosis("Density"), doc.GetKurtosis("Density"));
    }

    [Fact]
    public void GetKurtosis_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCityTsv());
        var before = doc.GetKurtosis("GDPBillions");
        var path = TempFile("kurt_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetKurtosis("GDPBillions"), 4);
    }

    // -------------------------------------------------------------------------
    // GetEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEntropy_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateCityTsv());
        var ex = Record.Exception(() => doc.GetEntropy("MedianAge"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetEntropy_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateCityTsv());
        Assert.True(doc.GetEntropy("Population") >= 0.0);
    }

    [Fact]
    public void GetEntropy_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCityTsv());
        Assert.Equal(doc.GetEntropy("Density"), doc.GetEntropy("Density"));
    }

    [Fact]
    public void GetEntropy_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCityTsv());
        var before = doc.GetEntropy("AreaKm2");
        var path = TempFile("ent_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetEntropy("AreaKm2"), 4);
    }

    // -------------------------------------------------------------------------
    // GetVarianceCoefficient
    // -------------------------------------------------------------------------

    [Fact]
    public void GetVarianceCoefficient_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateCityTsv());
        var ex = Record.Exception(() => doc.GetVarianceCoefficient("Population"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetVarianceCoefficient_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateCityTsv());
        Assert.True(doc.GetVarianceCoefficient("GDPBillions") >= 0.0);
    }

    [Fact]
    public void GetVarianceCoefficient_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCityTsv());
        Assert.Equal(doc.GetVarianceCoefficient("Density"), doc.GetVarianceCoefficient("Density"));
    }

    [Fact]
    public void GetVarianceCoefficient_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCityTsv());
        var before = doc.GetVarianceCoefficient("Population");
        var path = TempFile("cv_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetVarianceCoefficient("Population"), 4);
    }

    [Fact]
    public void GetVarianceCoefficient_Approx_StdDev_Over_Mean()
    {
        var doc = TsvDocument.LoadFile(CreateCityTsv());
        var cv = doc.GetVarianceCoefficient("GDPBillions");
        var mean = doc.GetMean("GDPBillions");
        var stddev = doc.GetStdDev("GDPBillions");
        if (mean > 0)
            Assert.Equal(stddev / mean, cv, 4);
        else
            Assert.True(cv >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetKurtosis_GetEntropy_GetVarianceCoefficient_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_traffic.tsv");
        var content =
            "Intersection\tMorningPeak\tEveningPeak\tAvgSpeed\tAccidents\tThroughput\n" +
            "INT_001\t1250\t1480\t42.3\t2\t8500\n" +
            "INT_002\t980\t1120\t38.7\t1\t7200\n" +
            "INT_003\t2100\t2350\t28.5\t5\t12400\n" +
            "INT_004\t650\t720\t48.2\t0\t5100\n" +
            "INT_005\t1850\t1990\t33.4\t3\t10800\n" +
            "INT_006\t3200\t3580\t22.1\t8\t16500\n" +
            "INT_007\t420\t510\t52.6\t0\t3800\n" +
            "INT_008\t1680\t1820\t35.9\t2\t9600\n" +
            "INT_009\t2450\t2750\t26.8\t6\t14200\n" +
            "INT_010\t890\t980\t41.5\t1\t6700\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRowCount());

        // GetKurtosis — MorningPeak
        var kurtPeak = doc.GetKurtosis("MorningPeak");
        Assert.True(double.IsFinite(kurtPeak));
        Assert.Equal(kurtPeak, doc.GetKurtosis("MorningPeak")); // consistent

        // GetKurtosis — Accidents (likely high kurtosis due to skew)
        var kurtAcc = doc.GetKurtosis("Accidents");
        Assert.True(double.IsFinite(kurtAcc));

        // GetEntropy — MorningPeak
        var entPeak = doc.GetEntropy("MorningPeak");
        Assert.True(entPeak >= 0.0);
        Assert.Equal(entPeak, doc.GetEntropy("MorningPeak")); // consistent

        // GetEntropy — AvgSpeed
        var entSpeed = doc.GetEntropy("AvgSpeed");
        Assert.True(entSpeed >= 0.0);

        // GetVarianceCoefficient — Throughput
        var cvThroughput = doc.GetVarianceCoefficient("Throughput");
        Assert.True(cvThroughput >= 0.0);
        Assert.Equal(cvThroughput, doc.GetVarianceCoefficient("Throughput")); // consistent

        // GetVarianceCoefficient approx StdDev/Mean
        var meanTP = doc.GetMean("Throughput");
        var stdTP = doc.GetStdDev("Throughput");
        if (meanTP > 0)
            Assert.Equal(stdTP / meanTP, cvThroughput, 4);

        // GetVarianceCoefficient — Accidents
        var cvAcc = doc.GetVarianceCoefficient("Accidents");
        Assert.True(cvAcc >= 0.0);

        // AddRow and recheck
        doc.AddRow(new[] { "INT_011", "1560", "1720", "37.2", "2", "9100" });
        Assert.Equal(11, doc.GetRowCount());
        Assert.True(double.IsFinite(doc.GetKurtosis("MorningPeak")));
        Assert.True(doc.GetEntropy("Throughput") >= 0.0);

        // SaveToFile
        var savePath = TempFile("dogfood_traffic_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(11, loaded.GetRowCount());
        Assert.Equal(doc.GetKurtosis("MorningPeak"), loaded.GetKurtosis("MorningPeak"), 4);
        Assert.Equal(doc.GetEntropy("AvgSpeed"), loaded.GetEntropy("AvgSpeed"), 4);
        Assert.Equal(doc.GetVarianceCoefficient("Throughput"), loaded.GetVarianceCoefficient("Throughput"), 4);

        // Final save
        var path2 = TempFile("dogfood_traffic_v2.tsv");
        loaded.SaveToFile(path2);
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetKurtosis("EveningPeak"), loaded2.GetKurtosis("EveningPeak"), 4);
        Assert.Equal(loaded.GetEntropy("Accidents"), loaded2.GetEntropy("Accidents"), 4);
        Assert.Equal(loaded.GetVarianceCoefficient("MorningPeak"), loaded2.GetVarianceCoefficient("MorningPeak"), 4);
    }
}
