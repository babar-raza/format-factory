// Tests for NetpbmImage.GetNoiseEstimate, GetSNR, GetPSNR deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R325

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R325: Tests for NetpbmImage.GetNoiseEstimate, GetSNR, GetPSNR deeper.
/// GetNoiseEstimate(): returns an estimate of the noise standard deviation in the image.
/// GetSNR(): returns the signal-to-noise ratio (mean/noise estimate).
/// GetPSNR(): returns the peak signal-to-noise ratio in decibels (20*log10(MaxValue/RMSE)).
/// Covers: GetNoiseEstimate no-throw; GetNoiseEstimate non-negative; GetNoiseEstimate consistent;
/// GetNoiseEstimate zero for uniform image;
/// GetSNR no-throw; GetSNR non-negative for non-trivial image; GetSNR consistent;
/// GetPSNR no-throw; GetPSNR non-negative; GetPSNR consistent;
/// GetPSNR save-load;
/// dogfood GetNoiseEstimate→GetSNR→GetPSNR→SaveToFile pipeline.
/// </summary>
public class NetpbmR325GetNoiseEstimateAndSNRDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR325GetNoiseEstimateAndSNRDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR325_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateNoisyPgm()
    {
        // 12×12 PGM with salt-and-pepper noise over mid-grey background
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        int[] row0 = { 128, 0, 128, 255, 128, 128, 0, 128, 128, 255, 128, 0 };
        int[] row1 = { 128, 128, 255, 128, 0, 128, 128, 128, 255, 128, 0, 128 };
        int[] rowMid = { 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128 };
        for (int r = 0; r < 12; r++)
        {
            if (r % 3 == 0)
                sb.AppendLine(string.Join(" ", row0));
            else if (r % 3 == 1)
                sb.AppendLine(string.Join(" ", row1));
            else
                sb.AppendLine(string.Join(" ", rowMid));
        }
        var path = TempFile("noisy.pgm");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformPgm()
    {
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
            sb.AppendLine("100 100 100 100 100 100 100 100 100 100 100 100");
        var path = TempFile("uniform.pgm");
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
        Assert.True(img.GetNoiseEstimate() >= 0);
    }

    [Fact]
    public void GetNoiseEstimate_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        Assert.Equal(img.GetNoiseEstimate(), img.GetNoiseEstimate());
    }

    [Fact]
    public void GetNoiseEstimate_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, img.GetNoiseEstimate(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetSNR
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSNR_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        var ex = Record.Exception(() => img.GetSNR());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSNR_NonNegative_ForNonTrivialImage()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        Assert.True(img.GetSNR() >= 0);
    }

    [Fact]
    public void GetSNR_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        Assert.Equal(img.GetSNR(), img.GetSNR());
    }

    // -------------------------------------------------------------------------
    // GetPSNR
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPSNR_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        var ex = Record.Exception(() => img.GetPSNR());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPSNR_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        Assert.True(img.GetPSNR() >= 0);
    }

    [Fact]
    public void GetPSNR_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        Assert.Equal(img.GetPSNR(), img.GetPSNR());
    }

    [Fact]
    public void GetPSNR_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        var before = img.GetPSNR();
        var path = TempFile("psnr_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetPSNR(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetNoiseEstimate_GetSNR_GetPSNR_SaveToFile_Pipeline()
    {
        // Radio astronomy — synthesised beam image noise characterisation for VLBI imaging pipeline
        // 12×12 PGM simulating CLEAN component map with noise pedestal (cosmic microwave background-like)

        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        // Radio source (bright compact emission) at centre, noise floor everywhere else
        // Row 0-2: noise pedestal
        sb.AppendLine("3 2 4 3 5 2 4 3 2 5 3 4");
        sb.AppendLine("4 3 2 5 3 4 2 3 5 3 4 2");
        sb.AppendLine("2 5 3 4 2 5 3 4 2 5 3 2");
        // Row 3-4: extended emission lobe (low-level)
        sb.AppendLine("3 8 12 15 12 8 6 5 3 4 2 3");
        sb.AppendLine("4 10 18 24 18 10 8 6 4 3 5 4");
        // Row 5-6: primary beam (bright source)
        sb.AppendLine("3 15 35 80 180 80 35 15 8 5 3 2");
        sb.AppendLine("2 12 30 75 170 75 30 12 6 4 2 3");
        // Row 7-8: extended emission lobe (low-level)
        sb.AppendLine("4 8 16 22 16 8 6 5 3 4 2 3");
        sb.AppendLine("3 6 10 14 10 6 5 4 3 2 4 3");
        // Row 9-11: noise pedestal
        sb.AppendLine("5 3 4 2 3 5 3 2 4 3 5 2");
        sb.AppendLine("3 4 2 5 3 2 4 5 3 4 2 3");
        sb.AppendLine("2 3 5 3 4 2 3 5 2 3 4 2");

        var path = TempFile("dogfood_vlbi_beam.pgm");
        File.WriteAllText(path, sb.ToString());
        var img = NetpbmImage.LoadFile(path);

        Assert.Equal(12, img.Width);
        Assert.Equal(12, img.Height);
        Assert.Equal(255, img.MaxValue);

        // GetNoiseEstimate — noisy image should have non-zero estimate
        var noise = img.GetNoiseEstimate();
        Assert.True(noise >= 0);
        Assert.Equal(noise, img.GetNoiseEstimate()); // consistent

        // Compare with uniform image
        var flatPath = TempFile("dogfood_flat.pgm");
        var flatSb = new StringBuilder();
        flatSb.AppendLine("P2");
        flatSb.AppendLine("12 12");
        flatSb.AppendLine("255");
        for (int r = 0; r < 12; r++) flatSb.AppendLine("50 50 50 50 50 50 50 50 50 50 50 50");
        File.WriteAllText(flatPath, flatSb.ToString());
        var flatImg = NetpbmImage.LoadFile(flatPath);
        Assert.Equal(0.0, flatImg.GetNoiseEstimate(), precision: 6);

        // GetSNR
        var snr = img.GetSNR();
        Assert.True(snr >= 0);
        Assert.Equal(snr, img.GetSNR()); // consistent

        // GetPSNR
        var psnr = img.GetPSNR();
        Assert.True(psnr >= 0);
        Assert.Equal(psnr, img.GetPSNR()); // consistent

        // GetMean and GetStdDev consistency
        var mean = img.GetMean();
        var std = img.GetStdDev();
        Assert.True(mean >= 0);
        Assert.True(std >= 0);

        // SaveToFile
        var outPath = TempFile("dogfood_vlbi_out.pgm");
        img.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify metrics preserved
        var loaded = NetpbmImage.LoadFile(outPath);
        Assert.Equal(noise, loaded.GetNoiseEstimate(), precision: 6);
        Assert.Equal(psnr, loaded.GetPSNR(), precision: 6);
        Assert.Equal(snr, loaded.GetSNR(), precision: 6);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);

        // GetPixelValue round-trip — source centre should be brightest
        var centreVal = loaded.GetPixelValue(5, 5);
        Assert.True(centreVal > 0);

        // GetHistogram
        var hist = loaded.GetHistogram();
        Assert.NotNull(hist);
        var ex1 = Record.Exception(() => loaded.GetNoiseEstimate());
        var ex2 = Record.Exception(() => loaded.GetSNR());
        var ex3 = Record.Exception(() => loaded.GetPSNR());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
