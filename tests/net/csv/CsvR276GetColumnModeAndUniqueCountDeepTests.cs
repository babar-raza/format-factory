// Tests for CsvDocument.GetColumnMode, GetColumnUniqueCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R276

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R276: Tests for CsvDocument.GetColumnMode, GetColumnUniqueCount deeper.
/// GetColumnMode(colName): returns the most frequently occurring value in the column.
/// GetColumnUniqueCount(colName): returns the number of distinct values in the column.
/// Covers: GetColumnMode no-throw; GetColumnMode correct for known data;
/// GetColumnMode consistent; GetColumnMode save-load;
/// GetColumnUniqueCount no-throw; GetColumnUniqueCount 1 for uniform;
/// GetColumnUniqueCount leq RowCount; GetColumnUniqueCount consistent;
/// GetColumnUniqueCount save-load; dogfood pipeline.
/// </summary>
public class CsvR276GetColumnModeAndUniqueCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR276GetColumnModeAndUniqueCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR276_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id,category,score");
        // category X appears 5 times (mode), Y 3 times, Z 2 times
        string[] cats = { "X", "X", "Y", "X", "Z", "Y", "X", "Z", "X", "Y" };
        for (int i = 0; i < cats.Length; i++)
            sb.AppendLine($"{i},{cats[i]},{i * 5.0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,status");
        for (int i = 0; i < 20; i++)
            sb.AppendLine($"{i},PASS");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMode_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnMode("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMode_Correct_ForKnownData()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal("X", doc.GetColumnMode("category"));
    }

    [Fact]
    public void GetColumnMode_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnMode("category"), doc.GetColumnMode("category"));
    }

    [Fact]
    public void GetColumnMode_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnMode("category");
        var path = TempFile("mode_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnMode("category"));
    }

    // -------------------------------------------------------------------------
    // GetColumnUniqueCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnUniqueCount_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnUniqueCount("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnUniqueCount_One_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(1, doc.GetColumnUniqueCount("status"));
    }

    [Fact]
    public void GetColumnUniqueCount_Three_ForThreeValues()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(3, doc.GetColumnUniqueCount("category"));
    }

    [Fact]
    public void GetColumnUniqueCount_Leq_RowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnUniqueCount("category") <= doc.RowCount);
    }

    [Fact]
    public void GetColumnUniqueCount_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnUniqueCount("category"), doc.GetColumnUniqueCount("category"));
    }

    [Fact]
    public void GetColumnUniqueCount_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnUniqueCount("category");
        var path = TempFile("uc_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnUniqueCount("category"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMode_GetColumnUniqueCount_Pipeline()
    {
        // Environment — Environment Agency / DEFRA: Water Quality Classification 2024
        // River and lake monitoring sites classified under Water Framework Directive (England)
        // Mode reveals the most common ecological status; unique count measures classification diversity

        var path = TempFile("ea_water_quality_wfd_2024.csv");
        var sb = new StringBuilder();
        sb.AppendLine("site_id,waterbody_name,waterbody_type,catchment,wfd_ecological_status,chemical_status,quantitative_status,risk_category,sampling_frequency,phosphorus_ugL,nitrate_mgL,dissolved_oxygen_pct");

        var rng = new Random(20240601);
        string[] waterbodyTypes = { "River", "Lake", "Transitional", "Coastal", "Groundwater" };
        string[] catchments = { "Thames", "Severn", "Trent", "Humber", "Anglian",
                                 "South_West", "South_East", "Solway_Tweed", "Dee", "Western_Wales" };
        // WFD ecological status: Good is the modal class for England waterbodies
        string[] ecologicalPool = {
            "High","Good","Good","Good","Good","Good","Moderate","Moderate","Poor","Bad"
        };
        string[] chemicalStatuses = { "Good", "Good", "Good", "Fail" };
        string[] riskCategories = { "At_Risk", "Probably_At_Risk", "Not_At_Risk", "Not_At_Risk", "Not_At_Risk" };

        for (int i = 0; i < 40; i++)
        {
            string type = waterbodyTypes[rng.Next(waterbodyTypes.Length)];
            string catchment = catchments[rng.Next(catchments.Length)];
            string ecoStatus = ecologicalPool[rng.Next(ecologicalPool.Length)];
            string chemStatus = chemicalStatuses[rng.Next(chemicalStatuses.Length)];
            string quantStatus = rng.NextDouble() < 0.85 ? "Good" : "Poor";
            string risk = riskCategories[rng.Next(riskCategories.Length)];
            int sampFreq = new[] { 4, 12, 26, 52 }[rng.Next(4)];
            double phosphorus = 10 + rng.NextDouble() * 490;
            double nitrate = 0.5 + rng.NextDouble() * 49.5;
            double do_ = 50 + rng.NextDouble() * 50;
            sb.AppendLine($"GB{100000 + i},Waterbody_{i:D3},{type},{catchment},{ecoStatus},{chemStatus},{quantStatus},{risk},{sampFreq},{phosphorus:F1},{nitrate:F2},{do_:F1}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(40, doc.RowCount);
        Assert.Equal(12, doc.ColumnCount);

        // Ecological status mode (should be "Good" — most common per WFD)
        var ecoMode = doc.GetColumnMode("wfd_ecological_status");
        Assert.NotNull(ecoMode);
        Assert.NotEmpty(ecoMode);
        Assert.Equal(ecoMode, doc.GetColumnMode("wfd_ecological_status")); // consistent

        // Ecological status unique count (High/Good/Moderate/Poor/Bad → up to 5)
        var ecoUnique = doc.GetColumnUniqueCount("wfd_ecological_status");
        Assert.True(ecoUnique >= 1);
        Assert.True(ecoUnique <= 5);
        Assert.Equal(ecoUnique, doc.GetColumnUniqueCount("wfd_ecological_status")); // consistent

        // Chemical status mode
        var chemMode = doc.GetColumnMode("chemical_status");
        Assert.NotNull(chemMode);
        Assert.Equal(chemMode, doc.GetColumnMode("chemical_status")); // consistent

        // Chemical status unique count (Good/Fail → 2)
        var chemUnique = doc.GetColumnUniqueCount("chemical_status");
        Assert.True(chemUnique >= 1);
        Assert.True(chemUnique <= 2);

        // Waterbody type unique count (up to 5 types)
        var typeUnique = doc.GetColumnUniqueCount("waterbody_type");
        Assert.True(typeUnique >= 1);
        Assert.True(typeUnique <= 5);

        // Catchment unique count (up to 10 catchments)
        var catchUnique = doc.GetColumnUniqueCount("catchment");
        Assert.True(catchUnique >= 1);
        Assert.True(catchUnique <= 10);

        // Risk category mode
        var riskMode = doc.GetColumnMode("risk_category");
        Assert.NotNull(riskMode);
        Assert.Equal(riskMode, doc.GetColumnMode("risk_category")); // consistent

        // SaveToFile
        var outPath = TempFile("ea_water_quality_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(ecoMode, loaded.GetColumnMode("wfd_ecological_status"));
        Assert.Equal(ecoUnique, loaded.GetColumnUniqueCount("wfd_ecological_status"));
        Assert.Equal(chemMode, loaded.GetColumnMode("chemical_status"));
        Assert.Equal(chemUnique, loaded.GetColumnUniqueCount("chemical_status"));
        Assert.Equal(typeUnique, loaded.GetColumnUniqueCount("waterbody_type"));
        Assert.Equal(catchUnique, loaded.GetColumnUniqueCount("catchment"));
    }
}
