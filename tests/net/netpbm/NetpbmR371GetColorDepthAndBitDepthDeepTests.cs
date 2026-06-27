// Tests for NetpbmImage.GetColorDepth, GetBitDepth deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R371

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R371: Tests for NetpbmImage.GetColorDepth, GetBitDepth deeper.
/// GetColorDepth(): returns the number of distinct intensity values (1..MaxValue+1) present in the image.
/// GetBitDepth(): returns the minimum number of bits required to represent the max value (log2(MaxVal+1) ceiling).
/// Covers: GetColorDepth no-throw; GetColorDepth at least one; GetColorDepth consistent;
/// GetColorDepth one for uniform; GetColorDepth save-load;
/// GetBitDepth no-throw; GetBitDepth positive; GetBitDepth consistent;
/// GetBitDepth save-load; GetBitDepth eight for 255 maxval;
/// GetColorDepth le MaxValue plus one; dogfood pipeline.
/// </summary>
public class NetpbmR371GetColorDepthAndBitDepthDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR371GetColorDepthAndBitDepthDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR371_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateUniformPgm(int width = 40, int height = 40, int value = 128, int maxVal = 255)
    {
        var path = TempFile($"uniform_{value}.pgm");
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine(maxVal.ToString());
        for (int r = 0; r < height; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < width; c++)
            {
                if (c > 0) row.Append(' ');
                row.Append(value);
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateFullRangePgm(int width = 256, int height = 1)
    {
        var path = TempFile("full_range.pgm");
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        var row = new StringBuilder();
        for (int c = 0; c < 256; c++)
        {
            if (c > 0) row.Append(' ');
            row.Append(c);
        }
        sb.AppendLine(row.ToString());
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateSamplePgm()
    {
        var path = TempFile("sample.pgm");
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("40 40");
        sb.AppendLine("255");
        var rng = new Random(42);
        for (int r = 0; r < 40; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < 40; c++)
            {
                if (c > 0) row.Append(' ');
                row.Append(rng.Next(256));
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColorDepth
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorDepth_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSamplePgm());
        var ex = Record.Exception(() => img.GetColorDepth());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColorDepth_AtLeastOne()
    {
        var img = NetpbmImage.LoadFile(CreateSamplePgm());
        Assert.True(img.GetColorDepth() >= 1);
    }

    [Fact]
    public void GetColorDepth_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSamplePgm());
        Assert.Equal(img.GetColorDepth(), img.GetColorDepth());
    }

    [Fact]
    public void GetColorDepth_One_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(1, img.GetColorDepth());
    }

    [Fact]
    public void GetColorDepth_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSamplePgm());
        var before = img.GetColorDepth();
        var path = TempFile("cd_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetColorDepth());
    }

    // -------------------------------------------------------------------------
    // GetBitDepth
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBitDepth_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSamplePgm());
        var ex = Record.Exception(() => img.GetBitDepth());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBitDepth_Positive()
    {
        var img = NetpbmImage.LoadFile(CreateSamplePgm());
        Assert.True(img.GetBitDepth() > 0);
    }

    [Fact]
    public void GetBitDepth_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSamplePgm());
        Assert.Equal(img.GetBitDepth(), img.GetBitDepth());
    }

    [Fact]
    public void GetBitDepth_Eight_For_MaxVal_255()
    {
        var img = NetpbmImage.LoadFile(CreateSamplePgm()); // maxval=255
        Assert.Equal(8, img.GetBitDepth());
    }

    [Fact]
    public void GetBitDepth_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSamplePgm());
        var before = img.GetBitDepth();
        var path = TempFile("bd_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetBitDepth());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColorDepth_GetBitDepth_SaveToFile_Pipeline()
    {
        // Geophysics — British Geological Survey (BGS): Magnetic Anomaly Maps
        // PGM images representing total-field magnetic intensity anomalies
        // Color depth and bit depth analysis for datum encoding quality control

        // Full-range anomaly map (all 256 values used)
        var pathFullRange = TempFile("magnetic_anomaly_fullrange.pgm");
        {
            int w = 64, h = 64;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            // Fill with all 256 values cyclically to guarantee full range
            int val = 0;
            for (int r = 0; r < h; r++)
            {
                var row = new StringBuilder();
                for (int c = 0; c < w; c++)
                {
                    if (c > 0) row.Append(' ');
                    row.Append(val % 256);
                    val++;
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathFullRange, sb.ToString());
        }

        // Low-contrast map (narrow value range: 100-140)
        var pathNarrow = TempFile("magnetic_anomaly_narrow.pgm");
        {
            int w = 60, h = 60;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240902);
            for (int r = 0; r < h; r++)
            {
                var row = new StringBuilder();
                for (int c = 0; c < w; c++)
                {
                    if (c > 0) row.Append(' ');
                    row.Append(100 + rng.Next(41)); // 100-140 only
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathNarrow, sb.ToString());
        }

        // Uniform map (single value — background field)
        var pathUniform = TempFile("magnetic_anomaly_uniform.pgm");
        {
            int w = 40, h = 40;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            for (int r = 0; r < h; r++)
            {
                var row = new StringBuilder();
                for (int c = 0; c < w; c++)
                {
                    if (c > 0) row.Append(' ');
                    row.Append(128); // uniform background
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathUniform, sb.ToString());
        }

        var imgFull = NetpbmImage.LoadFile(pathFullRange);
        var imgNarrow = NetpbmImage.LoadFile(pathNarrow);
        var imgUniform = NetpbmImage.LoadFile(pathUniform);

        // GetColorDepth assertions
        var cdFull = imgFull.GetColorDepth();
        var cdNarrow = imgNarrow.GetColorDepth();
        var cdUniform = imgUniform.GetColorDepth();
        Assert.True(cdFull >= 1);
        Assert.True(cdNarrow >= 1);
        Assert.Equal(1, cdUniform); // uniform → 1 distinct value
        Assert.True(cdFull > cdNarrow); // full range > narrow range
        Assert.True(cdNarrow > cdUniform);
        Assert.Equal(cdFull, imgFull.GetColorDepth()); // consistent
        Assert.Equal(cdNarrow, imgNarrow.GetColorDepth());

        // GetBitDepth assertions
        var bdFull = imgFull.GetBitDepth();
        var bdNarrow = imgNarrow.GetBitDepth();
        var bdUniform = imgUniform.GetBitDepth();
        Assert.True(bdFull > 0);
        Assert.True(bdNarrow > 0);
        Assert.True(bdUniform > 0);
        Assert.Equal(8, bdFull);   // maxval=255 → 8 bits
        Assert.Equal(8, bdNarrow); // maxval=255 (header) → 8 bits
        Assert.Equal(8, bdUniform); // maxval=255 (header) → 8 bits
        Assert.Equal(bdFull, imgFull.GetBitDepth()); // consistent

        // Image dimensions
        Assert.Equal(64, imgFull.Width);
        Assert.Equal(64, imgFull.Height);
        Assert.True(imgFull.GetGlobalMean() > 0);

        // SaveToFile
        var outFull = TempFile("magnetic_fullrange_out.pgm");
        imgFull.SaveToFile(outFull);
        Assert.True(File.Exists(outFull));
        var loadedFull = NetpbmImage.LoadFile(outFull);
        Assert.Equal(cdFull, loadedFull.GetColorDepth());
        Assert.Equal(bdFull, loadedFull.GetBitDepth());

        var outNarrow = TempFile("magnetic_narrow_out.pgm");
        imgNarrow.SaveToFile(outNarrow);
        var loadedNarrow = NetpbmImage.LoadFile(outNarrow);
        Assert.Equal(cdNarrow, loadedNarrow.GetColorDepth());
        Assert.Equal(bdNarrow, loadedNarrow.GetBitDepth());

        var outUniform = TempFile("magnetic_uniform_out.pgm");
        imgUniform.SaveToFile(outUniform);
        var loadedUniform = NetpbmImage.LoadFile(outUniform);
        Assert.Equal(1, loadedUniform.GetColorDepth());
        Assert.Equal(8, loadedUniform.GetBitDepth());

        var ex1 = Record.Exception(() => loadedFull.GetColorDepth());
        var ex2 = Record.Exception(() => loadedFull.GetBitDepth());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
