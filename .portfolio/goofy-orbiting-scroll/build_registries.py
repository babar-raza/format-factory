"""TC-GOS-009 through TC-GOS-011: Build canonical registries, provenance map, and lane/conflict classification."""
import hashlib, json, datetime
from pathlib import Path

PORTFOLIO_ROOT = Path('.portfolio/goofy-orbiting-scroll')
PORTFOLIO_ID = 'GOS-72E1DF137383C56F'
REPO_REV = 'ccff6265e2351f02cb836d41e1fd981445c11032'
JOURNAL = PORTFOLIO_ROOT / 'journal/execution-journal.jsonl'
now = datetime.datetime.now(datetime.timezone.utc).isoformat()

def evt(event_id, event_type, task_id, reason, prev):
    e = {
        'schema_version': '1.0', 'event_id': event_id, 'timestamp': now,
        'portfolio_id': PORTFOLIO_ID, 'event_type': event_type, 'task_id': task_id,
        'lane_id': 'L09', 'repository_revision_before': REPO_REV, 'repository_revision_after': REPO_REV,
        'reason': reason, 'actor': 'claude-sonnet-4-6', 'parent_event_id': prev,
    }
    e['checksum'] = hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest()
    with JOURNAL.open('a') as f:
        f.write(json.dumps(e) + '\n')


# ============================================================
# TC-GOS-009: Canonical Requirement Registry
# ============================================================
print('\n=== TC-GOS-009: Canonical Requirement Registry ===')

