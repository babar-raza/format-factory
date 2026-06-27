// Tests for CsvDocument.GetColumnFirstQuartile, GetColumnThirdQuartile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R273

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R273: Tests for CsvDocument.GetColumnFirstQuartile, GetColumnThirdQuartile deeper.
/// GetColumnFirstQuartile(colName): returns the first quartile (Q1, 25th percentile) of numeric values.
/// GetColumnThirdQuartile(colName): returns the third quartile (Q3, 75th percentile) of numeric values.
/// Covers: GetColumnFirstQuartile no-throw; GetColumnFirstQuartile in-range;
/// GetColumnFirstQuartile equal for uniform; GetColumnFirstQuartile consistent;
/// GetColumnFirstQuartile save-load;
/// GetColumnThirdQuartile no-throw; GetColumnThirdQuartile in-range;
/// GetColumnThirdQuartile equal for uniform; GetColumnThirdQuartile consistent;
/// GetColumnThirdQuartile save-load;
/// GetColumnFirstQuartile leq GetColumnThirdQuartile; dogfood pipeline.
/// </summary>
public class CsvR273GetColumnFirstQuartileAndThirdQuartileDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR273GetColumnFirstQuartileAndThirdQuartileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR273_" + Guid.NewGuid().ToString("N"));
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
        for (int i = 0; i <= 11; i++) sb.AppendLine($"R{i:D2},{i * 10.0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,measure");
        for (int i = 0; i < 20; i++) sb.AppendLine($"R{i:D2},55.0");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnFirstQuartile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnFirstQuartile_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnFirstQuartile("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnFirstQuartile_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var q1 = doc.GetColumnFirstQuartile("value");
        Assert.True(q1 >= doc.GetColumnMin("value") && q1 <= doc.GetColumnMax("value"));
    }

    [Fact]
    public void GetColumnFirstQuartile_Equal_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(55.0, doc.GetColumnFirstQuartile("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnFirstQuartile_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnFirstQuartile("value"), doc.GetColumnFirstQuartile("value"));
    }

    [Fact]
    public void GetColumnFirstQuartile_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnFirstQuartile("value");
        var path = TempFile("q1_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnFirstQuartile("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnThirdQuartile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnThirdQuartile_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnThirdQuartile("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnThirdQuartile_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var q3 = doc.GetColumnThirdQuartile("value");
        Assert.True(q3 >= doc.GetColumnMin("value") && q3 <= doc.GetColumnMax("value"));
    }

    [Fact]
    public void GetColumnThirdQuartile_Equal_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(55.0, doc.GetColumnThirdQuartile("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnThirdQuartile_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnThirdQuartile("value"), doc.GetColumnThirdQuartile("value"));
    }

    [Fact]
    public void GetColumnThirdQuartile_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnThirdQuartile("value");
        var path = TempFile("q3_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnThirdQuartile("value"), precision: 6);
    }

    [Fact]
    public void GetColumnFirstQuartile_Leq_GetColumnThirdQuartile()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnFirstQuartile("value") <= doc.GetColumnThirdQuartile("value"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnFirstQuartile_GetColumnThirdQuartile_Pipeline()
    {
        // Education — Ofqual / DfE: A-Level Grade Distributions by Subject 2024
        // Candidate marks and grade boundaries across subjects and awarding organisations
        // Q1/Q3 quantify mark spread and inform grade boundary setting methodology

        var path = TempFile("ofqual_alevel_2024.csv");
        var sb = new StringBuilder();
        sb.AppendLine("candidate_id,subject,awarding_body,raw_mark,scaled_mark,grade_boundary_a,grade_boundary_e,ums_score,resit");

        var rng = new Random(20240815);
        string[] subjects = {
            "Mathematics", "Further_Maths", "Biology", "Chemistry", "Physics",
            "English_Lit", "History", "Economics", "Psychology", "Computer_Science"
        };
        string[] bodies = { "AQA", "Edexcel", "OCR", "WJEC", "CCEA" };

        // Raw mark maxima per subject (out of different totals)
        int[] rawMax = { 300, 300, 270, 270, 300, 240, 240, 240, 210, 270 };
        double[] meanPct = { 0.62, 0.58, 0.60, 0.57, 0.55, 0.65, 0.63, 0.61, 0.64, 0.59 };

        for (int i = 0; i < 450; i++)
        {
            int subjIdx = rng.Next(subjects.Length);
            int maxMark = rawMax[subjIdx];
            double mean = meanPct[subjIdx] * maxMark;
            double raw = Math.Max(0, Math.Min(maxMark, mean + (rng.NextDouble() - 0.5) * maxMark * 0.45));
            double scaled = raw * (300.0 / maxMark) * (0.95 + 0.1 * rng.NextDouble());
            scaled = Math.Max(0, Math.Min(300, scaled));
            int boundA = (int)(maxMark * 0.75);
            int boundE = (int)(maxMark * 0.40);
            double ums = Math.Min(600, raw / maxMark * 600 * (0.9 + 0.2 * rng.NextDouble()));
            bool resit = rng.NextDouble() < 0.12;
            sb.AppendLine($"CND{i:D5},{subjects[subjIdx]},{bodies[rng.Next(bodies.Length)]},{raw:F1},{scaled:F1},{boundA},{boundE},{ums:F0},{(resit ? 1 : 0)}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(450, doc.RowCount);
        Assert.Equal(9, doc.ColumnCount);

        // Raw mark quartiles
        var rawQ1 = doc.GetColumnFirstQuartile("raw_mark");
        var rawQ3 = doc.GetColumnThirdQuartile("raw_mark");
        Assert.True(rawQ1 >= doc.GetColumnMin("raw_mark"));
        Assert.True(rawQ3 <= doc.GetColumnMax("raw_mark"));
        Assert.True(rawQ1 <= rawQ3);
        Assert.Equal(rawQ1, doc.GetColumnFirstQuartile("raw_mark")); // consistent
        Assert.Equal(rawQ3, doc.GetColumnThirdQuartile("raw_mark")); // consistent

        // UMS score quartiles
        var umsQ1 = doc.GetColumnFirstQuartile("ums_score");
        var umsQ3 = doc.GetColumnThirdQuartile("ums_score");
        Assert.True(umsQ1 >= 0.0);
        Assert.True(umsQ3 <= 600.0);
        Assert.True(umsQ1 <= umsQ3);

        // Scaled mark quartiles
        var scaledQ1 = doc.GetColumnFirstQuartile("scaled_mark");
        var scaledQ3 = doc.GetColumnThirdQuartile("scaled_mark");
        Assert.True(scaledQ1 >= 0.0);
        Assert.True(scaledQ1 <= scaledQ3);

        // IQR non-negative
        Assert.True((rawQ3 - rawQ1) >= 0.0);
        Assert.True((umsQ3 - umsQ1) >= 0.0);

        // SaveToFile
        var outPath = TempFile("ofqual_alevel_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(rawQ1, loaded.GetColumnFirstQuartile("raw_mark"), precision: 6);
        Assert.Equal(rawQ3, loaded.GetColumnThirdQuartile("raw_mark"), precision: 6);
        Assert.Equal(umsQ1, loaded.GetColumnFirstQuartile("ums_score"), precision: 6);
        Assert.Equal(umsQ3, loaded.GetColumnThirdQuartile("ums_score"), precision: 6);
        Assert.Equal(scaledQ1, loaded.GetColumnFirstQuartile("scaled_mark"), precision: 6);
    }
}
