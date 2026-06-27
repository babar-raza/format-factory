// Tests for ZstDocument.GetFrameCount, IsMultiFrame deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R270

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R270: Tests for ZstDocument.GetFrameCount, IsMultiFrame deeper.
/// GetFrameCount(): returns the number of frames in the compressed stream; ≥ 1 for valid files.
/// IsMultiFrame(): returns true if the file contains more than one frame.
/// Covers: GetFrameCount no-throw; GetFrameCount ge 1; GetFrameCount consistent;
/// GetFrameCount save-load; IsMultiFrame no-throw; IsMultiFrame false for single-frame;
/// IsMultiFrame consistent; IsMultiFrame save-load;
/// dogfood pipeline.
/// </summary>
public class ZstR270GetFrameCountAndIsMultiFrameDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR270GetFrameCountAndIsMultiFrameDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR270_" + Guid.NewGuid().ToString("N"));
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

    private string CreateSampleZst() =>
        CreateZst("sample.zst", "Frame count test file. " + string.Concat(Enumerable.Repeat("data ", 100)));

    private string CreateLargeZst()
    {
        var sb = new StringBuilder();
        for (int i = 0; i < 300; i++)
            sb.AppendLine($"Record {i:D4}: value={i * 3.14159:F6} tag=frame_test_{i % 10}");
        return CreateZst("large.zst", sb.ToString());
    }

    // -------------------------------------------------------------------------
    // GetFrameCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetFrameCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameCount_Ge1()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetFrameCount() >= 1);
    }

    [Fact]
    public void GetFrameCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        Assert.Equal(doc.GetFrameCount(), doc.GetFrameCount());
    }

    [Fact]
    public void GetFrameCount_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var before = doc.GetFrameCount();
        var path = TempFile("fc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrameCount());
    }

    // -------------------------------------------------------------------------
    // IsMultiFrame
    // -------------------------------------------------------------------------

    [Fact]
    public void IsMultiFrame_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.IsMultiFrame());
        Assert.Null(ex);
    }

    [Fact]
    public void IsMultiFrame_False_ForSingleFrame()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        // Single-frame ZLib output should not be multi-frame
        Assert.False(doc.IsMultiFrame());
    }

    [Fact]
    public void IsMultiFrame_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.IsMultiFrame(), doc.IsMultiFrame());
    }

    [Fact]
    public void IsMultiFrame_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargeZst());
        var before = doc.IsMultiFrame();
        var path = TempFile("mf_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.IsMultiFrame());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFrameCount_IsMultiFrame_Pipeline()
    {
        // Science — CERN: CMS Detector Event Data Compressed Archives
        // LHC proton-proton collision event data compressed for long-term preservation
        // Frame count validates streaming compression format for HEP event reconstruction

        // Beam 1: Small calibration run (single compressed block)
        var path1 = TempFile("cms_calibration_run_366001.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("CMS Detector Calibration Run");
            content.AppendLine("LHC Fill: 9472 | Run: 366001 | Luminosity: 0.42 fb-1");
            content.AppendLine("Collision energy: 13.6 TeV | Bunch crossings: 2748");
            for (int i = 0; i < 100; i++)
            {
                double pt = 25 + i * 0.3;
                double eta = -2.4 + i * 0.048;
                content.AppendLine($"Event{i:D6}|pT={pt:F2}GeV|eta={eta:F4}|phi={Math.Sin(i * 0.1):F6}|nJets={i % 8}|MET={30 + i % 50:F1}GeV");
            }
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path1, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
            zlib.Write(bytes, 0, bytes.Length);
        }

        // Beam 2: Large physics run (higher volume)
        var path2 = TempFile("cms_higgsbb_run_366100.zst");
        {
            var content = new StringBuilder();
            content.AppendLine("CMS Physics Run — H→bb Analysis Data");
            content.AppendLine("Dataset: /HiggsToTwoBB/Run2024A-v1/MINIAOD");
            content.AppendLine("Golden JSON: Cert_Collisions2024_378981_385000");
            for (int i = 0; i < 350; i++)
            {
                double mbb = 80 + i * 0.3;
                double csvScore = 0.5 + (i % 50) * 0.01;
                int nBTags = 1 + i % 3;
                content.AppendLine($"Event{i:D8}|m_bb={mbb:F1}GeV|CSV_score={csvScore:F4}|n_bjets={nBTags}|trigger=HLT_PFMET110_PFMHT110|weight={1 + i * 0.001:F6}");
            }
            var bytes = Encoding.UTF8.GetBytes(content.ToString());
            using var outStream = new FileStream(path2, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.Optimal);
            zlib.Write(bytes, 0, bytes.Length);
        }

        // Metadata file
        var path3 = TempFile("cms_das_query_result.zst");
        {
            var content = "{\"dataset\":\"/HiggsToTwoBB/Run2024A\",\"files\":4821,\"events\":12483921,\"size_TB\":3.7,\"certified\":true}";
            var bytes = Encoding.UTF8.GetBytes(content);
            using var outStream = new FileStream(path3, FileMode.Create);
            using var zlib = new ZLibStream(outStream, CompressionLevel.SmallestSize);
            zlib.Write(bytes, 0, bytes.Length);
        }

        var doc1 = ZstDocument.LoadFile(path1);
        var doc2 = ZstDocument.LoadFile(path2);
        var doc3 = ZstDocument.LoadFile(path3);

        // Frame count
        var fc1 = doc1.GetFrameCount();
        var fc2 = doc2.GetFrameCount();
        var fc3 = doc3.GetFrameCount();
        Assert.True(fc1 >= 1);
        Assert.True(fc2 >= 1);
        Assert.True(fc3 >= 1);
        Assert.Equal(fc1, doc1.GetFrameCount()); // consistent
        Assert.Equal(fc2, doc2.GetFrameCount()); // consistent

        // IsMultiFrame
        var mf1 = doc1.IsMultiFrame();
        var mf2 = doc2.IsMultiFrame();
        var mf3 = doc3.IsMultiFrame();
        Assert.Equal(mf1, doc1.IsMultiFrame()); // consistent
        Assert.Equal(mf2, doc2.IsMultiFrame()); // consistent

        // Frame count and IsMultiFrame should be consistent
        if (mf1) Assert.True(fc1 > 1);
        if (!mf1) Assert.True(fc1 == 1);
        if (mf2) Assert.True(fc2 > 1);

        // Basic ZST metrics
        Assert.True(doc1.CompressedSize > 0);
        Assert.True(doc2.CompressedSize > 0);
        Assert.True(doc2.OriginalSize > doc1.OriginalSize);

        // SaveToFile
        var out1 = TempFile("cms_calibration_out.zst");
        doc1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        var loaded1 = ZstDocument.LoadFile(out1);
        Assert.Equal(fc1, loaded1.GetFrameCount());
        Assert.Equal(mf1, loaded1.IsMultiFrame());

        var out2 = TempFile("cms_higgsbb_out.zst");
        doc2.SaveToFile(out2);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.Equal(fc2, loaded2.GetFrameCount());
        Assert.Equal(mf2, loaded2.IsMultiFrame());

        Assert.Equal(doc1.OriginalSize, loaded1.OriginalSize);
        Assert.Equal(doc2.CompressedSize, loaded2.CompressedSize);

        var ex1 = Record.Exception(() => loaded1.GetFrameCount());
        var ex2 = Record.Exception(() => loaded1.IsMultiFrame());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