# Semantic requirement groups identified from research across all 41 plans
canonical_requirements = [
    {
        'requirement_id': 'REQ-VALCOUNT-001',
        'normalized_statement': 'Resolve validator expected_count discrepancy (165 claimed vs 167 actual in runner)',
        'source_plan_ids': ['s001', 's007', 's012', 's013'],
        'source_anchors': ['multiple plans reference 165 validators; runner has 167'],
        'intent': 'Single authoritative validator count must be established and MEMORY.md corrected',
        'scope': 'tools/supervisor/governance_validator_runner.py + MEMORY.md',
        'acceptance_criteria': ['expected_count in runner matches MEMORY.md claims', 'all governance plans start from same count'],
        'affected_surfaces': ['tools/supervisor/governance_validator_runner.py', 'MEMORY.md'],
        'current_repository_state': 'runner has 167; MEMORY.md claims 165 — DISCREPANCY EXISTS',
        'conflicts': [],
        'canonical_task_ids': ['CT-001'],
        'status': 'NOT_STARTED',
    },
    {
        'requirement_id': 'REQ-PIPE-001',
        'normalized_statement': 'Reconcile two competing pipeline output authorities: next-work-items.json vs next-sprint.md',
        'source_plan_ids': ['s006', 's013'],
        'source_anchors': ['bubbly-dancing-pony REQ-IDS 1-19', 'vast-wibbling-moon S01-S15'],
        'intent': 'item_ids in next-sprint.md must match next-work-items.json; no fixture fallback competing authority',
        'scope': 'tools/supervisor/autonomous_cycle.py + generate_next_worker_prompt.py',
        'acceptance_criteria': ['next-sprint.md item_ids match next-work-items.json', 'idempotent second run produces zero material changes'],
        'affected_surfaces': ['tools/supervisor/autonomous_cycle.py', 'tools/supervisor/generate_next_worker_prompt.py'],
        'current_repository_state': 'PARTIAL — pipeline exists but divergence unresolved',
        'conflicts': ['CONFLICT-003'],
        'canonical_task_ids': ['CT-002'],
        'status': 'PARTIAL',
    },
    {
        'requirement_id': 'REQ-PLAN-IMPORT-001',
        'normalized_statement': 'Replace CLAUDE.md Step 0 cp command with governed plan_importer.py (idempotent, registry-backed)',
        'source_plan_ids': ['s009'],
        'source_anchors': ['stateful-booping-mountain full plan'],
        'intent': 'Eliminate 3 failure modes: plan overwrite via cp, partial taskcard parse, mission ID conflicts',
        'scope': 'tools/supervisor/plan_importer.py (new file)',
        'acceptance_criteria': ['plan_importer.py implements idempotent import', 'session-B does not overwrite session-A state', '.local/supervisor/plan-registry.json created'],
        'affected_surfaces': ['tools/supervisor/plan_importer.py', 'CLAUDE.md', '.local/supervisor/plan-registry.json'],
        'current_repository_state': 'NOT_STARTED (plan_importer.py does not exist)',
        'conflicts': [],
        'canonical_task_ids': ['CT-003'],
        'status': 'NOT_STARTED',
    },
    {
        'requirement_id': 'REQ-ORACLE-ASSESS-001',
        'normalized_statement': 'Audit oracle system for production-grade defects in execute_oracle.py, gate_executor.py, oracle-package.yaml',
        'source_plan_ids': ['s001'],
        'source_anchors': ['shiny-percolating-sky full plan'],
        'intent': 'Oracle must detect real parser regressions reliably across reruns',
        'scope': 'oracle/formats/, tools/supervisor/gate_executor.py',
        'acceptance_criteria': ['6 identified defects resolved', 'system detects parser regressions across reruns'],
        'affected_surfaces': ['oracle/formats/', 'tools/supervisor/gate_executor.py'],
        'current_repository_state': 'IN_PROGRESS',
        'conflicts': [],
        'canonical_task_ids': ['CT-004'],
        'status': 'IN_PROGRESS',
    },
    {
        'requirement_id': 'REQ-AGENT-PARITY-001',
        'normalized_statement': 'Machine-readable delivery mechanism for all 3 agents (Claude, Codex, Kilo); fix opt-out defaults',
        'source_plan_ids': ['s002'],
        'source_anchors': ['glimmering-hopping-kazoo TC-ACP-001..016'],
        'intent': 'All 16 parent taskcards closed; opt-out default in skill-registry.yaml fixed',
        'scope': '.supervisor/skill-registry.yaml, agent adapter tooling',
        'acceptance_criteria': ['All 16 TC-ACP TCs closed', 'machine-readable delivery for all 3 agents'],
        'affected_surfaces': ['.supervisor/skill-registry.yaml'],
        'current_repository_state': 'IN_PROGRESS',
        'conflicts': [],
        'canonical_task_ids': ['CT-005'],
        'status': 'IN_PROGRESS',
    },
    {
        'requirement_id': 'REQ-GOV-HEAL-001',
        'normalized_statement': 'Fix 7 governance enforcement root causes: V119/V120 skipping, check_continuation ignoring 22 validators, rework dead letter, blast-radius-register unused',
        'source_plan_ids': ['s004', 's005'],
        'source_anchors': ['iterative-mixing-shannon + memoized-frolicking-donut (CONFLICT-001)'],
        'intent': 'Governance system produces consistent verdicts on repeated runs; enforcement actually blocks bad sprints',
        'scope': 'tools/supervisor/governance_validators.py + check_continuation.py',
        'acceptance_criteria': ['All 23 TC-GOV TCs (v3) closed', 'Tier 1 enforcement fixes precede Tier 2'],
        'affected_surfaces': ['tools/supervisor/governance_validators.py', 'tools/supervisor/check_continuation.py'],
        'current_repository_state': 'NOT_STARTED',
        'conflicts': ['CONFLICT-001'],
        'canonical_task_ids': ['CT-006'],
        'status': 'NOT_STARTED',
    },
    {
        'requirement_id': 'REQ-FODS-GOV-001',
        'normalized_statement': 'Govern FODS product-code: resolve 43 dict fields, fix V88 false-negative rate (~70-80%), reconcile gap ledger',
        'source_plan_ids': ['s011'],
        'source_anchors': ['splendid-squishing-orbit full plan'],
        'intent': 'FODS product governance meets Gate 11 criteria; V88 false-negatives eliminated',
        'scope': 'src/python/fods/, tests/fods/',
        'acceptance_criteria': ['V87/V88 pass', 'all 25+ parent TCs closed', 'gap ledger reconciled'],
        'affected_surfaces': ['src/python/fods/', 'tests/fods/'],
        'current_repository_state': 'IN_PROGRESS',
        'conflicts': [],
        'canonical_task_ids': ['CT-007'],
        'status': 'IN_PROGRESS',
    },
    {
        'requirement_id': 'REQ-LIFECYCLE-001',
        'normalized_statement': 'Fix machinery lifecycle loop: AUDIT→GAP→HARDENING→EXECUTE→VERIFY→RE-AUDIT must iterate ≥2 times; lifecycle_audit.py never reads iteration state',
        'source_plan_ids': ['s037'],
        'source_anchors': ['velvet-swinging-wreath full plan'],
        'intent': 'Lifecycle loop iterates properly; ITERATION_REQUIRED triggers taskcard generation',
        'scope': 'tools/supervisor/lifecycle_audit.py + check_continuation.py',
        'acceptance_criteria': ['All 6 root causes fixed', 'behavioral iteration ≥2 proven'],
        'affected_surfaces': ['tools/supervisor/lifecycle_audit.py', 'tools/supervisor/check_continuation.py'],
        'current_repository_state': 'PARTIAL (lifecycle_audit.py exists, ITERATION_REQUIRED routing unimplemented)',
        'conflicts': [],
        'canonical_task_ids': ['CT-008'],
        'status': 'PARTIAL',
    },
    {
        'requirement_id': 'REQ-ORACLE-PHASE2-001',
        'normalized_statement': 'Oracle Phase II: progress all 20 Python FOSS formats to D2+ depth; auto-onboarding; oracle maturity Level 5',
        'source_plan_ids': ['s031'],
        'source_anchors': ['modular-noodling-galaxy TC-W0..W7'],
        'intent': 'Oracle layer becomes self-sustaining with auto-onboarding',
        'scope': 'oracle/formats/, tools/supervisor/governance_validators_oracle.py',
        'acceptance_criteria': ['All 17 TCs (W0-W7) closed', 'oracle maturity Level 5', 'auto-onboarding proven'],
        'affected_surfaces': ['oracle/formats/'],
        'current_repository_state': 'PARTIAL (all 20 formats at D1, D2 pending)',
        'conflicts': [],
        'canonical_task_ids': ['CT-009'],
        'status': 'PARTIAL',
    },
    {
        'requirement_id': 'REQ-SKILL-GOV-001',
        'normalized_statement': 'All 7 skill/command registries synchronized, governance enforced in CI, 165+ validators pass',
        'source_plan_ids': ['s032'],
        'source_anchors': ['imperative-floating-book TC-W0..W7'],
        'intent': 'Skill-first execution is machine-enforced via CI gates',
        'scope': '.supervisor/skill-registry.yaml + CI workflows',
        'acceptance_criteria': ['All 7 registries synchronized', 'CI gates active', '165+ validators pass'],
        'affected_surfaces': ['.supervisor/skill-registry.yaml', '.github/workflows/'],
        'current_repository_state': 'NOT_STARTED',
        'conflicts': [],
        'canonical_task_ids': ['CT-010'],
        'status': 'NOT_STARTED',
    },
    {
        'requirement_id': 'REQ-LLM-GRADER-001',
        'normalized_statement': 'LLM grader production reliability: separate test events from production log, add circuit breaker, retry path',
        'source_plan_ids': ['s015'],
        'source_anchors': ['warm-enchanting-grove TC-LGT-001..007'],
        'intent': 'RC-1 through RC-5 addressed; tests separated from production log',
        'scope': 'tools/supervisor/grader_reliability.py + llm_backend_config.py',
        'acceptance_criteria': ['All 7 TC-LGT TCs closed', 'circuit breaker implemented', 'test/prod log separation'],
        'affected_surfaces': ['tools/supervisor/grader_reliability.py', 'tools/supervisor/llm_backend_config.py'],
        'current_repository_state': 'PARTIAL (grader_reliability.py exists; circuit breaker status unknown)',
        'conflicts': [],
        'canonical_task_ids': ['CT-011'],
        'status': 'PARTIAL',
    },
    {
        'requirement_id': 'REQ-GAP-LIFECYCLE-001',
        'normalized_statement': 'Fix gap lifecycle: close 8 gaps stuck in implementation_verified state; add close_implementation_verified_gaps() to gap_closure_engine.py',
        'source_plan_ids': ['s018'],
        'source_anchors': ['kind-crunching-coral full plan'],
        'intent': 'implementation_verified gaps get terminal event; re-enter queue if no test found',
        'scope': 'tools/supervisor/gap_closure_engine.py + autonomous_cycle.py',
        'acceptance_criteria': ['3 DIF gaps + 5 install gaps closed', 'V-validator added for open+implementation_verified combo'],
        'affected_surfaces': ['tools/supervisor/gap_closure_engine.py', 'tools/supervisor/autonomous_cycle.py'],
        'current_repository_state': 'PARTIAL (gap_closure_engine.py exists 157 LOC; fix not implemented)',
        'conflicts': [],
        'canonical_task_ids': ['CT-012'],
        'status': 'PARTIAL',
    },
    {
        'requirement_id': 'REQ-DUAL-LANE-DOM-001',
        'normalized_statement': 'DOM maturity gap generator with supplemental=True preservation; wire into compiler; starvation scoring',
        'source_plan_ids': ['s023', 's024'],
        'source_anchors': ['precious-wandering-lighthouse TC-VPR-001..008 (superseded by s024)'],
        'intent': 'Generator produces 8 DOM gaps; compiler outputs 8 DOM items; starvation scoring verified',
        'scope': 'tools/supervisor/dom_maturity_promoter.py + capability_feature_compiler.py',
        'acceptance_criteria': ['TC-VPR-001..008 all closed', 'dom_maturity_gap_generator.py built and wired'],
        'affected_surfaces': ['tools/supervisor/dom_maturity_promoter.py', 'tools/supervisor/capability_feature_compiler.py'],
        'current_repository_state': 'PARTIAL (dom_maturity_promoter.py exists 119 LOC; generator not wired)',
        'conflicts': ['CONFLICT-002'],
        'canonical_task_ids': ['CT-013'],
        'status': 'PARTIAL',
    },
    {
        'requirement_id': 'REQ-PLAYBOOK-001',
        'normalized_statement': 'Playbook context flows through sprint via forward channel; drift detection active; 217 tests in CI',
        'source_plan_ids': ['s016'],
        'source_anchors': ['glowing-swinging-grove RC-1..RC-5'],
        'intent': 'All 5 structural changes integrated; playbook system forms closed feedback loop',
        'scope': 'tools/supervisor/autonomous_cycle.py + tests/playbook/',
        'acceptance_criteria': ['5 changes C1-C5 integrated', '217 tests in CI', 'V92 escalated to blocking'],
        'affected_surfaces': ['tools/supervisor/autonomous_cycle.py', 'tests/playbook/'],
        'current_repository_state': 'NOT_STARTED',
        'conflicts': [],
        'canonical_task_ids': ['CT-014'],
        'status': 'NOT_STARTED',
    },
    {
        'requirement_id': 'REQ-CANARY-001',
        'normalized_statement': 'Canary control: validator shadow mode, grader shadow log, gap compilation diff',
        'source_plan_ids': ['s014'],
        'source_anchors': ['clever-tickling-island REQ-DIAG-001..003'],
        'intent': 'Validators can run in shadow before promotion; provider switches logged; gap diffs before commit',
        'scope': '.supervisor/validator-shadow-registry.yaml (new)',
        'acceptance_criteria': ['3 components live', 'shadow registry operational', 'grader shadow log active'],
        'affected_surfaces': ['.supervisor/validator-shadow-registry.yaml'],
        'current_repository_state': 'NOT_STARTED (shadow registry does not exist)',
        'conflicts': [],
        'canonical_task_ids': ['CT-015'],
        'status': 'NOT_STARTED',
    },
    {
        'requirement_id': 'REQ-SUPERVISOR-AUDIT-001',
        'normalized_statement': 'Full supervisor machinery audit: LOC classification, component registry, problem catalog, guarantee matrix, risk register',
        'source_plan_ids': ['s003'],
        'source_anchors': ['polymorphic-foraging-feather TC-INV-000..011'],
        'intent': 'Final executive decision brief issued; target architecture defined',
        'scope': 'tools/supervisor/ (analysis only — no mutations)',
        'acceptance_criteria': ['All 12 TC-INV TCs closed', 'executive decision brief issued'],
        'affected_surfaces': [],
        'current_repository_state': 'NOT_STARTED',
        'conflicts': [],
        'canonical_task_ids': ['CT-016'],
        'status': 'NOT_STARTED',
    },
    {
        'requirement_id': 'REQ-CQGA-002-001',
        'normalized_statement': 'Code Quality Governance Audit CQGA-002: fix 7 root causes (A-G) covering Supreme Directive blocks, validator drift, promotion state',
        'source_plan_ids': ['s007'],
        'source_anchors': ['mutable-exploring-hellman TC-CQGA2-001..032+'],
        'intent': 'Governance system produces consistent verdicts on repeated runs',
        'scope': 'tools/supervisor/governance_validators.py + check_continuation.py',
        'acceptance_criteria': ['All repairs merged', 'consistent verdicts across reruns'],
        'affected_surfaces': ['tools/supervisor/governance_validators.py'],
        'current_repository_state': 'NOT_STARTED',
        'conflicts': [],
        'canonical_task_ids': ['CT-017'],
        'status': 'NOT_STARTED',
    },
    {
        'requirement_id': 'REQ-ESPANSO-001',
        'normalized_statement': 'All 123 capabilities mapped in espanso-provenance-map.yaml; duplicates resolved; conflict log closed',
        'source_plan_ids': ['s026'],
        'source_anchors': ['imperative-coalescing-bengio full plan'],
        'intent': 'Espanso integration complete with 0 broken references',
        'scope': 'espanso-provenance-map.yaml',
        'acceptance_criteria': ['All 123 capabilities mapped', 'conflict log closed'],
        'affected_surfaces': ['espanso-provenance-map.yaml'],
        'current_repository_state': 'IN_PROGRESS (118 entries exist, 0 broken references)',
        'conflicts': [],
        'canonical_task_ids': ['CT-018'],
        'status': 'IN_PROGRESS',
    },
    {
        'requirement_id': 'REQ-PRODUCT-LIBRARY-001',
        'normalized_statement': 'Enforce class-aggregate LOC measurement; trajectory requirement; oracle coverage extended to .NET FODS',
        'source_plan_ids': ['s010'],
        'source_anchors': ['splendid-prancing-wind TC-SPW-001..007'],
        'intent': 'Monolith split into partial classes no longer games V78; aggregate checked',
        'scope': 'tools/supervisor/governance_validators.py (V78 enhancement) + src/net/fods/',
        'acceptance_criteria': ['All 7 TC-SPW TCs closed', 'class-aggregate LOC enforced', 'oracle extended to .NET FODS'],
        'affected_surfaces': ['tools/supervisor/governance_validators.py', 'src/net/fods/'],
        'current_repository_state': 'NOT_STARTED',
        'conflicts': [],
        'canonical_task_ids': ['CT-019'],
        'status': 'NOT_STARTED',
    },
    {
        'requirement_id': 'REQ-FORENSICS-HEAL-001',
        'normalized_statement': 'Heal forensic sprint findings: phantom TC refs, priority conflicts, test count instability, uncommitted files',
        'source_plan_ids': ['s017'],
        'source_anchors': ['vast-splashing-allen FINDING-001..006'],
        'intent': 'All 6 findings healed; working tree clean; P1-P3 gaps executable',
        'scope': 'Multiple: plans/, tests/, .local/supervisor/',
        'acceptance_criteria': ['FINDING-001..006 all healed', 'working tree clean'],
        'affected_surfaces': ['plans/', 'tests/', '.local/supervisor/'],
        'current_repository_state': 'NOT_STARTED',
        'conflicts': [],
        'canonical_task_ids': ['CT-020'],
        'status': 'NOT_STARTED',
    },
    # Additional requirements for remaining plans
    {
        'requirement_id': 'REQ-CERT-LAYER-001',
        'normalized_statement': 'Certification layer formalization: V88 terminal closeout gate, layer_promotion.py covering all 7 registries',
        'source_plan_ids': ['s025'],
        'source_anchors': ['glittery-splashing-manatee TC-LHEAL-001..010'],
        'intent': 'L28 completeness verified; all 7 registries covered',
        'scope': 'tools/supervisor/ (certification + layer_promotion)',
        'acceptance_criteria': ['All 10 TC-LHEAL TCs closed', 'V88 validator added'],
        'affected_surfaces': ['tools/supervisor/'],
        'current_repository_state': 'NOT_STARTED',
        'conflicts': [],
        'canonical_task_ids': ['CT-021'],
        'status': 'NOT_STARTED',
    },
    {
        'requirement_id': 'REQ-STUB-V149-001',
        'normalized_statement': 'V149 stub gate fix: over-broad allowlist pattern, implement baseline-tracking in V149 to match V105/V106',
        'source_plan_ids': ['s012'],
        'source_anchors': ['twinkly-nibbling-platypus TC-TNP-001..002'],
        'intent': 'Write registry/stub-violations-baseline.json; V149 uses baseline tracking',
        'scope': 'tools/supervisor/governance_validators.py (V149) + registry/stub-violations-baseline.json',
        'acceptance_criteria': ['TC-TNP-001..002 closed', 'baseline.json written', 'V149 uses it'],
        'affected_surfaces': ['tools/supervisor/governance_validators.py', 'registry/'],
        'current_repository_state': 'NOT_STARTED',
        'conflicts': [],
        'canonical_task_ids': ['CT-022'],
        'status': 'NOT_STARTED',
    },
    {
        'requirement_id': 'REQ-OCRD-001',
        'normalized_statement': 'Operational Control Record and Discovery: wire control index into decision paths; gap_attempts table; evidence grading cross-check',
        'source_plan_ids': ['s027'],
        'source_anchors': ['silly-popping-tower TC-OCRD-A1..C6+'],
        'intent': 'Control index writes back to decision paths; contradictions enforced',
        'scope': 'tools/supervisor/control_index/',
        'acceptance_criteria': ['All OCRD TCs closed', 'gap_attempts table created', 'contradictions enforced'],
        'affected_surfaces': ['tools/supervisor/control_index/'],
        'current_repository_state': 'PARTIAL (control index exists, write-back missing)',
        'conflicts': [],
        'canonical_task_ids': ['CT-023'],
        'status': 'PARTIAL',
    },
    {
        'requirement_id': 'REQ-SKILL-FIRST-003-001',
        'normalized_statement': 'SKILL-FIRST-003: Enforce composable skill-first execution; 122 skills verified; 8 pilots complete',
        'source_plan_ids': ['s035'],
        'source_anchors': ['wild-napping-cherny TC-SFE3-000..008'],
        'intent': 'All 122 active skills verified; SKILL-GAP-003/009/010 resolved',
        'scope': '.supervisor/skill-registry.yaml + tools/supervisor/',
        'acceptance_criteria': ['All 9 TC-SFE3 TCs closed', '8 pilots with receipts'],
        'affected_surfaces': ['.supervisor/skill-registry.yaml'],
        'current_repository_state': 'NOT_STARTED',
        'conflicts': [],
        'canonical_task_ids': ['CT-024'],
        'status': 'NOT_STARTED',
    },
    {
        'requirement_id': 'REQ-REMAINING-MACHINERY',
        'normalized_statement': 'Remaining machinery plans: drivers subsystem, root folder recon, API architecture policy, Gate 4 hardening, capability layer, FIOP, sprint engine, spec-to-code forensic, QName healing, generation archaeology, governance healing sprint',
        'source_plan_ids': ['s021','s022','s008','s020','s019','s033','s034','s036','s039','s040','s041'],
        'source_anchors': ['multiple plans'],
        'intent': 'All listed plans executed and closed per their individual acceptance criteria',
        'scope': 'Multiple lanes',
        'acceptance_criteria': ['Each plan closed per its own criteria'],
        'affected_surfaces': ['Multiple'],
        'current_repository_state': 'MIXED (s036 and s039 TERMINAL_CLOSED, s019 PARTIAL, rest NOT_STARTED)',
        'conflicts': [],
        'canonical_task_ids': ['CT-025'],
        'status': 'NOT_STARTED',
    },
    {
        'requirement_id': 'REQ-PRODUCT-DEEPENING-001',
        'normalized_statement': 'Dual-lane product deepening: behavioral proof execution for DOM maturity; peppy-crafting-lark and fizzy-imagining-hinton',
        'source_plan_ids': ['s028', 's029'],
        'source_anchors': ['peppy-crafting-lark + fizzy-imagining-hinton'],
        'intent': 'DOM maturity behavioral proof; portfolio recon-and-healing waves complete',
        'scope': 'src/python/ + tools/supervisor/',
        'acceptance_criteria': ['All TCs closed for both plans'],
        'affected_surfaces': ['src/python/'],
        'current_repository_state': 'PARTIAL (dom_maturity_promoter.py exists)',
        'conflicts': [],
        'canonical_task_ids': ['CT-026'],
        'status': 'PARTIAL',
    },
]

