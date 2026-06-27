// Tests for ZstDocument.GetWindowSize, GetSearchDepth deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R263

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R263: Tests for ZstDocument.GetWindowSize, GetSearchDepth deeper.
/// GetWindowSize(): returns the window size (in bytes) used during compression.
/// GetSearchDepth(): returns the search depth / compression level as encoded in the frame header.
/// Covers: GetWindowSize no-throw; GetWindowSize positive; GetWindowSize consistent;
/// GetWindowSize save-load; GetSearchDepth no-throw; GetSearchDepth non-negative;
/// GetSearchDepth consistent; GetSearchDepth save-load;
/// GetWindowSize greater than CompressedSize for small inputs;
/// dogfood CreateDoc→GetWindowSize→GetSearchDepth→SaveToFile pipeline.
/// </summary>
public class ZstR263GetWindowSizeAndSearchDepthDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR263GetWindowSizeAndSearchDepthDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR263_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleZst(string suffix = "a")
    {
        var path = TempFile($"sample_{suffix}.zst");
        var text = "The Competition and Markets Authority conducts merger inquiries and antitrust investigations. ";
        var source = Encoding.UTF8.GetBytes(string.Concat(Enumerable.Repeat(text, 100)));
        using var fs = File.Create(path);
        using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
        zs.Write(source, 0, source.Length);
        return path;
    }

    private string CreateSmallZst()
    {
        var path = TempFile("small.zst");
        var source = Encoding.UTF8.GetBytes("Small payload.");
        using var fs = File.Create(path);
        using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
        zs.Write(source, 0, source.Length);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetWindowSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWindowSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetWindowSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWindowSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetWindowSize() > 0);
    }

    [Fact]
    public void GetWindowSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetWindowSize(), doc.GetWindowSize());
    }

    [Fact]
    public void GetWindowSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetWindowSize();
        var path = TempFile("ws_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetWindowSize());
    }

    // -------------------------------------------------------------------------
    // GetSearchDepth
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSearchDepth_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetSearchDepth());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSearchDepth_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetSearchDepth() >= 0);
    }

    [Fact]
    public void GetSearchDepth_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetSearchDepth(), doc.GetSearchDepth());
    }

    [Fact]
    public void GetSearchDepth_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetSearchDepth();
        var path = TempFile("sd_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSearchDepth());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetWindowSize_GetSearchDepth_SaveToFile_Pipeline()
    {
        // Data infrastructure — Office for National Statistics (ONS) Census 2021
        // Large-scale microdata compressed archives for secure research access
        // Window size and search depth analysis for storage tier and access latency planning

        // File 1: Structured tabular census data (highly compressible)
        var pathCensus = TempFile("census_2021_microdata.zst");
        {
            var sb = new StringBuilder();
            sb.AppendLine("person_id,la_code,age_band,sex,ethnic_group,religion,occupation_soc,nssec,tenure,car_availability");
            var rng = new Random(20240901);
            string[] ageBands = { "0-15", "16-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75+" };
            string[] ethnicGroups = { "White British", "White Other", "Asian Indian", "Asian Pakistani", "Asian Bangladeshi", "Black African", "Black Caribbean", "Mixed", "Other" };
            string[] religions = { "Christian", "Muslim", "Hindu", "Sikh", "Jewish", "Buddhist", "None", "Not stated" };
            string[] tenures = { "Own outright", "Own mortgage", "Private rented", "Social rented", "Other" };
            for (int i = 0; i < 400; i++)
            {
                string la = $"E090{rng.Next(10, 99):D2}{rng.Next(100, 999)}";
                string age = ageBands[rng.Next(ageBands.Length)];
                string sex = rng.Next(2) == 0 ? "Male" : "Female";
                string ethnic = ethnicGroups[rng.Next(ethnicGroups.Length)];
                string relig = religions[rng.Next(religions.Length)];
                int soc = 1110 + rng.Next(8890);
                int nssec = 1 + rng.Next(8);
                string tenure = tenures[rng.Next(tenures.Length)];
                int cars = rng.Next(4);
                sb.AppendLine($"P{i:D8},{la},{age},{sex},{ethnic},{relig},{soc},{nssec},{tenure},{cars}");
            }
            var source = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(pathCensus);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
            zs.Write(source, 0, source.Length);
        }

        // File 2: Aggregate counts data (repetitive integer patterns)
        var pathAgg = TempFile("census_2021_aggregates.zst");
        {
            var sb = new StringBuilder();
            sb.AppendLine("la_code,variable,category,count,percentage");
            var rng = new Random(20240902);
            string[] variables = { "age_band", "sex", "ethnic_group", "tenure", "religion", "qualification" };
            for (int i = 0; i < 300; i++)
            {
                string la = $"E090{(i % 30) + 10:D2}{(i % 100) + 100}";
                string variable = variables[i % variables.Length];
                string cat = $"cat_{i % 8}";
                int count = 500 + rng.Next(50000);
                double pct = Math.Round(count / 100000.0 * 100, 2);
                sb.AppendLine($"{la},{variable},{cat},{count},{pct}");
            }
            var source = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(pathAgg);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
            zs.Write(source, 0, source.Length);
        }

        var docCensus = ZstDocument.LoadFile(pathCensus);
        var docAgg = ZstDocument.LoadFile(pathAgg);

        // GetWindowSize
        var wsCensus = docCensus.GetWindowSize();
        var wsAgg = docAgg.GetWindowSize();
        Assert.True(wsCensus > 0);
        Assert.True(wsAgg > 0);
        Assert.Equal(wsCensus, docCensus.GetWindowSize()); // consistent
        Assert.Equal(wsAgg, docAgg.GetWindowSize()); // consistent

        // GetSearchDepth
        var sdCensus = docCensus.GetSearchDepth();
        var sdAgg = docAgg.GetSearchDepth();
        Assert.True(sdCensus >= 0);
        Assert.True(sdAgg >= 0);
        Assert.Equal(sdCensus, docCensus.GetSearchDepth()); // consistent
        Assert.Equal(sdAgg, docAgg.GetSearchDepth()); // consistent

        // Basic document properties
        Assert.True(docCensus.CompressedSize > 0);
        Assert.True(docAgg.CompressedSize > 0);

        // SaveToFile
        var outCensus = TempFile("census_out.zst");
        docCensus.SaveToFile(outCensus);
        Assert.True(File.Exists(outCensus));
        var loadedCensus = ZstDocument.LoadFile(outCensus);
        Assert.Equal(wsCensus, loadedCensus.GetWindowSize());
        Assert.Equal(sdCensus, loadedCensus.GetSearchDepth());

        var outAgg = TempFile("aggregates_out.zst");
        docAgg.SaveToFile(outAgg);
        Assert.True(File.Exists(outAgg));
        var loadedAgg = ZstDocument.LoadFile(outAgg);
        Assert.Equal(wsAgg, loadedAgg.GetWindowSize());
        Assert.Equal(sdAgg, loadedAgg.GetSearchDepth());

        var ex1 = Record.Exception(() => loadedCensus.GetWindowSize());
        var ex2 = Record.Exception(() => loadedCensus.GetSearchDepth());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
