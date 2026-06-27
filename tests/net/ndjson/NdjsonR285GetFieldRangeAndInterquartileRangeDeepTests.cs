// Tests for NdjsonDocument.GetFieldRange, GetFieldInterquartileRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R285

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R285: Tests for NdjsonDocument.GetFieldRange, GetFieldInterquartileRange deeper.
/// GetFieldRange(fieldName): returns the range (max - min) of numeric field values across all records.
/// GetFieldInterquartileRange(fieldName): returns the IQR (Q3 - Q1) of numeric field values.
/// Covers: GetFieldRange no-throw; GetFieldRange non-negative; GetFieldRange 0 for uniform;
/// GetFieldRange consistent; GetFieldRange save-load;
/// GetFieldInterquartileRange no-throw; GetFieldInterquartileRange non-negative;
/// GetFieldInterquartileRange 0 for uniform;
/// GetFieldInterquartileRange leq GetFieldRange;
/// GetFieldInterquartileRange consistent; GetFieldInterquartileRange save-load; dogfood pipeline.
/// </summary>
public class NdjsonR285GetFieldRangeAndInterquartileRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR285GetFieldRangeAndInterquartileRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR285_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleNdjson()
    {
        var path = TempFile("sample.ndjson");
        var sb = new StringBuilder();
        // values 10,20,30,40,50,60,70,80,90,100 → range=90, Q1=27.5, Q3=72.5, IQR=45
        double[] vals = { 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 };
        for (int i = 0; i < vals.Length; i++)
            sb.AppendLine($"{{\"id\":{i},\"value\":{vals[i]}}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformNdjson()
    {
        var path = TempFile("uniform.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 10; i++)
            sb.AppendLine($"{{\"id\":{i},\"value\":42.0}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldRange_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldRange("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldRange_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldRange("value") >= 0);
    }

    [Fact]
    public void GetFieldRange_Zero_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(0.0, doc.GetFieldRange("value"), precision: 5);
    }

    [Fact]
    public void GetFieldRange_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldRange("value"), doc.GetFieldRange("value"));
    }

    [Fact]
    public void GetFieldRange_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldRange("value");
        var path = TempFile("range_save.ndjson");
        doc.SaveToFile(path);
        Assert.Equal(before, NdjsonDocument.LoadFile(path).GetFieldRange("value"), precision: 5);
    }

    // -------------------------------------------------------------------------
    // GetFieldInterquartileRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldInterquartileRange_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldInterquartileRange("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldInterquartileRange_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldInterquartileRange("value") >= 0);
    }

    [Fact]
    public void GetFieldInterquartileRange_Zero_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(0.0, doc.GetFieldInterquartileRange("value"), precision: 5);
    }

    [Fact]
    public void GetFieldInterquartileRange_Leq_GetFieldRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldInterquartileRange("value") <= doc.GetFieldRange("value"));
    }

    [Fact]
    public void GetFieldInterquartileRange_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldInterquartileRange("value"), doc.GetFieldInterquartileRange("value"));
    }

    [Fact]
    public void GetFieldInterquartileRange_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldInterquartileRange("value");
        var path = TempFile("iqr_save.ndjson");
        doc.SaveToFile(path);
        Assert.Equal(before, NdjsonDocument.LoadFile(path).GetFieldInterquartileRange("value"), precision: 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldRange_GetFieldInterquartileRange_Pipeline()
    {
        // Energy — National Grid ESO / Ofgem: GB Balancing Mechanism Settlement 2024
        // Half-hourly System Price (SBP/SSP) and imbalance volume data
        // Range identifies price spike events; IQR gives the typical settlement band for auction design

        var path = TempFile("neso_bm_settlement_2024.ndjson");
        var sb = new StringBuilder();

        var rng = new Random(20240101);
        string[] settlementDates = {
            "2024-01-15", "2024-02-12", "2024-03-18", "2024-04-22", "2024-05-09",
            "2024-06-17", "2024-07-03", "2024-08-19", "2024-09-11", "2024-10-28",
            "2024-11-04", "2024-12-23"
        };

        // Simulate 48 settlement periods per day for 12 selected dates
        for (int d = 0; d < settlementDates.Length; d++)
        {
            for (int sp = 1; sp <= 48; sp++)
            {
                // System Buy Price (SBP) — typically £40-£300/MWh with occasional spikes
                double sbp;
                if (rng.NextDouble() < 0.05) // 5% spike probability
                    sbp = 200 + rng.NextDouble() * 800; // £200-£1000 spike
                else
                    sbp = 40 + rng.NextDouble() * 100; // £40-£140 normal

                // System Sell Price (SSP) — typically £20-£80/MWh
                double ssp = 20 + rng.NextDouble() * 60;

                // Net imbalance volume (MWh) — negative = short system, positive = long system
                double niv = (rng.NextDouble() - 0.5) * 400; // -200 to +200 MWh

                // Accepted BM offer/bid volume
                double offerVol = rng.NextDouble() * 150;
                double bidVol = rng.NextDouble() * 150;

                // Frequency response (Hz deviation from 50 Hz)
                double freqDev = (rng.NextDouble() - 0.5) * 0.4; // ±0.2 Hz

                sb.AppendLine($"{{\"settlement_date\":\"{settlementDates[d]}\",\"settlement_period\":{sp}," +
                              $"\"sbp_gbp_per_mwh\":{sbp:F2},\"ssp_gbp_per_mwh\":{ssp:F2}," +
                              $"\"net_imbalance_volume_mwh\":{niv:F3}," +
                              $"\"bm_offer_volume_mwh\":{offerVol:F3},\"bm_bid_volume_mwh\":{bidVol:F3}," +
                              $"\"frequency_deviation_hz\":{freqDev:F4}}}");
            }
        }

        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(576, doc.RecordCount); // 12 dates × 48 settlement periods

        // SBP range (captures price spike magnitude)
        var sbpRange = doc.GetFieldRange("sbp_gbp_per_mwh");
        Assert.True(sbpRange > 0); // spikes ensure non-trivial range
        Assert.Equal(sbpRange, doc.GetFieldRange("sbp_gbp_per_mwh"), precision: 5); // consistent

        // SBP IQR (the typical settlement band)
        var sbpIqr = doc.GetFieldInterquartileRange("sbp_gbp_per_mwh");
        Assert.True(sbpIqr >= 0);
        Assert.True(sbpIqr <= sbpRange); // IQR ≤ range
        Assert.Equal(sbpIqr, doc.GetFieldInterquartileRange("sbp_gbp_per_mwh"), precision: 5); // consistent

        // SSP analytics (sell price — tighter distribution)
        var sspRange = doc.GetFieldRange("ssp_gbp_per_mwh");
        var sspIqr = doc.GetFieldInterquartileRange("ssp_gbp_per_mwh");
        Assert.True(sspRange >= 0);
        Assert.True(sspIqr >= 0);
        Assert.True(sspIqr <= sspRange);

        // NIV range (system imbalance spread)
        var nivRange = doc.GetFieldRange("net_imbalance_volume_mwh");
        var nivIqr = doc.GetFieldInterquartileRange("net_imbalance_volume_mwh");
        Assert.True(nivRange >= 0);
        Assert.True(nivIqr >= 0);
        Assert.True(nivIqr <= nivRange);

        // Frequency deviation — small range expected (grid frequency control)
        var freqRange = doc.GetFieldRange("frequency_deviation_hz");
        var freqIqr = doc.GetFieldInterquartileRange("frequency_deviation_hz");
        Assert.True(freqRange >= 0);
        Assert.True(freqIqr >= 0);
        Assert.True(freqIqr <= freqRange);

        // SaveToFile
        var outPath = TempFile("neso_bm_settlement_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(sbpRange, loaded.GetFieldRange("sbp_gbp_per_mwh"), precision: 5);
        Assert.Equal(sbpIqr, loaded.GetFieldInterquartileRange("sbp_gbp_per_mwh"), precision: 5);
        Assert.Equal(sspRange, loaded.GetFieldRange("ssp_gbp_per_mwh"), precision: 5);
        Assert.Equal(sspIqr, loaded.GetFieldInterquartileRange("ssp_gbp_per_mwh"), precision: 5);

        var ex1 = Record.Exception(() => loaded.GetFieldRange("sbp_gbp_per_mwh"));
        var ex2 = Record.Exception(() => loaded.GetFieldInterquartileRange("sbp_gbp_per_mwh"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
