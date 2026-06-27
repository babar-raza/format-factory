// Tests for TsvDocument.GetColumnOutliers, GetColumnOutlierCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R262

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R262: Tests for TsvDocument.GetColumnOutliers, GetColumnOutlierCount deeper.
/// GetColumnOutliers(colName): returns the list of outlier values (IQR method: outside Q1-1.5*IQR or Q3+1.5*IQR).
/// GetColumnOutlierCount(colName): returns the count of outliers in the column.
/// Covers: GetColumnOutlierCount no-throw; GetColumnOutlierCount non-negative;
/// GetColumnOutlierCount consistent; GetColumnOutlierCount zero for uniform;
/// GetColumnOutlierCount save-load; GetColumnOutliers no-throw;
/// GetColumnOutliers count equals GetColumnOutlierCount; GetColumnOutliers consistent;
/// GetColumnOutliers save-load; GetColumnOutlierCount le RowCount;
/// dogfood CreateDoc→GetColumnOutliers→GetColumnOutlierCount pipeline.
/// </summary>
public class TsvR262GetColumnOutliersAndOutlierCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR262GetColumnOutliersAndOutlierCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR262_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id\tsalary\tage\tscore");
        var rng = new Random(20240815);
        // Mostly normal values with a few obvious outliers
        for (int i = 0; i < 90; i++)
            sb.AppendLine($"{i}\t{30000 + rng.Next(40000)}\t{22 + rng.Next(45)}\t{50 + rng.Next(50)}");
        // Add clear outliers
        sb.AppendLine("90\t500000\t85\t99");
        sb.AppendLine("91\t1000000\t90\t100");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tvalue");
        for (int i = 0; i < 50; i++)
            sb.AppendLine($"{i}\t100");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnOutlierCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnOutlierCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnOutlierCount("salary"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnOutlierCount_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnOutlierCount("salary") >= 0);
    }

    [Fact]
    public void GetColumnOutlierCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnOutlierCount("salary"), doc.GetColumnOutlierCount("salary"));
    }

    [Fact]
    public void GetColumnOutlierCount_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0, doc.GetColumnOutlierCount("value"));
    }

    [Fact]
    public void GetColumnOutlierCount_Le_RowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnOutlierCount("salary") <= doc.RowCount);
    }

    [Fact]
    public void GetColumnOutlierCount_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnOutlierCount("salary");
        var path = TempFile("oc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnOutlierCount("salary"));
    }

    // -------------------------------------------------------------------------
    // GetColumnOutliers
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnOutliers_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnOutliers("salary"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnOutliers_Count_Equals_OutlierCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnOutlierCount("salary"), doc.GetColumnOutliers("salary").Count);
    }

    [Fact]
    public void GetColumnOutliers_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var o1 = doc.GetColumnOutliers("salary");
        var o2 = doc.GetColumnOutliers("salary");
        Assert.Equal(o1, o2);
    }

    [Fact]
    public void GetColumnOutliers_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnOutliers("salary");
        var path = TempFile("outliers_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnOutliers("salary"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnOutliers_GetColumnOutlierCount_Pipeline()
    {
        // Healthcare — NHS England GP Practice Prescribing Cost Analysis
        // Detecting outlier prescribing costs by practice for anomaly detection and audit
        var path = TempFile("gp_prescribing.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("practice_code\tpractice_name\tlist_size\tcost_per_patient\titems_per_patient\tantibiotic_rate\topioid_rate");

        var rng = new Random(20240901);
        string[] regions = { "London", "Midlands", "North West", "South East", "South West" };

        for (int i = 0; i < 180; i++)
        {
            string code = $"E{81000 + i:D5}";
            string name = $"The {regions[i % regions.Length]} Surgery";
            int listSize = 3000 + rng.Next(12000);
            double costPerPt = Math.Round(80 + rng.NextDouble() * 60, 2);
            double itemsPerPt = Math.Round(16 + rng.NextDouble() * 20, 1);
            double abxRate = Math.Round(0.4 + rng.NextDouble() * 0.3, 3);
            double opioidRate = Math.Round(0.05 + rng.NextDouble() * 0.15, 3);
            sb.AppendLine($"{code}\t{name}\t{listSize}\t{costPerPt}\t{itemsPerPt}\t{abxRate}\t{opioidRate}");
        }
        // Add clear outlier practices
        sb.AppendLine("E99001\tHigh Volume Practice\t20000\t250.50\t45.0\t0.85\t0.45");
        sb.AppendLine("E99002\tHigh Cost Dispensing Practice\t4500\t310.20\t38.5\t0.72\t0.38");
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(182, doc.RowCount);
        Assert.Equal(7, doc.ColumnCount);

        // Outlier count for cost_per_patient (2 outliers added)
        var outlierCountCost = doc.GetColumnOutlierCount("cost_per_patient");
        Assert.True(outlierCountCost >= 0);
        Assert.True(outlierCountCost <= doc.RowCount);
        Assert.Equal(outlierCountCost, doc.GetColumnOutlierCount("cost_per_patient")); // consistent

        // Outlier values for cost_per_patient
        var outliersCost = doc.GetColumnOutliers("cost_per_patient");
        Assert.Equal(outlierCountCost, outliersCost.Count);
        Assert.Equal(outliersCost, doc.GetColumnOutliers("cost_per_patient")); // consistent

        // Outlier count for list_size
        var outlierCountList = doc.GetColumnOutlierCount("list_size");
        Assert.True(outlierCountList >= 0);
        Assert.True(outlierCountList <= doc.RowCount);
        var outliersListSize = doc.GetColumnOutliers("list_size");
        Assert.Equal(outlierCountList, outliersListSize.Count);

        // Outlier count for items_per_patient
        var outlierCountItems = doc.GetColumnOutlierCount("items_per_patient");
        Assert.True(outlierCountItems >= 0);
        var outliersItems = doc.GetColumnOutliers("items_per_patient");
        Assert.Equal(outlierCountItems, outliersItems.Count);

        // Opioid rate outliers
        var outlierCountOpioid = doc.GetColumnOutlierCount("opioid_rate");
        Assert.True(outlierCountOpioid >= 0);
        var outliersOpioid = doc.GetColumnOutliers("opioid_rate");
        Assert.Equal(outlierCountOpioid, outliersOpioid.Count);

        // Basic column stats
        Assert.True(doc.GetColumnMean("cost_per_patient") > 0);
        Assert.True(doc.GetColumnStdDev("cost_per_patient") > 0);

        // SaveToFile
        var outPath = TempFile("gp_prescribing_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(outlierCountCost, loaded.GetColumnOutlierCount("cost_per_patient"));
        Assert.Equal(outliersCost, loaded.GetColumnOutliers("cost_per_patient"));

        // Uniform sub-test
        var path2 = TempFile("uniform_gp.tsv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("code\tcost_per_patient");
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"E{i:D5}\t100");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = TsvDocument.LoadFile(path2);
        Assert.Equal(0, doc2.GetColumnOutlierCount("cost_per_patient"));
        Assert.Empty(doc2.GetColumnOutliers("cost_per_patient"));
    }
}