req_registry = {
    'schema_version': '1.0',
    'portfolio_id': PORTFOLIO_ID,
    'generated_at': now,
    'requirement_count': len(canonical_requirements),
    'requirements': canonical_requirements
}
(PORTFOLIO_ROOT / 'requirement-registry.json').write_text(json.dumps(req_registry, indent=2))
print(f'requirement-registry.json: {len(canonical_requirements)} canonical requirements')

# ============================================================
# TC-GOS-009: Canonical Task Registry
# ============================================================

canonical_tasks = [
    {'task_id': 'CT-001', 'objective': 'Fix validator expected_count discrepancy (165 vs 167)', 'requirement_ids': ['REQ-VALCOUNT-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s001','s007','s012','s013'], 'status': 'NOT_STARTED', 'estimated_context_class': 'SMALL'},
    {'task_id': 'CT-002', 'objective': 'Reconcile next-work-items.json vs next-sprint.md pipeline authority', 'requirement_ids': ['REQ-PIPE-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s006','s013'], 'status': 'PARTIAL', 'estimated_context_class': 'MEDIUM'},
    {'task_id': 'CT-003', 'objective': 'Build plan_importer.py (idempotent plan ingestion)', 'requirement_ids': ['REQ-PLAN-IMPORT-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s009'], 'status': 'NOT_STARTED', 'estimated_context_class': 'MEDIUM'},
    {'task_id': 'CT-004', 'objective': 'Oracle system production-grade assessment and defect resolution', 'requirement_ids': ['REQ-ORACLE-ASSESS-001'], 'primary_lane': 'L07', 'source_plan_ids': ['s001'], 'status': 'IN_PROGRESS', 'estimated_context_class': 'LARGE'},
    {'task_id': 'CT-005', 'objective': 'Agentic system completion and parity (Claude/Codex/Kilo)', 'requirement_ids': ['REQ-AGENT-PARITY-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s002'], 'status': 'IN_PROGRESS', 'estimated_context_class': 'LARGE'},
    {'task_id': 'CT-006', 'objective': 'Product governance healing (memoized-frolicking-donut v3, 23 TCs)', 'requirement_ids': ['REQ-GOV-HEAL-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s004','s005'], 'status': 'NOT_STARTED', 'estimated_context_class': 'LARGE', 'supersedes': ['CT-004-ITER-001']},
    {'task_id': 'CT-007', 'objective': 'FODS product-code governance: V88 fix, gap ledger reconciliation', 'requirement_ids': ['REQ-FODS-GOV-001'], 'primary_lane': 'L02', 'source_plan_ids': ['s011'], 'status': 'IN_PROGRESS', 'estimated_context_class': 'VERY_LARGE'},
    {'task_id': 'CT-008', 'objective': 'Machinery lifecycle healing: AUDIT→EXECUTE loop iteration fix', 'requirement_ids': ['REQ-LIFECYCLE-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s037'], 'status': 'PARTIAL', 'estimated_context_class': 'MEDIUM'},
    {'task_id': 'CT-009', 'objective': 'Oracle Phase II: D2+ depth for all 20 formats; auto-onboarding', 'requirement_ids': ['REQ-ORACLE-PHASE2-001'], 'primary_lane': 'L07', 'source_plan_ids': ['s031'], 'status': 'PARTIAL', 'estimated_context_class': 'LARGE'},
    {'task_id': 'CT-010', 'objective': 'Forensic skill/command governance audit: 7 registries synchronized, CI gates', 'requirement_ids': ['REQ-SKILL-GOV-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s032'], 'status': 'NOT_STARTED', 'estimated_context_class': 'LARGE'},
    {'task_id': 'CT-011', 'objective': 'LLM grader reliability: circuit breaker, test/prod log separation, retry path', 'requirement_ids': ['REQ-LLM-GRADER-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s015'], 'status': 'PARTIAL', 'estimated_context_class': 'MEDIUM'},
    {'task_id': 'CT-012', 'objective': 'Fix gap lifecycle: implementation_verified terminal event; close 8 stuck gaps', 'requirement_ids': ['REQ-GAP-LIFECYCLE-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s018'], 'status': 'PARTIAL', 'estimated_context_class': 'SMALL'},
    {'task_id': 'CT-013', 'objective': 'Dual-lane DOM gap generator: supplemental=True, wired into compiler', 'requirement_ids': ['REQ-DUAL-LANE-DOM-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s023','s024'], 'status': 'PARTIAL', 'estimated_context_class': 'MEDIUM'},
    {'task_id': 'CT-014', 'objective': 'Playbook system structural integration: forward channel, CI, V92 escalation', 'requirement_ids': ['REQ-PLAYBOOK-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s016'], 'status': 'NOT_STARTED', 'estimated_context_class': 'MEDIUM'},
    {'task_id': 'CT-015', 'objective': 'Canary control: validator shadow registry, grader shadow log, gap diff tool', 'requirement_ids': ['REQ-CANARY-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s014'], 'status': 'NOT_STARTED', 'estimated_context_class': 'MEDIUM'},
    {'task_id': 'CT-016', 'objective': 'Supervisor machinery full audit: LOC classification, component registry, risk register', 'requirement_ids': ['REQ-SUPERVISOR-AUDIT-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s003'], 'status': 'NOT_STARTED', 'estimated_context_class': 'LARGE'},
    {'task_id': 'CT-017', 'objective': 'CQGA-002: Fix governance audit root causes A-G', 'requirement_ids': ['REQ-CQGA-002-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s007'], 'status': 'NOT_STARTED', 'estimated_context_class': 'LARGE'},
    {'task_id': 'CT-018', 'objective': 'Espanso integration completion: all 123 capabilities mapped', 'requirement_ids': ['REQ-ESPANSO-001'], 'primary_lane': 'L05', 'source_plan_ids': ['s026'], 'status': 'IN_PROGRESS', 'estimated_context_class': 'SMALL'},
    {'task_id': 'CT-019', 'objective': 'Product library healing: class-aggregate LOC enforcement; .NET oracle extension', 'requirement_ids': ['REQ-PRODUCT-LIBRARY-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s010'], 'status': 'NOT_STARTED', 'estimated_context_class': 'MEDIUM'},
    {'task_id': 'CT-020', 'objective': 'Forensics healing sprint: heal 6 findings, clean working tree', 'requirement_ids': ['REQ-FORENSICS-HEAL-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s017'], 'status': 'NOT_STARTED', 'estimated_context_class': 'MEDIUM'},
    {'task_id': 'CT-021', 'objective': 'Certification layer formalization: V88 gate, layer_promotion.py 7 registries', 'requirement_ids': ['REQ-CERT-LAYER-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s025'], 'status': 'NOT_STARTED', 'estimated_context_class': 'MEDIUM'},
    {'task_id': 'CT-022', 'objective': 'V149 stub gate fix: baseline tracking, stub-violations-baseline.json', 'requirement_ids': ['REQ-STUB-V149-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s012'], 'status': 'NOT_STARTED', 'estimated_context_class': 'SMALL'},
    {'task_id': 'CT-023', 'objective': 'OCRD: wire control index into decision paths; gap_attempts table; contradiction enforcement', 'requirement_ids': ['REQ-OCRD-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s027'], 'status': 'PARTIAL', 'estimated_context_class': 'MEDIUM'},
    {'task_id': 'CT-024', 'objective': 'SKILL-FIRST-003: enforce composable skill-first execution; 122 skills; 8 pilots', 'requirement_ids': ['REQ-SKILL-FIRST-003-001'], 'primary_lane': 'L01', 'source_plan_ids': ['s035'], 'status': 'NOT_STARTED', 'estimated_context_class': 'MEDIUM'},
    {'task_id': 'CT-025', 'objective': 'Remaining machinery plans batch: drivers, root-folder-recon, API policy, Gate4, capability, FIOP, sprint-engine, spec-forensic, QName, archaeology, gov-healing-sprint', 'requirement_ids': ['REQ-REMAINING-MACHINERY'], 'primary_lane': 'L01', 'source_plan_ids': ['s008','s019','s020','s021','s022','s033','s034','s036','s039','s040','s041'], 'status': 'NOT_STARTED', 'estimated_context_class': 'VERY_LARGE'},
    {'task_id': 'CT-026', 'objective': 'Product deepening: DOM maturity behavioral proof; portfolio recon waves', 'requirement_ids': ['REQ-PRODUCT-DEEPENING-001'], 'primary_lane': 'L02', 'source_plan_ids': ['s028','s029'], 'status': 'PARTIAL', 'estimated_context_class': 'LARGE'},
]

