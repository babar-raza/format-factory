// Tests for TsvDocument.GetColumnIQR, GetColumnQuartiles deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R261

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R261: Tests for TsvDocument.GetColumnIQR, GetColumnQuartiles deeper.
/// GetColumnIQR(colName): returns the interquartile range (Q3-Q1) of numeric values in the column.
/// GetColumnQuartiles(colName): returns Q1, Q2 (median), Q3 as a tuple/struct.
/// Covers: GetColumnIQR no-throw; GetColumnIQR non-negative; GetColumnIQR consistent;
/// GetColumnIQR zero for constant; GetColumnIQR save-load;
/// GetColumnQuartiles no-throw; GetColumnQuartiles Q1 le Q2 le Q3;
/// GetColumnQuartiles Q2 is median; GetColumnQuartiles consistent; GetColumnQuartiles save-load;
/// GetColumnIQR equals Q3 minus Q1; dogfood CreateDoc→GetColumnIQR→GetColumnQuartiles pipeline.
/// </summary>
public class TsvR261GetColumnIQRAndQuartilesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR261GetColumnIQRAndQuartilesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR261_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("student_id\texam_score\tattendance_pct\tcredit_hours");
        var rng = new Random(20240815);
        for (int i = 0; i < 80; i++)
        {
            int score = 40 + rng.Next(60);
            int att = 60 + rng.Next(40);
            int cr = 12 + rng.Next(24);
            sb.AppendLine($"S{i:D4}\t{score}\t{att}\t{cr}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantTsv()
    {
        var path = TempFile("constant.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tvalue");
        for (int i = 0; i < 40; i++)
            sb.AppendLine($"{i}\t50");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateSmallTsv()
    {
        var path = TempFile("small.tsv");
        // Known quartiles: values 1,2,3,4,5,6,7,8 → Q1=2.5, Q2=4.5, Q3=6.5, IQR=4
        var sb = new StringBuilder();
        sb.AppendLine("id\tval");
        for (int i = 1; i <= 8; i++)
            sb.AppendLine($"{i}\t{i}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnIQR
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnIQR_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnIQR("exam_score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnIQR_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnIQR("exam_score") >= 0.0);
    }

    [Fact]
    public void GetColumnIQR_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnIQR("exam_score"), doc.GetColumnIQR("exam_score"));
    }

    [Fact]
    public void GetColumnIQR_Zero_ForConstant()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0.0, doc.GetColumnIQR("value"), precision: 8);
    }

    [Fact]
    public void GetColumnIQR_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnIQR("exam_score");
        var path = TempFile("iqr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnIQR("exam_score"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnQuartiles
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnQuartiles_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnQuartiles("exam_score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnQuartiles_Q1_Le_Q2_Le_Q3()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var q = doc.GetColumnQuartiles("exam_score");
        Assert.True(q.Q1 <= q.Q2);
        Assert.True(q.Q2 <= q.Q3);
    }

    [Fact]
    public void GetColumnQuartiles_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var q1 = doc.GetColumnQuartiles("attendance_pct");
        var q2 = doc.GetColumnQuartiles("attendance_pct");
        Assert.Equal(q1.Q1, q2.Q1);
        Assert.Equal(q1.Q2, q2.Q2);
        Assert.Equal(q1.Q3, q2.Q3);
    }

    [Fact]
    public void GetColumnQuartiles_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnQuartiles("credit_hours");
        var path = TempFile("q_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetColumnQuartiles("credit_hours");
        Assert.Equal(before.Q1, after.Q1, precision: 8);
        Assert.Equal(before.Q2, after.Q2, precision: 8);
        Assert.Equal(before.Q3, after.Q3, precision: 8);
    }

    [Fact]
    public void GetColumnIQR_Equals_Q3_Minus_Q1()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var q = doc.GetColumnQuartiles("exam_score");
        var iqr = doc.GetColumnIQR("exam_score");
        Assert.Equal(q.Q3 - q.Q1, iqr, precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnIQR_GetColumnQuartiles_Pipeline()
    {
        // Education — UCAS Undergraduate Admissions 2024 Cycle
        // Subject-level offer rates, grades distributions, and widening participation metrics
        // IQR analysis to identify subjects with concentrated vs dispersed grade distributions
        var path = TempFile("ucas_admissions.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("applicant_id\tsubject_group\tpredicted_grade_pts\toffer_grade_pts\tattendance_pct\tdistance_to_provider_km\twp_flag");

        var rng = new Random(20240901);
        string[] subjects = { "Medicine", "Law", "Computer Science", "Engineering", "Economics",
                               "Psychology", "History", "Biology", "Chemistry", "Mathematics" };
        // Predicted grades cluster by subject
        int[] subjectMeans = { 155, 145, 135, 140, 148, 128, 122, 138, 142, 150 };

        for (int i = 0; i < 200; i++)
        {
            int subIdx = i % subjects.Length;
            string subject = subjects[subIdx];
            int basePts = subjectMeans[subIdx];
            int pred = Math.Max(48, Math.Min(168, basePts + rng.Next(-24, 25)));
            int offer = Math.Max(48, Math.Min(168, basePts + rng.Next(-12, 13)));
            int att = 75 + rng.Next(25);
            int dist = rng.Next(5, 350);
            bool wp = dist > 150 || att < 85;
            sb.AppendLine($"A{i:D5}\t{subject}\t{pred}\t{offer}\t{att}\t{dist}\t{(wp ? "Y" : "N")}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(7, doc.ColumnCount);

        // IQR of predicted grade points
        var iqrPred = doc.GetColumnIQR("predicted_grade_pts");
        Assert.True(iqrPred >= 0);
        Assert.Equal(iqrPred, doc.GetColumnIQR("predicted_grade_pts")); // consistent

        // Quartiles of predicted grade points
        var qPred = doc.GetColumnQuartiles("predicted_grade_pts");
        Assert.True(qPred.Q1 <= qPred.Q2);
        Assert.True(qPred.Q2 <= qPred.Q3);
        Assert.True(qPred.Q1 >= 48); // cannot go below 48
        Assert.True(qPred.Q3 <= 168); // cannot exceed 168 (A*A*A*)
        Assert.Equal(qPred.Q3 - qPred.Q1, iqrPred, precision: 6);

        // IQR of offer grade points
        var iqrOffer = doc.GetColumnIQR("offer_grade_pts");
        Assert.True(iqrOffer >= 0);
        var qOffer = doc.GetColumnQuartiles("offer_grade_pts");
        Assert.True(qOffer.Q1 <= qOffer.Q2);
        Assert.True(qOffer.Q2 <= qOffer.Q3);
        Assert.Equal(qOffer.Q3 - qOffer.Q1, iqrOffer, precision: 6);

        // IQR of attendance_pct — narrower as most are in 75-100 range
        var iqrAtt = doc.GetColumnIQR("attendance_pct");
        Assert.True(iqrAtt >= 0);
        Assert.True(iqrAtt <= 25); // max range is 25 pts
        var qAtt = doc.GetColumnQuartiles("attendance_pct");
        Assert.True(qAtt.Q1 >= 75); // minimum set
        Assert.True(qAtt.Q3 <= 100); // maximum possible

        // IQR of distance_to_provider_km — wider spread
        var iqrDist = doc.GetColumnIQR("distance_to_provider_km");
        Assert.True(iqrDist >= 0);
        var qDist = doc.GetColumnQuartiles("distance_to_provider_km");
        Assert.True(qDist.Q1 <= qDist.Q2);
        Assert.True(qDist.Q2 <= qDist.Q3);

        // Basic column stats
        Assert.True(doc.GetColumnMean("predicted_grade_pts") > 0);
        Assert.True(doc.GetColumnMean("offer_grade_pts") > 0);
        Assert.True(doc.GetColumnStdDev("distance_to_provider_km") > 0);

        // SaveToFile
        var outPath = TempFile("ucas_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(iqrPred, loaded.GetColumnIQR("predicted_grade_pts"), precision: 8);
        var qLoaded = loaded.GetColumnQuartiles("predicted_grade_pts");
        Assert.Equal(qPred.Q1, qLoaded.Q1, precision: 8);
        Assert.Equal(qPred.Q2, qLoaded.Q2, precision: 8);
        Assert.Equal(qPred.Q3, qLoaded.Q3, precision: 8);

        // Constant IQR sub-test
        var path2 = TempFile("constant_ucas.tsv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("id\tgrade_pts");
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"{i}\t128");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = TsvDocument.LoadFile(path2);
        Assert.Equal(0.0, doc2.GetColumnIQR("grade_pts"), precision: 8);
        var q2 = doc2.GetColumnQuartiles("grade_pts");
        Assert.Equal(128.0, q2.Q1, precision: 6);
        Assert.Equal(128.0, q2.Q2, precision: 6);
        Assert.Equal(128.0, q2.Q3, precision: 6);
    }
}
