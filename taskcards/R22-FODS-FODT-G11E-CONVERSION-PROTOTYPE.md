# Taskcard: R22-FODS-FODT-G11E-CONVERSION-PROTOTYPE

**Sprint:** R22 (planned)
**Date created:** 2026-05-17
**Status:** PENDING EXPLICIT AUTHORIZATION PROMPT

## Objective

Implement G11-E conversion/export capability for FODS and FODT (.NET track).

## Prerequisites

1. G11-A: delegated_architecture_review_complete (DONE R21)
2. G11-B: planning_level_license_confirmation_complete (DONE R21)
3. G11-C: package_plan_complete (DONE R21)
4. G11-E design: design_complete_not_implemented (DONE R21)
5. **Explicit R22 prompt authorizing src/net mutation for G11-E**

## Blocked Until

Explicit human authorization prompt that:
- Explicitly permits src/net mutation for G11-E
- Specifies which conversion targets to implement (CSV/TXT/HTML/DOCX)
- Confirms commercial product scope

## Design Reference

- FODS G11-E: acquisition-packs/fods/gate11-conversion-export-technical-design.md
- FODT G11-E: acquisition-packs/fodt/gate11-conversion-export-technical-design.md

## What Must NOT Happen Without Authorization

- No src/net/ file creation or modification
- No commercial_product_ready=true
- No NuGet package build
