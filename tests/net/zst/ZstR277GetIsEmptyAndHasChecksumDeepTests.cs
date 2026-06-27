// Tests for ZstDocument.GetIsEmpty, HasChecksum deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R277

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R277: Tests for ZstDocument.GetIsEmpty, HasChecksum deeper.
/// GetIsEmpty(): returns true when the archive contains no data; false for non-empty archives.
/// HasChecksum(): returns true when the archive includes an integrity checksum.
/// Covers: GetIsEmpty false for non-empty archive; GetIsEmpty consistent; GetIsEmpty save-load;
/// HasChecksum no-throw; HasChecksum non-null-or-throws;
/// HasChecksum consistent; HasChecksum save-load; dogfood pipeline.
/// </summary>
public class ZstR277GetIsEmptyAndHasChecksumDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR277GetIsEmptyAndHasChecksumDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR277_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateNonEmptyZst(string name = "nonempty.zst")
    {
        var path = TempFile(name);
        var src = Encoding.UTF8.GetBytes(
            string.Concat(Enumerable.Repeat("Non-empty archive content with compressible payload data. ", 80)));
        using var fs = File.Create(path);
        using var zs = new ZLibStream(fs, CompressionLevel.Optimal, leaveOpen: true);
        zs.Write(src, 0, src.Length);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetIsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsEmpty_False_ForNonEmptyArchive()
    {
        var doc = ZstDocument.LoadFile(CreateNonEmptyZst());
        Assert.False(doc.GetIsEmpty());
    }

    [Fact]
    public void GetIsEmpty_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateNonEmptyZst());
        var ex = Record.Exception(() => doc.GetIsEmpty());
        Assert.Null(ex);
    }

    [Fact]
    public void GetIsEmpty_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateNonEmptyZst());
        Assert.Equal(doc.GetIsEmpty(), doc.GetIsEmpty());
    }

    [Fact]
    public void GetIsEmpty_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateNonEmptyZst());
        var before = doc.GetIsEmpty();
        var path = TempFile("ie_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).GetIsEmpty());
    }

    // -------------------------------------------------------------------------
    // HasChecksum
    // -------------------------------------------------------------------------

    [Fact]
    public void HasChecksum_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateNonEmptyZst());
        var ex = Record.Exception(() => doc.HasChecksum());
        Assert.Null(ex);
    }

    [Fact]
    public void HasChecksum_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateNonEmptyZst());
        Assert.Equal(doc.HasChecksum(), doc.HasChecksum());
    }

    [Fact]
    public void HasChecksum_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateNonEmptyZst());
        var before = doc.HasChecksum();
        var path = TempFile("hc_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).HasChecksum());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetIsEmpty_HasChecksum_Pipeline()
    {
        // Security — GCHQ / NCSC: Cyber Threat Intelligence Feed Archive
        // Compressed STIX 2.1 threat indicator bundles for UK CNI sectors
        // IsEmpty check validates feed integrity before import; checksum verifies provenance

        // Feed 1: Financial sector threat indicators (non-empty, substantial)
        var path1 = TempFile("ncsc_cti_financial_sector_2024.zst");
        {
            var sb = new StringBuilder();
            sb.AppendLine("{");
            sb.AppendLine("  \"type\": \"bundle\",");
            sb.AppendLine("  \"id\": \"bundle--ncsc-fin-2024-q3\",");
            sb.AppendLine("  \"spec_version\": \"2.1\",");
            sb.AppendLine("  \"objects\": [");
            var rng = new Random(20240701);
            string[] indicatorTypes = { "malicious-url", "file-hash-sha256", "ip-address", "domain-name", "email-pattern" };
            string[] threatActors = { "APT28_COLDWAR", "LAZARUS_GROUP", "SANDWORM", "COZY_BEAR", "ENERGETIC_BEAR" };
            for (int i = 0; i < 100; i++)
            {
                string iocType = indicatorTypes[rng.Next(indicatorTypes.Length)];
                string actor = threatActors[rng.Next(threatActors.Length)];
                string iocValue = iocType switch {
                    "malicious-url" => $"https://malicious-{rng.Next(100000)}.example.com/payload",
                    "file-hash-sha256" => $"{rng.Next(0x10000000, int.MaxValue):x8}{rng.Next(0x10000000, int.MaxValue):x8}{rng.Next(0x10000000, int.MaxValue):x8}{rng.Next(0x10000000, int.MaxValue):x8}",
                    "ip-address" => $"{rng.Next(1,255)}.{rng.Next(0,255)}.{rng.Next(0,255)}.{rng.Next(1,255)}",
                    "domain-name" => $"c2-{rng.Next(10000)}.threat-infra.net",
                    _ => $"threat-actor-{i:D5}@malicious-domain.io"
                };
                sb.AppendLine($"    {{\"type\":\"indicator\",\"id\":\"indicator--ncsc-fin-{i:D5}\",\"indicator_type\":\"{iocType}\",\"value\":\"{iocValue}\",\"threat_actor\":\"{actor}\",\"confidence\":{rng.Next(40,100)},\"tlp\":\"TLP:GREEN\",\"sector\":\"Financial\"}}");
                if (i < 99) sb.Append(",");
            }
            sb.AppendLine("  ]");
            sb.AppendLine("}");
            var raw = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(path1);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal, leaveOpen: true);
            zs.Write(raw, 0, raw.Length);
        }

        // Feed 2: Energy sector indicators
        var path2 = TempFile("ncsc_cti_energy_sector_2024.zst");
        {
            var sb = new StringBuilder();
            sb.AppendLine("{\"type\":\"bundle\",\"id\":\"bundle--ncsc-energy-2024-q3\",\"spec_version\":\"2.1\",\"objects\":[");
            var rng = new Random(20240702);
            for (int i = 0; i < 80; i++)
            {
                double lon = -3.5 + rng.NextDouble() * 7;
                double lat = 51 + rng.NextDouble() * 7;
                sb.AppendLine($"{{\"type\":\"attack-pattern\",\"id\":\"attack--ncsc-energy-{i:D4}\",\"name\":\"ICS_ATTACK_{i:D4}\",\"technique_id\":\"T{rng.Next(1000,2000)}\",\"sector\":\"Energy\",\"target_system\":\"ICS_SCADA\",\"severity\":{rng.Next(3,10)},\"geo_lat\":{lat:F4},\"geo_lon\":{lon:F4}}}");
                if (i < 79) sb.Append(",");
            }
            sb.AppendLine("]}");
            var raw = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(path2);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal, leaveOpen: true);
            zs.Write(raw, 0, raw.Length);
        }

        // Feed 3: Healthcare sector indicators
        var path3 = TempFile("ncsc_cti_healthcare_2024.zst");
        {
            var sb = new StringBuilder();
            sb.AppendLine("{\"type\":\"bundle\",\"id\":\"bundle--ncsc-health-2024-q3\",\"spec_version\":\"2.1\",\"objects\":[");
            var rng = new Random(20240703);
            for (int i = 0; i < 60; i++)
            {
                sb.AppendLine($"{{\"type\":\"malware\",\"id\":\"malware--ncsc-health-{i:D4}\",\"name\":\"RANSOMWARE_{rng.Next(100,999)}\",\"family\":\"Lockbit\",\"encrypted_extension\":\".{rng.Next(1000,9999)}\",\"ransom_demand_btc\":{0.5 + rng.NextDouble() * 10:F2},\"target_sector\":\"Healthcare\",\"nhs_trust_at_risk\":{(rng.NextDouble()<0.3?"true":"false")}}}");
                if (i < 59) sb.Append(",");
            }
            sb.AppendLine("]}");
            var raw = Encoding.UTF8.GetBytes(sb.ToString());
            using var fs = File.Create(path3);
            using var zs = new ZLibStream(fs, CompressionLevel.Optimal, leaveOpen: true);
            zs.Write(raw, 0, raw.Length);
        }

        var doc1 = ZstDocument.LoadFile(path1);
        var doc2 = ZstDocument.LoadFile(path2);
        var doc3 = ZstDocument.LoadFile(path3);

        // IsEmpty checks
        Assert.False(doc1.GetIsEmpty());
        Assert.False(doc2.GetIsEmpty());
        Assert.False(doc3.GetIsEmpty());
        Assert.Equal(doc1.GetIsEmpty(), doc1.GetIsEmpty()); // consistent
        Assert.Equal(doc2.GetIsEmpty(), doc2.GetIsEmpty()); // consistent

        // HasChecksum checks
        var hc1 = doc1.HasChecksum();
        var hc2 = doc2.HasChecksum();
        var hc3 = doc3.HasChecksum();
        Assert.Equal(hc1, doc1.HasChecksum()); // consistent
        Assert.Equal(hc2, doc2.HasChecksum()); // consistent
        Assert.Equal(hc3, doc3.HasChecksum()); // consistent
        // All created with same ZLibStream — should have same checksum behaviour
        Assert.Equal(hc1, hc2);

        // Compressed sizes are all positive (feeds have content)
        Assert.True(doc1.GetCompressedSize() > 0);
        Assert.True(doc2.GetCompressedSize() > 0);
        Assert.True(doc3.GetCompressedSize() > 0);

        // SaveToFile
        var out1 = TempFile("ncsc_fin_out.zst");
        doc1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loaded1 = ZstDocument.LoadFile(out1);
        Assert.Equal(doc1.GetIsEmpty(), loaded1.GetIsEmpty());
        Assert.Equal(hc1, loaded1.HasChecksum());

        var out2 = TempFile("ncsc_energy_out.zst");
        doc2.SaveToFile(out2);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.Equal(doc2.GetIsEmpty(), loaded2.GetIsEmpty());
        Assert.Equal(hc2, loaded2.HasChecksum());

        var out3 = TempFile("ncsc_health_out.zst");
        doc3.SaveToFile(out3);
        var loaded3 = ZstDocument.LoadFile(out3);
        Assert.Equal(doc3.GetIsEmpty(), loaded3.GetIsEmpty());
        Assert.Equal(hc3, loaded3.HasChecksum());

        var ex1 = Record.Exception(() => loaded1.GetIsEmpty());
        var ex2 = Record.Exception(() => loaded2.HasChecksum());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
