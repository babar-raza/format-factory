# Solution Options Analysis
Generated: 2026-07-04

## Design Choice: QName Hierarchy Document Format

### Option A: Flat YAML list of qname_node entries
- Pros: Simple, readable, easy to validate
- Cons: Hierarchy not explicit in structure

### Option B: Nested YAML tree (parent contains children)
- Pros: Hierarchy explicit
- Cons: Harder to query individual nodes

### Option C: Graph edge list (separate nodes + edges)
- Pros: Flexible for complex graphs
- Cons: Overcomplicated for ODF hierarchy

**Selected: Option A** — flat list with parent_qnames + child_qnames fields. Readable and validatable.

---

## Design Choice: Promotion Registry Scope

### Option A: Single registry covers architecture + source CI state
- Risk: Duplicates blossom TC-CQGA-018/019 registry/promotion-ledger.yaml

### Option B: Two separate registries
- Arc: reports/product-architecture/promotion-registry.yaml (architecture approval level)
- Blossom: registry/promotion-ledger.yaml (source CI state)
- promotion_manager.py cross-references both

**Selected: Option B** — no duplication; arc registry is architecture-level only.

---

## Design Choice: Governance Validator Extension File Naming

### Option A: Extend governance_validators_ext3.py
- Risk: governance_validators_ext3.py belongs to PQLM-001 (blossom)

### Option B: Create governance_validators_ext4.py
- Safe: separate file, IDs V111-V127
- No collision with existing files

**Selected: Option B** — governance_validators_ext4.py with IDs V111-V127.
