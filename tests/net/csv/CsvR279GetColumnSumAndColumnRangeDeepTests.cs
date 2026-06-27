// Tests for CsvDocument.GetColumnSum, GetColumnRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R279

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R279: Tests for CsvDocument.GetColumnSum, GetColumnRange deeper.
/// GetColumnSum(colName): returns the sum of all numeric values in the column.
/// GetColumnRange(colName): returns the range (max - min) of numeric values in the column.
/// Covers: GetColumnSum no-throw; GetColumnSum correct for known data;
/// GetColumnSum consistent; GetColumnSum save-load;
/// GetColumnRange no-throw; GetColumnRange correct for known data;
/// GetColumnRange non-negative; GetColumnRange 0 for uniform;
/// GetColumnRange consistent; GetColumnRange save-load; dogfood pipeline.
/// </summary>
public class CsvR279GetColumnSumAndColumnRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR279GetColumnSumAndColumnRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR279_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id,amount,quantity");
        // sum of amount = 10+20+30+40+50 = 150; range = 50-10 = 40
        double[] amounts = { 10.0, 20.0, 30.0, 40.0, 50.0 };
        for (int i = 0; i < amounts.Length; i++)
            sb.AppendLine($"{i},{amounts[i]:F1},{i + 1}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,value");
        for (int i = 0; i < 8; i++)
            sb.AppendLine($"{i},25.0");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnSum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnSum_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnSum("amount"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnSum_Correct_ForKnownData()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(150.0, doc.GetColumnSum("amount"), precision: 5);
    }

    [Fact]
    public void GetColumnSum_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnSum("amount"), doc.GetColumnSum("amount"));
    }

    [Fact]
    public void GetColumnSum_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnSum("amount");
        var path = TempFile("sum_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnSum("amount"), precision: 5);
    }

    // -------------------------------------------------------------------------
    // GetColumnRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRange_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnRange("amount"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRange_Correct_ForKnownData()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(40.0, doc.GetColumnRange("amount"), precision: 5);
    }

    [Fact]
    public void GetColumnRange_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnRange("amount") >= 0);
    }

    [Fact]
    public void GetColumnRange_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, doc.GetColumnRange("value"), precision: 5);
    }

    [Fact]
    public void GetColumnRange_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnRange("amount"), doc.GetColumnRange("amount"));
    }

    [Fact]
    public void GetColumnRange_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnRange("amount");
        var path = TempFile("range_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnRange("amount"), precision: 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnSum_GetColumnRange_Pipeline()
    {
        // Health — NHS England / NHSBSA: Prescription Cost Analysis England 2024
        // GP practice-level prescription data: item counts, net ingredient cost, quantity dispensed
        // Sum = total national drug spend; range identifies cost outliers for prescribing efficiency audit

        var path = TempFile("nhsbsa_prescription_cost_2024.csv");
        var sb = new StringBuilder();
        sb.AppendLine("ods_code,practice_name,icb_code,icb_name,bnf_chapter,drug_name,items_prescribed,nic_gbp,quantity_dispensed_units,avg_cost_per_item_gbp");

        var rng = new Random(20240401);
        string[] odsCodes = {
            "A81001", "A81002", "A81003", "A81004", "A81005",
            "B82001", "B82002", "B82003", "B82004", "B82005",
            "C83001", "C83002", "C83003", "C83004", "C83005",
            "D84001", "D84002", "D84003", "D84004", "D84005",
            "E85001", "E85002", "E85003", "E85004", "E85005"
        };
        string[] practiceNames = {
            "Ancoats_Medical_Practice", "Ardwick_Group_Practice", "Chorlton_Health_Centre",
            "Didsbury_Medical_Group", "East_Manchester_PCN", "Bradford_City_Medical",
            "Calverley_Surgery", "Dewsbury_Health_Centre", "Elland_Medical_Group", "Farsley_Medical",
            "Coventry_City_Practice", "Daventry_Group", "Earlsdon_Health_Centre",
            "Foleshill_Medical", "Gosford_Park_Practice", "Durham_City_GP", "Easington_Health",
            "Framwellgate_Moor", "Gilesgate_Surgery", "Houghton_Le_Spring_Medical",
            "Ipswich_Road_Surgery", "Kirkley_Mill_Health", "Lowestoft_Medical", "Martlesham_GP",
            "Needham_Market_Practice"
        };
        string[] icbCodes = {
            "QOP", "QOP", "QOP", "QOP", "QOP",
            "QWO", "QWO", "QWO", "QWO", "QWO",
            "QHL", "QHL", "QHL", "QHL", "QHL",
            "QHM", "QHM", "QHM", "QHM", "QHM",
            "QMM", "QMM", "QMM", "QMM", "QMM"
        };
        string[] icbNames = {
            "NHS_Greater_Manchester_ICB", "NHS_Greater_Manchester_ICB", "NHS_Greater_Manchester_ICB", "NHS_Greater_Manchester_ICB", "NHS_Greater_Manchester_ICB",
            "NHS_West_Yorkshire_ICB", "NHS_West_Yorkshire_ICB", "NHS_West_Yorkshire_ICB", "NHS_West_Yorkshire_ICB", "NHS_West_Yorkshire_ICB",
            "NHS_Coventry_and_Warwickshire_ICB", "NHS_Coventry_and_Warwickshire_ICB", "NHS_Coventry_and_Warwickshire_ICB", "NHS_Coventry_and_Warwickshire_ICB", "NHS_Coventry_and_Warwickshire_ICB",
            "NHS_County_Durham_ICB", "NHS_County_Durham_ICB", "NHS_County_Durham_ICB", "NHS_County_Durham_ICB", "NHS_County_Durham_ICB",
            "NHS_Suffolk_and_North_East_Essex_ICB", "NHS_Suffolk_and_North_East_Essex_ICB", "NHS_Suffolk_and_North_East_Essex_ICB", "NHS_Suffolk_and_North_East_Essex_ICB", "NHS_Suffolk_and_North_East_Essex_ICB"
        };
        string[] bnfChapters = { "02_Cardiovascular", "04_CNS", "06_Endocrine", "10_MSK", "01_GI" };
        string[] drugNames = {
            "Atorvastatin_20mg_tablets", "Amlodipine_5mg_tablets", "Ramipril_5mg_capsules",
            "Sertraline_50mg_tablets", "Metformin_500mg_tablets", "Levothyroxine_50mcg_tablets",
            "Naproxen_500mg_tablets", "Omeprazole_20mg_capsules", "Salbutamol_100mcg_inhaler",
            "Co-amoxiclav_500/125mg_tablets", "Lisinopril_10mg_tablets", "Bisoprolol_5mg_tablets",
            "Paracetamol_500mg_tablets", "Amoxicillin_500mg_capsules", "Doxycycline_100mg_capsules",
            "Citalopram_20mg_tablets", "Gabapentin_300mg_capsules", "Pregabalin_75mg_capsules",
            "Warfarin_5mg_tablets", "Furosemide_40mg_tablets", "Azithromycin_250mg_capsules",
            "Flucloxacillin_500mg_capsules", "Trimethoprim_200mg_tablets", "Nitrofurantoin_100mg_MR",
            "Cetirizine_10mg_tablets"
        };

        for (int i = 0; i < odsCodes.Length; i++)
        {
            string bnfCh = bnfChapters[i % bnfChapters.Length];
            string drug = drugNames[i % drugNames.Length];
            int items = 800 + rng.Next(9200); // 800–10000 items
            double nic = items * (0.80 + rng.NextDouble() * 4.20); // £0.80–£5.00 per item
            int qty = items * (28 + rng.Next(57)); // 28–84 units per item
            double avgCost = nic / items;
            sb.AppendLine($"{odsCodes[i]},{practiceNames[i]},{icbCodes[i]},{icbNames[i]},{bnfCh},{drug},{items},{nic:F2},{qty},{avgCost:F4}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(25, doc.RowCount);

        // Items prescribed sum (total national prescriptions subset)
        var totalItems = doc.GetColumnSum("items_prescribed");
        Assert.True(totalItems > 0);
        Assert.Equal(totalItems, doc.GetColumnSum("items_prescribed"), precision: 3); // consistent

        // NIC sum (net ingredient cost — total drug spend)
        var totalNic = doc.GetColumnSum("nic_gbp");
        Assert.True(totalNic > 0);
        Assert.Equal(totalNic, doc.GetColumnSum("nic_gbp"), precision: 3); // consistent

        // Items range
        var itemsRange = doc.GetColumnRange("items_prescribed");
        Assert.True(itemsRange >= 0);
        Assert.Equal(itemsRange, doc.GetColumnRange("items_prescribed"), precision: 3); // consistent

        // NIC range (cost spread between highest and lowest prescribing practices)
        var nicRange = doc.GetColumnRange("nic_gbp");
        Assert.True(nicRange >= 0);
        Assert.Equal(nicRange, doc.GetColumnRange("nic_gbp"), precision: 3); // consistent

        // Avg cost range
        var avgCostRange = doc.GetColumnRange("avg_cost_per_item_gbp");
        Assert.True(avgCostRange >= 0);

        // Quantity dispensed sum
        var totalQty = doc.GetColumnSum("quantity_dispensed_units");
        Assert.True(totalQty > 0);

        // SaveToFile
        var outPath = TempFile("nhsbsa_prescription_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(totalItems, loaded.GetColumnSum("items_prescribed"), precision: 3);
        Assert.Equal(totalNic, loaded.GetColumnSum("nic_gbp"), precision: 3);
        Assert.Equal(itemsRange, loaded.GetColumnRange("items_prescribed"), precision: 3);
        Assert.Equal(nicRange, loaded.GetColumnRange("nic_gbp"), precision: 3);

        var ex1 = Record.Exception(() => loaded.GetColumnSum("nic_gbp"));
        var ex2 = Record.Exception(() => loaded.GetColumnRange("items_prescribed"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
