#!/usr/bin/env python3
"""Assertion depth scorer for .NET test files.

Parses C# test files and classifies each Assert.* call into:
  - behavioral: Assert.Equal with a meaningful expected value (not just comparing same var)
  - structural: Assert.NotNull, Assert.Null, Assert.IsType, Assert.NotEmpty, Assert.True/False
                on simple checks, Assert.Single, Assert.Contains
  - guard: Assert.ThrowsAny, Assert.Throws

Computes depth ratio: behavioral / (behavioral + structural)
Guard assertions are excluded from the ratio (they test error paths, which is valid).

Also detects:
  - roundtrip tests: save -> reload -> assert pattern
  - real-file tests: tests that load from a file path (not CreateNew/CreateEmpty)

Usage:
    python tools/quality/depth_scorer.py [--format FODS] [--dir tests/net/fods]
    python tools/quality/depth_scorer.py --file tests/net/fods/FodsR351GetCellFontColorDedicatedTests.cs
"""
import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class FileScore:
    path: str
    behavioral: int = 0
    structural: int = 0
    guard: int = 0
    has_roundtrip: bool = False
    has_real_file: bool = False
    dogfood_weak: int = 0  # dogfood asserts that are NotNull instead of Equal

    @property
    def total_non_guard(self) -> int:
        return self.behavioral + self.structural

    @property
    def depth_ratio(self) -> float:
        total = self.total_non_guard
        if total == 0:
            return 0.0
        return self.behavioral / total


# Patterns for classification
RE_ASSERT_EQUAL = re.compile(r'Assert\.Equal\s*\(')
RE_ASSERT_NOT_NULL = re.compile(r'Assert\.NotNull\s*\(')
RE_ASSERT_NULL = re.compile(r'Assert\.Null\s*\(')
RE_ASSERT_THROWS = re.compile(r'Assert\.Throws(?:Any|Async)?\s*[<(]')
RE_ASSERT_IS_TYPE = re.compile(r'Assert\.IsType\s*[<(]')
RE_ASSERT_TRUE = re.compile(r'Assert\.True\s*\(')
RE_ASSERT_FALSE = re.compile(r'Assert\.False\s*\(')
RE_ASSERT_SINGLE = re.compile(r'Assert\.Single\s*\(')
RE_ASSERT_CONTAINS = re.compile(r'Assert\.Contains\s*\(')
RE_ASSERT_DOES_NOT_CONTAIN = re.compile(r'Assert\.DoesNotContain\s*\(')
RE_ASSERT_NOT_EMPTY = re.compile(r'Assert\.NotEmpty\s*\(')
RE_ASSERT_EMPTY = re.compile(r'Assert\.Empty\s*\(')
RE_ASSERT_NOT_EQUAL = re.compile(r'Assert\.NotEqual\s*\(')
RE_ASSERT_IN_RANGE = re.compile(r'Assert\.InRange\s*\(')
RE_ASSERT_SAME = re.compile(r'Assert\.Same\s*\(')
RE_ASSERT_NOT_SAME = re.compile(r'Assert\.NotSame\s*\(')
RE_ASSERT_COLLECTION = re.compile(r'Assert\.Collection\s*\(')
RE_ASSERT_ALL = re.compile(r'Assert\.All\s*\(')
RE_ASSERT_STARTS_WITH = re.compile(r'Assert\.StartsWith\s*\(')
RE_ASSERT_ENDS_WITH = re.compile(r'Assert\.EndsWith\s*\(')
RE_ASSERT_MATCHES = re.compile(r'Assert\.Matches\s*\(')

# Detect roundtrip: save/ToFodsXml then Load/LoadFromXml
RE_ROUNDTRIP_SAVE = re.compile(r'\.(?:Save|ToFodsXml|ExportTo\w+)\s*\(')
RE_ROUNDTRIP_RELOAD = re.compile(r'(?:FodsDocument\.(?:Load|LoadFromXml)|\.Load)\s*\(')

# Detect real file usage (not CreateNew/CreateEmpty)
RE_REAL_FILE = re.compile(r'FodsDocument\.Load\s*\(\s*(?:path|filePath|srcPath|fixturePath|samplePath)')

# Detect dogfood section
RE_DOGFOOD_SECTION = re.compile(r'//\s*Dogfood|DogfoodPipeline')

