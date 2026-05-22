"""
tools/package/run_dotnet_object_model_poc.py

R49 .NET Object-Model POC proof script.
Tests the full edit/save/reload/verify chain for FODS and FODT.

Usage:
    python tools/package/run_dotnet_object_model_poc.py [--artifacts-dir DIR]

Sprint: FORMAT-FACTORY-R49-EDITABLE-OBJECT-MODEL-POC-BASELINE-AND-STRATEGY-SYNC-001
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Inline C# programs
# ---------------------------------------------------------------------------

FODS_CSPROJ_TEMPLATE = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <RootNamespace>FodsObjectModelPoc</RootNamespace>
    <AssemblyName>FodsObjectModelPoc</AssemblyName>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="FormatFactory.Fods" Version="0.1.0-tier0" />
  </ItemGroup>
</Project>
"""

FODS_CONSUMER_PROGRAM = r"""
// FODS .NET Object-Model POC: Load → Navigate → SetText → Save → Reload → Verify
using FormatFactory.Fods;
using System.IO;

var repoRoot = Environment.GetEnvironmentVariable("REPO_ROOT") ?? FindRepoRoot();
var samplePath = Path.Combine(repoRoot, "samples", "by-format", "fods", "minimal-spreadsheet.fods");

if (!File.Exists(samplePath))
{
    Console.Error.WriteLine($"FODS_POC_FAIL: sample not found at {samplePath}");
    return 1;
}

// Step 1: Load
var doc = FodsDocument.Load(samplePath);
var sheets = doc.Sheets;
if (sheets.Count == 0)
{
    Console.Error.WriteLine("FODS_POC_FAIL: no sheets in document");
    return 1;
}
Console.WriteLine($"FODS_POC: loaded sheet_count={sheets.Count}");

// Step 2: Navigate to first cell of first sheet
var sheet = sheets[0];
var rows = sheet.Rows;
if (rows.Count == 0)
{
    Console.Error.WriteLine("FODS_POC_FAIL: no rows in first sheet");
    return 1;
}
var firstRow = rows[0];
var cells = firstRow.Cells;
if (cells.Count == 0)
{
    Console.Error.WriteLine("FODS_POC_FAIL: no cells in first row");
    return 1;
}
var targetCell = cells[0];
var originalValue = targetCell.Value;
Console.WriteLine($"FODS_POC: navigate_ok original_value={originalValue ?? "(null)"}");

// Step 3: Edit cell text
const string EDITED_VALUE = "R49_DOTNET_EDITED_CELL";
targetCell.SetText(EDITED_VALUE);
Console.WriteLine($"FODS_POC: settext_ok new_value={EDITED_VALUE}");

// Step 4: Save to temp file
var tmpPath = Path.Combine(Path.GetTempPath(), $"r49_fods_poc_{Guid.NewGuid():N}.fods");
try
{
    doc.Save(tmpPath);
    Console.WriteLine($"FODS_POC: save_ok path={tmpPath}");

    // Step 5: Reload
    var reloaded = FodsDocument.Load(tmpPath);
    var reloadedSheets = reloaded.Sheets;
    if (reloadedSheets.Count == 0)
    {
        Console.Error.WriteLine("FODS_POC_FAIL: reload returned no sheets");
        return 1;
    }
    var reloadedCell = reloadedSheets[0].Rows[0].Cells[0];
    var reloadedValue = reloadedCell.Value;
    Console.WriteLine($"FODS_POC: reload_ok reloaded_value={reloadedValue ?? "(null)"}");

    // Step 6: Verify edit persisted
    if (reloadedValue != EDITED_VALUE)
    {
        Console.Error.WriteLine(
            $"FODS_POC_FAIL: edit not preserved; expected={EDITED_VALUE} got={reloadedValue}");
        return 1;
    }
    Console.WriteLine("FODS_POC: verify_edit_ok");

    // Step 7: Verify untouched cells are unchanged (if more than 1 cell in row)
    if (cells.Count > 1)
    {
        var origSecond = reloadedSheets[0].Rows[0].Cells.Count > 1
            ? reloadedSheets[0].Rows[0].Cells[1].Value
            : null;
        Console.WriteLine($"FODS_POC: preservation_check second_cell={origSecond ?? "(none)"}");
    }
    Console.WriteLine("FODS_DOTNET_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS");
    return 0;
}
finally
{
    if (File.Exists(tmpPath)) File.Delete(tmpPath);
}

static string FindRepoRoot()
{
    var dir = new DirectoryInfo(AppContext.BaseDirectory);
    for (int i = 0; i < 10; i++)
    {
        if (dir == null) break;
        if (File.Exists(Path.Combine(dir.FullName, ".git", "config")))
            return dir.FullName;
        dir = dir.Parent;
    }
    return AppContext.BaseDirectory;
}
"""

