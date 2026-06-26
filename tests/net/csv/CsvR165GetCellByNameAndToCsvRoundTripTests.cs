// Tests for CsvDocument.GetCellValue by name, ToCsv round-trip, SaveToFile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R165

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R165: Tests for CsvDocument.GetCellValue by column name, ToCsv round-trip, SaveToFile.
/// GetCellValue(row, colName): returns cell value by column header name.
/// ToCsv(): serializes document to CSV string with headers.
/// SaveToFile(path): writes CSV to file.
/// LoadFile(path): loads from file.
/// Covers: GetCellValue by name correct; GetCellValue by name for all rows;
/// GetCellValue returns null for missing column; ToCsv non-null;
/// ToCsv contains headers; ToCsv contains all rows;
/// ToCsv->Load round-trip count matches; ToCsv->Load column values correct;
/// SaveToFile creates file; SaveToFile content has headers;
/// SaveToFile->LoadFile round-trip row count matches;
/// Filter->ToCsv->Load count preserved;
/// dogfood Load->GetCellValues->ToCsv->Load->SaveToFile->LoadFile->Filter->Verify pipeline.
/// </summary>
public class CsvR165GetCellByNameAndToCsvRoundTripTests : IDisposable
{
    private readonly string _tempDir;

    private const string ThreeRowCsv =
        "name,dept,salary\n" +
        "Alice,Eng,95000\n" +
        "Bob,Finance,82000\n" +
        "Carol,Eng,88000";

    public CsvR165GetCellByNameAndToCsvRoundTripTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR165_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // GetCellValue by column name
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_ByColumnName_Row0_Correct()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var val = doc.GetCellValue(0, "name");
        Assert.Equal("Alice", val);
    }

    [Fact]
    public void GetCellValue_ByColumnName_Row1_Correct()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var val = doc.GetCellValue(1, "name");
        Assert.Equal("Bob", val);
    }

    [Fact]
    public void GetCellValue_ByColumnName_DeptColumn_Correct()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var val = doc.GetCellValue(2, "dept");
        Assert.Equal("Eng", val);
    }

    [Fact]
    public void GetCellValue_ByColumnName_SalaryColumn_Correct()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var val = doc.GetCellValue(0, "salary");
        Assert.Equal("95000", val);
    }

    [Fact]
    public void GetCellValue_ByColumnName_MissingColumn_NullOrEmpty()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var val = doc.GetCellValue(0, "nonexistent");
        Assert.True(val == null || val == string.Empty);
    }

    // -------------------------------------------------------------------------
    // ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_NonNull()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        Assert.NotNull(csv);
    }

    [Fact]
    public void ToCsv_ContainsHeaders()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains("name", csv);
        Assert.Contains("dept", csv);
        Assert.Contains("salary", csv);
    }

    [Fact]
    public void ToCsv_ContainsAllRows()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
        Assert.Contains("Carol", csv);
    }

    [Fact]
    public void ToCsv_Load_RoundTrip_CountMatches()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        var loaded = CsvDocument.Load(csv);
        Assert.Equal(3, loaded.RowCount);
    }

    [Fact]
    public void ToCsv_Load_RoundTrip_ColumnValuesCorrect()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        var loaded = CsvDocument.Load(csv);
        var names = loaded.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void Filter_ToCsv_Load_CountPreserved()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var csv = eng.ToCsv();
        var loaded = CsvDocument.Load(csv);
        Assert.Equal(2, loaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // SaveToFile / LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var path = TempFile("out.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_ContentHasHeaders()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var path = TempFile("hdr.csv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("name", content);
    }

    [Fact]
    public void SaveToFile_LoadFile_RowCountMatches()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var path = TempFile("roundtrip.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(3, loaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadGetCellValuesToCsvLoadSaveLoadFilterVerify_Pipeline()
    {
        // Load
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal(3, doc.RowCount);

        // GetCellValue by name for each row
        Assert.Equal("Alice", doc.GetCellValue(0, "name"));
        Assert.Equal("Bob", doc.GetCellValue(1, "name"));
        Assert.Equal("Carol", doc.GetCellValue(2, "name"));
        Assert.Equal("95000", doc.GetCellValue(0, "salary"));

        // ToCsv
        var csv = doc.ToCsv();
        Assert.Contains("dept", csv);

        // Load from ToCsv
        var reloaded = CsvDocument.Load(csv);
        Assert.Equal(3, reloaded.RowCount);

        // SaveToFile
        var path = TempFile("pipeline.csv");
        reloaded.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var fromFile = CsvDocument.LoadFile(path);
        Assert.Equal(3, fromFile.RowCount);

        // Filter Eng
        var eng = fromFile.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);

        // Verify values
        var salaries = eng.GetColumn("salary");
        Assert.Contains("95000", salaries);
        Assert.Contains("88000", salaries);
    }
}
