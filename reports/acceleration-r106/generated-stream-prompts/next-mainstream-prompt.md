# Mainstream R108 Sprint Prompt

## Sprint ID
FORMAT-FACTORY-MAINSTREAM-R108-PRODUCT-DEPTH-AND-GATE-READINESS-CAMPAIGN-001

## Mission
Continue deepening FODS, FODT, and Netpbm .NET product implementations toward Gate 11 commercial readiness.

## Lane A: FODS .NET Product Depth
- Add next capability from product-capability-matrix gap list
- Target: export functionality or cell manipulation API
- Write tests proving new capability

## Lane B: FODT .NET Product Depth
- Add next capability from product-capability-matrix gap list
- Target: text manipulation or structural API
- Write tests proving new capability

## Lane C: Netpbm .NET Product Depth
- Continue image manipulation API expansion
- Write tests proving new capability

## Lane D: Python FOSS Hardening
- Run existing FOSS test suite, fix any regressions
- Add roundtrip tests for ZST/PPM/SYLK

## Evidence Closeout
Write evidence-declaration.yaml and run autonomous-cycle.

## File Boundaries
- ALLOWED: src/net/*, src/python/*, tests/net/*, tests/python/*
- FORBIDDEN: tools/supervisor/*, tests/supervisor/*