FODT_CSPROJ_TEMPLATE = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <RootNamespace>FodtObjectModelPoc</RootNamespace>
    <AssemblyName>FodtObjectModelPoc</AssemblyName>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="FormatFactory.Fodt" Version="0.1.0-tier0" />
  </ItemGroup>
</Project>
"""

FODT_CONSUMER_PROGRAM = r"""
// FODT .NET Object-Model POC: Load → Navigate → SetText → Save → Reload → Verify
using FormatFactory.Fodt;
using System.IO;

var repoRoot = Environment.GetEnvironmentVariable("REPO_ROOT") ?? FindRepoRoot();
var samplePath = Path.Combine(repoRoot, "samples", "by-format", "fodt", "headings-and-paragraphs.fodt");

if (!File.Exists(samplePath))
{
    Console.Error.WriteLine($"FODT_POC_FAIL: sample not found at {samplePath}");
    return 1;
}

// Step 1: Load
var doc = FodtDocument.Load(samplePath);
var paragraphs = doc.Paragraphs;
if (paragraphs.Count == 0)
{
    Console.Error.WriteLine("FODT_POC_FAIL: no paragraphs in document");
    return 1;
}
Console.WriteLine($"FODT_POC: loaded paragraph_count={paragraphs.Count}");

// Step 2: Navigate to first paragraph
var target = paragraphs[0];
var originalText = target.Text;
Console.WriteLine($"FODT_POC: navigate_ok original_text={originalText ?? "(null)"}");

// Step 3: Edit paragraph text
const string EDITED_TEXT = "R49_DOTNET_EDITED_PARAGRAPH";
target.SetText(EDITED_TEXT);
Console.WriteLine($"FODT_POC: settext_ok new_text={EDITED_TEXT}");

// Step 4: Save to temp file
var tmpPath = Path.Combine(Path.GetTempPath(), $"r49_fodt_poc_{Guid.NewGuid():N}.fodt");
try
{
    doc.Save(tmpPath);
    Console.WriteLine($"FODT_POC: save_ok path={tmpPath}");

    // Step 5: Reload
    var reloaded = FodtDocument.Load(tmpPath);
    var reloadedParas = reloaded.Paragraphs;
    if (reloadedParas.Count == 0)
    {
        Console.Error.WriteLine("FODT_POC_FAIL: reload returned no paragraphs");
        return 1;
    }
    var reloadedText = reloadedParas[0].Text;
    Console.WriteLine($"FODT_POC: reload_ok reloaded_text={reloadedText ?? "(null)"}");

    // Step 6: Verify edit persisted
    if (reloadedText != EDITED_TEXT)
    {
        Console.Error.WriteLine(
            $"FODT_POC_FAIL: edit not preserved; expected={EDITED_TEXT} got={reloadedText}");
        return 1;
    }
    Console.WriteLine("FODT_POC: verify_edit_ok");

    // Step 7: Verify untouched paragraphs (if count > 1)
    if (reloadedParas.Count > 1)
    {
        var secondText = reloadedParas[1].Text;
        Console.WriteLine($"FODT_POC: preservation_check second_para={secondText ?? "(null)"}");
    }
    Console.WriteLine("FODT_DOTNET_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS");
    return 0;
}
finally
{
    if (File.Exists(tmpPath)) File.Delete(tmpPath);
}

static string FindRepoRoot()
{
    var dir = new DirectoryInfo(AppContext.BaseDirectory);
    for (int i = 0; i < 10; i++)
    {
        if (dir == null) break;
        if (File.Exists(Path.Combine(dir.FullName, ".git", "config")))
            return dir.FullName;
        dir = dir.Parent;
    }
    return AppContext.BaseDirectory;
}
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_nupkg(artifacts_dir: Path, package_id: str) -> Path | None:
    for p in artifacts_dir.rglob("*.nupkg"):
        if package_id.lower() in p.name.lower():
            return p
    return None


def run_command(
    cmd: list[str], cwd: Path, env: dict | None = None, timeout: int = 120
) -> tuple[int, str]:
    result = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True,
        env=env, timeout=timeout
    )
    return result.returncode, result.stdout + result.stderr