task_registry = {
    'schema_version': '1.0',
    'portfolio_id': PORTFOLIO_ID,
    'generated_at': now,
    'task_count': len(canonical_tasks),
    'tasks': canonical_tasks
}
(PORTFOLIO_ROOT / 'task-registry.json').write_text(json.dumps(task_registry, indent=2))
print(f'task-registry.json: {len(canonical_tasks)} canonical tasks')

# Update plan records with canonical IDs
req_by_plan = {}
for req in canonical_requirements:
    for pid in req['source_plan_ids']:
        req_by_plan.setdefault(pid, []).append(req['requirement_id'])

task_by_plan = {}
for task in canonical_tasks:
    for pid in task['source_plan_ids']:
        task_by_plan.setdefault(pid, []).append(task['task_id'])

import hashlib as hl
for source_id in [s['source_id'] for s in json.loads((PORTFOLIO_ROOT / 'source-inventory.json').read_text())['sources']]:
    r_path = PORTFOLIO_ROOT / f'plan-registry/{source_id}.json'
    if not r_path.exists():
        continue
    record = json.loads(r_path.read_text())
    record['canonical_requirement_ids'] = req_by_plan.get(source_id, [])
    record['canonical_task_ids'] = task_by_plan.get(source_id, [])
    cs = hl.sha256(json.dumps({k:v for k,v in record.items() if k!='checksum'}, sort_keys=True).encode()).hexdigest()
    record['checksum'] = cs
    r_path.write_text(json.dumps(record, indent=2))

