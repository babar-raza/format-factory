// Tests for TsvDocument.GetColumnMissingRate, GetColumnFillRate deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R266

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R266: Tests for TsvDocument.GetColumnMissingRate, GetColumnFillRate deeper.
/// GetColumnMissingRate(colName): returns the fraction of rows with missing (null/empty) values in the column.
/// GetColumnFillRate(colName): returns the fraction of rows with non-missing values (1 - missing rate).
/// Covers: GetColumnMissingRate no-throw; GetColumnMissingRate in-range;
/// GetColumnMissingRate consistent; GetColumnMissingRate zero for fully-populated;
/// GetColumnMissingRate save-load; GetColumnFillRate no-throw; GetColumnFillRate in-range;
/// GetColumnFillRate consistent; GetColumnFillRate one for fully-populated;
/// GetColumnFillRate save-load; MissingRate + FillRate = 1;
/// dogfood CreateDoc→GetColumnMissingRate→GetColumnFillRate→SaveToFile pipeline.
/// </summary>
public class TsvR266GetColumnMissingRateAndFillRateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR266GetColumnMissingRateAndFillRateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR266_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateFullyPopulatedTsv()
    {
        var path = TempFile("full.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tname\tscore");
        for (int i = 0; i < 50; i++)
            sb.AppendLine($"{i}\tStudent_{i}\t{60 + i}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateWithMissingTsv()
    {
        // 10 rows: score missing for rows 0, 3, 7 (30% missing)
        var path = TempFile("missing.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tname\tscore");
        for (int i = 0; i < 10; i++)
        {
            bool missing = i == 0 || i == 3 || i == 7;
            sb.AppendLine($"{i}\tStudent_{i}\t{(missing ? "" : (60 + i).ToString())}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateAllMissingTsv()
    {
        var path = TempFile("all_missing.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tscore");
        for (int i = 0; i < 20; i++)
            sb.AppendLine($"{i}\t");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMissingRate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMissingRate_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateWithMissingTsv());
        var ex = Record.Exception(() => doc.GetColumnMissingRate("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMissingRate_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateWithMissingTsv());
        var mr = doc.GetColumnMissingRate("score");
        Assert.True(mr >= 0.0 && mr <= 1.0);
    }

    [Fact]
    public void GetColumnMissingRate_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateWithMissingTsv());
        Assert.Equal(doc.GetColumnMissingRate("score"), doc.GetColumnMissingRate("score"));
    }

    [Fact]
    public void GetColumnMissingRate_Zero_ForFullyPopulated()
    {
        var doc = TsvDocument.LoadFile(CreateFullyPopulatedTsv());
        Assert.Equal(0.0, doc.GetColumnMissingRate("score"), precision: 6);
    }

    [Fact]
    public void GetColumnMissingRate_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateWithMissingTsv());
        var before = doc.GetColumnMissingRate("score");
        var path = TempFile("mr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMissingRate("score"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnFillRate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnFillRate_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateFullyPopulatedTsv());
        var ex = Record.Exception(() => doc.GetColumnFillRate("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnFillRate_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateWithMissingTsv());
        var fr = doc.GetColumnFillRate("score");
        Assert.True(fr >= 0.0 && fr <= 1.0);
    }

    [Fact]
    public void GetColumnFillRate_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateWithMissingTsv());
        Assert.Equal(doc.GetColumnFillRate("score"), doc.GetColumnFillRate("score"));
    }

    [Fact]
    public void GetColumnFillRate_One_ForFullyPopulated()
    {
        var doc = TsvDocument.LoadFile(CreateFullyPopulatedTsv());
        Assert.Equal(1.0, doc.GetColumnFillRate("score"), precision: 6);
    }

    [Fact]
    public void GetColumnFillRate_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateWithMissingTsv());
        var before = doc.GetColumnFillRate("score");
        var path = TempFile("fr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnFillRate("score"), precision: 6);
    }

    [Fact]
    public void MissingRate_Plus_FillRate_Equals_One()
    {
        var doc = TsvDocument.LoadFile(CreateWithMissingTsv());
        var mr = doc.GetColumnMissingRate("score");
        var fr = doc.GetColumnFillRate("score");
        Assert.Equal(1.0, mr + fr, precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMissingRate_GetColumnFillRate_Pipeline()
    {
        // Public Sector — ONS: Annual Survey of Hours and Earnings (ASHE) 2024
        // Employee-level microdata with known data quality issues (missing pay data, sector codes)
        // Missing rate analysis for data quality assurance before ONS publication

        var path = TempFile("ons_ashe_2024.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("employee_ref\temployer_ref\tsoc_code\tregion\tsector\tpay_gross_weekly\thours_worked\tcontract_type\tage_band\tgender");

        var rng = new Random(20241101);
        string[] regions = { "London", "South East", "East of England", "West Midlands", "Yorkshire", "North West", "North East", "Scotland", "Wales", "NI" };
        string[] sectors = { "Private", "Public", "Voluntary" };
        string[] contracts = { "Full-time", "Part-time" };
        string[] ageBands = { "16-24", "25-34", "35-44", "45-54", "55-64", "65+" };
        string[] genders = { "Male", "Female" };

        for (int i = 0; i < 300; i++)
        {
            string empRef = $"EMP{i:D7}";
            string emplRef = $"EMPL{rng.Next(10000):D5}";

            // SOC code: 5% missing (interviewer skip)
            string soc = rng.NextDouble() < 0.05 ? "" : $"{rng.Next(1111, 9999)}";

            // Region: always populated
            string region = regions[rng.Next(regions.Length)];

            // Sector: 3% missing (non-response)
            string sector = rng.NextDouble() < 0.03 ? "" : sectors[rng.Next(sectors.Length)];

            // Gross weekly pay: 8% missing (refusal / nil return)
            string pay = rng.NextDouble() < 0.08 ? "" : $"{200 + rng.Next(1800):F2}";

            // Hours worked: 2% missing
            string hours = rng.NextDouble() < 0.02 ? "" : $"{20 + rng.Next(30)}";

            // Contract type: always populated
            string contract = contracts[rng.Next(contracts.Length)];

            // Age band: 1% missing
            string age = rng.NextDouble() < 0.01 ? "" : ageBands[rng.Next(ageBands.Length)];

            // Gender: always populated
            string gender = genders[rng.Next(genders.Length)];

            sb.AppendLine($"{empRef}\t{emplRef}\t{soc}\t{region}\t{sector}\t{pay}\t{hours}\t{contract}\t{age}\t{gender}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(300, doc.RowCount);
        Assert.Equal(10, doc.ColumnCount);

        // Region — always populated → missing rate = 0, fill rate = 1
        var mrRegion = doc.GetColumnMissingRate("region");
        var frRegion = doc.GetColumnFillRate("region");
        Assert.Equal(0.0, mrRegion, precision: 6);
        Assert.Equal(1.0, frRegion, precision: 6);
        Assert.Equal(1.0, mrRegion + frRegion, precision: 6);

        // Pay — ~8% missing
        var mrPay = doc.GetColumnMissingRate("pay_gross_weekly");
        var frPay = doc.GetColumnFillRate("pay_gross_weekly");
        Assert.True(mrPay >= 0.0 && mrPay <= 1.0);
        Assert.True(frPay >= 0.0 && frPay <= 1.0);
        Assert.Equal(1.0, mrPay + frPay, precision: 6);
        Assert.Equal(mrPay, doc.GetColumnMissingRate("pay_gross_weekly")); // consistent

        // SOC code — ~5% missing
        var mrSoc = doc.GetColumnMissingRate("soc_code");
        var frSoc = doc.GetColumnFillRate("soc_code");
        Assert.True(mrSoc >= 0.0 && mrSoc <= 1.0);
        Assert.Equal(1.0, mrSoc + frSoc, precision: 6);

        // Sector — ~3% missing → lower missing rate than pay
        var mrSector = doc.GetColumnMissingRate("sector");
        Assert.True(mrSector >= 0.0 && mrSector <= 1.0);
        Assert.Equal(1.0, mrSector + doc.GetColumnFillRate("sector"), precision: 6);

        // Hours — ~2% missing
        var mrHours = doc.GetColumnMissingRate("hours_worked");
        Assert.True(mrHours >= 0.0 && mrHours <= 1.0);
        Assert.True(mrHours <= mrPay); // hours less often missing than pay

        // Contract type — always populated
        Assert.Equal(0.0, doc.GetColumnMissingRate("contract_type"), precision: 6);
        Assert.Equal(1.0, doc.GetColumnFillRate("contract_type"), precision: 6);

        // SaveToFile
        var outPath = TempFile("ons_ashe_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(mrPay, loaded.GetColumnMissingRate("pay_gross_weekly"), precision: 6);
        Assert.Equal(frPay, loaded.GetColumnFillRate("pay_gross_weekly"), precision: 6);
        Assert.Equal(mrRegion, loaded.GetColumnMissingRate("region"), precision: 6);
        Assert.Equal(frRegion, loaded.GetColumnFillRate("region"), precision: 6);

        // MissingRate + FillRate = 1 for all loaded columns
        Assert.Equal(1.0, loaded.GetColumnMissingRate("soc_code") + loaded.GetColumnFillRate("soc_code"), precision: 6);
        Assert.Equal(1.0, loaded.GetColumnMissingRate("sector") + loaded.GetColumnFillRate("sector"), precision: 6);
    }
}
