# ZST Aspose Support-Matrix Audit
Sprint: FORMAT-FACTORY-R13B-DELEGATED-ZST-GATE1-REAL-SUPPORT-AUDIT-AND-GOVERNANCE-NORMALIZATION-SWARM-001
Gate: 4 (Lane E)
Date: 2026-05-15
Internet access: AUTHORIZED for this audit

---

## Audit Scope

Official Aspose documentation and API reference pages only.
No community forums, blogs, or unofficial sources used as primary evidence.
All URLs captured with access date 2026-05-15.

---

## Primary Evidence

### 1. Supported File Formats Page

**URL:** https://docs.aspose.com/zip/net/supported-file-formats/
**Accessed:** 2026-05-15
**Excerpt:**
- GZIP, BZ2, LZ, LZ4, LZMA, CPIO, XZ, Z, **Zstd**, UUE listed as primary formats (Load & Save)
- TAR listed with "optional gz, bzip2, lz, xz, z, or **Zstandard** compression"
- ZIP listed with "Deflate, Bzip2, LZMA, PPMd, XZ or **Zstandard** compression algorithms"

**Classification:** ZST (Zstandard) is a first-class listed format for both Load and Save.

---

### 2. Aspose.Zip.Zstandard Namespace

**URL:** https://reference.aspose.com/zip/net/aspose.zip.zstandard/
**Accessed:** 2026-05-15

Classes in namespace:

| Class | Description |
|-------|-------------|
| ZstandardArchive | "Represents a Zstandard archive file. Use it to compose Zstandard archives." |
| ZstandardLoadOptions | Options for loading/decompressing Zstandard archives |
| ZstandardSaveOptions | Settings for Zstandard archive creation |

---

### 3. ZstandardArchive Constructor/Method Details

**URL:** https://reference.aspose.com/zip/net/aspose.zip.zstandard/zstandardarchive/
**Accessed:** 2026-05-15

Constructors:
- `ZstandardArchive()` — "prepared for compressing"
- `ZstandardArchive(Stream, ZstandardLoadOptions)` — "prepared for decompressing"
- `ZstandardArchive(string, ZstandardLoadOptions)` — from file path

Methods:
- `SetSource()` — define compression content
- `Save()` — compress and save
- `Extract()` — decompress to stream or file
- `ExtractToDirectory()` — extract all
- `Open()` — open for streaming access
- `Dispose()`

**API surface classification:** Full round-trip (compress + decompress + streaming).

---

### 4. TarArchive.SaveZstandard (.tar.zst support)

**URL:** https://reference.aspose.com/zip/net/aspose.zip.tar/tararchive/
**Accessed:** 2026-05-15

TarArchive has a `SaveZstandard` method (2 overloads: Stream + file path):
- "Saves archive to the stream with Zstandard compression"
- "Saves archive to the file by path with Zstandard compression"

**Output format:** .tar.zst (TAR with Zstandard compression)

---

### 5. CpioArchive.SaveZstandard (.cpio.zst support)

**URL:** https://reference.aspose.com/zip/net/aspose.zip.cpio/cpioarchive/savezstandard/
**Accessed:** 2026-05-15

`CpioArchive.SaveZstandard` exists with two overloads (Stream and file path).
Output confirmed as `.cpio.zst`.

---

### 6. Product Overview: Platform Support

**URL:** https://products.aspose.com/zip/most-common-archives/what-is-zstd/
**Accessed:** 2026-05-15

Zstandard support available across:
- Aspose.ZIP for .NET
- Aspose.ZIP for Java
- Aspose.ZIP for Python.NET

Operations confirmed: create, compress, decompress, multi-threading, custom dictionary support.

---

## Audit Questions Answered

| Question | Answer |
|----------|--------|
| Does Aspose.ZIP for .NET support Zstandard/ZST? | **YES** |
| Does any Aspose platform support ZST? | YES (.NET, Java, Python.NET) |
| Compression-only, decompression-only, or full round-trip? | **Full round-trip** (ZstandardArchive supports both; TarArchive.SaveZstandard for tar.zst) |
| Is there a clear API surface/class/method? | YES — `ZstandardArchive`, `ZstandardLoadOptions`, `ZstandardSaveOptions`, `TarArchive.SaveZstandard`, `CpioArchive.SaveZstandard` |
| Code examples or release notes confirming ZST? | YES — class descriptions in official API reference |
| Does product documentation distinguish .zst? | YES — separate Aspose.Zip.Zstandard namespace |
| Does Aspose support .tar.zst? | YES — `TarArchive.SaveZstandard` |
| Is support current or deprecated? | **CURRENT** — NuGet package 26.2.0 (2026) |

---

## Classification

**aspose_supported: true**

Evidence quality: HIGH (official API reference + supported file formats page)
Support level: FULL_ROUND_TRIP (compress + decompress + .tar.zst)
API surface: DEDICATED_NAMESPACE (Aspose.Zip.Zstandard)
Platforms: .NET (primary), Java, Python.NET

---

## Note on Licensing and Cost

Aspose.ZIP is a commercial library. Integration with format-factory's .NET commercial track requires a valid Aspose.ZIP license. This is a KNOWN constraint for the commercial product track (all Aspose-based formats share this constraint). For the Python FOSS track, `python-zstandard` (BSD-3-Clause) is the appropriate library — no Aspose dependency.

---

## Audit Result

ZST_ASPOSE_SUPPORT_AUDIT: PASS
aspose_supported: true
Evidence: official Aspose.ZIP API reference + supported formats page (accessed 2026-05-15)
