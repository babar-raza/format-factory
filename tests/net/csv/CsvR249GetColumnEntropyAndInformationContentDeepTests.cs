// Tests for CsvDocument.GetColumnEntropy, GetColumnInformationContent, GetColumnMutualInformation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R249

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R249: Tests for CsvDocument.GetColumnEntropy, GetColumnInformationContent, GetColumnMutualInformation deeper.
/// GetColumnEntropy(columnName): returns the Shannon entropy of the column value distribution (bits).
/// GetColumnInformationContent(columnName): returns the information content for the mode value.
/// GetColumnMutualInformation(column1, column2): returns mutual information between two columns.
/// Covers: GetColumnEntropy no-throw; GetColumnEntropy non-negative; GetColumnEntropy consistent;
/// GetColumnEntropy zero for constant column;
/// GetColumnInformationContent no-throw; GetColumnInformationContent non-negative; GetColumnInformationContent consistent;
/// GetColumnMutualInformation no-throw; GetColumnMutualInformation non-negative; GetColumnMutualInformation consistent;
/// GetColumnMutualInformation save-load;
/// dogfood CreateDoc→GetColumnEntropy→GetColumnInformationContent→GetColumnMutualInformation pipeline.
/// </summary>
public class CsvR249GetColumnEntropyAndInformationContentDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR249GetColumnEntropyAndInformationContentDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR249_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCreditCsv()
    {
        var path = TempFile("credit.csv");
        var lines = new System.Collections.Generic.List<string>
        {
            "application_id,employment_status,loan_purpose,credit_grade,default_flag",
            "A001,Employed,Home_Improvement,A,0",
            "A002,Self_Employed,Debt_Consolidation,B,0",
            "A003,Employed,Car_Purchase,A,0",
            "A004,Unemployed,Debt_Consolidation,D,1",
            "A005,Employed,Home_Improvement,B,0",
            "A006,Self_Employed,Business,C,0",
            "A007,Employed,Debt_Consolidation,A,0",
            "A008,Retired,Home_Improvement,B,0",
            "A009,Unemployed,Debt_Consolidation,D,1",
            "A010,Employed,Car_Purchase,A,0",
            "A011,Self_Employed,Business,C,1",
            "A012,Employed,Home_Improvement,B,0",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateConstantCsv()
    {
        var path = TempFile("constant.csv");
        var lines = new string[]
        {
            "id,value,status",
            "1,50,Active",
            "2,50,Active",
            "3,50,Active",
            "4,50,Active",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnEntropy_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateCreditCsv());
        var ex = Record.Exception(() => doc.GetColumnEntropy("employment_status"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropy_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateCreditCsv());
        Assert.True(doc.GetColumnEntropy("employment_status") >= 0);
    }

    [Fact]
    public void GetColumnEntropy_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCreditCsv());
        Assert.Equal(doc.GetColumnEntropy("loan_purpose"), doc.GetColumnEntropy("loan_purpose"));
    }

    [Fact]
    public void GetColumnEntropy_Zero_For_Constant()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0.0, doc.GetColumnEntropy("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnInformationContent
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnInformationContent_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateCreditCsv());
        var ex = Record.Exception(() => doc.GetColumnInformationContent("credit_grade"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnInformationContent_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateCreditCsv());
        Assert.True(doc.GetColumnInformationContent("credit_grade") >= 0);
    }

    [Fact]
    public void GetColumnInformationContent_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCreditCsv());
        Assert.Equal(
            doc.GetColumnInformationContent("employment_status"),
            doc.GetColumnInformationContent("employment_status"));
    }

    // -------------------------------------------------------------------------
    // GetColumnMutualInformation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMutualInformation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateCreditCsv());
        var ex = Record.Exception(() => doc.GetColumnMutualInformation("credit_grade", "default_flag"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMutualInformation_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateCreditCsv());
        Assert.True(doc.GetColumnMutualInformation("credit_grade", "default_flag") >= 0);
    }

    [Fact]
    public void GetColumnMutualInformation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCreditCsv());
        Assert.Equal(
            doc.GetColumnMutualInformation("employment_status", "default_flag"),
            doc.GetColumnMutualInformation("employment_status", "default_flag"));
    }

    [Fact]
    public void GetColumnMutualInformation_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateCreditCsv());
        var before = doc.GetColumnMutualInformation("credit_grade", "default_flag");
        var path = TempFile("mi_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMutualInformation("credit_grade", "default_flag"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropy_GetColumnInformationContent_GetColumnMutualInformation_Pipeline()
    {
        // E-commerce — product recommendation feature engineering for collaborative filtering
        var path = TempFile("recommendation_features.csv");
        var csvLines = new System.Collections.Generic.List<string>();
        csvLines.Add("session_id,device_type,traffic_source,category_viewed,price_band,purchase_flag");
        var rng = new Random(20250601);
        string[] devices = { "Mobile", "Desktop", "Tablet" };
        string[] sources = { "Organic", "Paid_Search", "Social", "Email", "Direct" };
        string[] categories = { "Electronics", "Clothing", "Books", "Home_Garden", "Sports", "Beauty" };
        string[] priceBands = { "Under_20", "20_50", "50_100", "100_250", "Over_250" };
        for (int i = 0; i < 150; i++)
        {
            string device = devices[i % 3];
            string source = sources[rng.Next(5)];
            string category = categories[rng.Next(6)];
            string priceBand = priceBands[rng.Next(5)];
            // Purchase correlated with price band and source
            int purchase = (source == "Email" && priceBand == "20_50") ? (rng.NextDouble() < 0.5 ? 1 : 0) :
                           (source == "Paid_Search") ? (rng.NextDouble() < 0.3 ? 1 : 0) :
                           (rng.NextDouble() < 0.1 ? 1 : 0);
            csvLines.Add($"SES{i:D6},{device},{source},{category},{priceBand},{purchase}");
        }
        File.WriteAllLines(path, csvLines);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);

        // GetColumnEntropy — device_type (3 categories)
        var deviceEntropy = doc.GetColumnEntropy("device_type");
        Assert.True(deviceEntropy >= 0 && deviceEntropy <= 2.0); // max for 3 categories ≈ 1.58 bits
        Assert.Equal(deviceEntropy, doc.GetColumnEntropy("device_type")); // consistent

        // GetColumnEntropy — category (6 categories, higher entropy)
        var catEntropy = doc.GetColumnEntropy("category_viewed");
        Assert.True(catEntropy >= 0);

        // GetColumnEntropy — purchase_flag (binary, ≤ 1 bit)
        var purchEntropy = doc.GetColumnEntropy("purchase_flag");
        Assert.True(purchEntropy >= 0 && purchEntropy <= 1.1);

        // GetColumnInformationContent
        var deviceIC = doc.GetColumnInformationContent("device_type");
        Assert.True(deviceIC >= 0);
        Assert.Equal(deviceIC, doc.GetColumnInformationContent("device_type")); // consistent

        var sourceIC = doc.GetColumnInformationContent("traffic_source");
        Assert.True(sourceIC >= 0);

        // GetColumnMutualInformation — source vs purchase (high predictive value)
        var sourcePurchMI = doc.GetColumnMutualInformation("traffic_source", "purchase_flag");
        Assert.True(sourcePurchMI >= 0);
        Assert.Equal(sourcePurchMI, doc.GetColumnMutualInformation("traffic_source", "purchase_flag")); // consistent

        // GetColumnMutualInformation — category vs price_band
        var catPriceMI = doc.GetColumnMutualInformation("category_viewed", "price_band");
        Assert.True(catPriceMI >= 0);

        // All entropy values non-negative
        foreach (var col in new[] { "device_type", "traffic_source", "category_viewed", "price_band" })
        {
            Assert.True(doc.GetColumnEntropy(col) >= 0);
            Assert.True(doc.GetColumnInformationContent(col) >= 0);
        }

        // SaveToFile
        var outPath = TempFile("recommendation_features_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(deviceEntropy, loaded.GetColumnEntropy("device_type"), precision: 6);
        Assert.Equal(sourcePurchMI, loaded.GetColumnMutualInformation("traffic_source", "purchase_flag"), precision: 6);
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // Additional stats
        var modeDevice = doc.GetColumnMode("device_type");
        Assert.NotNull(modeDevice);
        var uniqueCats = doc.GetColumnUniqueCount("category_viewed");
        Assert.True(uniqueCats > 0 && uniqueCats <= 6);
    }
}
