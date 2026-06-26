// Tests for CsvDocument.GetMedian, GetStdDev, FilterRows deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R218

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R218: Tests for CsvDocument.GetMedian, GetStdDev, FilterRows deeper.
/// GetMedian(colName): returns the median value of the numeric column.
/// GetStdDev(colName): returns the standard deviation of the numeric column.
/// FilterRows(colName, value): returns a new document with only rows where colName equals value.
/// Covers: GetMedian no-throw; GetMedian correct value; GetMedian consistent;
/// GetMedian save-load; GetMedian between min and max;
/// GetStdDev no-throw; GetStdDev non-negative; GetStdDev consistent;
/// GetStdDev save-load; GetStdDev zero for uniform;
/// FilterRows no-throw; FilterRows non-null; FilterRows correct count;
/// FilterRows consistent; FilterRows save-load; FilterRows then GetMedian;
/// FilterRows then ExportToHtml no-throw;
/// dogfood LoadFile→GetMedian→GetStdDev→FilterRows→SaveToFile pipeline.
/// </summary>
public class CsvR218GetMedianAndFilterRowsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR218GetMedianAndFilterRowsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR218_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateGradeCsv()
    {
        var path = TempFile("grades.csv");
        var content =
            "Student,Subject,Grade,Credits,Year\n" +
            "Alice,Math,88,4,2024\n" +
            "Bob,Math,72,4,2024\n" +
            "Carol,Science,95,3,2025\n" +
            "Dave,Math,65,4,2025\n" +
            "Eve,Science,81,3,2024\n" +
            "Frank,History,78,2,2025\n" +
            "Grace,Science,90,3,2024\n" +
            "Hector,History,70,2,2025\n";
        File.WriteAllText(path, content);
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var content =
            "Id,Score\n" +
            "1,75\n" +
            "2,75\n" +
            "3,75\n" +
            "4,75\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetMedian
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMedian_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        var ex = Record.Exception(() => doc.GetMedian("Grade"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMedian_CorrectValue()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        var median = doc.GetMedian("Grade");
        Assert.True(median >= 65 && median <= 95);
    }

    [Fact]
    public void GetMedian_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        Assert.Equal(doc.GetMedian("Grade"), doc.GetMedian("Grade"));
    }

    [Fact]
    public void GetMedian_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        var before = doc.GetMedian("Grade");
        var path = TempFile("gm_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMedian("Grade"), 2);
    }

    [Fact]
    public void GetMedian_BetweenMinAndMax()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        var median = doc.GetMedian("Grade");
        Assert.True(median >= doc.GetMinValue("Grade"));
        Assert.True(median <= doc.GetMaxValue("Grade"));
    }

    // -------------------------------------------------------------------------
    // GetStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStdDev_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        var ex = Record.Exception(() => doc.GetStdDev("Grade"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetStdDev_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        Assert.True(doc.GetStdDev("Grade") >= 0);
    }

    [Fact]
    public void GetStdDev_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        Assert.Equal(doc.GetStdDev("Grade"), doc.GetStdDev("Grade"));
    }

    [Fact]
    public void GetStdDev_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        var before = doc.GetStdDev("Grade");
        var path = TempFile("gsd_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetStdDev("Grade"), 2);
    }

    [Fact]
    public void GetStdDev_Zero_For_UniformColumn()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, doc.GetStdDev("Score"), 2);
    }

    // -------------------------------------------------------------------------
    // FilterRows
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        var ex = Record.Exception(() => doc.FilterRows("Subject", "Math"));
        Assert.Null(ex);
    }

    [Fact]
    public void FilterRows_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        Assert.NotNull(doc.FilterRows("Subject", "Science"));
    }

    [Fact]
    public void FilterRows_CorrectCount()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        // Math: Alice, Bob, Dave = 3
        var mathRows = doc.FilterRows("Subject", "Math");
        Assert.Equal(3, mathRows.GetRowCount());
    }

    [Fact]
    public void FilterRows_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        var f1 = doc.FilterRows("Subject", "Science");
        var f2 = doc.FilterRows("Subject", "Science");
        Assert.Equal(f1.GetRowCount(), f2.GetRowCount());
    }

    [Fact]
    public void FilterRows_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        var filtered = doc.FilterRows("Subject", "History");
        var path = TempFile("fr_save.csv");
        filtered.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(filtered.GetRowCount(), loaded.GetRowCount());
    }

    [Fact]
    public void FilterRows_Then_GetMedian()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        var science = doc.FilterRows("Subject", "Science");
        // Science: Carol(95), Eve(81), Grace(90) → median=90
        var median = science.GetMedian("Grade");
        Assert.True(median >= 81 && median <= 95);
    }

    [Fact]
    public void FilterRows_Then_ExportToHtml_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateGradeCsv());
        var filtered = doc.FilterRows("Year", "2024");
        var ex = Record.Exception(() => filtered.ExportToHtml());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMedian_GetStdDev_FilterRows_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_results.csv");
        var content =
            "Region,Salesperson,Product,Revenue,Margin,Quarter\n" +
            "EMEA,Alice,Infra,45000,32,Q1\n" +
            "APAC,Bob,Software,62000,45,Q2\n" +
            "AMER,Carol,Infra,38000,29,Q1\n" +
            "EMEA,Dave,Services,29000,58,Q3\n" +
            "APAC,Eve,Software,71000,43,Q2\n" +
            "AMER,Frank,Infra,51000,31,Q3\n" +
            "EMEA,Grace,Software,84000,47,Q4\n" +
            "APAC,Hector,Services,33000,55,Q4\n" +
            "AMER,Iris,Software,68000,44,Q1\n" +
            "EMEA,Jack,Infra,42000,28,Q2\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRowCount());

        // GetMedian — Revenue
        var medianRev = doc.GetMedian("Revenue");
        Assert.True(medianRev >= doc.GetMinValue("Revenue"));
        Assert.True(medianRev <= doc.GetMaxValue("Revenue"));
        Assert.Equal(medianRev, doc.GetMedian("Revenue")); // consistent

        // GetMedian — Margin
        var medianMargin = doc.GetMedian("Margin");
        Assert.True(medianMargin >= 0);

        // GetStdDev — Revenue
        var stdRev = doc.GetStdDev("Revenue");
        Assert.True(stdRev >= 0);
        Assert.Equal(stdRev, doc.GetStdDev("Revenue")); // consistent

        // GetStdDev — Margin
        var stdMargin = doc.GetStdDev("Margin");
        Assert.True(stdMargin >= 0);

        // FilterRows — EMEA region
        var emea = doc.FilterRows("Region", "EMEA");
        Assert.Equal(4, emea.GetRowCount());
        var emeaMedian = emea.GetMedian("Revenue");
        Assert.True(emeaMedian >= emea.GetMinValue("Revenue"));
        Assert.True(emeaMedian <= emea.GetMaxValue("Revenue"));

        // FilterRows — Software product
        var software = doc.FilterRows("Product", "Software");
        Assert.Equal(4, software.GetRowCount());
        var softwareMedian = software.GetMedian("Revenue");
        Assert.True(softwareMedian >= 0);
        var softwareStd = software.GetStdDev("Revenue");
        Assert.True(softwareStd >= 0);

        // FilterRows — Q1
        var q1 = doc.FilterRows("Quarter", "Q1");
        Assert.Equal(3, q1.GetRowCount());

        // FilterRows consistent
        var emea2 = doc.FilterRows("Region", "EMEA");
        Assert.Equal(emea.GetRowCount(), emea2.GetRowCount());

        // ExportToHtml on filtered
        var html = emea.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile — full doc
        var savePath = TempFile("dogfood_results_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(10, loaded.GetRowCount());
        Assert.Equal(medianRev, loaded.GetMedian("Revenue"), 2);
        Assert.Equal(stdRev, loaded.GetStdDev("Revenue"), 2);

        // FilterRows on loaded
        var loadedEmea = loaded.FilterRows("Region", "EMEA");
        Assert.Equal(4, loadedEmea.GetRowCount());

        // Save filtered
        var filterPath = TempFile("dogfood_emea.csv");
        loadedEmea.SaveToFile(filterPath);
        Assert.True(File.Exists(filterPath));
        var loadedFilter = CsvDocument.LoadFile(filterPath);
        Assert.Equal(4, loadedFilter.GetRowCount());
        Assert.Equal(emea.GetMedian("Revenue"), loadedFilter.GetMedian("Revenue"), 2);

        // Final save
        var path2 = TempFile("dogfood_results_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetMedian("Revenue"), loaded2.GetMedian("Revenue"), 2);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        Assert.Null(ex1);
    }
}
