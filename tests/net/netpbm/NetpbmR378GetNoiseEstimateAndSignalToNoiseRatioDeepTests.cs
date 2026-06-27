// Tests for NetpbmImage.GetNoiseEstimate, GetSignalToNoiseRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R378

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R378: Tests for NetpbmImage.GetNoiseEstimate, GetSignalToNoiseRatio deeper.
/// GetNoiseEstimate(): returns an estimate of the noise level in the image (higher = noisier).
/// GetSignalToNoiseRatio(): returns SNR = mean / std-dev (or 0 for uniform images with zero std-dev).
/// Covers: GetNoiseEstimate no-throw; GetNoiseEstimate non-negative; GetNoiseEstimate consistent;
/// GetNoiseEstimate save-load; GetNoiseEstimate higher for noisy image;
/// GetSignalToNoiseRatio no-throw; GetSignalToNoiseRatio non-negative;
/// GetSignalToNoiseRatio consistent; GetSignalToNoiseRatio save-load;
/// GetSignalToNoiseRatio higher for clean image; dogfood pipeline.
/// </summary>
public class NetpbmR378GetNoiseEstimateAndSignalToNoiseRatioDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR378GetNoiseEstimateAndSignalToNoiseRatioDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR378_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCleanPgm()
    {
        // Smooth gradient — no noise
        var path = TempFile("clean.pgm");
        var sb = new StringBuilder();
        int w = 40, h = 40;
        sb.AppendLine("P2");
        sb.AppendLine($"{w} {h}");
        sb.AppendLine("255");
        for (int r = 0; r < h; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < w; c++)
            {
                if (c > 0) row.Append(' ');
                row.Append((c * 200) / (w - 1) + 27); // 27-227 smooth gradient
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateNoisyPgm()
    {
        // Same gradient with heavy noise added
        var path = TempFile("noisy.pgm");
        var sb = new StringBuilder();
        int w = 40, h = 40;
        sb.AppendLine("P2");
        sb.AppendLine($"{w} {h}");
        sb.AppendLine("255");
        var rng = new Random(42);
        for (int r = 0; r < h; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < w; c++)
            {
                if (c > 0) row.Append(' ');
                int base_ = (c * 200) / (w - 1) + 27;
                int noisy = base_ + rng.Next(-50, 51); // ±50 noise
                row.Append(Math.Max(0, Math.Min(255, noisy)));
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformPgm()
    {
        var path = TempFile("uniform.pgm");
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("40 40");
        sb.AppendLine("255");
        for (int r = 0; r < 40; r++)
        {
            var row = new StringBuilder();
            for (int c = 0; c < 40; c++) { if (c > 0) row.Append(' '); row.Append(128); }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetNoiseEstimate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNoiseEstimate_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        var ex = Record.Exception(() => img.GetNoiseEstimate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetNoiseEstimate_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        Assert.True(img.GetNoiseEstimate() >= 0.0);
    }

    [Fact]
    public void GetNoiseEstimate_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        Assert.Equal(img.GetNoiseEstimate(), img.GetNoiseEstimate());
    }

    [Fact]
    public void GetNoiseEstimate_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        var before = img.GetNoiseEstimate();
        var path = TempFile("ne_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetNoiseEstimate(), precision: 6);
    }

    [Fact]
    public void GetNoiseEstimate_Higher_ForNoisy_Than_Clean()
    {
        var imgNoisy = NetpbmImage.LoadFile(CreateNoisyPgm());
        var imgClean = NetpbmImage.LoadFile(CreateCleanPgm());
        Assert.True(imgNoisy.GetNoiseEstimate() >= imgClean.GetNoiseEstimate());
    }

    // -------------------------------------------------------------------------
    // GetSignalToNoiseRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSignalToNoiseRatio_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateCleanPgm());
        var ex = Record.Exception(() => img.GetSignalToNoiseRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSignalToNoiseRatio_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateCleanPgm());
        Assert.True(img.GetSignalToNoiseRatio() >= 0.0);
    }

    [Fact]
    public void GetSignalToNoiseRatio_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCleanPgm());
        Assert.Equal(img.GetSignalToNoiseRatio(), img.GetSignalToNoiseRatio());
    }

    [Fact]
    public void GetSignalToNoiseRatio_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCleanPgm());
        var before = img.GetSignalToNoiseRatio();
        var path = TempFile("snr_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetSignalToNoiseRatio(), precision: 6);
    }

    [Fact]
    public void GetSignalToNoiseRatio_Higher_ForClean_Than_Noisy()
    {
        var imgClean = NetpbmImage.LoadFile(CreateCleanPgm());
        var imgNoisy = NetpbmImage.LoadFile(CreateNoisyPgm());
        // Clean image: small noise → high SNR; Noisy: large variance → lower SNR
        Assert.True(imgClean.GetSignalToNoiseRatio() >= imgNoisy.GetSignalToNoiseRatio());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetNoiseEstimate_GetSignalToNoiseRatio_SaveToFile_Pipeline()
    {
        // Scientific — UK Astronomy Technology Centre (ATC): Dark Energy Survey CCD Images
        // Raw and calibrated astronomical images — noise floor and SNR analysis
        // Dark current, read noise, and sky background subtraction quality assessment

        // Image 1: Clean calibrated science frame (bias-subtracted, flat-fielded)
        var pathCalibrated = TempFile("atc_calibrated_frame.pgm");
        {
            int w = 80, h = 60;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240901);
            for (int r = 0; r < h; r++)
            {
                var row = new StringBuilder();
                for (int c = 0; c < w; c++)
                {
                    if (c > 0) row.Append(' ');
                    // Galaxy profile: central bright source + smooth background
                    double dx = c - w / 2.0, dy = r - h / 2.0;
                    double dist = Math.Sqrt(dx * dx + dy * dy);
                    int galaxy = (int)(200 * Math.Exp(-dist * dist / 200.0));
                    int sky = 40; // sky background after subtraction
                    int readNoise = rng.Next(-2, 3); // low read noise (±2 ADU)
                    row.Append(Math.Max(0, Math.Min(255, galaxy + sky + readNoise)));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathCalibrated, sb.ToString());
        }

        // Image 2: Raw uncalibrated frame (high noise: dark current + cosmic rays)
        var pathRaw = TempFile("atc_raw_frame.pgm");
        {
            int w = 80, h = 60;
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
                    double dx = c - w / 2.0, dy = r - h / 2.0;
                    double dist = Math.Sqrt(dx * dx + dy * dy);
                    int galaxy = (int)(200 * Math.Exp(-dist * dist / 200.0));
                    int sky = 80; // higher background (not subtracted)
                    int darkCurrent = rng.Next(0, 30); // dark current noise
                    int readNoise = rng.Next(-15, 16); // high read noise
                    // Cosmic ray hits
                    bool cosmicRay = rng.NextDouble() < 0.01;
                    int v = cosmicRay ? 255 : galaxy + sky + darkCurrent + readNoise;
                    row.Append(Math.Max(0, Math.Min(255, v)));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(pathRaw, sb.ToString());
        }

        var imgCalibrated = NetpbmImage.LoadFile(pathCalibrated);
        var imgRaw = NetpbmImage.LoadFile(pathRaw);

        // Noise estimate assertions
        var neCalibrated = imgCalibrated.GetNoiseEstimate();
        var neRaw = imgRaw.GetNoiseEstimate();
        Assert.True(neCalibrated >= 0.0);
        Assert.True(neRaw >= 0.0);
        Assert.True(neRaw >= neCalibrated); // raw frame noisier than calibrated
        Assert.Equal(neCalibrated, imgCalibrated.GetNoiseEstimate()); // consistent

        // SNR assertions
        var snrCalibrated = imgCalibrated.GetSignalToNoiseRatio();
        var snrRaw = imgRaw.GetSignalToNoiseRatio();
        Assert.True(snrCalibrated >= 0.0);
        Assert.True(snrRaw >= 0.0);
        Assert.Equal(snrCalibrated, imgCalibrated.GetSignalToNoiseRatio()); // consistent

        // Uniform image: SNR = 0 (or undefined/0 when std-dev = 0)
        var imgUniform = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.True(imgUniform.GetNoiseEstimate() >= 0.0);
        Assert.True(imgUniform.GetSignalToNoiseRatio() >= 0.0);

        // Image properties
        Assert.Equal(80, imgCalibrated.Width);
        Assert.Equal(60, imgCalibrated.Height);
        Assert.True(imgCalibrated.GetGlobalMean() > 0);

        // SaveToFile
        var outCalibrated = TempFile("atc_calibrated_frame_out.pgm");
        imgCalibrated.SaveToFile(outCalibrated);
        Assert.True(File.Exists(outCalibrated));
        Assert.True(new FileInfo(outCalibrated).Length > 0);
        var loadedCalibrated = NetpbmImage.LoadFile(outCalibrated);
        Assert.Equal(neCalibrated, loadedCalibrated.GetNoiseEstimate(), precision: 6);
        Assert.Equal(snrCalibrated, loadedCalibrated.GetSignalToNoiseRatio(), precision: 6);

        var outRaw = TempFile("atc_raw_frame_out.pgm");
        imgRaw.SaveToFile(outRaw);
        var loadedRaw = NetpbmImage.LoadFile(outRaw);
        Assert.Equal(neRaw, loadedRaw.GetNoiseEstimate(), precision: 6);
        Assert.Equal(snrRaw, loadedRaw.GetSignalToNoiseRatio(), precision: 6);

        Assert.Equal(imgCalibrated.Width, loadedCalibrated.Width);
        Assert.Equal(imgCalibrated.Height, loadedCalibrated.Height);

        var ex1 = Record.Exception(() => loadedCalibrated.GetNoiseEstimate());
        var ex2 = Record.Exception(() => loadedCalibrated.GetSignalToNoiseRatio());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
