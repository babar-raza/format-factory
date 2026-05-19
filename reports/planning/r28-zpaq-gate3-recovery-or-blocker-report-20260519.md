# R28 Lane H: ZPAQ Gate 3 Recovery / Blocker Report

- **Sprint:** R28
- **Lane:** H
- **Format:** ZPAQ (zpaq)
- **Date:** 2026-05-19
- **Classification:** GATE3_BLOCKED_REQUIRES_EXTERNAL_TOOL
- **Verdict:** BLOCKED (no change from R27)

---

## 1. Executive Summary

ZPAQ Gate 3 remains blocked. The zpaq CLI is not available on this system
(`which zpaq` / `where zpaq` returned not-found). No pre-existing ZPAQ sample
files were found anywhere in the repository. Gate 3 cannot be completed without
an external tool or pre-made test corpus.

## 2. Why Gate 3 Is Blocked

ZPAQ archives are fundamentally different from simpler binary formats (QOI, XCF,
ZST) where valid files can be constructed programmatically using `struct.pack`.

**Root cause:** Every ZPAQ block contains an embedded ZPAQL bytecode program that
defines the compression/decompression algorithm. This bytecode runs on a
stack-based virtual machine with 256 opcodes, context mixing, and arithmetic
coding. A valid ZPAQ archive requires:

1. A correct block header (`zPQ` magic + level byte + header size)
2. A syntactically and semantically valid ZPAQL bytecode program
3. Compressed segment data that was produced by that specific ZPAQL program
4. Correct SHA-1 hashes and end markers

Items 2-3 are interdependent: the compressed data must be decompressible by the
exact ZPAQL program stored in the same block. Fabricating valid bytecode and
matching compressed data from scratch requires implementing a ZPAQL compiler or
interpreter -- this is not a trivial struct-packing exercise.

**Header-only stubs** (magic bytes + partial block header) could be created for
probe/magic-detection tests, but do NOT satisfy Gate 3 corpus requirements
(minimum 3 valid + 1 invalid sample with round-trip or extraction verification).

## 3. Three Resolution Paths

### Path A: Install zpaq CLI

- **Description:** Install the public-domain `zpaq` command-line tool (Matt
  Mahoney, C++). Use it to compress known input files into `.zpaq` archives.
  Record full provenance (zpaq version, command line, input file SHA-256, output
  SHA-256).
- **Effort:** Low (minutes if binary is available; build from source ~15 min)
- **Security implications:**
  - Binary must be verified (SHA-256 of download vs. published hash)
  - Source is public domain C++ (~3000 lines), auditable
  - No network dependencies at runtime
  - Risk: downloading pre-built binaries from third-party sites introduces
    supply-chain risk. Building from source (mattmahoney.net/dc/zpaq.cpp) is
    safer.
- **Provenance chain:** STRONG -- tool is public domain, command-line invocation
  is deterministic and recordable
- **Gate 3 feasibility:** HIGH -- can produce valid/invalid samples immediately

### Path B: Port Minimal ZPAQL Model to Python

- **Description:** Implement a minimal ZPAQL bytecode program (e.g., the
  simplest "store" model with no compression) and an arithmetic coder in Python.
  Generate archives containing this trivial model.
- **Effort:** HIGH (estimated 2-4 days). Requires:
  - ZPAQL bytecode assembler (or hand-coded bytecode)
  - Arithmetic encoder matching ZPAQ spec
  - Block/segment framing with correct checksums
- **Security implications:**
  - No external binaries -- pure Python
  - Risk of subtle spec-compliance bugs (bytecode correctness, arithmetic
    coding edge cases)
  - Custom implementation would need extensive validation against reference
- **Provenance chain:** MODERATE -- self-generated but harder to verify
  correctness without reference tool
- **Gate 3 feasibility:** MODERATE -- high effort, risk of invalid output

### Path C: Source Public-Domain ZPAQ Test Files

- **Description:** Obtain pre-existing ZPAQ test archives from public-domain
  sources. The reference implementation repository and various open-source
  backup tools include test fixtures.
- **Potential sources:**
  - Matt Mahoney's zpaq distribution (public domain, includes test archives)
  - zpaq GitHub mirrors (e.g., zpaq/zpaq on GitHub)
  - Internet Archive preservation collections
- **Effort:** LOW-MODERATE (finding files is easy; establishing provenance
  chain and license confirmation requires documentation)
- **Security implications:**
  - Files from untrusted sources could contain malicious ZPAQL bytecode
    (the VM is Turing-complete)
  - Must verify: (a) source authenticity, (b) file integrity (SHA-256),
    (c) license/public-domain status
  - ZPAQL bytecode in sourced files should be inspected or sandboxed
- **Provenance chain:** VARIABLE -- depends on source. Matt Mahoney's own
  files have strongest provenance.
- **Gate 3 feasibility:** MODERATE -- need to confirm files meet corpus
  requirements (valid/invalid, variety)

## 4. Security Comparison Matrix

| Criterion              | Path A (CLI)    | Path B (Port)   | Path C (Source) |
|------------------------|-----------------|-----------------|-----------------|
| Supply-chain risk      | LOW (if built)  | NONE            | MEDIUM          |
| Implementation risk    | NONE            | HIGH            | NONE            |
| ZPAQL bytecode risk    | LOW (our input) | LOW (our code)  | MEDIUM (foreign)|
| Provenance strength    | STRONG          | MODERATE        | VARIABLE        |
| Effort                 | LOW             | HIGH            | LOW-MODERATE    |
| Time to Gate 3         | Same day        | 2-4 days        | 1-2 days        |

## 5. Recommended Next Safe Path

**Primary recommendation: Path A (install zpaq CLI)**

Rationale:
- Lowest effort, highest confidence in output validity
- Public domain source, auditable (~3000 lines C++)
- Deterministic provenance (command + input + output hashes)
- Same-day Gate 3 completion once tool is available

**Fallback: Path C** if CLI installation is not feasible (e.g., policy
restriction on installing tools). In that case, source files from Matt
Mahoney's official distribution only.

**Path B is NOT recommended** at this time -- effort is disproportionate to
value for a Review-band format (score 6.2/10).

## 6. Action Items for Human Decision

1. **DECIDE:** Approve zpaq CLI installation (Path A) -- Y/N
   - If Y: provide preferred installation method (build from source vs.
     package manager vs. pre-built binary)
2. **DECIDE:** If Path A rejected, approve Path C with provenance requirements
3. **DECIDE:** If both rejected, accept ZPAQ Gate 3 as DEFERRED until tooling
   is available

## 7. Current State

- Gate 1: PASSED (delegated, score 6.2/10, Review band, awaiting human IV)
- Gate 2: PASSED (delegated, full public spec confirmed, awaiting human IV)
- Gate 3: BLOCKED (`blocked_sample_generation_requires_tool`)
- No source code exists or should be created (no `src/python/zpaq/`)
- Pack.yaml updated with R28 recovery attempt documentation

---

**GATE3_BLOCKED_REQUIRES_EXTERNAL_TOOL**

Sprint: R28 Lane H | Format: ZPAQ | Outcome: BLOCKED (unchanged)
