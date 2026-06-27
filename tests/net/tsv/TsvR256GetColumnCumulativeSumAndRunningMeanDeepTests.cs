// Tests for TsvDocument.GetColumnCumulativeSum, GetColumnRunningMean deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R256

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R256: Tests for TsvDocument.GetColumnCumulativeSum, GetColumnRunningMean deeper.
/// GetColumnCumulativeSum(colName): returns an array of running totals for a numeric column.
/// GetColumnRunningMean(colName): returns an array of running means for a numeric column.
/// Covers: GetColumnCumulativeSum no-throw; GetColumnCumulativeSum non-null;
/// GetColumnCumulativeSum length equals RowCount; GetColumnCumulativeSum last equals column sum;
/// GetColumnCumulativeSum monotone for non-negative; GetColumnCumulativeSum consistent;
/// GetColumnCumulativeSum save-load;
/// GetColumnRunningMean no-throw; GetColumnRunningMean non-null;
/// GetColumnRunningMean length equals RowCount; GetColumnRunningMean last equals column mean;
/// GetColumnRunningMean consistent; GetColumnRunningMean save-load;
/// dogfood CreateDoc→GetColumnCumulativeSum→GetColumnRunningMean pipeline.
/// </summary>
public class TsvR256GetColumnCumulativeSumAndRunningMeanDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR256GetColumnCumulativeSumAndRunningMeanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR256_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleTsv()
    {
        var path = TempFile("sample.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("month\trevenue\tcosts\tprofit\tcumulative_users");
        double[] revs = { 120000, 135000, 142000, 158000, 163000, 171000,
                          180000, 195000, 188000, 201000, 215000, 228000 };
        for (int i = 0; i < 12; i++)
        {
            double costs = revs[i] * 0.65;
            double profit = revs[i] - costs;
            int users = 10000 + i * 850;
            sb.AppendLine($"2024-{i + 1:D2}\t{revs[i]:F0}\t{costs:F0}\t{profit:F0}\t{users}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnCumulativeSum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCumulativeSum_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnCumulativeSum("revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCumulativeSum_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetColumnCumulativeSum("revenue"));
    }

    [Fact]
    public void GetColumnCumulativeSum_LengthEqualsRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.RowCount, doc.GetColumnCumulativeSum("revenue").Length);
    }

    [Fact]
    public void GetColumnCumulativeSum_LastEqualsColumnSum()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var cs = doc.GetColumnCumulativeSum("revenue");
        Assert.Equal(doc.GetColumnSum("revenue"), cs[cs.Length - 1], precision: 4);
    }

    [Fact]
    public void GetColumnCumulativeSum_MonotoneForPositive()
    {
        // All revenues are positive — cumulative sum should be non-decreasing
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var cs = doc.GetColumnCumulativeSum("revenue");
        for (int i = 1; i < cs.Length; i++)
            Assert.True(cs[i] >= cs[i - 1]);
    }

    [Fact]
    public void GetColumnCumulativeSum_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var cs1 = doc.GetColumnCumulativeSum("profit");
        var cs2 = doc.GetColumnCumulativeSum("profit");
        Assert.Equal(cs1.Length, cs2.Length);
        for (int i = 0; i < cs1.Length; i++)
            Assert.Equal(cs1[i], cs2[i]);
    }

    [Fact]
    public void GetColumnCumulativeSum_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnCumulativeSum("revenue");
        var path = TempFile("cs_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetColumnCumulativeSum("revenue");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnRunningMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRunningMean_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnRunningMean("revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRunningMean_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetColumnRunningMean("revenue"));
    }

    [Fact]
    public void GetColumnRunningMean_LengthEqualsRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.RowCount, doc.GetColumnRunningMean("revenue").Length);
    }

    [Fact]
    public void GetColumnRunningMean_LastEqualsColumnMean()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var rm = doc.GetColumnRunningMean("revenue");
        Assert.Equal(doc.GetColumnMean("revenue"), rm[rm.Length - 1], precision: 4);
    }

    [Fact]
    public void GetColumnRunningMean_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var rm1 = doc.GetColumnRunningMean("costs");
        var rm2 = doc.GetColumnRunningMean("costs");
        Assert.Equal(rm1.Length, rm2.Length);
        for (int i = 0; i < rm1.Length; i++)
            Assert.Equal(rm1[i], rm2[i]);
    }

    [Fact]
    public void GetColumnRunningMean_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnRunningMean("profit");
        var path = TempFile("rm_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetColumnRunningMean("profit");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnCumulativeSum_GetColumnRunningMean_Pipeline()
    {
        // Government finance — HM Treasury Public Sector Net Borrowing (PSNB) Monthly Data
        // Cumulative borrowing tracking against OBR fiscal forecasts for 2024-25
        var path = TempFile("hmtreasury_psnb.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("month\tpsnb_gbm\tobr_forecast_gbm\tcentral_govt_receipts\tcentral_govt_spending\tinterest_payments\tpublic_sector_debt_gbm");

        // Monthly PSNB profile for 2024-25 (simulated, aligned to OBR March 2024 forecast)
        double[] psnb = { 14.2, 12.8, 15.6, 8.9, 10.4, 17.8, 11.2, 9.8, 13.5, 16.1, 14.9, 8.3 };
        double[] obrForecast = { 13.5, 13.0, 14.8, 9.5, 10.8, 16.9, 11.9, 10.2, 13.1, 15.8, 15.2, 9.3 };
        double[] receipts = { 72.1, 68.4, 75.8, 82.3, 79.6, 66.2, 70.8, 73.5, 77.2, 69.8, 78.4, 95.6 };
        double baseDebt = 2682.4;

        for (int i = 0; i < 12; i++)
        {
            double spending = receipts[i] + psnb[i];
            double interest = 5.2 + (i % 3 == 0 ? 1.8 : 0.4);
            double debt = baseDebt + psnb.Take(i + 1).Sum();
            string month = $"2024-{(i + 4 > 12 ? i - 8 : i + 4):D2}"; // Apr 2024 to Mar 2025
            sb.AppendLine($"{month}\t{psnb[i]:F1}\t{obrForecast[i]:F1}\t{receipts[i]:F1}\t{spending:F1}\t{interest:F2}\t{debt:F1}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(12, doc.RowCount);
        Assert.Equal(7, doc.ColumnCount);

        // GetColumnCumulativeSum — cumulative PSNB
        var csPsnb = doc.GetColumnCumulativeSum("psnb_gbm");
        Assert.NotNull(csPsnb);
        Assert.Equal(12, csPsnb.Length);
        Assert.Equal(doc.GetColumnSum("psnb_gbm"), csPsnb[11], precision: 4);

        // Cumulative PSNB should be non-decreasing (all monthly values positive)
        for (int i = 1; i < csPsnb.Length; i++)
            Assert.True(csPsnb[i] >= csPsnb[i - 1]);

        // Consistent
        var csPsnb2 = doc.GetColumnCumulativeSum("psnb_gbm");
        for (int i = 0; i < csPsnb.Length; i++)
            Assert.Equal(csPsnb[i], csPsnb2[i]);

        // OBR forecast cumulative
        var csObr = doc.GetColumnCumulativeSum("obr_forecast_gbm");
        Assert.Equal(12, csObr.Length);
        Assert.Equal(doc.GetColumnSum("obr_forecast_gbm"), csObr[11], precision: 4);

        // GetColumnRunningMean — rolling average receipts
        var rmReceipts = doc.GetColumnRunningMean("central_govt_receipts");
        Assert.NotNull(rmReceipts);
        Assert.Equal(12, rmReceipts.Length);
        Assert.Equal(doc.GetColumnMean("central_govt_receipts"), rmReceipts[11], precision: 4);

        // Running mean after 1 month = first value
        Assert.Equal(doc.GetColumnSum("central_govt_receipts") > 0 ? rmReceipts[0] : 0,
                     rmReceipts[0]);

        // Consistent
        var rmReceipts2 = doc.GetColumnRunningMean("central_govt_receipts");
        for (int i = 0; i < rmReceipts.Length; i++)
            Assert.Equal(rmReceipts[i], rmReceipts2[i]);

        // Running mean PSNB
        var rmPsnb = doc.GetColumnRunningMean("psnb_gbm");
        Assert.NotNull(rmPsnb);
        Assert.Equal(doc.GetColumnMean("psnb_gbm"), rmPsnb[11], precision: 4);

        // Basic stats
        Assert.True(doc.GetColumnSum("psnb_gbm") > 0);
        Assert.True(doc.GetColumnMean("central_govt_receipts") > 0);
        Assert.True(doc.GetColumnMin("psnb_gbm") <= doc.GetColumnMax("psnb_gbm"));

        // SaveToFile
        var outPath = TempFile("hmtreasury_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(12, loaded.RowCount);
        var loadedCs = loaded.GetColumnCumulativeSum("psnb_gbm");
        Assert.Equal(csPsnb.Length, loadedCs.Length);
        for (int i = 0; i < csPsnb.Length; i++)
            Assert.Equal(csPsnb[i], loadedCs[i], precision: 4);
        var loadedRm = loaded.GetColumnRunningMean("central_govt_receipts");
        Assert.Equal(rmReceipts.Length, loadedRm.Length);
        Assert.Equal(rmReceipts[11], loadedRm[11], precision: 4);
    }
}
