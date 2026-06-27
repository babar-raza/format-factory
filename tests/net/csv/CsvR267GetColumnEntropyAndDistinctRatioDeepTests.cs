// Tests for CsvDocument.GetColumnEntropy, GetColumnDistinctRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R267

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R267: Tests for CsvDocument.GetColumnEntropy, GetColumnDistinctRatio deeper.
/// GetColumnEntropy(colName): returns Shannon entropy of the value distribution in the column (bits).
/// GetColumnDistinctRatio(colName): returns (distinct count / total row count) as a fraction 0..1.
/// Covers: GetColumnEntropy no-throw; GetColumnEntropy non-negative; GetColumnEntropy consistent;
/// GetColumnEntropy zero for constant; GetColumnEntropy save-load;
/// GetColumnDistinctRatio no-throw; GetColumnDistinctRatio in-range;
/// GetColumnDistinctRatio one for all-unique; GetColumnDistinctRatio near-zero for constant;
/// GetColumnDistinctRatio consistent; GetColumnDistinctRatio save-load;
/// dogfood CreateDoc→GetColumnEntropy→GetColumnDistinctRatio→SaveToFile pipeline.
/// </summary>
public class CsvR267GetColumnEntropyAndDistinctRatioDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR267GetColumnEntropyAndDistinctRatioDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR267_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleCsv()
    {
        var path = TempFile("sample.csv");
        var sb = new StringBuilder();
        sb.AppendLine("claim_id,insurer_code,product_type,claim_status,settlement_band,fraud_flag");
        string[] insurers = { "AXA", "Aviva", "RSA", "Zurich", "Allianz", "Admiral", "Direct Line", "LV=" };
        string[] products = { "Motor", "Home", "Travel", "Commercial", "Life", "Health" };
        string[] statuses = { "Open", "Closed", "Pending", "Rejected" };
        string[] bands = { "0-1k", "1k-5k", "5k-25k", "25k-100k", "100k+" };
        var rng = new Random(20240901);
        for (int i = 0; i < 200; i++)
        {
            bool fraud = rng.NextDouble() < 0.05; // 5% fraud rate
            sb.AppendLine($"CLM{i:D6},{insurers[rng.Next(insurers.Length)]},{products[rng.Next(products.Length)]},{statuses[rng.Next(statuses.Length)]},{bands[rng.Next(bands.Length)]},{(fraud ? "Y" : "N")}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantCsv()
    {
        var path = TempFile("constant.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,country");
        for (int i = 0; i < 60; i++)
            sb.AppendLine($"{i},UK");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniqueCsv()
    {
        var path = TempFile("unique.csv");
        var sb = new StringBuilder();
        sb.AppendLine("policy_id,premium");
        for (int i = 0; i < 60; i++)
            sb.AppendLine($"POL{i:D6},{i * 50 + 100}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnEntropy_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnEntropy("product_type"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropy_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnEntropy("product_type") >= 0.0);
    }

    [Fact]
    public void GetColumnEntropy_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnEntropy("product_type"), doc.GetColumnEntropy("product_type"));
    }

    [Fact]
    public void GetColumnEntropy_Zero_ForConstant()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0.0, doc.GetColumnEntropy("country"), precision: 8);
    }

    [Fact]
    public void GetColumnEntropy_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnEntropy("claim_status");
        var path = TempFile("ent_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnEntropy("claim_status"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnDistinctRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnDistinctRatio_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnDistinctRatio("product_type"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnDistinctRatio_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var dr = doc.GetColumnDistinctRatio("product_type");
        Assert.True(dr >= 0.0 && dr <= 1.0);
    }

    [Fact]
    public void GetColumnDistinctRatio_One_ForAllUnique()
    {
        var doc = CsvDocument.LoadFile(CreateUniqueCsv());
        Assert.Equal(1.0, doc.GetColumnDistinctRatio("policy_id"), precision: 6);
    }

    [Fact]
    public void GetColumnDistinctRatio_NearZero_ForConstant()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        var dr = doc.GetColumnDistinctRatio("country");
        Assert.True(dr <= 0.05); // 1 distinct / 60 rows
    }

    [Fact]
    public void GetColumnDistinctRatio_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnDistinctRatio("claim_status"), doc.GetColumnDistinctRatio("claim_status"));
    }

    [Fact]
    public void GetColumnDistinctRatio_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnDistinctRatio("insurer_code");
        var path = TempFile("dr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnDistinctRatio("insurer_code"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropy_GetColumnDistinctRatio_Pipeline()
    {
        // Finance — Association of British Insurers (ABI): Motor Claims Data 2024
        // Bodily injury and property damage claims across UK motor insurers
        // Entropy and distinct-ratio analysis for fraud detection and data quality assurance

        var path = TempFile("abi_motor_claims.csv");
        var sb = new StringBuilder();
        sb.AppendLine("claim_ref,insurer_group,accident_type,fault_indicator,injury_severity,settlement_type,claimant_age_band,amount_gbp,weeks_to_settle,fraud_indicator");

        var rng = new Random(20241015);
        string[] insurers = { "Aviva", "AXA", "RSA", "Direct Line", "Admiral", "Ageas", "Zurich", "NFU Mutual", "Liverpool Victoria", "Saga" };
        // Accident type distribution: rear-end very common, angle less so
        string[] accTypes = { "Rear-end", "Rear-end", "Rear-end", "Angle", "Angle", "Side-swipe", "Head-on", "Single-vehicle", "Pedestrian", "Cyclist" };
        string[] faults = { "TP_Fault", "TP_Fault", "TP_Fault", "Split", "Own_Fault" }; // TP fault most common
        string[] injuries = { "Whiplash", "Whiplash", "Whiplash", "Whiplash", "Soft-tissue", "Fracture", "Head", "None", "None", "None" };
        string[] settles = { "Direct", "Direct", "Solicitor", "Solicitor", "CMC", "Litigation" };
        string[] ages = { "17-24", "25-34", "35-44", "45-54", "55-64", "65+" };

        for (int i = 0; i < 300; i++)
        {
            string ins = insurers[rng.Next(insurers.Length)];
            string acc = accTypes[rng.Next(accTypes.Length)];
            string fault = faults[rng.Next(faults.Length)];
            string inj = injuries[rng.Next(injuries.Length)];
            string settle = settles[rng.Next(settles.Length)];
            string age = ages[rng.Next(ages.Length)];
            int amount = inj == "None" ? rng.Next(500, 3000) :
                         inj == "Whiplash" ? rng.Next(1500, 12000) :
                         inj == "Fracture" ? rng.Next(8000, 50000) :
                         rng.Next(20000, 200000);
            int weeks = settle == "Direct" ? rng.Next(4, 26) :
                        settle == "Solicitor" ? rng.Next(26, 78) :
                        rng.Next(52, 156);
            bool fraud = rng.NextDouble() < 0.03;
            sb.AppendLine($"MOT{i:D7},{ins},{acc},{fault},{inj},{settle},{age},{amount},{weeks},{(fraud ? "Y" : "N")}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(300, doc.RowCount);
        Assert.Equal(10, doc.ColumnCount);

        // Entropy of accident_type — rear-end dominates → lower entropy
        var entAcc = doc.GetColumnEntropy("accident_type");
        Assert.True(entAcc >= 0.0);
        Assert.Equal(entAcc, doc.GetColumnEntropy("accident_type")); // consistent

        // Entropy of insurer_group — more uniform → higher entropy
        var entIns = doc.GetColumnEntropy("insurer_group");
        Assert.True(entIns >= 0.0);
        Assert.True(entIns > entAcc); // 10 insurers roughly uniform vs skewed accident types

        // Entropy of fraud_indicator — very skewed (3% fraud) → very low entropy
        var entFraud = doc.GetColumnEntropy("fraud_indicator");
        Assert.True(entFraud >= 0.0);
        Assert.True(entFraud < entAcc); // fraud rarer than accident type variety

        // Entropy of amount_gbp — continuous-like → high entropy
        var entAmt = doc.GetColumnEntropy("amount_gbp");
        Assert.True(entAmt >= 0.0);

        // DistinctRatio of claim_ref — all unique → 1.0
        var drRef = doc.GetColumnDistinctRatio("claim_ref");
        Assert.Equal(1.0, drRef, precision: 6);

        // DistinctRatio of insurer_group — 10 insurers / 300 rows ≈ 0.033
        var drIns = doc.GetColumnDistinctRatio("insurer_group");
        Assert.True(drIns >= 0.0 && drIns <= 1.0);
        Assert.True(drIns < 0.1);

        // DistinctRatio of fraud_indicator — 2 values (Y/N) → very low
        var drFraud = doc.GetColumnDistinctRatio("fraud_indicator");
        Assert.True(drFraud >= 0.0 && drFraud <= 1.0);
        Assert.True(drFraud <= 0.02); // 2 / 300

        // DistinctRatio of claimant_age_band — 6 bands → still low
        var drAge = doc.GetColumnDistinctRatio("claimant_age_band");
        Assert.True(drAge >= 0.0 && drAge <= 1.0);

        // Basic stats
        Assert.True(doc.GetColumnMean("amount_gbp") > 0);
        Assert.True(doc.GetColumnMean("weeks_to_settle") > 0);

        // Constant-column sanity check
        var pathConst = TempFile("const.csv");
        var sbConst = new StringBuilder();
        sbConst.AppendLine("id,country");
        for (int i = 0; i < 100; i++) sbConst.AppendLine($"{i},United Kingdom");
        File.WriteAllText(pathConst, sbConst.ToString());
        var docConst = CsvDocument.LoadFile(pathConst);
        Assert.Equal(0.0, docConst.GetColumnEntropy("country"), precision: 8);
        Assert.True(docConst.GetColumnDistinctRatio("country") <= 0.02);

        // SaveToFile
        var outPath = TempFile("abi_motor_claims_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(entAcc, loaded.GetColumnEntropy("accident_type"), precision: 8);
        Assert.Equal(drRef, loaded.GetColumnDistinctRatio("claim_ref"), precision: 8);
        Assert.Equal(entIns, loaded.GetColumnEntropy("insurer_group"), precision: 8);
        Assert.Equal(drIns, loaded.GetColumnDistinctRatio("insurer_group"), precision: 8);
    }
}