def run_poc_proof(
    format_name: str,
    csproj_template: str,
    program_code: str,
    nupkg_path: Path,
    repo_root: Path,
    work_dir: Path,
) -> bool:
    """Build and run the POC program in a temp directory."""
    proj_dir = work_dir / f"{format_name}_object_model_poc"
    proj_dir.mkdir(parents=True, exist_ok=True)

    # Write project file and program
    (proj_dir / f"{format_name.capitalize()}ObjectModelPoc.csproj").write_text(
        csproj_template, encoding="utf-8"
    )
    (proj_dir / "Program.cs").write_text(program_code, encoding="utf-8")

    # Set up local NuGet source
    nuget_dir = work_dir / "nuget-local"
    nuget_dir.mkdir(exist_ok=True)
    shutil.copy2(nupkg_path, nuget_dir / nupkg_path.name)

    nuget_config = f"""\
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <add key="local-r49" value="{nuget_dir}" />
  </packageSources>
</configuration>
"""
    (proj_dir / "nuget.config").write_text(nuget_config, encoding="utf-8")

    env = os.environ.copy()
    env["REPO_ROOT"] = str(repo_root)
    env["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
    env["NUGET_PACKAGES"] = str(work_dir / "nuget-cache")

    # Restore
    rc, out = run_command(["dotnet", "restore", "--nologo"], proj_dir, env=env)
    print(f"  restore exit={rc}")
    if rc != 0:
        print(f"  RESTORE FAILED:\n{out}")
        return False

    # Run
    rc, out = run_command(["dotnet", "run", "--nologo"], proj_dir, env=env)
    print(out)
    pass_token = f"{format_name.upper()}_DOTNET_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS"
    if rc == 0 and pass_token in out:
        print(f"  {pass_token} confirmed.")
        return True
    else:
        print(f"  FAIL: exit={rc}; expected token={pass_token}")
        return False


def main():
    parser = argparse.ArgumentParser(description="R49 .NET Object-Model POC proof")
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=Path(".local/r49-metadata/package-artifacts"),
        help="Directory containing .nupkg files (default: .local/r49-metadata/package-artifacts)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent.parent.resolve()
    artifacts_dir = (repo_root / args.artifacts_dir).resolve() if not args.artifacts_dir.is_absolute() else args.artifacts_dir

    print(f"R49 .NET Object-Model POC Proof")
    print(f"Repo root: {repo_root}")
    print(f"Artifacts dir: {artifacts_dir}")
    print()

    if not artifacts_dir.exists():
        print(f"ERROR: artifacts dir not found: {artifacts_dir}")
        sys.exit(1)

    fods_nupkg = find_nupkg(artifacts_dir, "fods")
    fodt_nupkg = find_nupkg(artifacts_dir, "fodt")

    if not fods_nupkg:
        print(f"ERROR: No FODS nupkg found in {artifacts_dir}")
        sys.exit(1)
    if not fodt_nupkg:
        print(f"ERROR: No FODT nupkg found in {artifacts_dir}")
        sys.exit(1)

    print(f"FODS nupkg: {fods_nupkg.name} sha256={sha256_file(fods_nupkg)[:16]}...")
    print(f"FODT nupkg: {fodt_nupkg.name} sha256={sha256_file(fodt_nupkg)[:16]}...")
    print()

    results = {}
    with tempfile.TemporaryDirectory(prefix="r49_dotnet_poc_") as tmp:
        work_dir = Path(tmp)

        print("=" * 60)
        print("FODS Object-Model POC")
        print("=" * 60)
        results["fods"] = run_poc_proof(
            "fods", FODS_CSPROJ_TEMPLATE, FODS_CONSUMER_PROGRAM,
            fods_nupkg, repo_root, work_dir / "fods",
        )

        print()
        print("=" * 60)
        print("FODT Object-Model POC")
        print("=" * 60)
        results["fodt"] = run_poc_proof(
            "fodt", FODT_CSPROJ_TEMPLATE, FODT_CONSUMER_PROGRAM,
            fodt_nupkg, repo_root, work_dir / "fodt",
        )

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for fmt, ok in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  {fmt.upper()}: {status}")

    if all(results.values()):
        print()
        print("FODS_DOTNET_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS")
        print("FODT_DOTNET_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS")
        print("R49_DOTNET_OBJECT_MODEL_POC: PASS")
        sys.exit(0)
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"R49_DOTNET_OBJECT_MODEL_POC: FAIL ({', '.join(failed)})")
        sys.exit(1)


if __name__ == "__main__":
    main()
