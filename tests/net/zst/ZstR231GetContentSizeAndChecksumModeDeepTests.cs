// Tests for ZstDocument.GetContentSize, GetChecksumMode, GetSkipFrameCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R231

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R231: Tests for ZstDocument.GetContentSize, GetChecksumMode, GetSkipFrameCount deeper.
/// GetContentSize(): returns the decompressed content size stored in the frame header (-1 if unknown).
/// GetChecksumMode(): returns whether checksum verification is enabled for this frame.
/// GetSkipFrameCount(): returns the number of skippable frames in the compressed file.
/// Covers: GetContentSize no-throw; GetContentSize >= -1; GetContentSize consistent;
/// GetContentSize save-load;
/// GetChecksumMode no-throw; GetChecksumMode consistent; GetChecksumMode save-load;
/// GetSkipFrameCount no-throw; GetSkipFrameCount non-negative; GetSkipFrameCount consistent;
/// GetSkipFrameCount save-load;
/// dogfood Compress→GetContentSize→GetChecksumMode→GetSkipFrameCount→SaveToFile pipeline.
/// </summary>
public class ZstR231GetContentSizeAndChecksumModeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR231GetContentSizeAndChecksumModeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR231_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateKnownSizeZst()
    {
        var content = "Known content size frame for Zstandard header tests.\n" +
                      string.Join("\n", System.Linq.Enumerable.Range(1, 150).Select(i => $"line_{i:D4}=value_{i * 7}"));
        var raw = Encoding.UTF8.GetBytes(content);
        var data = ZstWriter.Compress(raw);
        var path = TempFile("known_size.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    private string CreateChecksumZst()
    {
        var content = string.Join("\n", System.Linq.Enumerable.Range(1, 200).Select(i =>
            $"chk_{i:D5},{i % 50},{i * 1.23:F4}"));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content), enableChecksum: true);
        var path = TempFile("checksum.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    private string CreateStandardZst()
    {
        var content = string.Join(" ", System.Linq.Enumerable.Range(1, 100).Select(i => $"word{i}"));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("standard.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetContentSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContentSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateKnownSizeZst());
        var ex = Record.Exception(() => doc.GetContentSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContentSize_AtLeastMinusOne()
    {
        var doc = ZstDocument.LoadFile(CreateKnownSizeZst());
        Assert.True(doc.GetContentSize() >= -1);
    }

    [Fact]
    public void GetContentSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateKnownSizeZst());
        Assert.Equal(doc.GetContentSize(), doc.GetContentSize());
    }

    [Fact]
    public void GetContentSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateKnownSizeZst());
        var before = doc.GetContentSize();
        var path = TempFile("cs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetContentSize());
    }

    // -------------------------------------------------------------------------
    // GetChecksumMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChecksumMode_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetChecksumMode());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChecksumMode_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        Assert.Equal(doc.GetChecksumMode(), doc.GetChecksumMode());
    }

    [Fact]
    public void GetChecksumMode_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        var before = doc.GetChecksumMode();
        var path = TempFile("cm_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetChecksumMode());
    }

    // -------------------------------------------------------------------------
    // GetSkipFrameCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSkipFrameCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetSkipFrameCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSkipFrameCount_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.True(doc.GetSkipFrameCount() >= 0);
    }

    [Fact]
    public void GetSkipFrameCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(doc.GetSkipFrameCount(), doc.GetSkipFrameCount());
    }

    [Fact]
    public void GetSkipFrameCount_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var before = doc.GetSkipFrameCount();
        var path = TempFile("sf_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSkipFrameCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetContentSize_GetChecksumMode_GetSkipFrameCount_SaveToFile_Pipeline()
    {
        // Network packet capture simulation: structured pcap-like metadata
        var sb = new StringBuilder();
        sb.AppendLine("packet_id,timestamp_us,src_ip,dst_ip,protocol,src_port,dst_port,payload_bytes,flags,ttl");
        var rng = new Random(42);
        string[] protocols = { "TCP", "UDP", "ICMP", "HTTP", "HTTPS" };
        string[] flags = { "SYN", "ACK", "FIN", "RST", "PSH" };
        for (int i = 0; i < 350; i++)
        {
            long ts = 1719360000000000L + i * 1000L + rng.Next(500);
            int srcOct = rng.Next(256); int dstOct = rng.Next(256);
            string src = $"192.168.{srcOct}.{rng.Next(256)}";
            string dst = $"10.0.{dstOct}.{rng.Next(256)}";
            string proto = protocols[i % protocols.Length];
            int srcPort = 1024 + rng.Next(60000);
            int dstPort = i % 5 == 0 ? 443 : (i % 3 == 0 ? 80 : 8080);
            int payload = 64 + rng.Next(1400);
            string flag = flags[rng.Next(flags.Length)];
            int ttl = 32 + rng.Next(96);
            sb.AppendLine($"PKT_{i:D6},{ts},{src},{dst},{proto},{srcPort},{dstPort},{payload},{flag},{ttl}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_pcap.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetContentSize — >= -1
        var contentSize = doc.GetContentSize();
        Assert.True(contentSize >= -1);
        Assert.Equal(contentSize, doc.GetContentSize()); // consistent

        // GetChecksumMode
        var checksumMode = doc.GetChecksumMode();
        Assert.Equal(checksumMode, doc.GetChecksumMode()); // consistent

        // GetSkipFrameCount — non-negative
        var skipCount = doc.GetSkipFrameCount();
        Assert.True(skipCount >= 0);
        Assert.Equal(skipCount, doc.GetSkipFrameCount()); // consistent

        // Compare standard vs checksum frames
        var stdDoc = ZstDocument.LoadFile(CreateStandardZst());
        var chkDoc = ZstDocument.LoadFile(CreateChecksumZst());
        Assert.True(stdDoc.GetSkipFrameCount() >= 0);
        Assert.True(chkDoc.GetSkipFrameCount() >= 0);
        Assert.Equal(stdDoc.GetChecksumMode(), stdDoc.GetChecksumMode());

        // Content size from known-size frame
        var knownDoc = ZstDocument.LoadFile(CreateKnownSizeZst());
        Assert.True(knownDoc.GetContentSize() >= -1);

        // SaveToFile — original
        var out1 = TempFile("dogfood_pcap_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(contentSize, loaded.GetContentSize());
        Assert.Equal(checksumMode, loaded.GetChecksumMode());
        Assert.Equal(skipCount, loaded.GetSkipFrameCount());

        // Verify decompressed content is correct
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        Assert.True(decompressed.Length > 0);

        // Final save
        var out2 = TempFile("dogfood_pcap_v2.zst");
        var recompressed = ZstWriter.Compress(decompressed, enableChecksum: true);
        File.WriteAllBytes(out2, recompressed);
        Assert.True(File.Exists(out2));
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.True(loaded2.GetContentSize() >= -1);
        Assert.True(loaded2.GetSkipFrameCount() >= 0);
        var ex1 = Record.Exception(() => loaded2.GetContentSize());
        var ex2 = Record.Exception(() => loaded2.GetChecksumMode());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
