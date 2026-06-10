# Acceleration Adoption Checklist (Skills R105)

## Gap Selection
- [ ] Select gaps from `product-capability-matrix/poc-targets.yaml`
- [ ] Use `/select-poc-gap` skill if available

## Handoff Generation
- [ ] Identify the skill_id for the gap's product_track
- [ ] Use `/generate-execution-handoff` to create structured handoff
- [ ] Ensure all required_handoff_fields are present
- [ ] Place handoff in `reports/skills-r{N}/generated-handoffs/`

## Delegation
- [ ] Do NOT edit product source directly
- [ ] Route source changes through Mainstream via handoffs
- [ ] Track handoff consumption in next sprint
