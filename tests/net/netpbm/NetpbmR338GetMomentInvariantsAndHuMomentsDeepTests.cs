// Tests for NetpbmImage.GetMomentInvariants, GetHuMoment deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R338

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R338: Tests for NetpbmImage.GetMomentInvariants, GetHuMoment deeper.
/// GetMomentInvariants(): returns an array of 7 Hu moment invariants for the image.
/// GetHuMoment(index): returns the n-th Hu moment invariant (0-indexed, n in [0,6]).
/// Covers: GetMomentInvariants no-throw; GetMomentInvariants length 7; GetMomentInvariants consistent;
/// GetMomentInvariants non-null;
/// GetHuMoment no-throw; GetHuMoment consistent; GetHuMoment zero index equals invariants[0];
/// GetHuMoment save-load consistent;
/// dogfood CreateDoc→GetMomentInvariants→GetHuMoment pipeline.
/// </summary>
public class NetpbmR338GetMomentInvariantsAndHuMomentsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR338GetMomentInvariantsAndHuMomentsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR338_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateUniformPgm(int width = 40, int height = 40, int value = 128)
    {
        var path = TempFile($"uniform_{value}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine($"P2\n{width} {height}\n255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
                sb.Append(value + " ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateDiskPgm(int width = 60, int height = 60, int radius = 20)
    {
        var path = TempFile("disk.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine($"P2\n{width} {height}\n255");
        int cx = width / 2, cy = height / 2;
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
            {
                double dist = Math.Sqrt((c - cx) * (c - cx) + (r - cy) * (r - cy));
                sb.Append((dist <= radius ? 255 : 0) + " ");
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateGradientPgm(int width = 50, int height = 50)
    {
        var path = TempFile("gradient.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine($"P2\n{width} {height}\n255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
                sb.Append((c * 255 / (width - 1)) + " ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetMomentInvariants
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMomentInvariants_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateDiskPgm());
        var ex = Record.Exception(() => img.GetMomentInvariants());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMomentInvariants_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateDiskPgm());
        Assert.NotNull(img.GetMomentInvariants());
    }

    [Fact]
    public void GetMomentInvariants_Length_Seven()
    {
        var img = NetpbmImage.LoadFile(CreateDiskPgm());
        var invariants = img.GetMomentInvariants();
        Assert.Equal(7, invariants.Length);
    }

    [Fact]
    public void GetMomentInvariants_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateDiskPgm());
        var inv1 = img.GetMomentInvariants();
        var inv2 = img.GetMomentInvariants();
        Assert.Equal(inv1.Length, inv2.Length);
        for (int i = 0; i < inv1.Length; i++)
            Assert.Equal(inv1[i], inv2[i]);
    }

    // -------------------------------------------------------------------------
    // GetHuMoment
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHuMoment_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateDiskPgm());
        var ex = Record.Exception(() => img.GetHuMoment(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetHuMoment_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateDiskPgm());
        Assert.Equal(img.GetHuMoment(1), img.GetHuMoment(1));
    }

    [Fact]
    public void GetHuMoment_Index0_Equals_Invariants_First()
    {
        var img = NetpbmImage.LoadFile(CreateDiskPgm());
        var inv = img.GetMomentInvariants();
        Assert.Equal(inv[0], img.GetHuMoment(0));
    }

    [Fact]
    public void GetHuMoment_AllIndices_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateDiskPgm());
        for (int i = 0; i < 7; i++)
        {
            var ex = Record.Exception(() => img.GetHuMoment(i));
            Assert.Null(ex);
        }
    }

    [Fact]
    public void GetHuMoment_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateDiskPgm());
        var before = img.GetHuMoment(0);
        var path = TempFile("hm_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetHuMoment(0));
    }

    [Fact]
    public void GetHuMoment_Gradient_AllNoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        for (int i = 0; i < 7; i++)
        {
            var ex = Record.Exception(() => img.GetHuMoment(i));
            Assert.Null(ex);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMomentInvariants_GetHuMoment_Pipeline()
    {
        // Pathology — H&E stained tissue section nuclear morphology analysis for Ki-67 proliferation index
        // Create synthetic pathology images: nuclei represented as bright discs on dark background
        var rng = new Random(20240901);
        int width = 120, height = 120;

        // Image 1: scattered nuclei (moderate proliferation)
        var path1 = TempFile("pathology_nuclei_moderate.pgm");
        var pixels1 = new int[height, width];
        // Background
        for (int r = 0; r < height; r++)
            for (int c = 0; c < width; c++)
                pixels1[r, c] = 30 + rng.Next(20);
        // Add 8 circular nuclei
        int[][] nuclei = {
            new[]{20,20,10}, new[]{20,60,12}, new[]{20,100,9},
            new[]{60,20,11}, new[]{60,60,13}, new[]{60,100,10},
            new[]{100,20,9}, new[]{100,60,11}
        };
        foreach (var n in nuclei)
            for (int r = 0; r < height; r++)
                for (int c = 0; c < width; c++)
                    if (Math.Sqrt((r - n[0]) * (r - n[0]) + (c - n[1]) * (c - n[1])) <= n[2])
                        pixels1[r, c] = 200 + rng.Next(40);

        var sb1 = new System.Text.StringBuilder();
        sb1.AppendLine($"P2\n{width} {height}\n255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
                sb1.Append(Math.Min(255, pixels1[r, c]) + " ");
            sb1.AppendLine();
        }
        File.WriteAllText(path1, sb1.ToString());

        // Image 2: uniform (background only — low proliferation)
        var path2 = TempFile("pathology_background.pgm");
        var sb2 = new System.Text.StringBuilder();
        sb2.AppendLine($"P2\n{width} {height}\n255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
                sb2.Append((40 + rng.Next(15)) + " ");
            sb2.AppendLine();
        }
        File.WriteAllText(path2, sb2.ToString());

        var img1 = NetpbmImage.LoadFile(path1);
        var img2 = NetpbmImage.LoadFile(path2);

        Assert.Equal(width, img1.Width);
        Assert.Equal(height, img1.Height);
        Assert.Equal(width, img2.Width);
        Assert.Equal(height, img2.Height);

        // GetMomentInvariants
        var inv1 = img1.GetMomentInvariants();
        Assert.NotNull(inv1);
        Assert.Equal(7, inv1.Length);
        Assert.Equal(inv1[0], img1.GetMomentInvariants()[0]); // consistent

        var inv2 = img2.GetMomentInvariants();
        Assert.NotNull(inv2);
        Assert.Equal(7, inv2.Length);

        // GetHuMoment
        for (int i = 0; i < 7; i++)
        {
            var h1 = img1.GetHuMoment(i);
            Assert.Equal(h1, img1.GetHuMoment(i)); // consistent
            Assert.Equal(inv1[i], img1.GetHuMoment(i));

            var h2 = img2.GetHuMoment(i);
            Assert.Equal(h2, img2.GetHuMoment(i));
            Assert.Equal(inv2[i], img2.GetHuMoment(i));
        }

        // Other image stats
        Assert.True(img1.GetMeanIntensity() > img2.GetMeanIntensity()); // nuclei image brighter
        Assert.True(img1.GetStdDevIntensity() >= 0.0);
        Assert.True(img2.GetStdDevIntensity() >= 0.0);

        // SaveToFile
        var outPath1 = TempFile("pathology_nuclei_out.pgm");
        img1.SaveToFile(outPath1);
        Assert.True(File.Exists(outPath1));
        Assert.True(new FileInfo(outPath1).Length > 0);

        // LoadFile and verify
        var loaded1 = NetpbmImage.LoadFile(outPath1);
        Assert.Equal(width, loaded1.Width);
        Assert.Equal(height, loaded1.Height);
        Assert.Equal(7, loaded1.GetMomentInvariants().Length);
        for (int i = 0; i < 7; i++)
            Assert.Equal(inv1[i], loaded1.GetHuMoment(i));

        // SaveToFile img2
        var outPath2 = TempFile("pathology_background_out.pgm");
        img2.SaveToFile(outPath2);
        var loaded2 = NetpbmImage.LoadFile(outPath2);
        Assert.Equal(7, loaded2.GetMomentInvariants().Length);
        var ex1 = Record.Exception(() => loaded1.GetMomentInvariants());
        var ex2 = Record.Exception(() => loaded2.GetHuMoment(6));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
