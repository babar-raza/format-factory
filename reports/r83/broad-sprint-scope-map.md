# R83 Broad Sprint Scope Map

## Primary Goal: Fix R82 Artifact Failure

The supervisor received the inner evidence bundle (r82-pass2.zip) instead of the supervisor review package. R83 must produce r83-supervisor-review-package.zip as primary artifact using the proper build_supervisor_review_package.py tool.

## Parallel Work Streams

### Stream 1: Artifact Closure (Trains A-D)
- R82 IV + defect ledger
- Build proper supervisor review package
- Fix all PENDING metadata before bundle build
- Add validator tests to prevent regression

### Stream 2: FODS Product Finish (Trains E-G)
- Run FODS workflow from extracted review package (outside repo, no PYTHONPATH)
- Feature deepening (CSV export, warning codes)
- Product completion decision

### Stream 3: FODT Product Track (Trains H-I)
- Run FODT workflow from extracted review package
- Feature deepening (text export, paragraph styles)

### Stream 4: ZST Dependency (Train J)
- Classify offline replay vs dependency-required
- Test probe-only no-dependency behavior

### Stream 5: .NET Advancement (Trains K-L)
- Fresh .NET tests + parity additions
- Commercial gap ledger

### Stream 6: Next-Format Advancement (Trains M-P)
- Netpbm improvements
- SYLK/DIF improvements
- Gate 8 readiness matrix
- Probe package truth

### Stream 7: Examples/Docs (Trains Q-R)
- Real installed-package examples
- Publication readiness matrix

### Stream 8: AI/Automation (Trains S-T)
- AI gap extraction (fixture mode)
- Closeout automation driver

### Stream 9: Authority Sync (Trains U-V)
- State/master-plan updated BEFORE bundle build
- Final adversarial IV

## Critical Sequencing Rules

1. Metadata files must be FINAL before bundle build
2. State snapshot must run before bundle build
3. Primary artifact = supervisor review package, not inner bundle
4. Installed workflows must run AFTER review package is built and extracted
