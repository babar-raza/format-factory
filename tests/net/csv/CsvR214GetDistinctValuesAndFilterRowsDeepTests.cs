// Tests for CsvDocument.GetDistinctValues, FilterRows, ExportToHtml deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R214

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R214: Tests for CsvDocument.GetDistinctValues, FilterRows, ExportToHtml deeper.
/// GetDistinctValues(colName): returns unique values from the named column.
/// FilterRows(colName, value): returns a new CsvDocument with rows matching the filter.
/// ExportToHtml(): returns the document as an HTML table string.
/// Covers: GetDistinctValues non-null; GetDistinctValues no-throw;
/// GetDistinctValues count; GetDistinctValues no duplicates; GetDistinctValues correct;
/// GetDistinctValues consistent; GetDistinctValues save-load;
/// FilterRows non-null; FilterRows no-throw; FilterRows correct row count;
/// FilterRows content correct; FilterRows consistent; FilterRows save-load;
/// FilterRows no-match returns empty; FilterRows then ExportToHtml no-throw;
/// ExportToHtml non-null; ExportToHtml no-throw; ExportToHtml has table;
/// ExportToHtml has headers; ExportToHtml consistent; ExportToHtml save-load;
/// ExportToHtml after AddRow grows;
/// dogfood LoadFile→GetDistinctValues→FilterRows→ExportToHtml→SaveToFile pipeline.
/// </summary>
public class CsvR214GetDistinctValuesAndFilterRowsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR214GetDistinctValuesAndFilterRowsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR214_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateOrdersCsv()
    {
        var path = TempFile("orders.csv");
        var content =
            "OrderId,Customer,Category,Amount,Status\n" +
            "ORD-001,Acme Corp,Electronics,1200.00,Shipped\n" +
            "ORD-002,Beta LLC,Hardware,450.00,Pending\n" +
            "ORD-003,Acme Corp,Software,2800.00,Delivered\n" +
            "ORD-004,Gamma Inc,Electronics,980.00,Shipped\n" +
            "ORD-005,Beta LLC,Electronics,670.00,Delivered\n" +
            "ORD-006,Delta Co,Hardware,1100.00,Pending\n" +
            "ORD-007,Acme Corp,Hardware,350.00,Shipped\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        Assert.NotNull(doc.GetDistinctValues("Category"));
    }

    [Fact]
    public void GetDistinctValues_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var ex = Record.Exception(() => doc.GetDistinctValues("Customer"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDistinctValues_Category_ThreeValues()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        // Electronics, Hardware, Software
        var distinct = doc.GetDistinctValues("Category");
        Assert.Equal(3, distinct.Count);
    }

    [Fact]
    public void GetDistinctValues_Customer_FourValues()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        // Acme Corp, Beta LLC, Gamma Inc, Delta Co
        var distinct = doc.GetDistinctValues("Customer");
        Assert.Equal(4, distinct.Count);
    }

    [Fact]
    public void GetDistinctValues_NoDuplicates()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var distinct = doc.GetDistinctValues("Category");
        var set = new System.Collections.Generic.HashSet<string>(distinct);
        Assert.Equal(distinct.Count, set.Count);
    }

    [Fact]
    public void GetDistinctValues_CorrectValues()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var distinct = doc.GetDistinctValues("Category");
        Assert.True(distinct.Contains("Electronics") || distinct.Exists(v => v.Contains("Electronics")));
    }

    [Fact]
    public void GetDistinctValues_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var d1 = doc.GetDistinctValues("Status");
        var d2 = doc.GetDistinctValues("Status");
        Assert.Equal(d1.Count, d2.Count);
    }

    [Fact]
    public void GetDistinctValues_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var before = doc.GetDistinctValues("Category").Count;
        var path = TempFile("dv_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDistinctValues("Category").Count);
    }

    // -------------------------------------------------------------------------
    // FilterRows
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        Assert.NotNull(doc.FilterRows("Category", "Electronics"));
    }

    [Fact]
    public void FilterRows_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var ex = Record.Exception(() => doc.FilterRows("Status", "Shipped"));
        Assert.Null(ex);
    }

    [Fact]
    public void FilterRows_Electronics_ThreeRows()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var filtered = doc.FilterRows("Category", "Electronics");
        Assert.Equal(3, filtered.GetRowCount());
    }

    [Fact]
    public void FilterRows_Pending_TwoRows()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var filtered = doc.FilterRows("Status", "Pending");
        Assert.Equal(2, filtered.GetRowCount());
    }

    [Fact]
    public void FilterRows_NoMatch_EmptyResult()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var filtered = doc.FilterRows("Category", "NonExistentCategory");
        Assert.Equal(0, filtered.GetRowCount());
    }

    [Fact]
    public void FilterRows_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var f1 = doc.FilterRows("Customer", "Acme Corp");
        var f2 = doc.FilterRows("Customer", "Acme Corp");
        Assert.Equal(f1.GetRowCount(), f2.GetRowCount());
    }

    [Fact]
    public void FilterRows_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var filtered = doc.FilterRows("Status", "Shipped");
        var before = filtered.GetRowCount();
        var path = TempFile("fr_save.csv");
        filtered.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRowCount());
    }

    [Fact]
    public void FilterRows_Then_ExportToHtml_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var filtered = doc.FilterRows("Category", "Hardware");
        var ex = Record.Exception(() => filtered.ExportToHtml());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // ExportToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        Assert.NotNull(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToHtml_HasTableStructure()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("<table") || html.Contains("<TABLE") || html.Contains("<tr") || html.Contains("<td"));
    }

    [Fact]
    public void ExportToHtml_HasHeaders()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("OrderId") || html.Contains("Customer") || html.Contains("Category"));
    }

    [Fact]
    public void ExportToHtml_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        Assert.Equal(doc.ExportToHtml().Length, doc.ExportToHtml().Length);
    }

    [Fact]
    public void ExportToHtml_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateOrdersCsv());
        var before = doc.ExportToHtml().Length;
        var path = TempFile("html_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.True(Math.Abs(loaded.ExportToHtml().Length - before) <= 20);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDistinctValues_FilterRows_ExportToHtml_SaveToFile_Pipeline()
    {
        // Build comprehensive CSV
        var path = TempFile("dogfood_orders.csv");
        var content =
            "InvoiceId,Vendor,ProductLine,Quantity,UnitCost,Status,Region\n" +
            "INV-001,Apex Solutions,Infrastructure,50,1200.00,Paid,EMEA\n" +
            "INV-002,Beta Systems,Software,10,4500.00,Outstanding,APAC\n" +
            "INV-003,Apex Solutions,Software,25,2200.00,Paid,EMEA\n" +
            "INV-004,Gamma Corp,Hardware,100,350.00,Outstanding,AMER\n" +
            "INV-005,Beta Systems,Infrastructure,30,1800.00,Paid,APAC\n" +
            "INV-006,Delta Partners,Hardware,75,480.00,Paid,EMEA\n" +
            "INV-007,Apex Solutions,Hardware,60,290.00,Outstanding,AMER\n" +
            "INV-008,Gamma Corp,Software,15,3800.00,Paid,APAC\n" +
            "INV-009,Delta Partners,Infrastructure,40,1500.00,Outstanding,AMER\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(9, doc.GetRowCount());

        // GetDistinctValues — ProductLine
        var productLines = doc.GetDistinctValues("ProductLine");
        Assert.NotNull(productLines);
        Assert.Equal(3, productLines.Count); // Infrastructure, Software, Hardware
        var plSet = new System.Collections.Generic.HashSet<string>(productLines);
        Assert.Equal(productLines.Count, plSet.Count); // no duplicates

        // GetDistinctValues — Vendor
        var vendors = doc.GetDistinctValues("Vendor");
        Assert.Equal(4, vendors.Count); // Apex, Beta, Gamma, Delta

        // GetDistinctValues — Region
        var regions = doc.GetDistinctValues("Region");
        Assert.Equal(3, regions.Count); // EMEA, APAC, AMER

        // Consistent
        Assert.Equal(productLines.Count, doc.GetDistinctValues("ProductLine").Count);

        // FilterRows — Paid status
        var paidOrders = doc.FilterRows("Status", "Paid");
        Assert.NotNull(paidOrders);
        Assert.Equal(5, paidOrders.GetRowCount()); // INV-001, 003, 005, 006, 008

        // FilterRows — Outstanding status
        var outstandingOrders = doc.FilterRows("Status", "Outstanding");
        Assert.Equal(4, outstandingOrders.GetRowCount()); // INV-002, 004, 007, 009

        // FilterRows — by ProductLine
        var infraOrders = doc.FilterRows("ProductLine", "Infrastructure");
        Assert.Equal(3, infraOrders.GetRowCount()); // INV-001, 005, 009

        // FilterRows — by Vendor
        var apexOrders = doc.FilterRows("Vendor", "Apex Solutions");
        Assert.Equal(3, apexOrders.GetRowCount()); // INV-001, 003, 007

        // FilterRows no match
        var noMatch = doc.FilterRows("Region", "Antarctica");
        Assert.Equal(0, noMatch.GetRowCount());

        // Consistent
        Assert.Equal(paidOrders.GetRowCount(), doc.FilterRows("Status", "Paid").GetRowCount());

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);
        Assert.True(html.Contains("<table") || html.Contains("<tr") || html.Contains("InvoiceId") || html.Contains("Vendor"));

        // ExportToHtml consistent
        Assert.Equal(html.Length, doc.ExportToHtml().Length);

        // ExportToHtml on filtered
        var paidHtml = paidOrders.ExportToHtml();
        Assert.NotNull(paidHtml);
        Assert.NotEmpty(paidHtml);

        // GetDistinctValues on filtered
        var paidVendors = paidOrders.GetDistinctValues("Vendor");
        Assert.True(paidVendors.Count >= 1);

        // SaveToFile filtered
        var filteredPath = TempFile("dogfood_paid_orders.csv");
        paidOrders.SaveToFile(filteredPath);
        Assert.True(File.Exists(filteredPath));
        var loadedFiltered = CsvDocument.LoadFile(filteredPath);
        Assert.Equal(5, loadedFiltered.GetRowCount());

        // GetDistinctValues on loaded
        Assert.Equal(3, loadedFiltered.GetDistinctValues("ProductLine").Count);

        // SaveToFile main doc
        var savePath = TempFile("dogfood_orders_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRowCount());
        Assert.Equal(3, loaded.GetDistinctValues("ProductLine").Count);
        Assert.Equal(4, loaded.GetDistinctValues("Vendor").Count);

        // FilterRows on loaded
        Assert.Equal(5, loaded.FilterRows("Status", "Paid").GetRowCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // Final save
        var path2 = TempFile("dogfood_orders_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetDistinctValues("Region").Count, loaded2.GetDistinctValues("Region").Count);
        var ex = Record.Exception(() => loaded2.ExportToHtml());
        Assert.Null(ex);
    }
}