evt('EVT-009', 'REGISTRIES_BUILT', 'TC-GOS-009',
    f'TC-GOS-009: {len(canonical_requirements)} canonical reqs, {len(canonical_tasks)} canonical tasks', 'EVT-008')
print('EVT-009 REGISTRIES_BUILT')

# ============================================================
# TC-GOS-010: Provenance Map
# ============================================================
print('\n=== TC-GOS-010: Provenance Map ===')

# Source requirement mappings (one per plan-level requirement cluster)
source_req_mappings = []
source_task_mappings = []

records_dir = PORTFOLIO_ROOT / 'plan-registry'
for r_path in sorted(records_dir.glob('*.json')):
    record = json.loads(r_path.read_text())
    source_id = record['plan_id']
    c_req_ids = record.get('canonical_requirement_ids', [])
    c_task_ids = record.get('canonical_task_ids', [])

    # Plan-level requirement mapping
    source_req_mappings.append({
        'source_plan_id': source_id,
        'source_requirement_id': f'REQ-PLAN-{source_id}',
        'source_anchor': f'{source_id}.objectives',
        'canonical_requirement_ids': c_req_ids,
        'canonical_task_ids': c_task_ids,
        'disposition': 'EXECUTE_CANONICAL_TASK' if c_task_ids else 'REQUIRES_HUMAN_DECISION',
        'evidence': [],
        'status': 'MAPPED' if c_task_ids else 'NOT_MAPPED'
    })

    # Per-taskcard mappings
    for tc in record.get('source_taskcards', []):
        tc_id = tc['tc_id']
        # Map to canonical tasks based on plan membership
        source_task_mappings.append({
            'source_plan_id': source_id,
            'source_task_id': tc_id,
            'source_anchor': f'{source_id}.taskcards.{tc_id}',
            'canonical_task_ids': c_task_ids,
            'disposition': 'EXECUTE_CANONICAL_TASK' if c_task_ids else 'REQUIRES_HUMAN_DECISION',
            'evidence': [],
            'status': 'MAPPED' if c_task_ids else 'NOT_MAPPED'
        })

