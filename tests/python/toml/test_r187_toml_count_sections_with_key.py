"""
Tests for count_sections_with_key — count top-level TOML sections containing a key.
Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT80-001
"""

import sys
import pytest

sys.path.insert(0, "src/python")

from toml import count_sections_with_key


def test_all_sections_have_key():
    src = b"""
[database]
host = "localhost"
port = 5432

[cache]
host = "redis"
port = 6379
"""
    assert count_sections_with_key(src, "host") == 2


def test_some_sections_have_key():
    src = b"""
[database]
host = "localhost"
port = 5432

[cache]
port = 6379
"""
    assert count_sections_with_key(src, "host") == 1


def test_no_sections_have_key():
    src = b"""
[database]
port = 5432

[cache]
port = 6379
"""
    assert count_sections_with_key(src, "host") == 0


def test_empty_toml():
    src = b""
    assert count_sections_with_key(src, "host") == 0


def test_no_sections_only_scalars():
    src = b"""
name = "app"
version = "1.0"
"""
    assert count_sections_with_key(src, "name") == 0


def test_single_section_with_key():
    src = b"""
[server]
timeout = 30
"""
    assert count_sections_with_key(src, "timeout") == 1


def test_nested_key_not_counted():
    # The key exists only nested inside a subsection — not as direct child of top-level section
    src = b"""
[section_a]
subsection = {deep = true}
"""
    assert count_sections_with_key(src, "deep") == 0


def test_key_absent_everywhere():
    src = b"""
[alpha]
x = 1

[beta]
y = 2
"""
    assert count_sections_with_key(src, "z") == 0


def test_three_sections_all_match():
    src = b"""
[a]
enabled = true

[b]
enabled = false

[c]
enabled = true
"""
    assert count_sections_with_key(src, "enabled") == 3


def test_bytes_input():
    # Verify bytes input is accepted
    src = b"[section]\nkey = 1\n"
    assert count_sections_with_key(src, "key") == 1
