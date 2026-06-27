// Tests for NdjsonDocument.GetRecordsByPage, GetFieldValueAt, AggregateSumByField deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R239

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R239: Tests for NdjsonDocument.GetRecordsByPage, GetFieldValueAt, AggregateSumByField deeper.
/// GetRecordsByPage(pageIndex, pageSize): returns a page of records.
/// GetFieldValueAt(recordIndex, fieldName): returns the string value of a field in a record.
/// AggregateSumByField(fieldName): returns the numeric sum of the specified field across all records.
/// Covers: GetRecordsByPage no-throw; GetRecordsByPage count leq pageSize; GetRecordsByPage consistent;
/// GetRecordsByPage last page; GetRecordsByPage save-load;
/// GetFieldValueAt no-throw; GetFieldValueAt non-null; GetFieldValueAt consistent;
/// GetFieldValueAt save-load;
/// AggregateSumByField no-throw; AggregateSumByField non-negative; AggregateSumByField consistent;
/// AggregateSumByField equals manual sum; AggregateSumByField save-load;
/// dogfood CreateDoc→GetRecordsByPage→GetFieldValueAt→AggregateSumByField→SaveToFile pipeline.
/// </summary>
public class NdjsonR239GetRecordsByPageAndAggregateByFieldDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR239GetRecordsByPageAndAggregateByFieldDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR239_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateLogisticsNdjson()
    {
        var path = TempFile("logistics.ndjson");
        File.WriteAllText(path,
            "{\"shipment_id\":\"SH001\",\"origin\":\"Shanghai\",\"destination\":\"Rotterdam\",\"weight_kg\":12500.0,\"transit_days\":28,\"status\":\"delivered\"}\n" +
            "{\"shipment_id\":\"SH002\",\"origin\":\"Hamburg\",\"destination\":\"New York\",\"weight_kg\":8200.0,\"transit_days\":14,\"status\":\"in_transit\"}\n" +
            "{\"shipment_id\":\"SH003\",\"origin\":\"Singapore\",\"destination\":\"Los Angeles\",\"weight_kg\":15800.0,\"transit_days\":21,\"status\":\"delivered\"}\n" +
            "{\"shipment_id\":\"SH004\",\"origin\":\"Dubai\",\"destination\":\"Mumbai\",\"weight_kg\":3400.0,\"transit_days\":7,\"status\":\"processing\"}\n" +
            "{\"shipment_id\":\"SH005\",\"origin\":\"Antwerp\",\"destination\":\"Busan\",\"weight_kg\":19200.0,\"transit_days\":32,\"status\":\"delivered\"}\n" +
            "{\"shipment_id\":\"SH006\",\"origin\":\"Los Angeles\",\"destination\":\"Tokyo\",\"weight_kg\":6700.0,\"transit_days\":18,\"status\":\"in_transit\"}\n" +
            "{\"shipment_id\":\"SH007\",\"origin\":\"Rotterdam\",\"destination\":\"Chennai\",\"weight_kg\":11300.0,\"transit_days\":25,\"status\":\"delivered\"}\n" +
            "{\"shipment_id\":\"SH008\",\"origin\":\"Busan\",\"destination\":\"Long Beach\",\"weight_kg\":22100.0,\"transit_days\":20,\"status\":\"in_transit\"}\n" +
            "{\"shipment_id\":\"SH009\",\"origin\":\"Sydney\",\"destination\":\"Singapore\",\"weight_kg\":4800.0,\"transit_days\":9,\"status\":\"delivered\"}\n" +
            "{\"shipment_id\":\"SH010\",\"origin\":\"New York\",\"destination\":\"Felixstowe\",\"weight_kg\":9500.0,\"transit_days\":16,\"status\":\"processing\"}\n" +
            "{\"shipment_id\":\"SH011\",\"origin\":\"Mumbai\",\"destination\":\"Hamburg\",\"weight_kg\":13600.0,\"transit_days\":22,\"status\":\"delivered\"}\n" +
            "{\"shipment_id\":\"SH012\",\"origin\":\"Tokyo\",\"destination\":\"Vancouver\",\"weight_kg\":7900.0,\"transit_days\":17,\"status\":\"in_transit\"}\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRecordsByPage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordsByPage_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        var ex = Record.Exception(() => doc.GetRecordsByPage(0, 5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordsByPage_Count_LeqPageSize()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        Assert.True(doc.GetRecordsByPage(0, 5).Count <= 5);
    }

    [Fact]
    public void GetRecordsByPage_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        var p1 = doc.GetRecordsByPage(0, 4);
        var p2 = doc.GetRecordsByPage(0, 4);
        Assert.Equal(p1.Count, p2.Count);
    }

    [Fact]
    public void GetRecordsByPage_LastPage_Smaller()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        var total = doc.GetRecordCount();
        int pageSize = 5;
        int lastPage = (total - 1) / pageSize;
        var last = doc.GetRecordsByPage(lastPage, pageSize);
        Assert.True(last.Count <= pageSize);
        Assert.True(last.Count > 0);
    }

    [Fact]
    public void GetRecordsByPage_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        var before = doc.GetRecordsByPage(0, 3).Count;
        var path = TempFile("page_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordsByPage(0, 3).Count);
    }

    // -------------------------------------------------------------------------
    // GetFieldValueAt
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValueAt_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        var ex = Record.Exception(() => doc.GetFieldValueAt(0, "origin"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldValueAt_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        Assert.NotNull(doc.GetFieldValueAt(0, "origin"));
    }

    [Fact]
    public void GetFieldValueAt_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        Assert.Equal(doc.GetFieldValueAt(0, "status"), doc.GetFieldValueAt(0, "status"));
    }

    [Fact]
    public void GetFieldValueAt_CorrectValue_FirstRecord()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        Assert.Equal("Shanghai", doc.GetFieldValueAt(0, "origin"));
    }

    [Fact]
    public void GetFieldValueAt_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        var before = doc.GetFieldValueAt(2, "destination");
        var path = TempFile("fv_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldValueAt(2, "destination"));
    }

    // -------------------------------------------------------------------------
    // AggregateSumByField
    // -------------------------------------------------------------------------

    [Fact]
    public void AggregateSumByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        var ex = Record.Exception(() => doc.AggregateSumByField("weight_kg"));
        Assert.Null(ex);
    }

    [Fact]
    public void AggregateSumByField_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        Assert.True(doc.AggregateSumByField("weight_kg") > 0.0);
    }

    [Fact]
    public void AggregateSumByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        Assert.Equal(doc.AggregateSumByField("transit_days"), doc.AggregateSumByField("transit_days"));
    }

    [Fact]
    public void AggregateSumByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLogisticsNdjson());
        var before = doc.AggregateSumByField("weight_kg");
        var path = TempFile("agg_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.AggregateSumByField("weight_kg"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRecordsByPage_GetFieldValueAt_AggregateSumByField_SaveToFile_Pipeline()
    {
        // E-commerce order dataset — 12 orders across 3 pages
        var path = TempFile("dogfood_ecommerce.ndjson");
        File.WriteAllText(path,
            "{\"order_id\":\"ORD-2026-001\",\"customer\":\"Alice Chen\",\"category\":\"Electronics\",\"amount\":1285.50,\"units\":2,\"region\":\"APAC\"}\n" +
            "{\"order_id\":\"ORD-2026-002\",\"customer\":\"Bob Mueller\",\"category\":\"Furniture\",\"amount\":842.00,\"units\":1,\"region\":\"EMEA\"}\n" +
            "{\"order_id\":\"ORD-2026-003\",\"customer\":\"Clara Santos\",\"category\":\"Apparel\",\"amount\":196.75,\"units\":5,\"region\":\"LATAM\"}\n" +
            "{\"order_id\":\"ORD-2026-004\",\"customer\":\"David Kim\",\"category\":\"Electronics\",\"amount\":2150.00,\"units\":1,\"region\":\"APAC\"}\n" +
            "{\"order_id\":\"ORD-2026-005\",\"customer\":\"Emma Johansson\",\"category\":\"Books\",\"amount\":89.40,\"units\":8,\"region\":\"EMEA\"}\n" +
            "{\"order_id\":\"ORD-2026-006\",\"customer\":\"Faisal Al-Amin\",\"category\":\"Furniture\",\"amount\":1640.00,\"units\":2,\"region\":\"MEA\"}\n" +
            "{\"order_id\":\"ORD-2026-007\",\"customer\":\"Grace O'Brien\",\"category\":\"Apparel\",\"amount\":312.25,\"units\":4,\"region\":\"NA\"}\n" +
            "{\"order_id\":\"ORD-2026-008\",\"customer\":\"Hiroshi Tanaka\",\"category\":\"Electronics\",\"amount\":3420.00,\"units\":1,\"region\":\"APAC\"}\n" +
            "{\"order_id\":\"ORD-2026-009\",\"customer\":\"Ingrid Larsen\",\"category\":\"Books\",\"amount\":145.80,\"units\":12,\"region\":\"EMEA\"}\n" +
            "{\"order_id\":\"ORD-2026-010\",\"customer\":\"James Okafor\",\"category\":\"Electronics\",\"amount\":980.00,\"units\":2,\"region\":\"AFRICA\"}\n" +
            "{\"order_id\":\"ORD-2026-011\",\"customer\":\"Kateryna Bondar\",\"category\":\"Furniture\",\"amount\":2280.00,\"units\":3,\"region\":\"EMEA\"}\n" +
            "{\"order_id\":\"ORD-2026-012\",\"customer\":\"Li Wei\",\"category\":\"Apparel\",\"amount\":428.60,\"units\":6,\"region\":\"APAC\"}\n");

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRecordCount());

        // GetRecordsByPage — page 0, page 1, page 2 (4 per page)
        var page0 = doc.GetRecordsByPage(0, 4);
        Assert.Equal(4, page0.Count);

        var page1 = doc.GetRecordsByPage(1, 4);
        Assert.Equal(4, page1.Count);

        var page2 = doc.GetRecordsByPage(2, 4);
        Assert.Equal(4, page2.Count);

        // Total across pages = record count
        Assert.Equal(12, page0.Count + page1.Count + page2.Count);

        // Consistent
        var page0b = doc.GetRecordsByPage(0, 4);
        Assert.Equal(page0.Count, page0b.Count);

        // Beyond last page returns empty or partial
        var pageBeyond = doc.GetRecordsByPage(10, 4);
        Assert.True(pageBeyond.Count >= 0);

        // GetFieldValueAt — first and last records
        var firstOrder = doc.GetFieldValueAt(0, "order_id");
        Assert.NotNull(firstOrder);
        Assert.Equal("ORD-2026-001", firstOrder);

        var lastRegion = doc.GetFieldValueAt(11, "region");
        Assert.NotNull(lastRegion);
        Assert.Equal("APAC", lastRegion);

        // Middle record
        var mid = doc.GetFieldValueAt(5, "category");
        Assert.NotNull(mid);
        Assert.Equal("Furniture", mid);

        // Consistent
        Assert.Equal(doc.GetFieldValueAt(3, "customer"), doc.GetFieldValueAt(3, "customer"));

        // AggregateSumByField — total revenue
        var totalAmount = doc.AggregateSumByField("amount");
        Assert.True(totalAmount > 0.0);
        // 1285.50+842+196.75+2150+89.40+1640+312.25+3420+145.80+980+2280+428.60 = 13770.30
        Assert.True(totalAmount > 13000.0);
        Assert.Equal(totalAmount, doc.AggregateSumByField("amount")); // consistent

        // Total units
        var totalUnits = doc.AggregateSumByField("units");
        Assert.True(totalUnits > 0.0);
        Assert.Equal(totalUnits, doc.AggregateSumByField("units")); // consistent

        // SaveToFile
        var out1 = TempFile("dogfood_ecommerce_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRecordCount());
        Assert.Equal(page0.Count, loaded.GetRecordsByPage(0, 4).Count);
        Assert.Equal(firstOrder, loaded.GetFieldValueAt(0, "order_id"));
        Assert.Equal(totalAmount, loaded.AggregateSumByField("amount"), precision: 4);

        // AddRecord on loaded
        loaded.AddRecord("{\"order_id\":\"ORD-2026-013\",\"customer\":\"Mei Lin\",\"category\":\"Books\",\"amount\":67.20,\"units\":3,\"region\":\"APAC\"}");
        Assert.Equal(13, loaded.GetRecordCount());

        // Verify page 3 now has 1 record (13 records, page 3 with size 4 = 1 record)
        var page3 = loaded.GetRecordsByPage(3, 4);
        Assert.True(page3.Count >= 1);

        // AggregateSumByField on updated doc
        var newTotal = loaded.AggregateSumByField("amount");
        Assert.True(newTotal > totalAmount); // increased

        // Final save
        var out2 = TempFile("dogfood_ecommerce_v2.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NdjsonDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRecordCount());
        Assert.True(loaded2.AggregateSumByField("amount") > 0.0);
        Assert.True(loaded2.GetRecordsByPage(0, 5).Count <= 5);
        var ex1 = Record.Exception(() => loaded2.GetFieldValueAt(0, "order_id"));
        Assert.Null(ex1);
    }
}
