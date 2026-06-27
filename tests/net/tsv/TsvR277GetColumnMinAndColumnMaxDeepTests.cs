// Tests for TsvDocument.GetColumnMin, GetColumnMax deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R277

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R277: Tests for TsvDocument.GetColumnMin, GetColumnMax deeper.
/// GetColumnMin(colName): returns the minimum numeric value in the column.
/// GetColumnMax(colName): returns the maximum numeric value in the column.
/// Covers: GetColumnMin no-throw; GetColumnMin correct for known data;
/// GetColumnMin consistent; GetColumnMin save-load;
/// GetColumnMax no-throw; GetColumnMax correct for known data;
/// GetColumnMax consistent; GetColumnMax save-load;
/// GetColumnMin leq GetColumnMax; equal for uniform; dogfood pipeline.
/// </summary>
public class TsvR277GetColumnMinAndColumnMaxDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR277GetColumnMinAndColumnMaxDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR277_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id\tscore\trank");
        double[] scores = { 45.2, 88.7, 12.3, 99.1, 67.4, 33.8, 76.5, 55.0, 21.9, 84.6 };
        for (int i = 0; i < scores.Length; i++)
            sb.AppendLine($"{i}\t{scores[i]:F1}\t{i + 1}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tvalue");
        for (int i = 0; i < 10; i++)
            sb.AppendLine($"{i}\t42.0");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMin
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMin_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnMin("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMin_Correct_ForKnownData()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(12.3, doc.GetColumnMin("score"), precision: 5);
    }

    [Fact]
    public void GetColumnMin_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnMin("score"), doc.GetColumnMin("score"));
    }

    [Fact]
    public void GetColumnMin_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnMin("score");
        var path = TempFile("min_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnMin("score"), precision: 5);
    }

    // -------------------------------------------------------------------------
    // GetColumnMax
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMax_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnMax("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMax_Correct_ForKnownData()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(99.1, doc.GetColumnMax("score"), precision: 5);
    }

    [Fact]
    public void GetColumnMax_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnMax("score"), doc.GetColumnMax("score"));
    }

    [Fact]
    public void GetColumnMax_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnMax("score");
        var path = TempFile("max_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnMax("score"), precision: 5);
    }

    [Fact]
    public void GetColumnMin_Leq_GetColumnMax()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnMin("score") <= doc.GetColumnMax("score"));
    }

    [Fact]
    public void GetColumnMin_Equals_GetColumnMax_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(doc.GetColumnMin("value"), doc.GetColumnMax("value"), precision: 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMin_GetColumnMax_Pipeline()
    {
        // Transport — DfT / Network Rail: National Rail Station Footfall Census Q3 2024
        // Station-level passenger counts, accessibility ratings, and platform dwell times
        // Min/max analytics identify outlier stations for capacity planning and accessibility audits

        var path = TempFile("dft_station_footfall_q3_2024.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("station_crscode\tstation_name\tregion\tannual_footfall_millions\tplatforms\taccessibility_score\tavg_dwell_seconds\tpeak_hour_trains");

        string[] crsCodes = {
            "WAT", "VIC", "LBG", "CST", "CHX", "PAD", "EUS", "KGX", "MYB", "STP",
            "BHM", "MAN", "LDS", "NCL", "BRI", "LIV", "SHF", "NTT", "CVT", "EXD",
            "RDG", "SOT", "NRW", "CBG", "OXF", "YRK", "CAR", "SWA", "ABD", "EDI"
        };
        string[] names = {
            "London_Waterloo", "London_Victoria", "London_Bridge", "London_Cannon_Street", "London_Charing_Cross",
            "London_Paddington", "London_Euston", "London_Kings_Cross", "London_Marylebone", "London_St_Pancras",
            "Birmingham_New_Street", "Manchester_Piccadilly", "Leeds", "Newcastle", "Bristol_Temple_Meads",
            "Liverpool_Lime_Street", "Sheffield", "Nottingham", "Coventry", "Exeter_St_Davids",
            "Reading", "Southampton_Central", "Norwich", "Cambridge", "Oxford",
            "York", "Cardiff_Central", "Swansea", "Aberdeen", "Edinburgh_Waverley"
        };
        string[] regions = {
            "London", "London", "London", "London", "London",
            "London", "London", "London", "London", "London",
            "West_Midlands", "North_West", "Yorkshire", "North_East", "South_West",
            "North_West", "Yorkshire", "East_Midlands", "West_Midlands", "South_West",
            "South_East", "South_East", "East_of_England", "East_of_England", "South_East",
            "Yorkshire", "Wales", "Wales", "Scotland", "Scotland"
        };
        double[] footfalls = {
            97.1, 82.4, 54.7, 43.2, 38.9,
            80.3, 68.7, 62.4, 19.8, 41.3,
            43.1, 38.7, 31.4, 22.8, 18.9,
            16.4, 14.2, 11.8, 12.3, 8.7,
            21.4, 9.8, 8.2, 12.7, 9.4,
            13.6, 14.1, 7.3, 6.8, 24.3
        };
        int[] platforms = {
            24, 19, 15, 8, 6,
            14, 18, 12, 6, 8,
            12, 14, 17, 12, 13,
            10, 8, 9, 7, 6,
            15, 7, 8, 8, 5,
            11, 8, 6, 7, 19
        };
        double[] accessibility = {
            87.4, 82.1, 74.3, 68.9, 71.2,
            91.3, 88.7, 93.2, 65.4, 89.6,
            84.3, 86.7, 79.4, 81.2, 77.8,
            76.4, 72.3, 68.7, 71.8, 69.4,
            83.7, 74.2, 67.8, 88.4, 72.6,
            78.3, 76.8, 64.3, 71.2, 86.7
        };
        double[] dwell = {
            42.3, 38.7, 34.2, 28.4, 31.6,
            45.8, 41.2, 43.7, 27.3, 39.4,
            38.2, 36.7, 32.4, 34.1, 31.8,
            29.4, 27.8, 26.3, 28.7, 24.6,
            35.2, 27.4, 23.8, 31.7, 26.4,
            33.2, 29.8, 22.7, 21.4, 38.9
        };
        int[] peakTrains = {
            18, 16, 14, 10, 8,
            15, 17, 14, 6, 12,
            14, 16, 14, 10, 8,
            8, 7, 6, 7, 5,
            12, 6, 5, 7, 5,
            9, 7, 4, 4, 14
        };

        for (int i = 0; i < crsCodes.Length; i++)
            sb.AppendLine($"{crsCodes[i]}\t{names[i]}\t{regions[i]}\t{footfalls[i]:F1}\t{platforms[i]}\t{accessibility[i]:F1}\t{dwell[i]:F1}\t{peakTrains[i]}");

        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(30, doc.RowCount);

        // Footfall min/max (London Waterloo should be highest at 97.1; Aberdeen lowest at 6.8)
        var footMin = doc.GetColumnMin("annual_footfall_millions");
        var footMax = doc.GetColumnMax("annual_footfall_millions");
        Assert.True(footMin >= 0);
        Assert.True(footMax > 0);
        Assert.True(footMin <= footMax);
        Assert.Equal(footMin, doc.GetColumnMin("annual_footfall_millions"), precision: 5); // consistent
        Assert.Equal(footMax, doc.GetColumnMax("annual_footfall_millions"), precision: 5); // consistent

        // Accessibility score min/max
        var accMin = doc.GetColumnMin("accessibility_score");
        var accMax = doc.GetColumnMax("accessibility_score");
        Assert.True(accMin >= 0);
        Assert.True(accMax <= 100);
        Assert.True(accMin <= accMax);

        // Platform count min/max
        var platMin = doc.GetColumnMin("platforms");
        var platMax = doc.GetColumnMax("platforms");
        Assert.True(platMin >= 1);
        Assert.True(platMax >= platMin);

        // Dwell time min/max
        var dwellMin = doc.GetColumnMin("avg_dwell_seconds");
        var dwellMax = doc.GetColumnMax("avg_dwell_seconds");
        Assert.True(dwellMin >= 0);
        Assert.True(dwellMax >= dwellMin);

        // Peak trains min/max
        var peakMin = doc.GetColumnMin("peak_hour_trains");
        var peakMax = doc.GetColumnMax("peak_hour_trains");
        Assert.True(peakMin >= 0);
        Assert.True(peakMax >= peakMin);

        // SaveToFile
        var outPath = TempFile("dft_station_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(footMin, loaded.GetColumnMin("annual_footfall_millions"), precision: 5);
        Assert.Equal(footMax, loaded.GetColumnMax("annual_footfall_millions"), precision: 5);
        Assert.Equal(accMin, loaded.GetColumnMin("accessibility_score"), precision: 5);
        Assert.Equal(accMax, loaded.GetColumnMax("accessibility_score"), precision: 5);

        var ex1 = Record.Exception(() => loaded.GetColumnMin("annual_footfall_millions"));
        var ex2 = Record.Exception(() => loaded.GetColumnMax("annual_footfall_millions"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
