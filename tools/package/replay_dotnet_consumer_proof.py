#!/usr/bin/env python3
"""
replay_dotnet_consumer_proof.py — Deterministic .NET consumer proof from extracted bundle.

R47 MT3: Consumer proof must be replayable from an extracted bundle alone.
This script:
  1. Accepts an extracted bundle directory path (or .local/r47-metadata as source).
  2. Locates bundled .nupkg files under bundle-metadata/package-artifacts/.
  3. Creates temporary FODS/FODT consumer projects in a requested output directory.
  4. Writes nuget.config pointing to the bundled artifacts.
  5. Runs dotnet restore + build + run (smoke).
  6. Writes logs to the output directory.
  7. Returns 0 on full pass, non-zero on any failure.

Usage:
    python replay_dotnet_consumer_proof.py \\
        --artifacts-dir <path-to-package-artifacts-dir> \\
        --output-dir <path-to-output-dir> \\
        [--repo-root <path>]

Where:
    --artifacts-dir   Directory containing .nupkg files (e.g. extracted-bundle/bundle-metadata/package-artifacts/
                      or .local/r47-metadata/package-artifacts/)
    --output-dir      Directory where consumer projects and logs will be written
    --repo-root       Repo root for finding fixture samples (default: auto-detect from script location)

Exit codes:
    0 = PASS (both FODS and FODT consumer proofs passed)
    1 = FAIL (at least one consumer proof failed)
    2 = BLOCKED (SDK not available or artifacts missing)

publication_authorized: false
commercial_ready: false
Sprint: FORMAT-FACTORY-R47-ARTIFACT-PROOF-REPAIR-AND-PHASE-AUDIT-PROGRESSION-001
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT_DEFAULT = SCRIPT_DIR.parent.parent

FODS_CONSUMER_CSPROJ_TEMPLATE = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <RootNamespace>FodsConsumerReplay</RootNamespace>
    <AssemblyName>FodsConsumerReplay</AssemblyName>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="FormatFactory.Fods" Version="0.1.0-tier0" />
  </ItemGroup>
</Project>
"""

FODS_CONSUMER_PROGRAM = """\
// FODS consumer replay proof (R47 deterministic replay)
// Verifies FormatFactory.Fods can be restored from bundled .nupkg and used.
using FormatFactory.Fods;
using System.IO;

var repoRoot = Environment.GetEnvironmentVariable("REPO_ROOT") ?? FindRepoRoot();
var samplePath = Path.Combine(repoRoot, "samples", "by-format", "fods", "minimal-spreadsheet.fods");

if (!File.Exists(samplePath))
{
    Console.Error.WriteLine($"CONSUMER_PROOF_FAIL: sample not found at {samplePath}");
    return 1;
}

var doc = FodsDocument.Load(samplePath);
if (doc == null)
{
    Console.Error.WriteLine("CONSUMER_PROOF_FAIL: FodsDocument.Load returned null");
    return 1;
}

var sheets = doc.Sheets;
Console.WriteLine($"FODS_CONSUMER_REPLAY: package_restored=true");
Console.WriteLine($"FODS_CONSUMER_REPLAY: sample={Path.GetFileName(samplePath)}");
Console.WriteLine($"FODS_CONSUMER_REPLAY: sheet_count={sheets.Count}");
Console.WriteLine($"FODS_CONSUMER_REPLAY: PASS");
return 0;

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

FODT_CONSUMER_CSPROJ_TEMPLATE = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <RootNamespace>FodtConsumerReplay</RootNamespace>
    <AssemblyName>FodtConsumerReplay</AssemblyName>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="FormatFactory.Fodt" Version="0.1.0-tier0" />
  </ItemGroup>
</Project>
"""