# Handle CONFLICT-001: iterative-mixing-shannon (s004) SUPERSEDED BY memoized-frolicking-donut (s005)
for m in source_req_mappings:
    if m['source_plan_id'] == 's004':
        m['disposition'] = 'CONSOLIDATED_WITH_EQUIVALENT_TASK'
        m['evidence'] = ['CONFLICT-001: s005 (memoized-frolicking-donut v3) has stronger acceptance criteria (23 TCs vs 19); s004 SUPERSEDED']
        m['status'] = 'MAPPED'

# Handle CONFLICT-002: precious-wandering-lighthouse (s023) SUPERSEDED BY serialized-petting-crab (s024)
for m in source_req_mappings:
    if m['source_plan_id'] == 's023':
        m['disposition'] = 'SUPERSEDED_WITH_PROOF'
        m['evidence'] = ['CONFLICT-002: s024 (serialized-petting-crab) has newer mission ID DUAL-LANE-VERIFICATION-001; identical TC-VPR-001..008 IDs confirm revision']
        m['status'] = 'MAPPED'

# Handle TERMINAL_CLOSED plans
for m in source_req_mappings:
    if m['source_plan_id'] in ('s036', 's039'):
        m['disposition'] = 'SUPERSEDED_WITH_PROOF'
        m['evidence'] = ['Plan declared TERMINAL_CLOSED in source file; treated as completed per source declaration']
        m['status'] = 'MAPPED'

