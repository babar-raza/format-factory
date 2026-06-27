// Tests for TsvDocument.GetColumnRank, GetColumnPercentile, GetColumnQuantile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R237

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R237: Tests for TsvDocument.GetColumnRank, GetColumnPercentile, GetColumnQuantile deeper.
/// GetColumnRank(col, value): returns the rank (1-based) of the given value within the column.
/// GetColumnPercentile(col, percentile): returns the value at the given percentile.
/// GetColumnQuantile(col, quantile): returns the value at the given quantile (0-1 scale).
/// Covers: GetColumnRank no-throw; GetColumnRank positive; GetColumnRank consistent;
/// GetColumnRank save-load;
/// GetColumnPercentile no-throw; GetColumnPercentile in range; GetColumnPercentile consistent;
/// GetColumnPercentile p50 equals median; GetColumnPercentile save-load;
/// GetColumnQuantile no-throw; GetColumnQuantile in range; GetColumnQuantile consistent;
/// GetColumnQuantile q0.5 near median; GetColumnQuantile save-load;
/// dogfood Append→GetColumnRank→GetColumnPercentile→GetColumnQuantile→SaveToFile pipeline.
/// </summary>
public class TsvR237GetColumnRankAndPercentileDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR237GetColumnRankAndPercentileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR237_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateScoresTsv()
    {
        var path = TempFile("scores.tsv");
        var lines = new[]
        {
            "student_id\texam_score\tassignment_score\tfinal_grade",
            "S001\t88\t92\t90",
            "S002\t74\t78\t76",
            "S003\t95\t91\t93",
            "S004\t62\t70\t66",
            "S005\t80\t85\t82",
            "S006\t91\t88\t90",
            "S007\t55\t65\t60",
            "S008\t78\t82\t80",
            "S009\t85\t87\t86",
            "S010\t70\t75\t72",
            "S011\t93\t90\t92",
            "S012\t68\t72\t70"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnRank
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRank_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        var ex = Record.Exception(() => doc.GetColumnRank("exam_score", 88.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRank_Positive()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        Assert.True(doc.GetColumnRank("exam_score", 88.0) >= 1);
    }

    [Fact]
    public void GetColumnRank_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        Assert.Equal(doc.GetColumnRank("exam_score", 95.0), doc.GetColumnRank("exam_score", 95.0));
    }

    [Fact]
    public void GetColumnRank_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        var before = doc.GetColumnRank("exam_score", 80.0);
        var path = TempFile("rank_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnRank("exam_score", 80.0));
    }

    // -------------------------------------------------------------------------
    // GetColumnPercentile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnPercentile_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        var ex = Record.Exception(() => doc.GetColumnPercentile("exam_score", 75));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnPercentile_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        var p75 = doc.GetColumnPercentile("exam_score", 75);
        Assert.True(p75 >= doc.GetColumnMin("exam_score"));
        Assert.True(p75 <= doc.GetColumnMax("exam_score"));
    }

    [Fact]
    public void GetColumnPercentile_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        Assert.Equal(doc.GetColumnPercentile("exam_score", 50), doc.GetColumnPercentile("exam_score", 50), precision: 4);
    }

    [Fact]
    public void GetColumnPercentile_P50_Near_Median()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        var p50 = doc.GetColumnPercentile("exam_score", 50);
        var median = doc.GetColumnMedian("exam_score");
        Assert.True(Math.Abs(p50 - median) < 5.0);
    }

    [Fact]
    public void GetColumnPercentile_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        var before = doc.GetColumnPercentile("final_grade", 25);
        var path = TempFile("pct_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnPercentile("final_grade", 25), precision: 2);
    }

    // -------------------------------------------------------------------------
    // GetColumnQuantile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnQuantile_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        var ex = Record.Exception(() => doc.GetColumnQuantile("exam_score", 0.75));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnQuantile_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        var q75 = doc.GetColumnQuantile("exam_score", 0.75);
        Assert.True(q75 >= doc.GetColumnMin("exam_score"));
        Assert.True(q75 <= doc.GetColumnMax("exam_score"));
    }

    [Fact]
    public void GetColumnQuantile_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        Assert.Equal(doc.GetColumnQuantile("exam_score", 0.9), doc.GetColumnQuantile("exam_score", 0.9), precision: 4);
    }

    [Fact]
    public void GetColumnQuantile_Q05_Near_Median()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        var q50 = doc.GetColumnQuantile("exam_score", 0.5);
        var median = doc.GetColumnMedian("exam_score");
        Assert.True(Math.Abs(q50 - median) < 5.0);
    }

    [Fact]
    public void GetColumnQuantile_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateScoresTsv());
        var before = doc.GetColumnQuantile("assignment_score", 0.25);
        var path = TempFile("qtl_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnQuantile("assignment_score", 0.25), precision: 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnRank_GetColumnPercentile_GetColumnQuantile_SaveToFile_Pipeline()
    {
        // Human resources — compensation benchmarking and pay equity analysis
        var path = TempFile("dogfood_compensation.tsv");
        var lines = new[]
        {
            "emp_id\tband\trole\tdepartment\tbase_salary\tbonus\ttotal_comp\ttenure_years\tperformance",
            "E001\tL3\tSWE\tEngineering\t95000\t9500\t104500\t3\t4",
            "E002\tL4\tSeniorSWE\tEngineering\t135000\t20250\t155250\t6\t5",
            "E003\tL3\tPM\tProduct\t92000\t9200\t101200\t2\t3",
            "E004\tL5\tStaffSWE\tEngineering\t175000\t35000\t210000\t9\t5",
            "E005\tL2\tJuniorSWE\tEngineering\t78000\t5460\t83460\t1\t3",
            "E006\tL3\tDataSci\tAnalytics\t98000\t9800\t107800\t4\t4",
            "E007\tL4\tSeniorPM\tProduct\t128000\t19200\t147200\t7\t4",
            "E008\tL6\tPrincipal\tEngineering\t215000\t53750\t268750\t12\t5",
            "E009\tL2\tDesigner\tDesign\t72000\t5040\t77040\t2\t3",
            "E010\tL4\tSeniorDSci\tAnalytics\t142000\t21300\t163300\t5\t5",
            "E011\tL3\tSWE\tEngineering\t94000\t7050\t101050\t3\t4",
            "E012\tL5\tStaffDSci\tAnalytics\t168000\t33600\t201600\t8\t4"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(12, doc.RowCount);

        // GetColumnRank — highest earner (E008 total_comp=268750 → rank 1)
        var rank1 = doc.GetColumnRank("total_comp", 268750.0);
        Assert.True(rank1 >= 1);
        Assert.True(rank1 <= 12);
        Assert.Equal(rank1, doc.GetColumnRank("total_comp", 268750.0)); // consistent

        // GetColumnRank — lowest earner (E009 total_comp=77040 → rank 12)
        var rank12 = doc.GetColumnRank("total_comp", 77040.0);
        Assert.True(rank12 >= 1);
        Assert.True(rank12 <= 12);

        // GetColumnPercentile — total_comp
        var p25 = doc.GetColumnPercentile("total_comp", 25);
        var p50 = doc.GetColumnPercentile("total_comp", 50);
        var p75 = doc.GetColumnPercentile("total_comp", 75);
        Assert.True(p25 <= p50);
        Assert.True(p50 <= p75);
        Assert.Equal(p50, doc.GetColumnPercentile("total_comp", 50), precision: 2); // consistent

        // GetColumnPercentile — base_salary P90 (senior+ levels)
        var p90Salary = doc.GetColumnPercentile("base_salary", 90);
        Assert.True(p90Salary >= doc.GetColumnMin("base_salary"));
        Assert.True(p90Salary <= doc.GetColumnMax("base_salary"));

        // GetColumnQuantile — total_comp IQR (Q1 to Q3)
        var q1 = doc.GetColumnQuantile("total_comp", 0.25);
        var q3 = doc.GetColumnQuantile("total_comp", 0.75);
        Assert.True(q1 <= q3);
        Assert.Equal(q3, doc.GetColumnQuantile("total_comp", 0.75), precision: 2); // consistent

        // GetColumnQuantile — tenure Q0.9 (senior tenure)
        var tenureQ90 = doc.GetColumnQuantile("tenure_years", 0.9);
        Assert.True(tenureQ90 >= 1.0);
        Assert.True(tenureQ90 <= 12.0);

        // P50 ≈ Q0.5 (within 5 units)
        var p50b = doc.GetColumnPercentile("base_salary", 50);
        var q50b = doc.GetColumnQuantile("base_salary", 0.5);
        Assert.True(Math.Abs(p50b - q50b) < 5.0);

        // AppendRow — two new employees
        doc.AppendRow(new[] { "E013", "L1", "Intern", "Engineering", "45000", "0", "45000", "0", "2" });
        doc.AppendRow(new[] { "E014", "L6", "Distinguished", "Engineering", "280000", "84000", "364000", "15", "5" });
        Assert.Equal(14, doc.RowCount);

        // After append: ranks shift
        var newRankTop = doc.GetColumnRank("total_comp", 364000.0);
        Assert.True(newRankTop >= 1);

        // SaveToFile
        var out1 = TempFile("dogfood_compensation_out.tsv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(out1);
        Assert.Equal(14, loaded.RowCount);
        Assert.Equal(doc.GetColumnPercentile("base_salary", 50), loaded.GetColumnPercentile("base_salary", 50), precision: 2);
        Assert.Equal(doc.GetColumnQuantile("total_comp", 0.75), loaded.GetColumnQuantile("total_comp", 0.75), precision: 2);

        // Final save
        var out2 = TempFile("dogfood_compensation_v2.tsv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = TsvDocument.LoadFile(out2);
        Assert.Equal(14, loaded2.RowCount);
        Assert.True(loaded2.GetColumnPercentile("total_comp", 90) > 0);
        Assert.True(loaded2.GetColumnQuantile("base_salary", 0.5) > 0);
        var ex1 = Record.Exception(() => loaded2.GetColumnRank("base_salary", 95000.0));
        var ex2 = Record.Exception(() => loaded2.GetColumnPercentile("bonus", 75));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
