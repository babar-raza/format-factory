// Tests for CsvDocument.GetColumnBinCount, GetColumnHistogram, GetColumnBinEdges deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R246

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R246: Tests for CsvDocument.GetColumnBinCount, GetColumnHistogram, GetColumnBinEdges deeper.
/// GetColumnBinCount(columnName, binCount): returns count of values per bin across the value range.
/// GetColumnHistogram(columnName, binCount): returns a histogram as a list of (edge, count) pairs.
/// GetColumnBinEdges(columnName, binCount): returns the bin boundary values.
/// Covers: GetColumnBinCount no-throw; GetColumnBinCount non-null; GetColumnBinCount sum equals row count;
/// GetColumnBinCount consistent;
/// GetColumnHistogram no-throw; GetColumnHistogram non-null; GetColumnHistogram count equals binCount;
/// GetColumnHistogram consistent;
/// GetColumnBinEdges no-throw; GetColumnBinEdges non-null; GetColumnBinEdges count equals binCount+1;
/// GetColumnBinEdges save-load;
/// dogfood CreateDoc→GetColumnBinCount→GetColumnHistogram→GetColumnBinEdges pipeline.
/// </summary>
public class CsvR246GetColumnBinCountAndHistogramDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR246GetColumnBinCountAndHistogramDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR246_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateWeightCsv()
    {
        var path = TempFile("weights.csv");
        var lines = new System.Collections.Generic.List<string>
        {
            "participant_id,group,baseline_bmi,week12_bmi,weight_change_kg,adherence_pct",
            "P001,Intervention,32.1,29.8,-6.2,94",
            "P002,Control,30.5,30.2,-0.8,87",
            "P003,Intervention,35.4,31.2,-10.5,98",
            "P004,Control,28.9,29.1,0.5,76",
            "P005,Intervention,31.8,28.6,-8.4,91",
            "P006,Intervention,38.2,33.5,-11.6,89",
            "P007,Control,29.4,29.8,1.1,72",
            "P008,Intervention,33.7,30.1,-9.0,95",
            "P009,Control,31.2,31.5,0.7,81",
            "P010,Intervention,36.1,31.9,-10.5,97",
            "P011,Control,27.8,28.1,0.8,68",
            "P012,Intervention,34.5,30.8,-9.3,92",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnBinCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnBinCount_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateWeightCsv());
        var ex = Record.Exception(() => doc.GetColumnBinCount("baseline_bmi", 5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnBinCount_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateWeightCsv());
        Assert.NotNull(doc.GetColumnBinCount("baseline_bmi", 5));
    }

    [Fact]
    public void GetColumnBinCount_Sum_Equals_RowCount()
    {
        var doc = CsvDocument.LoadFile(CreateWeightCsv());
        var bins = doc.GetColumnBinCount("baseline_bmi", 4);
        int total = 0;
        foreach (var count in bins) total += count;
        Assert.Equal(doc.RowCount, total);
    }

    [Fact]
    public void GetColumnBinCount_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateWeightCsv());
        var bins1 = doc.GetColumnBinCount("weight_change_kg", 5);
        var bins2 = doc.GetColumnBinCount("weight_change_kg", 5);
        Assert.Equal(bins1.Count, bins2.Count);
    }

    // -------------------------------------------------------------------------
    // GetColumnHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHistogram_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateWeightCsv());
        var ex = Record.Exception(() => doc.GetColumnHistogram("baseline_bmi", 4));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnHistogram_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateWeightCsv());
        Assert.NotNull(doc.GetColumnHistogram("week12_bmi", 4));
    }

    [Fact]
    public void GetColumnHistogram_Count_Equals_BinCount()
    {
        var doc = CsvDocument.LoadFile(CreateWeightCsv());
        var hist = doc.GetColumnHistogram("baseline_bmi", 4);
        Assert.Equal(4, hist.Count);
    }

    [Fact]
    public void GetColumnHistogram_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateWeightCsv());
        var h1 = doc.GetColumnHistogram("adherence_pct", 3);
        var h2 = doc.GetColumnHistogram("adherence_pct", 3);
        Assert.Equal(h1.Count, h2.Count);
    }

    // -------------------------------------------------------------------------
    // GetColumnBinEdges
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnBinEdges_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateWeightCsv());
        var ex = Record.Exception(() => doc.GetColumnBinEdges("baseline_bmi", 4));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnBinEdges_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateWeightCsv());
        Assert.NotNull(doc.GetColumnBinEdges("weight_change_kg", 4));
    }

    [Fact]
    public void GetColumnBinEdges_Count_Equals_BinCountPlusOne()
    {
        var doc = CsvDocument.LoadFile(CreateWeightCsv());
        var edges = doc.GetColumnBinEdges("baseline_bmi", 4);
        Assert.Equal(5, edges.Count); // binCount + 1
    }

    [Fact]
    public void GetColumnBinEdges_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateWeightCsv());
        var before = doc.GetColumnBinEdges("baseline_bmi", 4).Count;
        var path = TempFile("be_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnBinEdges("baseline_bmi", 4).Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnBinCount_GetColumnHistogram_GetColumnBinEdges_Pipeline()
    {
        // UK environment agency — river flow and flood risk return period analysis
        var path = TempFile("river_flow.csv");
        var csvLines = new System.Collections.Generic.List<string>();
        csvLines.Add("gauge_id,river_name,date,daily_mean_cumecs,peak_flow_cumecs,stage_m,return_period_years,flood_alert");
        var rng = new Random(20240101);
        string[] rivers = { "Thames", "Severn", "Trent", "Ouse", "Wye", "Avon" };
        for (int i = 0; i < 150; i++)
        {
            var river = rivers[i % 6];
            // Daily mean flow — log-normal distribution approximation
            double dailyMeanFlow = Math.Exp(3.0 + rng.NextDouble() * 2.5); // roughly 20-1200 cumecs
            double peakFlow = dailyMeanFlow * (1.0 + rng.NextDouble() * 0.8);
            double stage = 0.5 + rng.NextDouble() * 5.0;
            // Return period: most events are frequent (short return period)
            double retPeriod = Math.Exp(rng.NextDouble() * 5.0); // 1-150 years
            int alert = (retPeriod > 50) ? 1 : 0;
            csvLines.Add($"GAUGE{(i % 30):D3},{river},2024-{(i % 12 + 1):D2}-{(i % 28 + 1):D2},{dailyMeanFlow:F1},{peakFlow:F1},{stage:F2},{retPeriod:F1},{alert}");
        }
        File.WriteAllLines(path, csvLines);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);

        // GetColumnBinCount — flow distribution in 6 bins
        var flowBins = doc.GetColumnBinCount("daily_mean_cumecs", 6);
        Assert.NotNull(flowBins);
        Assert.Equal(6, flowBins.Count);
        int binTotal = 0;
        foreach (var cnt in flowBins) binTotal += cnt;
        Assert.Equal(150, binTotal);
        var flowBinsAgain = doc.GetColumnBinCount("daily_mean_cumecs", 6);
        Assert.Equal(flowBins.Count, flowBinsAgain.Count); // consistent

        // GetColumnHistogram — return period frequency analysis
        var hist5 = doc.GetColumnHistogram("return_period_years", 5);
        Assert.NotNull(hist5);
        Assert.Equal(5, hist5.Count);
        var hist5Again = doc.GetColumnHistogram("return_period_years", 5);
        Assert.Equal(hist5.Count, hist5Again.Count); // consistent

        // GetColumnBinEdges — stage height bins
        var stageEdges = doc.GetColumnBinEdges("stage_m", 6);
        Assert.NotNull(stageEdges);
        Assert.Equal(7, stageEdges.Count); // 6 bins = 7 edges
        // Edges should be monotonically non-decreasing
        for (int i = 0; i < stageEdges.Count - 1; i++)
            Assert.True(stageEdges[i] <= stageEdges[i + 1]);
        var stageEdgesAgain = doc.GetColumnBinEdges("stage_m", 6);
        Assert.Equal(stageEdges.Count, stageEdgesAgain.Count); // consistent

        // SaveToFile
        var outPath = TempFile("river_flow_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(flowBins.Count, loaded.GetColumnBinCount("daily_mean_cumecs", 6).Count);
        Assert.Equal(hist5.Count, loaded.GetColumnHistogram("return_period_years", 5).Count);
        Assert.Equal(stageEdges.Count, loaded.GetColumnBinEdges("stage_m", 6).Count);
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // Additional stats
        var meanFlow = doc.GetColumnMean("daily_mean_cumecs");
        Assert.True(meanFlow > 0);
        var maxFlow = doc.GetColumnMax("peak_flow_cumecs");
        Assert.True(maxFlow > meanFlow);
    }
}
