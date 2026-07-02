"""Concurrent Agent Execution Hardening — concurrency control package.

Provides machine-enforced coordination for autonomous agents:
- MissionLock: SQLite-backed mission controller lock with heartbeat
- WorkerClaims: Atomic path ownership registry
- CheckpointManager: Git-diff-based checkpoint and recovery

Mission: CONC-HARDENING-2026-07-02
"""
