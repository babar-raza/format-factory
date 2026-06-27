// Tests for ZstDocument.GetFrameChecksum, ValidateChecksum, GetChecksumAlgorithm deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R238

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R238: Tests for ZstDocument.GetFrameChecksum, ValidateChecksum, GetChecksumAlgorithm deeper.
/// GetFrameChecksum(): returns the checksum value stored in the Zstandard frame.
/// ValidateChecksum(): verifies the checksum matches the decompressed content.
/// GetChecksumAlgorithm(): returns a string describing the checksum algorithm used.
/// Covers: GetFrameChecksum no-throw; GetFrameChecksum consistent; GetFrameChecksum save-load;
/// ValidateChecksum no-throw; ValidateChecksum true for valid data; ValidateChecksum consistent;
/// ValidateChecksum save-load;
/// GetChecksumAlgorithm no-throw; GetChecksumAlgorithm non-null; GetChecksumAlgorithm consistent;
/// dogfood Compress→GetFrameChecksum→ValidateChecksum→GetChecksumAlgorithm→SaveToFile pipeline.
/// </summary>
public class ZstR238GetFrameChecksumAndValidateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR238GetFrameChecksumAndValidateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR238_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateChecksumZst()
    {
        var content = string.Join("\n", Enumerable.Repeat(
            "CHECKSUM_FRAME_TEST_ALPHA_BETA_GAMMA_DELTA_EPSILON_ZETA_ETA_THETA", 80));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("checksum.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFrameChecksum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameChecksum_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        var ex = Record.Exception(() => doc.GetFrameChecksum());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameChecksum_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        Assert.Equal(doc.GetFrameChecksum(), doc.GetFrameChecksum());
    }

    [Fact]
    public void GetFrameChecksum_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        var before = doc.GetFrameChecksum();
        var path = TempFile("fc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrameChecksum());
    }

    // -------------------------------------------------------------------------
    // ValidateChecksum
    // -------------------------------------------------------------------------

    [Fact]
    public void ValidateChecksum_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        var ex = Record.Exception(() => doc.ValidateChecksum());
        Assert.Null(ex);
    }

    [Fact]
    public void ValidateChecksum_True_ForValidData()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        Assert.True(doc.ValidateChecksum());
    }

    [Fact]
    public void ValidateChecksum_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        Assert.Equal(doc.ValidateChecksum(), doc.ValidateChecksum());
    }

    [Fact]
    public void ValidateChecksum_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        var before = doc.ValidateChecksum();
        var path = TempFile("vc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.ValidateChecksum());
    }

    // -------------------------------------------------------------------------
    // GetChecksumAlgorithm
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChecksumAlgorithm_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        var ex = Record.Exception(() => doc.GetChecksumAlgorithm());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChecksumAlgorithm_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        Assert.NotNull(doc.GetChecksumAlgorithm());
    }

    [Fact]
    public void GetChecksumAlgorithm_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateChecksumZst());
        Assert.Equal(doc.GetChecksumAlgorithm(), doc.GetChecksumAlgorithm());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFrameChecksum_ValidateChecksum_GetChecksumAlgorithm_SaveToFile_Pipeline()
    {
        // Biomedical imaging — compressed DICOM pixel data integrity verification
        var sb = new StringBuilder();
        sb.AppendLine("patient_id,study_date,modality,body_part,slice_index,pixel_min,pixel_max,pixel_mean,snr_db,artifact_flag");
        string[] modalities = { "CT", "MRI", "PET", "SPECT" };
        string[] bodyParts = { "Brain", "Chest", "Abdomen", "Pelvis", "Spine", "Extremity" };
        var rng = new Random(77777);
        for (int i = 0; i < 300; i++)
        {
            var mod = modalities[i % 4];
            int pmin = rng.Next(0, 100);
            int pmax = rng.Next(800, 4096);
            double pmean = pmin + rng.NextDouble() * (pmax - pmin);
            sb.AppendLine($"PAT{i:D5},20240{(i % 12 + 1):D2}15,{mod},{bodyParts[i % 6]},{i % 128},{pmin},{pmax},{pmean:F1},{20.0 + rng.NextDouble() * 40.0:F1},{(rng.NextDouble() < 0.05 ? 1 : 0)}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_dicom_pixels.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetFrameChecksum
        var checksum = doc.GetFrameChecksum();
        Assert.Equal(checksum, doc.GetFrameChecksum()); // consistent

        // ValidateChecksum
        Assert.True(doc.ValidateChecksum());
        Assert.Equal(doc.ValidateChecksum(), doc.ValidateChecksum()); // consistent

        // GetChecksumAlgorithm
        var algo = doc.GetChecksumAlgorithm();
        Assert.NotNull(algo);
        Assert.Equal(algo, doc.GetChecksumAlgorithm()); // consistent

        // SaveToFile
        var out1 = TempFile("dogfood_dicom_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));

        // LoadFile — verify checksum preserved
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(checksum, loaded.GetFrameChecksum());
        Assert.True(loaded.ValidateChecksum());
        Assert.NotNull(loaded.GetChecksumAlgorithm());

        // Decompression round-trip
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        var text = Encoding.UTF8.GetString(decompressed);
        Assert.Contains("CT", text);
        Assert.Contains("MRI", text);
        Assert.Contains("Brain", text);

        // Second compression and verify
        var recompressed = ZstWriter.Compress(decompressed);
        var out2 = TempFile("dogfood_dicom_v2.zst");
        File.WriteAllBytes(out2, recompressed);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.True(loaded2.ValidateChecksum());
        Assert.NotNull(loaded2.GetChecksumAlgorithm());
        Assert.Equal(0xFD2FB528u, (uint)loaded2.GetMagicNumber());
        var ex1 = Record.Exception(() => loaded2.GetFrameHeaderSize());
        Assert.Null(ex1);
    }
}
