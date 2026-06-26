// Tests for CsvDocument.GetKurtosis, GetEntropy, GetVarianceCoefficient deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R226

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R226: Tests for CsvDocument.GetKurtosis, GetEntropy, GetVarianceCoefficient deeper.
/// GetKurtosis(colName): returns the kurtosis statistic for a numeric column.
/// GetEntropy(colName): returns the Shannon entropy of the column value distribution.
/// GetVarianceCoefficient(colName): returns StdDev/Mean (coefficient of variation).
/// Covers: GetKurtosis no-throw; GetKurtosis finite; GetKurtosis consistent; GetKurtosis save-load;
/// GetEntropy no-throw; GetEntropy non-negative; GetEntropy consistent; GetEntropy save-load;
/// GetVarianceCoefficient no-throw; GetVarianceCoefficient non-negative;
/// GetVarianceCoefficient consistent; GetVarianceCoefficient save-load;
/// GetVarianceCoefficient approx-stddev-over-mean;
/// dogfood LoadFile→GetKurtosis→GetEntropy→GetVarianceCoefficient→SaveToFile pipeline.
/// </summary>
public class CsvR226GetKurtosisAndEntropyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR226GetKurtosisAndEntropyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR226_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateRiskCsv()
    {
        var path = TempFile("risk.csv");
        var content =
            "AssetId,PD,LGD,EAD,RWA,ExpectedLoss\n" +
            "A001,0.02,0.45,500000,225000,4500\n" +
            "A002,0.05,0.60,280000,168000,8400\n" +
            "A003,0.01,0.35,950000,332500,3325\n" +
            "A004,0.12,0.75,180000,135000,16200\n" +
            "A005,0.03,0.50,620000,310000,9300\n" +
            "A006,0.08,0.65,340000,221000,17680\n" +
            "A007,0.01,0.30,1200000,360000,3600\n" +
            "A008,0.25,0.80,95000,76000,19000\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetKurtosis_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateRiskCsv());
        var ex = Record.Exception(() => doc.GetKurtosis("PD"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetKurtosis_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateRiskCsv());
        Assert.True(double.IsFinite(doc.GetKurtosis("LGD")));
    }

    [Fact]
    public void GetKurtosis_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateRiskCsv());
        Assert.Equal(doc.GetKurtosis("EAD"), doc.GetKurtosis("EAD"));
    }

    [Fact]
    public void GetKurtosis_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateRiskCsv());
        var before = doc.GetKurtosis("RWA");
        var path = TempFile("kurt_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetKurtosis("RWA"), 4);
    }

    // -------------------------------------------------------------------------
    // GetEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEntropy_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateRiskCsv());
        var ex = Record.Exception(() => doc.GetEntropy("PD"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetEntropy_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateRiskCsv());
        Assert.True(doc.GetEntropy("LGD") >= 0.0);
    }

    [Fact]
    public void GetEntropy_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateRiskCsv());
        Assert.Equal(doc.GetEntropy("ExpectedLoss"), doc.GetEntropy("ExpectedLoss"));
    }

    [Fact]
    public void GetEntropy_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateRiskCsv());
        var before = doc.GetEntropy("PD");
        var path = TempFile("ent_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetEntropy("PD"), 4);
    }

    // -------------------------------------------------------------------------
    // GetVarianceCoefficient
    // -------------------------------------------------------------------------

    [Fact]
    public void GetVarianceCoefficient_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateRiskCsv());
        var ex = Record.Exception(() => doc.GetVarianceCoefficient("EAD"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetVarianceCoefficient_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateRiskCsv());
        Assert.True(doc.GetVarianceCoefficient("PD") >= 0.0);
    }

    [Fact]
    public void GetVarianceCoefficient_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateRiskCsv());
        Assert.Equal(doc.GetVarianceCoefficient("RWA"), doc.GetVarianceCoefficient("RWA"));
    }

    [Fact]
    public void GetVarianceCoefficient_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateRiskCsv());
        var before = doc.GetVarianceCoefficient("ExpectedLoss");
        var path = TempFile("cv_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetVarianceCoefficient("ExpectedLoss"), 4);
    }

    [Fact]
    public void GetVarianceCoefficient_Approx_StdDev_Over_Mean()
    {
        var doc = CsvDocument.LoadFile(CreateRiskCsv());
        var cv = doc.GetVarianceCoefficient("EAD");
        var mean = doc.GetMean("EAD");
        var stddev = doc.GetStdDev("EAD");
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
        var path = TempFile("dogfood_patients.csv");
        var content =
            "PatientId,HbA1c,FastingGlucose,BMI,SystolicBP,DiastolicBP,CholesterolTotal\n" +
            "P001,5.4,88,22.3,115,75,175\n" +
            "P002,7.8,142,31.5,148,92,240\n" +
            "P003,5.1,82,20.8,108,70,160\n" +
            "P004,9.2,185,38.2,162,98,280\n" +
            "P005,6.1,102,25.7,125,80,195\n" +
            "P006,5.8,94,23.9,118,76,182\n" +
            "P007,8.5,168,35.4,155,95,265\n" +
            "P008,6.8,118,27.8,132,84,210\n" +
            "P009,5.2,85,21.5,110,72,168\n" +
            "P010,10.5,215,42.1,172,105,295\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRowCount());

        // GetKurtosis — HbA1c (right-skewed diabetes marker)
        var kurtHba = doc.GetKurtosis("HbA1c");
        Assert.True(double.IsFinite(kurtHba));
        Assert.Equal(kurtHba, doc.GetKurtosis("HbA1c")); // consistent

        // GetKurtosis — BMI
        var kurtBmi = doc.GetKurtosis("BMI");
        Assert.True(double.IsFinite(kurtBmi));

        // GetEntropy — FastingGlucose
        var entGlucose = doc.GetEntropy("FastingGlucose");
        Assert.True(entGlucose >= 0.0);
        Assert.Equal(entGlucose, doc.GetEntropy("FastingGlucose")); // consistent

        // GetEntropy — CholesterolTotal
        var entChol = doc.GetEntropy("CholesterolTotal");
        Assert.True(entChol >= 0.0);

        // GetVarianceCoefficient — HbA1c
        var cvHba = doc.GetVarianceCoefficient("HbA1c");
        Assert.True(cvHba >= 0.0);
        Assert.Equal(cvHba, doc.GetVarianceCoefficient("HbA1c")); // consistent

        // GetVarianceCoefficient approx StdDev/Mean
        var meanHba = doc.GetMean("HbA1c");
        var stdHba = doc.GetStdDev("HbA1c");
        if (meanHba > 0)
            Assert.Equal(stdHba / meanHba, cvHba, 4);

        // GetVarianceCoefficient — SystolicBP
        var cvBP = doc.GetVarianceCoefficient("SystolicBP");
        Assert.True(cvBP >= 0.0);

        // AddRow and recheck
        doc.AddRow(new[] { "P011", "6.5", "112", "26.8", "128", "82", "202" });
        Assert.Equal(11, doc.GetRowCount());
        Assert.True(double.IsFinite(doc.GetKurtosis("BMI")));
        Assert.True(doc.GetEntropy("HbA1c") >= 0.0);

        // SaveToFile
        var savePath = TempFile("dogfood_patients_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(11, loaded.GetRowCount());
        Assert.Equal(doc.GetKurtosis("HbA1c"), loaded.GetKurtosis("HbA1c"), 4);
        Assert.Equal(doc.GetEntropy("FastingGlucose"), loaded.GetEntropy("FastingGlucose"), 4);
        Assert.Equal(doc.GetVarianceCoefficient("BMI"), loaded.GetVarianceCoefficient("BMI"), 4);

        // GetColumnNames cross-check
        var cols = loaded.GetColumnNames();
        Assert.Contains("HbA1c", cols);
        Assert.Contains("CholesterolTotal", cols);

        // Final save
        var path2 = TempFile("dogfood_patients_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetKurtosis("SystolicBP"), loaded2.GetKurtosis("SystolicBP"), 4);
        Assert.Equal(loaded.GetEntropy("BMI"), loaded2.GetEntropy("BMI"), 4);
        Assert.Equal(loaded.GetVarianceCoefficient("CholesterolTotal"), loaded2.GetVarianceCoefficient("CholesterolTotal"), 4);
    }
}
