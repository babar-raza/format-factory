# Human Action Adjudication
## Sprint: FORMAT-FACTORY-EXPERT-MANUAL-SYSTEM-REVIEW-INVESTIGATE-AND-HEAL-001

| Action | Classification | Agent Can Do | Human Must Do |
|--------|---------------|-------------|--------------|
| Create src/net/netpbm/README.md for PROB-PK05 | AGENT_CAN_PREPARE_ONLY | Prepare template for review | Approve content and authorize creation |
| Full pyproject.toml for all 10 Python packages | AGENT_CAN_PREPARE_ONLY | Pilot abw+gnumeric; prepare templates for remaining 8 | Authorize extension to all 10 packages |
| Gate 11 NuGet publication | TRUE_EXTERNAL_AUTHORITY_REQUIRED | Run `dotnet pack`, prepare publication manifest | Provide credentials + authorize push |
| poc-targets.yaml mutation | AGENT_CAN_PREPARE_ONLY | Write proposed delta file | Approve and apply delta |
| Git commit of sprint fixes | TRUE_EXTERNAL_AUTHORITY_REQUIRED | Produce commit candidate manifest | Authorize commit + push |

All FIX_NOW_SAFE and FIX_NOW_WITH_LIMITED_SCOPE fixes in fix-queue.json have been classified as
AGENT_CAN_DO_NOW and will be applied in Phase 4 without further human authorization.
