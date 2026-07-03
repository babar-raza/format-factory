// Tests for CsvDocument.GetColumnMode, GetColumnRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R271

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R271: Tests for CsvDocument.GetColumnMode, GetColumnRange deeper.
/// GetColumnMode(colName): returns the most frequently occurring numeric value in the column.
/// GetColumnRange(colName): returns the range (max - min) of numeric values; ≥ 0.
/// Covers: GetColumnMode no-throw; GetColumnMode consistent; GetColumnMode save-load;
/// GetColumnRange no-throw; GetColumnRange non-negative; GetColumnRange zero for uniform;
/// GetColumnRange consistent; GetColumnRange save-load;
/// GetColumnRange equals GetColumnMax minus GetColumnMin; dogfood pipeline.
/// </summary>
public class CsvR271GetColumnModeAndColumnRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR271GetColumnModeAndColumnRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR271_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id,score,band");
        for (int i = 0; i < 6; i++) sb.AppendLine($"R{i:D2},100,A");
        for (int i = 6; i < 9; i++) sb.AppendLine($"R{i:D2},200,B");
        for (int i = 9; i < 11; i++) sb.AppendLine($"R{i:D2},300,C");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,value");
        for (int i = 0; i < 25; i++) sb.AppendLine($"R{i:D2},75");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMode_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnMode("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMode_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnMode("score"), doc.GetColumnMode("score"));
    }

    [Fact]
    public void GetColumnMode_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnMode("score");
        var path = TempFile("mode_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMode("score"));
    }

    [Fact]
    public void GetColumnMode_Uniform_EqualsSingleValue()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal("75", doc.GetColumnMode("value"));
    }

    // -------------------------------------------------------------------------
    // GetColumnRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRange_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnRange("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRange_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnRange("score") >= 0.0);
    }

    [Fact]
    public void GetColumnRange_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, doc.GetColumnRange("value"), precision: 6);
    }

    [Fact]
    public void GetColumnRange_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnRange("score"), doc.GetColumnRange("score"));
    }

    [Fact]
    public void GetColumnRange_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnRange("score");
        var path = TempFile("range_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnRange("score"), precision: 6);
    }

    [Fact]
    public void GetColumnRange_EqualsMaxMinusMin()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var range = doc.GetColumnRange("score");
        var max = doc.GetColumnMax("score");
        var min = doc.GetColumnMin("score");
        Assert.Equal(max - min, range, precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMode_GetColumnRange_Pipeline()
    {
        // Housing — ONS / MHCLG: UK House Price Index (UK HPI) 2024
        // Land Registry residential property transaction data
        // Mode identifies the most common sale price band; range captures market price spread

        var path = TempFile("uk_hpi_2024_q3.csv");
        var sb = new StringBuilder();
        sb.AppendLine("transaction_id,sale_price_gbp,property_type,tenure_type,new_build,district,county,region");

        var rng = new Random(20240901);
        string[] propTypes = { "D", "S", "T", "T", "F", "F" }; // D=detached, S=semi, T=terrace, F=flat
        string[] tenures = { "F", "L" }; // F=freehold, L=leasehold
        string[] districts = { "Westminster", "Camden", "Islington", "Hackney", "Tower_Hamlets",
                                "Southwark", "Lambeth", "Manchester_C", "Leeds_C", "Birmingham_C",
                                "Bristol_C", "Sheffield_C", "Edinburgh_C", "Cardiff_C", "Liverpool_C" };
        string[] counties = { "Greater_London", "Greater_London", "Greater_London", "Greater_London",
                               "Greater_London", "Greater_London", "Greater_London", "Greater_Manchester",
                               "West_Yorkshire", "West_Midlands", "Avon", "South_Yorkshire",
                               "Lothian", "South_Glamorgan", "Merseyside" };
        string[] regions = { "London", "London", "London", "London", "London", "London", "London",
                              "North_West", "Yorkshire", "West_Midlands", "South_West",
                              "Yorkshire", "Scotland", "Wales", "North_West" };

        // Price distribution: mode ~250000, range up to 3M
        double[] priceAnchors = { 175000, 250000, 250000, 250000, 320000, 420000, 650000, 850000, 1200000, 2500000 };

        for (int i = 0; i < 400; i++)
        {
            string tid = $"GB{rng.Next(100000000, 999999999)}";
            double price = priceAnchors[rng.Next(priceAnchors.Length)] * (0.85 + rng.NextDouble() * 0.3);
            string propType = propTypes[rng.Next(propTypes.Length)];
            string tenure = tenures[rng.Next(2)];
            string newBuild = rng.NextDouble() < 0.12 ? "Y" : "N";
            int idx = rng.Next(districts.Length);
            sb.AppendLine($"{tid},{price:F0},{propType},{tenure},{newBuild},{districts[idx]},{counties[idx]},{regions[idx]}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(400, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // GetColumnMode for sale_price_gbp
        var priceMode = doc.GetColumnMode("sale_price_gbp");
        Assert.Equal(priceMode, doc.GetColumnMode("sale_price_gbp")); // consistent

        // GetColumnRange for sale_price_gbp
        var priceRange = doc.GetColumnRange("sale_price_gbp");
        Assert.True(priceRange >= 0.0);
        Assert.True(priceRange > 0.0); // prices definitely vary
        Assert.Equal(priceRange, doc.GetColumnRange("sale_price_gbp")); // consistent

        // Range = max - min
        var maxPrice = doc.GetColumnMax("sale_price_gbp");
        var minPrice = doc.GetColumnMin("sale_price_gbp");
        Assert.Equal(maxPrice - minPrice, priceRange, precision: 2);
        Assert.True(maxPrice > minPrice);
        Assert.True(minPrice > 0); // all prices positive
        Assert.True(maxPrice < 5000000); // sanity cap

        // Mode should be within the range
        Assert.True(double.TryParse(priceMode, out var pmVal) && pmVal >= minPrice && pmVal <= maxPrice);

        // SaveToFile
        var outPath = TempFile("uk_hpi_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(priceMode, loaded.GetColumnMode("sale_price_gbp"));
        Assert.Equal(priceRange, loaded.GetColumnRange("sale_price_gbp"), precision: 2);
        Assert.Equal(maxPrice, loaded.GetColumnMax("sale_price_gbp"), precision: 2);
        Assert.Equal(minPrice, loaded.GetColumnMin("sale_price_gbp"), precision: 2);
    }
}
