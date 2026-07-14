"""Plan Importer — tools/supervisor/plan_importer.py

Fixes three production failure modes from stateful-booping-mountain (FF-PLIS-001):

  1. Session B OVERWRITES Session A's modified plan file when `cp` runs unconditionally.
     Fix: check source_hash in registry before writing; skip cp if already registered.

  2. lifecycle_audit sees partial taskcard count, triggers premature closure.
     Fix: embed expected_taskcard_count in plan_identity at import time.

  3. Duplicate mission_ids silently conflict.
     Fix: registry indexed by mission_id; import fails if mission already ACTIVE.

Usage:
    python tools/supervisor/plan_importer.py --source <path-to-external-plan>
    python tools/supervisor/plan_importer.py --source <path> --force   # re-import even if registered
    python tools/supervisor/plan_importer.py --status                  # show registry
    python tools/supervisor/plan_importer.py --rebuild                 # rebuild registry from plan files
"""
import argparse, hashlib, json, os, re, shutil, sys, datetime
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PLANS_DIR = REPO_ROOT / 'plans' / '.claude'
REGISTRY_PATH = REPO_ROOT / '.local' / 'supervisor' / 'plan-registry.json'

TC_TABLE_RE = re.compile(
    r'\|\s*(TC-[\w-]+)\s*\|\s*(OPEN|CLOSED|IN_PROGRESS|PENDING|READY|DONE|VERIFIED|BLOCKED|TODO)\s*\|',
    re.IGNORECASE
)
TC_HEADING_RE = re.compile(r'^#{1,4}\s+(TC-[\w-]+)', re.MULTILINE)
MISSION_ID_RE = re.compile(r'(?:mission_id|Mission[_ ]ID)\s*[:=]\s*([A-Z0-9_\-]+)', re.IGNORECASE)
PLAN_ID_RE = re.compile(r'(?:plan_id|Plan[_ ]ID)\s*[:=]\s*([\w\-]+)', re.IGNORECASE)
EXPECTED_TC_RE = re.compile(r'expected_taskcard_count\s*:\s*(\d+)')


class ImportResult(NamedTuple):
    success: bool
    plan_path: str
    source_hash: str
    mission_id: str | None
    plan_id: str | None
    taskcard_count: int
    status: str  # IMPORTED | ALREADY_REGISTERED | SKIPPED_CONFLICT | ERROR
    message: str


class ValidationResult(NamedTuple):
    valid: bool
    errors: list[str]
    warnings: list[str]


class RegistrationResult(NamedTuple):
    success: bool
    registry_path: str
    message: str


# ── Registry ─────────────────────────────────────────────────────────────────

def _load_registry() -> dict:
    if REGISTRY_PATH.exists():
        try:
            return json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {'version': '1.0', 'plans': {}, 'active_missions': {}}


