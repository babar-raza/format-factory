// Tests for TsvDocument.GetColumnSkewness, GetColumnKurtosis deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R272

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R272: Tests for TsvDocument.GetColumnSkewness, GetColumnKurtosis deeper.
/// GetColumnSkewness(colName): returns the skewness of the numeric distribution in the column.
/// GetColumnKurtosis(colName): returns the kurtosis of the numeric distribution in the column.
/// Covers: GetColumnSkewness no-throw; GetColumnSkewness finite; GetColumnSkewness zero for uniform;
/// GetColumnSkewness consistent; GetColumnSkewness save-load;
/// GetColumnKurtosis no-throw; GetColumnKurtosis finite;
/// GetColumnKurtosis consistent; GetColumnKurtosis save-load;
/// dogfood pipeline.
/// </summary>
public class TsvR272GetColumnSkewnessAndKurtosisDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR272GetColumnSkewnessAndKurtosisDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR272_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id\tvalue");
        for (int i = 0; i < 20; i++) sb.AppendLine($"R{i:D2}\t{i * 5.0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tmeasure");
        for (int i = 0; i < 20; i++) sb.AppendLine($"R{i:D2}\t42.0");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnSkewness_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnSkewness("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnSkewness_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var sk = doc.GetColumnSkewness("value");
        Assert.True(!double.IsNaN(sk) && !double.IsInfinity(sk));
    }

    [Fact]
    public void GetColumnSkewness_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0.0, doc.GetColumnSkewness("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnSkewness_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnSkewness("value"), doc.GetColumnSkewness("value"));
    }

    [Fact]
    public void GetColumnSkewness_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnSkewness("value");
        var path = TempFile("sk_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnSkewness("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnKurtosis_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnKurtosis("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnKurtosis_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var kurt = doc.GetColumnKurtosis("value");
        Assert.True(!double.IsNaN(kurt) && !double.IsInfinity(kurt));
    }

    [Fact]
    public void GetColumnKurtosis_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnKurtosis("value"), doc.GetColumnKurtosis("value"));
    }

    [Fact]
    public void GetColumnKurtosis_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnKurtosis("value");
        var path = TempFile("kurt_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnKurtosis("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnSkewness_GetColumnKurtosis_Pipeline()
    {
        // Finance — FCA / PRA: Retail Banking Conduct Metrics 2024
        // Branch and digital channel complaint rates and resolution times
        // Skewness/kurtosis identify non-normal complaint distributions requiring regulatory attention

        var path = TempFile("fca_pra_retail_banking_2024.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("firm_id\tfirm_name\tchannel\tcomplaints_per_1k_accounts\tresolution_days\tfinancial_redress_gbp\tuphold_rate_pct\tescalation_rate_pct");

        var rng = new Random(20240701);
        string[] firms = {
            "Barclays", "HSBC_UK", "Lloyds_Bank", "NatWest", "Santander_UK",
            "Halifax", "Nationwide_BS", "Metro_Bank", "TSB_Bank", "Virgin_Money",
            "Monzo_Bank", "Starling_Bank", "Revolut_UK", "Chase_UK", "Atom_Bank",
            "First_Direct", "M&S_Bank", "Tesco_Bank", "Co_operative_Bank", "Clydesdale_Bank"
        };
        string[] channels = { "Branch", "Digital", "Telephone", "Branch", "Digital",
                               "Digital", "Branch", "Digital", "Telephone", "Digital",
                               "Digital", "Digital", "Digital", "Digital", "Digital",
                               "Telephone", "Telephone", "Branch", "Branch", "Branch" };

        for (int i = 0; i < firms.Length; i++)
        {
            // Complaint rate: mostly low, Monzo/Revolut/Chase slightly higher (digital onboarding)
            double compRate = i < 11 ? 0.8 + rng.NextDouble() * 2.5
                            : i < 14 ? 2.5 + rng.NextDouble() * 4.0 + (i == 12 ? 8.0 : 0) // Revolut outlier
                            : 0.5 + rng.NextDouble() * 1.5;
            // Resolution days: right-skewed (most <10, some very long cases)
            double resDays = rng.NextDouble() < 0.15
                ? 30 + rng.NextDouble() * 30  // complex cases
                : 2 + rng.NextDouble() * 8;
            double redress = compRate * (50 + rng.NextDouble() * 300);
            double uphold = 20 + rng.NextDouble() * 40;
            double escalation = 5 + rng.NextDouble() * 20;
            sb.AppendLine($"FRM{i:D3}\t{firms[i]}\t{channels[i]}\t{compRate:F2}\t{resDays:F1}\t{redress:F0}\t{uphold:F1}\t{escalation:F1}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(firms.Length, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // Complaint rate skewness (positive expected due to outliers)
        var compSkew = doc.GetColumnSkewness("complaints_per_1k_accounts");
        var compKurt = doc.GetColumnKurtosis("complaints_per_1k_accounts");
        Assert.True(!double.IsNaN(compSkew) && !double.IsInfinity(compSkew));
        Assert.True(!double.IsNaN(compKurt) && !double.IsInfinity(compKurt));
        Assert.Equal(compSkew, doc.GetColumnSkewness("complaints_per_1k_accounts")); // consistent
        Assert.Equal(compKurt, doc.GetColumnKurtosis("complaints_per_1k_accounts")); // consistent

        // Resolution days skewness (right-skewed: outlier long-running cases)
        var resDaysSkew = doc.GetColumnSkewness("resolution_days");
        var resDaysKurt = doc.GetColumnKurtosis("resolution_days");
        Assert.True(!double.IsNaN(resDaysSkew) && !double.IsInfinity(resDaysSkew));
        Assert.True(!double.IsNaN(resDaysKurt) && !double.IsInfinity(resDaysKurt));

        // Uphold rate skewness (more symmetric distribution expected)
        var upholdSkew = doc.GetColumnSkewness("uphold_rate_pct");
        var upholdKurt = doc.GetColumnKurtosis("uphold_rate_pct");
        Assert.True(!double.IsNaN(upholdSkew) && !double.IsInfinity(upholdSkew));
        Assert.True(!double.IsNaN(upholdKurt) && !double.IsInfinity(upholdKurt));

        // SaveToFile
        var outPath = TempFile("fca_pra_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(compSkew, loaded.GetColumnSkewness("complaints_per_1k_accounts"), precision: 6);
        Assert.Equal(compKurt, loaded.GetColumnKurtosis("complaints_per_1k_accounts"), precision: 6);
        Assert.Equal(resDaysSkew, loaded.GetColumnSkewness("resolution_days"), precision: 6);
        Assert.Equal(upholdKurt, loaded.GetColumnKurtosis("uphold_rate_pct"), precision: 6);
    }
}