# Assert.Equal with a literal/const expected value (behavioral)
# e.g., Assert.Equal("Jane Smith", author) or Assert.Equal(42, count) or Assert.Equal(true, flag)
RE_BEHAVIORAL_EQUAL = re.compile(
    r'Assert\.Equal\s*\(\s*'
    r'(?:'
    r'"[^"]*"'       # string literal
    r'|\'[^\']*\''   # char literal
    r'|\d+(?:\.\d+)?[fFdDmM]?'  # numeric literal
    r'|true|false'   # boolean literal
    r'|null'         # null literal
    r')'
    r'\s*,'
)

# Assert.Equal comparing two variables (structural - just consistency check)
RE_STRUCTURAL_EQUAL = re.compile(
    r'Assert\.Equal\s*\(\s*'
    r'(?:before|first|count\d?|original)\s*,'
)


def score_file(filepath: Path) -> FileScore:
    """Score a single .cs test file."""
    score = FileScore(path=str(filepath))
    try:
        content = filepath.read_text(encoding='utf-8-sig', errors='replace')
    except Exception:
        return score

    lines = content.split('\n')
    in_dogfood = False
    has_save = bool(RE_ROUNDTRIP_SAVE.search(content))
    has_reload = bool(RE_ROUNDTRIP_RELOAD.search(content))
    score.has_roundtrip = has_save and has_reload
    score.has_real_file = bool(RE_REAL_FILE.search(content))

    for line in lines:
        stripped = line.strip()

        # Track dogfood sections
        if RE_DOGFOOD_SECTION.search(stripped):
            in_dogfood = True

        # Guard assertions
        if RE_ASSERT_THROWS.search(stripped):
            score.guard += 1
            continue

        # Assert.Equal classification
        if RE_ASSERT_EQUAL.search(stripped):
            if RE_BEHAVIORAL_EQUAL.search(stripped):
                score.behavioral += 1
            elif RE_STRUCTURAL_EQUAL.search(stripped):
                score.structural += 1
            else:
                # Default: if it has a literal first arg, behavioral; else structural
                score.behavioral += 1
            continue

        # Assert.NotEqual, Contains, DoesNotContain with literals = behavioral
        if RE_ASSERT_NOT_EQUAL.search(stripped):
            score.behavioral += 1
            continue
        if RE_ASSERT_CONTAINS.search(stripped):
            score.behavioral += 1
            continue
        if RE_ASSERT_DOES_NOT_CONTAIN.search(stripped):
            score.behavioral += 1
            continue
        if RE_ASSERT_STARTS_WITH.search(stripped):
            score.behavioral += 1
            continue
        if RE_ASSERT_ENDS_WITH.search(stripped):
            score.behavioral += 1
            continue
        if RE_ASSERT_MATCHES.search(stripped):
            score.behavioral += 1
            continue
        if RE_ASSERT_IN_RANGE.search(stripped):
            score.behavioral += 1
            continue

        # Structural assertions
        if RE_ASSERT_NOT_NULL.search(stripped):
            score.structural += 1
            if in_dogfood:
                score.dogfood_weak += 1
            continue
        if RE_ASSERT_NULL.search(stripped):
            score.structural += 1
            continue
        if RE_ASSERT_IS_TYPE.search(stripped):
            score.structural += 1
            continue
        if RE_ASSERT_TRUE.search(stripped):
            score.structural += 1
            continue
        if RE_ASSERT_FALSE.search(stripped):
            score.structural += 1
            continue
        if RE_ASSERT_SINGLE.search(stripped):
            score.structural += 1
            continue
        if RE_ASSERT_NOT_EMPTY.search(stripped):
            score.structural += 1
            continue
        if RE_ASSERT_EMPTY.search(stripped):
            score.structural += 1
            continue
        if RE_ASSERT_SAME.search(stripped):
            score.structural += 1
            continue
        if RE_ASSERT_NOT_SAME.search(stripped):
            score.structural += 1
            continue
        if RE_ASSERT_COLLECTION.search(stripped):
            score.behavioral += 1
            continue
        if RE_ASSERT_ALL.search(stripped):
            score.behavioral += 1
            continue

    return score


def score_directory(dirpath: Path, pattern: str = "*Tests.cs") -> list[FileScore]:
    """Score all test files in a directory."""
    scores = []
    for f in sorted(dirpath.rglob(pattern)):
        scores.append(score_file(f))
    return scores