def _save_registry(reg: dict) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = REGISTRY_PATH.with_suffix('.tmp')
    tmp.write_text(json.dumps(reg, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, REGISTRY_PATH)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_taskcard_ids(text: str) -> list[str]:
    """Extract all TC-* IDs from plan text using table + heading patterns."""
    found: dict[str, str] = {}
    for m in TC_TABLE_RE.finditer(text):
        tc_id = m.group(1).strip()
        status = m.group(2).strip().upper()
        found[tc_id] = status
    for m in TC_HEADING_RE.finditer(text):
        tc_id = m.group(1).strip()
        if tc_id not in found:
            found[tc_id] = 'OPEN'
    return sorted(found.keys())


def _extract_mission_id(text: str) -> str | None:
    m = MISSION_ID_RE.search(text[:4000])
    return m.group(1).strip() if m else None


def _extract_plan_id(text: str) -> str | None:
    m = PLAN_ID_RE.search(text[:4000])
    return m.group(1).strip() if m else None


def _extract_expected_tc_count(text: str) -> int | None:
    m = EXPECTED_TC_RE.search(text[:4000])
    return int(m.group(1)) if m else None


def _embed_expected_tc_count(plan_path: Path, tc_count: int) -> None:
    """Inject expected_taskcard_count into the plan_identity block if not present."""
    text = plan_path.read_text(encoding='utf-8')
    if EXPECTED_TC_RE.search(text):
        return  # already present
    # Find plan_type line to insert after
    plan_type_m = re.search(r'^(## plan_type.*)', text, re.MULTILINE)
    if plan_type_m:
        new_line = f'{plan_type_m.group(1)}\n## expected_taskcard_count: {tc_count}'
        new_text = text.replace(plan_type_m.group(1), new_line)
        plan_path.write_text(new_text, encoding='utf-8')


# ── Public API ────────────────────────────────────────────────────────────────

def import_plan(source_path: str | Path, force: bool = False) -> ImportResult:
    """
    Import a plan from an external path into plans/.claude/.

    Returns ImportResult with success status and diagnostics.
    Idempotent: will NOT overwrite a modified in-repo plan if already registered.
    """
    source = Path(source_path)
    if not source.exists():
        return ImportResult(False, '', '', None, None, 0, 'ERROR',
                            f'Source not found: {source}')

    source_hash = _sha256(source)
    reg = _load_registry()

    # Check registry
    existing = reg['plans'].get(f'sha256:{source_hash}')
    if existing and not force:
        return ImportResult(
            True, existing['plan_path'], source_hash,
            existing.get('mission_id'), existing.get('plan_id'),
            existing.get('taskcard_count', 0),
            'ALREADY_REGISTERED',
            f'Already registered as {existing["plan_id"]} at {existing["plan_path"]}'
        )

    # Parse the source plan
    text = source.read_text(encoding='utf-8', errors='replace')
    plan_id = _extract_plan_id(text) or source.stem
    mission_id = _extract_mission_id(text)
    tc_ids = _extract_taskcard_ids(text)
    declared_expected = _extract_expected_tc_count(text)
    tc_count = declared_expected or len(tc_ids)

    # Mission conflict detection
    if mission_id and not force:
        existing_mission = reg['active_missions'].get(mission_id)
        if existing_mission and existing_mission != f'sha256:{source_hash}':
            existing_plan = reg['plans'].get(existing_mission, {})
            return ImportResult(
                False, '', source_hash, mission_id, plan_id, tc_count,
                'SKIPPED_CONFLICT',
                f'Mission {mission_id} already ACTIVE in {existing_plan.get("plan_path", "unknown")}. '
                f'Use --force to override.'
            )

    # Determine target path
    target = PLANS_DIR / source.name
    if not target.suffix:
        target = target.with_suffix('.md')

    # Atomic write to target (only if not already there with modifications)
    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    if target.exists() and not force:
        # Preserve existing modified content — do not overwrite
        pass
    else:
        tmp = target.with_suffix('.tmp')
        shutil.copy2(source, tmp)
        os.replace(tmp, target)

    # Embed expected_taskcard_count if not present
    if tc_count > 0:
        try:
            _embed_expected_tc_count(target, tc_count)
        except Exception:
            pass  # non-blocking

    # Register
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    reg['plans'][f'sha256:{source_hash}'] = {
        'plan_id': plan_id,
        'mission_id': mission_id,
        'plan_path': str(target.relative_to(REPO_ROOT)),
        'source_path': str(source),
        'source_hash': source_hash,
        'taskcard_count': tc_count,
        'taskcard_ids': tc_ids[:200],  # cap stored list
        'status': 'ACTIVE',
        'imported_at': now,
    }
    if mission_id:
        reg['active_missions'][mission_id] = f'sha256:{source_hash}'
    _save_registry(reg)

    return ImportResult(
        True, str(target), source_hash, mission_id, plan_id, tc_count,
        'IMPORTED',
        f'Imported {plan_id} -> {target} ({tc_count} taskcards)'
    )


def validate_plan(path: str | Path) -> ValidationResult:
    """
    Validate a plan file for structural compliance.
    Returns ValidationResult with errors and warnings.
    """
    p = Path(path)
    errors: list[str] = []
    warnings: list[str] = []

    if not p.exists():
        errors.append(f'File not found: {p}')
        return ValidationResult(False, errors, warnings)

    text = p.read_text(encoding='utf-8', errors='replace')

    # Required fields
    if not MISSION_ID_RE.search(text[:4000]):
        warnings.append('No mission_id found in first 4000 chars')
    if not PLAN_ID_RE.search(text[:4000]):
        warnings.append('No plan_id found in first 4000 chars')

    # Taskcard detection
    tc_ids = _extract_taskcard_ids(text)
    if not tc_ids:
        warnings.append('No TC-* taskcards found')
    else:
        declared = _extract_expected_tc_count(text)
        if declared and declared != len(tc_ids):
            warnings.append(
                f'expected_taskcard_count={declared} but found {len(tc_ids)} TC-* IDs. '
                f'Some taskcards may be in non-parseable format.'
            )

    # Plan type
    if '## plan_type:' not in text and 'plan_type:' not in text[:2000]:
        warnings.append('No plan_type field found')

    return ValidationResult(len(errors) == 0, errors, warnings)


def register_plan(path: str | Path, mission_id: str = None,
                  status: str = 'ACTIVE') -> RegistrationResult:
    """
    Register an already-in-repo plan in the plan registry.
    Use when a plan was imported manually and needs registry entry.
    """
    p = Path(path)
    if not p.exists():
        return RegistrationResult(False, str(REGISTRY_PATH),
                                  f'Plan not found: {p}')

    source_hash = _sha256(p)
    text = p.read_text(encoding='utf-8', errors='replace')
    plan_id = _extract_plan_id(text) or p.stem
    detected_mission = _extract_mission_id(text)
    effective_mission = mission_id or detected_mission
    tc_ids = _extract_taskcard_ids(text)

    reg = _load_registry()
    key = f'sha256:{source_hash}'
    reg['plans'][key] = {
        'plan_id': plan_id,
        'mission_id': effective_mission,
        'plan_path': str(p.relative_to(REPO_ROOT)) if p.is_relative_to(REPO_ROOT) else str(p),
        'source_hash': source_hash,
        'taskcard_count': len(tc_ids),
        'taskcard_ids': tc_ids[:200],
        'status': status,
        'registered_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    if effective_mission:
        reg['active_missions'][effective_mission] = key
    _save_registry(reg)
    return RegistrationResult(True, str(REGISTRY_PATH),
                              f'Registered {plan_id} (mission={effective_mission}, {len(tc_ids)} TCs)')


def _cmd_status() -> None:
    """Print registry status."""
    reg = _load_registry()
    plans = reg.get('plans', {})
    missions = reg.get('active_missions', {})
    print(f'Plan registry: {REGISTRY_PATH}')
    print(f'Registered plans: {len(plans)}')
    print(f'Active missions: {len(missions)}')
    for key, p in sorted(plans.items(), key=lambda x: x[1].get('plan_id', '')):
        print(f'  [{p.get("status","?")}] {p.get("plan_id","?")} | mission={p.get("mission_id","?")} | TCs={p.get("taskcard_count",0)} | {p.get("plan_path","")}')


def _cmd_rebuild() -> None:
    """Rebuild registry by scanning all plans/.claude/*.md files."""
    reg = _load_registry()
    rebuilt = 0
    for plan_file in sorted(PLANS_DIR.glob('*.md')):
        result = register_plan(plan_file)
        if result.success:
            rebuilt += 1
            print(f'  Registered: {result.message}')
    print(f'Rebuilt registry: {rebuilt} plans')
    print(f'Registry written to: {REGISTRY_PATH}')


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Plan Importer — safe plan ingestion with registry and conflict detection'
    )
    parser.add_argument('--source', help='External plan file to import')
    parser.add_argument('--force', action='store_true',
                        help='Re-import even if already registered / override mission conflict')
    parser.add_argument('--validate', help='Validate a plan file (path)')
    parser.add_argument('--register', help='Register an existing in-repo plan (path)')
    parser.add_argument('--status', action='store_true', help='Show registry status')
    parser.add_argument('--rebuild', action='store_true', help='Rebuild registry from repo plans')
    args = parser.parse_args()

    if args.status:
        _cmd_status()
    elif args.rebuild:
        _cmd_rebuild()
    elif args.validate:
        result = validate_plan(args.validate)
        print(f'Valid: {result.valid}')
        for e in result.errors:
            print(f'  ERROR: {e}')
        for w in result.warnings:
            print(f'  WARN: {w}')
        sys.exit(0 if result.valid else 1)
    elif args.register:
        result = register_plan(args.register)
        print(result.message)
        sys.exit(0 if result.success else 1)
    elif args.source:
        result = import_plan(args.source, force=args.force)
        print(f'{result.status}: {result.message}')
        if result.success:
            print(f'  Plan path: {result.plan_path}')
            print(f'  Mission:   {result.mission_id}')
            print(f'  TCs:       {result.taskcard_count}')
        sys.exit(0 if result.success else 1)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
