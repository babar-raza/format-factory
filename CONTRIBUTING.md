# Contributing to format-factory

## Prerequisites

- Python 3.9 or later
- Git

## Development Setup

```bash
# Clone the repository
git clone https://github.com/prora/format-factory.git
cd format-factory

# Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dev dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Run tests for a specific format
pytest tests/python/fods/

# Run supervisor tests
pytest tests/supervisor/
```

## Running the Linter

```bash
# Check for issues
ruff check src/ tests/ tools/

# Auto-fix safe issues
ruff check src/ tests/ tools/ --fix
```

## Running Security Scan

```bash
bandit -r src/ -ll -q
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Run tests: `pytest`
4. Run linter: `ruff check src/ tests/ tools/`
5. Open a Pull Request against `main`
6. Wait for CI checks to pass and review approval

## For AI Agent Contributors

AI agents operating on this repository must follow the rules in [`AGENTS.md`](AGENTS.md). Key rules:

- Agents are executors, not approvers
- No autonomous gate approval
- No push or commit without explicit human authorization
- Evidence declarations required at sprint close

See [`AGENTS.md`](AGENTS.md) for the full operating contract.

## For Human Contributors

Human contributors should review [`GOVERNANCE.md`](GOVERNANCE.md) for:

- Gate approval process (all 11 gates require human approval)
- Release control and visibility classification
- Open-source boundary rules

## Legal Requirements

Before working on any format, review [`docs/legal-and-licensing.md`](docs/legal-and-licensing.md). All formats must be legally classified before any prototype work begins. Category 5 (reverse-engineered binary) and Category 6 (blocked) formats are automatic rejects.

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
