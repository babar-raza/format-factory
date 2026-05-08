---
artifact_id: oracle-operator-handoff-fods
artifact_type: acquisition-pack
path: acquisition-packs/fods/oracle-operator-handoff.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
generated_by: claude
generated_at: "2026-05-07"
stale: false
notes: "Oracle operator handoff document for FODS Gate 6. Created run038 (2026-05-07) to provide a single precise reference for the person installing LibreOffice to unblock Gate 6."
---

# Oracle Operator Handoff — FODS Gate 6

**Created:** 2026-05-07 (run038)
**Status:** RESOLVED — Gate 6 PASSED (Babar Raza, 2026-05-08, run044). LibreOffice installed run043. ORACLE_PREFLIGHT: PASS. ORACLE_RUN: PASS 4/4. ORACLE_COMPARE: PASS 3/4 WARN 1/4. TC-0026 COMPLETED. TC-0027 DEC-034 PASS 24/24.
**Action required by:** None — Gate 6 is approved. This document is archived for historical reference.

---

## 1. Historical Situation (RESOLVED)

Gate 6 (Oracle Comparison) for FODS was blocked because LibreOffice was not installed on the development machine. The blocker was resolved in run043 (2026-05-08) when LibreOffice 26.2.3.2 was installed via `winget install -e --id TheDocumentFoundation.LibreOffice`. Gate 6 was subsequently APPROVED (Babar Raza, 2026-05-08, run044).

Oracle preflight history (for reference):

| Run | Date | Result |
|---|---|---|
| run035 | 2026-05-06 | ORACLE_PREFLIGHT: FAIL |
| run036 | 2026-05-06 | ORACLE_PREFLIGHT: FAIL |
| run037 | 2026-05-07 | ORACLE_PREFLIGHT: FAIL |
| run038 | 2026-05-07 | ORACLE_ENV: BLOCKED |
| run043 (after install) | 2026-05-08 | ORACLE_PREFLIGHT: PASS |

---

## 2. What to Install

**Required:** LibreOffice (any version ≥ 7.0; recommended: 24.2 LTS)

**Download:** https://www.libreoffice.org/download/libreoffice-still/

**Why LibreOffice:** LibreOffice is the co-developer of the ODF format, supports FODS natively, has production-quality headless mode, and is MPL-2.0 licensed. It is the only approved oracle provider for FODS Gate 6. See `acquisition-packs/fods/oracle-provider-options.md` for full alternatives evaluation.

---

## 3. Standard Expected Windows Path

After a standard Windows installation:
```
C:\Program Files\LibreOffice\program\soffice.exe
```

The oracle harness automatically checks this path during preflight.

---

## 4. Option A — Use Standard Installation (Recommended)

1. Install LibreOffice from https://www.libreoffice.org/download/libreoffice-still/
2. Use the default installation path (`C:\Program Files\LibreOffice\`)
3. Verify installation:
   ```
   "C:\Program Files\LibreOffice\program\soffice.exe" --version
   ```
   Expected output: `LibreOffice 24.2.x.x ...` (or similar)
4. Confirm oracle environment ready:
   ```
   python tools/oracle/validate_oracle_environment.py
   ```
   Expected: `ORACLE_ENV: READY`

---

## 5. Option B — Non-Standard Path (Use Environment Variable)

If LibreOffice is installed at a non-standard path, set the environment variable:

**Windows PowerShell:**
```powershell
$env:FORMAT_FACTORY_SOFFICE = "C:\Custom\Path\LibreOffice\program\soffice.exe"
```

**Windows (permanent, via System Properties):**
1. Open "Edit the system environment variables"
2. Add `FORMAT_FACTORY_SOFFICE` = `<path to soffice.exe>`

**Verify:**
```
python tools/oracle/validate_oracle_environment.py
```

---

## 6. Option C — Explicit Path Flag

If you prefer not to set an environment variable, pass the path explicitly:

```
python tools/oracle/preflight_oracle.py --soffice-path "C:\Program Files\LibreOffice\program\soffice.exe" --verbose
```

---

## 7. Verify Oracle Environment Before Executing TC-0026

**Always run this before issuing the TC-0026 execution prompt:**
```
python tools/oracle/validate_oracle_environment.py
```

Expected output when ready:
```
ORACLE_ENV: READY
Provider: LibreOffice
  Found: <path>
  Version: LibreOffice 24.2.x.x
```

---

## 8. How to Execute TC-0026 Once Ready

Issue this exact prompt (substitute actual path and version):

```
Execute TC-0026: FODS Gate 6 oracle execution.
LibreOffice is installed at C:\Program Files\LibreOffice\program\soffice.exe.
Version: [version string from --version output].
FORMAT_FACTORY_SOFFICE is set / --soffice-path will be used.
```

The oracle harness will:
1. Run preflight → confirm ORACLE_ENV: READY
2. Export all 4 FODS samples to CSV via `soffice --headless --convert-to csv`
3. Run comparison (parser output vs oracle CSV)
4. Produce summary report
5. Write committed report to `acquisition-packs/fods/gate6-oracle-comparison-report.md`

---

## 9. What NOT To Do

| Action | Status |
|---|---|
| Auto-install LibreOffice from a script | PROHIBITED |
| Use a cloud-based oracle or online LibreOffice service | PROHIBITED |
| Approve Gate 6 without running TC-0026 | PROHIBITED |
| Create fake oracle evidence | PROHIBITED |
| Create `src/python/fods/` or `src/net/fods/` product source | PROHIBITED |
| Create `reports/security/` or `reports/legal/` | PROHIBITED |
| Mark Gate 6 passed from within an agent session | PROHIBITED — human-only |

---

## 10. Related Files

| File | Purpose |
|---|---|
| `acquisition-packs/fods/oracle-installation-checklist.md` | Detailed installation guide |
| `acquisition-packs/fods/gate6-oracle-blocker-report.md` | Blocker evidence (all 4 preflight runs) |
| `acquisition-packs/fods/oracle-provider-options.md` | Why LibreOffice was chosen |
| `tools/oracle/provider_registry.yaml` | Approved oracle providers registry |
| `tools/oracle/validate_oracle_environment.py` | Environment readiness check |
| `tools/oracle/preflight_oracle.py --verbose` | Detailed preflight with candidate output |
| `taskcards/TC-0026-fods-gate6-oracle-execution.md` | TC-0026 execution taskcard |
| `docs/oracle-provider-strategy.md` | Oracle provider architecture |
