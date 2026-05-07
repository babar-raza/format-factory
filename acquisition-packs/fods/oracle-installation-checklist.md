---
artifact_id: fods-oracle-installation-checklist
artifact_type: operator-checklist
path: acquisition-packs/fods/oracle-installation-checklist.md
format_id: fods
visibility: internal
publish_allowed: false
generated_by: claude
generated_at: "2026-05-07"
notes: "Oracle installation and verification checklist for FODS Gate 6. Created run036 (2026-05-07)."
---

# FODS Gate 6 — Oracle Installation Checklist

**Purpose:** Step-by-step checklist to install and verify the LibreOffice oracle tool before executing TC-0026.

**Blocking:** TC-0026 (Gate 6 oracle comparison execution)

---

## Preflight Status (run036, 2026-05-07)

| Check | Status |
|---|---|
| Gate 5 PASSED | YES — Babar Raza, 2026-05-06 |
| TC-0025 planning reviewed | YES — completed run035 |
| LibreOffice installed | **NO — BLOCKER** |
| Oracle harness ready | YES — tools/oracle/ (5 files + oracle_common.py) |
| Preflight tool ready | YES — tools/oracle/preflight_oracle.py |

---

## Step 1: Download and Install LibreOffice

1. Go to https://www.libreoffice.org/download/libreoffice-still/
2. Download the **Still** (stable) release for Windows x86-64
3. Recommended version: 7.6.x or 24.x (latest stable)
4. Run the installer with default options

**Expected install path:** `C:\Program Files\LibreOffice\program\soffice.exe`

---

## Step 2: Verify Installation

Open a command prompt and run:

```
"C:\Program Files\LibreOffice\program\soffice.exe" --version
```

Expected output (example):
```
LibreOffice 7.6.7.2 (x86)
```

Or from a bash terminal:
```bash
"/c/Program Files/LibreOffice/program/soffice.exe" --version
```

---

## Step 3: Set Environment Variable (optional but recommended)

To make all tools discoverable without specifying the path each time:

In PowerShell:
```powershell
$env:FORMAT_FACTORY_SOFFICE = "C:\Program Files\LibreOffice\program\soffice.exe"
```

In bash:
```bash
export FORMAT_FACTORY_SOFFICE="C:/Program Files/LibreOffice/program/soffice.exe"
```

---

## Step 4: Run Oracle Preflight

From the repo root:

```bash
python tools/oracle/preflight_oracle.py --verbose
```

Or with explicit path:
```bash
python tools/oracle/preflight_oracle.py --soffice-path "C:/Program Files/LibreOffice/program/soffice.exe" --verbose
```

**Expected output:**
```
ORACLE_PREFLIGHT: PASS
```

If preflight fails:
- Check that the install path matches the path in `oracle_common.LIBREOFFICE_CANDIDATES`
- Use `--soffice-path` to override discovery
- See error messages for diagnostic information

---

## Step 5: Record Version

After preflight passes, note the version string from `.local/oracle/fods/oracle-preflight.yaml`.

---

## Step 6: Issue TC-0026 Execution Prompt

Issue an explicit Gate 6 execution prompt that:
1. Names this taskcard (TC-0026)
2. States the LibreOffice version verified
3. Authorizes oracle comparison execution

**Do NOT start TC-0026 without an explicit human execution prompt.**

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `soffice.exe` not found at standard path | Use `--soffice-path` or set `FORMAT_FACTORY_SOFFICE` |
| Version command hangs or times out | Check firewall; use `--headless` flag test separately |
| LibreOffice opens GUI instead of headless | Ensure `--headless` flag is included in all tool invocations |
| CSV export produces 0 files | Check output directory permissions and that sample files exist |
| Multiple LibreOffice versions installed | Use explicit `--soffice-path` to target the desired version |

---

## Related Files

- `tools/oracle/preflight_oracle.py` — preflight tool (runs step 4)
- `tools/oracle/oracle_common.py` — shared discovery logic and path model
- `tools/oracle/README.md` — oracle tooling overview
- `acquisition-packs/fods/gate6-oracle-blocker-report.md` — current blocker status
- `acquisition-packs/fods/gate6-oracle-plan.md` — Gate 6 execution plan
- `taskcards/TC-0026-fods-gate6-oracle-execution.md` — execution taskcard
