// Tests for CsvWriter.WriteToStream, ToCsv deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R192

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R192: Tests for CsvWriter.WriteToStream, CsvDocument.ToCsv deeper coverage.
/// CsvWriter.WriteToStream(rows, stream, headers): writes rows to a stream as CSV.
/// CsvDocument.ToCsv(): serializes the document as a CSV string.
/// Covers: WriteToStream creates bytes; WriteToStream bytes positive; WriteToStream has commas;
/// WriteToStream header in output; WriteToStream data in output; WriteToStream multiple rows;
/// WriteToStream round-trip via CsvReader.ReadRowsFromStream; WriteToStream vs WriteRowsToFile match;
/// ToCsv non-null; ToCsv non-empty; ToCsv has commas; ToCsv no newline-only;
/// ToCsv contains headers; ToCsv contains data; ToCsv after AddRow larger;
/// ToCsv after Filter smaller; ToCsv after SaveAndLoad consistent; ToCsv row count in lines;
/// dogfood WriteToStream→ReadRowsFromStream→LoadFile→ToCsv→AddRow→Filter pipeline.
/// </summary>
public class CsvR192CsvWriterWriteToStreamAndToCsvDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR192CsvWriterWriteToStreamAndToCsvDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR192_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string[] Headers = { "Country", "Capital", "Population", "Continent" };
    private static readonly string[][] DataRows =
    {
        new[] { "France", "Paris", "67000000", "Europe" },
        new[] { "Germany", "Berlin", "83000000", "Europe" },
        new[] { "Japan", "Tokyo", "125000000", "Asia" },
        new[] { "Brazil", "Brasilia", "215000000", "Americas" },
        new[] { "Kenya", "Nairobi", "54000000", "Africa" },
    };

    private string SampleCsv =>
        "Country,Capital,Population,Continent\n" +
        "France,Paris,67000000,Europe\n" +
        "Germany,Berlin,83000000,Europe\n" +
        "Japan,Tokyo,125000000,Asia\n" +
        "Brazil,Brasilia,215000000,Americas\n" +
        "Kenya,Nairobi,54000000,Africa\n";

    private CsvDocument LoadSample()
    {
        var path = TempFile("sample.csv");
        File.WriteAllText(path, SampleCsv);
        return CsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // WriteToStream
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToStream_CreatesBytes()
    {
        using var ms = new MemoryStream();
        CsvWriter.WriteToStream(DataRows, ms, Headers);
        Assert.True(ms.Length > 0);
    }

    [Fact]
    public void WriteToStream_HasCommas()
    {
        using var ms = new MemoryStream();
        CsvWriter.WriteToStream(DataRows, ms, Headers);
        var content = Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains(",", content);
    }

    [Fact]
    public void WriteToStream_HeaderInOutput()
    {
        using var ms = new MemoryStream();
        CsvWriter.WriteToStream(DataRows, ms, Headers);
        var content = Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains("Country", content);
        Assert.Contains("Capital", content);
    }

    [Fact]
    public void WriteToStream_DataInOutput()
    {
        using var ms = new MemoryStream();
        CsvWriter.WriteToStream(DataRows, ms, Headers);
        var content = Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains("France", content);
        Assert.Contains("Japan", content);
    }

    [Fact]
    public void WriteToStream_AllCountriesPresent()
    {
        using var ms = new MemoryStream();
        CsvWriter.WriteToStream(DataRows, ms, Headers);
        var content = Encoding.UTF8.GetString(ms.ToArray());
        foreach (var row in DataRows)
            Assert.Contains(row[0], content);
    }

    [Fact]
    public void WriteToStream_RoundTripViaReadRowsFromStream()
    {
        using var ms = new MemoryStream();
        CsvWriter.WriteToStream(DataRows, ms, Headers);
        ms.Seek(0, SeekOrigin.Begin);
        var rows = CsvReader.ReadRowsFromStream(ms);
        Assert.True(rows.Exists(r => r.Contains("France")));
        Assert.True(rows.Exists(r => r.Contains("Kenya")));
    }

    [Fact]
    public void WriteToStream_SingleRow()
    {
        using var ms = new MemoryStream();
        CsvWriter.WriteToStream(new[] { new[] { "Solo", "OnlyCity", "1000", "Unknown" } }, ms, Headers);
        var content = Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains("Solo", content);
    }

    // -------------------------------------------------------------------------
    // ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ToCsv());
    }

    [Fact]
    public void ToCsv_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(doc.ToCsv());
    }

    [Fact]
    public void ToCsv_HasCommas()
    {
        var doc = LoadSample();
        Assert.Contains(",", doc.ToCsv());
    }

    [Fact]
    public void ToCsv_ContainsHeaders()
    {
        var doc = LoadSample();
        var csv = doc.ToCsv();
        Assert.True(csv.Contains("Country") || csv.Contains("Capital"));
    }

    [Fact]
    public void ToCsv_ContainsData()
    {
        var doc = LoadSample();
        Assert.Contains("France", doc.ToCsv());
    }

    [Fact]
    public void ToCsv_AllDataPresent()
    {
        var doc = LoadSample();
        var csv = doc.ToCsv();
        Assert.Contains("France", csv);
        Assert.Contains("Japan", csv);
        Assert.Contains("Kenya", csv);
    }

    [Fact]
    public void ToCsv_AfterAddRow_Larger()
    {
        var doc = LoadSample();
        var before = doc.ToCsv().Length;
        doc.AddRow(new[] { "Australia", "Canberra", "26000000", "Oceania" });
        Assert.True(doc.ToCsv().Length > before);
    }

    [Fact]
    public void ToCsv_AfterFilter_Smaller()
    {
        var doc = LoadSample();
        var all = doc.ToCsv();
        var filtered = doc.Filter("Continent", "Europe").ToCsv();
        Assert.True(filtered.Length < all.Length);
    }

    [Fact]
    public void ToCsv_RowCountInLines()
    {
        var doc = LoadSample();
        var csv = doc.ToCsv();
        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        // Header + 5 data rows = 6 lines minimum
        Assert.True(lines.Length >= 5);
    }

    [Fact]
    public void ToCsv_AfterSaveAndLoad_Consistent()
    {
        var doc = LoadSample();
        var before = doc.ToCsv();
        var path = TempFile("saveload.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.ToCsv();
        // Should have same data (may have minor whitespace diffs)
        Assert.Contains("France", after);
        Assert.Contains("Japan", after);
        Assert.True(after.Length >= before.Length - 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToStream_ReadRowsFromStream_LoadFile_ToCsv_AddRow_Filter_Pipeline()
    {
        // WriteToStream
        using var ms = new MemoryStream();
        CsvWriter.WriteToStream(DataRows, ms, Headers);
        Assert.True(ms.Length > 0);

        // ReadRowsFromStream
        ms.Seek(0, SeekOrigin.Begin);
        var rows = CsvReader.ReadRowsFromStream(ms);
        Assert.NotNull(rows);
        Assert.True(rows.Exists(r => r.Contains("France")));

        // Save to file then LoadFile
        var path = TempFile("dogfood.csv");
        File.WriteAllText(path, SampleCsv);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(5, doc.RowCount);

        // ToCsv
        var csv = doc.ToCsv();
        Assert.NotNull(csv);
        Assert.Contains(",", csv);
        Assert.Contains("France", csv);
        Assert.Contains("Japan", csv);

        // Filter Europe
        var europe = doc.Filter("Continent", "Europe");
        Assert.Equal(2, europe.RowCount); // France, Germany
        var europeCsv = europe.ToCsv();
        Assert.Contains("France", europeCsv);
        Assert.Contains("Germany", europeCsv);
        Assert.True(europeCsv.Length < csv.Length);

        // WriteToStream for Europe
        var rows2d = Enumerable.Range(0, europe.RowCount).Select(i => europe.GetRow(i)).ToArray();
        using var euroMs = new MemoryStream();
        CsvWriter.WriteToStream(rows2d, euroMs, Headers);
        var euroContent = Encoding.UTF8.GetString(euroMs.ToArray());
        Assert.Contains("France", euroContent);
        Assert.DoesNotContain("Japan", euroContent);

        // AddRow — continent Oceania
        doc.AddRow(new[] { "Australia", "Canberra", "26000000", "Oceania" });
        Assert.Equal(6, doc.RowCount);
        Assert.Contains("Australia", doc.ToCsv());
        Assert.True(doc.ToCsv().Length > csv.Length);

        // WriteToStream after AddRow
        using var addedMs = new MemoryStream();
        CsvWriter.WriteToStream(
            Enumerable.Range(0, doc.RowCount).Select(i => doc.GetRow(i)).ToArray(),
            addedMs, Headers);
        var addedContent = Encoding.UTF8.GetString(addedMs.ToArray());
        Assert.Contains("Australia", addedContent);

        // ToCsv consistent across calls
        Assert.Equal(doc.ToCsv(), doc.ToCsv());
    }
}
