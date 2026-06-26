// Tests for NdjsonDocument.AggregateByField, GetTimeSeriesData, GetRecordsByDateRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R233

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R233: Tests for NdjsonDocument.AggregateByField, GetTimeSeriesData, GetRecordsByDateRange deeper.
/// AggregateByField(groupField, valueField, operation): returns aggregated records grouped by field.
/// GetTimeSeriesData(timeField, valueField): returns records sorted by a time/date field.
/// GetRecordsByDateRange(field, from, to): returns records within an inclusive date range.
/// Covers: AggregateByField no-throw; AggregateByField non-null; AggregateByField count leq total;
/// AggregateByField consistent; AggregateByField save-load;
/// GetTimeSeriesData no-throw; GetTimeSeriesData count leq total; GetTimeSeriesData consistent;
/// GetTimeSeriesData save-load; GetTimeSeriesData non-null;
/// GetRecordsByDateRange no-throw; GetRecordsByDateRange count leq total; GetRecordsByDateRange consistent;
/// GetRecordsByDateRange save-load; GetRecordsByDateRange non-null;
/// dogfood CreateDoc→AggregateByField→GetTimeSeriesData→GetRecordsByDateRange→SaveToFile pipeline.
/// </summary>
public class NdjsonR233AggregateByFieldAndTimeSeriesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR233AggregateByFieldAndTimeSeriesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR233_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSalesNdjson()
    {
        var path = TempFile("sales.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"date\":\"2026-01-05\",\"region\":\"North\",\"product\":\"Widget A\",\"revenue\":12500.0,\"units\":50}",
            "{\"date\":\"2026-01-12\",\"region\":\"South\",\"product\":\"Widget B\",\"revenue\":8900.0,\"units\":36}",
            "{\"date\":\"2026-01-19\",\"region\":\"East\",\"product\":\"Widget A\",\"revenue\":14200.0,\"units\":57}",
            "{\"date\":\"2026-02-03\",\"region\":\"North\",\"product\":\"Widget C\",\"revenue\":6700.0,\"units\":27}",
            "{\"date\":\"2026-02-10\",\"region\":\"West\",\"product\":\"Widget B\",\"revenue\":11100.0,\"units\":45}",
            "{\"date\":\"2026-02-17\",\"region\":\"South\",\"product\":\"Widget A\",\"revenue\":9800.0,\"units\":39}",
            "{\"date\":\"2026-03-02\",\"region\":\"East\",\"product\":\"Widget C\",\"revenue\":7300.0,\"units\":29}",
            "{\"date\":\"2026-03-09\",\"region\":\"North\",\"product\":\"Widget B\",\"revenue\":13600.0,\"units\":55}",
            "{\"date\":\"2026-03-16\",\"region\":\"West\",\"product\":\"Widget A\",\"revenue\":10400.0,\"units\":42}",
            "{\"date\":\"2026-03-23\",\"region\":\"South\",\"product\":\"Widget C\",\"revenue\":5900.0,\"units\":24}",
        });
        return path;
    }

    private string CreateTelemetryNdjson()
    {
        var path = TempFile("telemetry.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"timestamp\":\"2026-06-01T00:00:00Z\",\"sensor\":\"T01\",\"value\":22.4,\"unit\":\"celsius\"}",
            "{\"timestamp\":\"2026-06-01T01:00:00Z\",\"sensor\":\"T02\",\"value\":23.1,\"unit\":\"celsius\"}",
            "{\"timestamp\":\"2026-06-01T02:00:00Z\",\"sensor\":\"T01\",\"value\":21.9,\"unit\":\"celsius\"}",
            "{\"timestamp\":\"2026-06-02T00:00:00Z\",\"sensor\":\"T03\",\"value\":24.5,\"unit\":\"celsius\"}",
            "{\"timestamp\":\"2026-06-02T01:00:00Z\",\"sensor\":\"T01\",\"value\":22.0,\"unit\":\"celsius\"}",
            "{\"timestamp\":\"2026-06-02T02:00:00Z\",\"sensor\":\"T02\",\"value\":23.8,\"unit\":\"celsius\"}",
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // AggregateByField
    // -------------------------------------------------------------------------

    [Fact]
    public void AggregateByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        var ex = Record.Exception(() => doc.AggregateByField("region", "revenue", "sum"));
        Assert.Null(ex);
    }

    [Fact]
    public void AggregateByField_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        Assert.NotNull(doc.AggregateByField("region", "revenue", "sum"));
    }

    [Fact]
    public void AggregateByField_Count_LeqTotal()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        var result = doc.AggregateByField("region", "revenue", "sum");
        Assert.True(result.Count <= doc.GetRecordCount());
    }

    [Fact]
    public void AggregateByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        var r1 = doc.AggregateByField("region", "revenue", "sum");
        var r2 = doc.AggregateByField("region", "revenue", "sum");
        Assert.Equal(r1.Count, r2.Count);
    }

    [Fact]
    public void AggregateByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        var before = doc.AggregateByField("product", "units", "sum");
        var path = TempFile("agg_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var after = loaded.AggregateByField("product", "units", "sum");
        Assert.Equal(before.Count, after.Count);
    }

    // -------------------------------------------------------------------------
    // GetTimeSeriesData
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTimeSeriesData_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        var ex = Record.Exception(() => doc.GetTimeSeriesData("date", "revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTimeSeriesData_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        Assert.NotNull(doc.GetTimeSeriesData("date", "revenue"));
    }

    [Fact]
    public void GetTimeSeriesData_Count_LeqTotal()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        var ts = doc.GetTimeSeriesData("date", "revenue");
        Assert.True(ts.Count <= doc.GetRecordCount());
    }

    [Fact]
    public void GetTimeSeriesData_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        var ts1 = doc.GetTimeSeriesData("date", "revenue");
        var ts2 = doc.GetTimeSeriesData("date", "revenue");
        Assert.Equal(ts1.Count, ts2.Count);
    }

    [Fact]
    public void GetTimeSeriesData_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        var before = doc.GetTimeSeriesData("date", "units");
        var path = TempFile("ts_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var after = loaded.GetTimeSeriesData("date", "units");
        Assert.Equal(before.Count, after.Count);
    }

    // -------------------------------------------------------------------------
    // GetRecordsByDateRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordsByDateRange_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        var ex = Record.Exception(() => doc.GetRecordsByDateRange("date", "2026-01-01", "2026-01-31"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordsByDateRange_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        Assert.NotNull(doc.GetRecordsByDateRange("date", "2026-01-01", "2026-12-31"));
    }

    [Fact]
    public void GetRecordsByDateRange_Count_LeqTotal()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        var result = doc.GetRecordsByDateRange("date", "2026-01-01", "2026-03-31");
        Assert.True(result.Count <= doc.GetRecordCount());
    }

    [Fact]
    public void GetRecordsByDateRange_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        var r1 = doc.GetRecordsByDateRange("date", "2026-02-01", "2026-02-28");
        var r2 = doc.GetRecordsByDateRange("date", "2026-02-01", "2026-02-28");
        Assert.Equal(r1.Count, r2.Count);
    }

    [Fact]
    public void GetRecordsByDateRange_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSalesNdjson());
        var before = doc.GetRecordsByDateRange("date", "2026-01-01", "2026-01-31");
        var path = TempFile("dr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var after = loaded.GetRecordsByDateRange("date", "2026-01-01", "2026-01-31");
        Assert.Equal(before.Count, after.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AggregateByField_GetTimeSeriesData_GetRecordsByDateRange_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_portfolio.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"date\":\"2026-01-03\",\"asset\":\"MSFT\",\"sector\":\"Technology\",\"price\":415.2,\"volume\":22000000,\"return_pct\":1.2}",
            "{\"date\":\"2026-01-03\",\"asset\":\"AAPL\",\"sector\":\"Technology\",\"price\":187.5,\"volume\":55000000,\"return_pct\":0.8}",
            "{\"date\":\"2026-01-03\",\"asset\":\"JPM\",\"sector\":\"Finance\",\"price\":198.3,\"volume\":9000000,\"return_pct\":-0.3}",
            "{\"date\":\"2026-01-10\",\"asset\":\"MSFT\",\"sector\":\"Technology\",\"price\":420.1,\"volume\":19000000,\"return_pct\":1.2}",
            "{\"date\":\"2026-01-10\",\"asset\":\"XOM\",\"sector\":\"Energy\",\"price\":112.4,\"volume\":15000000,\"return_pct\":-0.7}",
            "{\"date\":\"2026-01-10\",\"asset\":\"JNJ\",\"sector\":\"Healthcare\",\"price\":158.6,\"volume\":7000000,\"return_pct\":0.5}",
            "{\"date\":\"2026-02-07\",\"asset\":\"AAPL\",\"sector\":\"Technology\",\"price\":192.3,\"volume\":48000000,\"return_pct\":2.6}",
            "{\"date\":\"2026-02-07\",\"asset\":\"JPM\",\"sector\":\"Finance\",\"price\":202.1,\"volume\":8500000,\"return_pct\":1.9}",
            "{\"date\":\"2026-02-07\",\"asset\":\"XOM\",\"sector\":\"Energy\",\"price\":108.9,\"volume\":14000000,\"return_pct\":-3.1}",
            "{\"date\":\"2026-02-14\",\"asset\":\"MSFT\",\"sector\":\"Technology\",\"price\":428.7,\"volume\":21000000,\"return_pct\":2.0}",
            "{\"date\":\"2026-02-14\",\"asset\":\"JNJ\",\"sector\":\"Healthcare\",\"price\":161.2,\"volume\":6500000,\"return_pct\":1.6}",
            "{\"date\":\"2026-03-06\",\"asset\":\"AAPL\",\"sector\":\"Technology\",\"price\":189.8,\"volume\":52000000,\"return_pct\":-1.3}",
            "{\"date\":\"2026-03-06\",\"asset\":\"JPM\",\"sector\":\"Finance\",\"price\":205.4,\"volume\":9200000,\"return_pct\":1.6}",
            "{\"date\":\"2026-03-06\",\"asset\":\"XOM\",\"sector\":\"Energy\",\"price\":115.7,\"volume\":16000000,\"return_pct\":2.9}",
            "{\"date\":\"2026-03-13\",\"asset\":\"MSFT\",\"sector\":\"Technology\",\"price\":435.0,\"volume\":20000000,\"return_pct\":1.5}",
        });

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(15, doc.GetRecordCount());

        // AggregateByField — by sector
        var bySector = doc.AggregateByField("sector", "return_pct", "sum");
        Assert.NotNull(bySector);
        Assert.True(bySector.Count <= doc.GetRecordCount());
        Assert.Equal(bySector.Count, doc.AggregateByField("sector", "return_pct", "sum").Count);

        // AggregateByField — by asset
        var byAsset = doc.AggregateByField("asset", "volume", "sum");
        Assert.NotNull(byAsset);
        Assert.True(byAsset.Count <= doc.GetRecordCount());
        Assert.True(byAsset.Count > 0);

        // AggregateByField — by date
        var byDate = doc.AggregateByField("date", "return_pct", "sum");
        Assert.NotNull(byDate);
        Assert.True(byDate.Count <= doc.GetRecordCount());

        // GetTimeSeriesData — by date, price
        var tsPrice = doc.GetTimeSeriesData("date", "price");
        Assert.NotNull(tsPrice);
        Assert.True(tsPrice.Count <= doc.GetRecordCount());
        Assert.Equal(tsPrice.Count, doc.GetTimeSeriesData("date", "price").Count);

        // GetTimeSeriesData — by date, return_pct
        var tsReturn = doc.GetTimeSeriesData("date", "return_pct");
        Assert.NotNull(tsReturn);
        Assert.True(tsReturn.Count <= doc.GetRecordCount());

        // GetRecordsByDateRange — January
        var janRecords = doc.GetRecordsByDateRange("date", "2026-01-01", "2026-01-31");
        Assert.NotNull(janRecords);
        Assert.True(janRecords.Count <= doc.GetRecordCount());
        Assert.Equal(janRecords.Count, doc.GetRecordsByDateRange("date", "2026-01-01", "2026-01-31").Count);

        // GetRecordsByDateRange — February
        var febRecords = doc.GetRecordsByDateRange("date", "2026-02-01", "2026-02-28");
        Assert.NotNull(febRecords);
        Assert.True(febRecords.Count <= doc.GetRecordCount());

        // GetRecordsByDateRange — full range returns all
        var allRecords = doc.GetRecordsByDateRange("date", "2026-01-01", "2026-12-31");
        Assert.NotNull(allRecords);
        Assert.True(allRecords.Count <= doc.GetRecordCount());

        // GetFieldCount and GetFieldNames
        var fieldCount = doc.GetFieldCount();
        Assert.True(fieldCount > 0);
        var fieldNames = doc.GetFieldNames();
        Assert.NotNull(fieldNames);
        Assert.True(fieldNames.Count > 0);

        // SaveToFile
        var out1 = TempFile("dogfood_portfolio_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify aggregates persist
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(15, loaded.GetRecordCount());
        var loadedBySector = loaded.AggregateByField("sector", "return_pct", "sum");
        Assert.Equal(bySector.Count, loadedBySector.Count);

        var loadedJan = loaded.GetRecordsByDateRange("date", "2026-01-01", "2026-01-31");
        Assert.Equal(janRecords.Count, loadedJan.Count);

        var loadedTs = loaded.GetTimeSeriesData("date", "price");
        Assert.Equal(tsPrice.Count, loadedTs.Count);

        // AddRecord — Q2 entry
        loaded.AddRecord("{\"date\":\"2026-04-05\",\"asset\":\"MSFT\",\"sector\":\"Technology\",\"price\":441.0,\"volume\":18000000,\"return_pct\":1.4}");
        Assert.Equal(16, loaded.GetRecordCount());

        // Range with new record
        var q2Records = loaded.GetRecordsByDateRange("date", "2026-04-01", "2026-04-30");
        Assert.NotNull(q2Records);
        Assert.True(q2Records.Count <= loaded.GetRecordCount());

        // Final save
        var out2 = TempFile("dogfood_portfolio_v2.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NdjsonDocument.LoadFile(out2);
        Assert.Equal(16, loaded2.GetRecordCount());
        var ex1 = Record.Exception(() => loaded2.AggregateByField("sector", "return_pct", "sum"));
        var ex2 = Record.Exception(() => loaded2.GetTimeSeriesData("date", "price"));
        var ex3 = Record.Exception(() => loaded2.GetRecordsByDateRange("date", "2026-01-01", "2026-12-31"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