# Canonical task → all source items reverse index
ct_to_sources = {}
for task in canonical_tasks:
    ct_to_sources[task['task_id']] = {
        'canonical_task_id': task['task_id'],
        'source_plan_ids': task['source_plan_ids'],
        'all_affected_source_requirements': [m['source_requirement_id'] for m in source_req_mappings if task['task_id'] in m['canonical_task_ids']],
        'all_affected_source_tasks': [m['source_task_id'] for m in source_task_mappings if task['task_id'] in m['canonical_task_ids']],
    }

prov_map = {
    'schema_version': '1.0',
    'portfolio_id': PORTFOLIO_ID,
    'generated_at': now,
    'source_requirement_mappings': source_req_mappings,
    'source_task_mappings': source_task_mappings,
    'canonical_task_reverse_index': ct_to_sources,
    'counters': {
        'source_req_mappings': len(source_req_mappings),
        'source_task_mappings': len(source_task_mappings),
        'not_mapped_reqs': sum(1 for m in source_req_mappings if m['status'] == 'NOT_MAPPED'),
        'not_mapped_tasks': sum(1 for m in source_task_mappings if m['status'] == 'NOT_MAPPED'),
    }
}
(PORTFOLIO_ROOT / 'provenance-map.json').write_text(json.dumps(prov_map, indent=2))

not_mapped_reqs = prov_map['counters']['not_mapped_reqs']
not_mapped_tasks = prov_map['counters']['not_mapped_tasks']
print(f'provenance-map.json: {len(source_req_mappings)} req-mappings, {len(source_task_mappings)} task-mappings')
print(f'NOT_MAPPED requirements: {not_mapped_reqs}')
print(f'NOT_MAPPED taskcards: {not_mapped_tasks}')

evt('EVT-010', 'PROVENANCE_MAPPED', 'TC-GOS-010',
    f'TC-GOS-010: {len(source_req_mappings)} req-mappings, {len(source_task_mappings)} task-mappings. NOT_MAPPED_REQS={not_mapped_reqs}', 'EVT-009')
print('EVT-010 PROVENANCE_MAPPED')

# ============================================================
# TC-GOS-011: Lane Discovery + Conflict Classification
# ============================================================
print('\n=== TC-GOS-011: Lane Discovery + Conflict Classification ===')

lane_registry = {
    'schema_version': '1.0',
    'portfolio_id': PORTFOLIO_ID,
    'generated_at': now,
    'lanes': [
        {'lane_id': 'L01', 'purpose': 'Supervisor machinery (tools/supervisor/)', 'owned_paths': ['tools/supervisor/'], 'concurrency_limit': 1, 'status': 'ACTIVE'},
        {'lane_id': 'L02', 'purpose': 'FOSS Python product source (src/python/)', 'owned_paths': ['src/python/'], 'concurrency_limit': 3, 'status': 'ACTIVE'},
        {'lane_id': 'L03', 'purpose': '.NET product source (src/net/)', 'owned_paths': ['src/net/'], 'concurrency_limit': 3, 'status': 'ACTIVE'},
        {'lane_id': 'L04', 'purpose': 'Test suite (tests/)', 'owned_paths': ['tests/'], 'concurrency_limit': 1, 'status': 'ACTIVE'},
        {'lane_id': 'L05', 'purpose': 'Governance schemas + capability registry (.governance/)', 'owned_paths': ['.governance/'], 'concurrency_limit': 1, 'status': 'ACTIVE'},
        {'lane_id': 'L06', 'purpose': 'Format registry + source baseline (registry/)', 'owned_paths': ['registry/'], 'concurrency_limit': 1, 'status': 'ACTIVE'},
        {'lane_id': 'L07', 'purpose': 'Oracle layer (oracle/)', 'owned_paths': ['oracle/'], 'concurrency_limit': 2, 'status': 'ACTIVE'},
        {'lane_id': 'L08', 'purpose': 'Supervisor outputs (reports/supervisor/)', 'owned_paths': ['reports/supervisor/'], 'concurrency_limit': 1, 'status': 'ACTIVE'},
        {'lane_id': 'L09', 'purpose': 'Plan migration (plans/.claude/)', 'owned_paths': ['plans/.claude/'], 'concurrency_limit': 1, 'status': 'ACTIVE'},
        {'lane_id': 'L10', 'purpose': 'Tooling (tools/capability_sync/, tools/supervisor/control_index/)', 'owned_paths': ['tools/capability_sync/', 'tools/supervisor/control_index/'], 'concurrency_limit': 1, 'status': 'ACTIVE'},
    ]
}
(PORTFOLIO_ROOT / 'lane-registry.json').write_text(json.dumps(lane_registry, indent=2))
n_lanes = len(lane_registry['lanes']); print(f'lane-registry.json: {n_lanes} lanes')

