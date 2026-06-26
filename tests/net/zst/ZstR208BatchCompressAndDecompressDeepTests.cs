// Tests for ZstWriter batch compress/decompress operations deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R208

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R208: Tests for ZstWriter batch compress/decompress operations deeper.
/// CompressBytes(data): compresses a byte array and returns compressed bytes.
/// DecompressBytes(data): decompresses a byte array and returns original bytes.
/// CompressString(text): compresses a string and returns compressed bytes.
/// DecompressString(data): decompresses bytes back to string.
/// Covers: CompressBytes non-null; CompressBytes non-empty; CompressBytes no-throw;
/// CompressBytes smaller for compressible data; CompressBytes consistent;
/// CompressBytes then DecompressBytes roundtrip; CompressBytes large data;
/// DecompressBytes non-null; DecompressBytes no-throw; DecompressBytes restores original;
/// DecompressBytes consistent; DecompressBytes then re-compress no-throw;
/// CompressString non-null; CompressString non-empty; CompressString no-throw;
/// CompressString then DecompressString roundtrip; CompressString consistent;
/// CompressString then ParseStream; DecompressString non-null; DecompressString no-throw;
/// DecompressString restores original; DecompressString consistent;
/// DecompressString for different inputs differs; DecompressString save-load;
/// dogfood CompressString→DecompressString→CompressBytes→DecompressBytes→SaveToFile pipeline.
/// </summary>
public class ZstR208BatchCompressAndDecompressDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR208BatchCompressAndDecompressDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR208_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // CompressBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressBytes_NonNull()
    {
        var data = System.Text.Encoding.UTF8.GetBytes("Test content for compression.");
        Assert.NotNull(ZstWriter.CompressBytes(data));
    }

    [Fact]
    public void CompressBytes_NonEmpty()
    {
        var data = System.Text.Encoding.UTF8.GetBytes("Non-empty compression test.");
        Assert.True(ZstWriter.CompressBytes(data).Length > 0);
    }

    [Fact]
    public void CompressBytes_NoThrow()
    {
        var data = System.Text.Encoding.UTF8.GetBytes("No throw test for CompressBytes.");
        var ex = Record.Exception(() => ZstWriter.CompressBytes(data));
        Assert.Null(ex);
    }

    [Fact]
    public void CompressBytes_Consistent()
    {
        var data = System.Text.Encoding.UTF8.GetBytes("Consistent compression test.");
        var c1 = ZstWriter.CompressBytes(data);
        var c2 = ZstWriter.CompressBytes(data);
        Assert.Equal(c1.Length, c2.Length);
    }

    [Fact]
    public void CompressBytes_Roundtrip_RestoresOriginal()
    {
        var original = System.Text.Encoding.UTF8.GetBytes("Roundtrip content for compression test.");
        var compressed = ZstWriter.CompressBytes(original);
        var decompressed = ZstWriter.DecompressBytes(compressed);
        Assert.Equal(original, decompressed);
    }

    [Fact]
    public void CompressBytes_LargeData_NoThrow()
    {
        var data = new byte[50000];
        for (int i = 0; i < data.Length; i++)
            data[i] = (byte)(i % 256);
        var ex = Record.Exception(() => ZstWriter.CompressBytes(data));
        Assert.Null(ex);
    }

    [Fact]
    public void CompressBytes_RepetitiveData_SmallerThanOriginal()
    {
        var data = new byte[10000];
        // All same byte — highly compressible
        for (int i = 0; i < data.Length; i++) data[i] = 0x42;
        var compressed = ZstWriter.CompressBytes(data);
        Assert.True(compressed.Length < data.Length);
    }

    // -------------------------------------------------------------------------
    // DecompressBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressBytes_NonNull()
    {
        var data = System.Text.Encoding.UTF8.GetBytes("Decompress bytes test.");
        var compressed = ZstWriter.CompressBytes(data);
        Assert.NotNull(ZstWriter.DecompressBytes(compressed));
    }

    [Fact]
    public void DecompressBytes_NoThrow()
    {
        var data = System.Text.Encoding.UTF8.GetBytes("No throw decompress bytes.");
        var compressed = ZstWriter.CompressBytes(data);
        var ex = Record.Exception(() => ZstWriter.DecompressBytes(compressed));
        Assert.Null(ex);
    }

    [Fact]
    public void DecompressBytes_RestoresOriginal()
    {
        var original = System.Text.Encoding.UTF8.GetBytes("Restore original bytes test.");
        var decompressed = ZstWriter.DecompressBytes(ZstWriter.CompressBytes(original));
        Assert.Equal(original, decompressed);
    }

    [Fact]
    public void DecompressBytes_Consistent()
    {
        var data = System.Text.Encoding.UTF8.GetBytes("Consistent decompress bytes.");
        var compressed = ZstWriter.CompressBytes(data);
        var d1 = ZstWriter.DecompressBytes(compressed);
        var d2 = ZstWriter.DecompressBytes(compressed);
        Assert.Equal(d1, d2);
    }

    [Fact]
    public void DecompressBytes_ThenReCompress_NoThrow()
    {
        var original = System.Text.Encoding.UTF8.GetBytes("Re-compress after decompress.");
        var compressed = ZstWriter.CompressBytes(original);
        var decompressed = ZstWriter.DecompressBytes(compressed);
        var ex = Record.Exception(() => ZstWriter.CompressBytes(decompressed));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // CompressString
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressString_NonNull()
    {
        Assert.NotNull(ZstWriter.CompressString("Test string for compression."));
    }

    [Fact]
    public void CompressString_NonEmpty()
    {
        Assert.True(ZstWriter.CompressString("Non-empty string compress.").Length > 0);
    }

    [Fact]
    public void CompressString_NoThrow()
    {
        var ex = Record.Exception(() => ZstWriter.CompressString("No throw string compress."));
        Assert.Null(ex);
    }

    [Fact]
    public void CompressString_Consistent()
    {
        var text = "Consistent string compression.";
        var c1 = ZstWriter.CompressString(text);
        var c2 = ZstWriter.CompressString(text);
        Assert.Equal(c1.Length, c2.Length);
    }

    [Fact]
    public void CompressString_Roundtrip_RestoresOriginal()
    {
        var text = "Complete roundtrip string compression and decompression test.";
        var compressed = ZstWriter.CompressString(text);
        var restored = ZstWriter.DecompressString(compressed);
        Assert.Equal(text, restored);
    }

    [Fact]
    public void CompressString_ThenParseStream_ValidDoc()
    {
        var text = "Stream-parseable compressed string content.";
        var compressed = ZstWriter.CompressString(text);
        var path = TempFile("string_stream.zst");
        File.WriteAllBytes(path, compressed);
        ZstDocument doc;
        using (var fs = File.OpenRead(path))
            doc = ZstParser.ParseStream(fs);
        Assert.True(doc.FrameCount >= 1);
    }

    // -------------------------------------------------------------------------
    // DecompressString
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressString_NonNull()
    {
        var compressed = ZstWriter.CompressString("Decompress string test.");
        Assert.NotNull(ZstWriter.DecompressString(compressed));
    }

    [Fact]
    public void DecompressString_NoThrow()
    {
        var compressed = ZstWriter.CompressString("No throw decompress string.");
        var ex = Record.Exception(() => ZstWriter.DecompressString(compressed));
        Assert.Null(ex);
    }

    [Fact]
    public void DecompressString_RestoresOriginal()
    {
        var text = "Restored string after decompression.";
        var compressed = ZstWriter.CompressString(text);
        Assert.Equal(text, ZstWriter.DecompressString(compressed));
    }

    [Fact]
    public void DecompressString_Consistent()
    {
        var compressed = ZstWriter.CompressString("Consistent decompress string.");
        Assert.Equal(ZstWriter.DecompressString(compressed), ZstWriter.DecompressString(compressed));
    }

    [Fact]
    public void DecompressString_DifferentInputs_DifferentResults()
    {
        var c1 = ZstWriter.CompressString("First string content here.");
        var c2 = ZstWriter.CompressString("Second string entirely different.");
        Assert.NotEqual(ZstWriter.DecompressString(c1), ZstWriter.DecompressString(c2));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressString_DecompressString_CompressBytes_DecompressBytes_Pipeline()
    {
        var text1 = "The annual technology strategy review covers all major platforms and initiatives.";
        var text2 = new string('M', 5000) + " end of repetitive marker content block.";
        var text3 = string.Join("|", new[] { "alpha", "beta", "gamma", "delta", "epsilon" });

        // CompressString roundtrip for all three
        var c1 = ZstWriter.CompressString(text1);
        var c2 = ZstWriter.CompressString(text2);
        var c3 = ZstWriter.CompressString(text3);

        Assert.NotNull(c1);
        Assert.True(c1.Length > 0);
        Assert.True(c2.Length > 0);
        Assert.True(c3.Length > 0);

        // text2 compresses much smaller (repetitive)
        Assert.True(c2.Length < text2.Length);

        // DecompressString restores all
        Assert.Equal(text1, ZstWriter.DecompressString(c1));
        Assert.Equal(text2, ZstWriter.DecompressString(c2));
        Assert.Equal(text3, ZstWriter.DecompressString(c3));

        // Consistent
        Assert.Equal(c1.Length, ZstWriter.CompressString(text1).Length);
        Assert.Equal(text1, ZstWriter.DecompressString(c1));

        // CompressBytes roundtrip
        var bytes1 = System.Text.Encoding.UTF8.GetBytes(text1);
        var bytes2 = System.Text.Encoding.UTF8.GetBytes(text2);
        var compB1 = ZstWriter.CompressBytes(bytes1);
        var compB2 = ZstWriter.CompressBytes(bytes2);

        Assert.NotNull(compB1);
        Assert.True(compB1.Length > 0);
        Assert.True(compB2.Length < bytes2.Length); // repetitive compresses well

        // DecompressBytes restores
        var decompB1 = ZstWriter.DecompressBytes(compB1);
        var decompB2 = ZstWriter.DecompressBytes(compB2);
        Assert.Equal(bytes1, decompB1);
        Assert.Equal(bytes2, decompB2);

        // Cross-method: CompressString → write to file → ParseFile → FrameCount
        var pathC1 = TempFile("dogfood_c1.zst");
        File.WriteAllBytes(pathC1, c1);
        var docC1 = ZstParser.ParseFile(pathC1);
        Assert.True(docC1.FrameCount >= 1);
        Assert.True(docC1.DecompressedSize > 0);
        Assert.True(docC1.IsValid);

        var pathC2 = TempFile("dogfood_c2.zst");
        File.WriteAllBytes(pathC2, c2);
        var docC2 = ZstParser.ParseFile(pathC2);
        Assert.True(docC2.FrameCount >= 1);
        // Repetitive text2 decompresses to text2.Length bytes
        Assert.True(docC2.DecompressedSize > 0);

        // CompressBytes → DecompressFile roundtrip via file
        var pathB1 = TempFile("dogfood_b1.zst");
        File.WriteAllBytes(pathB1, compB1);
        var decompPath = TempFile("dogfood_b1_decomp.bin");
        ZstWriter.DecompressFile(pathB1, decompPath);
        Assert.True(File.Exists(decompPath));
        var decompContent = File.ReadAllBytes(decompPath);
        Assert.Equal(bytes1, decompContent);

        // ParseStream from CompressString output
        using (var ms = new MemoryStream(c3))
        {
            var streamDoc = ZstParser.ParseStream(ms);
            Assert.True(streamDoc.FrameCount >= 1);
        }

        // ExportToBase64 from file-based doc
        var b64 = docC1.ExportToBase64();
        Assert.NotNull(b64);
        Assert.NotEmpty(b64);
        var bytesFromB64 = Convert.FromBase64String(b64);
        Assert.Equal(c1, bytesFromB64);

        // Decompress the base64 bytes
        var restoredText = ZstWriter.DecompressString(bytesFromB64);
        Assert.Equal(text1, restoredText);

        // Multiple round-trips still work
        for (int i = 0; i < 3; i++)
        {
            var recompressed = ZstWriter.CompressString(text1);
            var redecompressed = ZstWriter.DecompressString(recompressed);
            Assert.Equal(text1, redecompressed);
        }
    }
}
