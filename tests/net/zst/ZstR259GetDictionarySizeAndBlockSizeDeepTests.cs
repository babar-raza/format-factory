// Tests for ZstDocument.GetDictionarySize, GetBlockSize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R259

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R259: Tests for ZstDocument.GetDictionarySize, GetBlockSize deeper.
/// GetDictionarySize(): returns the size of the compression dictionary in bytes (0 if none used).
/// GetBlockSize(): returns the maximum block size used in the compressed frame.
/// Covers: GetDictionarySize no-throw; GetDictionarySize non-negative; GetDictionarySize consistent;
/// GetDictionarySize save-load; GetBlockSize no-throw; GetBlockSize positive;
/// GetBlockSize consistent; GetBlockSize save-load;
/// GetBlockSize <= GetContentSize; GetDictionarySize zero for standard frames;
/// dogfood CreateDoc→GetDictionarySize→GetBlockSize pipeline.
/// </summary>
public class ZstR259GetDictionarySizeAndBlockSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR259GetDictionarySizeAndBlockSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR259_" + Guid.NewGuid().ToString("N"));
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
        for (int i = 0; i < 250; i++)
            sb.AppendLine($"line_{i:D5}|data_{i * 17 % 500:D4}|type_{i % 6}|weight_{i % 12 + 1}");
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        using var ms = new MemoryStream();
        var writer = new ZstWriter(ms);
        writer.Write(raw);
        writer.Finish();
        File.WriteAllBytes(path, ms.ToArray());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetDictionarySize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDictionarySize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetDictionarySize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDictionarySize_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetDictionarySize() >= 0);
    }

    [Fact]
    public void GetDictionarySize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetDictionarySize(), doc.GetDictionarySize());
    }

    [Fact]
    public void GetDictionarySize_Zero_ForStandardFrame()
    {
        // Standard Zstandard frame without pre-trained dictionary
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(0L, doc.GetDictionarySize());
    }

    [Fact]
    public void GetDictionarySize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetDictionarySize();
        var path = TempFile("ds_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDictionarySize());
    }

    // -------------------------------------------------------------------------
    // GetBlockSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlockSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetBlockSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlockSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetBlockSize() > 0);
    }

    [Fact]
    public void GetBlockSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetBlockSize(), doc.GetBlockSize());
    }

    [Fact]
    public void GetBlockSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetBlockSize();
        var path = TempFile("bs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBlockSize());
    }

    [Fact]
    public void GetBlockSize_LessThanOrEqual_ContentSize()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetBlockSize() <= doc.GetContentSize());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDictionarySize_GetBlockSize_Pipeline()
    {
        // Satellite data processing — ESA Copernicus Sentinel-1 SAR metadata archive
        // Level-1 product annotation XML fragments: dictionary/block analysis for ingest pipeline
        var rng = new Random(20241201);
        var sb = new StringBuilder();
        sb.AppendLine("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
        sb.AppendLine("<sentinel1ProductAnnotation>");
        sb.AppendLine("  <productInfo>");
        sb.AppendLine("    <missionId>S1A</missionId>");
        sb.AppendLine("    <productType>GRD</productType>");
        sb.AppendLine("    <acquisitionMode>IW</acquisitionMode>");
        sb.AppendLine("    <polarization>VV+VH</polarization>");
        sb.AppendLine("    <processingLevel>1</processingLevel>");
        sb.AppendLine("  </productInfo>");
        sb.AppendLine("  <sliceList count=\"300\">");

        for (int i = 0; i < 300; i++)
        {
            int sliceNum = i + 1;
            double lat = 51.0 + (i * 0.01 % 2.0);
            double lon = -1.5 + (i * 0.01 % 3.0);
            long azimuthTimeEpoch = 1700000000L + (i * 2800);
            double incidenceAngle = 30.0 + rng.NextDouble() * 16.0;
            double rangePixelSpacing = 9.9 + rng.NextDouble() * 0.2;
            double azimuthPixelSpacing = 13.9 + rng.NextDouble() * 0.2;
            int lineCount = 16736 + rng.Next(200);
            int sampleCount = 26096 + rng.Next(200);
            sb.AppendLine($"    <slice sliceNumber=\"{sliceNum}\">");
            sb.AppendLine($"      <azimuthTime>{azimuthTimeEpoch}</azimuthTime>");
            sb.AppendLine($"      <latitude>{lat:F6}</latitude>");
            sb.AppendLine($"      <longitude>{lon:F6}</longitude>");
            sb.AppendLine($"      <incidenceAngle>{incidenceAngle:F4}</incidenceAngle>");
            sb.AppendLine($"      <rangePixelSpacing>{rangePixelSpacing:F4}</rangePixelSpacing>");
            sb.AppendLine($"      <azimuthPixelSpacing>{azimuthPixelSpacing:F4}</azimuthPixelSpacing>");
            sb.AppendLine($"      <lines>{lineCount}</lines>");
            sb.AppendLine($"      <samples>{sampleCount}</samples>");
            sb.AppendLine($"    </slice>");
        }

        sb.AppendLine("  </sliceList>");
        sb.AppendLine("</sentinel1ProductAnnotation>");

        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var path = TempFile("sentinel1_annotation.zst");
        using (var ms = new MemoryStream())
        {
            var writer = new ZstWriter(ms);
            writer.Write(raw);
            writer.Finish();
            File.WriteAllBytes(path, ms.ToArray());
        }
        Assert.True(File.Exists(path));

        var doc = ZstDocument.LoadFile(path);

        // GetDictionarySize — standard frame: no pre-trained dictionary
        var dictSize = doc.GetDictionarySize();
        Assert.True(dictSize >= 0);
        Assert.Equal(0L, dictSize); // standard compression: no dictionary
        Assert.Equal(dictSize, doc.GetDictionarySize()); // consistent

        // GetBlockSize
        var blockSize = doc.GetBlockSize();
        Assert.True(blockSize > 0);
        Assert.Equal(blockSize, doc.GetBlockSize()); // consistent

        // Block size ≤ content size
        Assert.True(blockSize <= doc.GetContentSize());

        // Frame properties
        Assert.True(doc.FrameCount > 0);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // XML is repetitive → good compression
        Assert.True(doc.GetThroughputRatio() >= 1.0);

        // SaveToFile
        var outPath = TempFile("sentinel1_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(dictSize, loaded.GetDictionarySize());
        Assert.Equal(blockSize, loaded.GetBlockSize());

        // Second dataset: smaller content
        var sb2 = new StringBuilder();
        sb2.AppendLine("<s1annotation><sliceList count=\"5\">");
        for (int i = 0; i < 5; i++)
            sb2.AppendLine($"  <slice sliceNumber=\"{i + 1}\"><azimuthTime>{1700000000L + i * 2800}</azimuthTime></slice>");
        sb2.AppendLine("</sliceList></s1annotation>");
        var raw2 = Encoding.UTF8.GetBytes(sb2.ToString());
        var path2 = TempFile("sentinel1_small.zst");
        using (var ms2 = new MemoryStream())
        {
            var w2 = new ZstWriter(ms2);
            w2.Write(raw2);
            w2.Finish();
            File.WriteAllBytes(path2, ms2.ToArray());
        }
        var doc2 = ZstDocument.LoadFile(path2);
        Assert.Equal(0L, doc2.GetDictionarySize()); // still no dictionary
        Assert.True(doc2.GetBlockSize() > 0);
        // Larger doc has greater content
        Assert.True(doc.GetContentSize() > doc2.GetContentSize());

        var ex1 = Record.Exception(() => loaded.GetDictionarySize());
        var ex2 = Record.Exception(() => loaded.GetBlockSize());
        var ex3 = Record.Exception(() => loaded.GetCompressionRatio());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
