# Forbidden Paths
# Sprint: FORMAT-FACTORY-LOCAL-MEMORY-PRODUCT-FIRST-AI-EXTERNAL-TOOLS-SYNC-001

This sprint MUST NOT write to any of the following:

## Product Source (HARD BLOCK)
- src/net/*
- src/python/*

## Tests (HARD BLOCK)
- tests/net/*
- tests/python/*
- tests/supervisor/*

## Registry and Gates (HARD BLOCK)
- registry/format-registry.yaml
- publication/*
- release/*

## MCP and Credentials (HARD BLOCK)
- .vscode/mcp.json
- credentials.*
- secrets.*
- *.env

## Policy Files (HARD BLOCK)
- .supervisor/policies.yaml (may not be modified)

## Product Capability Matrix (read only)
- product-capability-matrix/poc-targets.yaml (read-only; proposed patches via reports only)

## Prohibited Actions
- No git commit
- No git push
- No package publication
- No gate approval
- No external tool installation (Ruflo, Superpowers, GhidraMCP)
- No MCP activation or modification
