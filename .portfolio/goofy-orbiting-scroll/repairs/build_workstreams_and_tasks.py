"""
Build workstreams and executable tasks from 2510 source taskcards.

Design principles:
- One workstream = one coherent implementation area / repository surface
- One executable task = smallest complete change that can be verified independently
- Source taskcards are assigned to executable tasks by plan + subject area
- Plans with 100+ TCs are broken into coherent sub-groups by implementation surface
- Superseded plans (s004 superseded by s005, s023 superseded by s024) are disposed
"""
import json, hashlib, datetime
from pathlib import Path

ROOT = Path('.portfolio/goofy-orbiting-scroll')
now = datetime.datetime.now(datetime.timezone.utc).isoformat()

stcs_data = json.loads(Path(ROOT / 'source-taskcards/all-source-taskcards.json').read_text(encoding='utf-8', errors='replace'))
stcs = stcs_data['source_taskcards']
summary = json.loads(Path(ROOT / 'source-taskcards/extraction-summary.json').read_text(encoding='utf-8'))

# ── Workstream definitions ────────────────────────────────────────────────────
# Keyed by workstream_id
WORKSTREAMS = {
    'WS-01-SUPERVISOR-MACHINERY': {
        'objective': 'Repair and harden the supervisor plan machinery: plan_importer.py, lifecycle loop fix, plan lock robustness',
        'source_plan_ids': ['s009', 's037'],
        'primary_lane': 'L01',
        'notes': 'stateful-booping-mountain (plan_importer) + velvet-swinging-wreath (lifecycle healing)'
    },
    'WS-02-GOVERNANCE-HEALING': {
        'objective': 'Implement governance validator healing suite: fix validator count, add missing validators, pass all governance checks',
        'source_plan_ids': ['s004', 's005', 's012'],
        'primary_lane': 'L01',
        'notes': 's005 (memoized-frolicking-donut v3) supersedes s004 (iterative-mixing-shannon). s012 = validator count discrepancy.'
    },
    'WS-03-ORACLE-ASSESSMENT': {
        'objective': 'Complete oracle system assessment and remediation for shiny-percolating-sky',
        'source_plan_ids': ['s001'],
        'primary_lane': 'L07',
        'notes': 'IN_PROGRESS in source. Oracle assessment for format factory spec compliance.'
    },
    'WS-04-AGENTIC-PARITY': {
        'objective': 'Complete FF-AGENTS-PARITY-001: agentic system parity for all formats',
        'source_plan_ids': ['s002'],
        'primary_lane': 'L01',
        'notes': 'IN_PROGRESS in source. glimmering-hopping-kazoo.'
    },
    'WS-05-PIPELINE-RECONCILIATION': {
        'objective': 'Reconcile pipeline divergence: next-work-items.json vs next-sprint.md for all formats',
        'source_plan_ids': ['s006', 's013'],
        'primary_lane': 'L08',
        'notes': 'bubbly-dancing-pony (s006) + vast-wibbling-moon (s013). s013 subsumes s006 scope.'
    },
    'WS-06-CODE-QUALITY-AUDIT': {
        'objective': 'Code quality audit: identify and document violations, prepare remediation plan',
        'source_plan_ids': ['s007'],
        'primary_lane': 'L01',
        'notes': 'mutable-exploring-hellman. Audit-first, then implementation repairs.'
    },
    'WS-07-MINSKY-ELEGANCE': {
        'objective': 'Elegant API design improvements per elegant-napping-minsky plan',
        'source_plan_ids': ['s008'],
        'primary_lane': 'L02',
        'notes': 'elegant-napping-minsky. Product API elegance.'
    },
    'WS-08-PRODUCT-LIBRARY-HEALING': {
        'objective': 'Heal product library for all FOSS Python formats per splendid-prancing-wind',
        'source_plan_ids': ['s010'],
        'primary_lane': 'L02',
        'notes': 'splendid-prancing-wind. Product source healing.'
    },
    'WS-09-FODS-GOVERNANCE': {
        'objective': 'Complete FODS governance, SAL validation, and FODS-specific test coverage',
        'source_plan_ids': ['s011'],
        'primary_lane': 'L01',
        'notes': 'splendid-squishing-orbit. 250 TCs — FODS is the largest governance plan.'
    },
    'WS-10-CONTROL-INDEX': {
        'objective': 'Build and validate the control index system',
        'source_plan_ids': ['s014'],
        'primary_lane': 'L01',
        'notes': 'clever-tickling-island. Control index implementation.'
    },
    'WS-11-GOVERNANCE-SUITE-BATCH2': {
        'objective': 'Second batch of governance healing tasks from warm-enchanting-grove',
        'source_plan_ids': ['s015'],
        'primary_lane': 'L01',
        'notes': 'warm-enchanting-grove.'
    },
    'WS-12-GLOWING-GROVE': {
        'objective': 'Implement glowing-swinging-grove plan objectives',
        'source_plan_ids': ['s016'],
        'primary_lane': 'L01',
        'notes': 'glowing-swinging-grove. Only 5 TCs.'
    },
    'WS-13-VAST-SPLASHING-ALLEN': {
        'objective': 'Complete vast-splashing-allen plan objectives',
        'source_plan_ids': ['s017'],
        'primary_lane': 'L01',
        'notes': 'vast-splashing-allen.'
    },
    'WS-14-KIND-CRUNCHING-CORAL': {
        'objective': 'Complete kind-crunching-coral plan objectives',
        'source_plan_ids': ['s018'],
        'primary_lane': 'L01',
        'notes': 'kind-crunching-coral.'
    },
    'WS-15-HUMBLE-HATCHING': {
        'objective': 'Complete humble-hatching-lark plan objectives',
        'source_plan_ids': ['s019'],
        'primary_lane': 'L01',
        'notes': 'humble-hatching-lark. 104 TCs.'
    },
    'WS-16-ATOMIC-METEOR': {
        'objective': 'Complete atomic-chasing-meteor plan objectives',
        'source_plan_ids': ['s020'],
        'primary_lane': 'L01',
        'notes': 'atomic-chasing-meteor. 56 TCs.'
    },
    'WS-17-SPICY-GOSLING': {
        'objective': 'Complete spicy-sparking-gosling plan objectives',
        'source_plan_ids': ['s021'],
        'primary_lane': 'L01',
        'notes': 'spicy-sparking-gosling. 39 TCs.'
    },
    'WS-18-PLAYFUL-THUNDER': {
        'objective': 'Complete playful-discovering-thunder plan objectives',
        'source_plan_ids': ['s022'],
        'primary_lane': 'L01',
        'notes': 'playful-discovering-thunder. 95 TCs.'
    },
    'WS-19-DUAL-LANE-DOM': {
        'objective': 'Implement dual-lane DOM gap generator per serialized-petting-crab (supersedes precious-wandering-lighthouse)',
        'source_plan_ids': ['s024', 's023'],
        'primary_lane': 'L02',
        'notes': 'serialized-petting-crab (s024) supersedes precious-wandering-lighthouse (s023). TC-VPR-001..008.'
    },
    'WS-20-CERTIFICATION-LAYER': {
        'objective': 'Build certification layer per glittery-splashing-manatee',
        'source_plan_ids': ['s025'],
        'primary_lane': 'L01',
        'notes': 'glittery-splashing-manatee. 12 TCs.'
    },
    'WS-21-ESPANSO-INTEGRATION': {
        'objective': 'Complete Espanso integration per imperative-coalescing-bengio',
        'source_plan_ids': ['s026'],
        'primary_lane': 'L05',
        'notes': 'IN_PROGRESS. 28 TCs.'
    },
    'WS-22-SILLY-TOWER': {
        'objective': 'Complete silly-popping-tower plan objectives',
        'source_plan_ids': ['s027'],
        'primary_lane': 'L01',
        'notes': '76 TCs.'
    },
    'WS-23-PEPPY-LARK': {
        'objective': 'Complete peppy-crafting-lark product deepening',
        'source_plan_ids': ['s028'],
        'primary_lane': 'L02',
        'notes': '68 TCs.'
    },
    'WS-24-FIZZY-HINTON': {
        'objective': 'Complete fizzy-imagining-hinton plan objectives',
        'source_plan_ids': ['s029'],
        'primary_lane': 'L01',
        'notes': '36 TCs.'
    },
    'WS-25-SHIMMERING-MEERKAT': {
        'objective': 'Complete shimmering-rolling-meerkat plan objectives',
        'source_plan_ids': ['s030'],
        'primary_lane': 'L01',
        'notes': '12 TCs.'
    },
    'WS-26-ORACLE-HARDENING-2': {
        'objective': 'Oracle hardening Phase II per modular-noodling-galaxy',
        'source_plan_ids': ['s031'],
        'primary_lane': 'L07',
        'notes': '64 TCs.'
    },
    'WS-27-IMPERATIVE-BOOK': {
        'objective': 'Complete imperative-floating-book plan objectives',
        'source_plan_ids': ['s032'],
        'primary_lane': 'L01',
        'notes': '190 TCs — largest after s011.'
    },
    'WS-28-OPTIMIZED-GIRAFFE': {
        'objective': 'Complete optimized-meandering-giraffe plan objectives',
        'source_plan_ids': ['s033'],
        'primary_lane': 'L01',
        'notes': '12 TCs.'
    },
    'WS-29-SPLENDID-BEAVER': {
        'objective': 'Complete splendid-roaming-beaver plan objectives',
        'source_plan_ids': ['s034'],
        'primary_lane': 'L02',
        'notes': '68 TCs.'
    },
    'WS-30-WILD-CHERNY': {
        'objective': 'Complete wild-napping-cherny plan objectives',
        'source_plan_ids': ['s035'],
        'primary_lane': 'L01',
        'notes': '9 TCs.'
    },
    'WS-31-CHEEKY-MANATEE': {
        'objective': 'Complete cheeky-crafting-manatee forensic/archaeology objectives',
        'source_plan_ids': ['s036'],
        'primary_lane': 'L01',
        'notes': '100 TCs. Marked TERMINAL_CLOSED in source — verify individual TCs.'
    },
    'WS-32-GOLDEN-BOOT': {
        'objective': 'Complete golden-foraging-boot plan objectives',
        'source_plan_ids': ['s038'],
        'primary_lane': 'L01',
        'notes': '102 TCs.'
    },
    'WS-33-EFFERVESCENT-MARSHMALLOW': {
        'objective': 'Complete effervescent-sprouting-marshmallow forensic objectives',
        'source_plan_ids': ['s039'],
        'primary_lane': 'L01',
        'notes': '16 TCs. Marked TERMINAL_CLOSED in source — verify individual TCs.'
    },
    'WS-34-FUZZY-LOBSTER': {
        'objective': 'Complete fuzzy-conjuring-lobster forensic/archaeology objectives',
        'source_plan_ids': ['s040'],
        'primary_lane': 'L01',
        'notes': '84 TCs.'
    },
    'WS-35-LIVELY-ELEPHANT': {
        'objective': 'Complete lively-leaping-elephant plan objectives',
        'source_plan_ids': ['s041'],
        'primary_lane': 'L01',
        'notes': '15 TCs.'
    },
    'WS-36-POLYMORPHIC-FEATHER': {
        'objective': 'Complete polymorphic-foraging-feather spec parity objectives',
        'source_plan_ids': ['s003'],
        'primary_lane': 'L02',
        'notes': '12 TCs.'
    },
}

