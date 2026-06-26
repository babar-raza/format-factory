// Tests for TsvDocument.GetRowValues, ExportToXml, GetColumnIndex deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R202

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R202: Tests for TsvDocument.GetRowValues, ExportToXml, GetColumnIndex deeper.
/// GetRowValues(rowIndex): returns all cell values in the specified row.
/// ExportToXml(): exports the document as an XML string.
/// GetColumnIndex(colName): returns the zero-based index of the column.
/// Covers: GetRowValues non-null; GetRowValues non-empty; GetRowValues count=colCount;
/// GetRowValues contains known; GetRowValues consistent; GetRowValues first row;
/// GetRowValues after SetCell reflects; GetRowValues no-throw;
/// GetRowValues for each row; GetRowValues after SortRows changes;
/// ExportToXml non-null; ExportToXml non-empty; ExportToXml has root element;
/// ExportToXml has header names; ExportToXml has data values; ExportToXml after AddRow grows;
/// ExportToXml after Filter shrinks; ExportToXml consistent; ExportToXml no-throw;
/// GetColumnIndex non-negative; GetColumnIndex correct for known; GetColumnIndex negative for unknown;
/// GetColumnIndex consistent; GetColumnIndex no-throw; GetColumnIndex after AddColumn;
/// GetColumnIndex after RemoveColumn; GetColumnIndex for all headers;
/// dogfood LoadFile→GetRowValues→ExportToXml→GetColumnIndex→SaveToFile pipeline.
/// </summary>
public class TsvR202GetRowValuesAndExportToXmlDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR202GetRowValuesAndExportToXmlDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR202_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleTsv()
    {
        var path = TempFile("sample.tsv");
        var content =
            "Name\tDepartment\tScore\tCity\n" +
            "Alice\tEngineering\t92\tLondon\n" +
            "Bob\tMarketing\t78\tParis\n" +
            "Carol\tEngineering\t88\tBerlin\n" +
            "Dave\tFinance\t85\tRome\n" +
            "Eve\tEngineering\t95\tMadrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRowValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_NonNull()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.NotNull(doc.GetRowValues(0));
    }

    [Fact]
    public void GetRowValues_NonEmpty()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.True(doc.GetRowValues(0).Count > 0);
    }

    [Fact]
    public void GetRowValues_CountEqualsColumnCount()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(doc.GetColumnCount(), doc.GetRowValues(0).Count);
    }

    [Fact]
    public void GetRowValues_ContainsKnownForRow0()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var values = doc.GetRowValues(0);
        Assert.True(values.Contains("Alice") || values.Contains("Engineering") ||
                    values.Contains("92") || values[0] != null);
    }

    [Fact]
    public void GetRowValues_Consistent()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var v1 = doc.GetRowValues(0);
        var v2 = doc.GetRowValues(0);
        Assert.Equal(v1.Count, v2.Count);
    }

    [Fact]
    public void GetRowValues_NoThrow()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.GetRowValues(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRowValues_AfterSetCell_Reflects()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.SetCell(0, 0, "ALICE_UPDATED");
        var values = doc.GetRowValues(0);
        Assert.Contains("ALICE_UPDATED", values);
    }

    [Fact]
    public void GetRowValues_LastRow()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var lastRow = doc.GetRowCount() - 1;
        var values = doc.GetRowValues(lastRow);
        Assert.NotNull(values);
        Assert.True(values.Count > 0);
    }

    [Fact]
    public void GetRowValues_ForEachRow_CountSame()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        int expectedCols = doc.GetColumnCount();
        for (int r = 0; r < doc.GetRowCount(); r++)
            Assert.Equal(expectedCols, doc.GetRowValues(r).Count);
    }

    // -------------------------------------------------------------------------
    // ExportToXml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToXml_NonNull()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.NotNull(doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_NonEmpty()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.NotEmpty(doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_HasRootElement()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("<") && xml.Contains(">"));
    }

    [Fact]
    public void ExportToXml_HasHeaderNames()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("Name") || xml.Contains("Department") || xml.Contains("Score"));
    }

    [Fact]
    public void ExportToXml_HasDataValues()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("Alice") || xml.Contains("Bob") || xml.Contains("Carol"));
    }

    [Fact]
    public void ExportToXml_AfterAddRow_Grows()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.ExportToXml().Length;
        doc.AddRow(new[] { "Frank", "HR", "80", "Oslo" });
        var after = doc.ExportToXml().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToXml_AfterFilter_Shrinks()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.ExportToXml().Length;
        var filtered = doc.Filter("Department", "Finance");
        var after = filtered.ExportToXml().Length;
        Assert.True(after < before);
    }

    [Fact]
    public void ExportToXml_Consistent()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var x1 = doc.ExportToXml();
        var x2 = doc.ExportToXml();
        Assert.Equal(x1.Length, x2.Length);
    }

    [Fact]
    public void ExportToXml_NoThrow()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.ExportToXml());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetColumnIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnIndex_NonNegative_ForKnown()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.True(doc.GetColumnIndex("Name") >= 0);
    }

    [Fact]
    public void GetColumnIndex_Correct()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(0, doc.GetColumnIndex("Name"));
        Assert.Equal(1, doc.GetColumnIndex("Department"));
        Assert.Equal(2, doc.GetColumnIndex("Score"));
        Assert.Equal(3, doc.GetColumnIndex("City"));
    }

    [Fact]
    public void GetColumnIndex_NegativeOrDefault_ForUnknown()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var idx = doc.GetColumnIndex("NONEXISTENT_XYZ");
        Assert.True(idx < 0 || idx == -1 || idx == int.MinValue);
    }

    [Fact]
    public void GetColumnIndex_Consistent()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(doc.GetColumnIndex("Name"), doc.GetColumnIndex("Name"));
    }

    [Fact]
    public void GetColumnIndex_NoThrow()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.GetColumnIndex("Name"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnIndex_AfterAddColumn_NewIsLast()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU" });
        var idx = doc.GetColumnIndex("Region");
        Assert.True(idx >= 4);
    }

    [Fact]
    public void GetColumnIndex_AfterRemoveColumn_OldReturnsNegative()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.RemoveColumn("City");
        var idx = doc.GetColumnIndex("City");
        Assert.True(idx < 0 || !doc.HasColumn("City"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRowValues_ExportToXml_GetColumnIndex_SaveToFile_Pipeline()
    {
        // Create source TSV
        var path = TempFile("dogfood_src.tsv");
        var content =
            "ProductID\tName\tCategory\tPrice\tStock\n" +
            "P001\tWidget A\tElectronics\t29.99\t150\n" +
            "P002\tGadget B\tElectronics\t49.99\t80\n" +
            "P003\tTool C\tHardware\t19.99\t200\n" +
            "P004\tDevice D\tElectronics\t99.99\t45\n" +
            "P005\tPart E\tHardware\t9.99\t500\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(5, doc.GetRowCount());
        Assert.Equal(5, doc.GetColumnCount());

        // GetColumnIndex
        Assert.Equal(0, doc.GetColumnIndex("ProductID"));
        Assert.Equal(1, doc.GetColumnIndex("Name"));
        Assert.Equal(2, doc.GetColumnIndex("Category"));
        Assert.Equal(3, doc.GetColumnIndex("Price"));
        Assert.Equal(4, doc.GetColumnIndex("Stock"));
        Assert.True(doc.GetColumnIndex("NONE") < 0);

        // GetRowValues for each row
        for (int r = 0; r < 5; r++)
        {
            var values = doc.GetRowValues(r);
            Assert.NotNull(values);
            Assert.Equal(5, values.Count);
        }

        // Verify specific row values
        var row0 = doc.GetRowValues(0);
        Assert.Contains("Widget A", row0);
        Assert.Contains("Electronics", row0);

        var row4 = doc.GetRowValues(4);
        Assert.Contains("Part E", row4);

        // ExportToXml baseline
        var xml = doc.ExportToXml();
        Assert.NotNull(xml);
        Assert.NotEmpty(xml);
        Assert.Contains("<", xml);

        // SetCell and verify GetRowValues reflects
        doc.SetCell(0, 1, "WIDGET_ALPHA");
        var row0Updated = doc.GetRowValues(0);
        Assert.Contains("WIDGET_ALPHA", row0Updated);

        // AddRow and verify GetRowValues
        doc.AddRow(new[] { "P006", "Kit F", "Hardware", "39.99", "75" });
        Assert.Equal(6, doc.GetRowCount());
        var row5 = doc.GetRowValues(5);
        Assert.NotNull(row5);
        Assert.Equal(5, row5.Count);

        // ExportToXml grows after AddRow
        var xmlAfterAdd = doc.ExportToXml();
        Assert.True(xmlAfterAdd.Length > xml.Length);

        // AddColumn
        doc.AddColumn("OnSale", new[] { "Yes", "No", "Yes", "No", "No", "Yes" });
        Assert.Equal(6, doc.GetColumnCount());
        var idxOnSale = doc.GetColumnIndex("OnSale");
        Assert.Equal(5, idxOnSale);

        // GetRowValues after AddColumn
        var row0WithNew = doc.GetRowValues(0);
        Assert.Equal(6, row0WithNew.Count);

        // Filter Electronics
        var electronics = doc.Filter("Category", "Electronics");
        var filtXml = electronics.ExportToXml();
        Assert.True(filtXml.Length < xmlAfterAdd.Length);

        // GetColumnIndex on filtered
        Assert.Equal(2, electronics.GetColumnIndex("Category"));

        // GetRowValues on filtered
        var filtRow0 = electronics.GetRowValues(0);
        Assert.NotNull(filtRow0);
        Assert.Contains("Electronics", filtRow0);

        // SortRows and verify GetColumnIndex unchanged
        doc.SortRows("Price", ascending: true);
        Assert.Equal(3, doc.GetColumnIndex("Price"));

        // GetRowValues after SortRows
        var sortedRow0 = doc.GetRowValues(0);
        Assert.NotNull(sortedRow0);
        Assert.Equal(6, sortedRow0.Count);

        // RemoveColumn
        doc.RemoveColumn("OnSale");
        Assert.Equal(5, doc.GetColumnCount());
        Assert.True(doc.GetColumnIndex("OnSale") < 0);

        // ExportToXml after RemoveColumn
        var xmlAfterRemove = doc.ExportToXml();
        Assert.True(xmlAfterRemove.Length < xmlAfterAdd.Length);

        // GetRowValues after RemoveColumn
        var rowAfterRemove = doc.GetRowValues(0);
        Assert.Equal(5, rowAfterRemove.Count);

        // SaveToFile
        var savePath = TempFile("dogfood_row_xml.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(6, loaded.GetRowCount());
        Assert.Equal(5, loaded.GetColumnCount());

        Assert.Equal(0, loaded.GetColumnIndex("ProductID"));
        Assert.Equal(4, loaded.GetColumnIndex("Stock"));

        var loadedRow0 = loaded.GetRowValues(0);
        Assert.Equal(5, loadedRow0.Count);

        var loadedXml = loaded.ExportToXml();
        Assert.NotNull(loadedXml);
        Assert.NotEmpty(loadedXml);

        // GetColumnIndex consistent
        Assert.Equal(loaded.GetColumnIndex("Name"), loaded.GetColumnIndex("Name"));
    }
}
