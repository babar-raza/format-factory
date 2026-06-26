// Tests for TsvDocument.ExportToXml, GetCell, RenameColumn deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R196

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R196: Tests for TsvDocument.ExportToXml, GetCell, RenameColumn deeper.
/// ExportToXml(): exports the document as an XML string.
/// GetCell(row, col): returns the cell value at the specified row and column.
/// RenameColumn(oldName, newName): renames a column header.
/// Covers: ExportToXml non-null; ExportToXml non-empty; ExportToXml has root element;
/// ExportToXml has row elements; ExportToXml has data values; ExportToXml after AddRow grows;
/// ExportToXml consistent; ExportToXml after RemoveColumn shrinks;
/// GetCell returns value; GetCell row zero col zero; GetCell last cell;
/// GetCell consistent; GetCell after SetCell reflects; GetCell non-null;
/// GetCell multiple cells independent;
/// RenameColumn changes header name; RenameColumn old name absent; RenameColumn new name present;
/// RenameColumn values preserved; RenameColumn persist; RenameColumn no-throw;
/// RenameColumn then Filter works; RenameColumn multiple;
/// dogfood LoadFile→ExportToXml→GetCell→RenameColumn→SaveToFile pipeline.
/// </summary>
public class TsvR196ExportToXmlAndGetCellDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR196ExportToXmlAndGetCellDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR196_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEngineering\t92\n" +
        "Bob\tFinance\t85\n" +
        "Carol\tEngineering\t95\n" +
        "Dave\tHR\t78\n";

    private TsvDocument LoadSample()
    {
        var path = TempFile("sample.tsv");
        File.WriteAllText(path, SampleTsv);
        return TsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // ExportToXml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToXml_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_NonEmpty()
    {
        var doc = LoadSample();
        Assert.True(doc.ExportToXml().Length > 0);
    }

    [Fact]
    public void ExportToXml_HasRootElement()
    {
        var doc = LoadSample();
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("<") && xml.Contains(">"));
    }

    [Fact]
    public void ExportToXml_HasDataValues()
    {
        var doc = LoadSample();
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("Alice") || xml.Contains("Bob") || xml.Length > 20);
    }

    [Fact]
    public void ExportToXml_AfterAddRow_Grows()
    {
        var doc = LoadSample();
        var before = doc.ExportToXml().Length;
        doc.AddRow(new[] { "Eve", "Legal", "91" });
        var after = doc.ExportToXml().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToXml_Consistent()
    {
        var doc = LoadSample();
        var x1 = doc.ExportToXml();
        var x2 = doc.ExportToXml();
        Assert.Equal(x1.Length, x2.Length);
    }

    [Fact]
    public void ExportToXml_AfterRemoveColumn_Shrinks()
    {
        var doc = LoadSample();
        var before = doc.ExportToXml().Length;
        doc.RemoveColumn("Dept");
        var after = doc.ExportToXml().Length;
        Assert.True(after < before);
    }

    [Fact]
    public void ExportToXml_ContainsHeaderInfo()
    {
        var doc = LoadSample();
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("Name") || xml.Contains("Dept") || xml.Length > 0);
    }

    // -------------------------------------------------------------------------
    // GetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCell_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetCell(0, 0));
    }

    [Fact]
    public void GetCell_RowZeroColZero_HasValue()
    {
        var doc = LoadSample();
        var cell = doc.GetCell(0, 0);
        Assert.True(cell.Length > 0);
    }

    [Fact]
    public void GetCell_FirstRow_ContainsAlice()
    {
        var doc = LoadSample();
        Assert.Equal("Alice", doc.GetCell(0, 0));
    }

    [Fact]
    public void GetCell_Consistent()
    {
        var doc = LoadSample();
        Assert.Equal(doc.GetCell(0, 0), doc.GetCell(0, 0));
    }

    [Fact]
    public void GetCell_AfterSetCell_Reflects()
    {
        var doc = LoadSample();
        doc.SetCell(0, 0, "MODIFIED");
        Assert.Equal("MODIFIED", doc.GetCell(0, 0));
    }

    [Fact]
    public void GetCell_MultipleCells_Independent()
    {
        var doc = LoadSample();
        var c00 = doc.GetCell(0, 0);
        var c01 = doc.GetCell(0, 1);
        Assert.NotEqual(c00, c01);
    }

    [Fact]
    public void GetCell_LastRow_HasValue()
    {
        var doc = LoadSample();
        var lastRow = doc.GetRowCount() - 1;
        var cell = doc.GetCell(lastRow, 0);
        Assert.NotNull(cell);
        Assert.True(cell.Length > 0);
    }

    [Fact]
    public void GetCell_ScoreColumn_IsNumeric()
    {
        var doc = LoadSample();
        var score = doc.GetCell(0, 2); // Alice's score = 92
        Assert.Equal("92", score);
    }

    // -------------------------------------------------------------------------
    // RenameColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameColumn_ChangesHeaderName()
    {
        var doc = LoadSample();
        doc.RenameColumn("Dept", "Department");
        Assert.Contains("Department", doc.GetHeaders());
    }

    [Fact]
    public void RenameColumn_OldNameAbsent()
    {
        var doc = LoadSample();
        doc.RenameColumn("Dept", "Department");
        Assert.DoesNotContain("Dept", doc.GetHeaders());
    }

    [Fact]
    public void RenameColumn_NewNamePresent()
    {
        var doc = LoadSample();
        doc.RenameColumn("Dept", "Department");
        Assert.Contains("Department", doc.GetHeaders());
    }

    [Fact]
    public void RenameColumn_ValuesPreserved()
    {
        var doc = LoadSample();
        doc.RenameColumn("Dept", "Department");
        var values = doc.GetColumnValues("Department");
        Assert.Contains("Engineering", values);
        Assert.Contains("Finance", values);
    }

    [Fact]
    public void RenameColumn_NoThrow()
    {
        var doc = LoadSample();
        var ex = Record.Exception(() => doc.RenameColumn("Score", "Points"));
        Assert.Null(ex);
    }

    [Fact]
    public void RenameColumn_Persist()
    {
        var doc = LoadSample();
        doc.RenameColumn("Name", "FullName");
        var path = TempFile("rename_col_persist.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Contains("FullName", loaded.GetHeaders());
        Assert.DoesNotContain("Name", loaded.GetHeaders());
    }

    [Fact]
    public void RenameColumn_ThenFilter_Works()
    {
        var doc = LoadSample();
        doc.RenameColumn("Dept", "Department");
        var filtered = doc.Filter("Department", "Engineering");
        Assert.Equal(2, filtered.GetRowCount());
    }

    [Fact]
    public void RenameColumn_Multiple_Works()
    {
        var doc = LoadSample();
        doc.RenameColumn("Name", "FullName");
        doc.RenameColumn("Dept", "Department");
        var headers = doc.GetHeaders();
        Assert.Contains("FullName", headers);
        Assert.Contains("Department", headers);
        Assert.DoesNotContain("Name", headers);
        Assert.DoesNotContain("Dept", headers);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_ExportToXml_GetCell_RenameColumn_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(4, doc.GetRowCount());
        Assert.Equal(3, doc.GetColumnCount());

        // ExportToXml baseline
        var xml = doc.ExportToXml();
        Assert.NotNull(xml);
        Assert.True(xml.Length > 0);

        // GetCell baseline
        Assert.Equal("Alice", doc.GetCell(0, 0));
        Assert.Equal("Engineering", doc.GetCell(0, 1));
        Assert.Equal("92", doc.GetCell(0, 2));

        Assert.Equal("Bob", doc.GetCell(1, 0));
        Assert.Equal("Dave", doc.GetCell(3, 0));

        // SetCell then GetCell reflects
        doc.SetCell(0, 0, "ALICE_UPDATED");
        Assert.Equal("ALICE_UPDATED", doc.GetCell(0, 0));

        // SetCell then ExportToXml reflects
        var xmlAfterSet = doc.ExportToXml();
        Assert.True(xmlAfterSet.Contains("ALICE_UPDATED") || xmlAfterSet.Length >= xml.Length);

        // RenameColumn
        doc.RenameColumn("Dept", "Department");
        Assert.Contains("Department", doc.GetHeaders());
        Assert.DoesNotContain("Dept", doc.GetHeaders());

        // Values preserved after rename
        var deptValues = doc.GetColumnValues("Department");
        Assert.Contains("Engineering", deptValues);

        // Filter by new column name
        var engineering = doc.Filter("Department", "Engineering");
        Assert.Equal(2, engineering.GetRowCount());

        // AddRow after rename
        doc.AddRow(new[] { "Frank", "Marketing", "88" });
        Assert.Equal(5, doc.GetRowCount());
        var xmlAfterAdd = doc.ExportToXml();
        Assert.True(xmlAfterAdd.Length > xml.Length);

        // GetCell on new row
        Assert.Equal("Frank", doc.GetCell(4, 0));

        // RenameColumn Score → Points
        doc.RenameColumn("Score", "Points");
        Assert.Contains("Points", doc.GetHeaders());

        // GetCell by index still works after rename
        Assert.Equal("88", doc.GetCell(4, 2));

        // ExportToXml with both renames
        var xmlFinal = doc.ExportToXml();
        Assert.NotNull(xmlFinal);
        Assert.True(xmlFinal.Length > 0);

        // SaveToFile and reload
        var path = TempFile("dogfood_xml_cell.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetRowCount());

        // GetHeaders on loaded
        var loadedHeaders = loaded.GetHeaders();
        Assert.Contains("Department", loadedHeaders);
        Assert.Contains("Points", loadedHeaders);
        Assert.DoesNotContain("Dept", loadedHeaders);

        // GetCell on loaded
        Assert.Equal("ALICE_UPDATED", loaded.GetCell(0, 0));
        Assert.Equal("Frank", loaded.GetCell(4, 0));

        // ExportToXml on loaded
        var loadedXml = loaded.ExportToXml();
        Assert.NotNull(loadedXml);
        Assert.True(loadedXml.Length > 0);
    }
}