# ── Executable task definitions ───────────────────────────────────────────────
# Each executable task is atomic: one coherent mutation, independent verification

def make_task(task_id, workstream_id, objective, source_plan_ids, source_task_ids,
              affected_paths, implementation_steps, acceptance_criteria,
              focused_verification=None, lane_verification=None, evidence_requirements=None,
              dependencies=None, wave=0, primary_lane='L01', rollback='git checkout -- <affected_paths>',
              forbidden_paths=None, source_anchors=None, repository_assessment='NOT_STARTED'):
    return {
        'schema_version': '1.0',
        'task_id': task_id,
        'workstream_id': workstream_id,
        'objective': objective,
        'source_plan_ids': source_plan_ids,
        'source_task_ids': source_task_ids or [],
        'source_anchors': source_anchors or [],
        'source_requirement_ids': [],
        'affected_components': [],
        'affected_paths': affected_paths or [],
        'allowed_mutation_scope': affected_paths or [],
        'forbidden_paths': forbidden_paths or [],
        'prerequisites': [],
        'dependencies': dependencies or [],
        'shared_resources': [],
        'primary_lane': primary_lane,
        'supporting_lanes': [],
        'integration_owner': 'claude-sonnet-4-6',
        'implementation_steps': implementation_steps or [],
        'acceptance_criteria': acceptance_criteria or [],
        'negative_acceptance_criteria': [],
        'focused_verification': focused_verification or [],
        'lane_verification': lane_verification or [],
        'integration_verification': [],
        'regression_verification': [],
        'end_to_end_verification': [],
        'pilot_verification': [],
        'evidence_requirements': (evidence_requirements or ['Implementation file diff', 'Test output showing acceptance criteria met']),
        'rollback': rollback,
        'cleanup': '',
        'invalidation_triggers': [],
        'reopening_conditions': [],
        'wave': wave,
        'status': 'READY' if not dependencies else 'WAITING',
        'active_claim_id': None,
        'active_attempt_id': None,
        'closure_id': None,
        'claimed_at': None,
        'closed_at': None,
        'last_verified_at': None,
        'repository_assessment': repository_assessment,
    }


