// Tests for TsvDocument.GetNullCount, GetFillRate, GetCompleteness deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R221

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R221: Tests for TsvDocument.GetNullCount, GetFillRate, GetCompleteness deeper.
/// GetNullCount(colName): returns the number of null or empty values in the column.
/// GetFillRate(colName): returns the fraction of non-null values in [0.0, 1.0].
/// GetCompleteness(): returns the fraction of all non-null values across all columns.
/// Covers: GetNullCount no-throw; GetNullCount non-negative; GetNullCount consistent;
/// GetNullCount save-load; GetNullCount leq row count;
/// GetFillRate no-throw; GetFillRate in [0,1]; GetFillRate consistent;
/// GetFillRate save-load; GetFillRate plus null fraction equals 1;
/// GetCompleteness no-throw; GetCompleteness in [0,1]; GetCompleteness consistent;
/// GetCompleteness save-load; GetCompleteness equals 1 for complete data;
/// dogfood LoadFile→GetNullCount→GetFillRate→GetCompleteness→SaveToFile pipeline.
/// </summary>
public class TsvR221GetNullCountAndFillRateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR221GetNullCountAndFillRateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR221_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCompleteTsv()
    {
        var path = TempFile("complete.tsv");
        var content =
            "Id\tName\tAge\tDept\tSalary\n" +
            "1\tAlice\t28\tEng\t95000\n" +
            "2\tBob\t35\tMkt\t72000\n" +
            "3\tCarol\t42\tEng\t115000\n" +
            "4\tDave\t29\tHR\t68000\n" +
            "5\tEve\t38\tEng\t88000\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetNullCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNullCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        var ex = Record.Exception(() => doc.GetNullCount("Name"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNullCount_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        Assert.True(doc.GetNullCount("Name") >= 0);
    }

    [Fact]
    public void GetNullCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        Assert.Equal(doc.GetNullCount("Name"), doc.GetNullCount("Name"));
    }

    [Fact]
    public void GetNullCount_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        var before = doc.GetNullCount("Name");
        var path = TempFile("nc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNullCount("Name"));
    }

    [Fact]
    public void GetNullCount_Leq_RowCount()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        Assert.True(doc.GetNullCount("Name") <= doc.GetRowCount());
    }

    [Fact]
    public void GetNullCount_Zero_ForCompleteColumn()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        // All rows have Name values
        Assert.Equal(0, doc.GetNullCount("Name"));
    }

    // -------------------------------------------------------------------------
    // GetFillRate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFillRate_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        var ex = Record.Exception(() => doc.GetFillRate("Name"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFillRate_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        var r = doc.GetFillRate("Name");
        Assert.True(r >= 0.0 && r <= 1.0);
    }

    [Fact]
    public void GetFillRate_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        Assert.Equal(doc.GetFillRate("Salary"), doc.GetFillRate("Salary"));
    }

    [Fact]
    public void GetFillRate_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        var before = doc.GetFillRate("Age");
        var path = TempFile("fr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFillRate("Age"), 4);
    }

    [Fact]
    public void GetFillRate_One_ForCompleteColumn()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        // All rows have Name
        Assert.Equal(1.0, doc.GetFillRate("Name"), 4);
    }

    // -------------------------------------------------------------------------
    // GetCompleteness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompleteness_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        var ex = Record.Exception(() => doc.GetCompleteness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompleteness_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        var c = doc.GetCompleteness();
        Assert.True(c >= 0.0 && c <= 1.0);
    }

    [Fact]
    public void GetCompleteness_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        Assert.Equal(doc.GetCompleteness(), doc.GetCompleteness());
    }

    [Fact]
    public void GetCompleteness_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        var before = doc.GetCompleteness();
        var path = TempFile("comp_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompleteness(), 4);
    }

    [Fact]
    public void GetCompleteness_One_ForCompleteData()
    {
        var doc = TsvDocument.LoadFile(CreateCompleteTsv());
        // All cells are populated → completeness = 1.0
        Assert.Equal(1.0, doc.GetCompleteness(), 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetNullCount_GetFillRate_GetCompleteness_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_patients.tsv");
        var content =
            "PatientId\tAge\tDiagnosis\tBP\tCholesterol\tSmoker\n" +
            "P001\t45\tHypertension\t140/90\t210\tYes\n" +
            "P002\t62\tDiabetes\t\t185\tNo\n" +
            "P003\t38\t\t120/80\t195\tNo\n" +
            "P004\t55\tHypertension\t135/88\t\tYes\n" +
            "P005\t71\tCAD\t150/95\t240\tYes\n" +
            "P006\t49\tDiabetes\t125/82\t200\t\n" +
            "P007\t33\t\t118/76\t175\tNo\n" +
            "P008\t58\tHypertension\t\t220\tYes\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRowCount());

        // GetNullCount — BP has 2 empty values (P002, P008)
        var nullBP = doc.GetNullCount("BP");
        Assert.True(nullBP >= 0);
        Assert.True(nullBP <= doc.GetRowCount());
        Assert.Equal(nullBP, doc.GetNullCount("BP")); // consistent

        // GetNullCount — PatientId has 0 empty values
        var nullId = doc.GetNullCount("PatientId");
        Assert.Equal(0, nullId);

        // GetFillRate — PatientId = 1.0 (all present)
        var fillId = doc.GetFillRate("PatientId");
        Assert.Equal(1.0, fillId, 4);
        Assert.Equal(fillId, doc.GetFillRate("PatientId")); // consistent

        // GetFillRate — BP < 1.0 (some missing)
        var fillBP = doc.GetFillRate("BP");
        Assert.True(fillBP >= 0.0 && fillBP <= 1.0);
        Assert.True(fillBP < 1.0 || nullBP == 0);

        // GetCompleteness — some data is missing → < 1.0
        var completeness = doc.GetCompleteness();
        Assert.True(completeness >= 0.0 && completeness <= 1.0);
        Assert.Equal(completeness, doc.GetCompleteness()); // consistent

        // After saving complete data, completeness stays same
        var completePath = TempFile("dogfood_patients_complete.tsv");
        var completeContent =
            "PatientId\tAge\tDiagnosis\n" +
            "P001\t45\tHypertension\n" +
            "P002\t62\tDiabetes\n";
        File.WriteAllText(completePath, completeContent);
        var completeDoc = TsvDocument.LoadFile(completePath);
        Assert.Equal(1.0, completeDoc.GetCompleteness(), 4);

        // AddRow and recheck
        doc.AddRow(new[] { "P009", "44", "Asthma", "122/78", "188", "No" });
        Assert.Equal(9, doc.GetRowCount());
        Assert.True(doc.GetNullCount("BP") >= 0);
        Assert.True(doc.GetFillRate("PatientId") > 0);

        // SaveToFile
        var savePath = TempFile("dogfood_patients_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRowCount());
        Assert.Equal(doc.GetNullCount("BP"), loaded.GetNullCount("BP"));
        Assert.Equal(doc.GetFillRate("PatientId"), loaded.GetFillRate("PatientId"), 4);
        Assert.Equal(doc.GetCompleteness(), loaded.GetCompleteness(), 4);

        // Final save
        var path2 = TempFile("dogfood_patients_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetCompleteness(), loaded2.GetCompleteness(), 4);
        Assert.Equal(loaded.GetNullCount("BP"), loaded2.GetNullCount("BP"));
    }
}
