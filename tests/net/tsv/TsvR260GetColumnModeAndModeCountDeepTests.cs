// Tests for TsvDocument.GetColumnMode, GetColumnModeCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R260

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R260: Tests for TsvDocument.GetColumnMode, GetColumnModeCount deeper.
/// GetColumnMode(colName): returns the most frequently occurring value in the column.
/// GetColumnModeCount(colName): returns the count of occurrences of the mode value.
/// Covers: GetColumnMode no-throw; GetColumnMode non-null; GetColumnMode consistent;
/// GetColumnMode known value; GetColumnMode save-load;
/// GetColumnModeCount no-throw; GetColumnModeCount positive; GetColumnModeCount consistent;
/// GetColumnModeCount save-load; GetColumnModeCount >= 1; GetColumnMode constant column;
/// GetColumnModeCount equals RowCount for constant;
/// dogfood CreateDoc→GetColumnMode→GetColumnModeCount pipeline.
/// </summary>
public class TsvR260GetColumnModeAndModeCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR260GetColumnModeAndModeCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR260_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id\tcategory\tregion\tscore");
        var rng = new Random(20240901);
        string[] categories = { "A", "A", "A", "B", "C" }; // A dominates
        string[] regions = { "North", "South", "East", "West" };
        for (int i = 0; i < 100; i++)
        {
            string cat = categories[rng.Next(categories.Length)];
            string region = regions[rng.Next(regions.Length)];
            int score = rng.Next(100);
            sb.AppendLine($"{i}\t{cat}\t{region}\t{score}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateKnownTsv()
    {
        var path = TempFile("known.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tcolour");
        // Inject: Red=5, Blue=8, Green=3 — Blue is mode
        string[] items = { "Red", "Blue", "Green", "Red", "Blue", "Blue", "Red", "Blue", "Green", "Red", "Blue", "Red", "Blue", "Blue", "Green" };
        for (int i = 0; i < items.Length; i++)
            sb.AppendLine($"{i}\t{items[i]}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantTsv()
    {
        var path = TempFile("constant.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tstatus");
        for (int i = 0; i < 30; i++)
            sb.AppendLine($"{i}\tActive");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMode_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnMode("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMode_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetColumnMode("category"));
    }

    [Fact]
    public void GetColumnMode_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnMode("category"), doc.GetColumnMode("category"));
    }

    [Fact]
    public void GetColumnMode_Known_Value()
    {
        var doc = TsvDocument.LoadFile(CreateKnownTsv());
        Assert.Equal("Blue", doc.GetColumnMode("colour"));
    }

    [Fact]
    public void GetColumnMode_Constant_Column()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal("Active", doc.GetColumnMode("status"));
    }

    [Fact]
    public void GetColumnMode_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnMode("category");
        var path = TempFile("mode_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMode("category"));
    }

    // -------------------------------------------------------------------------
    // GetColumnModeCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnModeCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnModeCount("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnModeCount_Positive()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnModeCount("category") >= 1);
    }

    [Fact]
    public void GetColumnModeCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnModeCount("region"), doc.GetColumnModeCount("region"));
    }

    [Fact]
    public void GetColumnModeCount_Known_Value()
    {
        var doc = TsvDocument.LoadFile(CreateKnownTsv());
        // Blue appears 8 times in 15 items
        Assert.Equal(8, doc.GetColumnModeCount("colour"));
    }

    [Fact]
    public void GetColumnModeCount_Equals_RowCount_ForConstant()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(doc.RowCount, doc.GetColumnModeCount("status"));
    }

    [Fact]
    public void GetColumnModeCount_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnModeCount("category");
        var path = TempFile("mc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnModeCount("category"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMode_GetColumnModeCount_Pipeline()
    {
        // Social policy — UK Department for Work and Pensions (DWP) Universal Credit caseload
        // Claimant characteristic data: most common reason for claim, employment status, region
        var path = TempFile("dwp_uc_caseload.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("claimant_ref\tregion\temp_status\tclaim_reason\tcomponent\tweekly_award_gbp\tduration_weeks");

        var rng = new Random(20241101);
        string[] regions = { "London", "South East", "North West", "Yorkshire", "Midlands",
                              "Wales", "Scotland", "North East", "South West", "East Anglia" };
        // Employment status: out of work dominates
        string[] empStatuses = {
            "Unemployed", "Unemployed", "Unemployed", "Unemployed", "Unemployed",
            "Part-time", "Part-time", "Self-employed", "Sick/Disabled", "Carer"
        };
        // Claim reason: job loss is most common
        string[] claimReasons = {
            "Job loss", "Job loss", "Job loss", "Job loss", "Job loss", "Job loss",
            "Insufficient hours", "Insufficient hours", "Health condition",
            "Relationship breakdown", "Left education"
        };
        string[] components = { "Standard Allowance", "Standard Allowance", "Standard Allowance",
                                 "Housing", "Child", "Disabled Child", "Carer" };

        for (int i = 0; i < 200; i++)
        {
            string ref_ = $"UC{i + 1:D7}";
            string region = regions[rng.Next(regions.Length)];
            string empStatus = empStatuses[rng.Next(empStatuses.Length)];
            string reason = claimReasons[rng.Next(claimReasons.Length)];
            string component = components[rng.Next(components.Length)];
            double award = 80 + rng.NextDouble() * 520;
            int duration = 1 + rng.Next(104);
            sb.AppendLine($"{ref_}\t{region}\t{empStatus}\t{reason}\t{component}\t{award:F2}\t{duration}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(7, doc.ColumnCount);

        // GetColumnMode — emp_status: Unemployed dominates
        var modeEmpStatus = doc.GetColumnMode("emp_status");
        Assert.NotNull(modeEmpStatus);
        Assert.Equal("Unemployed", modeEmpStatus);
        Assert.Equal(modeEmpStatus, doc.GetColumnMode("emp_status")); // consistent

        // GetColumnModeCount — Unemployed count
        var mcEmpStatus = doc.GetColumnModeCount("emp_status");
        Assert.True(mcEmpStatus >= 1);
        Assert.Equal(mcEmpStatus, doc.GetColumnModeCount("emp_status")); // consistent
        // Mode count ≤ row count
        Assert.True(mcEmpStatus <= doc.RowCount);

        // GetColumnMode — claim_reason: Job loss dominates
        var modeReason = doc.GetColumnMode("claim_reason");
        Assert.Equal("Job loss", modeReason);

        var mcReason = doc.GetColumnModeCount("claim_reason");
        Assert.True(mcReason >= 1);
        Assert.True(mcReason > doc.GetColumnModeCount("component")); // job loss should be most common

        // GetColumnMode — component: Standard Allowance dominates
        var modeComponent = doc.GetColumnMode("component");
        Assert.Equal("Standard Allowance", modeComponent);

        var mcComponent = doc.GetColumnModeCount("component");
        Assert.True(mcComponent >= 1);

        // Regions: 10 roughly equal → mode count lower than emp_status
        var modeRegion = doc.GetColumnMode("region");
        Assert.NotNull(modeRegion);
        var mcRegion = doc.GetColumnModeCount("region");
        Assert.True(mcRegion >= 1);
        // No single region dominates like Unemployed does
        Assert.True(mcEmpStatus >= mcRegion);

        // SaveToFile
        var outPath = TempFile("dwp_uc_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(modeEmpStatus, loaded.GetColumnMode("emp_status"));
        Assert.Equal(mcEmpStatus, loaded.GetColumnModeCount("emp_status"));
        Assert.Equal(modeReason, loaded.GetColumnMode("claim_reason"));

        // Constant column test
        var path2 = TempFile("constant_uc.tsv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("ref\tscheme");
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"UC{i}\tUniversal Credit");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = TsvDocument.LoadFile(path2);
        Assert.Equal("Universal Credit", doc2.GetColumnMode("scheme"));
        Assert.Equal(50, doc2.GetColumnModeCount("scheme"));
    }
}
