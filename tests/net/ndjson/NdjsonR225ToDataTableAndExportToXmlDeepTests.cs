// Tests for NdjsonDocument.ToDataTable, ExportToXml, CreateFromList deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R225

using System;
using System.IO;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R225: Tests for NdjsonDocument.ToDataTable, ExportToXml, CreateFromList deeper.
/// ToDataTable(): returns a DataTable representation of all records.
/// ExportToXml(): returns the document as an XML string.
/// CreateFromList(records): creates a new NdjsonDocument from a list of dictionaries.
/// Covers: ToDataTable no-throw; ToDataTable non-null; ToDataTable row count;
/// ToDataTable consistent; ToDataTable save-load round-trip via GetRecordCount;
/// ExportToXml no-throw; ExportToXml non-null; ExportToXml non-empty;
/// ExportToXml consistent; ExportToXml save-load consistent;
/// CreateFromList no-throw; CreateFromList non-null; CreateFromList correct count;
/// CreateFromList consistent; CreateFromList save-load; CreateFromList then Sum;
/// dogfood LoadFile→ToDataTable→ExportToXml→CreateFromList→SaveToFile pipeline.
/// </summary>
public class NdjsonR225ToDataTableAndExportToXmlDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR225ToDataTableAndExportToXmlDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR225_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateProductNdjson()
    {
        var path = TempFile("products.ndjson");
        var content =
            "{\"sku\":\"P001\",\"name\":\"Widget Pro\",\"category\":\"Hardware\",\"price\":299.99,\"stock\":45}\n" +
            "{\"sku\":\"P002\",\"name\":\"Data Module\",\"category\":\"Software\",\"price\":149.00,\"stock\":200}\n" +
            "{\"sku\":\"P003\",\"name\":\"Control Unit\",\"category\":\"Hardware\",\"price\":1249.00,\"stock\":12}\n" +
            "{\"sku\":\"P004\",\"name\":\"Analytics Suite\",\"category\":\"Software\",\"price\":499.00,\"stock\":500}\n" +
            "{\"sku\":\"P005\",\"name\":\"Sensor Array\",\"category\":\"Hardware\",\"price\":389.00,\"stock\":28}\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // ToDataTable
    // -------------------------------------------------------------------------

    [Fact]
    public void ToDataTable_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var ex = Record.Exception(() => doc.ToDataTable());
        Assert.Null(ex);
    }

    [Fact]
    public void ToDataTable_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.NotNull(doc.ToDataTable());
    }

    [Fact]
    public void ToDataTable_RowCount_Equals_RecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var dt = doc.ToDataTable();
        Assert.Equal(doc.GetRecordCount(), dt.Rows.Count);
    }

    [Fact]
    public void ToDataTable_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var dt1 = doc.ToDataTable();
        var dt2 = doc.ToDataTable();
        Assert.Equal(dt1.Rows.Count, dt2.Rows.Count);
        Assert.Equal(dt1.Columns.Count, dt2.Columns.Count);
    }

    [Fact]
    public void ToDataTable_SaveLoad_RecordCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var before = doc.ToDataTable().Rows.Count;
        var path = TempFile("dt_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.ToDataTable().Rows.Count);
    }

    // -------------------------------------------------------------------------
    // ExportToXml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToXml_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var ex = Record.Exception(() => doc.ExportToXml());
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToXml_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.NotNull(doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_NonEmpty()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.NotEmpty(doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var x1 = doc.ExportToXml();
        var x2 = doc.ExportToXml();
        Assert.Equal(x1.Length, x2.Length);
    }

    [Fact]
    public void ExportToXml_SaveLoad_LengthConsistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var before = doc.ExportToXml().Length;
        var path = TempFile("xml_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.ExportToXml().Length);
    }

    // -------------------------------------------------------------------------
    // CreateFromList
    // -------------------------------------------------------------------------

    [Fact]
    public void CreateFromList_NoThrow()
    {
        var records = new List<Dictionary<string, object>>
        {
            new() { { "id", 1 }, { "name", "Alpha" }, { "value", 100 } },
            new() { { "id", 2 }, { "name", "Beta" }, { "value", 200 } }
        };
        var ex = Record.Exception(() => NdjsonDocument.CreateFromList(records));
        Assert.Null(ex);
    }

    [Fact]
    public void CreateFromList_NonNull()
    {
        var records = new List<Dictionary<string, object>>
        {
            new() { { "x", 1 }, { "y", 2 } }
        };
        Assert.NotNull(NdjsonDocument.CreateFromList(records));
    }

    [Fact]
    public void CreateFromList_CorrectCount()
    {
        var records = new List<Dictionary<string, object>>
        {
            new() { { "a", 1 } },
            new() { { "a", 2 } },
            new() { { "a", 3 } }
        };
        var doc = NdjsonDocument.CreateFromList(records);
        Assert.Equal(3, doc.GetRecordCount());
    }

    [Fact]
    public void CreateFromList_Consistent()
    {
        var records = new List<Dictionary<string, object>>
        {
            new() { { "k", "v1" } },
            new() { { "k", "v2" } }
        };
        var d1 = NdjsonDocument.CreateFromList(records);
        var d2 = NdjsonDocument.CreateFromList(records);
        Assert.Equal(d1.GetRecordCount(), d2.GetRecordCount());
    }

    [Fact]
    public void CreateFromList_SaveLoad_Consistent()
    {
        var records = new List<Dictionary<string, object>>
        {
            new() { { "id", "R1" }, { "score", 88 } },
            new() { { "id", "R2" }, { "score", 92 } },
            new() { { "id", "R3" }, { "score", 76 } }
        };
        var doc = NdjsonDocument.CreateFromList(records);
        var path = TempFile("cfl_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(doc.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void CreateFromList_Then_Sum()
    {
        var records = new List<Dictionary<string, object>>
        {
            new() { { "product", "A" }, { "revenue", 1000 } },
            new() { { "product", "B" }, { "revenue", 2000 } },
            new() { { "product", "C" }, { "revenue", 3000 } }
        };
        var doc = NdjsonDocument.CreateFromList(records);
        Assert.Equal(6000.0, doc.Sum("revenue"), 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ToDataTable_ExportToXml_CreateFromList_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_catalog.ndjson");
        File.WriteAllText(path,
            "{\"itemId\":\"I001\",\"category\":\"Electronics\",\"name\":\"Processor X1\",\"unitCost\":450.00,\"quantity\":32,\"inStock\":true}\n" +
            "{\"itemId\":\"I002\",\"category\":\"Peripherals\",\"name\":\"Display Pro\",\"unitCost\":320.00,\"quantity\":18,\"inStock\":true}\n" +
            "{\"itemId\":\"I003\",\"category\":\"Electronics\",\"name\":\"Memory Module\",\"unitCost\":85.00,\"quantity\":150,\"inStock\":true}\n" +
            "{\"itemId\":\"I004\",\"category\":\"Accessories\",\"name\":\"Cable Kit\",\"unitCost\":24.99,\"quantity\":500,\"inStock\":true}\n" +
            "{\"itemId\":\"I005\",\"category\":\"Electronics\",\"name\":\"Storage Unit\",\"unitCost\":195.00,\"quantity\":64,\"inStock\":false}\n" +
            "{\"itemId\":\"I006\",\"category\":\"Peripherals\",\"name\":\"Input Device\",\"unitCost\":75.00,\"quantity\":42,\"inStock\":true}\n");

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(6, doc.GetRecordCount());

        // ToDataTable
        var dt = doc.ToDataTable();
        Assert.NotNull(dt);
        Assert.Equal(6, dt.Rows.Count);
        Assert.True(dt.Columns.Count > 0);
        Assert.Equal(dt.Rows.Count, doc.ToDataTable().Rows.Count); // consistent

        // ExportToXml
        var xml = doc.ExportToXml();
        Assert.NotNull(xml);
        Assert.NotEmpty(xml);
        Assert.Equal(xml.Length, doc.ExportToXml().Length); // consistent

        // ExportToJson
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // ExportToCsv
        var csv = doc.ExportToCsv();
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // CreateFromList — new catalog entries
        var newRecords = new List<Dictionary<string, object>>
        {
            new() { { "itemId", "I007" }, { "category", "Electronics" }, { "name", "Power Supply" }, { "unitCost", 120.00 }, { "quantity", 25 } },
            new() { { "itemId", "I008" }, { "category", "Accessories" }, { "name", "Mount Kit" }, { "unitCost", 35.50 }, { "quantity", 200 } },
            new() { { "itemId", "I009" }, { "category", "Peripherals" }, { "name", "Audio Unit" }, { "unitCost", 89.00 }, { "quantity", 30 } }
        };
        var newDoc = NdjsonDocument.CreateFromList(newRecords);
        Assert.NotNull(newDoc);
        Assert.Equal(3, newDoc.GetRecordCount());
        Assert.True(newDoc.Sum("unitCost") > 0);

        // CreateFromList consistent
        var newDoc2 = NdjsonDocument.CreateFromList(newRecords);
        Assert.Equal(newDoc.GetRecordCount(), newDoc2.GetRecordCount());

        // ToDataTable on CreateFromList result
        var newDt = newDoc.ToDataTable();
        Assert.Equal(3, newDt.Rows.Count);

        // ExportToXml on CreateFromList result
        var newXml = newDoc.ExportToXml();
        Assert.NotNull(newXml);
        Assert.NotEmpty(newXml);

        // MergeWith
        var merged = doc.MergeWith(newDoc);
        Assert.Equal(9, merged.GetRecordCount());

        // SaveToFile
        var savePath = TempFile("dogfood_catalog_merged.ndjson");
        merged.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRecordCount());

        // ToDataTable on loaded
        var loadedDt = loaded.ToDataTable();
        Assert.Equal(9, loadedDt.Rows.Count);

        // ExportToXml on loaded
        var loadedXml = loaded.ExportToXml();
        Assert.NotNull(loadedXml);
        Assert.NotEmpty(loadedXml);

        // CreateFromList on loaded — subset records
        var subsetRecords = new List<Dictionary<string, object>>();
        for (int i = 0; i < 4; i++)
            subsetRecords.Add(new Dictionary<string, object> { { "seq", i }, { "val", i * 100 } });
        var subDoc = NdjsonDocument.CreateFromList(subsetRecords);
        Assert.Equal(4, subDoc.GetRecordCount());

        // Final save
        var path2 = TempFile("dogfood_catalog_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), loaded2.GetRecordCount());
        var ex1 = Record.Exception(() => loaded2.ExportToXml());
        var ex2 = Record.Exception(() => loaded2.ExportToJson());
        var ex3 = Record.Exception(() => loaded2.ToDataTable());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