FODT_CONSUMER_PROGRAM = """\
// FODT consumer replay proof (R47 deterministic replay)
// Verifies FormatFactory.Fodt can be restored from bundled .nupkg and used.
using FormatFactory.Fodt;
using System.IO;

var repoRoot = Environment.GetEnvironmentVariable("REPO_ROOT") ?? FindRepoRoot();
var samplePath = Path.Combine(repoRoot, "samples", "by-format", "fodt", "minimal-document.fodt");

if (!File.Exists(samplePath))
{
    Console.Error.WriteLine($"CONSUMER_PROOF_FAIL: sample not found at {samplePath}");
    return 1;
}

var doc = FodtDocument.Load(samplePath);
if (doc == null)
{
    Console.Error.WriteLine("CONSUMER_PROOF_FAIL: FodtDocument.Load returned null");
    return 1;
}

var paragraphs = doc.Paragraphs;
Console.WriteLine($"FODT_CONSUMER_REPLAY: package_restored=true");
Console.WriteLine($"FODT_CONSUMER_REPLAY: sample={Path.GetFileName(samplePath)}");
Console.WriteLine($"FODT_CONSUMER_REPLAY: paragraph_count={paragraphs?.Count ?? 0}");
Console.WriteLine($"FODT_CONSUMER_REPLAY: PASS");
return 0;

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

NUGET_CONFIG_TEMPLATE = """\
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <add key="bundled-artifacts" value="{artifacts_path}" />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
  </packageSources>
