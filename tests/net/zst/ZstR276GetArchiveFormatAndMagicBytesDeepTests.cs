// Tests for ZstDocument.GetArchiveFormat, GetMagicBytes deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R276

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R276: Tests for ZstDocument.GetArchiveFormat, GetMagicBytes deeper.
/// GetArchiveFormat(): returns a string describing the compression archive format (e.g. "zlib", "zstd").
/// GetMagicBytes(): returns the magic byte signature of the archive as a hex string or byte array string.
/// Covers: GetArchiveFormat no-throw; GetArchiveFormat non-null; GetArchiveFormat non-empty;
/// GetArchiveFormat consistent; GetArchiveFormat save-load;
/// GetMagicBytes no-throw; GetMagicBytes non-null; GetMagicBytes non-empty;
/// GetMagicBytes consistent; GetMagicBytes save-load; dogfood pipeline.
/// </summary>
public class ZstR276GetArchiveFormatAndMagicBytesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR276GetArchiveFormatAndMagicBytesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR276_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleZst(string name = "sample.zst")
    {
        var path = TempFile(name);
        var src = Encoding.UTF8.GetBytes(
            string.Concat(Enumerable.Repeat("Archive format test content with repeating data. ", 100)));
        using var fs = File.Create(path);
        using var zs = new ZLibStream(fs, CompressionLevel.Optimal, leaveOpen: true);
        zs.Write(src, 0, src.Length);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetArchiveFormat
    // -------------------------------------------------------------------------

    [Fact]
    public void GetArchiveFormat_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetArchiveFormat());
        Assert.Null(ex);
    }

    [Fact]
    public void GetArchiveFormat_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.NotNull(doc.GetArchiveFormat());
    }

    [Fact]
    public void GetArchiveFormat_NonEmpty()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.NotEmpty(doc.GetArchiveFormat());
    }

    [Fact]
    public void GetArchiveFormat_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetArchiveFormat(), doc.GetArchiveFormat());
    }

    [Fact]
    public void GetArchiveFormat_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetArchiveFormat();
        var path = TempFile("af_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).GetArchiveFormat());
    }

    // -------------------------------------------------------------------------
    // GetMagicBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMagicBytes_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetMagicBytes());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMagicBytes_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.NotNull(doc.GetMagicBytes());
    }

    [Fact]
    public void GetMagicBytes_NonEmpty()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.NotEmpty(doc.GetMagicBytes());
    }

    [Fact]
    public void GetMagicBytes_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetMagicBytes(), doc.GetMagicBytes());
    }

    [Fact]
    public void GetMagicBytes_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetMagicBytes();
        var path = TempFile("mb_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).GetMagicBytes());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetArchiveFormat_GetMagicBytes_Pipeline()
    {
        // Astronomy — STFC / UKRI: James Webb Space Telescope (JWST) UK Science Archive
        // Compressed FITS-like observation metadata from MIRI and NIRCam UK PI programmes
        // Archive format and magic bytes validate file provenance in CADC mirror pipeline

        // Dataset 1: NIRCam observation metadata (highly compressible FITS headers)
        var path1 = TempFile("jwst_nircam_uk_pi_obs_2024.zst");
        {
            var sb = new StringBuilder();
            sb.AppendLine("SIMPLE  =                    T / conforms to FITS standard");
            sb.AppendLine("BITPIX  =                  -32 / array data type");
            sb.AppendLine("NAXIS   =                    2 / number of array dimensions");
            sb.AppendLine("NAXIS1  =                 2048");
            sb.AppendLine("NAXIS2  =                 2048");
            sb.AppendLine("INSTRUME= 'NIRCAM  '           / instrument used to acquire data");
            sb.AppendLine("FILTER  = 'F150W   '           / filter used");
            sb.AppendLine("EXPTIME =              1200.000 / exposure duration (seconds)");
            sb.AppendLine("PROGRAM = '2660    '           / proposal ID");
            sb.AppendLine("PI_NAME = 'Dunlop_J'           / principal investigator");
            sb.AppendLine("TARGNAME= 'COSMOS-FIELD-UK-PI'");
            sb.AppendLine("RA_V1   =          150.1163083 / right ascension of telescope V1 axis");
            sb.AppendLine("DEC_V1  =            2.2000000 / declination of telescope V1 axis");
            sb.AppendLine("ORIGIN  = 'STScI   '           / institution responsible for creating FITS file");
            sb.AppendLine("TELESCOP= 'JWST    '           / telescope used to acquire data");
            sb.AppendLine("PIXSCALE=                0.031 / pixel scale arcsec/pixel");
            var rng = new Random(20240415);
            for (int i = 0; i < 500; i++)
                sb.AppendLine($"COMMENT  Observation extension {i:D4}: t_exp={1200 + rng.Next(600)} s, filter=F150W, readout=DEEP8, groups={rng.Next(5,20)}, integrations={rng.Next(1,5)}");
            var raw = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(path1);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal, leaveOpen: true);
            zs.Write(raw, 0, raw.Length);
        }

        // Dataset 2: MIRI photometry catalogue
        var path2 = TempFile("jwst_miri_uk_photometry_2024.zst");
        {
            var sb = new StringBuilder();
            sb.AppendLine("# JWST MIRI UK Programme Photometry Catalogue");
            sb.AppendLine("# PI: Prof. Gillian Wright (RAL Space / ATC Edinburgh)");
            sb.AppendLine("# Programme: 1285 (MIRI Early Release Science)");
            sb.AppendLine("# Filter sequence: F560W, F770W, F1000W, F1130W, F1280W, F1500W, F1800W, F2100W, F2550W");
            sb.AppendLine("source_id,ra_deg,dec_deg,f560w_ujy,f770w_ujy,f1000w_ujy,f1800w_ujy,f2100w_ujy,z_phot,class");
            var rng = new Random(20240416);
            for (int i = 0; i < 200; i++)
            {
                double ra = 83.8 + rng.NextDouble() * 0.1;
                double dec = -5.38 + rng.NextDouble() * 0.1;
                double f560 = Math.Exp(rng.NextDouble() * 8) * 0.1;
                double f770 = f560 * (0.8 + rng.NextDouble() * 0.4);
                double f1000 = f770 * (0.7 + rng.NextDouble() * 0.6);
                double f1800 = f1000 * (1.2 + rng.NextDouble() * 0.8);
                double f2100 = f1800 * (0.9 + rng.NextDouble() * 0.4);
                double z = 0.1 + rng.NextDouble() * 7;
                string cls = rng.NextDouble() < 0.7 ? "Galaxy" : rng.NextDouble() < 0.5 ? "Star" : "AGN";
                sb.AppendLine($"MIRI_{i:D6},{ra:F6},{dec:F6},{f560:F3},{f770:F3},{f1000:F3},{f1800:F3},{f2100:F3},{z:F3},{cls}");
            }
            var raw = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(path2);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal, leaveOpen: true);
            zs.Write(raw, 0, raw.Length);
        }

        var doc1 = ZstDocument.LoadFile(path1);
        var doc2 = ZstDocument.LoadFile(path2);

        // Archive formats
        var af1 = doc1.GetArchiveFormat();
        var af2 = doc2.GetArchiveFormat();
        Assert.NotNull(af1);
        Assert.NotNull(af2);
        Assert.NotEmpty(af1);
        Assert.NotEmpty(af2);
        Assert.Equal(af1, doc1.GetArchiveFormat()); // consistent
        Assert.Equal(af2, doc2.GetArchiveFormat()); // consistent
        // Both compressed with same library — format should match
        Assert.Equal(af1, af2);

        // Magic bytes
        var mb1 = doc1.GetMagicBytes();
        var mb2 = doc2.GetMagicBytes();
        Assert.NotNull(mb1);
        Assert.NotNull(mb2);
        Assert.NotEmpty(mb1);
        Assert.NotEmpty(mb2);
        Assert.Equal(mb1, doc1.GetMagicBytes()); // consistent
        Assert.Equal(mb2, doc2.GetMagicBytes()); // consistent
        // Both created with ZLibStream — magic bytes should match
        Assert.Equal(mb1, mb2);

        // Cross-check with other properties
        Assert.True(doc1.GetCompressedSize() > 0);
        Assert.True(doc2.GetCompressedSize() > 0);
        Assert.True(doc1.GetCompressionRatio() >= 1.0);
        Assert.True(doc2.GetCompressionRatio() >= 1.0);

        // SaveToFile
        var out1 = TempFile("jwst_nircam_out.zst");
        doc1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loaded1 = ZstDocument.LoadFile(out1);
        Assert.Equal(af1, loaded1.GetArchiveFormat());
        Assert.Equal(mb1, loaded1.GetMagicBytes());

        var out2 = TempFile("jwst_miri_out.zst");
        doc2.SaveToFile(out2);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.Equal(af2, loaded2.GetArchiveFormat());
        Assert.Equal(mb2, loaded2.GetMagicBytes());

        var ex1 = Record.Exception(() => loaded1.GetArchiveFormat());
        var ex2 = Record.Exception(() => loaded2.GetMagicBytes());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
