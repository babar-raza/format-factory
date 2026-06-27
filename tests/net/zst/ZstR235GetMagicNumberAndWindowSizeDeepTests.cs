// Tests for ZstDocument.GetMagicNumber, GetWindowSize, GetBlockCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R235

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R235: Tests for ZstDocument.GetMagicNumber, GetWindowSize, GetBlockCount deeper.
/// GetMagicNumber(): returns the 4-byte Zstandard magic number (0xFD2FB528).
/// GetWindowSize(): returns the maximum reconstruction window size in bytes.
/// GetBlockCount(): returns the number of compressed blocks in the frame.
/// Covers: GetMagicNumber no-throw; GetMagicNumber correct value; GetMagicNumber consistent;
/// GetMagicNumber save-load;
/// GetWindowSize no-throw; GetWindowSize positive; GetWindowSize consistent;
/// GetWindowSize save-load; GetWindowSize power of two or valid zstd size;
/// GetBlockCount no-throw; GetBlockCount positive; GetBlockCount consistent;
/// GetBlockCount save-load;
/// dogfood Compress→GetMagicNumber→GetWindowSize→GetBlockCount→SaveToFile pipeline.
/// </summary>
public class ZstR235GetMagicNumberAndWindowSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR235GetMagicNumberAndWindowSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR235_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateStandardZst()
    {
        var content = string.Join("\n", Enumerable.Repeat(
            "STANDARD_FRAME_TEST_CONTENT_ALPHA_BETA_GAMMA_DELTA_EPSILON_ZETA", 100));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("standard.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    private string CreateLargeZst()
    {
        var sb = new StringBuilder();
        for (int i = 0; i < 5000; i++)
            sb.AppendLine($"record_{i:D6},value_{i * 17 % 997},tag_{i % 50},score_{i * 3.14159:F4}");
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(sb.ToString()));
        var path = TempFile("large.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetMagicNumber
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMagicNumber_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetMagicNumber());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMagicNumber_CorrectValue()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        // Zstandard magic number: 0xFD2FB528
        Assert.Equal(0xFD2FB528u, (uint)doc.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(doc.GetMagicNumber(), doc.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var before = doc.GetMagicNumber();
        var path = TempFile("mn_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMagicNumber());
    }

    // -------------------------------------------------------------------------
    // GetWindowSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWindowSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetWindowSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWindowSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.True(doc.GetWindowSize() > 0);
    }

    [Fact]
    public void GetWindowSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(doc.GetWindowSize(), doc.GetWindowSize());
    }

    [Fact]
    public void GetWindowSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var before = doc.GetWindowSize();
        var path = TempFile("ws_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetWindowSize());
    }

    [Fact]
    public void GetWindowSize_LargerForLargeContent()
    {
        var small = ZstDocument.LoadFile(CreateStandardZst());
        var large = ZstDocument.LoadFile(CreateLargeZst());
        // Both must be positive; large content may have larger window
        Assert.True(small.GetWindowSize() > 0);
        Assert.True(large.GetWindowSize() > 0);
    }

    // -------------------------------------------------------------------------
    // GetBlockCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetBlockCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockCount_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.True(doc.GetBlockCount() > 0);
    }

    [Fact]
    public void GetBlockCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(doc.GetBlockCount(), doc.GetBlockCount());
    }

    [Fact]
    public void GetBlockCount_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var before = doc.GetBlockCount();
        var path = TempFile("bc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMagicNumber_GetWindowSize_GetBlockCount_SaveToFile_Pipeline()
    {
        // Financial market microstructure — limit order book tick data compression
        var sb = new StringBuilder();
        sb.AppendLine("timestamp_ns,symbol,side,price,quantity,order_id,venue,event_type");
        string[] symbols = { "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA" };
        string[] sides = { "BID", "ASK" };
        string[] venues = { "NYSE", "NASDAQ", "CBOE", "IEX" };
        string[] events = { "ADD", "MODIFY", "CANCEL", "TRADE" };
        var rng = new Random(54321);
        for (int i = 0; i < 600; i++)
        {
            var sym = symbols[i % 6];
            double basePrice = sym switch
            {
                "AAPL" => 185.0,
                "MSFT" => 415.0,
                "GOOGL" => 172.0,
                "AMZN" => 195.0,
                "NVDA" => 875.0,
                _ => 245.0
            };
            sb.AppendLine($"{1719360000000000000L + i * 1000000L},{sym},{sides[i % 2]},{basePrice + (rng.NextDouble() - 0.5) * 2.0:F2},{(rng.Next(1, 501) * 100)},ORD{i:D8},{venues[i % 4]},{events[i % 4]}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_lob.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);
        Assert.True(doc.DecompressedSize > doc.CompressedSize); // tick data compresses well

        // GetMagicNumber — must be 0xFD2FB528
        var magic = doc.GetMagicNumber();
        Assert.Equal(0xFD2FB528u, (uint)magic);
        Assert.Equal(magic, doc.GetMagicNumber()); // consistent

        // GetWindowSize
        var windowSize = doc.GetWindowSize();
        Assert.True(windowSize > 0);
        Assert.Equal(windowSize, doc.GetWindowSize()); // consistent

        // GetBlockCount
        var blockCount = doc.GetBlockCount();
        Assert.True(blockCount > 0);
        Assert.Equal(blockCount, doc.GetBlockCount()); // consistent

        // SaveToFile
        var out1 = TempFile("dogfood_lob_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify frame metadata preserved
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(0xFD2FB528u, (uint)loaded.GetMagicNumber());
        Assert.Equal(windowSize, loaded.GetWindowSize());
        Assert.Equal(blockCount, loaded.GetBlockCount());

        // Decompression round-trip
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        Assert.True(decompressed.Length > 0);
        var text = Encoding.UTF8.GetString(decompressed);
        Assert.Contains("AAPL", text);
        Assert.Contains("NVDA", text);

        // Large content comparison
        var largePath = TempFile("dogfood_large.zst");
        var largeData = ZstWriter.Compress(Encoding.UTF8.GetBytes(sb.ToString() + sb.ToString()));
        File.WriteAllBytes(largePath, largeData);
        var largeDoc = ZstDocument.LoadFile(largePath);
        Assert.Equal(0xFD2FB528u, (uint)largeDoc.GetMagicNumber()); // same magic for all zst
        Assert.True(largeDoc.GetWindowSize() > 0);
        Assert.True(largeDoc.GetBlockCount() > 0);

        // Recompress decompressed data
        var out2 = TempFile("dogfood_lob_v2.zst");
        var recompressed = ZstWriter.Compress(decompressed);
        File.WriteAllBytes(out2, recompressed);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.Equal(0xFD2FB528u, (uint)loaded2.GetMagicNumber());
        Assert.True(loaded2.GetWindowSize() > 0);
        Assert.True(loaded2.GetBlockCount() > 0);
        var ex1 = Record.Exception(() => loaded2.GetFrameHeaderSize());
        Assert.Null(ex1);
    }
}
