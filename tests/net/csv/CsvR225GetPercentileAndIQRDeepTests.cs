// Tests for CsvDocument.GetPercentile, GetIQR, GetSkewness deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R225

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R225: Tests for CsvDocument.GetPercentile, GetIQR, GetSkewness deeper.
/// GetPercentile(colName, p): returns the p-th percentile of a numeric column.
/// GetIQR(colName): returns the interquartile range (Q3 - Q1).
/// GetSkewness(colName): returns the skewness statistic for the column.
/// Covers: GetPercentile no-throw; GetPercentile in [min,max]; GetPercentile consistent;
/// GetPercentile 25th leq 75th; GetPercentile save-load;
/// GetIQR no-throw; GetIQR non-negative; GetIQR leq range; GetIQR consistent;
/// GetIQR save-load;
/// GetSkewness no-throw; GetSkewness finite; GetSkewness consistent;
/// GetSkewness save-load;
/// dogfood LoadFile→GetPercentile→GetIQR→GetSkewness→SaveToFile pipeline.
/// </summary>
public class CsvR225GetPercentileAndIQRDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR225GetPercentileAndIQRDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR225_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateExamCsv()
    {
        var path = TempFile("exams.csv");
        var content =
            "StudentId,Math,Science,English,History,PE\n" +
            "S001,88,92,85,78,95\n" +
            "S002,75,68,82,90,88\n" +
            "S003,95,98,91,85,72\n" +
            "S004,62,70,74,68,80\n" +
            "S005,80,85,88,82,91\n" +
            "S006,55,60,65,72,85\n" +
            "S007,92,88,94,88,78\n" +
            "S008,70,75,78,74,82\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetPercentile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPercentile_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var ex = Record.Exception(() => doc.GetPercentile("Math", 50));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPercentile_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var p50 = doc.GetPercentile("Science", 50);
        Assert.True(p50 >= doc.GetColumnMin("Science") && p50 <= doc.GetColumnMax("Science"));
    }

    [Fact]
    public void GetPercentile_25th_Leq_75th()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.True(doc.GetPercentile("Math", 25) <= doc.GetPercentile("Math", 75));
    }

    [Fact]
    public void GetPercentile_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.Equal(doc.GetPercentile("English", 50), doc.GetPercentile("English", 50));
    }

    [Fact]
    public void GetPercentile_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var before = doc.GetPercentile("History", 75);
        var path = TempFile("pct_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPercentile("History", 75), 4);
    }

    // -------------------------------------------------------------------------
    // GetIQR
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIQR_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var ex = Record.Exception(() => doc.GetIQR("Math"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetIQR_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.True(doc.GetIQR("Science") >= 0.0);
    }

    [Fact]
    public void GetIQR_Leq_Range()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.True(doc.GetIQR("Math") <= doc.GetColumnRange("Math"));
    }

    [Fact]
    public void GetIQR_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.Equal(doc.GetIQR("PE"), doc.GetIQR("PE"));
    }

    [Fact]
    public void GetIQR_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var before = doc.GetIQR("English");
        var path = TempFile("iqr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetIQR("English"), 4);
    }

    // -------------------------------------------------------------------------
    // GetSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSkewness_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var ex = Record.Exception(() => doc.GetSkewness("Math"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSkewness_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.True(double.IsFinite(doc.GetSkewness("Science")));
    }

    [Fact]
    public void GetSkewness_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.Equal(doc.GetSkewness("History"), doc.GetSkewness("History"));
    }

    [Fact]
    public void GetSkewness_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var before = doc.GetSkewness("Math");
        var path = TempFile("skew_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSkewness("Math"), 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetPercentile_GetIQR_GetSkewness_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_logistics.csv");
        var content =
            "ShipmentId,Weight,Distance,DeliveryDays,Cost,Rating\n" +
            "SH001,12.5,450,3,85.50,4.8\n" +
            "SH002,28.3,1200,5,195.20,4.5\n" +
            "SH003,5.8,280,2,52.40,4.9\n" +
            "SH004,45.2,890,4,310.80,4.2\n" +
            "SH005,18.7,620,3,140.60,4.6\n" +
            "SH006,72.1,1580,7,520.30,3.9\n" +
            "SH007,9.4,340,2,71.20,4.7\n" +
            "SH008,33.6,750,4,245.90,4.4\n" +
            "SH009,55.8,1100,6,398.50,4.1\n" +
            "SH010,15.2,520,3,118.70,4.5\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRowCount());

        // GetPercentile — Weight
        var wp25 = doc.GetPercentile("Weight", 25);
        var wp50 = doc.GetPercentile("Weight", 50);
        var wp75 = doc.GetPercentile("Weight", 75);
        Assert.True(wp25 <= wp50);
        Assert.True(wp50 <= wp75);
        Assert.True(wp25 >= doc.GetColumnMin("Weight"));
        Assert.True(wp75 <= doc.GetColumnMax("Weight"));
        Assert.Equal(wp50, doc.GetPercentile("Weight", 50)); // consistent

        // GetPercentile — Cost
        var cp25 = doc.GetPercentile("Cost", 25);
        var cp75 = doc.GetPercentile("Cost", 75);
        Assert.True(cp25 <= cp75);
        Assert.True(double.IsFinite(cp25) && double.IsFinite(cp75));

        // GetIQR — Weight = Q3 - Q1
        var iqrWeight = doc.GetIQR("Weight");
        Assert.True(iqrWeight >= 0);
        Assert.Equal(iqrWeight, doc.GetIQR("Weight")); // consistent
        Assert.True(iqrWeight <= doc.GetColumnRange("Weight"));
        Assert.Equal(wp75 - wp25, iqrWeight, 4);

        // GetIQR — Cost
        var iqrCost = doc.GetIQR("Cost");
        Assert.True(iqrCost >= 0);
        Assert.Equal(cp75 - cp25, iqrCost, 4);

        // GetIQR — DeliveryDays
        var iqrDays = doc.GetIQR("DeliveryDays");
        Assert.True(iqrDays >= 0);

        // GetSkewness — Weight (right-skewed data expected)
        var skewWeight = doc.GetSkewness("Weight");
        Assert.True(double.IsFinite(skewWeight));
        Assert.Equal(skewWeight, doc.GetSkewness("Weight")); // consistent

        // GetSkewness — Rating
        var skewRating = doc.GetSkewness("Rating");
        Assert.True(double.IsFinite(skewRating));

        // AddRow and recheck
        doc.AddRow(new[] { "SH011", "22.4", "680", "3", "162.30", "4.6" });
        Assert.Equal(11, doc.GetRowCount());
        Assert.True(doc.GetIQR("Weight") >= 0);
        Assert.True(double.IsFinite(doc.GetSkewness("Cost")));

        // SaveToFile
        var savePath = TempFile("dogfood_logistics_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(11, loaded.GetRowCount());
        Assert.Equal(doc.GetPercentile("Weight", 50), loaded.GetPercentile("Weight", 50), 4);
        Assert.Equal(doc.GetIQR("Cost"), loaded.GetIQR("Cost"), 4);
        Assert.Equal(doc.GetSkewness("Distance"), loaded.GetSkewness("Distance"), 4);

        // GetColumnNames cross-check
        var cols = loaded.GetColumnNames();
        Assert.Contains("Weight", cols);
        Assert.Contains("Rating", cols);

        // Final save
        var path2 = TempFile("dogfood_logistics_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetPercentile("Cost", 75), loaded2.GetPercentile("Cost", 75), 4);
        Assert.Equal(loaded.GetIQR("Weight"), loaded2.GetIQR("Weight"), 4);
        Assert.Equal(loaded.GetSkewness("Weight"), loaded2.GetSkewness("Weight"), 4);
    }
}
