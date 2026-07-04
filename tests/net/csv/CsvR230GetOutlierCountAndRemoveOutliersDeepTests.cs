// Tests for CsvDocument.GetOutlierCount, RemoveOutliers, GetZScore deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R230

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R230: Tests for CsvDocument.GetOutlierCount, RemoveOutliers, GetZScore deeper.
/// GetOutlierCount(columnName): returns the number of outliers in the column (|z| > 2).
/// RemoveOutliers(columnName): returns a new document with outlier rows removed.
/// GetZScore(columnName, rowIndex): returns the z-score of the value at the given row.
/// Covers: GetOutlierCount no-throw; GetOutlierCount non-negative; GetOutlierCount consistent;
/// GetOutlierCount zero for uniform; GetOutlierCount leq row count; GetOutlierCount save-load;
/// RemoveOutliers no-throw; RemoveOutliers non-null; RemoveOutliers count leq original;
/// RemoveOutliers consistent; RemoveOutliers save-load;
/// GetZScore no-throw; GetZScore finite; GetZScore consistent; GetZScore save-load;
/// dogfood CreateDoc→GetOutlierCount→RemoveOutliers→GetZScore→SaveToFile pipeline.
/// </summary>
public class CsvR230GetOutlierCountAndRemoveOutliersDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR230GetOutlierCountAndRemoveOutliersDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR230_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateRetailCsv()
    {
        var path = TempFile("retail.csv");
        File.WriteAllText(path,
            "store_id,weekly_footfall,avg_transaction_gbp,conversion_rate,sq_footage,revenue_k\n" +
            "S001,8200,42.5,0.28,4500,97.2\n" +
            "S002,12400,38.2,0.32,6800,142.8\n" +
            "S003,6800,51.3,0.24,3200,85.4\n" +
            "S004,9500,44.8,0.30,5100,108.6\n" +
            "S005,11200,40.1,0.31,6200,128.4\n" +
            "S006,250,89200,0.92,48000,18500.0\n" + // revenue outlier (flagship/luxury)
            "S007,7800,43.7,0.27,4100,92.3\n" +
            "S008,10600,41.2,0.29,5800,120.1\n" +
            "S009,8900,46.5,0.26,4700,102.8\n" +
            "S010,5,12.3,0.01,200,0.3\n" +     // footfall outlier (kiosk)
            "S011,9100,43.9,0.28,4900,104.7\n" +
            "S012,11800,39.6,0.33,6500,135.9\n");
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        File.WriteAllText(path,
            "id,value\n" +
            "1,50.0\n" +
            "2,50.0\n" +
            "3,50.0\n" +
            "4,50.0\n" +
            "5,50.0\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetOutlierCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOutlierCount_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        var ex = Record.Exception(() => doc.GetOutlierCount("weekly_footfall"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetOutlierCount_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        Assert.True(doc.GetOutlierCount("revenue_k") >= 0);
    }

    [Fact]
    public void GetOutlierCount_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        Assert.Equal(doc.GetOutlierCount("weekly_footfall"), doc.GetOutlierCount("weekly_footfall"));
    }

    [Fact]
    public void GetOutlierCount_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0, doc.GetOutlierCount("value"));
    }

    [Fact]
    public void GetOutlierCount_LeqRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        Assert.True(doc.GetOutlierCount("revenue_k") <= doc.GetRowCount());
    }

    [Fact]
    public void GetOutlierCount_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        var before = doc.GetOutlierCount("revenue_k");
        var path = TempFile("oc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetOutlierCount("revenue_k"));
    }

    // -------------------------------------------------------------------------
    // RemoveOutliers
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveOutliers_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        var ex = Record.Exception(() => doc.RemoveOutliers("revenue_k"));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveOutliers_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        var cleaned = doc.RemoveOutliers("revenue_k");
        Assert.NotNull(cleaned);
        // GAP-CSV-004 fix: RemoveOutliers must preserve headers. Strong assertion.
        Assert.Equal(doc.Headers, cleaned.Headers);
        // Result must have same or fewer rows than original.
        Assert.True(cleaned.GetRowCount() <= doc.GetRowCount());
    }

    [Fact]
    public void RemoveOutliers_Count_LeqOriginal()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        var cleaned = doc.RemoveOutliers("revenue_k");
        Assert.True(cleaned.GetRowCount() <= doc.GetRowCount());
    }

    [Fact]
    public void RemoveOutliers_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        var c1 = doc.RemoveOutliers("weekly_footfall");
        var c2 = doc.RemoveOutliers("weekly_footfall");
        Assert.Equal(c1.GetRowCount(), c2.GetRowCount());
    }

    [Fact]
    public void RemoveOutliers_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        var cleaned = doc.RemoveOutliers("revenue_k");
        var path = TempFile("ro_save.csv");
        cleaned.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(cleaned.GetRowCount(), loaded.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // GetZScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetZScore_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        var ex = Record.Exception(() => doc.GetZScore("revenue_k", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetZScore_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        Assert.True(double.IsFinite(doc.GetZScore("revenue_k", 0)));
    }

    [Fact]
    public void GetZScore_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        Assert.Equal(doc.GetZScore("weekly_footfall", 0), doc.GetZScore("weekly_footfall", 0));
    }

    [Fact]
    public void GetZScore_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateRetailCsv());
        var before = doc.GetZScore("revenue_k", 0);
        var path = TempFile("zs_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetZScore("revenue_k", 0), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetOutlierCount_RemoveOutliers_GetZScore_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_pharma.csv");
        File.WriteAllText(path,
            "trial_id,dose_mg,efficacy_pct,adverse_events,completion_rate,biomarker_level\n" +
            "T001,100,68.4,2,0.94,142.3\n" +
            "T002,200,74.2,3,0.91,158.7\n" +
            "T003,300,79.8,4,0.88,172.4\n" +
            "T004,400,82.1,5,0.85,186.2\n" +
            "T005,100,71.3,2,0.93,148.9\n" +
            "T006,200,76.5,3,0.90,163.1\n" +
            "T007,1200,15.2,48,0.12,890.4\n" + // toxicity outlier
            "T008,100,69.8,2,0.95,145.6\n" +
            "T009,300,80.4,4,0.87,175.3\n" +
            "T010,400,83.7,5,0.86,191.8\n" +
            "T011,200,75.9,3,0.91,161.4\n" +
            "T012,300,78.6,4,0.89,170.8\n");

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());
        Assert.Equal(6, doc.GetColumnCount());

        // GetOutlierCount
        var outAdverse = doc.GetOutlierCount("adverse_events");
        Assert.True(outAdverse >= 0);
        Assert.True(outAdverse <= doc.GetRowCount());

        var outBiomarker = doc.GetOutlierCount("biomarker_level");
        Assert.True(outBiomarker >= 0);

        var outCompletion = doc.GetOutlierCount("completion_rate");
        Assert.True(outCompletion >= 0);

        // Consistent
        Assert.Equal(outAdverse, doc.GetOutlierCount("adverse_events"));

        // RemoveOutliers — adverse events
        var cleanedAdverse = doc.RemoveOutliers("adverse_events");
        Assert.NotNull(cleanedAdverse);
        Assert.True(cleanedAdverse.GetRowCount() <= doc.GetRowCount());

        var cleanedBiomarker = doc.RemoveOutliers("biomarker_level");
        Assert.NotNull(cleanedBiomarker);
        Assert.True(cleanedBiomarker.GetRowCount() <= doc.GetRowCount());
        Assert.Equal(cleanedBiomarker.GetRowCount(), doc.RemoveOutliers("biomarker_level").GetRowCount());

        // GetZScore
        var z0 = doc.GetZScore("adverse_events", 0);
        Assert.True(double.IsFinite(z0));

        var z6 = doc.GetZScore("adverse_events", 6); // row 6 = T007 outlier
        Assert.True(double.IsFinite(z6));
        Assert.True(Math.Abs(z6) > Math.Abs(z0)); // outlier has larger |z|

        Assert.Equal(z0, doc.GetZScore("adverse_events", 0)); // consistent

        // SaveToFile
        var out1 = TempFile("dogfood_pharma_out.csv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(outAdverse, loaded.GetOutlierCount("adverse_events"));
        Assert.Equal(cleanedAdverse.GetRowCount(), loaded.RemoveOutliers("adverse_events").GetRowCount());
        Assert.Equal(z0, loaded.GetZScore("adverse_events", 0), precision: 6);

        // Save cleaned version
        var outCleaned = TempFile("dogfood_pharma_cleaned.csv");
        cleanedAdverse.SaveToFile(outCleaned);
        Assert.True(File.Exists(outCleaned));
        var loadedCleaned = CsvDocument.LoadFile(outCleaned);
        Assert.Equal(cleanedAdverse.GetRowCount(), loadedCleaned.GetRowCount());
        Assert.True(loadedCleaned.GetOutlierCount("adverse_events") >= 0);

        // AddRow — normal trial
        loaded.AddRow(new[] { "T013", "200", "77.1", "3", "0.91", "164.2" });
        Assert.Equal(13, loaded.GetRowCount());
        Assert.True(loaded.GetOutlierCount("adverse_events") >= 0);

        // Final save
        var out2 = TempFile("dogfood_pharma_v2.csv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = CsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.True(loaded2.GetOutlierCount("biomarker_level") >= 0);
        Assert.NotNull(loaded2.RemoveOutliers("adverse_events"));
        Assert.True(double.IsFinite(loaded2.GetZScore("adverse_events", 0)));
    }
}
