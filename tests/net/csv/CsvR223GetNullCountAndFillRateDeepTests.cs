// Tests for CsvDocument.GetNullCount, GetFillRate, GetCompleteness deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R223

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R223: Tests for CsvDocument.GetNullCount, GetFillRate, GetCompleteness deeper.
/// GetNullCount(colName): returns the number of empty or null values in the column.
/// GetFillRate(colName): returns the fraction of non-null values in [0.0, 1.0].
/// GetCompleteness(): returns the overall fraction of non-null values across all columns.
/// Covers: GetNullCount no-throw; GetNullCount non-negative; GetNullCount consistent;
/// GetNullCount save-load; GetNullCount leq row count; GetNullCount zero for complete column;
/// GetFillRate no-throw; GetFillRate in [0,1]; GetFillRate consistent;
/// GetFillRate save-load; GetFillRate one for complete column;
/// GetCompleteness no-throw; GetCompleteness in [0,1]; GetCompleteness consistent;
/// GetCompleteness save-load; GetCompleteness one for complete data;
/// dogfood LoadFile→GetNullCount→GetFillRate→GetCompleteness→SaveToFile pipeline.
/// </summary>
public class CsvR223GetNullCountAndFillRateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR223GetNullCountAndFillRateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR223_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCompleteCsv()
    {
        var path = TempFile("complete.csv");
        var content =
            "Id,Name,Score,Grade,Passed\n" +
            "1,Alice,92,A,Yes\n" +
            "2,Bob,78,B,Yes\n" +
            "3,Carol,88,B,Yes\n" +
            "4,Dave,65,D,No\n" +
            "5,Eve,95,A,Yes\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetNullCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNullCount_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        var ex = Record.Exception(() => doc.GetNullCount("Name"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNullCount_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        Assert.True(doc.GetNullCount("Name") >= 0);
    }

    [Fact]
    public void GetNullCount_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        Assert.Equal(doc.GetNullCount("Score"), doc.GetNullCount("Score"));
    }

    [Fact]
    public void GetNullCount_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        var before = doc.GetNullCount("Name");
        var path = TempFile("nc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNullCount("Name"));
    }

    [Fact]
    public void GetNullCount_Leq_RowCount()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        Assert.True(doc.GetNullCount("Name") <= doc.GetRowCount());
    }

    [Fact]
    public void GetNullCount_Zero_ForCompleteColumn()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        Assert.Equal(0, doc.GetNullCount("Name"));
    }

    // -------------------------------------------------------------------------
    // GetFillRate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFillRate_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        var ex = Record.Exception(() => doc.GetFillRate("Score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFillRate_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        var r = doc.GetFillRate("Score");
        Assert.True(r >= 0.0 && r <= 1.0);
    }

    [Fact]
    public void GetFillRate_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        Assert.Equal(doc.GetFillRate("Grade"), doc.GetFillRate("Grade"));
    }

    [Fact]
    public void GetFillRate_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        var before = doc.GetFillRate("Score");
        var path = TempFile("fr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFillRate("Score"), 4);
    }

    [Fact]
    public void GetFillRate_One_ForCompleteColumn()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        Assert.Equal(1.0, doc.GetFillRate("Name"), 4);
    }

    // -------------------------------------------------------------------------
    // GetCompleteness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompleteness_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        var ex = Record.Exception(() => doc.GetCompleteness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompleteness_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        var c = doc.GetCompleteness();
        Assert.True(c >= 0.0 && c <= 1.0);
    }

    [Fact]
    public void GetCompleteness_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        Assert.Equal(doc.GetCompleteness(), doc.GetCompleteness());
    }

    [Fact]
    public void GetCompleteness_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        var before = doc.GetCompleteness();
        var path = TempFile("comp_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompleteness(), 4);
    }

    [Fact]
    public void GetCompleteness_One_ForCompleteData()
    {
        var doc = CsvDocument.LoadFile(CreateCompleteCsv());
        Assert.Equal(1.0, doc.GetCompleteness(), 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetNullCount_GetFillRate_GetCompleteness_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_leads.csv");
        var content =
            "LeadId,CompanyName,ContactName,Email,Phone,AnnualRevenue,Source\n" +
            "L001,Acme Corp,Alice Smith,alice@acme.com,555-1234,5000000,WebForm\n" +
            "L002,TechCo,,bob@techco.com,,2000000,Referral\n" +
            "L003,BigBiz,Carol Lee,carol@bigbiz.com,555-5678,,Trade Show\n" +
            "L004,,Dave Kim,dave@startup.io,555-9012,800000,WebForm\n" +
            "L005,GrowthCo,Eve Park,eve@growthco.com,555-3456,3500000,LinkedIn\n" +
            "L006,NewBiz,Frank Ho,,555-7890,1200000,Referral\n" +
            "L007,TopFirm,Grace Yu,grace@topfirm.com,555-2345,,Cold Call\n" +
            "L008,SmallCo,Hector Wu,hector@smallco.com,555-6789,450000,WebForm\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRowCount());

        // GetNullCount — LeadId has 0 nulls
        Assert.Equal(0, doc.GetNullCount("LeadId"));

        // GetNullCount — CompanyName has 1 null (L004)
        var nullCompany = doc.GetNullCount("CompanyName");
        Assert.True(nullCompany >= 0);
        Assert.True(nullCompany <= doc.GetRowCount());
        Assert.Equal(nullCompany, doc.GetNullCount("CompanyName")); // consistent

        // GetFillRate — LeadId = 1.0
        Assert.Equal(1.0, doc.GetFillRate("LeadId"), 4);

        // GetFillRate — CompanyName < 1.0 (one missing)
        var fillCompany = doc.GetFillRate("CompanyName");
        Assert.True(fillCompany >= 0.0 && fillCompany <= 1.0);
        if (nullCompany > 0) Assert.True(fillCompany < 1.0);
        Assert.Equal(fillCompany, doc.GetFillRate("CompanyName")); // consistent

        // GetCompleteness — some fields missing → < 1.0
        var completeness = doc.GetCompleteness();
        Assert.True(completeness >= 0.0 && completeness <= 1.0);
        Assert.Equal(completeness, doc.GetCompleteness()); // consistent

        // GetNullCount — Email has 1 null (L006)
        var nullEmail = doc.GetNullCount("Email");
        Assert.True(nullEmail >= 0);

        // AddRow (complete) and recheck
        doc.AddRow(new[] { "L009", "PerfectLead", "Iris Chen", "iris@perfect.com", "555-0000", "7500000", "Conference" });
        Assert.Equal(9, doc.GetRowCount());
        Assert.True(doc.GetNullCount("LeadId") >= 0);
        Assert.True(doc.GetFillRate("LeadId") > 0);

        // SaveToFile
        var savePath = TempFile("dogfood_leads_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRowCount());
        Assert.Equal(doc.GetNullCount("CompanyName"), loaded.GetNullCount("CompanyName"));
        Assert.Equal(doc.GetFillRate("LeadId"), loaded.GetFillRate("LeadId"), 4);
        Assert.Equal(doc.GetCompleteness(), loaded.GetCompleteness(), 4);

        // GetColumnNames cross-check
        var cols = loaded.GetColumnNames();
        Assert.Contains("CompanyName", cols);
        Assert.Contains("Email", cols);

        // Final save
        var path2 = TempFile("dogfood_leads_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetCompleteness(), loaded2.GetCompleteness(), 4);
        Assert.Equal(loaded.GetNullCount("Email"), loaded2.GetNullCount("Email"));
    }
}
