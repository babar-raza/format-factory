// Tests for ZstDocument.GetFrameSize, GetContentSize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R255

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R255: Tests for ZstDocument.GetFrameSize, GetContentSize deeper.
/// GetFrameSize(): returns the compressed size of the Zstandard frame in bytes.
/// GetContentSize(): returns the original (uncompressed) content size in bytes.
/// Covers: GetFrameSize no-throw; GetFrameSize positive; GetFrameSize consistent;
/// GetFrameSize save-load; GetContentSize no-throw; GetContentSize positive;
/// GetContentSize greater-than-or-equal-to GetFrameSize for compressible data;
/// GetContentSize consistent; GetContentSize save-load;
/// dogfood CreateDoc→GetFrameSize→GetContentSize pipeline.
/// </summary>
public class ZstR255GetFrameSizeAndContentSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR255GetFrameSizeAndContentSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR255_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleZst()
    {
        var path = TempFile("sample.zst");
        var sb = new StringBuilder();
        for (int i = 0; i < 200; i++)
            sb.AppendLine($"record_{i:D6}|value_{i * 7 % 1000:D6}|category_{i % 10}|score_{i % 5 + 1}");
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        using var ms = new MemoryStream();
        var writer = new ZstWriter(ms);
        writer.Write(raw);
        writer.Finish();
        File.WriteAllBytes(path, ms.ToArray());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFrameSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetFrameSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetFrameSize() > 0);
    }

    [Fact]
    public void GetFrameSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetFrameSize(), doc.GetFrameSize());
    }

    [Fact]
    public void GetFrameSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetFrameSize();
        var path = TempFile("fs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrameSize());
    }

    // -------------------------------------------------------------------------
    // GetContentSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContentSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetContentSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContentSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetContentSize() > 0);
    }

    [Fact]
    public void GetContentSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetContentSize(), doc.GetContentSize());
    }

    [Fact]
    public void GetContentSize_GreaterOrEqualToFrameSize()
    {
        // Compressible text data: content size >= frame size
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetContentSize() >= doc.GetFrameSize());
    }

    [Fact]
    public void GetContentSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetContentSize();
        var path = TempFile("cs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetContentSize());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFrameSize_GetContentSize_Pipeline()
    {
        // Scientific computing — CERN CMS open data ROOT-format subset
        // LHC Run 2 dimuon event kinematics compressed for analysis pipeline
        var rng = new Random(20241115);
        var sb = new StringBuilder();

        // CSV-like structure: run,luminosityBlock,event,pt1,eta1,phi1,pt2,eta2,phi2,invMass
        sb.AppendLine("run,lb,event,pt1_gev,eta1,phi1_rad,pt2_gev,eta2,phi2_rad,invmass_gev,type");
        for (int i = 0; i < 250; i++)
        {
            int run = 315252 + rng.Next(3);
            int lb = rng.Next(1, 2000);
            long evt = 1000000L + rng.Next(100000);
            double pt1 = 5 + rng.NextDouble() * 95;
            double eta1 = -2.4 + rng.NextDouble() * 4.8;
            double phi1 = -Math.PI + rng.NextDouble() * 2 * Math.PI;
            double pt2 = 5 + rng.NextDouble() * 95;
            double eta2 = -2.4 + rng.NextDouble() * 4.8;
            double phi2 = -Math.PI + rng.NextDouble() * 2 * Math.PI;
            // Approximate invariant mass
            double invMass = Math.Sqrt(2 * pt1 * pt2 * (Math.Cosh(eta1 - eta2) - Math.Cos(phi1 - phi2)));
            string[] types = { "SS", "OS" };
            sb.AppendLine($"{run},{lb},{evt},{pt1:F3},{eta1:F4},{phi1:F4},{pt2:F3},{eta2:F4},{phi2:F4},{invMass:F3},{types[i % 2]}");
        }

        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var path = TempFile("cms_dimuon.zst");
        using (var ms = new MemoryStream())
        {
            var writer = new ZstWriter(ms);
            writer.Write(raw);
            writer.Finish();
            File.WriteAllBytes(path, ms.ToArray());
        }
        Assert.True(File.Exists(path));

        var doc = ZstDocument.LoadFile(path);

        // GetFrameSize
        var frameSize = doc.GetFrameSize();
        Assert.True(frameSize > 0);
        Assert.Equal(frameSize, doc.GetFrameSize()); // consistent

        // GetContentSize
        var contentSize = doc.GetContentSize();
        Assert.True(contentSize > 0);
        Assert.Equal(contentSize, doc.GetContentSize()); // consistent

        // Compressible CSV: content should exceed frame
        Assert.True(contentSize >= frameSize);

        // Ratio: content / frame ≥ 1 (compression applied)
        double ratio = (double)contentSize / frameSize;
        Assert.True(ratio >= 1.0);

        // Frame size should be less than raw size (good compression on repetitive CSV)
        Assert.True(frameSize < raw.Length);

        // Basic doc properties
        Assert.True(doc.FrameCount > 0);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // SaveToFile
        var outPath = TempFile("cms_dimuon_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(frameSize, loaded.GetFrameSize());
        Assert.Equal(contentSize, loaded.GetContentSize());

        // No-throw checks
        var ex1 = Record.Exception(() => loaded.GetFrameSize());
        var ex2 = Record.Exception(() => loaded.GetContentSize());
        var ex3 = Record.Exception(() => loaded.GetCompressionRatio());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);

        // Second dataset: smaller content for comparison
        var sb2 = new StringBuilder();
        sb2.AppendLine("run,event,invmass");
        for (int i = 0; i < 20; i++)
            sb2.AppendLine($"{315252},{i},{(88 + rng.NextDouble() * 5):F2}");
        var raw2 = Encoding.UTF8.GetBytes(sb2.ToString());
        var path2 = TempFile("cms_small.zst");
        using (var ms2 = new MemoryStream())
        {
            var w2 = new ZstWriter(ms2);
            w2.Write(raw2);
            w2.Finish();
            File.WriteAllBytes(path2, ms2.ToArray());
        }
        var doc2 = ZstDocument.LoadFile(path2);
        Assert.True(doc2.GetFrameSize() > 0);
        Assert.True(doc2.GetContentSize() > 0);
        // Larger dataset should have larger content size
        Assert.True(contentSize > doc2.GetContentSize());
    }
}