# Conflict + relationship records
conflicts = [
    {
        'relationship_id': 'REL-001',
        'classification': 'SEMANTIC_DUPLICATE',
        'left_task_id': 'CT-006-iterative-mixing',
        'right_task_id': 'CT-006',
        'left_plan_id': 's004',
        'right_plan_id': 's005',
        'conflict_id': 'CONFLICT-001',
        'resolution': 'EXECUTE_RIGHT: memoized-frolicking-donut v3 (23 TCs) has stronger acceptance criteria. iterative-mixing-shannon (s004) is CONSOLIDATED_WITH_EQUIVALENT_TASK. No separate execution needed for s004.',
        'evidence': ['v3 vs prior version naming', 'v3 adds V150-V155 validators vs V150-V163 in s004 (v3 is more targeted and current)', '23 vs 19 taskcards'],
        'status': 'RESOLVED'
    },
    {
        'relationship_id': 'REL-002',
        'classification': 'REVISION_CANDIDATE',
        'left_plan_id': 's023',
        'right_plan_id': 's024',
        'conflict_id': 'CONFLICT-002',
        'resolution': 'EXECUTE_RIGHT: serialized-petting-crab (s024) supersedes precious-wandering-lighthouse (s023). Identical taskcard IDs TC-VPR-001..008 confirm they are revisions. Newer mission ID DUAL-LANE-VERIFICATION-001 vs CERT-FORENSICS-20260710 confirms s024 is the current version.',
        'evidence': ['identical TC-VPR-001..008 IDs', 'newer mission ID in s024'],
        'status': 'RESOLVED'
    },
    {
        'relationship_id': 'REL-003',
        'classification': 'PARTIAL_OVERLAP',
        'left_plan_id': 's013',
        'right_plan_id': 's006',
        'conflict_id': 'CONFLICT-003',
        'resolution': 'CONSOLIDATE: vast-wibbling-moon (s013, 29 TCs, S01-S15) has broader scope that subsumes bubbly-dancing-pony (s006, 11 TCs). CT-002 covers both. bubbly-dancing-pony scope is incorporated into CT-002 acceptance criteria.',
        'evidence': ['s013 covers all 15 machinery stages including pipeline reconciliation (S01)', 's006 addresses same pipeline divergence with 11 TCs'],
        'status': 'RESOLVED'
    },
    {
        'relationship_id': 'REL-004',
        'classification': 'SHARED_REQUIREMENT',
        'affected_plans': ['s001', 's007', 's012', 's013'],
        'conflict_id': 'CONFLICT-004',
        'resolution': 'ONE_CANONICAL_TASK: CT-001 resolves the validator count. Must be executed FIRST (Wave 0) so all governance plans start from the same baseline. runner has 167; MEMORY.md claims 165; CT-001 reconciles and updates MEMORY.md.',
        'evidence': ['governance_validator_runner.py:813 has expected_count=167', 'MEMORY.md text has 165'],
        'status': 'RESOLVED'
    },
    {
        'relationship_id': 'REL-005',
        'classification': 'MUST_SERIALIZE',
        'left_task_id': 'CT-001',
        'right_task_ids': ['CT-006', 'CT-017', 'CT-022'],
        'reason': 'All governance plans that reference validator count must run AFTER CT-001 resolves the discrepancy',
        'status': 'DOCUMENTED'
    },
    {
        'relationship_id': 'REL-006',
        'classification': 'MUST_SERIALIZE',
        'left_task_id': 'CT-003',
        'right_task_ids': ['CT-005', 'CT-006', 'CT-010', 'CT-024'],
        'reason': 'plan_importer.py (CT-003) is foundation for clean plan execution machinery; should precede multi-TC machinery plans',
        'status': 'DOCUMENTED'
    },
    {
        'relationship_id': 'REL-007',
        'classification': 'MUST_SERIALIZE',
        'left_task_id': 'CT-008',
        'right_task_ids': ['CT-005', 'CT-006', 'CT-010', 'CT-016'],
        'reason': 'Lifecycle healing (CT-008) must precede machinery plans requiring AUDIT→EXECUTE iteration',
        'status': 'DOCUMENTED'
    },
    {
        'relationship_id': 'REL-008',
        'classification': 'SUPERSEDED_WITH_PROOF',
        'left_plan_id': 's036',
        'right_plan_id': None,
        'reason': 'cheeky-crafting-manatee declared TERMINAL_CLOSED in source file; treated as already executed',
        'disposition': 'OUT_OF_SCOPE_WITH_JUSTIFICATION',
        'status': 'DOCUMENTED'
    },
    {
        'relationship_id': 'REL-009',
        'classification': 'SUPERSEDED_WITH_PROOF',
        'left_plan_id': 's039',
        'right_plan_id': None,
        'reason': 'effervescent-sprouting-marshmallow declared TERMINAL_CLOSED in source file; treated as already executed',
        'disposition': 'OUT_OF_SCOPE_WITH_JUSTIFICATION',
        'status': 'DOCUMENTED'
    },
    {
        'relationship_id': 'REL-010',
        'classification': 'PARALLEL_SAFE',
        'task_ids': ['CT-007', 'CT-009', 'CT-026'],
        'reason': 'FODS governance (L02), Oracle Phase II (L07), and product deepening (L02) operate on different lane resources. CT-007 is FODS-specific; CT-009 is oracle; CT-026 is DOM maturity.',
        'status': 'DOCUMENTED'
    },
]

relationship_records = {
    'schema_version': '1.0',
    'portfolio_id': PORTFOLIO_ID,
    'generated_at': now,
    'records': conflicts,
    'conflict_summary': {
        'CONFLICT-001': 'RESOLVED: s005 supersedes s004',
        'CONFLICT-002': 'RESOLVED: s024 supersedes s023',
        'CONFLICT-003': 'RESOLVED: s013 subsumes s006 in CT-002',
        'CONFLICT-004': 'RESOLVED: CT-001 is the single fix, Wave 0 predecessor',
    }
}
(PORTFOLIO_ROOT / 'relationship-records.json').write_text(json.dumps(relationship_records, indent=2))
print(f'relationship-records.json: {len(conflicts)} relationships')
print('All 4 CONFLICT-001..004 RESOLVED')

evt('EVT-011', 'LANES_AND_CONFLICTS_CLASSIFIED', 'TC-GOS-011',
    'TC-GOS-011: 10 lanes, 10 relationships, CONFLICT-001..004 all RESOLVED', 'EVT-010')
print('EVT-011 LANES_AND_CONFLICTS_CLASSIFIED')

# Update manifest
manifest = json.loads((PORTFOLIO_ROOT / 'portfolio-manifest.json').read_text())
manifest['updated_at'] = now
manifest['canonical_requirement_count'] = len(canonical_requirements)
manifest['canonical_task_count'] = len(canonical_tasks)
manifest['last_event_id'] = 'EVT-011'
(PORTFOLIO_ROOT / 'portfolio-manifest.json').write_text(json.dumps(manifest, indent=2))
print('\nManifest updated. TC-GOS-009..011 COMPLETE.')