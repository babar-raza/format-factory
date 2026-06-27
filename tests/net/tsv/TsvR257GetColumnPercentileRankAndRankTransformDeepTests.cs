// Tests for TsvDocument.GetColumnPercentileRank, GetColumnRankTransform deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R257

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R257: Tests for TsvDocument.GetColumnPercentileRank, GetColumnRankTransform deeper.
/// GetColumnPercentileRank(colName, value): returns the percentile rank (0-100) of the given value.
/// GetColumnRankTransform(colName): returns an array of per-row rank values (1-based).
/// Covers: GetColumnPercentileRank no-throw; GetColumnPercentileRank in [0,100];
/// GetColumnPercentileRank consistent; GetColumnPercentileRank min = 0; GetColumnPercentileRank save-load;
/// GetColumnRankTransform no-throw; GetColumnRankTransform non-null;
/// GetColumnRankTransform length equals RowCount; GetColumnRankTransform contains 1;
/// GetColumnRankTransform consistent; GetColumnRankTransform save-load;
/// dogfood CreateDoc→GetColumnPercentileRank→GetColumnRankTransform pipeline.
/// </summary>
public class TsvR257GetColumnPercentileRankAndRankTransformDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR257GetColumnPercentileRankAndRankTransformDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR257_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("student_id\texam_score\tcoursework\tattendance_pct");
        var rng = new Random(20240901);
        for (int i = 0; i < 100; i++)
        {
            double exam = 30 + rng.NextDouble() * 70;
            double cw = 40 + rng.NextDouble() * 60;
            double att = 50 + rng.NextDouble() * 50;
            sb.AppendLine($"S{i:D4}\t{exam:F1}\t{cw:F1}\t{att:F0}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnPercentileRank
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnPercentileRank_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var min = doc.GetColumnMin("exam_score");
        var ex = Record.Exception(() => doc.GetColumnPercentileRank("exam_score", min));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnPercentileRank_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var median = doc.GetColumnMedian("exam_score");
        var pr = doc.GetColumnPercentileRank("exam_score", median);
        Assert.True(pr >= 0.0 && pr <= 100.0);
    }

    [Fact]
    public void GetColumnPercentileRank_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var val = doc.GetColumnMean("exam_score");
        Assert.Equal(doc.GetColumnPercentileRank("exam_score", val),
                     doc.GetColumnPercentileRank("exam_score", val));
    }

    [Fact]
    public void GetColumnPercentileRank_Min_IsZeroOrSmall()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var min = doc.GetColumnMin("exam_score");
        // Minimum value should have very low (near 0) percentile rank
        Assert.True(doc.GetColumnPercentileRank("exam_score", min - 1) <= 5.0);
    }

    [Fact]
    public void GetColumnPercentileRank_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var val = doc.GetColumnMean("coursework");
        var before = doc.GetColumnPercentileRank("coursework", val);
        var path = TempFile("pr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnPercentileRank("coursework", val), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnRankTransform
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRankTransform_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnRankTransform("exam_score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRankTransform_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetColumnRankTransform("exam_score"));
    }

    [Fact]
    public void GetColumnRankTransform_LengthEqualsRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.RowCount, doc.GetColumnRankTransform("exam_score").Length);
    }

    [Fact]
    public void GetColumnRankTransform_ContainsOne()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ranks = doc.GetColumnRankTransform("exam_score");
        bool hasOne = false;
        foreach (var r in ranks) if (r == 1) { hasOne = true; break; }
        Assert.True(hasOne);
    }

    [Fact]
    public void GetColumnRankTransform_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var r1 = doc.GetColumnRankTransform("coursework");
        var r2 = doc.GetColumnRankTransform("coursework");
        Assert.Equal(r1.Length, r2.Length);
        for (int i = 0; i < r1.Length; i++)
            Assert.Equal(r1[i], r2[i]);
    }

    [Fact]
    public void GetColumnRankTransform_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnRankTransform("exam_score");
        var path = TempFile("rt_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetColumnRankTransform("exam_score");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnPercentileRank_GetColumnRankTransform_Pipeline()
    {
        // Education — Ofqual A-Level Results Data 2024
        // National percentile ranking and grade boundary analysis across subjects
        var path = TempFile("ofqual_alevel.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("school_code\tsubject\tgender\tuas\traw_mark\tpredicted_grade\tactual_grade\tvalue_added_score\tpopulation_estimate");

        var rng = new Random(20240815);
        string[] subjects = { "Mathematics", "Chemistry", "Physics", "Biology", "Economics",
                               "History", "English Literature", "Psychology", "Computer Science", "Further Mathematics" };
        string[] grades = { "A*", "A", "B", "C", "D", "E", "U" };
        double[] gradeWeights = { 0.08, 0.25, 0.28, 0.22, 0.10, 0.05, 0.02 };
        string[] genders = { "M", "F" };

        for (int i = 0; i < 200; i++)
        {
            string school = $"SCH{1000 + rng.Next(500):D4}";
            string subject = subjects[rng.Next(subjects.Length)];
            string gender = genders[i % 2];

            // UAS (Uniform Assessment Score) 0-300
            int uas = rng.Next(50, 300);
            int rawMark = (int)(uas / 300.0 * 300 * (0.8 + rng.NextDouble() * 0.4));
            rawMark = Math.Min(300, rawMark);

            // Predicted grade based on UAS
            double r = rng.NextDouble();
            int gradeIdx = uas >= 270 ? 0 : uas >= 240 ? 1 : uas >= 210 ? 2 : uas >= 180 ? 3 : uas >= 150 ? 4 : uas >= 120 ? 5 : 6;
            gradeIdx = Math.Max(0, Math.Min(6, gradeIdx + (rng.NextDouble() < 0.7 ? 0 : (rng.NextDouble() < 0.5 ? 1 : -1))));
            string predictedGrade = grades[Math.Max(0, gradeIdx + (rng.NextDouble() < 0.15 ? 1 : 0))];
            string actualGrade = grades[gradeIdx];

            double va = -2.0 + rng.NextDouble() * 4.0; // value added score
            int popEst = 15000 + rng.Next(35000);

            sb.AppendLine($"{school}\t{subject}\t{gender}\t{uas}\t{rawMark}\t{predictedGrade}\t{actualGrade}\t{va:F3}\t{popEst}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(9, doc.ColumnCount);

        // GetColumnPercentileRank — UAS
        var prMin = doc.GetColumnPercentileRank("uas", doc.GetColumnMin("uas") - 1);
        Assert.True(prMin >= 0.0 && prMin <= 100.0);

        var prMedian = doc.GetColumnPercentileRank("uas", doc.GetColumnMedian("uas"));
        Assert.True(prMedian >= 0.0 && prMedian <= 100.0);
        // Median is around the 50th percentile
        Assert.True(prMedian >= 30.0 && prMedian <= 70.0);

        var prMax = doc.GetColumnPercentileRank("uas", doc.GetColumnMax("uas"));
        Assert.True(prMax >= 90.0 && prMax <= 100.0);

        // Consistent
        Assert.Equal(prMedian, doc.GetColumnPercentileRank("uas", doc.GetColumnMedian("uas")));

        // Value added score percentile
        var prVaPositive = doc.GetColumnPercentileRank("value_added_score", 0.5);
        Assert.True(prVaPositive >= 0.0 && prVaPositive <= 100.0);

        // Raw mark percentile
        var prRawMark = doc.GetColumnPercentileRank("raw_mark", 200);
        Assert.True(prRawMark >= 0.0 && prRawMark <= 100.0);

        // GetColumnRankTransform — UAS ranks
        var ranksUas = doc.GetColumnRankTransform("uas");
        Assert.NotNull(ranksUas);
        Assert.Equal(200, ranksUas.Length);

        // Must contain rank 1 (highest UAS)
        bool hasRankOne = false;
        foreach (var rk in ranksUas) if (rk == 1) { hasRankOne = true; break; }
        Assert.True(hasRankOne);

        // All ranks positive
        foreach (var rk in ranksUas)
            Assert.True(rk >= 1);

        // Consistent
        var ranksUas2 = doc.GetColumnRankTransform("uas");
        for (int i = 0; i < ranksUas.Length; i++)
            Assert.Equal(ranksUas[i], ranksUas2[i]);

        // Value added ranks
        var ranksVa = doc.GetColumnRankTransform("value_added_score");
        Assert.Equal(200, ranksVa.Length);

        // Basic stats
        Assert.True(doc.GetColumnMean("uas") > 0);
        Assert.True(doc.GetColumnMin("uas") <= doc.GetColumnMax("uas"));

        // SaveToFile
        var outPath = TempFile("ofqual_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(200, loaded.RowCount);
        Assert.Equal(prMedian, loaded.GetColumnPercentileRank("uas", doc.GetColumnMedian("uas")), precision: 4);
        var loadedRanks = loaded.GetColumnRankTransform("uas");
        Assert.Equal(ranksUas.Length, loadedRanks.Length);
        for (int i = 0; i < ranksUas.Length; i++)
            Assert.Equal(ranksUas[i], loadedRanks[i]);
    }
}
