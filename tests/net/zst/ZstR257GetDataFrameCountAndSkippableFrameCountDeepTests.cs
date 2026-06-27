// Tests for ZstDocument.GetDataFrameCount, GetSkippableFrameCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R257

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R257: Tests for ZstDocument.GetDataFrameCount, GetSkippableFrameCount deeper.
/// GetDataFrameCount(): returns the count of Zstandard data frames in the file.
/// GetSkippableFrameCount(): returns the count of skippable frames (magic 0x184D2A50-5F).
/// Covers: GetDataFrameCount no-throw; GetDataFrameCount positive;
/// GetDataFrameCount consistent; GetDataFrameCount equals FrameCount for simple files;
/// GetDataFrameCount save-load;
/// GetSkippableFrameCount no-throw; GetSkippableFrameCount non-negative;
/// GetSkippableFrameCount zero for standard file; GetSkippableFrameCount consistent;
/// GetSkippableFrameCount save-load;
/// dogfood CreateDoc→GetDataFrameCount→GetSkippableFrameCount pipeline.
/// </summary>
public class ZstR257GetDataFrameCountAndSkippableFrameCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR257GetDataFrameCountAndSkippableFrameCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR257_" + Guid.NewGuid().ToString("N"));
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
        for (int i = 0; i < 150; i++)
            sb.AppendLine($"line_{i:D5}|value_{i * 7 % 100}|tag_{i % 10}");
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        using var ms = new MemoryStream();
        var writer = new ZstWriter(ms);
        writer.Write(raw);
        writer.Finish();
        File.WriteAllBytes(path, ms.ToArray());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetDataFrameCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDataFrameCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetDataFrameCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDataFrameCount_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetDataFrameCount() > 0);
    }

    [Fact]
    public void GetDataFrameCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetDataFrameCount(), doc.GetDataFrameCount());
    }

    [Fact]
    public void GetDataFrameCount_EqualsFrameCount_ForSimpleFile()
    {
        // Standard single-frame file: GetDataFrameCount == FrameCount
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.FrameCount, doc.GetDataFrameCount() + doc.GetSkippableFrameCount());
    }

    [Fact]
    public void GetDataFrameCount_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetDataFrameCount();
        var path = TempFile("dfc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDataFrameCount());
    }

    // -------------------------------------------------------------------------
    // GetSkippableFrameCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSkippableFrameCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetSkippableFrameCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSkippableFrameCount_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetSkippableFrameCount() >= 0);
    }

    [Fact]
    public void GetSkippableFrameCount_Zero_ForStandardFile()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(0, doc.GetSkippableFrameCount());
    }

    [Fact]
    public void GetSkippableFrameCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetSkippableFrameCount(), doc.GetSkippableFrameCount());
    }

    [Fact]
    public void GetSkippableFrameCount_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetSkippableFrameCount();
        var path = TempFile("sfc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSkippableFrameCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDataFrameCount_GetSkippableFrameCount_Pipeline()
    {
        // Bioinformatics — Oxford Nanopore Technologies (ONT) FAST5 metadata compression
        // POD5 format compressed read metadata: frame counting for streaming alignment pipeline
        var rng = new Random(20241201);
        var sb = new StringBuilder();

        // Simulate ONT read summary fields (subset of sequencing_summary.txt)
        sb.AppendLine("read_id\tchannel\tmux\tstart_time\tduration\tnum_events\ttemplate_start\ttemplate_duration\tnum_called_template\tsequence_length_template\tmean_qscore_template\tstrand_score");
        for (int i = 0; i < 280; i++)
        {
            string readId = $"{Guid.NewGuid():N}".Substring(0, 36);
            // Simulate: 36-char UUID format XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
            readId = $"{rng.Next(0x10000000):x8}-{rng.Next(0x10000):x4}-{rng.Next(0x10000):x4}-{rng.Next(0x10000):x4}-{rng.Next(0x10000000):x8}{rng.Next(0x10000):x4}";
            int channel = 1 + rng.Next(512);
            int mux = 1 + rng.Next(4);
            double startTime = i * 0.15 + rng.NextDouble() * 0.05;
            double duration = 1.5 + rng.NextDouble() * 8.0;
            int numEvents = (int)(duration * 400 + rng.NextDouble() * 200);
            double templStart = startTime + 0.05 + rng.NextDouble() * 0.1;
            double templDur = duration - 0.12 - rng.NextDouble() * 0.08;
            int numCalled = (int)(templDur * 350 + rng.NextDouble() * 150);
            int seqLen = (int)(templDur * 450 + rng.NextDouble() * 200);
            double qscore = 8 + rng.NextDouble() * 14;
            double strandScore = 0.5 + rng.NextDouble() * 0.45;
            sb.AppendLine($"{readId}\t{channel}\t{mux}\t{startTime:F3}\t{duration:F3}\t{numEvents}\t{templStart:F3}\t{templDur:F3}\t{numCalled}\t{seqLen}\t{qscore:F2}\t{strandScore:F4}");
        }

        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var path = TempFile("ont_reads.zst");
        using (var ms = new MemoryStream())
        {
            var writer = new ZstWriter(ms);
            writer.Write(raw);
            writer.Finish();
            File.WriteAllBytes(path, ms.ToArray());
        }

        var doc = ZstDocument.LoadFile(path);

        // GetDataFrameCount
        var dfc = doc.GetDataFrameCount();
        Assert.True(dfc > 0);
        Assert.Equal(dfc, doc.GetDataFrameCount()); // consistent

        // GetSkippableFrameCount
        var sfc = doc.GetSkippableFrameCount();
        Assert.True(sfc >= 0);
        Assert.Equal(sfc, doc.GetSkippableFrameCount()); // consistent

        // Standard file: no skippable frames
        Assert.Equal(0, sfc);

        // Frame conservation: data + skippable = total
        Assert.Equal(doc.FrameCount, dfc + sfc);

        // Basic properties
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);
        Assert.True(doc.GetFrameSize() > 0);
        Assert.True(doc.GetContentSize() > 0);

        // SaveToFile
        var outPath = TempFile("ont_reads_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(dfc, loaded.GetDataFrameCount());
        Assert.Equal(sfc, loaded.GetSkippableFrameCount());
        Assert.Equal(doc.FrameCount, loaded.FrameCount);

        // Second dataset for comparison
        var sb2 = new StringBuilder();
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"read_{i}\t{rng.Next(512)}\t{rng.Next(4) + 1}\t{i * 0.2:F3}");
        var raw2 = Encoding.UTF8.GetBytes(sb2.ToString());
        var path2 = TempFile("ont_small.zst");
        using (var ms2 = new MemoryStream())
        {
            var w2 = new ZstWriter(ms2);
            w2.Write(raw2);
            w2.Finish();
            File.WriteAllBytes(path2, ms2.ToArray());
        }
        var doc2 = ZstDocument.LoadFile(path2);
        Assert.True(doc2.GetDataFrameCount() > 0);
        Assert.Equal(0, doc2.GetSkippableFrameCount());

        // No-throw
        var ex1 = Record.Exception(() => loaded.GetCompressionRatio());
        var ex2 = Record.Exception(() => loaded.GetCompressionLevel());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
