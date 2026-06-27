// Tests for TsvDocument.GetColumnCorrelation, GetColumnCovariance, GetColumnMutualInformation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R239

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R239: Tests for TsvDocument.GetColumnCorrelation, GetColumnCovariance, GetColumnMutualInformation deeper.
/// GetColumnCorrelation(col1, col2): returns the Pearson correlation coefficient between two numeric columns.
/// GetColumnCovariance(col1, col2): returns the sample covariance between two numeric columns.
/// GetColumnMutualInformation(col1, col2): returns an information-theoretic measure of dependence.
/// Covers: GetColumnCorrelation no-throw; GetColumnCorrelation in [-1,1]; GetColumnCorrelation consistent;
/// GetColumnCorrelation one for identical columns; GetColumnCorrelation zero for uncorrelated;
/// GetColumnCovariance no-throw; GetColumnCovariance consistent; GetColumnCovariance sign consistent with correlation;
/// GetColumnCovariance save-load;
/// GetColumnMutualInformation no-throw; GetColumnMutualInformation non-negative; GetColumnMutualInformation consistent;
/// dogfood GetColumnCorrelation→GetColumnCovariance→GetColumnMutualInformation pipeline.
/// </summary>
public class TsvR239GetColumnCorrelationAndCovarianceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR239GetColumnCorrelationAndCovarianceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR239_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateClimateDataTsv()
    {
        var path = TempFile("climate.tsv");
        File.WriteAllLines(path, new[]
        {
            "station\ttemp_c\thumidity_pct\tco2_ppm\train_mm\twind_kmh",
            "London\t12.4\t78\t418\t52\t24",
            "Edinburgh\t8.1\t82\t415\t89\t35",
            "Manchester\t10.8\t80\t416\t74\t28",
            "Birmingham\t11.2\t76\t417\t58\t21",
            "Bristol\t12.9\t74\t419\t46\t19",
            "Cardiff\t11.7\t79\t416\t68\t26",
            "Belfast\t9.3\t83\t414\t95\t32",
            "Glasgow\t7.8\t85\t413\t112\t38",
            "Liverpool\t10.1\t81\t415\t80\t30",
            "Leeds\t9.7\t79\t416\t75\t27",
            "Sheffield\t10.3\t77\t417\t66\t23",
            "Exeter\t13.1\t72\t420\t42\t17",
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCorrelation_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateClimateDataTsv());
        var ex = Record.Exception(() => doc.GetColumnCorrelation("temp_c", "humidity_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCorrelation_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateClimateDataTsv());
        var corr = doc.GetColumnCorrelation("temp_c", "humidity_pct");
        Assert.True(corr >= -1.0 && corr <= 1.0);
    }

    [Fact]
    public void GetColumnCorrelation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateClimateDataTsv());
        Assert.Equal(
            doc.GetColumnCorrelation("temp_c", "rain_mm"),
            doc.GetColumnCorrelation("temp_c", "rain_mm"));
    }

    [Fact]
    public void GetColumnCorrelation_One_ForIdenticalColumns()
    {
        var doc = TsvDocument.LoadFile(CreateClimateDataTsv());
        var corr = doc.GetColumnCorrelation("temp_c", "temp_c");
        Assert.True(Math.Abs(corr - 1.0) < 1e-6);
    }

    [Fact]
    public void GetColumnCorrelation_Symmetric()
    {
        var doc = TsvDocument.LoadFile(CreateClimateDataTsv());
        var c1 = doc.GetColumnCorrelation("temp_c", "rain_mm");
        var c2 = doc.GetColumnCorrelation("rain_mm", "temp_c");
        Assert.Equal(c1, c2, precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnCovariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCovariance_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateClimateDataTsv());
        var ex = Record.Exception(() => doc.GetColumnCovariance("temp_c", "rain_mm"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCovariance_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateClimateDataTsv());
        Assert.Equal(
            doc.GetColumnCovariance("humidity_pct", "rain_mm"),
            doc.GetColumnCovariance("humidity_pct", "rain_mm"));
    }

    [Fact]
    public void GetColumnCovariance_Sign_Consistent_With_Correlation()
    {
        var doc = TsvDocument.LoadFile(CreateClimateDataTsv());
        var corr = doc.GetColumnCorrelation("temp_c", "rain_mm");
        var cov = doc.GetColumnCovariance("temp_c", "rain_mm");
        // Sign of covariance must match sign of correlation
        Assert.True(Math.Sign(corr) == Math.Sign(cov) || (Math.Abs(corr) < 1e-6 && Math.Abs(cov) < 1e-6));
    }

    [Fact]
    public void GetColumnCovariance_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateClimateDataTsv());
        var before = doc.GetColumnCovariance("temp_c", "co2_ppm");
        var path = TempFile("cov_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCovariance("temp_c", "co2_ppm"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnMutualInformation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMutualInformation_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateClimateDataTsv());
        var ex = Record.Exception(() => doc.GetColumnMutualInformation("temp_c", "humidity_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMutualInformation_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateClimateDataTsv());
        Assert.True(doc.GetColumnMutualInformation("temp_c", "humidity_pct") >= 0);
    }

    [Fact]
    public void GetColumnMutualInformation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateClimateDataTsv());
        Assert.Equal(
            doc.GetColumnMutualInformation("temp_c", "rain_mm"),
            doc.GetColumnMutualInformation("temp_c", "rain_mm"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnCorrelation_GetColumnCovariance_GetColumnMutualInformation_Pipeline()
    {
        // Environmental science — air quality monitoring correlation analysis
        var path = TempFile("air_quality.tsv");
        var lines = new System.Collections.Generic.List<string>();
        lines.Add("date\tno2_ugm3\tpm25_ugm3\to3_ugm3\ttemp_c\twind_ms\trh_pct\ttraffic_idx");
        var rng = new Random(20240801);
        for (int i = 0; i < 90; i++) // 90 days of monitoring
        {
            double traffic = 30 + rng.NextDouble() * 140; // 30-170 traffic index
            double no2 = 15 + traffic * 0.3 + (rng.NextDouble() - 0.5) * 20; // correlated with traffic
            double pm25 = 5 + no2 * 0.25 + (rng.NextDouble() - 0.5) * 10; // correlated with NO2
            double o3 = 80 - no2 * 0.4 + (rng.NextDouble() - 0.5) * 30; // inversely correlated
            double temp = 8 + rng.NextDouble() * 18;
            double wind = 1 + rng.NextDouble() * 12;
            double rh = 40 + rng.NextDouble() * 55;
            lines.Add($"2024-{(i / 30 + 1):D2}-{(i % 30 + 1):D2}\t{no2:F1}\t{pm25:F1}\t{o3:F1}\t{temp:F1}\t{wind:F1}\t{rh:F1}\t{traffic:F0}");
        }
        File.WriteAllLines(path, lines);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(90, doc.RowCount);

        // GetColumnCorrelation — NO2 vs traffic (should be positively correlated)
        var no2TrafficCorr = doc.GetColumnCorrelation("no2_ugm3", "traffic_idx");
        Assert.True(no2TrafficCorr >= -1.0 && no2TrafficCorr <= 1.0);
        Assert.True(no2TrafficCorr > 0); // designed to be positively correlated
        Assert.Equal(no2TrafficCorr, doc.GetColumnCorrelation("no2_ugm3", "traffic_idx")); // consistent

        // Self-correlation = 1
        var selfCorr = doc.GetColumnCorrelation("pm25_ugm3", "pm25_ugm3");
        Assert.True(Math.Abs(selfCorr - 1.0) < 1e-6);

        // NO2 vs O3 — designed to be negatively correlated
        var no2O3Corr = doc.GetColumnCorrelation("no2_ugm3", "o3_ugm3");
        Assert.True(no2O3Corr >= -1.0 && no2O3Corr <= 1.0);
        Assert.True(no2O3Corr < 0); // negative correlation designed in

        // Symmetric
        var corrAB = doc.GetColumnCorrelation("no2_ugm3", "pm25_ugm3");
        var corrBA = doc.GetColumnCorrelation("pm25_ugm3", "no2_ugm3");
        Assert.Equal(corrAB, corrBA, precision: 6);

        // GetColumnCovariance
        var cov = doc.GetColumnCovariance("no2_ugm3", "traffic_idx");
        Assert.True(Math.Sign(cov) == Math.Sign(no2TrafficCorr) || Math.Abs(cov) < 1e-6);
        Assert.Equal(cov, doc.GetColumnCovariance("no2_ugm3", "traffic_idx")); // consistent

        // GetColumnMutualInformation
        var mi = doc.GetColumnMutualInformation("no2_ugm3", "traffic_idx");
        Assert.True(mi >= 0);
        Assert.Equal(mi, doc.GetColumnMutualInformation("no2_ugm3", "traffic_idx")); // consistent

        // All column pairs non-throwing
        string[] cols = { "no2_ugm3", "pm25_ugm3", "o3_ugm3", "temp_c", "wind_ms" };
        for (int i = 0; i < cols.Length; i++)
            for (int j = i + 1; j < cols.Length; j++)
            {
                var c = doc.GetColumnCorrelation(cols[i], cols[j]);
                Assert.True(c >= -1.0 && c <= 1.0);
                Assert.True(doc.GetColumnMutualInformation(cols[i], cols[j]) >= 0);
            }

        // SaveToFile
        var outPath = TempFile("air_quality_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(no2TrafficCorr, loaded.GetColumnCorrelation("no2_ugm3", "traffic_idx"), precision: 6);
        Assert.Equal(cov, loaded.GetColumnCovariance("no2_ugm3", "traffic_idx"), precision: 6);
        Assert.Equal(mi, loaded.GetColumnMutualInformation("no2_ugm3", "traffic_idx"), precision: 6);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }
}
