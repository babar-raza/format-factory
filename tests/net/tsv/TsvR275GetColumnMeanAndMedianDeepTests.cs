// Tests for TsvDocument.GetColumnMean, GetColumnMedian deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R275

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R275: Tests for TsvDocument.GetColumnMean, GetColumnMedian deeper.
/// GetColumnMean(colName): returns the arithmetic mean of numeric values in the column.
/// GetColumnMedian(colName): returns the median numeric value in the column.
/// Covers: GetColumnMean no-throw; GetColumnMean in-range (between min and max);
/// GetColumnMean exact for uniform; GetColumnMean consistent; GetColumnMean save-load;
/// GetColumnMedian no-throw; GetColumnMedian in-range; GetColumnMedian exact for uniform;
/// GetColumnMedian consistent; GetColumnMedian save-load;
/// GetColumnMean equals GetColumnMedian for uniform; dogfood pipeline.
/// </summary>
public class TsvR275GetColumnMeanAndMedianDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR275GetColumnMeanAndMedianDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR275_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id\tscore");
        // scores 0, 10, 20, 30, 40, 50, 60, 70, 80, 90 → mean=45, median=45
        for (int i = 0; i < 10; i++)
            sb.AppendLine($"{i}\t{i * 10.0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tvalue");
        for (int i = 0; i < 20; i++)
            sb.AppendLine($"{i}\t7.5");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMean_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnMean("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMean_InRange_BetweenMinAndMax()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var mean = doc.GetColumnMean("score");
        Assert.True(mean >= doc.GetColumnMin("score") && mean <= doc.GetColumnMax("score"));
    }

    [Fact]
    public void GetColumnMean_Exact_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(7.5, doc.GetColumnMean("value"), precision: 6);
    }

    [Fact]
    public void GetColumnMean_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnMean("score"), doc.GetColumnMean("score"));
    }

    [Fact]
    public void GetColumnMean_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnMean("score");
        var path = TempFile("mean_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnMean("score"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnMedian
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMedian_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnMedian("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMedian_InRange_BetweenMinAndMax()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var median = doc.GetColumnMedian("score");
        Assert.True(median >= doc.GetColumnMin("score") && median <= doc.GetColumnMax("score"));
    }

    [Fact]
    public void GetColumnMedian_Exact_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(7.5, doc.GetColumnMedian("value"), precision: 6);
    }

    [Fact]
    public void GetColumnMedian_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnMedian("score"), doc.GetColumnMedian("score"));
    }

    [Fact]
    public void GetColumnMedian_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnMedian("score");
        var path = TempFile("median_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnMedian("score"), precision: 6);
    }

    [Fact]
    public void GetColumnMean_Equals_Median_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(doc.GetColumnMean("value"), doc.GetColumnMedian("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMean_GetColumnMedian_Pipeline()
    {
        // Transport — DfT / Network Rail: UK Rail Punctuality and Performance Metrics 2024
        // Train operating company (TOC) performance data from the Public Performance Measure
        // Mean and median punctuality distinguish average performance from typical reliability

        var path = TempFile("dft_rail_ppm_2024.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("toc_id\ttoc_name\tfranchise_type\tregion\tppm_pct\ton_time_pct\tavg_delay_mins\tpassenger_journeys_m\tcancellation_rate_pct\tright_time_pct");

        var rng = new Random(20240901);
        string[] tocs = {
            "Avanti_West_Coast", "LNER", "Great_Western_Railway", "South_Western_Railway", "Southeastern",
            "Southern", "Thameslink", "Great_Northern", "East_Midlands_Railway", "CrossCountry",
            "West_Midlands_Trains", "Northern_Trains", "TransPennine_Express", "Merseyrail", "Scotrail",
            "Transport_for_Wales", "Chiltern_Railways", "Greater_Anglia", "c2c", "Heathrow_Express"
        };
        string[] franchiseTypes = {
            "Open_Access_Long_Distance", "Open_Access_Long_Distance", "Long_Distance",
            "South_East_London", "South_East_London", "South_East_London", "London_Travelcard",
            "London_Travelcard", "Long_Distance", "Cross_Country", "Regional", "Regional",
            "Regional", "Metro", "Devolved", "Devolved", "Long_Distance", "East_Anglia",
            "South_East_London", "Airport"
        };
        string[] regions = {
            "North_West", "East_Coast", "Western", "South_West", "South_East",
            "South", "London", "London", "East_Midlands", "National",
            "West_Midlands", "North_England", "Yorkshire", "Merseyside", "Scotland",
            "Wales", "Chilterns", "East_Anglia", "Essex", "London"
        };

        for (int i = 0; i < tocs.Length; i++)
        {
            double ppm = 65 + rng.NextDouble() * 30;           // PPM range 65-95%
            double onTime = ppm * 0.85 + rng.NextDouble() * 5; // On-time correlated with PPM
            double avgDelay = 4 + rng.NextDouble() * 8;
            double journeys = 5 + rng.NextDouble() * 150;
            double cancRate = 0.5 + rng.NextDouble() * 4;
            double rightTime = onTime * 0.8 + rng.NextDouble() * 5;

            // TransPennine and Avanti historically lower performance
            if (i == 0 || i == 12) { ppm -= 10; avgDelay += 3; cancRate += 2; }

            sb.AppendLine($"TOC{i:D2}\t{tocs[i]}\t{franchiseTypes[i]}\t{regions[i]}\t{ppm:F1}\t{onTime:F1}\t{avgDelay:F1}\t{journeys:F0}\t{cancRate:F2}\t{rightTime:F1}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(20, doc.RowCount);

        // PPM mean and median
        var ppmMean = doc.GetColumnMean("ppm_pct");
        var ppmMedian = doc.GetColumnMedian("ppm_pct");
        var ppmMin = doc.GetColumnMin("ppm_pct");
        var ppmMax = doc.GetColumnMax("ppm_pct");

        Assert.True(ppmMean >= ppmMin && ppmMean <= ppmMax);
        Assert.True(ppmMedian >= ppmMin && ppmMedian <= ppmMax);
        Assert.True(ppmMean > 0.0);
        Assert.True(ppmMedian > 0.0);
        Assert.Equal(ppmMean, doc.GetColumnMean("ppm_pct")); // consistent
        Assert.Equal(ppmMedian, doc.GetColumnMedian("ppm_pct")); // consistent

        // Average delay mean and median
        var delayMean = doc.GetColumnMean("avg_delay_mins");
        var delayMedian = doc.GetColumnMedian("avg_delay_mins");
        Assert.True(delayMean > 0.0);
        Assert.True(delayMedian > 0.0);
        Assert.True(delayMean >= doc.GetColumnMin("avg_delay_mins"));
        Assert.True(delayMean <= doc.GetColumnMax("avg_delay_mins"));

        // Cancellation rate mean and median (should be < 10%)
        var cancMean = doc.GetColumnMean("cancellation_rate_pct");
        var cancMedian = doc.GetColumnMedian("cancellation_rate_pct");
        Assert.True(cancMean >= 0.0 && cancMean < 15.0);
        Assert.True(cancMedian >= 0.0 && cancMedian < 15.0);

        // On-time percentage mean
        var onTimeMean = doc.GetColumnMean("on_time_pct");
        Assert.True(onTimeMean > 0.0 && onTimeMean <= 100.0);

        // SaveToFile
        var outPath = TempFile("dft_rail_ppm_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(ppmMean, loaded.GetColumnMean("ppm_pct"), precision: 6);
        Assert.Equal(ppmMedian, loaded.GetColumnMedian("ppm_pct"), precision: 6);
        Assert.Equal(delayMean, loaded.GetColumnMean("avg_delay_mins"), precision: 6);
        Assert.Equal(cancMedian, loaded.GetColumnMedian("cancellation_rate_pct"), precision: 6);

        var ex1 = Record.Exception(() => loaded.GetColumnMean("ppm_pct"));
        var ex2 = Record.Exception(() => loaded.GetColumnMedian("cancellation_rate_pct"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
