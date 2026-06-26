// Tests for CsvDocument.GetRow, SaveToFile, LoadFile deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R188

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R188: Tests for CsvDocument.GetRow, SaveToFile, LoadFile deeper coverage.
/// GetRow(rowIndex): returns all cell values in the row at the given index.
/// SaveToFile(path): saves the document as a CSV file.
/// LoadFile(path): loads a CsvDocument from a CSV file.
/// Covers: GetRow non-null; GetRow count>=ColumnCount; GetRow first correct;
/// GetRow last correct; GetRow middle correct; GetRow after SetCellValue reflects;
/// GetRow after AddRow accessible; GetRow all rows non-null;
/// SaveToFile creates file; SaveToFile file non-empty; SaveToFile has comma;
/// SaveToFile has headers; SaveToFile has data; SaveToFile then LoadFile round-trip;
/// LoadFile non-null; LoadFile RowCount preserved; LoadFile headers correct;
/// LoadFile data correct via GetRow; LoadFile after mutation reflects; LoadFile GetColumnValues;
/// dogfood LoadContent→GetRow all→SetCellValue→SaveToFile→LoadFile→GetRow→GetColumnValues pipeline.
/// </summary>
public class CsvR188GetRowAndSaveLoadDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR188GetRowAndSaveLoadDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR188_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleCsv =
        "Name,Score,Dept\n" +
        "Alice,92,Engineering\n" +
        "Bob,78,Finance\n" +
        "Carol,85,Engineering\n" +
        "Dave,71,HR\n" +
        "Eve,90,Finance\n";

    private CsvDocument LoadSample()
    {
        var path = TempFile("sample.csv");
        File.WriteAllText(path, SampleCsv);
        return CsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // GetRow
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRow_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetRow(0));
    }

    [Fact]
    public void GetRow_CountGteColumnCount()
    {
        var doc = LoadSample();
        Assert.True(doc.GetRow(0).Count >= doc.ColumnCount);
    }

    [Fact]
    public void GetRow_FirstRowCorrect()
    {
        var doc = LoadSample();
        var row = doc.GetRow(0);
        Assert.Contains("Alice", row);
        Assert.Contains("92", row);
        Assert.Contains("Engineering", row);
    }

    [Fact]
    public void GetRow_LastRowCorrect()
    {
        var doc = LoadSample();
        var row = doc.GetRow(doc.RowCount - 1);
        Assert.Contains("Eve", row);
        Assert.Contains("90", row);
        Assert.Contains("Finance", row);
    }

    [Fact]
    public void GetRow_MiddleRowCorrect()
    {
        var doc = LoadSample();
        var row = doc.GetRow(2); // Carol
        Assert.Contains("Carol", row);
        Assert.Contains("85", row);
    }

    [Fact]
    public void GetRow_AfterSetCellValue_Reflects()
    {
        var doc = LoadSample();
        doc.SetCellValue(0, "Name", "ALICE_MOD");
        var row = doc.GetRow(0);
        Assert.Contains("ALICE_MOD", row);
    }

    [Fact]
    public void GetRow_AfterAddRow_Accessible()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Frank", "88", "Engineering" });
        var row = doc.GetRow(doc.RowCount - 1);
        Assert.Contains("Frank", row);
    }

    [Fact]
    public void GetRow_AllRows_NonNull()
    {
        var doc = LoadSample();
        for (var i = 0; i < doc.RowCount; i++)
            Assert.NotNull(doc.GetRow(i));
    }

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = LoadSample();
        var path = TempFile("saved.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_NonEmpty()
    {
        var doc = LoadSample();
        var path = TempFile("nonempty.csv");
        doc.SaveToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void SaveToFile_HasComma()
    {
        var doc = LoadSample();
        var path = TempFile("comma.csv");
        doc.SaveToFile(path);
        Assert.Contains(",", File.ReadAllText(path));
    }

    [Fact]
    public void SaveToFile_HasHeaders()
    {
        var doc = LoadSample();
        var path = TempFile("headers.csv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.True(content.Contains("Name") || content.Contains("Score"));
    }

    [Fact]
    public void SaveToFile_HasData()
    {
        var doc = LoadSample();
        var path = TempFile("data.csv");
        doc.SaveToFile(path);
        Assert.Contains("Alice", File.ReadAllText(path));
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_NonNull()
    {
        var doc = LoadSample();
        var path = TempFile("load.csv");
        doc.SaveToFile(path);
        Assert.NotNull(CsvDocument.LoadFile(path));
    }

    [Fact]
    public void LoadFile_RowCountPreserved()
    {
        var doc = LoadSample();
        var path = TempFile("rowcount.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }

    [Fact]
    public void LoadFile_HeadersCorrect()
    {
        var doc = LoadSample();
        var path = TempFile("hdr.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var headers = loaded.GetHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Score", headers);
        Assert.Contains("Dept", headers);
    }

    [Fact]
    public void LoadFile_DataCorrectViaGetRow()
    {
        var doc = LoadSample();
        var path = TempFile("data_row.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var row = loaded.GetRow(0);
        Assert.Contains("Alice", row);
    }

    [Fact]
    public void LoadFile_GetColumnValues_AllNames()
    {
        var doc = LoadSample();
        var path = TempFile("gcv.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var names = loaded.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_GetRow_SetCellValue_SaveToFile_LoadFile_GetRow_GetColumnValues_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(5, doc.RowCount);

        // GetRow for all rows
        for (var i = 0; i < doc.RowCount; i++)
        {
            var row = doc.GetRow(i);
            Assert.NotNull(row);
            Assert.True(row.Count >= 3);
        }

        // Verify specific rows
        Assert.Contains("Alice", doc.GetRow(0));
        Assert.Contains("Eve", doc.GetRow(4));
        Assert.Contains("Carol", doc.GetRow(2));

        // SetCellValue mutations
        doc.SetCellValue(0, "Name", "ALICE_UPDATED");
        doc.SetCellValue(4, "Score", "100");

        // GetRow reflects changes
        Assert.Contains("ALICE_UPDATED", doc.GetRow(0));
        Assert.Contains("100", doc.GetRow(4));

        // SaveToFile
        var path = TempFile("dogfood.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(5, loaded.RowCount);

        // GetRow on loaded
        var aliceRow = loaded.GetRow(0);
        Assert.Contains("ALICE_UPDATED", aliceRow);
        var eveRow = loaded.GetRow(4);
        Assert.Contains("100", eveRow);

        // GetColumnValues on loaded
        var names = loaded.GetColumnValues("Name");
        Assert.Equal(5, names.Count);
        Assert.Contains("ALICE_UPDATED", names);
        Assert.Contains("Eve", names);

        var scores = loaded.GetColumnValues("Score");
        Assert.Contains("100", scores);

        // AddRow to loaded and save again
        loaded.AddRow(new[] { "Frank", "88", "Engineering" });
        Assert.Equal(6, loaded.RowCount);
        var path2 = TempFile("dogfood2.csv");
        loaded.SaveToFile(path2);
        var final = CsvDocument.LoadFile(path2);
        Assert.Equal(6, final.RowCount);
        Assert.Contains("Frank", final.GetColumnValues("Name"));
    }
}
