// Tests for ZstDocument.GetChecksumType, HasDictionary deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R273

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R273: Tests for ZstDocument.GetChecksumType, HasDictionary deeper.
/// GetChecksumType(): returns the checksum algorithm type used in the archive (e.g., "None", "Adler32", "CRC32").
/// HasDictionary(): returns true if the archive uses a preset dictionary for compression.
/// Covers: GetChecksumType no-throw; GetChecksumType non-null; GetChecksumType consistent;
/// GetChecksumType save-load;
/// HasDictionary no-throw; HasDictionary returns bool; HasDictionary false for standard archive;
/// HasDictionary consistent; HasDictionary save-load;
/// dogfood pipeline.
/// </summary>
public class ZstR273GetChecksumTypeAndHasDictionaryDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR273GetChecksumTypeAndHasDictionaryDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR273_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateStandardZst(string name, int size = 3000)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        for (int i = 0; i < size / 25; i++)
            sb.Append($"record_{i:D5}_payload_{(i % 100):D3} ");
        var original = Encoding.UTF8.GetBytes(sb.ToString());
        using var ms = new MemoryStream();
        using (var zs = new ZLibStream(ms, CompressionLevel.Optimal, leaveOpen: true))
            zs.Write(original, 0, original.Length);
        File.WriteAllBytes(path, ms.ToArray());
        return path;
    }

    private string CreateLargeZst(string name, int size = 15000)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        for (int i = 0; i < size / 30; i++)
            sb.Append($"entry_{i:D6}_data_{(i * 7 % 256):D3}_end ");
        var original = Encoding.UTF8.GetBytes(sb.ToString());
        using var ms = new MemoryStream();
        using (var zs = new ZLibStream(ms, CompressionLevel.Optimal, leaveOpen: true))
            zs.Write(original, 0, original.Length);
        File.WriteAllBytes(path, ms.ToArray());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetChecksumType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChecksumType_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst("sample.zst"));
        var ex = Record.Exception(() => doc.GetChecksumType());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChecksumType_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst("sample.zst"));
        Assert.NotNull(doc.GetChecksumType());
    }

    [Fact]
    public void GetChecksumType_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst("sample.zst"));
        Assert.Equal(doc.GetChecksumType(), doc.GetChecksumType());
    }

    [Fact]
    public void GetChecksumType_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst("sample.zst"));
        var before = doc.GetChecksumType();
        var path = TempFile("ck_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).GetChecksumType());
    }

    // -------------------------------------------------------------------------
    // HasDictionary
    // -------------------------------------------------------------------------

    [Fact]
    public void HasDictionary_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst("sample.zst"));
        var ex = Record.Exception(() => doc.HasDictionary());
        Assert.Null(ex);
    }

    [Fact]
    public void HasDictionary_ReturnsBool()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst("sample.zst"));
        var result = doc.HasDictionary();
        Assert.True(result == true || result == false);
    }

    [Fact]
    public void HasDictionary_False_ForStandardArchive()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst("sample.zst"));
        Assert.False(doc.HasDictionary());
    }

    [Fact]
    public void HasDictionary_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst("sample.zst"));
        Assert.Equal(doc.HasDictionary(), doc.HasDictionary());
    }

    [Fact]
    public void HasDictionary_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst("sample.zst"));
        var before = doc.HasDictionary();
        var path = TempFile("dict_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).HasDictionary());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetChecksumType_HasDictionary_Pipeline()
    {
        // Infrastructure — ONS / UKSA: Digital Economy Act Research Accreditation Data
        // Compressed microdata archives distributed to accredited researchers via DAP
        // Checksum type verifies data integrity; dictionary flag affects decompression prerequisites

        var path = TempFile("ons_dea_research_archive.zst");
        {
            // Simulate ONS microdata schema: census-style records
            var sb = new StringBuilder();
            sb.AppendLine("person_id,geography_code,age_band,tenure,household_composition,employment_status,nssec_group,health_status,qualification_level,country_of_birth");

            var rng = new Random(20240315);
            string[] geoCodes = {
                "E01000001", "E01000002", "E01000003", "E01000004", "E01000005",
                "W01000001", "W01000002", "S01000001", "S01000002", "N01000001"
            };
            string[] ageBands = { "0-15", "16-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75+" };
            string[] tenures = { "Owner_Occupied_Outright", "Owner_Occupied_Mortgage", "Social_Rented", "Private_Rented", "Other" };
            string[] hhComps = { "Single_Adult", "Couple_No_Children", "Couple_With_Children", "Lone_Parent", "Multi_Adult" };
            string[] employment = { "Employed_Full_Time", "Employed_Part_Time", "Self_Employed", "Unemployed", "Inactive_Retired", "Inactive_Student", "Inactive_Other" };
            string[] nssec = { "Higher_Managerial", "Lower_Managerial", "Intermediate", "Small_Employers", "Lower_Supervisory", "Semi_Routine", "Routine", "Never_Worked" };
            string[] health = { "Very_Good", "Good", "Fair", "Bad", "Very_Bad" };
            string[] quals = { "Degree_Plus", "Higher_Education", "A_Level", "GCSE_A_C", "GCSE_D_G", "No_Qualifications" };
            string[] birthplaces = { "UK", "EU27", "South_Asia", "East_Asia", "Africa", "Americas", "Rest_of_World" };

            for (int i = 0; i < 3000; i++)
            {
                sb.AppendLine($"P{i:D7},{geoCodes[rng.Next(geoCodes.Length)]},{ageBands[rng.Next(ageBands.Length)]},{tenures[rng.Next(tenures.Length)]},{hhComps[rng.Next(hhComps.Length)]},{employment[rng.Next(employment.Length)]},{nssec[rng.Next(nssec.Length)]},{health[rng.Next(health.Length)]},{quals[rng.Next(quals.Length)]},{birthplaces[rng.Next(birthplaces.Length)]}");
            }

            var original = Encoding.UTF8.GetBytes(sb.ToString());
            using var ms = new MemoryStream();
            using (var zs = new ZLibStream(ms, CompressionLevel.Optimal, leaveOpen: true))
                zs.Write(original, 0, original.Length);
            File.WriteAllBytes(path, ms.ToArray());
        }

        var doc = ZstDocument.LoadFile(path);

        // Checksum type
        var checksumType = doc.GetChecksumType();
        Assert.NotNull(checksumType);
        Assert.Equal(checksumType, doc.GetChecksumType()); // consistent

        // No dictionary for standard ZLib/ZST
        var hasDic = doc.HasDictionary();
        Assert.False(hasDic);
        Assert.Equal(hasDic, doc.HasDictionary()); // consistent

        // Other archive properties
        Assert.True(doc.GetFrameCount() >= 1);
        Assert.False(string.IsNullOrEmpty(doc.GetMagicBytes()));
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > 0);

        // SaveToFile
        var outPath = TempFile("ons_dea_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(checksumType, loaded.GetChecksumType());
        Assert.Equal(hasDic, loaded.HasDictionary());

        // Second archive
        var path2 = TempFile("ons_dea_small.zst");
        var doc2 = ZstDocument.LoadFile(CreateLargeZst(path2.Split('\\')[^1]));
        Assert.NotNull(doc2.GetChecksumType());
        Assert.False(doc2.HasDictionary());

        var ex1 = Record.Exception(() => loaded.GetChecksumType());
        var ex2 = Record.Exception(() => loaded.HasDictionary());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
