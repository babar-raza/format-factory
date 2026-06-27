// Tests for TsvDocument.GetColumnValueCounts, GetColumnTopValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R267

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R267: Tests for TsvDocument.GetColumnValueCounts, GetColumnTopValue deeper.
/// GetColumnValueCounts(colName): returns a dictionary of distinct values and their occurrence counts.
/// GetColumnTopValue(colName): returns the most frequently occurring value in the column.
/// Covers: GetColumnValueCounts no-throw; GetColumnValueCounts non-null;
/// GetColumnValueCounts sum equals RowCount; GetColumnValueCounts consistent;
/// GetColumnValueCounts save-load; GetColumnTopValue no-throw; GetColumnTopValue non-null-or-empty;
/// GetColumnTopValue consistent; GetColumnTopValue save-load;
/// GetColumnTopValue is key in GetColumnValueCounts; dogfood pipeline.
/// </summary>
public class TsvR267GetColumnValueCountsAndTopValueDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR267GetColumnValueCountsAndTopValueDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR267_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id\tcategory\tregion\tstatus");
        // category A appears 6x, B appears 4x, C appears 2x
        for (int i = 0; i < 6; i++) sb.AppendLine($"{i}\tA\tNorth\tActive");
        for (int i = 6; i < 10; i++) sb.AppendLine($"{i}\tB\tSouth\tPending");
        for (int i = 10; i < 12; i++) sb.AppendLine($"{i}\tC\tEast\tClosed");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tcolor");
        for (int i = 0; i < 30; i++) sb.AppendLine($"{i}\tBlue");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnValueCounts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValueCounts_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnValueCounts("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnValueCounts_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetColumnValueCounts("category"));
    }

    [Fact]
    public void GetColumnValueCounts_SumEqualsRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var counts = doc.GetColumnValueCounts("category");
        int total = 0;
        foreach (var kv in counts) total += kv.Value;
        Assert.Equal(doc.RowCount, total);
    }

    [Fact]
    public void GetColumnValueCounts_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var c1 = doc.GetColumnValueCounts("category");
        var c2 = doc.GetColumnValueCounts("category");
        Assert.Equal(c1.Count, c2.Count);
    }

    [Fact]
    public void GetColumnValueCounts_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnValueCounts("category");
        var path = TempFile("vc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetColumnValueCounts("category");
        Assert.Equal(before.Count, after.Count);
    }

    // -------------------------------------------------------------------------
    // GetColumnTopValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnTopValue_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnTopValue("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnTopValue_NonNullOrEmpty()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.False(string.IsNullOrEmpty(doc.GetColumnTopValue("category")));
    }

    [Fact]
    public void GetColumnTopValue_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnTopValue("category"), doc.GetColumnTopValue("category"));
    }

    [Fact]
    public void GetColumnTopValue_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnTopValue("category");
        var path = TempFile("tv_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnTopValue("category"));
    }

    [Fact]
    public void GetColumnTopValue_IsKey_InGetColumnValueCounts()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var topVal = doc.GetColumnTopValue("category");
        var counts = doc.GetColumnValueCounts("category");
        Assert.True(counts.ContainsKey(topVal));
    }

    [Fact]
    public void GetColumnTopValue_IsMaxCount_InGetColumnValueCounts()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var topVal = doc.GetColumnTopValue("category");
        var counts = doc.GetColumnValueCounts("category");
        int topCount = counts[topVal];
        foreach (var kv in counts)
            Assert.True(topCount >= kv.Value);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnValueCounts_GetColumnTopValue_Pipeline()
    {
        // Environment — DEFRA: UK Local Air Quality Management (LAQM) Monitoring Data
        // Annual mean NO2 and PM2.5 measurements across 400 monitoring stations
        // Value counts for exceedance classification and top-pollutant analysis

        var path = TempFile("defra_laqm_2024.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("station_id\tlocal_authority\tzone_type\tpollutant\texceedance_status\tno2_ug_m3\tpm25_ug_m3\tmonitoring_type");

        var rng = new Random(20241201);
        string[] las = { "Westminster", "Camden", "Islington", "Hackney", "Tower Hamlets",
                          "Southwark", "Lambeth", "Wandsworth", "Hammersmith", "Kensington",
                          "Manchester", "Birmingham", "Leeds", "Bristol", "Edinburgh",
                          "Glasgow", "Cardiff", "Belfast", "Liverpool", "Sheffield" };
        string[] zones = { "Urban_Background", "Urban_Background", "Urban_Background",
                            "Roadside", "Roadside", "Kerbside", "Industrial", "Suburban" };
        string[] pollutants = { "NO2", "NO2", "NO2", "PM2.5", "PM2.5", "PM10", "O3" };
        // Exceedance: most PASS, some FAIL (NO2 limit 40 µg/m³ annual mean)
        string[] statuses = { "PASS", "PASS", "PASS", "PASS", "PASS", "FAIL", "FAIL" };
        string[] monTypes = { "Automatic", "Automatic", "Diffusion_Tube", "Diffusion_Tube" };

        for (int i = 0; i < 400; i++)
        {
            string station = $"UKA{rng.Next(10000, 99999)}";
            string la = las[i % las.Length];
            string zone = zones[rng.Next(zones.Length)];
            string pollutant = pollutants[rng.Next(pollutants.Length)];
            string status = statuses[rng.Next(statuses.Length)];
            string monType = monTypes[rng.Next(monTypes.Length)];
            double no2 = status == "FAIL" ? 42 + rng.NextDouble() * 20 : 18 + rng.NextDouble() * 21;
            double pm25 = 8 + rng.NextDouble() * 12;
            sb.AppendLine($"{station}\t{la}\t{zone}\t{pollutant}\t{status}\t{no2:F1}\t{pm25:F1}\t{monType}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(400, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // Value counts of zone_type
        var zoneCounts = doc.GetColumnValueCounts("zone_type");
        Assert.NotNull(zoneCounts);
        int zoneTotal = 0;
        foreach (var kv in zoneCounts) zoneTotal += kv.Value;
        Assert.Equal(doc.RowCount, zoneTotal);

        // Value counts of exceedance_status — PASS majority
        var statusCounts = doc.GetColumnValueCounts("exceedance_status");
        Assert.True(statusCounts.ContainsKey("PASS"));
        Assert.True(statusCounts.ContainsKey("FAIL"));
        Assert.True(statusCounts["PASS"] > statusCounts["FAIL"]);

        // Value counts of pollutant
        var pollCounts = doc.GetColumnValueCounts("pollutant");
        Assert.NotNull(pollCounts);
        int pollTotal = 0;
        foreach (var kv in pollCounts) pollTotal += kv.Value;
        Assert.Equal(doc.RowCount, pollTotal);

        // Top value of exceedance_status → should be "PASS"
        var topStatus = doc.GetColumnTopValue("exceedance_status");
        Assert.Equal("PASS", topStatus);
        Assert.Equal(topStatus, doc.GetColumnTopValue("exceedance_status")); // consistent

        // Top value of pollutant → NO2 (most frequent per probabilities)
        var topPollutant = doc.GetColumnTopValue("pollutant");
        Assert.False(string.IsNullOrEmpty(topPollutant));
        var topPollCount = pollCounts[topPollutant];
        foreach (var kv in pollCounts)
            Assert.True(topPollCount >= kv.Value);

        // Top value of monitoring_type
        var topMonType = doc.GetColumnTopValue("monitoring_type");
        Assert.False(string.IsNullOrEmpty(topMonType));

        // SaveToFile
        var outPath = TempFile("defra_laqm_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(topStatus, loaded.GetColumnTopValue("exceedance_status"));
        Assert.Equal(topPollutant, loaded.GetColumnTopValue("pollutant"));
        var statusCountsLoaded = loaded.GetColumnValueCounts("exceedance_status");
        Assert.Equal(statusCounts.Count, statusCountsLoaded.Count);
        Assert.Equal(statusCounts["PASS"], statusCountsLoaded["PASS"]);
        Assert.Equal(statusCounts["FAIL"], statusCountsLoaded["FAIL"]);
    }
}
