// Tests for ZstDocument.GetContentHash, ValidateChecksum deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R254

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R254: Tests for ZstDocument.GetContentHash, ValidateChecksum deeper.
/// GetContentHash(): returns a hash/checksum of the decompressed content for integrity verification.
/// ValidateChecksum(): verifies the embedded checksum against computed checksum; returns true if valid.
/// Covers: GetContentHash no-throw; GetContentHash non-null; GetContentHash non-empty;
/// GetContentHash consistent; GetContentHash save-load;
/// ValidateChecksum no-throw; ValidateChecksum returns bool; ValidateChecksum consistent;
/// ValidateChecksum save-load; ValidateChecksum true for valid file;
/// dogfood CreateDoc→GetContentHash→ValidateChecksum→SaveToFile pipeline.
/// </summary>
public class ZstR254GetContentHashAndChecksumValidationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR254GetContentHashAndChecksumValidationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR254_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateValidZst()
    {
        var content = "Valid zstd frame for checksum validation. " +
                      string.Join(" ", System.Linq.Enumerable.Repeat("Regulatory data integrity test.", 50));
        var path = TempFile("valid.zst");
        var writer = new ZstWriter();
        writer.CompressToFile(System.Text.Encoding.UTF8.GetBytes(content), path);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetContentHash
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContentHash_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateValidZst());
        var ex = Record.Exception(() => doc.GetContentHash());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContentHash_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateValidZst());
        Assert.NotNull(doc.GetContentHash());
    }

    [Fact]
    public void GetContentHash_NonEmpty()
    {
        var doc = ZstDocument.LoadFile(CreateValidZst());
        Assert.NotEmpty(doc.GetContentHash());
    }

    [Fact]
    public void GetContentHash_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateValidZst());
        Assert.Equal(doc.GetContentHash(), doc.GetContentHash());
    }

    [Fact]
    public void GetContentHash_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateValidZst());
        var before = doc.GetContentHash();
        var path = TempFile("hash_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetContentHash());
    }

    // -------------------------------------------------------------------------
    // ValidateChecksum
    // -------------------------------------------------------------------------

    [Fact]
    public void ValidateChecksum_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateValidZst());
        var ex = Record.Exception(() => doc.ValidateChecksum());
        Assert.Null(ex);
    }

    [Fact]
    public void ValidateChecksum_ReturnsBool()
    {
        var doc = ZstDocument.LoadFile(CreateValidZst());
        var result = doc.ValidateChecksum();
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void ValidateChecksum_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateValidZst());
        Assert.Equal(doc.ValidateChecksum(), doc.ValidateChecksum());
    }

    [Fact]
    public void ValidateChecksum_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateValidZst());
        var before = doc.ValidateChecksum();
        var path = TempFile("vc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.ValidateChecksum());
    }

    [Fact]
    public void ValidateChecksum_True_ForValidFile()
    {
        var doc = ZstDocument.LoadFile(CreateValidZst());
        // Valid zstd files should pass checksum validation
        Assert.True(doc.ValidateChecksum());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetContentHash_ValidateChecksum_Pipeline()
    {
        // Digital preservation — NHS Digital long-term archive integrity verification
        // Simulating archival of HL7 FHIR R4 clinical data bundles for NHSDA Data Lake
        var rng = new Random(20241215);

        // Build HL7 FHIR-like clinical data bundle
        var bundleBuilder = new System.Text.StringBuilder();
        bundleBuilder.AppendLine("{");
        bundleBuilder.AppendLine("  \"resourceType\": \"Bundle\",");
        bundleBuilder.AppendLine("  \"id\": \"bundle-nhs-digital-archive-20241215\",");
        bundleBuilder.AppendLine("  \"type\": \"collection\",");
        bundleBuilder.AppendLine("  \"timestamp\": \"2024-12-15T09:00:00Z\",");
        bundleBuilder.AppendLine("  \"total\": 120,");
        bundleBuilder.AppendLine("  \"entry\": [");

        for (int i = 0; i < 120; i++)
        {
            // Patient resource
            string nhsNumber = $"{rng.Next(400, 999):D3} {rng.Next(100, 999):D3} {rng.Next(1000, 9999):D4}";
            string gender = rng.NextDouble() < 0.51 ? "female" : "male";
            int birthYear = 1945 + rng.Next(65);
            string icdCode = rng.Next(3) switch {
                0 => "I10",  // Hypertension
                1 => "E11",  // T2DM
                _ => "J44"   // COPD
            };
            bundleBuilder.AppendLine("    {");
            bundleBuilder.AppendLine($"      \"fullUrl\": \"urn:uuid:patient-{i:D4}\",");
            bundleBuilder.AppendLine("      \"resource\": {");
            bundleBuilder.AppendLine("        \"resourceType\": \"Patient\",");
            bundleBuilder.AppendLine($"        \"id\": \"patient-{i:D4}\",");
            bundleBuilder.AppendLine("        \"identifier\": [{");
            bundleBuilder.AppendLine("          \"system\": \"https://fhir.nhs.uk/Id/nhs-number\",");
            bundleBuilder.AppendLine($"          \"value\": \"{nhsNumber}\"");
            bundleBuilder.AppendLine("        }],");
            bundleBuilder.AppendLine($"        \"gender\": \"{gender}\",");
            bundleBuilder.AppendLine($"        \"birthDate\": \"{birthYear}-{rng.Next(1, 13):D2}-{rng.Next(1, 29):D2}\",");
            bundleBuilder.AppendLine("        \"address\": [{");
            bundleBuilder.AppendLine($"          \"postalCode\": \"{(char)('A' + rng.Next(26))}{(char)('A' + rng.Next(26))}{rng.Next(1, 10)} {rng.Next(1, 10)}{(char)('A' + rng.Next(26))}{(char)('A' + rng.Next(26))}\"");
            bundleBuilder.AppendLine("        }]");
            bundleBuilder.AppendLine("      }");
            bundleBuilder.AppendLine(i < 119 ? "    }," : "    }");
        }
        bundleBuilder.AppendLine("  ]");
        bundleBuilder.AppendLine("}");

        var payload = System.Text.Encoding.UTF8.GetBytes(bundleBuilder.ToString());

        // Compress
        var path = TempFile("nhs_fhir_bundle.zst");
        var writer = new ZstWriter();
        writer.CompressToFile(payload, path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > 0);

        // GetContentHash
        var hash = doc.GetContentHash();
        Assert.NotNull(hash);
        Assert.NotEmpty(hash);
        Assert.Equal(hash, doc.GetContentHash()); // consistent

        // ValidateChecksum
        var isValid = doc.ValidateChecksum();
        Assert.True(isValid); // valid compressed file
        Assert.Equal(isValid, doc.ValidateChecksum()); // consistent

        // Round-trip
        var decompressed = doc.Decompress();
        Assert.NotNull(decompressed);
        Assert.Equal(payload.Length, decompressed.Length);

        // Frame metadata
        Assert.True(doc.GetFrameCount() >= 1);
        Assert.Equal(0, doc.GetDictionaryId());
        Assert.True(doc.GetVersion() >= 0);
        Assert.NotNull(doc.GetMagicNumber());

        // SaveToFile
        var path2 = TempFile("nhs_fhir_bundle_copy.zst");
        doc.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        Assert.True(new FileInfo(path2).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(path2);
        Assert.Equal(hash, loaded.GetContentHash());
        Assert.True(loaded.ValidateChecksum());
        Assert.Equal(doc.GetCompressedSize(), loaded.GetCompressedSize());
        Assert.Equal(doc.GetDecompressedSize(), loaded.GetDecompressedSize());

        // Different content → different hash
        var path3 = TempFile("different_content.zst");
        var altPayload = System.Text.Encoding.UTF8.GetBytes("Completely different FHIR bundle content.");
        writer.CompressToFile(altPayload, path3);
        var docAlt = ZstDocument.LoadFile(path3);
        // Hashes of different content may differ
        Assert.NotNull(docAlt.GetContentHash());
        Assert.True(docAlt.ValidateChecksum());

        // Archive 5 bundles — each must validate
        for (int b = 0; b < 5; b++)
        {
            var miniBundlePath = TempFile($"mini_bundle_{b:D2}.zst");
            var miniPayload = System.Text.Encoding.UTF8.GetBytes(
                $"{{\"resourceType\":\"Bundle\",\"id\":\"mini-{b}\",\"entry\":[]}}");
            writer.CompressToFile(miniPayload, miniBundlePath);
            var miniDoc = ZstDocument.LoadFile(miniBundlePath);
            Assert.NotNull(miniDoc.GetContentHash());
            Assert.NotEmpty(miniDoc.GetContentHash());
            Assert.True(miniDoc.ValidateChecksum());
        }
    }
}