</configuration>
"""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_nupkg(artifacts_dir: Path, package_id: str) -> Path | None:
    """Find a .nupkg for the given package id (case-insensitive prefix match)."""
    prefix = package_id.lower()
    for f in sorted(artifacts_dir.iterdir()):
        if f.suffix == ".nupkg" and f.name.lower().startswith(prefix):
            return f
    return None


def run_command(cmd: list[str], cwd: Path, env: dict | None = None, timeout: int = 120) -> tuple[int, str]:
    """Run a command and return (returncode, combined_output)."""
    full_env = {**os.environ, **(env or {})}
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=full_env,
            encoding="utf-8",
            errors="replace",
        )
        output = result.stdout + result.stderr
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return -1, f"TIMEOUT after {timeout}s"
    except Exception as e:
        return -2, f"ERROR: {e}"


def run_consumer_proof(
    format_id: str,
    csproj_content: str,
    program_content: str,
    artifacts_dir: Path,
    output_dir: Path,
    repo_root: Path,
) -> tuple[bool, str]:
    """Create and run a consumer proof project for the given format."""
    project_dir = output_dir / f"{format_id}-consumer-replay"
    project_dir.mkdir(parents=True, exist_ok=True)

    # Write project files
    (project_dir / f"{format_id.capitalize()}ConsumerReplay.csproj").write_text(csproj_content, encoding="utf-8")
    (project_dir / "Program.cs").write_text(program_content, encoding="utf-8")

    # Write nuget.config — use absolute path to avoid resolution issues
    nuget_config = NUGET_CONFIG_TEMPLATE.format(artifacts_path=str(artifacts_dir).replace("\\", "/"))
    (project_dir / "nuget.config").write_text(nuget_config, encoding="utf-8")

    env = {"REPO_ROOT": str(repo_root)}
    log_lines = [f"=== {format_id.upper()} Consumer Replay ==="]
    log_lines.append(f"Project dir: {project_dir}")
    log_lines.append(f"Artifacts: {artifacts_dir}")
    log_lines.append(f"Repo root: {repo_root}")

    # Check nupkg exists
    pkg_id = f"FormatFactory.{format_id.capitalize()}"
    nupkg = find_nupkg(artifacts_dir, f"FormatFactory.{format_id.capitalize()}")
    if nupkg is None:
        msg = f"CONSUMER_PROOF_BLOCKED: no .nupkg for {pkg_id} in {artifacts_dir}"
        log_lines.append(msg)
        (output_dir / f"{format_id}-consumer-log.txt").write_text("\n".join(log_lines), encoding="utf-8")
        return False, msg
    log_lines.append(f"Found nupkg: {nupkg.name} sha256={sha256_file(nupkg)}")

    # dotnet restore
    rc, out = run_command(["dotnet", "restore", "--no-cache"], project_dir, env=env)
    log_lines.append(f"\n--- dotnet restore (rc={rc}) ---\n{out}")
    if rc != 0:
        log_lines.append(f"CONSUMER_PROOF_FAIL: dotnet restore failed (rc={rc})")
        (output_dir / f"{format_id}-consumer-log.txt").write_text("\n".join(log_lines), encoding="utf-8")
        return False, f"dotnet restore failed for {format_id}"

    # dotnet build
    rc, out = run_command(["dotnet", "build", "-c", "Release", "--no-restore"], project_dir, env=env)
    log_lines.append(f"\n--- dotnet build (rc={rc}) ---\n{out}")
    if rc != 0:
        log_lines.append(f"CONSUMER_PROOF_FAIL: dotnet build failed (rc={rc})")
        (output_dir / f"{format_id}-consumer-log.txt").write_text("\n".join(log_lines), encoding="utf-8")
        return False, f"dotnet build failed for {format_id}"

    # dotnet run
    rc, out = run_command(["dotnet", "run", "-c", "Release", "--no-build"], project_dir, env=env)
    log_lines.append(f"\n--- dotnet run (rc={rc}) ---\n{out}")
    passed = rc == 0 and "PASS" in out
    if not passed:
        log_lines.append(f"CONSUMER_PROOF_FAIL: dotnet run rc={rc}, PASS not in output")
        (output_dir / f"{format_id}-consumer-log.txt").write_text("\n".join(log_lines), encoding="utf-8")
        return False, f"dotnet run failed for {format_id}"

    log_lines.append(f"\n{format_id.upper()}_DOTNET_BUNDLED_NUPKG_CONSUMER_PASS")
    (output_dir / f"{format_id}-consumer-log.txt").write_text("\n".join(log_lines), encoding="utf-8")
    return True, f"{format_id.upper()}_DOTNET_BUNDLED_NUPKG_CONSUMER_PASS"


def main():
    parser = argparse.ArgumentParser(description="Replay .NET consumer proof from bundled artifacts")
    parser.add_argument("--artifacts-dir", required=True,
                        help="Directory containing .nupkg files")
    parser.add_argument("--output-dir", required=True,
                        help="Directory for consumer projects and logs")
    parser.add_argument("--repo-root", default=None,
                        help="Repo root for fixture samples (auto-detect if not set)")
    args = parser.parse_args()

    artifacts_dir = Path(args.artifacts_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else REPO_ROOT_DEFAULT
    output_dir.mkdir(parents=True, exist_ok=True)

    if not artifacts_dir.exists():
        print(f"CONSUMER_PROOF_BLOCKED: artifacts directory not found: {artifacts_dir}")
        sys.exit(2)

    # Check dotnet SDK
    rc, out = run_command(["dotnet", "--version"], output_dir)
    if rc != 0:
        print(f"CONSUMER_PROOF_BLOCKED: dotnet SDK not available: {out}")
        sys.exit(2)
    print(f"dotnet SDK: {out.strip()}")

    results = {}

    for fmt_id, csproj, program in [
        ("fods", FODS_CONSUMER_CSPROJ_TEMPLATE, FODS_CONSUMER_PROGRAM),
        ("fodt", FODT_CONSUMER_CSPROJ_TEMPLATE, FODT_CONSUMER_PROGRAM),
    ]:
        passed, msg = run_consumer_proof(fmt_id, csproj, program, artifacts_dir, output_dir, repo_root)
        results[fmt_id] = (passed, msg)
        status = "PASS" if passed else "FAIL"
        print(f"{fmt_id.upper()}_CONSUMER_REPLAY: {status} — {msg}")

    # Write summary
    summary_lines = ["DOTNET CONSUMER REPLAY SUMMARY", "=" * 40]
    for fmt_id, (passed, msg) in results.items():
        summary_lines.append(f"{fmt_id.upper()}: {'PASS' if passed else 'FAIL'} — {msg}")
    all_pass = all(p for p, _ in results.values())
    summary_lines.append("")
    summary_lines.append(f"OVERALL: {'PASS' if all_pass else 'FAIL'}")
    (output_dir / "consumer-replay-summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
