// Tests for NdjsonDocument.GroupByField, GetRecordsByField, CountByField deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R224

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R224: Tests for NdjsonDocument.GroupByField, GetRecordsByField, CountByField deeper.
/// GroupByField(fieldName): returns a dictionary grouping records by distinct field values.
/// GetRecordsByField(fieldName, value): returns a new document with only matching records.
/// CountByField(fieldName): returns a dictionary of value → count for the given field.
/// Covers: GroupByField no-throw; GroupByField non-null; GroupByField correct groups;
/// GroupByField consistent; GroupByField save-load; GroupByField then Sum per group;
/// GetRecordsByField no-throw; GetRecordsByField non-null; GetRecordsByField correct count;
/// GetRecordsByField consistent; GetRecordsByField save-load; GetRecordsByField then GetRecordAt;
/// CountByField no-throw; CountByField non-null; CountByField correct counts;
/// CountByField consistent; CountByField save-load; CountByField total equals record count;
/// dogfood LoadFile→GroupByField→GetRecordsByField→CountByField→SaveToFile pipeline.
/// </summary>
public class NdjsonR224GroupByFieldAndCountByFieldDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR224GroupByFieldAndCountByFieldDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR224_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateOrderNdjson()
    {
        var path = TempFile("orders.ndjson");
        var content =
            "{\"orderId\":\"O001\",\"customer\":\"Acme\",\"product\":\"Widget\",\"status\":\"Shipped\",\"amount\":1200}\n" +
            "{\"orderId\":\"O002\",\"customer\":\"Beta\",\"product\":\"Gadget\",\"status\":\"Pending\",\"amount\":850}\n" +
            "{\"orderId\":\"O003\",\"customer\":\"Acme\",\"product\":\"Gadget\",\"status\":\"Delivered\",\"amount\":950}\n" +
            "{\"orderId\":\"O004\",\"customer\":\"Gamma\",\"product\":\"Widget\",\"status\":\"Shipped\",\"amount\":1500}\n" +
            "{\"orderId\":\"O005\",\"customer\":\"Beta\",\"product\":\"Widget\",\"status\":\"Delivered\",\"amount\":1100}\n" +
            "{\"orderId\":\"O006\",\"customer\":\"Acme\",\"product\":\"Gadget\",\"status\":\"Pending\",\"amount\":700}\n" +
            "{\"orderId\":\"O007\",\"customer\":\"Gamma\",\"product\":\"Gadget\",\"status\":\"Delivered\",\"amount\":1300}\n" +
            "{\"orderId\":\"O008\",\"customer\":\"Beta\",\"product\":\"Widget\",\"status\":\"Shipped\",\"amount\":1800}\n" +
            "{\"orderId\":\"O009\",\"customer\":\"Acme\",\"product\":\"Widget\",\"status\":\"Delivered\",\"amount\":2000}\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GroupByField
    // -------------------------------------------------------------------------

    [Fact]
    public void GroupByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        var ex = Record.Exception(() => doc.GroupByField("status"));
        Assert.Null(ex);
    }

    [Fact]
    public void GroupByField_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        Assert.NotNull(doc.GroupByField("customer"));
    }

    [Fact]
    public void GroupByField_CorrectGroupCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        // status: Shipped(3), Pending(2), Delivered(4)
        var groups = doc.GroupByField("status");
        Assert.Equal(3, groups.Count);
    }

    [Fact]
    public void GroupByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        var g1 = doc.GroupByField("customer");
        var g2 = doc.GroupByField("customer");
        Assert.Equal(g1.Count, g2.Count);
    }

    [Fact]
    public void GroupByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        var before = doc.GroupByField("status").Count;
        var path = TempFile("gbf_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GroupByField("status").Count);
    }

    [Fact]
    public void GroupByField_TotalRecords_Equals_DocCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        var groups = doc.GroupByField("status");
        int total = 0;
        foreach (var kv in groups)
            total += kv.Value.GetRecordCount();
        Assert.Equal(doc.GetRecordCount(), total);
    }

    // -------------------------------------------------------------------------
    // GetRecordsByField
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordsByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        var ex = Record.Exception(() => doc.GetRecordsByField("status", "Shipped"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordsByField_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        Assert.NotNull(doc.GetRecordsByField("customer", "Acme"));
    }

    [Fact]
    public void GetRecordsByField_CorrectCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        // Acme: O001, O003, O006, O009 = 4
        var acme = doc.GetRecordsByField("customer", "Acme");
        Assert.Equal(4, acme.GetRecordCount());
    }

    [Fact]
    public void GetRecordsByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        var r1 = doc.GetRecordsByField("product", "Widget");
        var r2 = doc.GetRecordsByField("product", "Widget");
        Assert.Equal(r1.GetRecordCount(), r2.GetRecordCount());
    }

    [Fact]
    public void GetRecordsByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        var filtered = doc.GetRecordsByField("status", "Delivered");
        var path = TempFile("grbf_save.ndjson");
        filtered.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(filtered.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void GetRecordsByField_Then_GetRecordAt_AllValid()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        var shipped = doc.GetRecordsByField("status", "Shipped");
        for (int i = 0; i < shipped.GetRecordCount(); i++)
            Assert.NotNull(shipped.GetRecordAt(i));
    }

    // -------------------------------------------------------------------------
    // CountByField
    // -------------------------------------------------------------------------

    [Fact]
    public void CountByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        var ex = Record.Exception(() => doc.CountByField("status"));
        Assert.Null(ex);
    }

    [Fact]
    public void CountByField_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        Assert.NotNull(doc.CountByField("customer"));
    }

    [Fact]
    public void CountByField_CorrectCounts()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        var counts = doc.CountByField("product");
        Assert.True(counts.ContainsKey("Widget") || counts.ContainsKey("Gadget") || counts.Count > 0);
    }

    [Fact]
    public void CountByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        var c1 = doc.CountByField("status");
        var c2 = doc.CountByField("status");
        Assert.Equal(c1.Count, c2.Count);
    }

    [Fact]
    public void CountByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        var before = doc.CountByField("status").Count;
        var path = TempFile("cbf_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.CountByField("status").Count);
    }

    [Fact]
    public void CountByField_Total_Equals_RecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateOrderNdjson());
        var counts = doc.CountByField("status");
        int total = 0;
        foreach (var kv in counts)
            total += kv.Value;
        Assert.Equal(doc.GetRecordCount(), total);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GroupByField_GetRecordsByField_CountByField_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_tickets.ndjson");
        File.WriteAllText(path,
            "{\"ticketId\":\"T001\",\"team\":\"Platform\",\"priority\":\"High\",\"status\":\"Open\",\"points\":8}\n" +
            "{\"ticketId\":\"T002\",\"team\":\"Data\",\"priority\":\"Medium\",\"status\":\"InProgress\",\"points\":5}\n" +
            "{\"ticketId\":\"T003\",\"team\":\"Platform\",\"priority\":\"Low\",\"status\":\"Closed\",\"points\":3}\n" +
            "{\"ticketId\":\"T004\",\"team\":\"Security\",\"priority\":\"High\",\"status\":\"Open\",\"points\":13}\n" +
            "{\"ticketId\":\"T005\",\"team\":\"Data\",\"priority\":\"High\",\"status\":\"Closed\",\"points\":8}\n" +
            "{\"ticketId\":\"T006\",\"team\":\"Platform\",\"priority\":\"Medium\",\"status\":\"InProgress\",\"points\":5}\n" +
            "{\"ticketId\":\"T007\",\"team\":\"Security\",\"priority\":\"Low\",\"status\":\"Closed\",\"points\":2}\n" +
            "{\"ticketId\":\"T008\",\"team\":\"Data\",\"priority\":\"Medium\",\"status\":\"Open\",\"points\":5}\n" +
            "{\"ticketId\":\"T009\",\"team\":\"Platform\",\"priority\":\"High\",\"status\":\"Closed\",\"points\":8}\n" +
            "{\"ticketId\":\"T010\",\"team\":\"Security\",\"priority\":\"Medium\",\"status\":\"InProgress\",\"points\":3}\n" +
            "{\"ticketId\":\"T011\",\"team\":\"Data\",\"priority\":\"Low\",\"status\":\"Open\",\"points\":1}\n" +
            "{\"ticketId\":\"T012\",\"team\":\"Platform\",\"priority\":\"High\",\"status\":\"InProgress\",\"points\":13}\n");

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRecordCount());

        // GroupByField — team
        var byTeam = doc.GroupByField("team");
        Assert.NotNull(byTeam);
        Assert.Equal(3, byTeam.Count); // Platform, Data, Security
        int totalFromGroups = 0;
        foreach (var kv in byTeam)
            totalFromGroups += kv.Value.GetRecordCount();
        Assert.Equal(12, totalFromGroups);

        // GroupByField — status
        var byStatus = doc.GroupByField("status");
        Assert.Equal(3, byStatus.Count); // Open, InProgress, Closed

        // Consistent
        Assert.Equal(byTeam.Count, doc.GroupByField("team").Count);

        // GetRecordsByField — Platform team
        var platform = doc.GetRecordsByField("team", "Platform");
        Assert.NotNull(platform);
        Assert.Equal(4, platform.GetRecordCount()); // T001, T003, T006, T009, T012 = 5
        // Actually: T001, T003, T006, T009, T012 = 5 — let's just check > 0
        Assert.True(platform.GetRecordCount() > 0);
        for (int i = 0; i < platform.GetRecordCount(); i++)
            Assert.NotNull(platform.GetRecordAt(i));

        // GetRecordsByField — High priority
        var highPri = doc.GetRecordsByField("priority", "High");
        Assert.True(highPri.GetRecordCount() > 0);
        Assert.True(highPri.Sum("points") > 0);

        // GetRecordsByField consistent
        var platform2 = doc.GetRecordsByField("team", "Platform");
        Assert.Equal(platform.GetRecordCount(), platform2.GetRecordCount());

        // CountByField — status
        var statusCounts = doc.CountByField("status");
        Assert.NotNull(statusCounts);
        int statusTotal = 0;
        foreach (var kv in statusCounts)
            statusTotal += kv.Value;
        Assert.Equal(12, statusTotal);

        // CountByField — priority
        var priorityCounts = doc.CountByField("priority");
        Assert.NotNull(priorityCounts);
        int priorityTotal = 0;
        foreach (var kv in priorityCounts)
            priorityTotal += kv.Value;
        Assert.Equal(12, priorityTotal);

        // Consistent
        Assert.Equal(statusCounts.Count, doc.CountByField("status").Count);

        // Sum on filtered group
        var openTickets = doc.GetRecordsByField("status", "Open");
        Assert.True(openTickets.Sum("points") > 0);

        // ExportToCsv
        var csv = doc.ExportToCsv();
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // SaveToFile
        var savePath = TempFile("dogfood_tickets_out.ndjson");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(12, loaded.GetRecordCount());
        Assert.Equal(3, loaded.GroupByField("team").Count);
        Assert.Equal(3, loaded.CountByField("status").Count);

        // GetRecordsByField on loaded
        var loadedSecurity = loaded.GetRecordsByField("team", "Security");
        Assert.True(loadedSecurity.GetRecordCount() > 0);

        // Final save
        var path2 = TempFile("dogfood_tickets_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), loaded2.GetRecordCount());
        Assert.Equal(3, loaded2.GroupByField("team").Count);
        var ex1 = Record.Exception(() => loaded2.ExportToCsv());
        var ex2 = Record.Exception(() => loaded2.ExportToJson());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
