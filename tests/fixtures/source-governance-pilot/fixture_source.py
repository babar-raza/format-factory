"""fixture_source.py — Controlled source governance pilot fixture.

This file is a controlled fixture used ONLY for testing the governance validator chain.
It is NOT a real product source file. No changes to this file are product source mutations.

The function below represents the "before" state of a controlled pilot: a simple
function that existed before the governance taxonomy was established.

GOVERNANCE PILOT NOTE:
  - execution_method: MANUAL_GOVERNED_BY_SKILL
  - skill_id: add-python-api
  - idempotency_key: see fixture-evidence.yaml
  - This file must NEVER be imported by real product code.
"""
# FORMAT_FACTORY_EXECUTION: taskcard=GEC-TC-011; method=MANUAL_GOVERNED_BY_SKILL; skill=add-python-api; idempotency=gec011fixture0000000000000000000000000000000000000000000000000000; evidence=tests/fixtures/source-governance-pilot/fixture-evidence.yaml


def get_fixture_value(data: dict, key: str) -> str:
    """Return the string value for key from data dict.

    Controlled pilot function — demonstrates governance evidence chain.
    """
    return str(data.get(key, ""))
