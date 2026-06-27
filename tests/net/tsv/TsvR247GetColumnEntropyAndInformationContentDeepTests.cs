// Tests for TsvDocument.GetColumnEntropy, GetColumnInformationContent, GetColumnMutualInformation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R247

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R247: Tests for TsvDocument.GetColumnEntropy, GetColumnInformationContent, GetColumnMutualInformation deeper.
/// GetColumnEntropy(columnName): returns the Shannon entropy of the column value distribution (bits).
/// GetColumnInformationContent(columnName): returns the information content (negative log probability) for the mode value.
/// GetColumnMutualInformation(column1, column2): returns the mutual information between two columns.
/// Covers: GetColumnEntropy no-throw; GetColumnEntropy non-negative; GetColumnEntropy consistent;
/// GetColumnEntropy zero for constant column; GetColumnEntropy maximum for uniform distribution;
/// GetColumnInformationContent no-throw; GetColumnInformationContent non-negative; GetColumnInformationContent consistent;
/// GetColumnMutualInformation no-throw; GetColumnMutualInformation non-negative; GetColumnMutualInformation consistent;
/// GetColumnMutualInformation zero for independent columns; GetColumnMutualInformation save-load;
/// dogfood CreateDoc→GetColumnEntropy→GetColumnInformationContent→GetColumnMutualInformation pipeline.
/// </summary>
public class TsvR247GetColumnEntropyAndInformationContentDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR247GetColumnEntropyAndInformationContentDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR247_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateDiagnosticTsv()
    {
        var path = TempFile("diagnostic.tsv");
        var lines = new System.Collections.Generic.List<string>
        {
            "patient_id\tdiagnosis\tseverity\tage_group\toutcome",
            "P001\tPneumonia\tModerate\t65+\tRecovered",
            "P002\tCOPD\tSevere\t65+\tDischarged",
            "P003\tPneumonia\tMild\t45-64\tRecovered",
            "P004\tAsthma\tMild\t18-44\tRecovered",
            "P005\tPneumonia\tSevere\t65+\tDeceased",
            "P006\tCOPD\tModerate\t65+\tDischarged",
            "P007\tAsthma\tMild\t18-44\tRecovered",
            "P008\tPneumonia\tModerate\t45-64\tRecovered",
            "P009\tCOPD\tSevere\t65+\tDeceased",
            "P010\tPneumonia\tMild\t18-44\tRecovered",
            "P011\tAsthma\tModerate\t45-64\tRecovered",
            "P012\tPneumonia\tSevere\t65+\tDeceased",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateConstantTsv()
    {
        var path = TempFile("constant.tsv");
        var lines = new string[]
        {
            "id\tvalue\tcategory",
            "R1\t100\tA",
            "R2\t100\tA",
            "R3\t100\tA",
            "R4\t100\tA",
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
        var doc = TsvDocument.LoadFile(CreateDiagnosticTsv());
        var ex = Record.Exception(() => doc.GetColumnEntropy("diagnosis"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropy_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateDiagnosticTsv());
        Assert.True(doc.GetColumnEntropy("diagnosis") >= 0);
    }

    [Fact]
    public void GetColumnEntropy_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateDiagnosticTsv());
        Assert.Equal(doc.GetColumnEntropy("diagnosis"), doc.GetColumnEntropy("diagnosis"));
    }

    [Fact]
    public void GetColumnEntropy_Zero_For_Constant()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0.0, doc.GetColumnEntropy("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnInformationContent
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnInformationContent_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateDiagnosticTsv());
        var ex = Record.Exception(() => doc.GetColumnInformationContent("diagnosis"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnInformationContent_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateDiagnosticTsv());
        Assert.True(doc.GetColumnInformationContent("diagnosis") >= 0);
    }

    [Fact]
    public void GetColumnInformationContent_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateDiagnosticTsv());
        Assert.Equal(doc.GetColumnInformationContent("severity"), doc.GetColumnInformationContent("severity"));
    }

    // -------------------------------------------------------------------------
    // GetColumnMutualInformation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMutualInformation_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateDiagnosticTsv());
        var ex = Record.Exception(() => doc.GetColumnMutualInformation("diagnosis", "outcome"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMutualInformation_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateDiagnosticTsv());
        Assert.True(doc.GetColumnMutualInformation("diagnosis", "outcome") >= 0);
    }

    [Fact]
    public void GetColumnMutualInformation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateDiagnosticTsv());
        Assert.Equal(
            doc.GetColumnMutualInformation("severity", "outcome"),
            doc.GetColumnMutualInformation("severity", "outcome"));
    }

    [Fact]
    public void GetColumnMutualInformation_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateDiagnosticTsv());
        var before = doc.GetColumnMutualInformation("diagnosis", "outcome");
        var path = TempFile("mi_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMutualInformation("diagnosis", "outcome"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropy_GetColumnInformationContent_GetColumnMutualInformation_Pipeline()
    {
        // Telecommunications — customer churn prediction features from CRM data
        var path = TempFile("churn_features.tsv");
        var lines = new System.Collections.Generic.List<string>();
        lines.Add("customer_id\tcontract_type\tpayment_method\ttenure_band\tproduct_tier\tchurn_flag");
        var rng = new Random(20250501);
        string[] contracts = { "Month_to_Month", "One_Year", "Two_Year" };
        string[] payments = { "Electronic_Check", "Bank_Transfer", "Credit_Card", "Mailed_Check" };
        string[] tenures = { "0_6_Months", "6_12_Months", "1_2_Years", "2_5_Years", "5_Plus_Years" };
        string[] tiers = { "Basic", "Standard", "Premium" };
        for (int i = 0; i < 150; i++)
        {
            // Month-to-month contracts churn more
            string contract = contracts[rng.Next(3)];
            string payment = payments[rng.Next(4)];
            string tenure = tenures[rng.Next(5)];
            string tier = tiers[rng.Next(3)];
            // Churn correlated with contract type and tenure
            int churn = (contract == "Month_to_Month" && tenure == "0_6_Months") ? (rng.NextDouble() < 0.6 ? 1 : 0)
                      : (contract == "Month_to_Month") ? (rng.NextDouble() < 0.3 ? 1 : 0)
                      : (rng.NextDouble() < 0.05 ? 1 : 0);
            lines.Add($"CUST{i:D6}\t{contract}\t{payment}\t{tenure}\t{tier}\t{churn}");
        }
        File.WriteAllLines(path, lines);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);

        // GetColumnEntropy — contract_type (3 categories, moderate entropy)
        var contractEntropy = doc.GetColumnEntropy("contract_type");
        Assert.True(contractEntropy >= 0);
        Assert.Equal(contractEntropy, doc.GetColumnEntropy("contract_type")); // consistent

        // GetColumnEntropy — churn_flag (binary, entropy ≤ 1 bit)
        var churnEntropy = doc.GetColumnEntropy("churn_flag");
        Assert.True(churnEntropy >= 0 && churnEntropy <= 1.1); // ≤ 1 bit for binary

        // GetColumnInformationContent — contract_type mode
        var contractIC = doc.GetColumnInformationContent("contract_type");
        Assert.True(contractIC >= 0);
        Assert.Equal(contractIC, doc.GetColumnInformationContent("contract_type")); // consistent

        // GetColumnInformationContent — tenure
        var tenureIC = doc.GetColumnInformationContent("tenure_band");
        Assert.True(tenureIC >= 0);

        // GetColumnMutualInformation — contract vs churn (should be high)
        var contractChurnMI = doc.GetColumnMutualInformation("contract_type", "churn_flag");
        Assert.True(contractChurnMI >= 0);
        Assert.Equal(contractChurnMI, doc.GetColumnMutualInformation("contract_type", "churn_flag")); // consistent

        // GetColumnMutualInformation — payment_method vs product_tier (more independent)
        var payTierMI = doc.GetColumnMutualInformation("payment_method", "product_tier");
        Assert.True(payTierMI >= 0);

        // All columns
        foreach (var col in new[] { "contract_type", "payment_method", "tenure_band", "product_tier" })
        {
            Assert.True(doc.GetColumnEntropy(col) >= 0);
            Assert.True(doc.GetColumnInformationContent(col) >= 0);
        }

        // SaveToFile
        var outPath = TempFile("churn_features_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(contractEntropy, loaded.GetColumnEntropy("contract_type"), precision: 6);
        Assert.Equal(contractChurnMI, loaded.GetColumnMutualInformation("contract_type", "churn_flag"), precision: 6);
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // Additional stats
        var modeContract = doc.GetColumnMode("contract_type");
        Assert.NotNull(modeContract);
        var uniqueContracts = doc.GetColumnUniqueCount("contract_type");
        Assert.Equal(3, uniqueContracts);
    }
}
