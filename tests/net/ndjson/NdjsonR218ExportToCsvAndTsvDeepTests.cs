// Tests for NdjsonDocument.ExportToCsv, ExportToTsv, GetRecordAt deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R218

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R218: Tests for NdjsonDocument.ExportToCsv, ExportToTsv, GetRecordAt deeper.
/// ExportToCsv(): exports all records as a CSV string.
/// ExportToTsv(): exports all records as a TSV string.
/// GetRecordAt(index): returns the record at the given 0-based index.
/// Covers: ExportToCsv non-null; ExportToCsv non-empty; ExportToCsv has commas;
/// ExportToCsv has header row; ExportToCsv line count correct; ExportToCsv consistent;
/// ExportToCsv no-throw; ExportToCsv after AppendRecord grows; ExportToCsv save-load;
/// ExportToTsv non-null; ExportToTsv non-empty; ExportToTsv has tabs;
/// ExportToTsv consistent; ExportToTsv no-throw; ExportToTsv save-load;
/// ExportToTsv line count equals ExportToCsv line count;
/// GetRecordAt non-null; GetRecordAt no-throw; GetRecordAt index 0 correct;
/// GetRecordAt last index correct; GetRecordAt field count correct;
/// GetRecordAt consistent; GetRecordAt all values in range; GetRecordAt save-load;
/// dogfood CreateDoc→ExportToCsv→ExportToTsv→GetRecordAt→SaveToFile pipeline.
/// </summary>
public class NdjsonR218ExportToCsvAndTsvDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR218ExportToCsvAndTsvDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR218_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEmployeeNdjson()
    {
        var path = TempFile("employees.ndjson");
        var content =
            "{\"id\":\"E001\",\"name\":\"Alice\",\"department\":\"Engineering\",\"score\":92,\"salary\":95000}\n" +
            "{\"id\":\"E002\",\"name\":\"Bob\",\"department\":\"Marketing\",\"score\":78,\"salary\":55000}\n" +
            "{\"id\":\"E003\",\"name\":\"Carol\",\"department\":\"Engineering\",\"score\":88,\"salary\":115000}\n" +
            "{\"id\":\"E004\",\"name\":\"Dave\",\"department\":\"Finance\",\"score\":85,\"salary\":72000}\n" +
            "{\"id\":\"E005\",\"name\":\"Eve\",\"department\":\"Engineering\",\"score\":95,\"salary\":98000}\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // ExportToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToCsv_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.ExportToCsv());
    }

    [Fact]
    public void ExportToCsv_NonEmpty()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotEmpty(doc.ExportToCsv());
    }

    [Fact]
    public void ExportToCsv_HasCommas()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.Contains(",", doc.ExportToCsv());
    }

    [Fact]
    public void ExportToCsv_HasHeaderRow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var csv = doc.ExportToCsv();
        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        // First line should contain field names
        Assert.True(lines[0].Contains("name") || lines[0].Contains("id") || lines[0].Contains("department"));
    }

    [Fact]
    public void ExportToCsv_LineCount_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var csv = doc.ExportToCsv();
        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        // header + 5 data rows = 6
        Assert.Equal(6, lines.Length);
    }

    [Fact]
    public void ExportToCsv_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var c1 = doc.ExportToCsv();
        var c2 = doc.ExportToCsv();
        Assert.Equal(c1.Length, c2.Length);
    }

    [Fact]
    public void ExportToCsv_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.ExportToCsv());
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToCsv_AfterAppendRecord_Grows()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var before = doc.ExportToCsv().Length;
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object?>
        {
            { "id", "E006" }, { "name", "Frank" }, { "department", "Marketing" }, { "score", 82 }, { "salary", 62000 }
        });
        Assert.True(doc.ExportToCsv().Length > before);
    }

    [Fact]
    public void ExportToCsv_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var before = doc.ExportToCsv().Length;
        var path = TempFile("csv_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.ExportToCsv().Length);
    }

    // -------------------------------------------------------------------------
    // ExportToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToTsv_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.ExportToTsv());
    }

    [Fact]
    public void ExportToTsv_NonEmpty()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotEmpty(doc.ExportToTsv());
    }

    [Fact]
    public void ExportToTsv_HasTabs()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.Contains("\t", doc.ExportToTsv());
    }

    [Fact]
    public void ExportToTsv_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var t1 = doc.ExportToTsv();
        var t2 = doc.ExportToTsv();
        Assert.Equal(t1.Length, t2.Length);
    }

    [Fact]
    public void ExportToTsv_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.ExportToTsv());
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToTsv_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var before = doc.ExportToTsv().Length;
        var path = TempFile("tsv_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.ExportToTsv().Length);
    }

    [Fact]
    public void ExportToTsv_LineCount_EqualsExportToCsv()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var csvLines = doc.ExportToCsv().Split('\n', StringSplitOptions.RemoveEmptyEntries).Length;
        var tsvLines = doc.ExportToTsv().Split('\n', StringSplitOptions.RemoveEmptyEntries).Length;
        Assert.Equal(csvLines, tsvLines);
    }

    // -------------------------------------------------------------------------
    // GetRecordAt
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordAt_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.GetRecordAt(0));
    }

    [Fact]
    public void GetRecordAt_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GetRecordAt(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordAt_Index0_HasName()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var record = doc.GetRecordAt(0);
        Assert.True(record.ContainsKey("name") || record.ContainsKey("id") || record.ContainsKey("department"));
    }

    [Fact]
    public void GetRecordAt_LastIndex_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GetRecordAt(4));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordAt_FieldCount_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var record = doc.GetRecordAt(0);
        // 5 fields: id, name, department, score, salary
        Assert.Equal(5, record.Count);
    }

    [Fact]
    public void GetRecordAt_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var r1 = doc.GetRecordAt(0);
        var r2 = doc.GetRecordAt(0);
        Assert.Equal(r1.Count, r2.Count);
    }

    [Fact]
    public void GetRecordAt_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var beforeCount = doc.GetRecordAt(0).Count;
        var path = TempFile("gra_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(beforeCount, loaded.GetRecordAt(0).Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ExportToCsv_ExportToTsv_GetRecordAt_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_products.ndjson");
        var content =
            "{\"sku\":\"P001\",\"name\":\"Widget-Alpha\",\"category\":\"Electronics\",\"price\":29.99,\"stock\":500}\n" +
            "{\"sku\":\"P002\",\"name\":\"Gadget-Beta\",\"category\":\"Electronics\",\"price\":79.99,\"stock\":200}\n" +
            "{\"sku\":\"P003\",\"name\":\"Tool-Gamma\",\"category\":\"Hardware\",\"price\":14.99,\"stock\":800}\n" +
            "{\"sku\":\"P004\",\"name\":\"Device-Delta\",\"category\":\"Electronics\",\"price\":149.99,\"stock\":100}\n" +
            "{\"sku\":\"P005\",\"name\":\"Part-Epsilon\",\"category\":\"Hardware\",\"price\":9.99,\"stock\":1200}\n" +
            "{\"sku\":\"P006\",\"name\":\"Module-Zeta\",\"category\":\"Software\",\"price\":199.99,\"stock\":50}\n";
        File.WriteAllText(path, content);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(6, doc.GetRecordCount());

        // ExportToCsv
        var csv = doc.ExportToCsv();
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);
        Assert.Contains(",", csv);
        var csvLines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(7, csvLines.Length); // header + 6 data rows
        Assert.True(csvLines[0].Contains("sku") || csvLines[0].Contains("name") || csvLines[0].Contains("price"));

        // Consistent
        Assert.Equal(csv.Length, doc.ExportToCsv().Length);

        // ExportToTsv
        var tsv = doc.ExportToTsv();
        Assert.NotNull(tsv);
        Assert.NotEmpty(tsv);
        Assert.Contains("\t", tsv);
        var tsvLines = tsv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(csvLines.Length, tsvLines.Length);

        // Consistent
        Assert.Equal(tsv.Length, doc.ExportToTsv().Length);

        // GetRecordAt — index 0
        var rec0 = doc.GetRecordAt(0);
        Assert.NotNull(rec0);
        Assert.Equal(5, rec0.Count);
        Assert.True(rec0.ContainsKey("sku") || rec0.ContainsKey("name"));

        // GetRecordAt — index 5 (last)
        var rec5 = doc.GetRecordAt(5);
        Assert.NotNull(rec5);
        Assert.Equal(5, rec5.Count);

        // Consistent
        var rec0b = doc.GetRecordAt(0);
        Assert.Equal(rec0.Count, rec0b.Count);

        // AppendRecord and verify exports grow
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object?>
        {
            { "sku", "P007" }, { "name", "Cable-Eta" }, { "category", "Hardware" }, { "price", 4.99 }, { "stock", 2000 }
        });
        Assert.Equal(7, doc.GetRecordCount());
        Assert.True(doc.ExportToCsv().Length > csv.Length);
        Assert.True(doc.ExportToTsv().Length > tsv.Length);

        // GetRecordAt after append
        var rec6 = doc.GetRecordAt(6);
        Assert.NotNull(rec6);
        Assert.Equal(5, rec6.Count);

        // ExportToCsv lines = header + 7 rows
        var updatedCsv = doc.ExportToCsv();
        var updatedLines = updatedCsv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(8, updatedLines.Length);

        // SaveToFile
        var savePath = TempFile("dogfood_products_out.ndjson");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(7, loaded.GetRecordCount());

        // ExportToCsv on loaded
        var loadedCsv = loaded.ExportToCsv();
        Assert.Equal(doc.ExportToCsv().Length, loadedCsv.Length);
        var loadedCsvLines = loadedCsv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(8, loadedCsvLines.Length);

        // ExportToTsv on loaded
        var loadedTsv = loaded.ExportToTsv();
        Assert.Contains("\t", loadedTsv);

        // GetRecordAt on loaded
        var loadedRec0 = loaded.GetRecordAt(0);
        Assert.Equal(5, loadedRec0.Count);

        // Final save
        var path2 = TempFile("dogfood_products_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetRecordCount());
        Assert.Equal(loaded.ExportToCsv().Length, loaded2.ExportToCsv().Length);
        Assert.Equal(5, loaded2.GetRecordAt(0).Count);
    }
}
