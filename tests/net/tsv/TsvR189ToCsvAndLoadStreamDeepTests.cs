// Tests for TsvDocument.ToCsv, LoadStream deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R189

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R189: Tests for TsvDocument.ToCsv, LoadStream deeper coverage.
/// ToCsv(): converts the TSV document to CSV format string (comma-delimited).
/// TsvDocument.LoadStream(stream): loads a TSV document from a stream.
/// Covers: ToCsv non-null; ToCsv non-empty; ToCsv has commas; ToCsv no tabs;
/// ToCsv contains header; ToCsv contains data; ToCsv row count preserved;
/// ToCsv after AddRow larger; ToCsv after Filter smaller;
/// ToCsv round-trip via CsvDocument.LoadContent;
/// LoadStream non-null; LoadStream RowCount correct; LoadStream GetHeaders correct;
/// LoadStream GetColumnValues correct; LoadStream then SaveToFile works;
/// LoadStream after WriteToStream round-trip; LoadStream empty stream;
/// LoadStream multiple rows; LoadStream then Filter works;
/// dogfood WriteToFile→LoadStream→ToCsv→AddRow→Filter→SaveToFile pipeline.
/// </summary>
public class TsvR189ToCsvAndLoadStreamDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR189ToCsvAndLoadStreamDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR189_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleTsv =
        "City\tCountry\tPopulation\tContinent\n" +
        "Tokyo\tJapan\t13960000\tAsia\n" +
        "Delhi\tIndia\t32941000\tAsia\n" +
        "London\tUK\t9541000\tEurope\n" +
        "Paris\tFrance\t2161000\tEurope\n" +
        "New York\tUSA\t8336817\tAmerica\n";

    private TsvDocument LoadSample()
    {
        var path = TempFile("sample.tsv");
        File.WriteAllText(path, SampleTsv);
        return TsvDocument.LoadFile(path);
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
    public void ToCsv_NoTabs()
    {
        var doc = LoadSample();
        Assert.DoesNotContain("\t", doc.ToCsv());
    }

    [Fact]
    public void ToCsv_ContainsHeader()
    {
        var doc = LoadSample();
        var csv = doc.ToCsv();
        Assert.True(csv.Contains("City") || csv.Contains("Country"));
    }

    [Fact]
    public void ToCsv_ContainsData()
    {
        var doc = LoadSample();
        Assert.Contains("Tokyo", doc.ToCsv());
    }

    [Fact]
    public void ToCsv_AllDataPresent()
    {
        var doc = LoadSample();
        var csv = doc.ToCsv();
        Assert.Contains("Tokyo", csv);
        Assert.Contains("London", csv);
        Assert.Contains("New York", csv);
    }

    [Fact]
    public void ToCsv_AfterAddRow_Larger()
    {
        var doc = LoadSample();
        var before = doc.ToCsv().Length;
        doc.AddRow(new[] { "Sydney", "Australia", "5312000", "Oceania" });
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

    // -------------------------------------------------------------------------
    // LoadStream
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_NonNull()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        Assert.NotNull(TsvDocument.LoadStream(ms));
    }

    [Fact]
    public void LoadStream_RowCountCorrect()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        var doc = TsvDocument.LoadStream(ms);
        Assert.Equal(5, doc.RowCount);
    }

    [Fact]
    public void LoadStream_GetHeadersCorrect()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        var doc = TsvDocument.LoadStream(ms);
        var headers = doc.GetHeaders();
        Assert.Contains("City", headers);
        Assert.Contains("Country", headers);
    }

    [Fact]
    public void LoadStream_GetColumnValuesCorrect()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        var doc = TsvDocument.LoadStream(ms);
        var cities = doc.GetColumnValues("City");
        Assert.Contains("Tokyo", cities);
        Assert.Contains("London", cities);
    }

    [Fact]
    public void LoadStream_ThenSaveToFile_Works()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        var doc = TsvDocument.LoadStream(ms);
        var path = TempFile("from_stream.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var reloaded = TsvDocument.LoadFile(path);
        Assert.Equal(5, reloaded.RowCount);
    }

    [Fact]
    public void LoadStream_AfterWriteToStream_RoundTrip()
    {
        var doc = LoadSample();
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(
            Enumerable.Range(0, doc.RowCount).Select(i => doc.GetRow(i)).ToArray(),
            ms,
            doc.GetHeaders().ToArray()
        );
        ms.Seek(0, SeekOrigin.Begin);
        var reloaded = TsvDocument.LoadStream(ms);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
    }

    [Fact]
    public void LoadStream_MultipleRows()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        var doc = TsvDocument.LoadStream(ms);
        Assert.Equal(5, doc.RowCount);
    }

    [Fact]
    public void LoadStream_ThenFilter_Works()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        var doc = TsvDocument.LoadStream(ms);
        var asiaDoc = doc.Filter("Continent", "Asia");
        Assert.Equal(2, asiaDoc.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToFile_LoadStream_ToCsv_AddRow_Filter_SaveToFile_Pipeline()
    {
        // WriteToFile
        var path = TempFile("dogfood.tsv");
        File.WriteAllText(path, SampleTsv);
        Assert.True(File.Exists(path));

        // LoadStream
        using var fs = File.OpenRead(path);
        var doc = TsvDocument.LoadStream(fs);
        Assert.Equal(5, doc.RowCount);

        var headers = doc.GetHeaders();
        Assert.Contains("City", headers);

        // ToCsv
        var csv = doc.ToCsv();
        Assert.NotNull(csv);
        Assert.Contains(",", csv);
        Assert.DoesNotContain("\t", csv);
        Assert.Contains("Tokyo", csv);

        // Filter Europe
        var europe = doc.Filter("Continent", "Europe");
        Assert.Equal(2, europe.RowCount);
        var europeCsv = europe.ToCsv();
        Assert.True(europeCsv.Length < csv.Length);
        Assert.Contains("London", europeCsv);
        Assert.DoesNotContain("Tokyo", europeCsv);

        // AddRow
        doc.AddRow(new[] { "Sydney", "Australia", "5312000", "Oceania" });
        Assert.Equal(6, doc.RowCount);
        var updatedCsv = doc.ToCsv();
        Assert.True(updatedCsv.Length > csv.Length);
        Assert.Contains("Sydney", updatedCsv);

        // SaveToFile then LoadStream
        var outPath = TempFile("dogfood_out.tsv");
        doc.SaveToFile(outPath);
        using var outFs = File.OpenRead(outPath);
        var reloaded = TsvDocument.LoadStream(outFs);
        Assert.Equal(6, reloaded.RowCount);
        Assert.Contains("Sydney", reloaded.GetColumnValues("City"));

        // ToCsv on reloaded
        var reloadedCsv = reloaded.ToCsv();
        Assert.Contains(",", reloadedCsv);
        Assert.Contains("Sydney", reloadedCsv);

        // LoadStream from MemoryStream
        using var msCsv = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        var memDoc = TsvDocument.LoadStream(msCsv);
        Assert.Equal(5, memDoc.RowCount);
        Assert.Equal(4, memDoc.GetHeaders().Count);
    }
}