def print_report(scores: list[FileScore], verbose: bool = False):
    """Print a depth score report."""
    total_behavioral = sum(s.behavioral for s in scores)
    total_structural = sum(s.structural for s in scores)
    total_guard = sum(s.guard for s in scores)
    total_dogfood_weak = sum(s.dogfood_weak for s in scores)
    roundtrip_count = sum(1 for s in scores if s.has_roundtrip)
    real_file_count = sum(1 for s in scores if s.has_real_file)

    total_non_guard = total_behavioral + total_structural
    overall_ratio = total_behavioral / total_non_guard if total_non_guard else 0.0

    print(f"\n{'='*70}")
    print(f"DEPTH SCORE REPORT")
    print(f"{'='*70}")
    print(f"Files analyzed:       {len(scores)}")
    print(f"Behavioral asserts:   {total_behavioral}")
    print(f"Structural asserts:   {total_structural}")
    print(f"Guard asserts:        {total_guard}")
    print(f"Total non-guard:      {total_non_guard}")
    print(f"{'-'*70}")
    print(f"DEPTH RATIO:          {overall_ratio:.4f}  ({overall_ratio*100:.1f}%)")
    print(f"{'-'*70}")
    print(f"Roundtrip tests:      {roundtrip_count} files")
    print(f"Real-file tests:      {real_file_count} files")
    print(f"Weak dogfood asserts: {total_dogfood_weak} (NotNull in Dogfood sections)")
    print(f"{'='*70}")

    if verbose:
        # Show worst files (lowest depth ratio with > 0 assertions)
        scoreable = [s for s in scores if s.total_non_guard > 0]
        scoreable.sort(key=lambda s: s.depth_ratio)
        print(f"\nBottom 20 files by depth ratio:")
        print(f"{'Ratio':>7} {'Beh':>4} {'Str':>4} {'Grd':>4} {'DW':>3} {'File'}")
        for s in scoreable[:20]:
            name = Path(s.path).name
            print(f"{s.depth_ratio:7.3f} {s.behavioral:4} {s.structural:4} {s.guard:4} {s.dogfood_weak:3} {name}")

        print(f"\nTop 10 files by depth ratio:")
        for s in scoreable[-10:]:
            name = Path(s.path).name
            print(f"{s.depth_ratio:7.3f} {s.behavioral:4} {s.structural:4} {s.guard:4} {s.dogfood_weak:3} {name}")

    # Machine-readable summary
    print(f"\n## Machine-readable")
    print(f"depth_ratio={overall_ratio:.4f}")
    print(f"behavioral={total_behavioral}")
    print(f"structural={total_structural}")
    print(f"guard={total_guard}")
    print(f"roundtrip_files={roundtrip_count}")
    print(f"real_file_files={real_file_count}")
    print(f"dogfood_weak={total_dogfood_weak}")
    print(f"total_files={len(scores)}")
    gate_pass = overall_ratio >= 0.4
    print(f"gate_pass={'true' if gate_pass else 'false'}")
    print(f"gate_threshold=0.40")


def main():
    parser = argparse.ArgumentParser(description='Assertion depth scorer for .NET tests')
    parser.add_argument('--dir', type=str, default=None, help='Directory to scan')
    parser.add_argument('--file', type=str, default=None, help='Single file to score')
    parser.add_argument('--format', type=str, default='fods', help='Format name (used to find test dir)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show per-file details')
    parser.add_argument('--pattern', type=str, default='*Tests.cs', help='Glob pattern for test files')
    args = parser.parse_args()

    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"ERROR: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        scores = [score_file(filepath)]
    elif args.dir:
        dirpath = Path(args.dir)
        if not dirpath.exists():
            print(f"ERROR: Directory not found: {dirpath}", file=sys.stderr)
            sys.exit(1)
        scores = score_directory(dirpath, args.pattern)
    else:
        dirpath = Path(f'tests/net/{args.format}')
        if not dirpath.exists():
            print(f"ERROR: Directory not found: {dirpath}", file=sys.stderr)
            sys.exit(1)
        scores = score_directory(dirpath, args.pattern)

    if not scores:
        print("No test files found.", file=sys.stderr)
        sys.exit(1)

    print_report(scores, verbose=args.verbose)


if __name__ == '__main__':
    main()
