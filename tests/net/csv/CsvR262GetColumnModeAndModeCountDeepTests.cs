// Tests for CsvDocument.GetColumnMode, GetColumnModeCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R262

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R262: Tests for CsvDocument.GetColumnMode, GetColumnModeCount deeper.
/// GetColumnMode(colName): returns the most frequently occurring value in the column.
/// GetColumnModeCount(colName): returns the count of occurrences of the mode value.
/// Covers: GetColumnMode no-throw; GetColumnMode non-null; GetColumnMode consistent;
/// GetColumnMode known value; GetColumnMode save-load;
/// GetColumnModeCount no-throw; GetColumnModeCount positive; GetColumnModeCount consistent;
/// GetColumnModeCount save-load; GetColumnModeCount equals RowCount for constant;
/// GetColumnMode constant column; GetColumnModeCount known count;
/// dogfood CreateDoc→GetColumnMode→GetColumnModeCount pipeline.
/// </summary>
public class CsvR262GetColumnModeAndModeCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR262GetColumnModeAndModeCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR262_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id,product,channel,status");
        var rng = new Random(20240901);
        string[] products = { "Widget A", "Widget A", "Widget A", "Widget B", "Widget C" };
        string[] channels = { "Online", "Online", "Store", "Phone" };
        string[] statuses = { "Complete", "Complete", "Pending", "Cancelled" };
        for (int i = 0; i < 100; i++)
        {
            string product = products[rng.Next(products.Length)];
            string channel = channels[rng.Next(channels.Length)];
            string status = statuses[rng.Next(statuses.Length)];
            sb.AppendLine($"ORD{i:D4},{product},{channel},{status}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateKnownCsv()
    {
        var path = TempFile("known.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,fruit");
        // Apple=6, Banana=3, Cherry=4 → Apple is mode (6)
        string[] items = { "Apple", "Banana", "Apple", "Cherry", "Apple", "Banana", "Cherry", "Apple", "Cherry", "Apple", "Cherry", "Apple", "Banana" };
        for (int i = 0; i < items.Length; i++)
            sb.AppendLine($"{i},{items[i]}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantCsv()
    {
        var path = TempFile("constant.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,type");
        for (int i = 0; i < 30; i++)
            sb.AppendLine($"{i},Invoice");
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
        var ex = Record.Exception(() => doc.GetColumnMode("product"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMode_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.GetColumnMode("channel"));
    }

    [Fact]
    public void GetColumnMode_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnMode("product"), doc.GetColumnMode("product"));
    }

    [Fact]
    public void GetColumnMode_Known_Value()
    {
        var doc = CsvDocument.LoadFile(CreateKnownCsv());
        Assert.Equal("Apple", doc.GetColumnMode("fruit"));
    }

    [Fact]
    public void GetColumnMode_Constant_Column()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal("Invoice", doc.GetColumnMode("type"));
    }

    [Fact]
    public void GetColumnMode_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnMode("product");
        var path = TempFile("mode_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMode("product"));
    }

    // -------------------------------------------------------------------------
    // GetColumnModeCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnModeCount_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnModeCount("product"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnModeCount_Positive()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnModeCount("product") >= 1);
    }

    [Fact]
    public void GetColumnModeCount_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnModeCount("channel"), doc.GetColumnModeCount("channel"));
    }

    [Fact]
    public void GetColumnModeCount_Known_Count()
    {
        var doc = CsvDocument.LoadFile(CreateKnownCsv());
        // Apple appears 6 times in 13 items
        Assert.Equal(6, doc.GetColumnModeCount("fruit"));
    }

    [Fact]
    public void GetColumnModeCount_Equals_RowCount_ForConstant()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(doc.RowCount, doc.GetColumnModeCount("type"));
    }

    [Fact]
    public void GetColumnModeCount_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnModeCount("product");
        var path = TempFile("mc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnModeCount("product"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMode_GetColumnModeCount_Pipeline()
    {
        // Housing — UK Land Registry House Price Index data
        // Property transaction data: most common property type, tenure, region for market analysis
        var path = TempFile("hmlr_price_paid.csv");
        var sb = new StringBuilder();
        sb.AppendLine("transaction_id,county,property_type,old_new,duration,town,price_gbp");

        var rng = new Random(20241101);
        string[] counties = { "Greater London", "Greater London", "Greater London", "Greater London",
                              "West Midlands", "West Yorkshire", "Greater Manchester", "West Sussex",
                              "Surrey", "Kent", "Essex", "Hertfordshire" };
        // Property type: terraced dominates in most regions, then flat in London
        string[] propTypes = {
            "Terraced", "Terraced", "Terraced", "Terraced", "Terraced",
            "Flat/Maisonette", "Flat/Maisonette", "Flat/Maisonette",
            "Semi-detached", "Semi-detached",
            "Detached", "Other"
        };
        string[] tenures = { "Freehold", "Freehold", "Freehold", "Leasehold", "Leasehold" };
        string[] oldNew = { "Established", "Established", "Established", "Established", "New build" };

        for (int i = 0; i < 200; i++)
        {
            string txId = $"{{{Guid.NewGuid()}}}";
            string county = counties[rng.Next(counties.Length)];
            string propType = propTypes[rng.Next(propTypes.Length)];
            string tenure = tenures[rng.Next(tenures.Length)];
            string oldNewVal = oldNew[rng.Next(oldNew.Length)];
            string town = county.Contains("London") ? "London" : county.Split(' ')[0];
            double price = 150000 + rng.NextDouble() * 850000;
            if (county == "Greater London") price *= 1.8; // London premium
            sb.AppendLine($"{txId},{county},{propType},{oldNewVal},{tenure},{town},{price:F0}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(7, doc.ColumnCount);

        // GetColumnMode — property_type: Terraced dominates
        var modePropType = doc.GetColumnMode("property_type");
        Assert.NotNull(modePropType);
        Assert.Equal("Terraced", modePropType);
        Assert.Equal(modePropType, doc.GetColumnMode("property_type")); // consistent

        // GetColumnModeCount — Terraced count
        var mcPropType = doc.GetColumnModeCount("property_type");
        Assert.True(mcPropType >= 1);
        Assert.True(mcPropType <= doc.RowCount);
        Assert.Equal(mcPropType, doc.GetColumnModeCount("property_type")); // consistent

        // GetColumnMode — duration: Freehold dominates
        var modeTenure = doc.GetColumnMode("duration");
        Assert.Equal("Freehold", modeTenure);
        var mcTenure = doc.GetColumnModeCount("duration");
        Assert.True(mcTenure >= 1);

        // GetColumnMode — old_new: Established dominates
        var modeOldNew = doc.GetColumnMode("old_new");
        Assert.Equal("Established", modeOldNew);
        var mcOldNew = doc.GetColumnModeCount("old_new");
        Assert.True(mcOldNew >= 1);

        // County: Greater London dominates (4/12 entries)
        var modeCounty = doc.GetColumnMode("county");
        Assert.Equal("Greater London", modeCounty);
        var mcCounty = doc.GetColumnModeCount("county");
        Assert.True(mcCounty >= 1);
        // Terraced count > county mode count (terraced more dominant %)
        Assert.True(mcPropType >= mcCounty);

        // SaveToFile
        var outPath = TempFile("hmlr_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(modePropType, loaded.GetColumnMode("property_type"));
        Assert.Equal(mcPropType, loaded.GetColumnModeCount("property_type"));
        Assert.Equal(modeTenure, loaded.GetColumnMode("duration"));

        // Constant test
        var path2 = TempFile("constant_hmlr.csv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("ref,data_source");
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"T{i},Land Registry");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = CsvDocument.LoadFile(path2);
        Assert.Equal("Land Registry", doc2.GetColumnMode("data_source"));
        Assert.Equal(50, doc2.GetColumnModeCount("data_source"));
    }
}
