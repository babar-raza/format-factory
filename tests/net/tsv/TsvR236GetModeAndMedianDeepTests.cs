// Tests for TsvDocument.GetColumnMode, GetColumnMedian, GetColumnTrimmedMean deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R236

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R236: Tests for TsvDocument.GetColumnMode, GetColumnMedian, GetColumnTrimmedMean deeper.
/// GetColumnMode(col): returns the most frequently occurring value in the column.
/// GetColumnMedian(col): returns the median value of a numeric column.
/// GetColumnTrimmedMean(col, trimFraction): returns the mean after trimming extreme values.
/// Covers: GetColumnMode no-throw; GetColumnMode non-null; GetColumnMode consistent;
/// GetColumnMode correct for known data; GetColumnMode save-load;
/// GetColumnMedian no-throw; GetColumnMedian in range; GetColumnMedian consistent;
/// GetColumnMedian save-load;
/// GetColumnTrimmedMean no-throw; GetColumnTrimmedMean in range; GetColumnTrimmedMean consistent;
/// GetColumnTrimmedMean save-load;
/// dogfood Append→GetColumnMode→GetColumnMedian→GetColumnTrimmedMean→SaveToFile pipeline.
/// </summary>
public class TsvR236GetModeAndMedianDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR236GetModeAndMedianDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR236_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePropertyTsv()
    {
        var path = TempFile("property.tsv");
        var lines = new[]
        {
            "property_id\ttype\tbedrooms\tprice\tarea_sqm\tdistrict",
            "P001\tFlat\t2\t285000\t68\tNorth",
            "P002\tHouse\t3\t425000\t95\tSouth",
            "P003\tFlat\t1\t195000\t45\tCentral",
            "P004\tHouse\t4\t580000\t130\tNorth",
            "P005\tFlat\t2\t315000\t72\tEast",
            "P006\tHouse\t3\t445000\t102\tSouth",
            "P007\tFlat\t2\t298000\t70\tCentral",
            "P008\tHouse\t3\t398000\t88\tWest",
            "P009\tFlat\t1\t175000\t42\tNorth",
            "P010\tHouse\t3\t462000\t108\tSouth",
            "P011\tFlat\t2\t320000\t75\tEast",
            "P012\tHouse\t4\t650000\t145\tCentral"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMode_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var ex = Record.Exception(() => doc.GetColumnMode("type"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMode_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        Assert.NotNull(doc.GetColumnMode("type"));
    }

    [Fact]
    public void GetColumnMode_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        Assert.Equal(doc.GetColumnMode("bedrooms"), doc.GetColumnMode("bedrooms"));
    }

    [Fact]
    public void GetColumnMode_Correct_ForKnownData()
    {
        // Bedrooms: 2×5, 3×5, 1×2, 4×2 — mode is either "2" or "3"
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var mode = doc.GetColumnMode("bedrooms");
        Assert.True(mode == "2" || mode == "3");
    }

    [Fact]
    public void GetColumnMode_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var before = doc.GetColumnMode("district");
        var path = TempFile("mode_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMode("district"));
    }

    // -------------------------------------------------------------------------
    // GetColumnMedian
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMedian_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var ex = Record.Exception(() => doc.GetColumnMedian("price"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMedian_InRange()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var median = doc.GetColumnMedian("price");
        Assert.True(median >= doc.GetColumnMin("price"));
        Assert.True(median <= doc.GetColumnMax("price"));
    }

    [Fact]
    public void GetColumnMedian_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        Assert.Equal(doc.GetColumnMedian("area_sqm"), doc.GetColumnMedian("area_sqm"), precision: 4);
    }

    [Fact]
    public void GetColumnMedian_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var before = doc.GetColumnMedian("price");
        var path = TempFile("med_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMedian("price"), precision: 2);
    }

    // -------------------------------------------------------------------------
    // GetColumnTrimmedMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnTrimmedMean_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var ex = Record.Exception(() => doc.GetColumnTrimmedMean("price", 0.1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnTrimmedMean_InRange()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var tm = doc.GetColumnTrimmedMean("price", 0.1);
        Assert.True(tm >= doc.GetColumnMin("price"));
        Assert.True(tm <= doc.GetColumnMax("price"));
    }

    [Fact]
    public void GetColumnTrimmedMean_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        Assert.Equal(doc.GetColumnTrimmedMean("price", 0.2), doc.GetColumnTrimmedMean("price", 0.2), precision: 4);
    }

    [Fact]
    public void GetColumnTrimmedMean_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var before = doc.GetColumnTrimmedMean("price", 0.1);
        var path = TempFile("tm_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnTrimmedMean("price", 0.1), precision: 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMode_GetColumnMedian_GetColumnTrimmedMean_SaveToFile_Pipeline()
    {
        // Public sector pay transparency — UK civil service salary survey
        var path = TempFile("dogfood_civil_service.tsv");
        var lines = new[]
        {
            "employee_id\tgrade\tdepartment\tsalary\texperience_years\tlocation\tgender",
            "CS001\tAA\tHMRC\t22500\t2\tLondon\tF",
            "CS002\tEO\tDWP\t28000\t5\tLeeds\tM",
            "CS003\tHEO\tMOJ\t35000\t8\tManchester\tF",
            "CS004\tSEO\tHMRC\t44000\t12\tLondon\tM",
            "CS005\tEO\tDHSC\t29000\t4\tBirmingham\tF",
            "CS006\tAA\tDWP\t23500\t3\tCardiff\tM",
            "CS007\tHEO\tHMRC\t36500\t9\tLondon\tF",
            "CS008\tGrade7\tCabOff\t58000\t15\tLondon\tM",
            "CS009\tEO\tMOJ\t27500\t6\tLiverpool\tF",
            "CS010\tSEO\tDHSC\t43000\t11\tBristol\tM",
            "CS011\tHEO\tDWP\t34000\t7\tNewcastle\tF",
            "CS012\tGrade7\tHMRC\t61000\t18\tLondon\tM"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(12, doc.RowCount);

        // GetColumnMode — grade (EO appears 3 times, HEO 3 times — either valid)
        var gradeMode = doc.GetColumnMode("grade");
        Assert.NotNull(gradeMode);
        Assert.Equal(gradeMode, doc.GetColumnMode("grade")); // consistent

        // GetColumnMode — department (HMRC×3, DWP×3 — either valid)
        var deptMode = doc.GetColumnMode("department");
        Assert.NotNull(deptMode);

        // GetColumnMode — location (London×5 → clear mode)
        var locMode = doc.GetColumnMode("location");
        Assert.Equal("London", locMode);

        // GetColumnMedian — salary (sorted: 22500,23500,27500,28000,29000,34000,35000,36500,43000,44000,58000,61000 → median=(34000+35000)/2=34500)
        var salaryMedian = doc.GetColumnMedian("salary");
        Assert.True(salaryMedian >= 22500);
        Assert.True(salaryMedian <= 61000);
        Assert.Equal(salaryMedian, doc.GetColumnMedian("salary"), precision: 2); // consistent

        // GetColumnMedian — experience_years
        var expMedian = doc.GetColumnMedian("experience_years");
        Assert.True(expMedian >= 2);
        Assert.True(expMedian <= 18);

        // GetColumnTrimmedMean — salary (10% trim removes extremes: 22500 and 61000)
        var salaryTrimmed = doc.GetColumnTrimmedMean("salary", 0.1);
        Assert.True(salaryTrimmed >= 22500);
        Assert.True(salaryTrimmed <= 61000);
        Assert.Equal(salaryTrimmed, doc.GetColumnTrimmedMean("salary", 0.1), precision: 2); // consistent

        // GetColumnTrimmedMean — 20% trim (removes more extremes)
        var salary20 = doc.GetColumnTrimmedMean("salary", 0.2);
        Assert.True(salary20 >= 22500);
        Assert.True(salary20 <= 61000);

        // AppendRow — add senior executive
        doc.AppendRow(new[] { "CS013", "SCS", "CabOff", "95000", "22", "London", "F" });
        doc.AppendRow(new[] { "CS014", "EO", "HMRC", "28500", "5", "London", "M" });
        Assert.Equal(14, doc.RowCount);

        // After append: London still mode (7 occurrences)
        Assert.Equal("London", doc.GetColumnMode("location"));

        // Median updates with 95000 outlier present
        var newMedian = doc.GetColumnMedian("salary");
        Assert.True(newMedian >= 22500);

        // SaveToFile
        var out1 = TempFile("dogfood_civil_service_out.tsv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(out1);
        Assert.Equal(14, loaded.RowCount);
        Assert.Equal(doc.GetColumnMode("location"), loaded.GetColumnMode("location"));
        Assert.Equal(doc.GetColumnMedian("salary"), loaded.GetColumnMedian("salary"), precision: 2);
        Assert.Equal(doc.GetColumnTrimmedMean("salary", 0.1), loaded.GetColumnTrimmedMean("salary", 0.1), precision: 2);

        // Final save
        var out2 = TempFile("dogfood_civil_service_v2.tsv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = TsvDocument.LoadFile(out2);
        Assert.Equal(14, loaded2.RowCount);
        Assert.NotNull(loaded2.GetColumnMode("grade"));
        Assert.True(loaded2.GetColumnMedian("experience_years") >= 2.0);
        Assert.True(loaded2.GetColumnTrimmedMean("salary", 0.1) >= 22500);
        var ex1 = Record.Exception(() => loaded2.GetColumnMode("department"));
        var ex2 = Record.Exception(() => loaded2.GetColumnMedian("salary"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
