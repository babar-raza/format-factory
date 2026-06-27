// Tests for CsvDocument.GetColumnMissingRate, GetColumnFillRate deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R268

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R268: Tests for CsvDocument.GetColumnMissingRate, GetColumnFillRate deeper.
/// GetColumnMissingRate(colName): returns the fraction of rows with missing (null/empty) values.
/// GetColumnFillRate(colName): returns the fraction of rows with non-missing values (1 - missing rate).
/// Covers: GetColumnMissingRate no-throw; GetColumnMissingRate in-range;
/// GetColumnMissingRate consistent; GetColumnMissingRate zero for fully-populated;
/// GetColumnMissingRate save-load; GetColumnFillRate no-throw; GetColumnFillRate in-range;
/// GetColumnFillRate consistent; GetColumnFillRate one for fully-populated;
/// GetColumnFillRate save-load; MissingRate + FillRate = 1;
/// dogfood CreateDoc→GetColumnMissingRate→GetColumnFillRate→SaveToFile pipeline.
/// </summary>
public class CsvR268GetColumnMissingRateAndFillRateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR268GetColumnMissingRateAndFillRateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR268_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateFullyPopulatedCsv()
    {
        var path = TempFile("full.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,name,value");
        for (int i = 0; i < 50; i++)
            sb.AppendLine($"{i},Item_{i},{i * 10}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateWithMissingCsv()
    {
        // 10 rows: value missing for rows 1, 4, 8 (30% missing)
        var path = TempFile("missing.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,name,value");
        for (int i = 0; i < 10; i++)
        {
            bool missing = i == 1 || i == 4 || i == 8;
            sb.AppendLine($"{i},Item_{i},{(missing ? "" : (i * 10).ToString())}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMissingRate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMissingRate_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateWithMissingCsv());
        var ex = Record.Exception(() => doc.GetColumnMissingRate("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMissingRate_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateWithMissingCsv());
        var mr = doc.GetColumnMissingRate("value");
        Assert.True(mr >= 0.0 && mr <= 1.0);
    }

    [Fact]
    public void GetColumnMissingRate_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateWithMissingCsv());
        Assert.Equal(doc.GetColumnMissingRate("value"), doc.GetColumnMissingRate("value"));
    }

    [Fact]
    public void GetColumnMissingRate_Zero_ForFullyPopulated()
    {
        var doc = CsvDocument.LoadFile(CreateFullyPopulatedCsv());
        Assert.Equal(0.0, doc.GetColumnMissingRate("value"), precision: 6);
    }

    [Fact]
    public void GetColumnMissingRate_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateWithMissingCsv());
        var before = doc.GetColumnMissingRate("value");
        var path = TempFile("mr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMissingRate("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnFillRate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnFillRate_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateFullyPopulatedCsv());
        var ex = Record.Exception(() => doc.GetColumnFillRate("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnFillRate_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateWithMissingCsv());
        var fr = doc.GetColumnFillRate("value");
        Assert.True(fr >= 0.0 && fr <= 1.0);
    }

    [Fact]
    public void GetColumnFillRate_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateWithMissingCsv());
        Assert.Equal(doc.GetColumnFillRate("value"), doc.GetColumnFillRate("value"));
    }

    [Fact]
    public void GetColumnFillRate_One_ForFullyPopulated()
    {
        var doc = CsvDocument.LoadFile(CreateFullyPopulatedCsv());
        Assert.Equal(1.0, doc.GetColumnFillRate("value"), precision: 6);
    }

    [Fact]
    public void GetColumnFillRate_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateWithMissingCsv());
        var before = doc.GetColumnFillRate("value");
        var path = TempFile("fr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnFillRate("value"), precision: 6);
    }

    [Fact]
    public void MissingRate_Plus_FillRate_Equals_One()
    {
        var doc = CsvDocument.LoadFile(CreateWithMissingCsv());
        var mr = doc.GetColumnMissingRate("value");
        var fr = doc.GetColumnFillRate("value");
        Assert.Equal(1.0, mr + fr, precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMissingRate_GetColumnFillRate_Pipeline()
    {
        // Healthcare — NHS Digital: Hospital Episode Statistics (HES) 2024-25
        // Admitted Patient Care (APC) dataset — data completeness audit
        // Missing rate thresholds per NHS Digital Data Quality Framework (DQF)

        var path = TempFile("hes_apc_audit.csv");
        var sb = new StringBuilder();
        sb.AppendLine("episode_id,provider_code,specialty_code,diagnosis_primary,procedure_primary,admission_method,age_on_admission,sex,ethnic_category,imd_decile,length_of_stay_days,hrg_code");

        var rng = new Random(20241201);
        string[] providers = { "RJC", "RJE", "RKB", "RKE", "RKL", "RKM", "RLN", "RM2", "RM3", "RN5",
                                "RNJ", "RNQ", "RNS", "RNZ", "RP4", "RPY", "RQ3", "RQ8", "RQM", "RQN" };
        string[] specialties = { "100", "101", "110", "120", "130", "140", "150", "160", "170", "180",
                                  "190", "191", "192", "211", "212", "213", "220", "300", "301", "320" };
        string[] admMethods = { "11", "12", "13", "21", "22", "23", "24", "25", "28", "2A", "2B", "2C", "2D", "31", "32" };
        string[] sexCodes = { "1", "2", "9" };
        string[] ethnicCats = { "A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "R", "S", "Z" };

        for (int i = 0; i < 400; i++)
        {
            string episodeId = $"HES{i:D9}";
            string provider = providers[rng.Next(providers.Length)];
            string specialty = specialties[rng.Next(specialties.Length)];

            // Primary diagnosis: 0.5% missing (very high quality field per DQF)
            string diagnosis = rng.NextDouble() < 0.005 ? "" : $"I{rng.Next(10, 99):D2}.{rng.Next(9)}";

            // Primary procedure: 15% missing (elective non-procedure admissions)
            string procedure = rng.NextDouble() < 0.15 ? "" : $"K{rng.Next(10, 99):D2}.{rng.Next(9)}";

            // Admission method: 1% missing
            string admMethod = rng.NextDouble() < 0.01 ? "" : admMethods[rng.Next(admMethods.Length)];

            // Age: 0.2% missing
            string age = rng.NextDouble() < 0.002 ? "" : rng.Next(0, 100).ToString();

            // Sex: 0.5% missing (non-binary coding added 2020)
            string sex = rng.NextDouble() < 0.005 ? "" : sexCodes[rng.Next(sexCodes.Length)];

            // Ethnic category: 6% missing (patient refusal / not recorded)
            string ethnic = rng.NextDouble() < 0.06 ? "" : ethnicCats[rng.Next(ethnicCats.Length)];

            // IMD decile: 4% missing (address matching failure)
            string imd = rng.NextDouble() < 0.04 ? "" : rng.Next(1, 11).ToString();

            // Length of stay: 0.1% missing
            string los = rng.NextDouble() < 0.001 ? "" : rng.Next(0, 30).ToString();

            // HRG code: 2% missing (grouper failure)
            string hrg = rng.NextDouble() < 0.02 ? "" : $"AA{rng.Next(10, 99):D2}Z";

            sb.AppendLine($"{episodeId},{provider},{specialty},{diagnosis},{procedure},{admMethod},{age},{sex},{ethnic},{imd},{los},{hrg}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(400, doc.RowCount);
        Assert.Equal(12, doc.ColumnCount);

        // Primary diagnosis — very low missing rate (<1%)
        var mrDiag = doc.GetColumnMissingRate("diagnosis_primary");
        var frDiag = doc.GetColumnFillRate("diagnosis_primary");
        Assert.True(mrDiag >= 0.0 && mrDiag <= 1.0);
        Assert.Equal(1.0, mrDiag + frDiag, precision: 6);
        Assert.Equal(mrDiag, doc.GetColumnMissingRate("diagnosis_primary")); // consistent
        Assert.True(frDiag >= 0.99); // DQF standard: >99% fill rate expected

        // Primary procedure — ~15% missing
        var mrProc = doc.GetColumnMissingRate("procedure_primary");
        var frProc = doc.GetColumnFillRate("procedure_primary");
        Assert.True(mrProc >= 0.0 && mrProc <= 1.0);
        Assert.Equal(1.0, mrProc + frProc, precision: 6);
        Assert.True(mrProc > mrDiag); // procedures more often absent than diagnoses

        // Ethnic category — ~6% missing
        var mrEthnic = doc.GetColumnMissingRate("ethnic_category");
        var frEthnic = doc.GetColumnFillRate("ethnic_category");
        Assert.True(mrEthnic >= 0.0 && mrEthnic <= 1.0);
        Assert.Equal(1.0, mrEthnic + frEthnic, precision: 6);

        // IMD decile — ~4% missing
        var mrImd = doc.GetColumnMissingRate("imd_decile");
        var frImd = doc.GetColumnFillRate("imd_decile");
        Assert.True(mrImd >= 0.0 && mrImd <= 1.0);
        Assert.Equal(1.0, mrImd + frImd, precision: 6);

        // Provider code — always populated (system-generated)
        var mrProvider = doc.GetColumnMissingRate("provider_code");
        Assert.Equal(0.0, mrProvider, precision: 6);
        Assert.Equal(1.0, doc.GetColumnFillRate("provider_code"), precision: 6);

        // SaveToFile
        var outPath = TempFile("hes_apc_audit_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(mrDiag, loaded.GetColumnMissingRate("diagnosis_primary"), precision: 6);
        Assert.Equal(frDiag, loaded.GetColumnFillRate("diagnosis_primary"), precision: 6);
        Assert.Equal(mrProc, loaded.GetColumnMissingRate("procedure_primary"), precision: 6);
        Assert.Equal(frProc, loaded.GetColumnFillRate("procedure_primary"), precision: 6);
        Assert.Equal(mrEthnic, loaded.GetColumnMissingRate("ethnic_category"), precision: 6);
        Assert.Equal(frEthnic, loaded.GetColumnFillRate("ethnic_category"), precision: 6);

        // MissingRate + FillRate = 1 for all key columns
        Assert.Equal(1.0, loaded.GetColumnMissingRate("imd_decile") + loaded.GetColumnFillRate("imd_decile"), precision: 6);
        Assert.Equal(1.0, loaded.GetColumnMissingRate("hrg_code") + loaded.GetColumnFillRate("hrg_code"), precision: 6);
    }
}
