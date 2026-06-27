// Tests for ZstDocument.GetSkipFrameCount, GetSkippableFrameMetadata, GetTotalFrameSize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R249

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R249: Tests for ZstDocument.GetSkipFrameCount, GetSkippableFrameMetadata, GetTotalFrameSize deeper.
/// GetSkipFrameCount(): returns the number of skippable frames in the Zstandard file.
/// GetSkippableFrameMetadata(): returns metadata about skippable frames (or empty if none exist).
/// GetTotalFrameSize(): returns the total size of all frames (compressed + skippable) in bytes.
/// Covers: GetSkipFrameCount no-throw; GetSkipFrameCount non-negative; GetSkipFrameCount consistent;
/// GetSkipFrameCount zero for standard single-frame file;
/// GetSkippableFrameMetadata no-throw; GetSkippableFrameMetadata non-null; GetSkippableFrameMetadata consistent;
/// GetTotalFrameSize no-throw; GetTotalFrameSize positive; GetTotalFrameSize consistent;
/// GetTotalFrameSize save-load; GetTotalFrameSize at-least-compressed-size;
/// dogfood CreateDoc→GetSkipFrameCount→GetSkippableFrameMetadata→GetTotalFrameSize pipeline.
/// </summary>
public class ZstR249GetSkipFrameCountAndSkippableFrameMetadataDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR249GetSkipFrameCountAndSkippableFrameMetadataDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR249_" + Guid.NewGuid().ToString("N"));
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
        var content = System.Text.Encoding.UTF8.GetBytes(
            "id,type,value,status\n1,alpha,100,active\n2,beta,200,active\n3,gamma,300,inactive\n");
        var compressed = ZstWriter.Compress(content);
        File.WriteAllBytes(path, compressed);
        return path;
    }

    private string CreateLargerZst()
    {
        var path = TempFile("larger.zst");
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < 80; i++)
            sb.Append($"ENTRY:{i:D4}|data=value_{i * 7}|ts=2024-{(i % 12 + 1):D2}-01T00:00:00Z\n");
        var compressed = ZstWriter.Compress(System.Text.Encoding.UTF8.GetBytes(sb.ToString()));
        File.WriteAllBytes(path, compressed);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetSkipFrameCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSkipFrameCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetSkipFrameCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSkipFrameCount_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetSkipFrameCount() >= 0);
    }

    [Fact]
    public void GetSkipFrameCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetSkipFrameCount(), doc.GetSkipFrameCount());
    }

    [Fact]
    public void GetSkipFrameCount_Zero_ForStandardFrame()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        // Standard single-frame ZST files have no skippable frames
        Assert.Equal(0, doc.GetSkipFrameCount());
    }

    // -------------------------------------------------------------------------
    // GetSkippableFrameMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSkippableFrameMetadata_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetSkippableFrameMetadata());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSkippableFrameMetadata_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.NotNull(doc.GetSkippableFrameMetadata());
    }

    [Fact]
    public void GetSkippableFrameMetadata_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var m1 = doc.GetSkippableFrameMetadata();
        var m2 = doc.GetSkippableFrameMetadata();
        Assert.Equal(m1, m2);
    }

    // -------------------------------------------------------------------------
    // GetTotalFrameSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTotalFrameSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetTotalFrameSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTotalFrameSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetTotalFrameSize() > 0);
    }

    [Fact]
    public void GetTotalFrameSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetTotalFrameSize(), doc.GetTotalFrameSize());
    }

    [Fact]
    public void GetTotalFrameSize_AtLeast_CompressedSize()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetTotalFrameSize() >= doc.CompressedSize);
    }

    [Fact]
    public void GetTotalFrameSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetTotalFrameSize();
        var path = TempFile("tfs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTotalFrameSize());
    }

    [Fact]
    public void GetTotalFrameSize_LargerFile_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateLargerZst());
        Assert.True(doc.GetTotalFrameSize() > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetSkipFrameCount_GetSkippableFrameMetadata_GetTotalFrameSize_Pipeline()
    {
        // Space science — Gaia mission stellar astrometry and photometry catalogue extract
        var path = TempFile("gaia_dr3_extract.zst");
        var sb = new System.Text.StringBuilder();
        sb.Append("HEADER:GAIA_DR3_ASTROMETRY EPOCH=J2016.0 REF=ESA/DPAC CU3 VERSION=3.1.2\n");
        sb.Append("source_id\tra_deg\tdec_deg\tparallax_mas\tpmra_mas_yr\tpmdec_mas_yr\trv_km_s\tphot_g_mean_mag\tphot_bp_mean_mag\tphot_rp_mean_mag\n");

        var rng = new Random(20241101);
        for (int i = 0; i < 250; i++)
        {
            long sourceId = 4000000000000L + i * 1000000L + rng.Next(999999);
            double ra = rng.NextDouble() * 360.0;
            double dec = (rng.NextDouble() - 0.5) * 180.0;
            double parallax = 0.1 + rng.NextDouble() * 100.0; // mas
            double pmRa = (rng.NextDouble() - 0.5) * 200.0;  // mas/yr
            double pmDec = (rng.NextDouble() - 0.5) * 200.0;
            double rv = (rng.NextDouble() - 0.5) * 100.0;    // km/s (60% completeness)
            double gMag = 5.0 + rng.NextDouble() * 15.0;
            double bpMag = gMag + (rng.NextDouble() - 0.5) * 2.0;
            double rpMag = gMag - 0.3 - rng.NextDouble() * 0.8;
            string rvStr = rng.Next(5) < 3 ? $"{rv:F3}" : "null";
            sb.Append($"{sourceId}\t{ra:F6}\t{dec:F6}\t{parallax:F4}\t{pmRa:F4}\t{pmDec:F4}\t{rvStr}\t{gMag:F4}\t{bpMag:F4}\t{rpMag:F4}\n");
        }
        sb.Append("FOOTER:SOURCE_COUNT=250 EPOCH=J2016.0\n");

        var content = System.Text.Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(content);
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > doc.CompressedSize);

        // GetSkipFrameCount
        var skipCount = doc.GetSkipFrameCount();
        Assert.True(skipCount >= 0);
        Assert.Equal(skipCount, doc.GetSkipFrameCount()); // consistent

        // GetSkippableFrameMetadata
        var skipMeta = doc.GetSkippableFrameMetadata();
        Assert.NotNull(skipMeta);
        Assert.Equal(skipMeta, doc.GetSkippableFrameMetadata()); // consistent

        // GetTotalFrameSize
        var totalSize = doc.GetTotalFrameSize();
        Assert.True(totalSize > 0);
        Assert.True(totalSize >= doc.CompressedSize);
        Assert.Equal(totalSize, doc.GetTotalFrameSize()); // consistent

        // Frame-level properties
        var magic = doc.GetMagicNumber();
        Assert.Equal(0xFD2FB528u, (uint)magic);
        Assert.True(doc.FrameCount >= 1);
        Assert.True(doc.GetDictionaryId() >= 0);
        Assert.True(doc.GetWindowSize() > 0);
        Assert.True(doc.GetCompressionLevel() >= 0);

        // SearchForBytes
        var gaiaHeader = System.Text.Encoding.ASCII.GetBytes("HEADER:GAIA");
        Assert.True(doc.SearchForBytes(gaiaHeader) >= 0);
        var sourceIdPattern = System.Text.Encoding.ASCII.GetBytes("source_id");
        Assert.True(doc.SearchForBytes(sourceIdPattern) >= 0);
        var absentPattern = new byte[] { 0xCA, 0xFE, 0xBA, 0xBE };
        Assert.True(doc.SearchForBytes(absentPattern) < 0);

        // SaveToFile
        var outPath = TempFile("gaia_dr3_extract_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(skipCount, loaded.GetSkipFrameCount());
        Assert.Equal(skipMeta, loaded.GetSkippableFrameMetadata());
        Assert.Equal(totalSize, loaded.GetTotalFrameSize());
        Assert.Equal(doc.CompressedSize, loaded.CompressedSize);
        Assert.True(loaded.SearchForBytes(gaiaHeader) >= 0);

        // Compression ratio
        var ratio = doc.CompressionRatio;
        Assert.True(ratio > 1.0);
    }
}