EXECUTABLE_TASKS = [

    # ── WAVE 0: Foundation repairs — no predecessors ──────────────────────────

    make_task(
        'ET-W0-001',
        'WS-01-SUPERVISOR-MACHINERY',
        'Verify actual validator count and update MEMORY.md to reflect ground truth (167 per runner)',
        ['s009', 's012'],
        ['TC-SBM-001'],
        ['docs/MEMORY.md', 'tools/supervisor/governance_validator_runner.py'],
        [
            'Run: python -c "import re; f=open(\'tools/supervisor/governance_validator_runner.py\').read(); print(re.findall(r\'expected_count.*?\\d+\', f))"',
            'Count actual validate_ functions across all governance_validators*.py files',
            'Compare against expected_count=167 in runner',
            'Update MEMORY.md line about validator count to reflect truth (167)',
            'Record the discrepancy resolution in evidence/raw/ET-W0-001/',
        ],
        [
            'expected_count in governance_validator_runner.py matches actual validator count',
            'MEMORY.md correctly states validator count as 167 (not 165)',
            'No test regressions from MEMORY.md update',
        ],
        [
            'grep expected_count tools/supervisor/governance_validator_runner.py',
            'python -c "from pathlib import Path; import re; total=set(); [total.update(re.findall(r\'def (validate_\\w+)\', p.read_text(encoding=\'utf-8\', errors=\'replace\'))) for p in Path(\'tools/supervisor\').glob(\'governance_validators*.py\')]; print(len(total))"',
        ],
        lane_verification=['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        wave=0,
        primary_lane='L01',
        repository_assessment='PARTIAL',
    ),

    make_task(
        'ET-W0-002',
        'WS-01-SUPERVISOR-MACHINERY',
        'Create plan_importer.py in tools/supervisor/ — baseline skeleton with documented interface',
        ['s009'],
        ['TC-SBM-001', 'TC-SBM-002', 'TC-SBM-003'],
        ['tools/supervisor/plan_importer.py'],
        [
            'Read stateful-booping-mountain.md plan file for plan_importer.py specification',
            'Create tools/supervisor/plan_importer.py with functions: import_plan(path), validate_plan(path), register_plan(path)',
            'Each function must have docstring, proper error handling, and type hints',
            'import_plan: copies plan to plans/.claude/<name>.md, returns PlanImportResult',
            'validate_plan: checks plan schema compliance, returns ValidationResult',
            'register_plan: registers in plan registry JSON, returns RegistrationResult',
            'Write tests/supervisor/test_plan_importer.py with at least 3 test cases',
        ],
        [
            'tools/supervisor/plan_importer.py exists',
            'import_plan(), validate_plan(), register_plan() functions are importable',
            'tests/supervisor/test_plan_importer.py passes',
            'plan_importer.py < 200 LOC (lean implementation)',
        ],
        [
            'python -c "from tools.supervisor.plan_importer import import_plan, validate_plan, register_plan; print(\'OK\')"',
            'python .venv/Scripts/pytest tests/supervisor/test_plan_importer.py -v',
        ],
        lane_verification=['python .venv/Scripts/pytest tests/supervisor/ -q --tb=short 2>&1 | tail -5'],
        wave=0,
        primary_lane='L01',
        repository_assessment='NOT_STARTED',
    ),

    make_task(
        'ET-W0-003',
        'WS-02-GOVERNANCE-HEALING',
        'Investigate and document which governance validators are missing/broken per memoized-frolicking-donut',
        ['s005', 's004'],
        ['TC-GOV-001'],
        ['tools/supervisor/'],
        [
            'Read memoized-frolicking-donut.md (s005) plan completely',
            'Run existing governance validators: python tools/supervisor/governance_validator_runner.py',
            'Record all FAIL and WARN results',
            'For each failing validator: document root cause, affected files, fix steps',
            'Write evidence/raw/ET-W0-003/governance-audit.json with all findings',
            'Produce repair-list.json: ordered list of validator fixes with effort estimate',
        ],
        [
            'governance_validator_runner.py runs without exception',
            'evidence/raw/ET-W0-003/governance-audit.json exists with all FAIL/WARN items',
            'repair-list.json documents each fix needed',
        ],
        [
            'python tools/supervisor/governance_validator_runner.py 2>&1 | tail -20',
        ],
        wave=0,
        primary_lane='L01',
        repository_assessment='NOT_STARTED',
    ),

    make_task(
        'ET-W0-004',
        'WS-03-ORACLE-ASSESSMENT',
        'Complete oracle assessment for shiny-percolating-sky: verify all 20 formats at VERIFIED state',
        ['s001'],
        ['TC-ORA-001', 'TC-ORA-002', 'TC-ORA-003'],
        ['tools/supervisor/execute_oracle.py', 'oracle/'],
        [
            'Read shiny-percolating-sky.md (s001) plan completely',
            'Run: python tools/supervisor/execute_oracle.py --all-formats',
            'For any format not at VERIFIED: identify root cause',
            'Fix oracle test cases or oracle packages as needed',
            'Re-run until all 20 active Python formats at VERIFIED',
            'Record pass/fail matrix in evidence/raw/ET-W0-004/oracle-results.json',
        ],
        [
            'All 20 active Python FOSS formats at CASES_DEFINED or VERIFIED',
            'execute_oracle.py exits 0',
            'No format at OBLIGATION_CREATED except ora/pam/xpm/zpaq (no products)',
        ],
        [
            'python tools/supervisor/execute_oracle.py --all-formats 2>&1 | grep -E "(PASS|FAIL|VERIFIED)" | head -30',
        ],
        wave=0,
        primary_lane='L07',
        repository_assessment='IMPLEMENTED_UNVERIFIED',
    ),

    make_task(
        'ET-W0-005',
        'WS-04-AGENTIC-PARITY',
        'Assess agentic system parity state from glimmering-hopping-kazoo plan',
        ['s002'],
        ['TC-AGT-001'],
        [],
        [
            'Read glimmering-hopping-kazoo.md (s002) plan completely',
            'Identify which agentic parity TCs are already done vs outstanding',
            'Map each TC to current repository state',
            'Write evidence/raw/ET-W0-005/agentic-parity-assessment.json',
            'Create follow-on executable tasks for any remaining work',
        ],
        [
            'Assessment document written',
            'Every TC in s002 has a repository_assessment classification',
        ],
        [
            'cat .portfolio/goofy-orbiting-scroll/evidence/raw/ET-W0-005/agentic-parity-assessment.json',
        ],
        wave=0,
        primary_lane='L01',
        repository_assessment='NOT_STARTED',
    ),

    make_task(
        'ET-W0-006',
        'WS-21-ESPANSO-INTEGRATION',
        'Assess Espanso integration state from imperative-coalescing-bengio (IN_PROGRESS plan)',
        ['s026'],
        ['TC-ESP-001'],
        [],
        [
            'Read imperative-coalescing-bengio.md (s026) plan completely',
            'Identify which TCs are already done vs outstanding',
            'Check if Espanso package/config exists in repository',
            'Write evidence/raw/ET-W0-006/espanso-assessment.json',
        ],
        [
            'Assessment document written',
            'Every TC in s026 has a repository_assessment classification',
        ],
        ['cat .portfolio/goofy-orbiting-scroll/evidence/raw/ET-W0-006/espanso-assessment.json'],
        wave=0,
        primary_lane='L05',
        repository_assessment='NOT_STARTED',
    ),

    make_task(
        'ET-W0-007',
        'WS-36-POLYMORPHIC-FEATHER',
        'Complete polymorphic-foraging-feather spec parity objectives',
        ['s003'],
        ['TC-PFF-001', 'TC-PFF-002', 'TC-PFF-003'],
        ['src/python/'],
        [
            'Read polymorphic-foraging-feather.md (s003) plan completely',
            'Identify which taskcards are outstanding',
            'For each outstanding TC: assess current repository state',
            'Write evidence/raw/ET-W0-007/pff-assessment.json',
            'Execute any READY sub-tasks that can be done atomically',
        ],
        [
            'All 12 source TCs in s003 have final disposition',
            'Any implemented changes have passing tests',
        ],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        wave=0,
        primary_lane='L02',
        repository_assessment='NOT_STARTED',
    ),

    make_task(
        'ET-W0-008',
        'WS-05-PIPELINE-RECONCILIATION',
        'Audit pipeline divergence: identify exact differences between next-work-items.json and next-sprint.md',
        ['s006', 's013'],
        ['TC-BWM-001'],
        ['reports/supervisor/next-sprint.md', 'reports/supervisor/next-work-items.json'],
        [
            'Read bubbly-dancing-pony.md (s006) and vast-wibbling-moon.md (s013)',
            'Compare content of reports/supervisor/next-sprint.md vs next-work-items JSON files',
            'Identify discrepancies: items in one but not the other, stale items, ordering differences',
            'Write evidence/raw/ET-W0-008/pipeline-divergence-report.json',
            'Classify each divergence: true-gap vs transient-state vs stale',
        ],
        [
            'Pipeline divergence report written',
            'Every divergence classified',
            'Repair tasks created for true-gap items',
        ],
        ['cat .portfolio/goofy-orbiting-scroll/evidence/raw/ET-W0-008/pipeline-divergence-report.json'],
        wave=0,
        primary_lane='L08',
        repository_assessment='NOT_STARTED',
    ),

    # ── WAVE 1: Depends on Wave 0 ────────────────────────────────────────────

    make_task(
        'ET-W1-001',
        'WS-02-GOVERNANCE-HEALING',
        'Fix highest-priority governance validator failures identified in ET-W0-003 audit',
        ['s005'],
        ['TC-GOV-002', 'TC-GOV-003', 'TC-GOV-004'],
        ['tools/supervisor/governance_validators*.py'],
        [
            'Load evidence/raw/ET-W0-003/governance-audit.json repair-list.json',
            'Fix the top 5 FAIL validators in priority order',
            'For each fix: edit the validator, run it in isolation, verify it passes',
            'Run full governance_validator_runner.py and record results',
            'Update evidence/raw/ET-W1-001/validator-fixes.json',
        ],
        [
            'Top 5 governance FAIL validators now PASS',
            'No new FAIL validators introduced',
            'governance_validator_runner.py exit 0 or fewer FAIL than before',
        ],
        [
            'python tools/supervisor/governance_validator_runner.py 2>&1 | grep -c FAIL || echo 0',
        ],
        lane_verification=['python .venv/Scripts/pytest tests/supervisor/ -q --tb=short 2>&1 | tail -5'],
        dependencies=['ET-W0-003'],
        wave=1,
        primary_lane='L01',
        repository_assessment='NOT_STARTED',
    ),

    make_task(
        'ET-W1-002',
        'WS-01-SUPERVISOR-MACHINERY',
        'Complete lifecycle loop iteration fix: ensure AUDIT_PASS leads to TERMINAL_CLOSED, not ITERATION_REQUIRED loop',
        ['s037'],
        ['TC-VLH-001', 'TC-VLH-002'],
        ['tools/supervisor/lifecycle_audit.py', 'tools/supervisor/write_plan_lock.py'],
        [
            'Read velvet-swinging-wreath.md (s037) plan completely',
            'Reproduce the ITERATION_REQUIRED loop issue in a test scenario',
            'Identify root cause in lifecycle_audit.py or write_plan_lock.py',
            'Apply fix ensuring AUDIT_PASS → TERMINAL_CLOSED (not re-triggering ITERATION_REQUIRED)',
            'Write tests/supervisor/test_lifecycle_iteration_fix.py',
        ],
        [
            'lifecycle_audit.py returns AUDIT_PASS when all taskcards in table are CLOSED',
            'write_plan_lock.py with --audit-gate and AUDIT_PASS → status=TERMINAL_CLOSED',
            'No regression in existing plan lock tests',
        ],
        ['python .venv/Scripts/pytest tests/supervisor/test_plan_lock*.py -v'],
        wave=1,
        primary_lane='L01',
        repository_assessment='PARTIAL',
    ),

    make_task(
        'ET-W1-003',
        'WS-09-FODS-GOVERNANCE',
        'Execute FODS governance batch A: first 50 TCs from splendid-squishing-orbit',
        ['s011'],
        [f'TC-SQO-{i:03d}' for i in range(1, 51)],
        ['tools/supervisor/', 'src/python/fods/', 'oracle/fods/'],
        [
            'Read splendid-squishing-orbit.md (s011) TCs 1-50',
            'Identify which are already implemented vs outstanding',
            'Execute outstanding TCs in order within this batch',
            'Run FODS-specific tests after each change',
            'Write evidence/raw/ET-W1-003/fods-batch-a-results.json',
        ],
        [
            'All 50 TCs in batch A have final disposition (DONE or SATISFIED_BY_EXISTING)',
            'FODS oracle cases pass',
            'No FODS test regressions',
        ],
        ['python .venv/Scripts/pytest tests/fods/ -v 2>&1 | tail -20'],
        dependencies=['ET-W0-003'],
        wave=1,
        primary_lane='L01',
        repository_assessment='NOT_STARTED',
    ),

    make_task(
        'ET-W1-004',
        'WS-05-PIPELINE-RECONCILIATION',
        'Repair pipeline divergences identified in ET-W0-008: sync next-work-items.json with next-sprint.md',
        ['s006', 's013'],
        [],
        ['reports/supervisor/'],
        [
            'Load evidence/raw/ET-W0-008/pipeline-divergence-report.json',
            'For each true-gap divergence: fix the source (supervisor output or next-sprint.md)',
            'Re-run autonomous-cycle to regenerate consistent outputs',
            'Verify next-work-items.json and next-sprint.md are consistent',
        ],
        [
            'No true-gap divergences between next-work-items.json and next-sprint.md',
            'supervisor pipeline generates consistent outputs',
        ],
        ['python tools/supervisor/autonomous_cycle.py --dry-run 2>&1 | tail -10'],
        dependencies=['ET-W0-008'],
        wave=1,
        primary_lane='L08',
        repository_assessment='NOT_STARTED',
    ),

    # ── WAVE 2: After Wave 1 ─────────────────────────────────────────────────

    make_task(
        'ET-W2-001',
        'WS-02-GOVERNANCE-HEALING',
        'Fix remaining governance validator failures from s005 repair list (batch 2)',
        ['s005'],
        ['TC-GOV-005', 'TC-GOV-006', 'TC-GOV-007'],
        ['tools/supervisor/governance_validators*.py'],
        [
            'Continue from ET-W1-001: fix next batch of FAIL validators',
            'Target: all named validators in memoized-frolicking-donut pass',
            'Run full governance_validator_runner.py and verify improvement',
        ],
        [
            'All validators named in s005 now PASS',
            'governance_validator_runner.py shows 0 FAIL for s005-targeted validators',
        ],
        ['python tools/supervisor/governance_validator_runner.py 2>&1 | grep -E "FAIL|PASS" | head -30'],
        dependencies=['ET-W1-001'],
        wave=2,
        primary_lane='L01',
    ),

    make_task(
        'ET-W2-002',
        'WS-09-FODS-GOVERNANCE',
        'Execute FODS governance batch B: TCs 51-100 from splendid-squishing-orbit',
        ['s011'],
        [f'TC-SQO-{i:03d}' for i in range(51, 101)],
        ['tools/supervisor/', 'src/python/fods/', 'oracle/fods/'],
        [
            'Continue from ET-W1-003: process TCs 51-100',
            'Execute outstanding TCs in order',
            'Write evidence/raw/ET-W2-002/fods-batch-b-results.json',
        ],
        [
            'All 50 TCs in batch B have final disposition',
            'FODS tests still pass',
        ],
        ['python .venv/Scripts/pytest tests/fods/ -v 2>&1 | tail -10'],
        dependencies=['ET-W1-003'],
        wave=2,
        primary_lane='L01',
    ),

    make_task(
        'ET-W2-003',
        'WS-10-CONTROL-INDEX',
        'Validate and extend control index per clever-tickling-island plan',
        ['s014'],
        [],
        ['tools/supervisor/control_index/'],
        [
            'Read clever-tickling-island.md (s014) completely',
            'Run python -m tools.supervisor.control_index status',
            'Identify any outstanding TCs in s014',
            'Execute outstanding TCs',
            'Write evidence/raw/ET-W2-003/control-index-results.json',
        ],
        [
            'All 66 TCs in s014 have final disposition',
            'Control index operational (status command succeeds)',
        ],
        ['python -m tools.supervisor.control_index status 2>&1 | tail -10'],
        wave=2,
        primary_lane='L01',
    ),

    make_task(
        'ET-W2-004',
        'WS-19-DUAL-LANE-DOM',
        'Implement dual-lane DOM gap generator per serialized-petting-crab (TC-VPR-001..008)',
        ['s024'],
        ['TC-VPR-001', 'TC-VPR-002', 'TC-VPR-003', 'TC-VPR-004',
         'TC-VPR-005', 'TC-VPR-006', 'TC-VPR-007', 'TC-VPR-008'],
        ['tools/supervisor/', 'src/python/'],
        [
            'Read serialized-petting-crab.md (s024) completely',
            'precious-wandering-lighthouse (s023) is SUPERSEDED — do not execute its TCs',
            'Implement TC-VPR-001 through TC-VPR-008 in order',
            'Each TC: implement, test, record evidence',
            'Final: verify dual-lane DOM gap generator works end-to-end',
        ],
        [
            'TC-VPR-001 through TC-VPR-008 all pass acceptance criteria',
            'Dual-lane DOM gap generator produces correct output',
            'precious-wandering-lighthouse (s023) TCs disposed as SUPERSEDED_WITH_PROOF',
        ],
        ['python .venv/Scripts/pytest tests/ -k "dom" -v 2>&1 | tail -20'],
        wave=2,
        primary_lane='L02',
    ),

    # ── WAVE 3: After Wave 2 ─────────────────────────────────────────────────

    make_task(
        'ET-W3-001',
        'WS-09-FODS-GOVERNANCE',
        'Execute FODS governance batch C: TCs 101-150 from splendid-squishing-orbit',
        ['s011'],
        [f'TC-SQO-{i:03d}' for i in range(101, 151)],
        ['tools/supervisor/', 'src/python/fods/'],
        [
            'Continue from ET-W2-002: process TCs 101-150',
            'Write evidence/raw/ET-W3-001/fods-batch-c-results.json',
        ],
        ['All 50 TCs in batch C have final disposition', 'FODS tests pass'],
        ['python .venv/Scripts/pytest tests/fods/ -v 2>&1 | tail -5'],
        dependencies=['ET-W2-002'],
        wave=3,
        primary_lane='L01',
    ),

    make_task(
        'ET-W3-002',
        'WS-09-FODS-GOVERNANCE',
        'Execute FODS governance batch D: TCs 151-200 from splendid-squishing-orbit',
        ['s011'],
        [f'TC-SQO-{i:03d}' for i in range(151, 201)],
        ['tools/supervisor/', 'src/python/fods/'],
        [
            'Continue from ET-W3-001: process TCs 151-200',
            'Write evidence/raw/ET-W3-002/fods-batch-d-results.json',
        ],
        ['All 50 TCs in batch D have final disposition', 'FODS tests pass'],
        ['python .venv/Scripts/pytest tests/fods/ -v 2>&1 | tail -5'],
        dependencies=['ET-W3-001'],
        wave=3,
        primary_lane='L01',
    ),

    make_task(
        'ET-W3-003',
        'WS-09-FODS-GOVERNANCE',
        'Execute FODS governance batch E: TCs 201-250 from splendid-squishing-orbit',
        ['s011'],
        [f'TC-SQO-{i:03d}' for i in range(201, 251)],
        ['tools/supervisor/', 'src/python/fods/'],
        [
            'Continue from ET-W3-002: process TCs 201-250',
            'Write evidence/raw/ET-W3-003/fods-batch-e-results.json',
        ],
        ['All 50 TCs in batch E have final disposition', 'All 250 FODS TCs have final disposition'],
        ['python .venv/Scripts/pytest tests/fods/ -v 2>&1 | tail -5'],
        dependencies=['ET-W3-002'],
        wave=3,
        primary_lane='L01',
    ),

    make_task(
        'ET-W3-004',
        'WS-06-CODE-QUALITY-AUDIT',
        'Execute code quality audit per mutable-exploring-hellman: identify violations, produce repair plan',
        ['s007'],
        [],
        ['src/python/', 'tools/supervisor/'],
        [
            'Read mutable-exploring-hellman.md (s007) completely',
            'Run LOC checks, function count checks, analytics separation checks',
            'For each violation: document file, violation type, repair approach',
            'Write evidence/raw/ET-W3-004/code-quality-audit.json',
            'Produce ordered repair plan',
        ],
        [
            'All 106 TCs in s007 have final disposition',
            'code-quality-audit.json has complete violation inventory',
        ],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        dependencies=['ET-W1-002'],
        wave=3,
        primary_lane='L01',
    ),

    make_task(
        'ET-W3-005',
        'WS-26-ORACLE-HARDENING-2',
        'Execute oracle hardening Phase II per modular-noodling-galaxy (first 32 TCs)',
        ['s031'],
        [f'TC-MNG-{i:03d}' for i in range(1, 33)],
        ['tools/supervisor/execute_oracle.py', 'oracle/'],
        [
            'Read modular-noodling-galaxy.md (s031) completely',
            'Execute TCs 1-32 in order',
            'For each TC: implement, verify oracle cases pass, record evidence',
            'Write evidence/raw/ET-W3-005/oracle-h2-batch-a-results.json',
        ],
        [
            'TCs 1-32 in s031 have final disposition',
            'Oracle hardening phase II batch A complete',
        ],
        ['python tools/supervisor/execute_oracle.py --all-formats 2>&1 | tail -10'],
        dependencies=['ET-W0-004'],
        wave=3,
        primary_lane='L07',
    ),

    # ── WAVE 4: Broad remaining plans ────────────────────────────────────────

    make_task(
        'ET-W4-001',
        'WS-27-IMPERATIVE-BOOK',
        'Execute imperative-floating-book batch A: TCs 1-50',
        ['s032'],
        [f'TC-IFB-{i:03d}' for i in range(1, 51)],
        ['tools/supervisor/'],
        [
            'Read imperative-floating-book.md (s032) completely',
            'Execute TCs 1-50 in order',
            'Write evidence/raw/ET-W4-001/ifb-batch-a-results.json',
        ],
        ['TCs 1-50 in s032 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        wave=4,
        primary_lane='L01',
    ),

    make_task(
        'ET-W4-002',
        'WS-27-IMPERATIVE-BOOK',
        'Execute imperative-floating-book batch B: TCs 51-100',
        ['s032'],
        [f'TC-IFB-{i:03d}' for i in range(51, 101)],
        ['tools/supervisor/'],
        [
            'Continue from ET-W4-001: process TCs 51-100',
            'Write evidence/raw/ET-W4-002/ifb-batch-b-results.json',
        ],
        ['TCs 51-100 in s032 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        dependencies=['ET-W4-001'],
        wave=4,
        primary_lane='L01',
    ),

    make_task(
        'ET-W4-003',
        'WS-27-IMPERATIVE-BOOK',
        'Execute imperative-floating-book batch C: TCs 101-190',
        ['s032'],
        [f'TC-IFB-{i:03d}' for i in range(101, 191)],
        ['tools/supervisor/'],
        [
            'Continue from ET-W4-002: process TCs 101-190',
            'Write evidence/raw/ET-W4-003/ifb-batch-c-results.json',
        ],
        ['All 190 TCs in s032 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        dependencies=['ET-W4-002'],
        wave=4,
        primary_lane='L01',
    ),

    make_task(
        'ET-W4-004',
        'WS-15-HUMBLE-HATCHING',
        'Execute humble-hatching-lark in 2 batches: TCs 1-52',
        ['s019'],
        [f'TC-HHL-{i:03d}' for i in range(1, 53)],
        ['tools/supervisor/'],
        [
            'Read humble-hatching-lark.md (s019) completely',
            'Execute TCs 1-52 in order',
            'Write evidence/raw/ET-W4-004/hhl-batch-a-results.json',
        ],
        ['TCs 1-52 in s019 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        wave=4,
        primary_lane='L01',
    ),

    make_task(
        'ET-W4-005',
        'WS-15-HUMBLE-HATCHING',
        'Execute humble-hatching-lark TCs 53-104',
        ['s019'],
        [f'TC-HHL-{i:03d}' for i in range(53, 105)],
        ['tools/supervisor/'],
        [
            'Continue: process TCs 53-104',
            'Write evidence/raw/ET-W4-005/hhl-batch-b-results.json',
        ],
        ['All 104 TCs in s019 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        dependencies=['ET-W4-004'],
        wave=4,
        primary_lane='L01',
    ),

    make_task(
        'ET-W4-006',
        'WS-18-PLAYFUL-THUNDER',
        'Execute playful-discovering-thunder: all 95 TCs in 2 batches (batch A: 1-48)',
        ['s022'],
        [f'TC-PDT-{i:03d}' for i in range(1, 49)],
        ['tools/supervisor/', 'src/python/'],
        [
            'Read playful-discovering-thunder.md (s022)',
            'Execute TCs 1-48',
            'Write evidence/raw/ET-W4-006/pdt-batch-a-results.json',
        ],
        ['TCs 1-48 in s022 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        wave=4,
        primary_lane='L01',
    ),

    make_task(
        'ET-W4-007',
        'WS-18-PLAYFUL-THUNDER',
        'Execute playful-discovering-thunder TCs 49-95',
        ['s022'],
        [f'TC-PDT-{i:03d}' for i in range(49, 96)],
        ['tools/supervisor/', 'src/python/'],
        [
            'Continue: TCs 49-95',
            'Write evidence/raw/ET-W4-007/pdt-batch-b-results.json',
        ],
        ['All 95 TCs in s022 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        dependencies=['ET-W4-006'],
        wave=4,
        primary_lane='L01',
    ),

    make_task(
        'ET-W4-008',
        'WS-32-GOLDEN-BOOT',
        'Execute golden-foraging-boot: all 102 TCs in 2 batches (batch A: 1-51)',
        ['s038'],
        [f'TC-GFB-{i:03d}' for i in range(1, 52)],
        ['tools/supervisor/', 'src/python/'],
        [
            'Read golden-foraging-boot.md (s038)',
            'Execute TCs 1-51',
            'Write evidence/raw/ET-W4-008/gfb-batch-a-results.json',
        ],
        ['TCs 1-51 in s038 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        wave=4,
        primary_lane='L01',
    ),

    make_task(
        'ET-W4-009',
        'WS-32-GOLDEN-BOOT',
        'Execute golden-foraging-boot TCs 52-102',
        ['s038'],
        [f'TC-GFB-{i:03d}' for i in range(52, 103)],
        ['tools/supervisor/', 'src/python/'],
        [
            'Continue: TCs 52-102',
            'Write evidence/raw/ET-W4-009/gfb-batch-b-results.json',
        ],
        ['All 102 TCs in s038 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        dependencies=['ET-W4-008'],
        wave=4,
        primary_lane='L01',
    ),

    # ── WAVE 5: Remaining plans — mainly single-batch ────────────────────────

    make_task(
        'ET-W5-001',
        'WS-22-SILLY-TOWER',
        'Execute silly-popping-tower: all 76 TCs',
        ['s027'],
        [f'TC-SPT-{i:03d}' for i in range(1, 77)],
        ['tools/supervisor/'],
        [
            'Read silly-popping-tower.md (s027)',
            'Execute all 76 TCs',
            'Write evidence/raw/ET-W5-001/spt-results.json',
        ],
        ['All 76 TCs in s027 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        wave=5,
        primary_lane='L01',
    ),

    make_task(
        'ET-W5-002',
        'WS-23-PEPPY-LARK',
        'Execute peppy-crafting-lark product deepening: all 68 TCs',
        ['s028'],
        [f'TC-PCL-{i:03d}' for i in range(1, 69)],
        ['src/python/'],
        [
            'Read peppy-crafting-lark.md (s028)',
            'Execute all 68 TCs',
            'Write evidence/raw/ET-W5-002/pcl-results.json',
        ],
        ['All 68 TCs in s028 have final disposition', 'Product tests pass'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        wave=5,
        primary_lane='L02',
    ),

    make_task(
        'ET-W5-003',
        'WS-08-PRODUCT-LIBRARY-HEALING',
        'Execute splendid-prancing-wind product library healing: all 61 TCs',
        ['s010'],
        [f'TC-SPW-{i:03d}' for i in range(1, 62)],
        ['src/python/'],
        [
            'Read splendid-prancing-wind.md (s010)',
            'Execute all 61 TCs',
            'Write evidence/raw/ET-W5-003/spw-results.json',
        ],
        ['All 61 TCs in s010 have final disposition', 'Product library tests pass'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        wave=5,
        primary_lane='L02',
    ),

    make_task(
        'ET-W5-004',
        'WS-34-FUZZY-LOBSTER',
        'Execute fuzzy-conjuring-lobster forensic/archaeology: all 84 TCs',
        ['s040'],
        [f'TC-FCL-{i:03d}' for i in range(1, 85)],
        ['tools/supervisor/'],
        [
            'Read fuzzy-conjuring-lobster.md (s040)',
            'Execute all 84 TCs',
            'Write evidence/raw/ET-W5-004/fcl-results.json',
        ],
        ['All 84 TCs in s040 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -5'],
        wave=5,
        primary_lane='L01',
    ),

    make_task(
        'ET-W5-005',
        'WS-31-CHEEKY-MANATEE',
        'Verify TERMINAL_CLOSED disposition for cheeky-crafting-manatee TCs (self-declared done)',
        ['s036'],
        [f'TC-CCM-{i:03d}' for i in range(1, 101)],
        [],
        [
            'Read cheeky-crafting-manatee.md (s036)',
            'Verify each TC is genuinely complete per repository state',
            'For any TC not verified: add to re-open list',
            'Write evidence/raw/ET-W5-005/ccm-verification.json',
        ],
        [
            'All 100 TCs in s036 individually verified as SATISFIED_BY_VERIFIED_EXISTING_IMPLEMENTATION or TERMINAL_CLOSED_WITH_PROOF',
            'Any TCs not actually done are re-opened',
        ],
        ['cat .portfolio/goofy-orbiting-scroll/evidence/raw/ET-W5-005/ccm-verification.json'],
        wave=5,
        primary_lane='L01',
    ),

    make_task(
        'ET-W5-006',
        'WS-33-EFFERVESCENT-MARSHMALLOW',
        'Verify TERMINAL_CLOSED disposition for effervescent-sprouting-marshmallow TCs (self-declared done)',
        ['s039'],
        [f'TC-ESM-{i:03d}' for i in range(1, 17)],
        [],
        [
            'Read effervescent-sprouting-marshmallow.md (s039)',
            'Verify each of 16 TCs is genuinely complete',
            'Write evidence/raw/ET-W5-006/esm-verification.json',
        ],
        [
            'All 16 TCs in s039 individually verified',
            'Any TCs not actually done are re-opened',
        ],
        ['cat .portfolio/goofy-orbiting-scroll/evidence/raw/ET-W5-006/esm-verification.json'],
        wave=5,
        primary_lane='L01',
    ),

    # ── WAVE 5 continued — medium plans ──────────────────────────────────────

    make_task(
        'ET-W5-007',
        'WS-13-VAST-SPLASHING-ALLEN',
        'Execute vast-splashing-allen: all 12 TCs',
        ['s017'],
        [f'TC-VSA-{i:03d}' for i in range(1, 13)],
        ['tools/supervisor/'],
        ['Read vast-splashing-allen.md (s017) and execute all 12 TCs'],
        ['All 12 TCs in s017 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        wave=5, primary_lane='L01',
    ),

    make_task(
        'ET-W5-008',
        'WS-14-KIND-CRUNCHING-CORAL',
        'Execute kind-crunching-coral: all 7 TCs',
        ['s018'],
        [f'TC-KCC-{i:03d}' for i in range(1, 8)],
        ['tools/supervisor/'],
        ['Read kind-crunching-coral.md (s018) and execute all 7 TCs'],
        ['All 7 TCs in s018 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        wave=5, primary_lane='L01',
    ),

    make_task(
        'ET-W5-009',
        'WS-12-GLOWING-GROVE',
        'Execute glowing-swinging-grove: all 5 TCs',
        ['s016'],
        [f'TC-GSG-{i:03d}' for i in range(1, 6)],
        ['tools/supervisor/'],
        ['Read glowing-swinging-grove.md (s016) and execute all 5 TCs'],
        ['All 5 TCs in s016 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        wave=5, primary_lane='L01',
    ),

    make_task(
        'ET-W5-010',
        'WS-07-MINSKY-ELEGANCE',
        'Execute elegant-napping-minsky: all 7 TCs',
        ['s008'],
        [f'TC-ENM-{i:03d}' for i in range(1, 8)],
        ['src/python/'],
        ['Read elegant-napping-minsky.md (s008) and execute all 7 TCs'],
        ['All 7 TCs in s008 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        wave=5, primary_lane='L02',
    ),

    make_task(
        'ET-W5-011',
        'WS-30-WILD-CHERNY',
        'Execute wild-napping-cherny: all 9 TCs',
        ['s035'],
        [f'TC-WNC-{i:03d}' for i in range(1, 10)],
        ['tools/supervisor/'],
        ['Read wild-napping-cherny.md (s035) and execute all 9 TCs'],
        ['All 9 TCs in s035 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        wave=5, primary_lane='L01',
    ),

    make_task(
        'ET-W5-012',
        'WS-11-GOVERNANCE-SUITE-BATCH2',
        'Execute warm-enchanting-grove: all 49 TCs',
        ['s015'],
        [f'TC-WEG-{i:03d}' for i in range(1, 50)],
        ['tools/supervisor/'],
        ['Read warm-enchanting-grove.md (s015) and execute all 49 TCs'],
        ['All 49 TCs in s015 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        dependencies=['ET-W1-001'],
        wave=5, primary_lane='L01',
    ),

    make_task(
        'ET-W5-013',
        'WS-20-CERTIFICATION-LAYER',
        'Execute glittery-splashing-manatee certification layer: all 12 TCs',
        ['s025'],
        [f'TC-GSM-{i:03d}' for i in range(1, 13)],
        ['tools/supervisor/'],
        ['Read glittery-splashing-manatee.md (s025) and execute all 12 TCs'],
        ['All 12 TCs in s025 have final disposition', 'Certification layer operational'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        wave=5, primary_lane='L01',
    ),

    make_task(
        'ET-W5-014',
        'WS-24-FIZZY-HINTON',
        'Execute fizzy-imagining-hinton: all 36 TCs',
        ['s029'],
        [f'TC-FIH-{i:03d}' for i in range(1, 37)],
        ['tools/supervisor/'],
        ['Read fizzy-imagining-hinton.md (s029) and execute all 36 TCs'],
        ['All 36 TCs in s029 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        wave=5, primary_lane='L01',
    ),

    make_task(
        'ET-W5-015',
        'WS-25-SHIMMERING-MEERKAT',
        'Execute shimmering-rolling-meerkat: all 12 TCs',
        ['s030'],
        [f'TC-SRM-{i:03d}' for i in range(1, 13)],
        ['tools/supervisor/'],
        ['Read shimmering-rolling-meerkat.md (s030) and execute all 12 TCs'],
        ['All 12 TCs in s030 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        wave=5, primary_lane='L01',
    ),

    make_task(
        'ET-W5-016',
        'WS-28-OPTIMIZED-GIRAFFE',
        'Execute optimized-meandering-giraffe: all 12 TCs',
        ['s033'],
        [f'TC-OMG-{i:03d}' for i in range(1, 13)],
        ['tools/supervisor/'],
        ['Read optimized-meandering-giraffe.md (s033) and execute all 12 TCs'],
        ['All 12 TCs in s033 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        wave=5, primary_lane='L01',
    ),

    make_task(
        'ET-W5-017',
        'WS-29-SPLENDID-BEAVER',
        'Execute splendid-roaming-beaver: all 68 TCs',
        ['s034'],
        [f'TC-SRB-{i:03d}' for i in range(1, 69)],
        ['src/python/', 'tools/supervisor/'],
        ['Read splendid-roaming-beaver.md (s034) and execute all 68 TCs'],
        ['All 68 TCs in s034 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        wave=5, primary_lane='L02',
    ),

    make_task(
        'ET-W5-018',
        'WS-17-SPICY-GOSLING',
        'Execute spicy-sparking-gosling: all 39 TCs',
        ['s021'],
        [f'TC-SSG-{i:03d}' for i in range(1, 40)],
        ['tools/supervisor/'],
        ['Read spicy-sparking-gosling.md (s021) and execute all 39 TCs'],
        ['All 39 TCs in s021 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        wave=5, primary_lane='L01',
    ),

    make_task(
        'ET-W5-019',
        'WS-16-ATOMIC-METEOR',
        'Execute atomic-chasing-meteor: all 56 TCs',
        ['s020'],
        [f'TC-ACM-{i:03d}' for i in range(1, 57)],
        ['tools/supervisor/'],
        ['Read atomic-chasing-meteor.md (s020) and execute all 56 TCs'],
        ['All 56 TCs in s020 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        wave=5, primary_lane='L01',
    ),

    make_task(
        'ET-W5-020',
        'WS-35-LIVELY-ELEPHANT',
        'Execute lively-leaping-elephant: all 15 TCs',
        ['s041'],
        [f'TC-LLE-{i:03d}' for i in range(1, 16)],
        ['tools/supervisor/'],
        ['Read lively-leaping-elephant.md (s041) and execute all 15 TCs'],
        ['All 15 TCs in s041 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        wave=5, primary_lane='L01',
    ),

    make_task(
        'ET-W5-021',
        'WS-26-ORACLE-HARDENING-2',
        'Execute oracle hardening Phase II TCs 33-64 from modular-noodling-galaxy',
        ['s031'],
        [f'TC-MNG-{i:03d}' for i in range(33, 65)],
        ['tools/supervisor/execute_oracle.py', 'oracle/'],
        ['Continue oracle hardening Phase II: TCs 33-64',
         'Write evidence/raw/ET-W5-021/oracle-h2-batch-b-results.json'],
        ['All 64 TCs in s031 have final disposition'],
        ['python tools/supervisor/execute_oracle.py --all-formats 2>&1 | tail -5'],
        dependencies=['ET-W3-005'],
        wave=5, primary_lane='L07',
    ),

    make_task(
        'ET-W5-022',
        'WS-05-PIPELINE-RECONCILIATION',
        'Execute vast-wibbling-moon remaining TCs 1-162 (batch by batch after divergence repair)',
        ['s013'],
        [f'TC-VWM-{i:03d}' for i in range(1, 163)],
        ['reports/supervisor/', 'tools/supervisor/'],
        ['Read vast-wibbling-moon.md (s013) and execute outstanding TCs after pipeline repair',
         'Write evidence/raw/ET-W5-022/vwm-results.json'],
        ['All 162 TCs in s013 have final disposition', 'Pipeline reconciliation complete'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        dependencies=['ET-W1-004'],
        wave=5, primary_lane='L08',
    ),

    make_task(
        'ET-W5-023',
        'WS-04-AGENTIC-PARITY',
        'Execute agentic parity TCs identified as outstanding in ET-W0-005 assessment',
        ['s002'],
        [f'TC-AGT-{i:03d}' for i in range(2, 119)],
        ['tools/supervisor/'],
        ['Load ET-W0-005 assessment, execute outstanding agentic parity TCs',
         'Write evidence/raw/ET-W5-023/agentic-parity-results.json'],
        ['All 118 TCs in s002 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        dependencies=['ET-W0-005'],
        wave=5, primary_lane='L01',
    ),

    make_task(
        'ET-W5-024',
        'WS-21-ESPANSO-INTEGRATION',
        'Execute Espanso integration TCs from ET-W0-006 assessment',
        ['s026'],
        [f'TC-ESP-{i:03d}' for i in range(2, 29)],
        ['tools/supervisor/'],
        ['Load ET-W0-006 assessment, execute outstanding Espanso TCs',
         'Write evidence/raw/ET-W5-024/espanso-results.json'],
        ['All 28 TCs in s026 have final disposition'],
        ['python .venv/Scripts/pytest tests/ -q --tb=short 2>&1 | tail -3'],
        dependencies=['ET-W0-006'],
        wave=5, primary_lane='L05',
    ),
]

# ── Write workstreams ─────────────────────────────────────────────────────────
ws_dir = ROOT / 'workstreams'
ws_dir.mkdir(exist_ok=True)
for ws_id, ws_def in WORKSTREAMS.items():
    # Collect executable task IDs for this workstream
    ws_tasks = [t['task_id'] for t in EXECUTABLE_TASKS if t['workstream_id'] == ws_id]
    # Collect source task IDs
    all_src_tasks = []
    for pid in ws_def['source_plan_ids']:
        src_tcs = [s['source_task_id'] for s in stcs if s['source_plan_id'] == pid]
        all_src_tasks.extend(src_tcs)
    ws_record = {
        'schema_version': '1.0',
        'workstream_id': ws_id,
        'objective': ws_def['objective'],
        'source_plan_ids': ws_def['source_plan_ids'],
        'source_task_ids': sorted(set(all_src_tasks))[:500],  # cap for size
        'executable_task_ids': ws_tasks,
        'primary_lane': ws_def.get('primary_lane', 'L01'),
        'notes': ws_def.get('notes', ''),
        'status': 'PENDING',
    }
    (ws_dir / f'{ws_id}.json').write_text(json.dumps(ws_record, indent=2), encoding='utf-8')

print(f'Workstreams written: {len(WORKSTREAMS)}')

# ── Write executable tasks ────────────────────────────────────────────────────
et_dir = ROOT / 'executable-tasks'
et_dir.mkdir(exist_ok=True)
for task in EXECUTABLE_TASKS:
    (et_dir / f'{task["task_id"]}.json').write_text(json.dumps(task, indent=2), encoding='utf-8')
print(f'Executable tasks written: {len(EXECUTABLE_TASKS)}')

# ── Update wave registry ──────────────────────────────────────────────────────
waves_by_id: dict[int, list] = {}
for t in EXECUTABLE_TASKS:
    w = t.get('wave', 0)
    waves_by_id.setdefault(w, []).append(t['task_id'])

new_wave_registry = {
    'schema_version': '1.0',
    'portfolio_id': 'GOS-72E1DF137383C56F',
    'rebuilt_at': now,
    'granularity': 'EXECUTABLE_TASK',
    'waves': []
}
for w_num in sorted(waves_by_id.keys()):
    task_ids = waves_by_id[w_num]
    status = 'ACTIVE' if w_num == 0 else 'PENDING'
    new_wave_registry['waves'].append({
        'wave_id': f'W{w_num}',
        'wave_number': w_num,
        'status': status,
        'tasks': task_ids,
        'task_count': len(task_ids),
        'concurrency': 'SERIAL' if w_num == 0 else 'PARALLEL_SAFE_WITHIN_WAVE',
    })

(ROOT / 'wave-registry.json').write_text(json.dumps(new_wave_registry, indent=2), encoding='utf-8')
print(f'Wave registry rebuilt: {len(new_wave_registry["waves"])} waves')
for w in new_wave_registry['waves']:
    print(f'  W{w["wave_number"]}: {w["task_count"]} tasks — {w["tasks"][:3]}...')

# ── Source taskcard disposition assignment ────────────────────────────────────
# Assign every source taskcard to an executable task or a disposition
plan_to_tasks: dict[str, list] = {}
for t in EXECUTABLE_TASKS:
    for pid in t['source_plan_ids']:
        plan_to_tasks.setdefault(pid, []).append(t['task_id'])

# Superseded plans
SUPERSEDED_PLANS = {
    's004': {'superseded_by': 's005', 'executor': 'ET-W0-003'},  # iterative-mixing-shannon
    's023': {'superseded_by': 's024', 'executor': 'ET-W2-004'},  # precious-wandering-lighthouse
}

disposition_records = []
no_disposition_count = 0
for stc in stcs:
    pid = stc['source_plan_id']
    tid = stc['source_task_id']

    if pid in SUPERSEDED_PLANS:
        disp = 'SUPERSEDED_WITH_PROOF'
        exec_tasks = [SUPERSEDED_PLANS[pid]['executor']]
    elif pid in plan_to_tasks:
        disp = 'EXECUTE_TASK'
        exec_tasks = plan_to_tasks[pid]
    else:
        disp = 'NOT_MAPPED'
        exec_tasks = []
        no_disposition_count += 1

    disposition_records.append({
        'source_plan_id': pid,
        'source_task_id': tid,
        'disposition': disp,
        'executable_task_ids': exec_tasks,
    })

print(f'\nSource taskcard dispositions:')
from collections import Counter
disp_counts = Counter(r['disposition'] for r in disposition_records)
for d, c in disp_counts.most_common():
    print(f'  {d}: {c}')
print(f'NOT_MAPPED (must be 0): {no_disposition_count}')

# Write disposition summary
(ROOT / 'source-taskcards' / 'disposition-map.json').write_text(
    json.dumps({
        'schema_version': '1.0',
        'total': len(disposition_records),
        'dispositions': disp_counts,
        'not_mapped_count': no_disposition_count,
        'records': disposition_records,
    }, indent=2),
    encoding='utf-8'
)
print(f'Disposition map written: {len(disposition_records)} entries')
