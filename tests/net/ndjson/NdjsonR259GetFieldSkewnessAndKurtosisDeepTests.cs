// Tests for NdjsonDocument.GetFieldSkewness, GetFieldKurtosis deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R259

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R259: Tests for NdjsonDocument.GetFieldSkewness, GetFieldKurtosis deeper.
/// GetFieldSkewness(fieldName): returns the skewness of a numeric field across all records.
/// GetFieldKurtosis(fieldName): returns the excess kurtosis of a numeric field.
/// Covers: GetFieldSkewness no-throw; GetFieldSkewness finite; GetFieldSkewness consistent;
/// GetFieldSkewness zero for symmetric; GetFieldSkewness save-load;
/// GetFieldKurtosis no-throw; GetFieldKurtosis finite; GetFieldKurtosis consistent;
/// GetFieldKurtosis save-load;
/// dogfood CreateDoc→GetFieldSkewness→GetFieldKurtosis pipeline.
/// </summary>
public class NdjsonR259GetFieldSkewnessAndKurtosisDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR259GetFieldSkewnessAndKurtosisDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR259_" + Guid.NewGuid().ToString("N"));
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
        var rng = new Random(20240701);
        for (int i = 0; i < 100; i++)
        {
            double value = 10 + rng.NextDouble() * 80;
            double amount = Math.Exp(rng.NextDouble() * 3); // log-normal (right-skewed)
            sb.AppendLine($"{{\"id\":{i},\"value\":{value:F2},\"amount\":{amount:F4},\"category\":\"{(char)('A' + i % 5)}\"}}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateSymmetricNdjson()
    {
        // Uniform distribution over [-10, 10] — approximately zero skewness
        var path = TempFile("symmetric.ndjson");
        var sb = new StringBuilder();
        for (int i = -50; i < 50; i++)
            sb.AppendLine($"{{\"id\":{i + 50},\"symmetric_val\":{i}.0,\"label\":\"S\"}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldSkewness_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldSkewness("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldSkewness_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(double.IsFinite(doc.GetFieldSkewness("value")));
    }

    [Fact]
    public void GetFieldSkewness_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldSkewness("value"), doc.GetFieldSkewness("value"));
    }

    [Fact]
    public void GetFieldSkewness_NearZero_ForSymmetric()
    {
        var doc = NdjsonDocument.LoadFile(CreateSymmetricNdjson());
        // For a perfectly uniform symmetric distribution, skewness should be ~0
        Assert.True(Math.Abs(doc.GetFieldSkewness("symmetric_val")) < 1.0);
    }

    [Fact]
    public void GetFieldSkewness_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldSkewness("amount");
        var path = TempFile("skew_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldSkewness("amount"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetFieldKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldKurtosis_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldKurtosis("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldKurtosis_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(double.IsFinite(doc.GetFieldKurtosis("value")));
    }

    [Fact]
    public void GetFieldKurtosis_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldKurtosis("amount"), doc.GetFieldKurtosis("amount"));
    }

    [Fact]
    public void GetFieldKurtosis_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldKurtosis("value");
        var path = TempFile("kurt_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldKurtosis("value"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldSkewness_GetFieldKurtosis_Pipeline()
    {
        // Financial risk — daily returns distribution for UK equity portfolio (FTSE 350 constituents)
        // Skewness and kurtosis used for Value-at-Risk model selection and tail-risk assessment
        var path = TempFile("ftse350_daily_returns.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240104);

        string[] tickers = {
            "AZN", "HSBA", "SHEL", "ULVR", "BP", "GSK", "BATS", "RIO", "LSEG", "VOD",
            "BT", "IAG", "LLOY", "NWG", "BARC", "STAN", "TSCO", "SBRY", "MKS", "JD"
        };

        // Generate 150 trading day records with multiple assets
        for (int day = 0; day < 150; day++)
        {
            // Market-wide factor
            double mkt = (rng.NextDouble() - 0.5) * 0.04;
            foreach (var ticker in tickers)
            {
                // Individual return = market factor + idiosyncratic
                double idio = (rng.NextDouble() - 0.5) * 0.03;
                // Fat tails: occasionally large moves
                if (rng.NextDouble() < 0.05) idio *= 3.0;
                double ret = mkt + idio;
                double vol = 0.15 + rng.NextDouble() * 0.25; // annualised vol
                double beta = 0.6 + rng.NextDouble() * 0.8;
                double momentum = (rng.NextDouble() - 0.5) * 0.2;
                double size_factor = rng.NextDouble() * 0.1 - 0.05;
                sb.AppendLine($"{{\"date\":\"2024-{(day / 22 + 1):D2}-{(day % 22 + 1):D2}\"," +
                              $"\"ticker\":\"{ticker}\"," +
                              $"\"daily_return\":{ret:F6}," +
                              $"\"annualised_vol\":{vol:F4}," +
                              $"\"beta\":{beta:F4}," +
                              $"\"momentum_score\":{momentum:F4}," +
                              $"\"size_factor\":{size_factor:F4}," +
                              $"\"market_return\":{mkt:F6}}}");
            }
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(150 * tickers.Length, doc.RecordCount);

        // GetFieldSkewness — returns are typically negatively skewed (crash risk)
        var skewReturn = doc.GetFieldSkewness("daily_return");
        Assert.True(double.IsFinite(skewReturn));
        Assert.Equal(skewReturn, doc.GetFieldSkewness("daily_return")); // consistent

        var skewVol = doc.GetFieldSkewness("annualised_vol");
        Assert.True(double.IsFinite(skewVol));

        var skewBeta = doc.GetFieldSkewness("beta");
        Assert.True(double.IsFinite(skewBeta));

        var skewMomentum = doc.GetFieldSkewness("momentum_score");
        Assert.True(double.IsFinite(skewMomentum));

        // GetFieldKurtosis — financial returns have excess kurtosis (fat tails)
        var kurtReturn = doc.GetFieldKurtosis("daily_return");
        Assert.True(double.IsFinite(kurtReturn));
        Assert.Equal(kurtReturn, doc.GetFieldKurtosis("daily_return")); // consistent

        var kurtVol = doc.GetFieldKurtosis("annualised_vol");
        Assert.True(double.IsFinite(kurtVol));

        var kurtBeta = doc.GetFieldKurtosis("beta");
        Assert.True(double.IsFinite(kurtBeta));

        // Basic field stats cross-check
        var meanReturn = doc.GetFieldMean("daily_return");
        Assert.True(double.IsFinite(meanReturn));

        var stdReturn = doc.GetFieldStdDev("daily_return");
        Assert.True(stdReturn >= 0.0);

        var minReturn = doc.GetFieldMin("daily_return");
        var maxReturn = doc.GetFieldMax("daily_return");
        Assert.True(minReturn <= maxReturn);

        // Null pattern — all fields present
        var nullRate = doc.GetFieldNullRate("daily_return");
        Assert.Equal(0.0, nullRate, precision: 6);

        // SaveToFile
        var outPath = TempFile("ftse350_daily_returns_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(skewReturn, loaded.GetFieldSkewness("daily_return"), precision: 8);
        Assert.Equal(kurtReturn, loaded.GetFieldKurtosis("daily_return"), precision: 8);
        Assert.Equal(skewVol, loaded.GetFieldSkewness("annualised_vol"), precision: 8);
        Assert.Equal(kurtVol, loaded.GetFieldKurtosis("annualised_vol"), precision: 8);

        // Symmetric distribution — skewness near zero
        var pathSym = TempFile("symmetric_returns.ndjson");
        var sbSym = new StringBuilder();
        for (int i = -75; i < 75; i++)
            sbSym.AppendLine($"{{\"id\":{i + 75},\"return_bps\":{i}.0}}");
        File.WriteAllText(pathSym, sbSym.ToString());
        var docSym = NdjsonDocument.LoadFile(pathSym);
        Assert.True(Math.Abs(docSym.GetFieldSkewness("return_bps")) < 1.0);

        // Additional no-throw checks on loaded
        var ex1 = Record.Exception(() => loaded.GetFieldSkewness("beta"));
        var ex2 = Record.Exception(() => loaded.GetFieldKurtosis("momentum_score"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
