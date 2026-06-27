// Tests for ZstDocument.GetWindowSize, GetMagicBytes deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R269

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R269: Tests for ZstDocument.GetWindowSize, GetMagicBytes deeper.
/// GetWindowSize(): returns the window size used in compression in bytes; positive for valid frames.
/// GetMagicBytes(): returns the magic byte header string (e.g. "FD2FB528" for zstd); non-null.
/// Covers: GetWindowSize no-throw; GetWindowSize positive; GetWindowSize consistent;
/// GetWindowSize save-load; GetMagicBytes no-throw; GetMagicBytes non-null-or-empty;
/// GetMagicBytes consistent; GetMagicBytes save-load;
/// dogfood CreateDoc→GetWindowSize→GetMagicBytes→SaveToFile pipeline.
/// </summary>
public class ZstR269GetWindowSizeAndMagicBytesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR269GetWindowSizeAndMagicBytesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR269_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateZst(string name, string content)
    {
        var path = TempFile(name);
        var bytes = Encoding.UTF8.GetBytes(content);
        using var outStream = new FileStream(path, FileMode.Create);
        using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
        zlib.Write(bytes, 0, bytes.Length);
        return path;
    }

    private string CreateLargeZst()
    {
        var sb = new StringBuilder();
        for (int i = 0; i < 400; i++)
            sb.AppendLine($"Row {i:D4}: field_a={i * 2.71:F3} field_b={i * 1.41:F4} tag=seg_{i / 40}");
        return CreateZst("large.zst", sb.ToString());
    }

    private string CreateSmallZst() =>
        CreateZst("small.zst", "Small window size test payload. " + string.Concat(Enumerable.Repeat("abc ", 50)));

    // -------------------------------------------------------------------------
    // GetWindowSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWindowSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var ex = Record.Exception(() => doc.GetWindowSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWindowSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.True(doc.GetWindowSize() > 0);
    }

    [Fact]
    public void GetWindowSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.Equal(doc.GetWindowSize(), doc.GetWindowSize());
    }

    [Fact]
    public void GetWindowSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var before = doc.GetWindowSize();
        var path = TempFile("ws_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetWindowSize());
    }

    // -------------------------------------------------------------------------
    // GetMagicBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMagicBytes_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSmallZst());
        var ex = Record.Exception(() => doc.GetMagicBytes());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMagicBytes_NonNullOrEmpty()
    {
        var doc = ZstDocument.LoadFile(CreateSmallZst());
        Assert.False(string.IsNullOrEmpty(doc.GetMagicBytes()));
    }

    [Fact]
    public void GetMagicBytes_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSmallZst());
        Assert.Equal(doc.GetMagicBytes(), doc.GetMagicBytes());
    }

    [Fact]
    public void GetMagicBytes_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var before = doc.GetMagicBytes();
        var path = TempFile("mb_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMagicBytes());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetWindowSize_GetMagicBytes_SaveToFile_Pipeline()
    {
        // Environment — Environment Agency: National Flood Risk Assessment (NaFRA2)
        // Compressed flood risk model output archives for planning and insurance purposes
        // Window size and magic byte validation for archive integrity checking

        // File 1: River flood risk model output (large spatial dataset)
        var path1 = TempFile("nafra2_river_flood_risk_zone3.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("NaFRA2 — River Flood Risk Zone 3 Output");
            content.AppendLine("Model: 1D-2D coupled hydraulic model (ISIS/TUFLOW)");
            content.AppendLine("Coordinate system: OSGB 1936 / British National Grid (EPSG:27700)");
            content.AppendLine("Output reference period: 100-year return period (1% AEP)");
            for (int i = 0; i < 250; i++)
            {
                double easting = 400000 + i * 100;
                double northing = 250000 + (i % 50) * 100;
                double depth = 0.1 + (i % 20) * 0.15;
                double velocity = 0.3 + (i % 10) * 0.12;
                string riskType = i % 3 == 0 ? "Surface_Water" : i % 3 == 1 ? "River" : "Combined";
                content.AppendLine($"GRID{i:D6}|E{easting:F0}|N{northing:F0}|depth_m={depth:F3}|velocity_ms={velocity:F3}|risk={riskType}|flood_zone=FZ3");
            }
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path1, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
            zlib.Write(bytes, 0, bytes.Length);
        }

        // File 2: Tidal/coastal flood risk (medium dataset)
        var path2 = TempFile("nafra2_tidal_coastal_flood_200yr.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("NaFRA2 — Tidal and Coastal Flood Risk 0.5% AEP (200-year)");
            content.AppendLine("Model: SWAN wave model + XBeach storm surge");
            content.AppendLine("Coastline segments: ERCE coastal cell subdivisions");
            for (int i = 0; i < 180; i++)
            {
                double lon = -5.0 + i * 0.05;
                double lat = 50.0 + (i % 30) * 0.02;
                double surge = 0.8 + (i % 15) * 0.1;
                string authority = i % 4 == 0 ? "South_West_EA" : i % 4 == 1 ? "Southern_EA" : i % 4 == 2 ? "Anglian_EA" : "NW_EA";
                content.AppendLine($"COAST{i:D5}|lon={lon:F4}|lat={lat:F4}|surge_m={surge:F2}|authority={authority}|protection_standard=1_in_200");
            }
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path2, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
            zlib.Write(bytes, 0, bytes.Length);
        }

        // File 3: Summary statistics (small metadata file)
        var path3 = TempFile("nafra2_national_summary_stats.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("{\"model\":\"NaFRA2\",\"version\":\"2024.1\"," +
                               "\"total_properties_at_risk\":6200000," +
                               "\"zone3_properties\":520000," +
                               "\"zone2_properties\":2700000," +
                               "\"model_date\":\"2024-03-15\"," +
                               "\"published_by\":\"Environment_Agency\"}");
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path3, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.SmallestSize);
            zlib.Write(bytes, 0, bytes.Length);
        }

        var doc1 = ZstDocument.LoadFile(path1);
        var doc2 = ZstDocument.LoadFile(path2);
        var doc3 = ZstDocument.LoadFile(path3);

        // Window size
        var ws1 = doc1.GetWindowSize();
        var ws2 = doc2.GetWindowSize();
        var ws3 = doc3.GetWindowSize();
        Assert.True(ws1 > 0);
        Assert.True(ws2 > 0);
        Assert.True(ws3 > 0);
        Assert.Equal(ws1, doc1.GetWindowSize()); // consistent
        Assert.Equal(ws2, doc2.GetWindowSize()); // consistent

        // Magic bytes
        var mb1 = doc1.GetMagicBytes();
        var mb2 = doc2.GetMagicBytes();
        var mb3 = doc3.GetMagicBytes();
        Assert.False(string.IsNullOrEmpty(mb1));
        Assert.False(string.IsNullOrEmpty(mb2));
        Assert.False(string.IsNullOrEmpty(mb3));
        Assert.Equal(mb1, doc1.GetMagicBytes()); // consistent
        Assert.Equal(mb2, doc2.GetMagicBytes()); // consistent

        // Basic ZST metrics
        Assert.True(doc1.CompressedSize > 0);
        Assert.True(doc2.CompressedSize > 0);
        Assert.True(doc1.OriginalSize > 0);

        // SaveToFile
        var out1 = TempFile("nafra2_river_out.zst");
        doc1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        var loaded1 = ZstDocument.LoadFile(out1);
        Assert.Equal(ws1, loaded1.GetWindowSize());
        Assert.Equal(mb1, loaded1.GetMagicBytes());

        var out2 = TempFile("nafra2_tidal_out.zst");
        doc2.SaveToFile(out2);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.Equal(ws2, loaded2.GetWindowSize());
        Assert.Equal(mb2, loaded2.GetMagicBytes());

        Assert.Equal(doc1.OriginalSize, loaded1.OriginalSize);
        Assert.Equal(doc2.CompressedSize, loaded2.CompressedSize);

        var ex1 = Record.Exception(() => loaded1.GetWindowSize());
        var ex2 = Record.Exception(() => loaded1.GetMagicBytes());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
