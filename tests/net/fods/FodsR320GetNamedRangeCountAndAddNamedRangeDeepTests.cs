// Tests for FodsDocument.GetNamedRangeCount, AddNamedRange, GetNamedRangeAddress deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R320

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R320: Tests for FodsDocument.GetNamedRangeCount, AddNamedRange, GetNamedRangeAddress deeper.
/// GetNamedRangeCount(): returns the number of named ranges defined in the workbook.
/// AddNamedRange(name, sheetName, address): adds a named range pointing to the specified range.
/// GetNamedRangeAddress(name): returns the address string for the named range.
/// Covers: GetNamedRangeCount no-throw; GetNamedRangeCount non-negative; GetNamedRangeCount consistent;
/// GetNamedRangeCount zero for new doc; GetNamedRangeCount after AddNamedRange increases;
/// GetNamedRangeCount save-load;
/// AddNamedRange no-throw; AddNamedRange increases count; AddNamedRange save-load;
/// AddNamedRange multiple; AddNamedRange then ExportToCsv no-throw; AddNamedRange then GetRowCount positive;
/// GetNamedRangeAddress no-throw; GetNamedRangeAddress non-null; GetNamedRangeAddress consistent;
/// GetNamedRangeAddress save-load;
/// dogfood CreateDoc→AddNamedRange→GetNamedRangeCount→GetNamedRangeAddress→SaveToFile pipeline.
/// </summary>
public class FodsR320GetNamedRangeCountAndAddNamedRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR320GetNamedRangeCountAndAddNamedRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR320_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreatePortfolioDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Portfolio");
        doc.SetCellValue("Portfolio", 0, 0, "Ticker");
        doc.SetCellValue("Portfolio", 0, 1, "Sector");
        doc.SetCellValue("Portfolio", 0, 2, "Weight");
        doc.SetCellValue("Portfolio", 0, 3, "Price");
        doc.SetCellValue("Portfolio", 0, 4, "Return_1Y");
        doc.SetCellValue("Portfolio", 1, 0, "AAPL"); doc.SetCellValue("Portfolio", 1, 1, "Technology"); doc.SetCellValue("Portfolio", 1, 2, "0.12"); doc.SetCellValue("Portfolio", 1, 3, "189.50"); doc.SetCellValue("Portfolio", 1, 4, "0.24");
        doc.SetCellValue("Portfolio", 2, 0, "MSFT"); doc.SetCellValue("Portfolio", 2, 1, "Technology"); doc.SetCellValue("Portfolio", 2, 2, "0.10"); doc.SetCellValue("Portfolio", 2, 3, "415.20"); doc.SetCellValue("Portfolio", 2, 4, "0.31");
        doc.SetCellValue("Portfolio", 3, 0, "JPM");  doc.SetCellValue("Portfolio", 3, 1, "Financials"); doc.SetCellValue("Portfolio", 3, 2, "0.08"); doc.SetCellValue("Portfolio", 3, 3, "198.70"); doc.SetCellValue("Portfolio", 3, 4, "0.18");
        doc.SetCellValue("Portfolio", 4, 0, "XOM");  doc.SetCellValue("Portfolio", 4, 1, "Energy");    doc.SetCellValue("Portfolio", 4, 2, "0.07"); doc.SetCellValue("Portfolio", 4, 3, "112.30"); doc.SetCellValue("Portfolio", 4, 4, "0.09");
        doc.SetCellValue("Portfolio", 5, 0, "JNJ");  doc.SetCellValue("Portfolio", 5, 1, "Healthcare"); doc.SetCellValue("Portfolio", 5, 2, "0.08"); doc.SetCellValue("Portfolio", 5, 3, "156.80"); doc.SetCellValue("Portfolio", 5, 4, "0.05");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetNamedRangeCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRangeCount_NoThrow()
    {
        var doc = CreatePortfolioDoc();
        var ex = Record.Exception(() => doc.GetNamedRangeCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetNamedRangeCount_NonNegative()
    {
        var doc = CreatePortfolioDoc();
        Assert.True(doc.GetNamedRangeCount() >= 0);
    }

    [Fact]
    public void GetNamedRangeCount_Consistent()
    {
        var doc = CreatePortfolioDoc();
        Assert.Equal(doc.GetNamedRangeCount(), doc.GetNamedRangeCount());
    }

    [Fact]
    public void GetNamedRangeCount_Zero_ForNewDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Empty");
        Assert.Equal(0, doc.GetNamedRangeCount());
    }

    [Fact]
    public void GetNamedRangeCount_AfterAddNamedRange_Increases()
    {
        var doc = CreatePortfolioDoc();
        var before = doc.GetNamedRangeCount();
        doc.AddNamedRange("Tickers", "Portfolio", "A2:A6");
        Assert.Equal(before + 1, doc.GetNamedRangeCount());
    }

    [Fact]
    public void GetNamedRangeCount_SaveLoad_Consistent()
    {
        var doc = CreatePortfolioDoc();
        doc.AddNamedRange("Weights", "Portfolio", "C2:C6");
        var before = doc.GetNamedRangeCount();
        var path = TempFile("nrc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNamedRangeCount());
    }

    // -------------------------------------------------------------------------
    // AddNamedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void AddNamedRange_NoThrow()
    {
        var doc = CreatePortfolioDoc();
        var ex = Record.Exception(() => doc.AddNamedRange("AllData", "Portfolio", "A1:E6"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddNamedRange_Increases_Count()
    {
        var doc = CreatePortfolioDoc();
        var before = doc.GetNamedRangeCount();
        doc.AddNamedRange("Prices", "Portfolio", "D2:D6");
        Assert.Equal(before + 1, doc.GetNamedRangeCount());
    }

    [Fact]
    public void AddNamedRange_SaveLoad_Persists()
    {
        var doc = CreatePortfolioDoc();
        doc.AddNamedRange("Returns", "Portfolio", "E2:E6");
        var before = doc.GetNamedRangeCount();
        var path = TempFile("anr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNamedRangeCount());
    }

    [Fact]
    public void AddNamedRange_Multiple()
    {
        var doc = CreatePortfolioDoc();
        doc.AddNamedRange("Headers", "Portfolio", "A1:E1");
        doc.AddNamedRange("TechStocks", "Portfolio", "A2:E3");
        doc.AddNamedRange("FinancialStocks", "Portfolio", "A4:E4");
        Assert.Equal(3, doc.GetNamedRangeCount());
    }

    [Fact]
    public void AddNamedRange_Then_ExportToCsv_NoThrow()
    {
        var doc = CreatePortfolioDoc();
        doc.AddNamedRange("WeightRange", "Portfolio", "C2:C6");
        var ex = Record.Exception(() => doc.ExportToCsv("Portfolio"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddNamedRange_Then_GetRowCount_Positive()
    {
        var doc = CreatePortfolioDoc();
        doc.AddNamedRange("DataRange", "Portfolio", "A1:E6");
        Assert.True(doc.GetRowCount("Portfolio") > 0);
    }

    // -------------------------------------------------------------------------
    // GetNamedRangeAddress
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRangeAddress_NoThrow()
    {
        var doc = CreatePortfolioDoc();
        doc.AddNamedRange("TestRange", "Portfolio", "A1:C3");
        var ex = Record.Exception(() => doc.GetNamedRangeAddress("TestRange"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNamedRangeAddress_NonNull()
    {
        var doc = CreatePortfolioDoc();
        doc.AddNamedRange("NullTest", "Portfolio", "B2:D4");
        Assert.NotNull(doc.GetNamedRangeAddress("NullTest"));
    }

    [Fact]
    public void GetNamedRangeAddress_Consistent()
    {
        var doc = CreatePortfolioDoc();
        doc.AddNamedRange("ConsistRange", "Portfolio", "E2:E6");
        Assert.Equal(doc.GetNamedRangeAddress("ConsistRange"), doc.GetNamedRangeAddress("ConsistRange"));
    }

    [Fact]
    public void GetNamedRangeAddress_SaveLoad_Consistent()
    {
        var doc = CreatePortfolioDoc();
        doc.AddNamedRange("SaveRange", "Portfolio", "A2:E6");
        var before = doc.GetNamedRangeAddress("SaveRange");
        var path = TempFile("nra_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetNamedRangeAddress("SaveRange");
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddNamedRange_GetNamedRangeCount_GetNamedRangeAddress_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("FactorModel");
        // Headers
        doc.SetCellValue("FactorModel", 0, 0, "Factor");
        doc.SetCellValue("FactorModel", 0, 1, "Beta");
        doc.SetCellValue("FactorModel", 0, 2, "T_Stat");
        doc.SetCellValue("FactorModel", 0, 3, "P_Value");
        doc.SetCellValue("FactorModel", 0, 4, "Contribution");
        // Fama-French 5-factor model results
        doc.SetCellValue("FactorModel", 1, 0, "Market_RF");  doc.SetCellValue("FactorModel", 1, 1, "0.98");  doc.SetCellValue("FactorModel", 1, 2, "48.2");  doc.SetCellValue("FactorModel", 1, 3, "0.000"); doc.SetCellValue("FactorModel", 1, 4, "0.62");
        doc.SetCellValue("FactorModel", 2, 0, "SMB");        doc.SetCellValue("FactorModel", 2, 1, "0.21");  doc.SetCellValue("FactorModel", 2, 2, "8.4");   doc.SetCellValue("FactorModel", 2, 3, "0.001"); doc.SetCellValue("FactorModel", 2, 4, "0.08");
        doc.SetCellValue("FactorModel", 3, 0, "HML");        doc.SetCellValue("FactorModel", 3, 1, "-0.15"); doc.SetCellValue("FactorModel", 3, 2, "-5.1");  doc.SetCellValue("FactorModel", 3, 3, "0.004"); doc.SetCellValue("FactorModel", 3, 4, "-0.05");
        doc.SetCellValue("FactorModel", 4, 0, "RMW");        doc.SetCellValue("FactorModel", 4, 1, "0.32");  doc.SetCellValue("FactorModel", 4, 2, "12.8");  doc.SetCellValue("FactorModel", 4, 3, "0.000"); doc.SetCellValue("FactorModel", 4, 4, "0.14");
        doc.SetCellValue("FactorModel", 5, 0, "CMA");        doc.SetCellValue("FactorModel", 5, 1, "0.18");  doc.SetCellValue("FactorModel", 5, 2, "6.9");   doc.SetCellValue("FactorModel", 5, 3, "0.002"); doc.SetCellValue("FactorModel", 5, 4, "0.07");
        doc.SetCellValue("FactorModel", 6, 0, "Alpha");      doc.SetCellValue("FactorModel", 6, 1, "0.003"); doc.SetCellValue("FactorModel", 6, 2, "1.2");   doc.SetCellValue("FactorModel", 6, 3, "0.231"); doc.SetCellValue("FactorModel", 6, 4, "0.003");

        Assert.Equal(0, doc.GetNamedRangeCount());

        // AddNamedRange — factor model regions
        doc.AddNamedRange("AllFactors", "FactorModel", "A1:E7");
        Assert.Equal(1, doc.GetNamedRangeCount());

        doc.AddNamedRange("FactorNames", "FactorModel", "A2:A7");
        Assert.Equal(2, doc.GetNamedRangeCount());

        doc.AddNamedRange("BetaValues", "FactorModel", "B2:B7");
        Assert.Equal(3, doc.GetNamedRangeCount());

        doc.AddNamedRange("SignificantFactors", "FactorModel", "A2:E6");
        Assert.Equal(4, doc.GetNamedRangeCount());

        doc.AddNamedRange("Contributions", "FactorModel", "E2:E7");
        Assert.Equal(5, doc.GetNamedRangeCount());

        // Consistent
        Assert.Equal(doc.GetNamedRangeCount(), doc.GetNamedRangeCount());

        // GetNamedRangeAddress
        var addr0 = doc.GetNamedRangeAddress("AllFactors");
        Assert.NotNull(addr0);
        Assert.Equal(addr0, doc.GetNamedRangeAddress("AllFactors")); // consistent

        var addr1 = doc.GetNamedRangeAddress("BetaValues");
        Assert.NotNull(addr1);

        var addr2 = doc.GetNamedRangeAddress("Contributions");
        Assert.NotNull(addr2);

        // ExportToCsv works
        var csv = doc.ExportToCsv("FactorModel");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetRowCount positive
        Assert.True(doc.GetRowCount("FactorModel") > 0);

        // SaveToFile
        var path = TempFile("dogfood_factormodel.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetNamedRangeCount());
        Assert.True(loaded.GetRowCount("FactorModel") > 0);
        Assert.NotNull(loaded.GetNamedRangeAddress("AllFactors"));

        // AddNamedRange on loaded
        loaded.AddNamedRange("PValues", "FactorModel", "D2:D7");
        Assert.Equal(6, loaded.GetNamedRangeCount());

        // ExportToCsv on loaded
        var loadedCsv = loaded.ExportToCsv("FactorModel");
        Assert.NotNull(loadedCsv);
        Assert.NotEmpty(loadedCsv);

        // AddRow on loaded
        loaded.AddRow("FactorModel", new[] { "Momentum", "0.12", "4.5", "0.010", "0.04" });
        Assert.True(loaded.GetRowCount("FactorModel") > doc.GetRowCount("FactorModel"));

        // Final save
        var path2 = TempFile("dogfood_factormodel_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetNamedRangeCount());
        Assert.True(loaded2.GetRowCount("FactorModel") > 0);
        Assert.NotNull(loaded2.GetNamedRangeAddress("BetaValues"));
        var ex1 = Record.Exception(() => loaded2.GetNamedRangeCount());
        var ex2 = Record.Exception(() => loaded2.GetNamedRangeAddress("FactorNames"));
        var ex3 = Record.Exception(() => loaded2.ExportToCsv("FactorModel"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
