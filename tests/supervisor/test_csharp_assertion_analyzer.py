"""Tests for CSharpAssertionAnalyzer (TC-C1, playful-swimming-stearns)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make tools/assurance importable
_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "assurance"))

from csharp_assertion_analyzer import CSharpAssertionAnalyzer, STRONG_RATIO_THRESHOLD


@pytest.fixture
def analyzer() -> CSharpAssertionAnalyzer:
    return CSharpAssertionAnalyzer()


# ---------------------------------------------------------------------------
# 1. STRONG assertion patterns
# ---------------------------------------------------------------------------

def test_equal_literal_string_is_strong(analyzer: CSharpAssertionAnalyzer) -> None:
    content = """
    [Fact]
    public void TestSomething()
    {
        Assert.Equal("Alice", result.Name);
        Assert.Equal("Bob", other.Name);
    }
    """
    analysis = analyzer.analyze_content(content, "test.cs")
    assert analysis.assertion_count.strong >= 2
    assert analysis.grade == "STRONG_PROOF"


def test_equal_integer_is_strong(analyzer: CSharpAssertionAnalyzer) -> None:
    content = """
    [Fact]
    public void RowCount()
    {
        Assert.Equal(3, doc.RowCount);
        Assert.Equal(2, doc.ColumnCount);
    }
    """
    analysis = analyzer.analyze_content(content, "test.cs")
    assert analysis.assertion_count.strong >= 2
    assert analysis.grade == "STRONG_PROOF"


def test_inrange_is_strong(analyzer: CSharpAssertionAnalyzer) -> None:
    content = """
    [Fact]
    public void EntropyInRange()
    {
        Assert.InRange(entropy, 0.99, 1.01);
    }
    """
    analysis = analyzer.analyze_content(content, "test.cs")
    assert analysis.assertion_count.strong >= 1
    assert analysis.grade == "STRONG_PROOF"


# ---------------------------------------------------------------------------
# 2. WEAK assertion patterns
# ---------------------------------------------------------------------------

def test_not_null_only_is_weak(analyzer: CSharpAssertionAnalyzer) -> None:
    content = """
    [Fact]
    public void LoadReturnsNonNull()
    {
        Assert.NotNull(result);
        Assert.NotNull(result.Headers);
    }
    """
    analysis = analyzer.analyze_content(content, "test.cs")
    assert analysis.assertion_count.weak >= 2
    assert analysis.grade == "WEAK_PROOF"


def test_not_empty_only_is_weak(analyzer: CSharpAssertionAnalyzer) -> None:
    content = """
    [Fact]
    public void RowsNotEmpty()
    {
        Assert.NotEmpty(rows);
    }
    """
    analysis = analyzer.analyze_content(content, "test.cs")
    assert analysis.assertion_count.weak >= 1
    assert analysis.grade == "WEAK_PROOF"


# ---------------------------------------------------------------------------
# 3. Mixed — PARTIAL_PROOF
# ---------------------------------------------------------------------------

def test_mix_of_strong_and_weak_below_threshold(analyzer: CSharpAssertionAnalyzer) -> None:
    content = """
    [Fact]
    public void Mixed()
    {
        Assert.NotNull(doc);
        Assert.NotNull(doc.Headers);
        Assert.NotNull(doc.Rows);
        Assert.NotEmpty(doc.Rows);
        Assert.Equal("Name", doc.Headers[0]);
    }
    """
    analysis = analyzer.analyze_content(content, "test.cs")
    # 1 strong vs 4 weak → ratio = 0.2 < 0.3 threshold → PARTIAL_PROOF
    assert analysis.assertion_count.strong >= 1
    assert analysis.grade in ("PARTIAL_PROOF", "WEAK_PROOF")


# ---------------------------------------------------------------------------
# 4. File-level ratio threshold
# ---------------------------------------------------------------------------

def test_strong_ratio_above_threshold_is_strong_proof(analyzer: CSharpAssertionAnalyzer) -> None:
    # 3 strong, 1 weak → ratio = 3/4 = 0.75 > 0.3
    content = """
    Assert.Equal("Alice", row[0]);
    Assert.Equal("Bob", row[1]);
    Assert.Equal(42, count);
    Assert.NotNull(doc);
    """
    analysis = analyzer.analyze_content(content, "test.cs")
    assert analysis.grade == "STRONG_PROOF"
    assert analysis.assertion_count.strong_ratio >= STRONG_RATIO_THRESHOLD


def test_throws_assertion_is_strong(analyzer: CSharpAssertionAnalyzer) -> None:
    content = """
    [Fact]
    public void InvalidInput_Throws()
    {
        Assert.Throws<ArgumentException>(() => doc.GetColumn(""));
    }
    """
    analysis = analyzer.analyze_content(content, "test.cs")
    assert analysis.assertion_count.strong >= 1
    assert analysis.grade == "STRONG_PROOF"
