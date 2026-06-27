// Tests for CsvDocument.GetColumnMin, GetColumnMax deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R278

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R278: Tests for CsvDocument.GetColumnMin, GetColumnMax deeper.
/// GetColumnMin(colName): returns the minimum numeric value in the column.
/// GetColumnMax(colName): returns the maximum numeric value in the column; ≥ GetColumnMin.
/// Covers: GetColumnMin no-throw; GetColumnMin correct for known data;
/// GetColumnMin consistent; GetColumnMin save-load;
/// GetColumnMax no-throw; GetColumnMax correct for known data;
/// GetColumnMax consistent; GetColumnMax save-load;
/// GetColumnMin leq GetColumnMax; GetColumnMin eq GetColumnMax for uniform; dogfood pipeline.
/// </summary>
public class CsvR278GetColumnMinAndColumnMaxDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR278GetColumnMinAndColumnMaxDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR278_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleCsv()
    {
        var path = TempFile("sample.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,value");
        // values 10, 20, 30, 40, 50 — min=10, max=50
        for (int i = 1; i <= 5; i++)
            sb.AppendLine($"{i},{i * 10.0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,score");
        for (int i = 0; i < 20; i++)
            sb.AppendLine($"{i},99.5");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMin
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMin_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnMin("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMin_Correct_ForKnownData()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(10.0, doc.GetColumnMin("value"), precision: 6);
    }

    [Fact]
    public void GetColumnMin_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnMin("value"), doc.GetColumnMin("value"));
    }

    [Fact]
    public void GetColumnMin_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnMin("value");
        var path = TempFile("min_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnMin("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnMax
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMax_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnMax("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMax_Correct_ForKnownData()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(50.0, doc.GetColumnMax("value"), precision: 6);
    }

    [Fact]
    public void GetColumnMax_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnMax("value"), doc.GetColumnMax("value"));
    }

    [Fact]
    public void GetColumnMax_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnMax("value");
        var path = TempFile("max_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnMax("value"), precision: 6);
    }

    [Fact]
    public void GetColumnMin_Leq_GetColumnMax()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnMin("value") <= doc.GetColumnMax("value"));
    }

    [Fact]
    public void GetColumnMin_Equals_GetColumnMax_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(doc.GetColumnMin("score"), doc.GetColumnMax("score"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMin_GetColumnMax_Pipeline()
    {
        // Health — NHS Digital / NHSE: Integrated Care System (ICS) Performance Metrics 2024
        // ICS-level performance data across waiting times, cancer targets, and mental health access
        // Min/max identify best and worst performing ICSs for system improvement benchmarking

        var path = TempFile("nhse_ics_performance_2024.csv");
        var sb = new StringBuilder();
        sb.AppendLine("ics_code,ics_name,region,rtt_18w_pct,cancer_62d_pct,ambulance_8min_pct,mh_access_rate_pct,a_and_e_4h_pct,diagnostics_6w_pct,gp_same_day_pct,friends_family_score");

        var rng = new Random(20240901);
        string[] icsNames = {
            "Bath_and_NE_Somerset_Swindon_Wilts", "Bedfordshire_Luton_Milton_Keynes",
            "Birmingham_Solihull", "Black_Country", "Bristol_North_Somerset_South_Glos",
            "Buckinghamshire_Oxfordshire_Berkshire_West", "Cambridgeshire_Peterborough",
            "Cheshire_and_Wirral", "Cornwall_and_Isles_of_Scilly", "Coventry_and_Warwickshire",
            "Derby_and_Derbyshire", "Devon", "Dorset",
            "East_Lancashire", "Frimley", "Gloucestershire",
            "Greater_Manchester", "Hampshire_and_Isle_of_Wight", "Herefordshire_Worcestershire",
            "Hertfordshire_West_Essex", "Humber_and_North_Yorkshire", "Kent_and_Medway",
            "Lancashire_and_South_Cumbria", "Leicester_Leicestershire_Rutland",
            "Lincolnshire", "Liverpool", "Mid_and_South_Essex",
            "Norfolk_and_Waveney", "North_Central_London", "North_East_London",
            "North_East_and_North_Cumbria", "North_West_London", "Northamptonshire",
            "Nottingham_and_Nottinghamshire", "Shropshire_Telford_and_Wrekin",
            "Somerset", "South_East_London", "South_West_London",
            "South_Yorkshire", "Suffolk_and_North_East_Essex",
            "Surrey_Heartlands", "Sussex"
        };
        string[] regions = {
            "South_West", "East", "Midlands", "Midlands", "South_West",
            "South_East", "East", "North_West", "South_West", "Midlands",
            "Midlands", "South_West", "South_West",
            "North_West", "South_East", "South_West",
            "North_West", "South_East", "Midlands",
            "East", "North_East_Yorkshire", "South_East",
            "North_West", "Midlands",
            "Midlands", "North_West", "East",
            "East", "London", "London",
            "North_East_Yorkshire", "London", "Midlands",
            "Midlands", "Midlands",
            "South_West", "London", "London",
            "North_East_Yorkshire", "East",
            "South_East", "South_East"
        };

        for (int i = 0; i < icsNames.Length; i++)
        {
            double rtt = 55 + rng.NextDouble() * 30;
            double cancer62 = 65 + rng.NextDouble() * 25;
            double amb8 = 40 + rng.NextDouble() * 40;
            double mhAccess = 30 + rng.NextDouble() * 40;
            double ae4h = 55 + rng.NextDouble() * 30;
            double diag6w = 60 + rng.NextDouble() * 35;
            double gpSame = 45 + rng.NextDouble() * 40;
            double fft = 70 + rng.NextDouble() * 25;
            sb.AppendLine($"QIC{i:D3},{icsNames[i]},{regions[i % regions.Length]},{rtt:F1},{cancer62:F1},{amb8:F1},{mhAccess:F1},{ae4h:F1},{diag6w:F1},{gpSame:F1},{fft:F1}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(icsNames.Length, doc.RowCount);
        Assert.Equal(11, doc.ColumnCount);

        // RTT 18-week min and max
        var rttMin = doc.GetColumnMin("rtt_18w_pct");
        var rttMax = doc.GetColumnMax("rtt_18w_pct");
        Assert.True(rttMin >= 0.0 && rttMin <= 100.0);
        Assert.True(rttMax >= 0.0 && rttMax <= 100.0);
        Assert.True(rttMin <= rttMax);
        Assert.Equal(rttMin, doc.GetColumnMin("rtt_18w_pct")); // consistent
        Assert.Equal(rttMax, doc.GetColumnMax("rtt_18w_pct")); // consistent

        // A&E 4-hour performance min/max
        var aeMin = doc.GetColumnMin("a_and_e_4h_pct");
        var aeMax = doc.GetColumnMax("a_and_e_4h_pct");
        Assert.True(aeMin <= aeMax);
        Assert.True(aeMin >= 0.0);
        Assert.True(aeMax <= 100.0);

        // Cancer 62-day min/max
        var cancerMin = doc.GetColumnMin("cancer_62d_pct");
        var cancerMax = doc.GetColumnMax("cancer_62d_pct");
        Assert.True(cancerMin <= cancerMax);
        Assert.True(cancerMin >= 0.0);

        // Mental health access min/max
        var mhMin = doc.GetColumnMin("mh_access_rate_pct");
        var mhMax = doc.GetColumnMax("mh_access_rate_pct");
        Assert.True(mhMin <= mhMax);

        // Mean is between min and max
        var rttMean = doc.GetColumnMean("rtt_18w_pct");
        Assert.True(rttMean >= rttMin && rttMean <= rttMax);

        // SaveToFile
        var outPath = TempFile("nhse_ics_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(rttMin, loaded.GetColumnMin("rtt_18w_pct"), precision: 6);
        Assert.Equal(rttMax, loaded.GetColumnMax("rtt_18w_pct"), precision: 6);
        Assert.Equal(aeMin, loaded.GetColumnMin("a_and_e_4h_pct"), precision: 6);
        Assert.Equal(aeMax, loaded.GetColumnMax("a_and_e_4h_pct"), precision: 6);
        Assert.Equal(cancerMin, loaded.GetColumnMin("cancer_62d_pct"), precision: 6);
        Assert.Equal(mhMax, loaded.GetColumnMax("mh_access_rate_pct"), precision: 6);
    }
}
