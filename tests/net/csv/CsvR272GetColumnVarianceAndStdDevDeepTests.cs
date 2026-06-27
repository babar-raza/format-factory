// Tests for CsvDocument.GetColumnVariance, GetColumnStdDev deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R272

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R272: Tests for CsvDocument.GetColumnVariance, GetColumnStdDev deeper.
/// GetColumnVariance(colName): returns the sample variance of numeric values in the column.
/// GetColumnStdDev(colName): returns the sample standard deviation; equals sqrt(variance).
/// Covers: GetColumnVariance no-throw; GetColumnVariance non-negative; GetColumnVariance zero for uniform;
/// GetColumnVariance consistent; GetColumnVariance save-load;
/// GetColumnStdDev no-throw; GetColumnStdDev non-negative; GetColumnStdDev zero for uniform;
/// GetColumnStdDev consistent; GetColumnStdDev save-load;
/// GetColumnVariance equals GetColumnStdDev squared; dogfood pipeline.
/// </summary>
public class CsvR272GetColumnVarianceAndStdDevDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR272GetColumnVarianceAndStdDevDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR272_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id,value");
        for (int i = 0; i < 10; i++) sb.AppendLine($"R{i:D2},{i * 10.0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,measure");
        for (int i = 0; i < 20; i++) sb.AppendLine($"R{i:D2},42.5");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnVariance_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnVariance("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnVariance_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnVariance("value") >= 0.0);
    }

    [Fact]
    public void GetColumnVariance_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, doc.GetColumnVariance("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnVariance_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnVariance("value"), doc.GetColumnVariance("value"));
    }

    [Fact]
    public void GetColumnVariance_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnVariance("value");
        var path = TempFile("var_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnVariance("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStdDev_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnStdDev("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnStdDev_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnStdDev("value") >= 0.0);
    }

    [Fact]
    public void GetColumnStdDev_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, doc.GetColumnStdDev("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnStdDev_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnStdDev("value"), doc.GetColumnStdDev("value"));
    }

    [Fact]
    public void GetColumnStdDev_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnStdDev("value");
        var path = TempFile("sd_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnStdDev("value"), precision: 6);
    }

    [Fact]
    public void GetColumnVariance_Equals_StdDev_Squared()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var sd = doc.GetColumnStdDev("value");
        var var_ = doc.GetColumnVariance("value");
        Assert.Equal(sd * sd, var_, precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnVariance_GetColumnStdDev_Pipeline()
    {
        // Energy — Ofgem / National Grid ESO: Balancing Mechanism Bid/Offer Price Spread
        // Daily ancillary service price data from the GB electricity balancing mechanism
        // Variance/StdDev detect price volatility and concentration risk across BM participants

        var path = TempFile("ofgem_bm_prices_2024.csv");
        var sb = new StringBuilder();
        sb.AppendLine("unit_id,unit_name,technology,offer_price_gbpmwh,bid_price_gbpmwh,spread_gbpmwh,volume_mwh,utilisation_rate_pct,carbon_intensity_gco2kwh,response_time_sec");

        var rng = new Random(20240601);
        string[] units = {
            "DRAXT-1", "DRAXT-2", "PEMB-1G", "PEMB-2G", "KILLN-1", "FFES-BESS1",
            "FFES-BESS2", "GYAR-1", "STAY-3", "STAY-4", "RATS-1", "RATS-2",
            "GANL-1", "GANL-2", "FDUN-1", "FDUN-2", "WYLFA-1", "RHEI-BESS",
            "BATS-BESS", "MIDES-1"
        };
        string[] techs = {
            "CCGT", "CCGT", "OCGT", "OCGT", "PUMP_STORAGE",
            "BATTERY", "BATTERY", "WIND_OFFSHORE", "CCGT", "CCGT",
            "NUCLEAR", "NUCLEAR", "CCGT", "CCGT", "INTERCONNECTOR",
            "INTERCONNECTOR", "NUCLEAR", "BATTERY", "BATTERY", "OCGT"
        };

        for (int i = 0; i < units.Length; i++)
        {
            double offer = 80 + rng.NextDouble() * 200 + (i == 4 ? 150 : 0);  // KILLN outlier
            double bid = 20 + rng.NextDouble() * 60;
            double spread = offer - bid;
            double volume = 50 + rng.NextDouble() * 500;
            double util = 10 + rng.NextDouble() * 85;
            double carbon = i < 2 ? 350 + rng.NextDouble() * 100
                          : i < 4 ? 500 + rng.NextDouble() * 150
                          : i < 6 ? 0 : 420 + rng.NextDouble() * 80;
            double resp = i >= 5 && i <= 8 ? 0.5 + rng.NextDouble() * 2
                        : 5 + rng.NextDouble() * 30;
            sb.AppendLine($"{units[i]},{units[i]},{techs[i]},{offer:F2},{bid:F2},{spread:F2},{volume:F1},{util:F1},{carbon:F0},{resp:F1}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(units.Length, doc.RowCount);
        Assert.Equal(10, doc.ColumnCount);

        // Offer price variance and StdDev
        var offerVar = doc.GetColumnVariance("offer_price_gbpmwh");
        var offerSd = doc.GetColumnStdDev("offer_price_gbpmwh");
        Assert.True(offerVar >= 0.0);
        Assert.True(offerSd >= 0.0);
        Assert.True(offerVar > 0.0); // prices vary
        Assert.Equal(offerSd * offerSd, offerVar, precision: 4);
        Assert.Equal(offerVar, doc.GetColumnVariance("offer_price_gbpmwh")); // consistent
        Assert.Equal(offerSd, doc.GetColumnStdDev("offer_price_gbpmwh")); // consistent

        // Spread variance
        var spreadVar = doc.GetColumnVariance("spread_gbpmwh");
        var spreadSd = doc.GetColumnStdDev("spread_gbpmwh");
        Assert.True(spreadVar >= 0.0);
        Assert.True(spreadSd >= 0.0);
        Assert.Equal(spreadSd * spreadSd, spreadVar, precision: 4);

        // Volume variance
        var volVar = doc.GetColumnVariance("volume_mwh");
        var volSd = doc.GetColumnStdDev("volume_mwh");
        Assert.True(volVar >= 0.0);
        Assert.Equal(volSd * volSd, volVar, precision: 2);

        // Utilisation rate variance (should be smaller than price variance in absolute)
        var utilVar = doc.GetColumnVariance("utilisation_rate_pct");
        Assert.True(utilVar >= 0.0);

        // SaveToFile
        var outPath = TempFile("ofgem_bm_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(offerVar, loaded.GetColumnVariance("offer_price_gbpmwh"), precision: 6);
        Assert.Equal(offerSd, loaded.GetColumnStdDev("offer_price_gbpmwh"), precision: 6);
        Assert.Equal(spreadVar, loaded.GetColumnVariance("spread_gbpmwh"), precision: 6);
        Assert.Equal(spreadSd, loaded.GetColumnStdDev("spread_gbpmwh"), precision: 6);
        Assert.Equal(volVar, loaded.GetColumnVariance("volume_mwh"), precision: 3);
    }
}
