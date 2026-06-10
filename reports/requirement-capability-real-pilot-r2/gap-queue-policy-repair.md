# Gap Queue Policy Repair
Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R2-001

## Problem (R1 Caveat 6)
R1 gap queue routed FODS/FODT architecture-blocked exports to Mainstream-Dogfood with
generic 'Provide ImplementationProof' next_action. This was incorrect and would cause
Mainstream to attempt dogfood work before the target writer library exists.

## Fix Applied
File: tools/requirements_authority/mainstream_gap_queue.py
Method: _build_entry()
Change: Added architecture-blocked detection via blocked_by edge + metadata check.
Result: Architecture-blocked export claims now route to Target-Writer-Architecture lane
with specific next_action naming the required library.

## Verification
- arch_blocked_gaps routed to Target-Writer-Architecture: 4
- arch_blocked_gaps routed to Mainstream-Dogfood: 0 (must be 0)
- Policy compliant: True
