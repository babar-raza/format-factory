# Format Factory Knowledge Registry

**Purpose:** Canonical index of knowledge contracts for recurring repository structures. Agents query this before modifying any `src/python/` source file or creating new model classes — instead of browsing implementations to infer structure.

---

## How to Query

```
.venv/Scripts/python .supervisor/knowledge/validate_knowledge_contracts.py
```

Check single contract:
```
.venv/Scripts/python .supervisor/knowledge/validate_knowledge_contracts.py --contract KC-PYTHON-001
```

**When to use:** Before any `src/python/*/models.py` creation or modification, before invoking `/add-python-object-model-feature` or `/add-python-api`, or when uncertain about any recurring repository structure.

---

## Available Contracts

| ID | Subject | Status | Path |
|----|---------|--------|------|
| KC-PYTHON-001 | Python domain model class pattern | VERIFIED_CURRENT | [contracts/python-domain-model.yaml](contracts/python-domain-model.yaml) |
| KC-PYTHON-002 | Python format package directory layout | DRAFT_PENDING_AUTHORITY | [contracts/python-source-structure.yaml](contracts/python-source-structure.yaml) |

**Important:** Only follow contracts with `status: VERIFIED_CURRENT`. DRAFT contracts must not be used as guidance.

---

## Canonical Examples

| Example | Contract | Path |
|---------|----------|------|
| CE-PYTHON-001 (CsvDocument) | KC-PYTHON-001 | [examples/python-domain-model-canonical.py](examples/python-domain-model-canonical.py) |

---

## Machine-Readable Registry

Full contract index: [registry.yaml](registry.yaml)

---

## Adding a Knowledge Gap

When you encounter an ambiguity not covered by an existing contract, append an entry to [gaps.yaml](gaps.yaml) **before browsing implementations**. Follow the KG-001 template. Set `status: DISCOVERED`.

After resolving: update the entry to `status: CONTRACT_WRITTEN`.

Note in sprint declaration evidence: "Knowledge gap KG-NNN documented."

---

## Adding a Growth Event

When you resolve an ambiguity by writing a contract, append an entry to [growth-events.yaml](growth-events.yaml) following the GE-001 template. Then update `registry.yaml` with the new contract entry and run the validator.
