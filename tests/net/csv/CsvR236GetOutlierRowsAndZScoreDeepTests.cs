// Tests for CsvDocument.GetOutlierCount, GetZScores, GetNormalizedColumn deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R236

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R236: Tests for CsvDocument.GetOutlierCount, GetZScores, GetNormalizedColumn deeper.
/// GetOutlierCount(columnName, zThreshold): returns count of values with |z-score| > zThreshold.
/// GetZScores(columnName): returns the z-score for each row value in the column.
/// GetNormalizedColumn(columnName): returns values scaled to [0,1] using min-max normalisation.
/// Covers: GetOutlierCount no-throw; GetOutlierCount non-negative; GetOutlierCount consistent;
/// GetOutlierCount zero for uniform; GetOutlierCount detects extreme outlier; GetOutlierCount save-load;
/// GetZScores no-throw; GetZScores non-null; GetZScores count equals row count; GetZScores consistent;
/// GetZScores save-load;
/// GetNormalizedColumn no-throw; GetNormalizedColumn non-null; GetNormalizedColumn in range;
/// GetNormalizedColumn consistent; GetNormalizedColumn save-load;
/// dogfood CreateDoc→GetOutlierCount→GetZScores→GetNormalizedColumn→SaveToFile pipeline.
/// </summary>
public class CsvR236GetOutlierRowsAndZScoreDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR236GetOutlierRowsAndZScoreDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR236_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCreditRiskCsv()
    {
        var path = TempFile("credit.csv");
        // Normal credit scores plus one extreme outlier (250000 income)
        File.WriteAllText(path,
            "applicant_id,credit_score,annual_income,debt_ratio,loan_amount,years_employed\n" +
            "A001,720,68500,0.28,25000,8\n" +
            "A002,685,52000,0.35,18000,4\n" +
            "A003,745,82000,0.22,35000,12\n" +
            "A004,612,45000,0.42,12000,2\n" +
            "A005,698,61000,0.31,22000,6\n" +
            "A006,758,250000,0.18,85000,15\n" +  // income outlier
            "A007,672,55000,0.38,16000,3\n" +
            "A008,731,74000,0.26,28000,9\n" +
            "A009,695,58000,0.33,20000,5\n" +
            "A010,719,67000,0.29,24000,7\n" +
            "A011,742,79000,0.23,32000,11\n" +
            "A012,661,50000,0.40,14000,3\n");
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        File.WriteAllText(path, "id,value\n1,100\n2,100\n3,100\n4,100\n5,100\n6,100\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetOutlierCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOutlierCount_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        var ex = Record.Exception(() => doc.GetOutlierCount("annual_income", 2.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetOutlierCount_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        Assert.True(doc.GetOutlierCount("annual_income", 2.0) >= 0);
    }

    [Fact]
    public void GetOutlierCount_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        Assert.Equal(
            doc.GetOutlierCount("annual_income", 2.0),
            doc.GetOutlierCount("annual_income", 2.0));
    }

    [Fact]
    public void GetOutlierCount_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0, doc.GetOutlierCount("value", 2.0));
    }

    [Fact]
    public void GetOutlierCount_Detects_IncomeOutlier()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        Assert.True(doc.GetOutlierCount("annual_income", 2.0) >= 1);
    }

    [Fact]
    public void GetOutlierCount_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        var before = doc.GetOutlierCount("annual_income", 2.0);
        var path = TempFile("oc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetOutlierCount("annual_income", 2.0));
    }

    // -------------------------------------------------------------------------
    // GetZScores
    // -------------------------------------------------------------------------

    [Fact]
    public void GetZScores_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        var ex = Record.Exception(() => doc.GetZScores("credit_score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetZScores_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        Assert.NotNull(doc.GetZScores("credit_score"));
    }

    [Fact]
    public void GetZScores_CountEqualsRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        Assert.Equal(doc.GetRowCount(), doc.GetZScores("credit_score").Length);
    }

    [Fact]
    public void GetZScores_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        var z1 = doc.GetZScores("annual_income");
        var z2 = doc.GetZScores("annual_income");
        Assert.Equal(z1.Length, z2.Length);
    }

    [Fact]
    public void GetZScores_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        var before = doc.GetZScores("debt_ratio").Length;
        var path = TempFile("zs_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetZScores("debt_ratio").Length);
    }

    // -------------------------------------------------------------------------
    // GetNormalizedColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNormalizedColumn_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        var ex = Record.Exception(() => doc.GetNormalizedColumn("credit_score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNormalizedColumn_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        Assert.NotNull(doc.GetNormalizedColumn("credit_score"));
    }

    [Fact]
    public void GetNormalizedColumn_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        foreach (var v in doc.GetNormalizedColumn("credit_score"))
        {
            Assert.True(v >= 0.0);
            Assert.True(v <= 1.0);
        }
    }

    [Fact]
    public void GetNormalizedColumn_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        var n1 = doc.GetNormalizedColumn("loan_amount");
        var n2 = doc.GetNormalizedColumn("loan_amount");
        Assert.Equal(n1.Count, n2.Count);
    }

    [Fact]
    public void GetNormalizedColumn_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCreditRiskCsv());
        var before = doc.GetNormalizedColumn("years_employed").Count;
        var path = TempFile("nc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNormalizedColumn("years_employed").Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetOutlierCount_GetZScores_GetNormalizedColumn_SaveToFile_Pipeline()
    {
        // Quality control — manufacturing defect detection across 12 batches
        var path = TempFile("dogfood_qc.csv");
        File.WriteAllText(path,
            "batch_id,tensile_strength_mpa,hardness_hv,surface_roughness_ra,density_gcm3,yield_stress_mpa,elongation_pct,defect_count\n" +
            "B001,485.2,182.5,0.85,7.85,342.8,22.5,2\n" +
            "B002,492.8,186.2,0.92,7.82,348.5,21.8,1\n" +
            "B003,478.5,179.8,0.78,7.88,338.2,23.2,3\n" +
            "B004,498.4,189.5,0.95,7.80,352.4,21.2,1\n" +
            "B005,488.6,184.2,0.88,7.83,345.2,22.1,2\n" +
            "B006,215.8,98.5,4.85,7.45,142.5,8.5,48\n" +  // defective batch — extreme outlier
            "B007,491.2,185.8,0.90,7.82,347.8,21.9,1\n" +
            "B008,482.5,181.2,0.82,7.86,340.8,22.8,2\n" +
            "B009,495.8,187.5,0.93,7.81,350.2,21.5,1\n" +
            "B010,486.4,183.2,0.87,7.84,343.8,22.3,2\n" +
            "B011,494.2,188.5,0.91,7.81,349.5,21.6,1\n" +
            "B012,480.8,180.8,0.83,7.87,339.5,23.0,2\n");

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());
        Assert.Equal(8, doc.GetColumnCount());

        // GetOutlierCount — tensile strength anomaly (B006 is extreme)
        var tensileOutliers = doc.GetOutlierCount("tensile_strength_mpa", 2.0);
        Assert.True(tensileOutliers >= 0);
        Assert.True(tensileOutliers >= 1); // B006 is extreme
        Assert.Equal(tensileOutliers, doc.GetOutlierCount("tensile_strength_mpa", 2.0)); // consistent

        // defect_count outliers
        var defectOutliers = doc.GetOutlierCount("defect_count", 2.0);
        Assert.True(defectOutliers >= 1); // B006 has 48 defects vs ~2 normal

        // Uniform threshold
        var strictOutliers = doc.GetOutlierCount("tensile_strength_mpa", 4.0);
        Assert.True(strictOutliers >= 0);
        Assert.True(strictOutliers <= tensileOutliers);

        // GetZScores — tensile strength z-scores
        var zTensile = doc.GetZScores("tensile_strength_mpa");
        Assert.NotNull(zTensile);
        Assert.Equal(12, zTensile.Length);
        Assert.Equal(zTensile.Length, doc.GetZScores("tensile_strength_mpa").Length); // consistent

        var zHardness = doc.GetZScores("hardness_hv");
        Assert.NotNull(zHardness);
        Assert.Equal(12, zHardness.Length);

        // GetNormalizedColumn — hardness normalised
        var normHardness = doc.GetNormalizedColumn("hardness_hv");
        Assert.NotNull(normHardness);
        Assert.Equal(12, normHardness.Count);
        foreach (var v in normHardness) { Assert.True(v >= 0.0); Assert.True(v <= 1.0); }
        Assert.Equal(normHardness.Count, doc.GetNormalizedColumn("hardness_hv").Count); // consistent

        var normDensity = doc.GetNormalizedColumn("density_gcm3");
        Assert.NotNull(normDensity);
        foreach (var v in normDensity) { Assert.True(v >= 0.0); Assert.True(v <= 1.0); }

        // SaveToFile
        var out1 = TempFile("dogfood_qc_out.csv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(tensileOutliers, loaded.GetOutlierCount("tensile_strength_mpa", 2.0));
        Assert.Equal(12, loaded.GetZScores("tensile_strength_mpa").Length);
        var loadedNorm = loaded.GetNormalizedColumn("hardness_hv");
        Assert.Equal(12, loadedNorm.Count);
        for (int i = 0; i < normHardness.Count; i++)
            Assert.Equal(normHardness[i], loadedNorm[i], precision: 6);

        // AddRow
        loaded.AddRow(new[] { "B013", "489.5", "185.5", "0.89", "7.83", "346.5", "22.0", "1" });
        Assert.Equal(13, loaded.GetRowCount());
        Assert.Equal(13, loaded.GetZScores("tensile_strength_mpa").Length);

        // Uniform column has no outliers
        var uniformDoc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0, uniformDoc.GetOutlierCount("value", 2.0));

        // Final save
        var out2 = TempFile("dogfood_qc_v2.csv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = CsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.True(loaded2.GetOutlierCount("defect_count", 2.0) >= 0);
        Assert.NotNull(loaded2.GetNormalizedColumn("tensile_strength_mpa"));
    }
}
