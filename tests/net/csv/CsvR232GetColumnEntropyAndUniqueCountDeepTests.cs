// Tests for CsvDocument.GetColumnEntropy, GetMutualInformation, GetUniqueValueCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R232

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R232: Tests for CsvDocument.GetColumnEntropy, GetMutualInformation, GetUniqueValueCount deeper.
/// GetColumnEntropy(columnName): returns the Shannon entropy of the column value distribution.
/// GetMutualInformation(col1, col2): returns the mutual information between two columns.
/// GetUniqueValueCount(columnName): returns the number of distinct values in the column.
/// Covers: GetColumnEntropy no-throw; GetColumnEntropy non-negative; GetColumnEntropy consistent;
/// GetColumnEntropy zero for uniform; GetColumnEntropy save-load;
/// GetMutualInformation no-throw; GetMutualInformation non-negative; GetMutualInformation consistent;
/// GetMutualInformation save-load;
/// GetUniqueValueCount no-throw; GetUniqueValueCount positive; GetUniqueValueCount consistent;
/// GetUniqueValueCount leq row count; GetUniqueValueCount save-load;
/// dogfood CreateDoc→GetColumnEntropy→GetMutualInformation→GetUniqueValueCount→SaveToFile pipeline.
/// </summary>
public class CsvR232GetColumnEntropyAndUniqueCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR232GetColumnEntropyAndUniqueCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR232_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateTrafficCsv()
    {
        var path = TempFile("traffic.csv");
        File.WriteAllText(path,
            "incident_id,road_class,region,severity,vehicle_type,weather,time_of_day,casualties\n" +
            "I001,Motorway,North,Fatal,Car,Clear,Night,2\n" +
            "I002,A_Road,South,Serious,HGV,Rain,Morning,1\n" +
            "I003,B_Road,East,Slight,Car,Clear,Afternoon,0\n" +
            "I004,Motorway,West,Serious,Motorcycle,Fog,Evening,1\n" +
            "I005,A_Road,North,Slight,Car,Clear,Afternoon,0\n" +
            "I006,B_Road,South,Fatal,HGV,Rain,Night,3\n" +
            "I007,Motorway,East,Serious,Car,Clear,Morning,1\n" +
            "I008,A_Road,West,Slight,Bicycle,Clear,Afternoon,0\n" +
            "I009,B_Road,North,Serious,Motorcycle,Rain,Evening,1\n" +
            "I010,Motorway,South,Fatal,Car,Snow,Night,2\n" +
            "I011,A_Road,East,Slight,Car,Clear,Morning,0\n" +
            "I012,B_Road,West,Serious,HGV,Fog,Afternoon,1\n");
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        File.WriteAllText(path,
            "id,status\n" +
            "1,Active\n" +
            "2,Active\n" +
            "3,Active\n" +
            "4,Active\n" +
            "5,Active\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnEntropy_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateTrafficCsv());
        var ex = Record.Exception(() => doc.GetColumnEntropy("severity"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropy_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateTrafficCsv());
        Assert.True(doc.GetColumnEntropy("region") >= 0.0);
    }

    [Fact]
    public void GetColumnEntropy_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateTrafficCsv());
        Assert.Equal(doc.GetColumnEntropy("weather"), doc.GetColumnEntropy("weather"));
    }

    [Fact]
    public void GetColumnEntropy_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, doc.GetColumnEntropy("status"), precision: 6);
    }

    [Fact]
    public void GetColumnEntropy_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateTrafficCsv());
        var before = doc.GetColumnEntropy("vehicle_type");
        var path = TempFile("ce_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnEntropy("vehicle_type"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetMutualInformation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMutualInformation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateTrafficCsv());
        var ex = Record.Exception(() => doc.GetMutualInformation("severity", "weather"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMutualInformation_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateTrafficCsv());
        Assert.True(doc.GetMutualInformation("road_class", "severity") >= 0.0);
    }

    [Fact]
    public void GetMutualInformation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateTrafficCsv());
        Assert.Equal(
            doc.GetMutualInformation("severity", "time_of_day"),
            doc.GetMutualInformation("severity", "time_of_day"));
    }

    [Fact]
    public void GetMutualInformation_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateTrafficCsv());
        var before = doc.GetMutualInformation("severity", "weather");
        var path = TempFile("mi_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMutualInformation("severity", "weather"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetUniqueValueCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUniqueValueCount_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateTrafficCsv());
        var ex = Record.Exception(() => doc.GetUniqueValueCount("severity"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetUniqueValueCount_Positive()
    {
        var doc = CsvDocument.LoadFile(CreateTrafficCsv());
        Assert.True(doc.GetUniqueValueCount("road_class") > 0);
    }

    [Fact]
    public void GetUniqueValueCount_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateTrafficCsv());
        Assert.Equal(doc.GetUniqueValueCount("region"), doc.GetUniqueValueCount("region"));
    }

    [Fact]
    public void GetUniqueValueCount_LeqRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateTrafficCsv());
        Assert.True(doc.GetUniqueValueCount("vehicle_type") <= doc.GetRowCount());
    }

    [Fact]
    public void GetUniqueValueCount_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateTrafficCsv());
        var before = doc.GetUniqueValueCount("weather");
        var path = TempFile("uv_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetUniqueValueCount("weather"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropy_GetMutualInformation_GetUniqueValueCount_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_ecommerce.csv");
        File.WriteAllText(path,
            "order_id,customer_segment,product_category,channel,payment_method,country,order_value,returned,satisfaction\n" +
            "ORD001,Premium,Electronics,Web,Card,UK,450,No,5\n" +
            "ORD002,Standard,Clothing,App,Wallet,DE,85,No,4\n" +
            "ORD003,Premium,Furniture,Web,Card,FR,1200,Yes,2\n" +
            "ORD004,New,Books,Web,Card,UK,32,No,4\n" +
            "ORD005,Standard,Electronics,App,Card,ES,280,No,4\n" +
            "ORD006,Premium,Clothing,Web,Wallet,IT,320,No,5\n" +
            "ORD007,Standard,Food,App,Wallet,DE,45,No,3\n" +
            "ORD008,New,Electronics,Web,Card,FR,190,Yes,2\n" +
            "ORD009,Premium,Furniture,Store,Card,UK,2800,No,5\n" +
            "ORD010,Standard,Books,Web,Wallet,ES,28,No,4\n" +
            "ORD011,New,Clothing,App,Card,IT,75,No,3\n" +
            "ORD012,Premium,Food,Web,Card,UK,180,No,4\n");

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());
        Assert.Equal(9, doc.GetColumnCount());

        // GetColumnEntropy — customer_segment
        var entSeg = doc.GetColumnEntropy("customer_segment");
        Assert.True(entSeg >= 0.0);
        Assert.Equal(entSeg, doc.GetColumnEntropy("customer_segment")); // consistent

        // GetColumnEntropy — product_category
        var entCat = doc.GetColumnEntropy("product_category");
        Assert.True(entCat >= 0.0);

        // GetColumnEntropy — country
        var entCountry = doc.GetColumnEntropy("country");
        Assert.True(entCountry >= 0.0);

        // GetMutualInformation — segment and satisfaction
        var miSegSat = doc.GetMutualInformation("customer_segment", "satisfaction");
        Assert.True(miSegSat >= 0.0);
        Assert.Equal(miSegSat, doc.GetMutualInformation("customer_segment", "satisfaction")); // consistent

        // GetMutualInformation — channel and payment_method
        var miChanPay = doc.GetMutualInformation("channel", "payment_method");
        Assert.True(miChanPay >= 0.0);

        // GetMutualInformation — product_category and returned
        var miCatRet = doc.GetMutualInformation("product_category", "returned");
        Assert.True(miCatRet >= 0.0);

        // GetUniqueValueCount
        var uvSeg = doc.GetUniqueValueCount("customer_segment");
        Assert.True(uvSeg > 0);
        Assert.True(uvSeg <= doc.GetRowCount());
        Assert.Equal(uvSeg, doc.GetUniqueValueCount("customer_segment")); // consistent

        var uvChan = doc.GetUniqueValueCount("channel");
        Assert.True(uvChan > 0);

        var uvPay = doc.GetUniqueValueCount("payment_method");
        Assert.True(uvPay > 0);

        // Uniform column
        var uni = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, uni.GetColumnEntropy("status"), precision: 6);
        Assert.Equal(1, uni.GetUniqueValueCount("status"));

        // SaveToFile
        var out1 = TempFile("dogfood_ecommerce_out.csv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(entSeg, loaded.GetColumnEntropy("customer_segment"), precision: 6);
        Assert.Equal(uvSeg, loaded.GetUniqueValueCount("customer_segment"));

        // AddRow on loaded
        loaded.AddRow(new[] { "ORD013", "Standard", "Books", "Web", "Card", "DE", "42", "No", "4" });
        Assert.Equal(13, loaded.GetRowCount());
        Assert.True(loaded.GetColumnEntropy("customer_segment") >= 0.0);

        // Final save
        var out2 = TempFile("dogfood_ecommerce_v2.csv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = CsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.True(loaded2.GetColumnEntropy("product_category") >= 0.0);
        Assert.True(loaded2.GetMutualInformation("channel", "payment_method") >= 0.0);
        Assert.True(loaded2.GetUniqueValueCount("country") > 0);
    }
}
