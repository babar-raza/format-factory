// Tests for CsvDocument.GetColumnValueCounts, GetColumnTopValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R269

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R269: Tests for CsvDocument.GetColumnValueCounts, GetColumnTopValue deeper.
/// GetColumnValueCounts(colName): returns a dictionary of distinct values and their occurrence counts.
/// GetColumnTopValue(colName): returns the most frequently occurring value in the column.
/// Covers: GetColumnValueCounts no-throw; GetColumnValueCounts non-null;
/// GetColumnValueCounts sum equals RowCount; GetColumnValueCounts consistent;
/// GetColumnValueCounts save-load; GetColumnTopValue no-throw; GetColumnTopValue non-null-or-empty;
/// GetColumnTopValue consistent; GetColumnTopValue save-load;
/// GetColumnTopValue is key in GetColumnValueCounts; GetColumnTopValue is max-count entry;
/// dogfood DVLA Vehicle Licensing Statistics pipeline.
/// </summary>
public class CsvR269GetColumnValueCountsAndTopValueDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR269GetColumnValueCountsAndTopValueDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR269_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id,fuel_type,body_style,transmission,colour");
        // fuel_type: Petrol(8), Diesel(5), Electric(3)
        for (int i = 0; i < 8; i++) sb.AppendLine($"{i},Petrol,Hatchback,Manual,White");
        for (int i = 8; i < 13; i++) sb.AppendLine($"{i},Diesel,Saloon,Automatic,Black");
        for (int i = 13; i < 16; i++) sb.AppendLine($"{i},Electric,SUV,Automatic,Silver");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,region");
        for (int i = 0; i < 25; i++) sb.AppendLine($"{i},London");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnValueCounts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValueCounts_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnValueCounts("fuel_type"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnValueCounts_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.GetColumnValueCounts("fuel_type"));
    }

    [Fact]
    public void GetColumnValueCounts_SumEqualsRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var counts = doc.GetColumnValueCounts("fuel_type");
        int total = 0;
        foreach (var kv in counts) total += kv.Value;
        Assert.Equal(doc.RowCount, total);
    }

    [Fact]
    public void GetColumnValueCounts_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var c1 = doc.GetColumnValueCounts("fuel_type");
        var c2 = doc.GetColumnValueCounts("fuel_type");
        Assert.Equal(c1.Count, c2.Count);
    }

    [Fact]
    public void GetColumnValueCounts_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnValueCounts("fuel_type");
        var path = TempFile("vc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetColumnValueCounts("fuel_type");
        Assert.Equal(before.Count, after.Count);
    }

    // -------------------------------------------------------------------------
    // GetColumnTopValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnTopValue_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnTopValue("fuel_type"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnTopValue_NonNullOrEmpty()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.False(string.IsNullOrEmpty(doc.GetColumnTopValue("fuel_type")));
    }

    [Fact]
    public void GetColumnTopValue_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnTopValue("fuel_type"), doc.GetColumnTopValue("fuel_type"));
    }

    [Fact]
    public void GetColumnTopValue_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnTopValue("fuel_type");
        var path = TempFile("tv_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnTopValue("fuel_type"));
    }

    [Fact]
    public void GetColumnTopValue_IsKey_InGetColumnValueCounts()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var topVal = doc.GetColumnTopValue("fuel_type");
        var counts = doc.GetColumnValueCounts("fuel_type");
        Assert.True(counts.ContainsKey(topVal));
    }

    [Fact]
    public void GetColumnTopValue_IsMaxCount_InGetColumnValueCounts()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var topVal = doc.GetColumnTopValue("fuel_type");
        var counts = doc.GetColumnValueCounts("fuel_type");
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
        // Transport — DVLA: Vehicle Licensing Statistics (VLS) Q3 2024
        // Licensed vehicles in Great Britain by fuel type, body style, and propulsion
        // Value counts for market-share analysis and fleet transition monitoring

        var path = TempFile("dvla_vls_q3_2024.csv");
        var sb = new StringBuilder();
        sb.AppendLine("vehicle_id,fuel_type,body_style,propulsion,keepership,colour,age_band,region");

        var rng = new Random(20240930);
        // Fuel type distribution: Petrol dominant, Diesel declining, EV growing
        string[] fuels = { "Petrol", "Petrol", "Petrol", "Petrol", "Diesel", "Diesel",
                            "Battery_Electric", "Battery_Electric", "Plug_in_Hybrid", "Mild_Hybrid" };
        string[] bodies = { "Hatchback", "Hatchback", "Saloon", "SUV", "SUV",
                             "Estate", "MPV", "Convertible", "Coupe", "LCV" };
        string[] propulsions = { "Petrol", "Petrol", "Diesel", "Diesel", "Electric",
                                  "Petrol_Electric", "Diesel_Electric", "Electric", "Petrol", "Diesel" };
        string[] keeperships = { "Private", "Private", "Private", "Company", "Company", "Hire_Fleet" };
        string[] colours = { "White", "Black", "Silver", "Grey", "Blue", "Red", "Other" };
        string[] ages = { "0-1yr", "1-3yr", "3-5yr", "5-8yr", "8-12yr", "12yr+" };
        string[] regions = { "South_East", "London", "North_West", "West_Midlands", "Yorkshire",
                              "East_Midlands", "East", "South_West", "Wales", "Scotland" };

        for (int i = 0; i < 500; i++)
        {
            string fuel = fuels[rng.Next(fuels.Length)];
            string body = bodies[rng.Next(bodies.Length)];
            string prop = propulsions[rng.Next(propulsions.Length)];
            string keep = keeperships[rng.Next(keeperships.Length)];
            string colour = colours[rng.Next(colours.Length)];
            string age = ages[rng.Next(ages.Length)];
            string region = regions[rng.Next(regions.Length)];
            sb.AppendLine($"VH{i:D6},{fuel},{body},{prop},{keep},{colour},{age},{region}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(500, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // Value counts of fuel_type
        var fuelCounts = doc.GetColumnValueCounts("fuel_type");
        Assert.NotNull(fuelCounts);
        int fuelTotal = 0;
        foreach (var kv in fuelCounts) fuelTotal += kv.Value;
        Assert.Equal(doc.RowCount, fuelTotal);
        Assert.True(fuelCounts.ContainsKey("Petrol"));
        Assert.True(fuelCounts.ContainsKey("Battery_Electric"));

        // Petrol should be most common (appears 4× in sampling array)
        var topFuel = doc.GetColumnTopValue("fuel_type");
        Assert.Equal("Petrol", topFuel);
        Assert.True(fuelCounts["Petrol"] > fuelCounts["Battery_Electric"]);

        // Value counts of body_style
        var bodyCounts = doc.GetColumnValueCounts("body_style");
        Assert.NotNull(bodyCounts);
        int bodyTotal = 0;
        foreach (var kv in bodyCounts) bodyTotal += kv.Value;
        Assert.Equal(doc.RowCount, bodyTotal);

        // Top body style
        var topBody = doc.GetColumnTopValue("body_style");
        Assert.False(string.IsNullOrEmpty(topBody));
        int topBodyCount = bodyCounts[topBody];
        foreach (var kv in bodyCounts)
            Assert.True(topBodyCount >= kv.Value);

        // Value counts of region
        var regionCounts = doc.GetColumnValueCounts("region");
        Assert.NotNull(regionCounts);
        int regionTotal = 0;
        foreach (var kv in regionCounts) regionTotal += kv.Value;
        Assert.Equal(doc.RowCount, regionTotal);
        Assert.True(regionCounts.Count <= 10); // at most 10 distinct regions

        // Keepership — Private dominant
        var keepCounts = doc.GetColumnValueCounts("keepership");
        Assert.True(keepCounts.ContainsKey("Private"));
        Assert.True(keepCounts["Private"] > keepCounts.GetValueOrDefault("Company", 0));

        // Top value consistent
        Assert.Equal(topFuel, doc.GetColumnTopValue("fuel_type"));
        Assert.Equal(topBody, doc.GetColumnTopValue("body_style"));

        // SaveToFile
        var outPath = TempFile("dvla_vls_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(topFuel, loaded.GetColumnTopValue("fuel_type"));
        Assert.Equal(topBody, loaded.GetColumnTopValue("body_style"));
        var fuelCountsLoaded = loaded.GetColumnValueCounts("fuel_type");
        Assert.Equal(fuelCounts.Count, fuelCountsLoaded.Count);
        Assert.Equal(fuelCounts["Petrol"], fuelCountsLoaded["Petrol"]);
        Assert.Equal(fuelCounts["Battery_Electric"], fuelCountsLoaded["Battery_Electric"]);
    }
}
