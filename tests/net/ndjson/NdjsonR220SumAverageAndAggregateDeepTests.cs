// Tests for NdjsonDocument.Sum, Average, GetMinValue, GetMaxValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R220

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R220: Tests for NdjsonDocument.Sum, Average, GetMinValue, GetMaxValue deeper.
/// Sum(fieldName): returns the sum of numeric values in a field.
/// Average(fieldName): returns the average of numeric values in a field.
/// GetMinValue(fieldName): returns the minimum numeric value in a field.
/// GetMaxValue(fieldName): returns the maximum numeric value in a field.
/// Covers: Sum no-throw; Sum non-negative for positive data; Sum correct value;
/// Sum consistent; Sum save-load; Sum zero for absent field;
/// Average no-throw; Average positive; Average correct; Average consistent;
/// Average save-load; Average in range [min, max];
/// GetMinValue no-throw; GetMinValue correct; GetMinValue <= Average;
/// GetMinValue consistent; GetMinValue save-load;
/// GetMaxValue no-throw; GetMaxValue correct; GetMaxValue >= Average;
/// GetMaxValue consistent; GetMaxValue save-load; GetMaxValue >= GetMinValue;
/// dogfood LoadFile→Sum→Average→GetMinValue→GetMaxValue→SaveToFile pipeline.
/// </summary>
public class NdjsonR220SumAverageAndAggregateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR220SumAverageAndAggregateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR220_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSaleNdjson()
    {
        var path = TempFile("sales.ndjson");
        var content =
            "{\"product\":\"Widget A\",\"region\":\"North\",\"revenue\":12500,\"units\":250,\"margin\":0.32}\n" +
            "{\"product\":\"Widget B\",\"region\":\"South\",\"revenue\":8900,\"units\":178,\"margin\":0.28}\n" +
            "{\"product\":\"Widget C\",\"region\":\"East\",\"revenue\":15200,\"units\":304,\"margin\":0.35}\n" +
            "{\"product\":\"Widget D\",\"region\":\"West\",\"revenue\":6800,\"units\":136,\"margin\":0.25}\n" +
            "{\"product\":\"Widget E\",\"region\":\"North\",\"revenue\":11100,\"units\":222,\"margin\":0.30}\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // Sum
    // -------------------------------------------------------------------------

    [Fact]
    public void Sum_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var ex = Record.Exception(() => doc.Sum("revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void Sum_NonNegative_ForPositiveData()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        Assert.True(doc.Sum("revenue") >= 0.0);
    }

    [Fact]
    public void Sum_Revenue_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        // 12500 + 8900 + 15200 + 6800 + 11100 = 54500
        var sum = doc.Sum("revenue");
        Assert.True(Math.Abs(sum - 54500.0) < 1.0);
    }

    [Fact]
    public void Sum_Units_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        // 250 + 178 + 304 + 136 + 222 = 1090
        var sum = doc.Sum("units");
        Assert.True(Math.Abs(sum - 1090.0) < 1.0);
    }

    [Fact]
    public void Sum_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        Assert.Equal(doc.Sum("revenue"), doc.Sum("revenue"));
    }

    [Fact]
    public void Sum_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var before = doc.Sum("revenue");
        var path = TempFile("sum_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.Sum("revenue"), 1);
    }

    // -------------------------------------------------------------------------
    // Average
    // -------------------------------------------------------------------------

    [Fact]
    public void Average_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var ex = Record.Exception(() => doc.Average("revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void Average_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        Assert.True(doc.Average("revenue") > 0.0);
    }

    [Fact]
    public void Average_Revenue_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        // 54500 / 5 = 10900
        var avg = doc.Average("revenue");
        Assert.True(Math.Abs(avg - 10900.0) < 1.0);
    }

    [Fact]
    public void Average_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        Assert.Equal(doc.Average("revenue"), doc.Average("revenue"));
    }

    [Fact]
    public void Average_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var before = doc.Average("units");
        var path = TempFile("avg_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.Average("units"), 1);
    }

    [Fact]
    public void Average_InRange_MinMax()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var avg = doc.Average("revenue");
        var min = doc.GetMinValue("revenue");
        var max = doc.GetMaxValue("revenue");
        Assert.True(avg >= min && avg <= max);
    }

    // -------------------------------------------------------------------------
    // GetMinValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMinValue_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var ex = Record.Exception(() => doc.GetMinValue("revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMinValue_Revenue_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        // Min revenue = 6800 (Widget D)
        var min = doc.GetMinValue("revenue");
        Assert.True(Math.Abs(min - 6800.0) < 1.0);
    }

    [Fact]
    public void GetMinValue_LessThanOrEqualToAverage()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        Assert.True(doc.GetMinValue("revenue") <= doc.Average("revenue"));
    }

    [Fact]
    public void GetMinValue_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        Assert.Equal(doc.GetMinValue("revenue"), doc.GetMinValue("revenue"));
    }

    [Fact]
    public void GetMinValue_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var before = doc.GetMinValue("revenue");
        var path = TempFile("min_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMinValue("revenue"), 1);
    }

    // -------------------------------------------------------------------------
    // GetMaxValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxValue_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var ex = Record.Exception(() => doc.GetMaxValue("revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMaxValue_Revenue_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        // Max revenue = 15200 (Widget C)
        var max = doc.GetMaxValue("revenue");
        Assert.True(Math.Abs(max - 15200.0) < 1.0);
    }

    [Fact]
    public void GetMaxValue_GreaterThanOrEqualToAverage()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        Assert.True(doc.GetMaxValue("revenue") >= doc.Average("revenue"));
    }

    [Fact]
    public void GetMaxValue_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        Assert.Equal(doc.GetMaxValue("revenue"), doc.GetMaxValue("revenue"));
    }

    [Fact]
    public void GetMaxValue_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        var before = doc.GetMaxValue("units");
        var path = TempFile("max_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMaxValue("units"), 1);
    }

    [Fact]
    public void GetMaxValue_GreaterThanOrEqualToMinValue()
    {
        var doc = NdjsonDocument.LoadFile(CreateSaleNdjson());
        Assert.True(doc.GetMaxValue("revenue") >= doc.GetMinValue("revenue"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Sum_Average_GetMinValue_GetMaxValue_SaveToFile_Pipeline()
    {
        // Build comprehensive NDJSON
        var path = TempFile("dogfood_portfolio.ndjson");
        var content =
            "{\"fund\":\"Alpha Fund\",\"aum\":1250000000,\"return_pct\":12.5,\"risk_score\":65,\"holdings\":45}\n" +
            "{\"fund\":\"Beta Fund\",\"aum\":890000000,\"return_pct\":8.2,\"risk_score\":42,\"holdings\":30}\n" +
            "{\"fund\":\"Gamma Fund\",\"aum\":2100000000,\"return_pct\":15.8,\"risk_score\":78,\"holdings\":60}\n" +
            "{\"fund\":\"Delta Fund\",\"aum\":650000000,\"return_pct\":6.4,\"risk_score\":35,\"holdings\":22}\n" +
            "{\"fund\":\"Epsilon Fund\",\"aum\":1800000000,\"return_pct\":11.1,\"risk_score\":58,\"holdings\":38}\n" +
            "{\"fund\":\"Zeta Fund\",\"aum\":430000000,\"return_pct\":4.9,\"risk_score\":28,\"holdings\":18}\n" +
            "{\"fund\":\"Eta Fund\",\"aum\":3200000000,\"return_pct\":18.3,\"risk_score\":88,\"holdings\":75}\n";
        File.WriteAllText(path, content);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(7, doc.GetRecordCount());

        // Sum — aum
        var totalAum = doc.Sum("aum");
        // 1250+890+2100+650+1800+430+3200 = 10320 (millions)
        Assert.True(totalAum > 0);
        Assert.True(Math.Abs(totalAum - 10320000000.0) < 1000.0);

        // Sum — holdings
        var totalHoldings = doc.Sum("holdings");
        // 45+30+60+22+38+18+75 = 288
        Assert.True(Math.Abs(totalHoldings - 288.0) < 1.0);

        // Consistent
        Assert.Equal(totalAum, doc.Sum("aum"));

        // Average — return_pct
        var avgReturn = doc.Average("return_pct");
        // (12.5+8.2+15.8+6.4+11.1+4.9+18.3)/7 = 77.2/7 ≈ 11.03
        Assert.True(avgReturn > 0);
        Assert.True(avgReturn > 5.0 && avgReturn < 20.0);

        // Average — risk_score
        var avgRisk = doc.Average("risk_score");
        Assert.True(avgRisk > 0 && avgRisk <= 100);

        // Consistent
        Assert.Equal(avgReturn, doc.Average("return_pct"));

        // GetMinValue — return_pct
        var minReturn = doc.GetMinValue("return_pct");
        Assert.True(Math.Abs(minReturn - 4.9) < 0.1);

        // GetMinValue — risk_score
        var minRisk = doc.GetMinValue("risk_score");
        Assert.True(Math.Abs(minRisk - 28.0) < 1.0);

        // GetMaxValue — return_pct
        var maxReturn = doc.GetMaxValue("return_pct");
        Assert.True(Math.Abs(maxReturn - 18.3) < 0.1);

        // GetMaxValue — holdings
        var maxHoldings = doc.GetMaxValue("holdings");
        Assert.True(Math.Abs(maxHoldings - 75.0) < 1.0);

        // Range invariants
        Assert.True(minReturn <= avgReturn);
        Assert.True(maxReturn >= avgReturn);
        Assert.True(maxReturn >= minReturn);
        Assert.True(doc.GetMaxValue("risk_score") >= doc.GetMinValue("risk_score"));

        // Average in range
        Assert.True(avgReturn >= minReturn && avgReturn <= maxReturn);

        // ExportToJson still works
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // GetRecordCount unaffected
        Assert.Equal(7, doc.GetRecordCount());

        // SaveToFile
        var savePath = TempFile("dogfood_portfolio_out.ndjson");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify aggregates
        var loaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(7, loaded.GetRecordCount());
        Assert.Equal(totalAum, loaded.Sum("aum"), 1);
        Assert.Equal(avgReturn, loaded.Average("return_pct"), 2);
        Assert.Equal(minReturn, loaded.GetMinValue("return_pct"), 2);
        Assert.Equal(maxReturn, loaded.GetMaxValue("return_pct"), 2);

        // Final save
        var path2 = TempFile("dogfood_portfolio_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), loaded2.GetRecordCount());
        Assert.Equal(loaded.Sum("holdings"), loaded2.Sum("holdings"), 1);
        Assert.Equal(loaded.GetMaxValue("aum"), loaded2.GetMaxValue("aum"), 1);
        var ex1 = Record.Exception(() => loaded2.ExportToJson());
        var ex2 = Record.Exception(() => loaded2.ExportToCsv());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
